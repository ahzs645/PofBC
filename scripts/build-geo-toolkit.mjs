// Builds the geo-toolkit submodule (vendor/geo-toolkit) so the site can import its compiled output.
//
// The toolkit's source is TypeScript with Tailwind-processed CSS, which this site's Vite setup does
// not compile, so the Health Maps view imports its `dist/` instead (see vite.config.js). This
// installs the toolkit's own dependencies and builds it, and records the commit it built, so a
// rebuild happens only when the pinned commit (or its lockfile) changes.

import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const dir = fileURLToPath(new URL('../vendor/geo-toolkit/', import.meta.url))
const at = (path) => `${dir}${path}`

if (!existsSync(at('package.json'))) {
  console.error('vendor/geo-toolkit is empty. Run: git submodule update --init vendor/geo-toolkit')
  process.exit(1)
}

const run = (command, args) => execFileSync(command, args, { cwd: dir, stdio: ['ignore', 'ignore', 'inherit'] })
const read = (path) => (existsSync(at(path)) ? readFileSync(at(path), 'utf8') : null)
const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm'

let commit = 'unknown'
try { commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: dir, encoding: 'utf8' }).trim() } catch { /* not a checkout */ }
const lock = createHash('sha256').update(read('package-lock.json') ?? '').digest('hex')
const stamp = JSON.stringify({ commit, lock })

if (read('node_modules/.pofbc-install') !== lock) {
  run(npm, ['ci', '--no-audit', '--no-fund', '--ignore-scripts'])
  writeFileSync(at('node_modules/.pofbc-install'), lock)
}
if (commit === 'unknown' || read('dist/.pofbc-build') !== stamp) {
  run(npm, ['run', 'build', '--silent'])
  writeFileSync(at('dist/.pofbc-build'), stamp)
  console.log(`  geo-toolkit        built ${commit.slice(0, 7)}`)
} else {
  console.log(`  geo-toolkit        ${commit.slice(0, 7)} already built`)
}
