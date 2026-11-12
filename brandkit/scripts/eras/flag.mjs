// Writes <out>/bc-province-flag/brand.json: the flag identity (about 1983–2005), BC beside the
// waving provincial flag, with a ministry set beside or below it.
//
// Nothing here is measured afresh. The flag is PofBC's drawing (src/assets/flagMark.js, twelve
// shapes as supplied), and every distance comes from PofBC's layout (src/flag/flagLayout.js),
// which carries the seventeen printed references it was read from. The signatures are that
// layout run at a BC cap height of 100 and written down as brandkit elements, so the two cannot
// disagree about where anything goes:
//
//   - the flag is the brand's symbol, its three colours as roles ({blue}, {red}, {yellow}) so a
//     colourway can paint them, and its white left as the page, as on the printed documents;
//   - "BC" is Helvetica Bold, the ministry Helvetica Regular, set here in TeX Gyre Heros (the same
//     widths), wrapping to PofBC's measure of 5.5 BC caps on 13/12 leading.
//
// One approximation: set beside the symbol, PofBC grows the wording upward so its last line sits
// on the BC baseline. brandkit hangs a stack from its first line, so the beside signature is
// placed for a two-line ministry ("Ministry of / Forests"), the commonest; a longer one runs below.
//
//   npm run brandkit:build -- bc-province-flag

import { pofbc } from '../lib/paths.mjs'
import { HEROS, HEROS_FILES, round, writeEraBrand } from '../lib/era.mjs'
import { ministriesBetween } from '../lib/ministries.mjs'

const ID = 'bc-province-flag'
const { FLAG } = await pofbc('src/assets/flagMark.js')
const { layoutFlagLockup, NAME_MEASURE, PROVINCE_LINE } = await pofbc('src/flag/flagLayout.js')
const { FLAG_PALETTES } = await pofbc('src/flag/flagPalettes.js')

// The supplied drawing's three fills, as roles.
const SOURCE = Object.keys(FLAG_PALETTES.official.fills)
const ROLE = { [SOURCE[0]]: 'blue', [SOURCE[1]]: 'red', [SOURCE[2]]: 'yellow' }
const symbol = {
  name: 'bc-flag',
  title: 'The BC flag symbol',
  masterTitle: 'The waving provincial flag',
  masterDescription: 'The Spirit of BC flag as the identity carried it: twelve shapes in three colours, the white being the page between them.',
  viewBox: [0, 0, FLAG.width, FLAG.height],
  markup: FLAG.shapes.map((shape) => `<path d="${shape.d}" fill="{${ROLE[shape.fill] ?? 'blue'}}"/>`).join('')
}

const CAP = 100
const PROBE = 'Ministry of\nForests'
const signature = ({ id, label, use, symbolType, placement, province = false, departmental = true }) => {
  const layout = layoutFlagLockup({ symbol: symbolType, placement, province, ministry: departmental ? PROBE : '', cap: CAP })
  const elements = [{ type: 'symbol', x: round(layout.flag.x), y: round(layout.flag.y), height: round(layout.flag.height) }]
  if (layout.letters) elements.push({ type: 'text', text: 'BC', x: round(layout.letters.x), y: 0, size: round(layout.letters.style.fontSize), font: 'bold', role: 'letters' })
  if (departmental) {
    const lines = layout.lines
    const ministryLine = lines.find((line) => line.text !== PROVINCE_LINE)
    const size = round(ministryLine.style.fontSize)
    const leading = round(size * 13 / 12)
    const items = []
    if (province) items.push({ text: PROVINCE_LINE, size: round(lines[0].style.fontSize), font: 'bold', leading })
    items.push({ field: 'ministry', size, font: 'regular', leading, wrap: round(NAME_MEASURE * CAP), ...(province ? { gapBefore: round(leading * 0.45) } : {}) })
    items.push({ field: 'extra', size, font: 'regular', leading, wrap: round(NAME_MEASURE * CAP), gapBefore: round(leading * 0.45), when: 'extra' })
    elements.push({ type: 'stack', id: 'wording', x: round(lines[0].x + lines[0].ink.inkLeft), y: round(lines[0].y), items })
  }
  return {
    id, label, use, ...(departmental ? { departmental: true } : {}),
    metrics: { font: 'bold', capHeight: CAP, baseline: 0, logotypeX: 0 },
    elements
  }
}

const SIGNATURES = [
  signature({ id: 'symbol', label: 'BC and the flag', use: 'The symbol on its own: BC with the flag beside it, foot to foot.', symbolType: 'horizontal', placement: 'below', departmental: false }),
  signature({ id: 'horizontal', label: 'BC and the flag, ministry below', use: 'The commonest form: the ministry under the symbol, flush with its left edge. Measured off “Ministry of Forests”.', symbolType: 'horizontal', placement: 'below' }),
  signature({ id: 'horizontal-beside', label: 'BC and the flag, ministry beside', use: 'The ministry to the right of the symbol, which is then drawn half again as large against the letters, as both documents that set it so do.', symbolType: 'horizontal', placement: 'beside' }),
  signature({ id: 'vertical', label: 'Flag above BC, ministry below', use: 'The flag standing on the letters’ cap line, left edges flush, the ministry beneath.', symbolType: 'vertical', placement: 'below' }),
  signature({ id: 'vertical-province', label: 'Flag above BC, Province of British Columbia and ministry', use: 'As above, with “Province of British Columbia” in bold over the ministry. Measured off “Province of British Columbia · Ministry of Environment”.', symbolType: 'vertical', placement: 'below', province: true }),
  signature({ id: 'flag', label: 'The flag alone, ministry below', use: 'No letters, the flag sized as in the vertical form.', symbolType: 'flag', placement: 'below' })
]

const ministries = await ministriesBetween(1983, 2005)

export const brand = {
  schema: 'brandkit/1',
  id: ID,
  name: 'Province of British Columbia (flag)',
  version: 'flag-1983',
  displayVersion: 'Flag, about 1983–2005',
  source: 'PofBC’s flag identity: the supplied Spirit of BC flag drawing (artwork/flag/spirit-of-bc-flag.svg) and the layout measured from seventeen printed references (src/flag/flagLayout.js).',
  status: 'A historical reconstruction for reference and study. The years are working dates, not confirmed adoption dates. Not the Province’s current identity.',
  colours: {
    blue072: '#10069F', red032: '#EF3340', yellow109: '#FFD100',
    navy: '#013366', crimson: '#AD0000', gold: '#FCBA19',
    black: '#000000', white: '#FFFFFF', paper: '#FFFFFF'
  },
  colourNames: { blue072: 'Pantone Blue 072 C', red032: 'Pantone Red 032 C', yellow109: 'Pantone Yellow 109 C', navy: 'Navy (supplied artwork)', crimson: 'Red (supplied artwork)', gold: 'Gold (supplied artwork)' },
  roles: { ink: 'black', paper: 'paper', muted: 'black', primary: 'blue072', light: '#FFF6CC', reverse: 'white', line: '#D7D7DE', rule: 'black', symbol: 'blue072', type: 'black', letters: 'black', blue: 'blue072', red: 'red032', yellow: 'yellow109' },
  print: { pantone: { blue072: 'Blue 072 C', red032: 'Red 032 C', yellow109: 'Yellow 109 C' }, note: 'The standards page (B.C. Flag Symbol, Colour Usage) names Pantone Blue 072C, Red 032C and Yellow 109C, and white as the fourth colour on a coloured ground. Screen values are Pantone’s sRGB approximations. The supplied artwork carries a later navy, red and gold, offered as the Modern colourway.' },
  colourways: {
    official: { label: 'Official: Pantone 072, 032, 109', roles: { blue: 'blue072', red: 'red032', yellow: 'yellow109', letters: 'black', type: 'black' } },
    modern: { label: 'Modern: as supplied', roles: { blue: 'navy', red: 'crimson', yellow: 'gold', letters: 'black', type: 'black' } },
    black: { label: 'One ink: black', all: 'black' },
    blue: { label: 'One ink: Blue 072', all: 'blue072' },
    reverse: { label: 'One ink: white', all: 'white', ground: 'blue072' }
  },
  defaultColourway: 'official',
  logoColours: ['black', 'blue072', 'white', 'currentColor'],
  rasterColours: ['black', 'blue072', 'white'],
  fonts: {
    regular: HEROS.regular, bold: HEROS.bold, italic: HEROS.italic,
    body: HEROS.regular, display: HEROS.bold, displayRegular: HEROS.regular, extra: HEROS.bold, label: HEROS.regular
  },
  typography: {
    headlines: { family: 'Helvetica Bold', weight: 700, trackingEm: 0 },
    body: { family: 'Helvetica Regular', weight: 400 },
    labels: { family: 'Helvetica Regular', weight: 400, trackingEm: 0.04 },
    note: '“BC” in Helvetica Bold; the ministry in Helvetica Regular (some documents set it bold), on 13/12 leading. TeX Gyre Heros stands in for Helvetica with the same widths.'
  },
  symbol,
  signatures: SIGNATURES,
  lockup: { canvasPadding: 0, clearspaceRecommendation: 'On a coloured ground set the whole lockup in one ink: the flag’s white is the page showing through, not a white shape.', minimumHorizontalWidthPx: 96, minimumHorizontalWidthMm: 20 },
  departments: { label: 'Ministry', field: 'ministry', folder: 'ministries', colourways: ['official'], items: ministries, note: 'Every ministry in PofBC’s ministry history that existed between 1983 and 2005, the flag identity’s working years.' },
  fields: {
    ministry: { label: 'Ministry', placeholder: 'Ministry of\nAbcdefghijk', multiline: true },
    extra: { label: 'Third line (a minister, a place, a bulletin number)', placeholder: '' }
  },
  copy: {
    svgDescription: 'Province of British Columbia flag identity (about 1983–2005), reconstructed for reference. Not the Province’s current identity. Helvetica is set in TeX Gyre Heros.',
    templateDescription: 'Province of British Columbia, flag identity, reconstructed. Not the Province’s current identity.',
    logoLabel: 'Province of British Columbia flag signature',
    motifLabel: 'The BC flag',
    tagline: 'BC, beside its flag.'
  },
  templates: [],
  web: {
    componentName: 'BcFlagSignature',
    symbolComponentName: 'BcFlag',
    cssPrefix: 'bcflag',
    appIcon: { background: 'paper', colour: 'primary', size: 860 },
    favicon: { light: '#10069F', dark: '#FFFFFF', size: 60, micro: false, title: '{name} favicon' },
    intro: { eyebrow: 'Flag identity / about 1983–2005', headline: 'Province of\nBritish Columbia', body: 'BC beside the waving provincial flag, with any ministry of the period set beside or below it, as measured from seventeen printed documents. A historical reference, not the Province’s current identity.', edition: 'Flag-identity reconstruction', footer: 'Province of British Columbia flag identity. A reconstruction for reference; not the current provincial identity.' },
    landing: { eyebrow: 'Historical reference', headline: 'Province of\nBritish Columbia\nflag identity', body: 'BC and the flag, for every ministry of the period.', cta: 'Open the signatures', contactEyebrow: 'Not current guidance', contactBody: 'For the Province’s current identity, see the Government of British Columbia.', footer: 'Flag identity (reconstruction).' }
  },
  files: [{ to: 'README.md', from: 'docs/README.md' }, ...HEROS_FILES]
}

writeEraBrand(brand)
