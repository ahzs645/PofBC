// Writes <out>/bc-province-engraved-arms/brand.json: the Province before the 1977 Visual Identity
// Program, when ministers' stationery carried the full coat of arms, engraved, over formal script.
//
// The era starts with one piece: Grace M. McCarthy's calling card (Deputy Premier, Provincial
// Secretary, Minister of Recreation & Travel Industry), from the reconstruction in
// brandkit/sources/bc-province-engraved-arms/ (see its docs/RECONSTRUCTION.md). Every position and
// size below is that reconstruction's, on its 1800 × 1038 artboard:
//
//   - the arms are the supplied engraving (artwork/arms.svg), kept at their own proportions and
//     fitted to the height the card's crest stands, 239.7 px, from (221.2, 102.4);
//   - each line is set in the PlateForge Card Script study cut the reconstruction fitted to it, at
//     its size and baseline; the name and titles are centred on the axis their reference text was
//     set on, so edited wording stays centred, and Telephone stays flush left where it begins.
//
// The card's historical typeface, ink colour, date and printed size are not established; the
// fidelity notes say so wherever the template is shown.
//
//   npm run brandkit:build -- bc-province-engraved-arms

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import opentype from 'opentype.js'
import { folderOf, HEROS, HEROS_FILES, readSvg, round, writeEraBrand } from '../lib/era.mjs'

const ID = 'bc-province-engraved-arms'
const folder = folderOf(ID)

// --- The arms: the supplied path, preserved byte for byte, moved to the origin.
const arms = readSvg(resolve(folder, 'artwork/arms.svg'))
const [ax, ay, aw, ah] = arms.viewBox
const symbol = {
  name: 'arms-engraved',
  title: 'Arms of British Columbia (engraved)',
  masterTitle: 'Arms of British Columbia, engraved (supplied substitute)',
  masterDescription: 'The coat-of-arms engraving supplied with the calling-card reconstruction. It is a different engraving from the one printed on the card (different ribbon and supporters) and is kept at its own proportions rather than stretched to match.',
  viewBox: [0, 0, aw, ah],
  markup: `<g transform="translate(${-ax} ${-ay})">${arms.inner.replace(/\sfill="currentColor"/g, '')}</g>`
}

// --- The three study cuts, and the card's lines in them.
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

// The reconstruction's editable SVG: each line's start, baseline and size, and which cut it is in.
const LINES = [
  { id: 'name', text: 'Grace M. McCarthy', font: 'display', x: 469.6441088, y: 471.9843445, size: 131.9138233, anchor: 'middle', label: 'Name' },
  { id: 'title-1', text: 'Deputy Premier', font: 'compact', x: 726.6109534, y: 550.2974443, size: 88.1415695, anchor: 'middle', label: 'Title, first line' },
  { id: 'title-2', text: 'Provincial Secretary', font: 'compact', x: 689.4304434, y: 628.5609298, size: 86.6693911, anchor: 'middle', label: 'Title, second line' },
  { id: 'title-3', text: 'Minister of Recreation & Travel Industry', font: 'compact', x: 467.2423829, y: 704.5280365, size: 82.7330832, anchor: 'middle', label: 'Title, third line' },
  { id: 'telephone-line', text: 'Telephone 387-6601', font: 'script', x: 129.5233579, y: 897.7123003, size: 89.1322682, anchor: 'start', label: 'Telephone line' },
  { id: 'city', text: 'Victoria', font: 'script', x: 1354.7088161, y: 828.257918, size: 87.4916078, anchor: 'middle', label: 'City' },
  { id: 'province', text: 'British Columbia', font: 'script', x: 1231.509002, y: 903.5416071, size: 86.7582471, anchor: 'middle', label: 'Province' }
]
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
  ...(line.anchor === 'middle' ? { anchor: 'middle', fitWidth: line.id === 'name' ? 1180 : 1080 } : { fitWidth: 760 })
}))

const ARMS_HEIGHT = round(ah * 0.1923688, 2)
const card = {
  id: 'minister-calling-card',
  label: 'Calling card, Minister (engraved arms)',
  group: 'Calling cards',
  title: '{name} / Minister’s calling card, engraved arms',
  description: 'A minister’s calling card of the engraved-arms years, rebuilt from a photograph of Grace M. McCarthy’s card: the arms in olive-gold at the upper left, the name and portfolios centred in formal script, telephone at the foot, city and province at the right.',
  width: 1800,
  height: 1038,
  raster: 1800,
  elements: [
    { type: 'background', fill: 'paper' },
    { type: 'symbol', id: 'arms', x: round(217.5219135 + ax * 0.1923688, 2), y: round(98.552623 + ay * 0.1923688, 2), height: ARMS_HEIGHT, colour: 'symbol' },
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
  source: 'Grace M. McCarthy calling-card reconstruction (photograph, supplied arms engraving, PlateForge Card Script studies): brandkit/sources/bc-province-engraved-arms in PofBC.',
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
    'reference/source-card.png',
    'reference/rectified-reference.png',
    'reference/card-reconstruction.png',
    'reference/grace-mccarthy-font-comparison.png',
    'reference/grace-mccarthy-font-overlays.png',
    'reference/card-project.json',
    ...['geometry', 'reference-layout', 'editor-validation', 'validation', 'font-study'].map((name) => `reference/evidence/${name}.json`),
    'reference/evidence/supplied-arms-fragment.txt',
    ...Object.values(FONT_DIRS).flatMap((dir) => ['OFL.txt', 'provenance.json'].map((name) => `fonts/${dir}/${name}`)),
    ...Object.keys(FONT_DIRS).map(fontFile),
    ...HEROS_FILES
  ]
}

writeEraBrand(brand)
