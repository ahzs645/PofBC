// Builds every era, packs it, and puts the packs in one release zip:
//
//   npm run brandkit:release                   brandkit/out/release/pofbc-brandkit-<date>-<commit>.zip
//   npm run brandkit:release -- --name 2026.11 brandkit/out/release/pofbc-brandkit-2026.11.zip
//
// The zip holds a folder of the same name with:
//
//   <id>.zip, <id>.logo.svg   each era's brand pack and its menu logo
//   catalog.json              every pack, with its SHA-256
//   README.md                 what each era is, and how to open the packs
//
// The bundle (every pack again, in one file) is left out, since it would double the zip;
// npm run brandkit:pack still writes it to brandkit/out/packs.
//
// Packs are stored, not recompressed, and every entry has a fixed date, so the same commit gives
// the same zip byte for byte.

import { spawnSync } from 'node:child_process'
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { zipSync } from 'fflate'
import { ERAS } from '../eras.mjs'
import { ROOT } from './lib/paths.mjs'

const args = process.argv.slice(2)
const nameAt = args.indexOf('--name')
const git = (...command) => spawnSync('git', command, { cwd: ROOT, encoding: 'utf8' }).stdout.trim()
const commit = git('rev-parse', '--short', 'HEAD') || 'local'
const dirty = git('status', '--porcelain', '--', 'brandkit', 'artwork', 'src') ? '-modified' : ''
const date = (git('log', '-1', '--format=%cs') || new Date().toISOString().slice(0, 10))
const version = nameAt >= 0 ? args[nameAt + 1] : `${date}-${commit}${dirty}`
const name = `pofbc-brandkit-${version}`

const packs = resolve(ROOT, process.env.BRANDKIT_PACKS ?? 'brandkit/out/packs')
const packed = spawnSync(process.execPath, [resolve(ROOT, 'brandkit/scripts/pack.mjs')], { cwd: ROOT, stdio: 'inherit', env: { ...process.env, BRANDKIT_PACKS: packs } })
if (packed.status !== 0) process.exit(packed.status ?? 1)

const catalog = JSON.parse(readFileSync(resolve(packs, 'catalog.json'), 'utf8'))
const size = (bytes) => `${(bytes / 1024 / 1024).toFixed(1)} MB`
const readme = `# Province of British Columbia: every identity, as brandkit packs

Release ${version}, built from PofBC commit ${commit}${dirty ? ' (with uncommitted changes)' : ''} by \`npm run brandkit:release\`.

Open a pack in [brandkit](https://github.com/ahzs645/brandkit) by dropping it on the page, with
**⋯ → Open a brand…**, or by link (\`?url=<address of the zip>\`). \`catalog.json\` lists every pack with its SHA-256; host the folder anywhere that sends
\`Access-Control-Allow-Origin\` and open \`?catalog=<address of catalog.json>\`.

| Pack | Era | Years | Size |
| --- | --- | --- | --- |
${ERAS.map((era) => {
  const entry = catalog.packs.find((pack) => pack.id === era.id)
  return `| \`${era.id}.zip\` | ${era.label} | ${era.years} | ${size(entry.bytes)} |`
}).join('\n')}

${ERAS.map((era) => `- **${era.label}** (${era.years}): ${era.summary}`).join('\n')}

Every brand is a historical reconstruction or a reference kit built from published artwork: none
is the Province's current identity or a source of approved marks. Each pack carries its fonts'
licences, its sources and what is not established about it (its README.md and USE.md).
`

const FIXED = new Date('2000-01-01T00:00:00Z')
const files = {}
for (const file of readdirSync(packs).filter((entry) => !entry.endsWith('.bundle.zip')).sort()) {
  const bytes = new Uint8Array(readFileSync(resolve(packs, file)))
  files[`${name}/${file}`] = [bytes, { mtime: FIXED, level: file.endsWith('.zip') ? 0 : 9 }]
}
files[`${name}/README.md`] = [new TextEncoder().encode(readme), { mtime: FIXED, level: 9 }]

const out = resolve(ROOT, 'brandkit/out/release')
mkdirSync(out, { recursive: true })
const zip = zipSync(files)
writeFileSync(resolve(out, `${name}.zip`), zip)
console.log(`${name}.zip: ${Object.keys(files).length} files, ${size(zip.length)} → ${out}`)
