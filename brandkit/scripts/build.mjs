// Writes a brandkit brand folder for each of the Province's identities (brandkit/eras.mjs), ready
// for brandkit to open or for scripts/pack.mjs to pack.
//
//   npm run brandkit:build                       every era
//   npm run brandkit:build -- bc-province-1977   one or more, by id
//
// For each era: <out>/<id>/ is emptied, brandkit/sources/<id>/ and brandkit/shared/ copied into it, the era's script
// writes brand.json (and whatever pages it makes), then USE.md and logo-menu.svg are drawn from
// that brand.json and the whole folder is checked with brandkit's own validator, fonts and files.

import { spawnSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { ERAS } from '../eras.mjs'
import { BRANDKIT, OUT, ROOT, SHARED, SOURCES } from './lib/paths.mjs'

if (!existsSync(resolve(BRANDKIT, 'src/engine/brand.js'))) {
  console.error('vendor/brandkit is not checked out. Run: git submodule update --init vendor/brandkit')
  process.exit(1)
}
// The current era sets names with PofBC's alphabet, whose optional extension module is generated
// (and is a stub without a licensed Garamond): make it if this checkout has not yet.
if (!existsSync(resolve(ROOT, 'src/current/generated/nameGlyphsExtra.js'))) {
  const made = spawnSync(process.execPath, [resolve(ROOT, 'scripts/build-current-extras.mjs')], { cwd: ROOT, stdio: 'inherit' })
  if (made.status !== 0) process.exit(made.status ?? 1)
}
const engine = (path) => import(new URL(`../../vendor/brandkit/${path}`, import.meta.url))
const { validateBrand } = await engine('src/engine/brand.js')
const { loadBrandFontsFromDisk } = await engine('src/fonts/node.js')
const { documentationMarkdown } = await engine('src/engine/documentation.js')
const { menuLogo } = await engine('src/app/masthead.js')

const wanted = process.argv.slice(2).filter((arg) => !arg.startsWith('--'))
for (const id of wanted) if (!ERAS.some((era) => era.id === id)) throw new Error(`No era ${id}. Known: ${ERAS.map((era) => era.id).join(', ')}`)
const eras = wanted.length ? ERAS.filter((era) => wanted.includes(era.id)) : ERAS

mkdirSync(OUT, { recursive: true })
for (const era of eras) {
  const folder = resolve(OUT, era.id)
  rmSync(folder, { recursive: true, force: true })
  mkdirSync(folder, { recursive: true })
  const sources = resolve(SOURCES, era.id)
  if (existsSync(sources)) cpSync(sources, folder, { recursive: true })
  // Every era sets its labels, and three set their type, in TeX Gyre (brandkit/shared/fonts).
  cpSync(resolve(SHARED, 'fonts'), resolve(folder, 'fonts'), { recursive: true })

  await import(new URL(era.script, new URL('../eras.mjs', import.meta.url)))

  const brand = JSON.parse(readFileSync(resolve(folder, 'brand.json'), 'utf8'))
  // The era's place in the sequence, for catalogs and brand menus.
  brand.description = `${era.label}, ${era.years}. ${era.summary}`
  brand.era = { order: ERAS.indexOf(era) + 1, of: ERAS.length, label: era.label, years: era.years, sequence: ERAS.map(({ id, label, years }) => ({ id, label, years })) }
  writeFileSync(resolve(folder, 'brand.json'), `${JSON.stringify(brand, null, 1)}\n`)
  const problems = validateBrand(brand)
  if (problems.length) throw new Error(`${era.id}:\n${problems.join('\n')}`)
  const fonts = await loadBrandFontsFromDisk(brand, folder)
  if (fonts.failures.length) throw new Error(`${era.id}: fonts failed to load: ${fonts.failures.map(({ key, error }) => `${key}: ${error.message}`).join('; ')}`)
  for (const file of brand.files ?? []) {
    const from = typeof file === 'string' ? file : file.from
    if (!existsSync(resolve(folder, from))) throw new Error(`${era.id}: brand.json lists ${from}, which is not in the folder`)
  }
  writeFileSync(resolve(folder, 'USE.md'), documentationMarkdown(brand))
  writeFileSync(resolve(folder, 'logo-menu.svg'), menuLogo(brand, fonts))
  console.log(`${era.id} → ${folder}`)
}
