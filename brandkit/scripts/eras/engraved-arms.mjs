// Writes <out>/bc-province-engraved-arms/brand.json: the Province before the 1977 Visual Identity
// Program, when ministers' stationery carried the full coat of arms, engraved, over formal script.
//
// The era starts with one piece: Grace M. McCarthy's calling card (Deputy Premier, Provincial
// Secretary, Minister of Recreation & Travel Industry). Its source is the reconstruction package
// in artwork/stationery/grace-mccarthy/ (see its RECONSTRUCTION.md), and everything here is read
// from that package's editable SVG, on its 1800 × 1038 artboard, rather than copied by hand:
//
//   - the arms: the supplied engraving's path, byte for byte, and where the card places it
//     (<g id="coat-of-arms" transform="translate(…) scale(…)">), written out as artwork/arms.svg;
//   - each line: its text, start, baseline, size and the PlateForge Card Script study cut it is set
//     in (<text id="name" …> and the six others). The name and titles are centred on the axis their
//     reference text was set on, so edited wording stays centred; Telephone stays flush left.
//
// Replace the package (a corrected font cut, a refitted line, a better arms drawing) and rebuild:
// the brand follows. The card's historical typeface, ink colour, date and printed size are not
// established; the fidelity notes say so wherever the template is shown.
//
//   npm run brandkit:build -- bc-province-engraved-arms

import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import opentype from 'opentype.js'
import { ROOT } from '../lib/paths.mjs'
import { folderOf, HEROS, HEROS_FILES, round, writeEraBrand } from '../lib/era.mjs'

const ID = 'bc-province-engraved-arms'
const folder = folderOf(ID)
const SOURCE = resolve(ROOT, 'artwork/stationery/grace-mccarthy')

// --- The package's files, into the brand folder at the paths the kit lists them under.
const COPY = {
  'docs/RECONSTRUCTION.md': 'RECONSTRUCTION.md',
  'docs/card-editor.html': 'grace-mccarthy-card-editor.html',
  'reference/card-editable.svg': 'grace-mccarthy-card-editable.svg',
  'reference/card-outlined.svg': 'grace-mccarthy-card-outlined.svg',
  'reference/card-reconstruction.png': 'grace-mccarthy-card.png',
  'reference/card-project.json': 'grace-mccarthy-card-project.json',
  'reference/grace-mccarthy-font-comparison.png': 'grace-mccarthy-font-comparison.png',
  'reference/grace-mccarthy-font-overlays.png': 'grace-mccarthy-font-overlays.png',
  'reference/source-card.png': 'evidence/source-card.png',
  'reference/rectified-reference.png': 'evidence/rectified-reference.png',
  ...Object.fromEntries(['geometry', 'reference-layout', 'editor-validation', 'validation', 'font-study'].map((name) => [`reference/evidence/${name}.json`, `evidence/${name}.json`])),
  'reference/evidence/supplied-arms-fragment.txt': 'evidence/supplied-arms-fragment.txt'
}
for (const [to, from] of Object.entries(COPY)) {
  mkdirSync(dirname(resolve(folder, to)), { recursive: true })
  cpSync(resolve(SOURCE, from), resolve(folder, to))
}
cpSync(resolve(SOURCE, 'fonts'), resolve(folder, 'fonts'), { recursive: true })

const cardSvg = readFileSync(resolve(SOURCE, 'grace-mccarthy-card-editable.svg'), 'utf8')
const [, artboardWidth, artboardHeight] = /<svg[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(cardSvg).map(Number)
const unescape = (value) => value.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')

// --- The arms: the card's coat-of-arms group, its path kept exactly, moved to the origin.
const group = /<g id="coat-of-arms"[^>]*transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)"[^>]*>([\s\S]*?)<\/g>/.exec(cardSvg)
if (!group) throw new Error('grace-mccarthy-card-editable.svg: no <g id="coat-of-arms" transform="translate(…) scale(…)">')
const [, tx, ty, scale] = group.slice(0, 4).map(Number)
const path = /<path([^>]*)\sd="([^"]+)"/.exec(group[4])
const fillRule = /fill-rule="([^"]+)"/.exec(path[1])?.[1]
const d = path[2]
// The ink box, from the path's own points (every command is absolute M, L, C or Z).
const points = [...d.replace(/[MLCZ]/g, ' ').matchAll(/-?(?:\d+\.?\d*|\.\d+)/g)].map((match) => Number(match[0]))
const xs = points.filter((_, index) => index % 2 === 0)
const ys = points.filter((_, index) => index % 2 === 1)
const [ax, ay] = [Math.min(...xs), Math.min(...ys)]
const [aw, ah] = [Math.max(...xs) - ax, Math.max(...ys) - ay]
const armsPath = `<path${fillRule ? ` fill-rule="${fillRule}"` : ''} d="${d}"/>`
mkdirSync(resolve(folder, 'artwork'), { recursive: true })
writeFileSync(resolve(folder, 'artwork/arms.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${ax} ${ay} ${aw} ${ah}" width="${aw}" height="${ah}">\n<title>Arms of British Columbia (supplied engraving)</title>\n<desc>The coat-of-arms path supplied with the Grace M. McCarthy calling-card reconstruction, preserved exactly. A different engraving from the one printed on the card; see reference/evidence.</desc>\n${armsPath.replace('<path', '<path fill="currentColor"')}\n</svg>\n`)
const symbol = {
  name: 'arms-engraved',
  title: 'Arms of British Columbia (engraved)',
  masterTitle: 'Arms of British Columbia, engraved (supplied substitute)',
  masterDescription: 'The coat-of-arms engraving supplied with the calling-card reconstruction. It is a different engraving from the one printed on the card (different ribbon and supporters) and is kept at its own proportions rather than stretched to match.',
  viewBox: [0, 0, aw, ah],
  markup: `<g transform="translate(${-ax} ${-ay})">${armsPath}</g>`
}

// --- The study cuts, by the family names the SVG sets its lines in.
const FONT_DIRS = {
  display: 'plateforgecardscriptdisplaystudy',
  compact: 'plateforgecardscriptcompactstudy',
  script: 'plateforgecardscriptstudy'
}
const FAMILY = {
  display: 'PlateForge Card Script Display Study',
  compact: 'PlateForge Card Script Compact Study',
  script: 'PlateForge Card Script Study'
}
const fontFile = (key) => `fonts/${FONT_DIRS[key]}/${FAMILY[key].replace(/ /g, '')}-Regular.ttf`
const parsed = Object.fromEntries(Object.keys(FONT_DIRS).map((key) => {
  const bytes = readFileSync(resolve(folder, fontFile(key)))
  return [key, opentype.parse(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength))]
}))
const face = (key, label) => ({
  family: FAMILY[key],
  stack: `"${FAMILY[key]}", "Pinyon Script", cursive`,
  weight: 400,
  file: fontFile(key),
  web: fontFile(key),
  label,
  note: 'A source-informed study derived from the open Pinyon Script, fitted to the photographed card. Not an authenticated historical typeface.'
})

// --- The card's lines: the SVG's ids, as the template's fields.
const FIELDS = {
  name: { id: 'name', label: 'Name', anchor: 'middle', fitWidth: 1180 },
  deputy: { id: 'title-1', label: 'Title, first line', anchor: 'middle', fitWidth: 1080 },
  secretary: { id: 'title-2', label: 'Title, second line', anchor: 'middle', fitWidth: 1080 },
  minister: { id: 'title-3', label: 'Title, third line', anchor: 'middle', fitWidth: 1080 },
  telephone: { id: 'telephone-line', label: 'Telephone line', anchor: 'start', fitWidth: 760 },
  city: { id: 'city', label: 'City', anchor: 'middle', fitWidth: 1080 },
  province: { id: 'province', label: 'Province', anchor: 'middle', fitWidth: 1080 }
}
const attribute = (tag, name) => new RegExp(`\\s${name}=(?:"([^"]*)"|'([^']*)')`).exec(tag)?.slice(1).find((value) => value != null)
const LINES = [...cardSvg.matchAll(/(<text\b[^>]*>)([^<]*)<\/text>/g)].map(([, tag, content]) => {
  const field = FIELDS[attribute(tag, 'id')]
  if (!field) return null
  const families = attribute(tag, 'font-family')
  const font = Object.keys(FAMILY).find((key) => families.includes(`"${FAMILY[key]}"`))
  if (!font) throw new Error(`Line ${attribute(tag, 'id')} is set in ${families}, which is none of the study cuts`)
  return { ...field, text: unescape(content), font, x: Number(attribute(tag, 'x')), y: Number(attribute(tag, 'y')), size: Number(attribute(tag, 'font-size')) }
}).filter(Boolean)
const missing = Object.values(FIELDS).filter((field) => !LINES.some((line) => line.id === field.id)).map((field) => field.id)
if (missing.length) throw new Error(`grace-mccarthy-card-editable.svg has no line for ${missing.join(', ')}`)

const FONT_ROLE = { display: 'display', compact: 'displayRegular', script: 'body' }
const advance = ({ font, text, size }) => parsed[font].getAdvanceWidth(text, size)
const cardElements = LINES.map((line) => ({
  type: 'text',
  id: line.id,
  text: line.text,
  x: round(line.anchor === 'middle' ? line.x + advance(line) / 2 : line.x, 2),
  y: round(line.y, 2),
  size: round(line.size, 3),
  font: FONT_ROLE[line.font],
  colour: 'ink',
  ...(line.anchor === 'middle' ? { anchor: 'middle' } : {}),
  fitWidth: line.fitWidth
}))

const ARMS_HEIGHT = round(ah * scale, 2)
const card = {
  id: 'minister-calling-card',
  label: 'Calling card, Minister (engraved arms)',
  group: 'Calling cards',
  title: '{name} / Minister’s calling card, engraved arms',
  description: 'A minister’s calling card of the engraved-arms years, rebuilt from a photograph of Grace M. McCarthy’s card: the arms in olive-gold at the upper left, the name and portfolios centred in formal script, telephone at the foot, city and province at the right.',
  width: artboardWidth,
  height: artboardHeight,
  raster: artboardWidth,
  elements: [
    { type: 'background', fill: 'paper' },
    { type: 'symbol', id: 'arms', x: round(tx + ax * scale, 2), y: round(ty + ay * scale, 2), height: ARMS_HEIGHT, colour: 'symbol' },
    ...cardElements
  ],
  reference: {
    src: 'reference/rectified-reference.png',
    label: 'The photographed card, perspective-corrected',
    note: 'User-supplied photograph (2048 × 1179), rectified to the 1800 × 1038 artboard from estimated paper corners; the upper-right corner is uncertain by roughly 10–20 px. See reference/evidence/geometry.json.'
  },
  fidelity: {
    status: 'reconstruction',
    label: 'Reconstruction from one photograph',
    note: 'The lettering is set in source-informed study fonts derived from Pinyon Script, not the original typeface, which is unidentified. The arms are a different engraving from the card’s. Ink colours are visual approximations, and the card’s printed size and date are not established by the photograph, so the artboard keeps the photograph’s proportions (1800 × 1038) without claiming a physical size.'
  }
}

export const brand = {
  schema: 'brandkit/1',
  id: ID,
  name: 'Province of British Columbia (engraved arms)',
  version: 'pre-1977-engraved-arms',
  displayVersion: 'Before 1977',
  source: 'Grace M. McCarthy calling-card reconstruction (photograph, supplied arms engraving, PlateForge Card Script studies): artwork/stationery/grace-mccarthy in PofBC.',
  status: 'A historical reconstruction for reference and study, from a single photographed card. Not the Province’s current identity.',
  colours: { ink: '#171716', gold: '#807953', paper: '#FFFFFF', black: '#000000', white: '#FFFFFF', parchment: '#F4F1E8' },
  colourNames: { ink: 'Engraving black', gold: 'Olive-gold (arms)', parchment: 'Card stock' },
  roles: { ink: 'ink', paper: 'paper', muted: 'ink', primary: 'gold', light: 'parchment', reverse: 'white', line: '#D8D4C8', rule: 'ink', symbol: 'gold', type: 'ink' },
  print: { note: 'Screen approximations sampled from a photograph. The card’s ink colours and process (engraved, thermographed or offset) are not established.' },
  colourways: {
    engraved: { label: 'Olive-gold arms', roles: { symbol: 'gold', type: 'ink' } },
    black: { label: 'One colour: black', all: 'ink' },
    reverse: { label: 'Reverse: white', all: 'white', ground: 'ink' }
  },
  defaultColourway: 'engraved',
  logoColours: ['gold', 'ink', 'white', 'currentColor'],
  rasterColours: ['gold', 'ink', 'white'],
  fonts: {
    display: face('display', 'Card script, display (name)'),
    displayRegular: face('compact', 'Card script, compact (titles)'),
    body: face('script', 'Card script (telephone, city, province)'),
    bold: face('display', 'Card script, display'),
    extra: face('display', 'Card script, display'),
    label: HEROS.regular,
    regular: HEROS.regular,
    medium: HEROS.bold
  },
  typography: {
    headlines: { family: FAMILY.display, weight: 400, trackingEm: 0 },
    body: { family: FAMILY.script, weight: 400 },
    labels: { family: 'TeX Gyre Heros', weight: 400, trackingEm: 0.06 },
    note: 'Formal engraved (copperplate) script on the card; its typeface is unidentified. The study cuts are fitting choices for name, titles and footer, not evidence of three historical typefaces. Labels in this kit’s own pages are set in TeX Gyre Heros, which is not period evidence.'
  },
  symbol,
  signatures: [
    {
      id: 'arms',
      label: 'The arms',
      use: 'The engraved coat of arms on its own, as it heads the minister’s card: no logotype, no ministry signature.',
      elements: [{ type: 'symbol', x: 0, y: 0, height: 1000 }]
    }
  ],
  lockup: { canvasPadding: 0, clearspaceRecommendation: 'The arms appear complete and upright, never cropped, stretched or recoloured part by part.', minimumHorizontalWidthPx: 64, minimumHorizontalWidthMm: 10 },
  fields: Object.fromEntries(LINES.map((line) => [line.id, { label: line.label, placeholder: line.text }])),
  copy: {
    svgDescription: 'Province of British Columbia before 1977: engraved arms and formal script, reconstructed from one photographed card for reference. Not the Province’s current identity.',
    templateDescription: 'Province of British Columbia, engraved-arms years (before 1977), reconstructed. Not the Province’s current identity.',
    logoLabel: 'Arms of British Columbia',
    motifLabel: 'Arms of British Columbia (engraved)',
    tagline: 'Splendor sine occasu.'
  },
  templates: [card],
  web: {
    componentName: 'BcEngravedArms',
    symbolComponentName: 'BcEngravedArmsSymbol',
    cssPrefix: 'bcarms',
    appIcon: { background: 'paper', colour: 'primary', size: 860 },
    favicon: { light: '#807953', dark: '#FFFFFF', size: 60, micro: false, title: '{name} favicon' },
    intro: { eyebrow: 'Engraved arms / before 1977', headline: 'Province of\nBritish Columbia', body: 'The Province before its 1977 Visual Identity Program: the full coat of arms, engraved, over formal script. Rebuilt from Grace M. McCarthy’s calling card. A historical reference, not the Province’s current identity.', edition: 'Engraved-arms reconstruction', footer: 'Province of British Columbia, before 1977. A reconstruction for reference; not the current provincial identity.' },
    landing: { eyebrow: 'Historical reference', headline: 'Province of\nBritish Columbia\nbefore 1977', body: 'Engraved arms and formal script, from a minister’s calling card.', cta: 'Open the card', contactEyebrow: 'Not current guidance', contactBody: 'For the Province’s current identity, see the Government of British Columbia.', footer: 'Engraved arms, before 1977 (reconstruction).' }
  },
  files: [
    { to: 'README.md', from: 'docs/README.md' },
    'docs/RECONSTRUCTION.md',
    'docs/card-editor.html',
    'artwork/arms.svg',
    ...Object.keys(COPY).filter((path) => !path.startsWith('docs/')),
    ...Object.values(FONT_DIRS).flatMap((dir) => ['OFL.txt', 'provenance.json'].map((name) => `fonts/${dir}/${name}`)),
    ...Object.keys(FONT_DIRS).map(fontFile),
    ...HEROS_FILES
  ]
}

writeEraBrand(brand)
