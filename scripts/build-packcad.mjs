// Builds PackCAD's embeddable viewer (vendor/packcad) into public/packcad/, for the Paper Models view.
//
// PackCAD is React 19 and TypeScript on its own three.js and the Atelier engine, none of which this
// site shares, so it is not imported: the view puts its viewer page (vendor/packcad/viewer.html) in
// an iframe and drives it with window messages (vendor/packcad/docs/embed.md). PackCAD depends on
// Atelier by the sibling path `../atelier`, which is why Atelier is the submodule beside it,
// vendor/atelier: the link resolves with no change to either repository.
//
// Both are pnpm workspaces. Each is installed only when its lockfile changes, and the viewer is
// rebuilt only when either pinned commit or lockfile changes, as build-geo-toolkit.mjs does. The
// output is built with relative URLs (BASE_PATH=./), so it works wherever the site is served from.

import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('../', import.meta.url))
const dirs = { atelier: `${root}vendor/atelier/`, packcad: `${root}vendor/packcad/` }
const out = `${root}public/packcad/`

for (const [name, dir] of Object.entries(dirs)) {
  if (!existsSync(`${dir}package.json`)) {
    console.error(`vendor/${name} is empty. Run: git submodule update --init vendor/atelier vendor/packcad`)
    process.exit(1)
  }
}

const read = (path) => (existsSync(path) ? readFileSync(path, 'utf8') : null)
const hash = (text) => createHash('sha256').update(text ?? '').digest('hex')
const commitOf = (dir) => {
  try { return execFileSync('git', ['rev-parse', 'HEAD'], { cwd: dir, encoding: 'utf8' }).trim() } catch { return 'unknown' }
}

// pnpm if it is installed; otherwise the version PackCAD pins, fetched for the run.
const pnpm = (() => {
  try {
    execFileSync('pnpm', ['--version'], { stdio: 'ignore' })
    return { command: 'pnpm', prefix: [] }
  } catch {
    const pinned = JSON.parse(read(`${dirs.packcad}package.json`)).packageManager ?? 'pnpm@9'
    return { command: process.platform === 'win32' ? 'npx.cmd' : 'npx', prefix: ['--yes', pinned] }
  }
})()
const run = (dir, args, env = {}) => execFileSync(pnpm.command, [...pnpm.prefix, ...args], {
  cwd: dir,
  stdio: ['ignore', 'ignore', 'inherit'],
  env: { ...process.env, ...env }
})

const locks = {}
for (const [name, dir] of Object.entries(dirs)) {
  locks[name] = hash(read(`${dir}pnpm-lock.yaml`))
  if (read(`${dir}node_modules/.pofbc-install`) !== locks[name]) {
    run(dir, ['install', '--frozen-lockfile', '--ignore-scripts'])
    writeFileSync(`${dir}node_modules/.pofbc-install`, locks[name])
  }
}

const commits = { atelier: commitOf(dirs.atelier), packcad: commitOf(dirs.packcad) }
const stamp = JSON.stringify({ commits, locks })
const unknown = Object.values(commits).includes('unknown')
if (unknown || read(`${out}.pofbc-build`) !== stamp) {
  // vite directly rather than `pnpm build`: that also typechecks the editor, which the site does not ship.
  run(dirs.packcad, ['exec', 'vite', 'build', '--outDir', out, '--emptyOutDir', '--logLevel', 'error'], {
    PACKCAD_ENTRY: 'viewer',
    BASE_PATH: './'
  })
  writeFileSync(`${out}.pofbc-build`, stamp)
  console.log(`  packcad viewer     built ${commits.packcad.slice(0, 7)} (atelier ${commits.atelier.slice(0, 7)})`)
} else {
  console.log(`  packcad viewer     ${commits.packcad.slice(0, 7)} already built`)
}
