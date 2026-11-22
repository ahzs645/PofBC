// Assembles the Signs view's "Proposed park symbols, 1971" from the 22 reconstructed pictograms in
// artwork/recreation-conservation/park_symbols/ (see that folder's README and the research package
// research/identity/recreation-conservation-2026-11-21/notes/park_symbols.md).
//
// The pictograms are placed as the 1971 annual report prints them (PDF page 68): four to a row in
// the order of the package's manifest, five full rows and two on the last. Each file's drawing is
// kept as it is, moved into its cell; its title and description go, and its one id, the circle it
// is clipped to, is renamed so 22 of them can share a page. The package's own contact sheet is not
// used: its outlined captions are modern editorial labels, and its subtitle lost its spaces when it
// was outlined.
//
// Writes src/signs/parks/proposed-park-symbols.svg. Run: node scripts/build-park-symbols-sign.mjs

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const folder = resolve(root, 'artwork/recreation-conservation/park_symbols')
const manifest = JSON.parse(readFileSync(resolve(root,
  'research/identity/recreation-conservation-2026-11-21/construction/park_symbols/manifest.json'), 'utf8'))
const target = resolve(root, 'src/signs/parks/proposed-park-symbols.svg')

/** The site's id for a pictogram: its manifest id without the number, which a selector cannot start with. */
export const symbolId = (manifestId) => `pps-${manifestId.replace(/^\d+_/, '').replace(/_/g, '-')}`

const COLUMNS = 4
const PITCH = 250
const MARGIN = 25
const SIZE = 200

const cells = manifest.symbols.map(({ id: manifestId, name }, index) => {
  const source = readFileSync(resolve(folder, `${manifestId}.svg`), 'utf8')
  const svg = source.match(/<svg\b([^>]*)>([\s\S]*)<\/svg>\s*$/)
  if (!/viewBox="0 0 200 200"/.test(svg?.[1] ?? '')) throw new Error(`${manifestId}: expected a 200-unit drawing`)
  for (const banned of ['image', 'text', 'script', 'style', 'foreignObject', 'use']) {
    if (new RegExp(`<${banned}\\b`).test(svg[2])) throw new Error(`${manifestId}: has a <${banned}>`)
  }
  const id = symbolId(manifestId)
  const body = svg[2]
    .replace(/<(title|desc)\b[^>]*>[\s\S]*?<\/\1>/g, '')
    .replace(/\sid="circle_clip_[^"]*"/g, ` id="${id}-clip"`)
    .replace(/url\(#circle_clip_[^)]*\)/g, `url(#${id}-clip)`)
    .replace(/\s*\n\s*/g, '')
  if ((body.match(/\sid="/g) ?? []).length !== 1) throw new Error(`${manifestId}: unexpected ids`)
  const x = MARGIN + (index % COLUMNS) * PITCH
  const y = MARGIN + Math.floor(index / COLUMNS) * PITCH
  return { id, name, x, y, markup: `<g id="${id}" transform="translate(${x} ${y})">${body}</g>` }
})

const width = COLUMNS * PITCH
const height = Math.ceil(cells.length / COLUMNS) * PITCH
const drawing = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">` +
  '<title>Proposed park symbols, 1971: the 22 pictograms of the Department of Recreation and Conservation’s annual report, reconstructed</title>' +
  `<rect id="pps-page" width="${width}" height="${height}" fill="#ffffff"/>` +
  cells.map((cell) => cell.markup).join('') +
  '</svg>\n'

mkdirSync(dirname(target), { recursive: true })
writeFileSync(target, drawing)
console.log(`Wrote ${cells.length} symbols, ${width} × ${height}, to ${target}`)
for (const { id, name, x, y } of cells) console.log(`  ${id.padEnd(32)} ${name.padEnd(26)} box ${x} ${y} ${SIZE} ${SIZE}`)
