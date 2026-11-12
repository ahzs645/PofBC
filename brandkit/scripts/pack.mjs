// Packs each of the Province's identities as a brandkit brand pack: one zip per era, a catalog
// listing them, and a bundle holding all of them.
//
//   npm run brandkit:pack                                   build every era, then pack it
//   npm run brandkit:pack -- bc-province-flag               one or more eras, by id
//   npm run brandkit:pack -- --no-build                     pack what <out> already holds
//   npm run brandkit:pack -- --base-url https://host/path/  catalog entries as absolute addresses
//
// Writes to brandkit/out/packs (BRANDKIT_PACKS overrides it):
//
//   <id>.zip              the era's pack: open it in brandkit by dropping it on the page, with
//                         ⋯ → Open a brand…, or by link (?url=<address of the zip>)
//   <id>.logo.svg         its logo for brandkit's brand menu
//   catalog.json          every pack, for ?catalog=<address> or VITE_BRANDKIT_CATALOGS
//   bc-province.bundle.zip every pack in one file, which adds all the eras at once
//
// Packing is brandkit's own (vendor/brandkit/src/pack), so the packs are exactly what brandkit
// reads; they come out byte for byte the same from the same folders.

import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { ERAS } from '../eras.mjs'
import { OUT, ROOT } from './lib/paths.mjs'

const args = process.argv.slice(2)
const option = (name) => {
  const index = args.indexOf(name)
  return index < 0 ? undefined : args.splice(index, 2)[1]
}
const baseUrl = option('--base-url')
const noBuild = args.includes('--no-build')
const ids = args.filter((arg) => !arg.startsWith('--'))
for (const id of ids) if (!ERAS.some((era) => era.id === id)) throw new Error(`No era ${id}. Known: ${ERAS.map((era) => era.id).join(', ')}`)
const eras = ids.length ? ERAS.filter((era) => ids.includes(era.id)) : ERAS

const run = (script, scriptArgs) => {
  const result = spawnSync(process.execPath, [script, ...scriptArgs], { stdio: 'inherit', cwd: ROOT })
  if (result.status !== 0) process.exit(result.status ?? 1)
}

if (!noBuild) run(resolve(ROOT, 'brandkit/scripts/build.mjs'), eras.map((era) => era.id))
for (const era of eras) if (!existsSync(resolve(OUT, era.id, 'brand.json'))) throw new Error(`${era.id} has not been built: run npm run brandkit:build`)

const out = resolve(ROOT, process.env.BRANDKIT_PACKS ?? 'brandkit/out/packs')
const { pack } = await import(new URL('../../vendor/brandkit/src/pack/cli.js', import.meta.url))
pack([
  ...eras.map((era) => resolve(OUT, era.id)),
  '--out', out,
  '--name', 'Province of British Columbia, every identity',
  ...(baseUrl ? ['--base-url', baseUrl] : []),
  ...(eras.length > 1 ? ['--bundle', 'bc-province.bundle.zip'] : [])
])
