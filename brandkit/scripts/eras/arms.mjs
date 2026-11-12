// Writes <out>/bc-province-arms/brand.json: the identity that followed the flag one, the full
// achievement of arms with the outlined BRITISH COLUMBIA wordmark and a ministry set against it.
//
// As with the flag, nothing is measured afresh: the arms and wordmark are PofBC's drawings
// (src/assets/crestMark.js, extracted by scripts/build_crest.py), and every distance is PofBC's
// layout (src/crest/crestLayout.js, read off twelve printed documents), run with the arms
// 1000 units tall and written down as brandkit elements. The ministry is set in Helvetica Regular
// (TeX Gyre Heros) at PofBC's default size, 0.212 of the wordmark's height in cap height, on 1.222
// leading, wrapping at 26.5 of its own cap heights.
//
// PofBC centres wording set *beside* the mark on the mark's height, so the block moves as it gains
// lines; brandkit hangs a stack from its first line, so that signature is placed for a two-line
// ministry. Wording set *below* hangs from the mark as PofBC sets it, at any length.
//
//   npm run brandkit:build -- bc-province-arms

import { pofbc } from '../lib/paths.mjs'
import { HEROS, HEROS_FILES, round, writeEraBrand } from '../lib/era.mjs'
import { ministriesBetween } from '../lib/ministries.mjs'

const ID = 'bc-province-arms'
const { ARMS, WORDMARK } = await pofbc('src/assets/crestMark.js')
const { layoutCrestLockup, MINISTRY_MEASURE, MINISTRY_SIZES, DEFAULT_MINISTRY_SIZE } = await pofbc('src/crest/crestLayout.js')

const paths = (drawing) => drawing.shapes.map((shape) => `<path d="${shape.d}"${shape.rule ? ` fill-rule="${shape.rule}"` : ''}/>`).join('')
const symbol = {
  name: 'bc-arms',
  title: 'Arms of British Columbia',
  masterTitle: 'The full achievement of arms',
  masterDescription: 'The coat of arms as drawn in the identity’s artwork, lifted from a page extraction onto its own ink box.',
  viewBox: [0, 0, ARMS.width, ARMS.height],
  markup: paths(ARMS)
}

const SIZE = 1000
const PROBE = 'Ministry of Small Business\nand Revenue'
const LEADING = 1.222
const signature = ({ id, label, use, arrangement, placement, align = 'centre', departmental = true }) => {
  const layout = layoutCrestLockup({ arrangement, placement, align, ministry: departmental ? PROBE : '', size: SIZE })
  const { arms, wordmark } = layout
  const wordmarkScale = wordmark.height / WORDMARK.height
  const elements = [
    { type: 'symbol', x: round(arms.x), y: round(arms.y), height: round(arms.height) },
    { type: 'art', x: round(wordmark.x), y: round(wordmark.y), scale: round(wordmarkScale, 6), bounds: [0, 0, WORDMARK.width, WORDMARK.height], markup: `<g fill="{symbol}">${paths(WORDMARK)}</g>` }
  ]
  if (departmental) {
    const [first] = layout.lines
    const size = round(first.style.fontSize)
    const cap = MINISTRY_SIZES[DEFAULT_MINISTRY_SIZE] * wordmark.height
    const centred = arrangement !== 'horizontal' && placement === 'below' && align === 'centre'
    const markRight = Math.max(arms.x + arms.width, wordmark.x + wordmark.width)
    elements.push({
      type: 'stack', id: 'ministry', y: round(first.y),
      x: round(centred ? markRight / 2 : first.x + first.ink.inkLeft),
      ...(centred ? { anchor: 'middle' } : {}),
      items: [
        { field: 'ministry', size, font: 'regular', leading: round(size * LEADING), wrap: round(MINISTRY_MEASURE * cap) },
        { field: 'extra', size, font: 'regular', leading: round(size * LEADING), wrap: round(MINISTRY_MEASURE * cap), gapBefore: round(size * LEADING * 0.5), when: 'extra' }
      ]
    })
  }
  return { id, label, use, ...(departmental ? { departmental: true } : {}), metrics: { font: 'regular', capHeight: round(wordmark.height), baseline: round(wordmark.y + wordmark.height), logotypeX: round(wordmark.x) }, elements }
}

const SIGNATURES = [
  signature({ id: 'horizontal', label: 'Arms and wordmark, side by side', use: 'The arms, then BRITISH COLUMBIA beside them, their tops and feet aligned. Measured off a vector page.', arrangement: 'horizontal', placement: 'beside', departmental: false }),
  signature({ id: 'vertical', label: 'Arms over wordmark', use: 'Stacked on a common axis, the two drawn at much the same height. Three documents agree.', arrangement: 'vertical', placement: 'below', departmental: false }),
  signature({ id: 'horizontal-beside', label: 'Side by side, ministry beside', use: 'The ministry to the right of the wordmark, centred against the mark (placed here for a two-line name).', arrangement: 'horizontal', placement: 'beside' }),
  signature({ id: 'horizontal-below', label: 'Side by side, ministry below', use: 'The ministry under the side-by-side mark, flush left.', arrangement: 'horizontal', placement: 'below' }),
  signature({ id: 'vertical-below', label: 'Stacked, ministry centred below', use: 'Each line centred on the mark’s axis, as two of the documents set it.', arrangement: 'vertical', placement: 'below' }),
  signature({ id: 'vertical-left', label: 'Stacked, ministry flush left', use: 'The ministry flush with the wordmark’s left edge, as a third document sets it.', arrangement: 'vertical', placement: 'below', align: 'left' }),
  signature({ id: 'vertical-arms', label: 'Stacked, large arms, ministry centred below', use: 'The arms drawn about twice the wordmark’s height. Three documents.', arrangement: 'vertical-arms', placement: 'below' })
]

const ministries = await ministriesBetween(1983, 2011)

export const brand = {
  schema: 'brandkit/1',
  id: ID,
  name: 'Province of British Columbia (arms and wordmark)',
  version: 'arms-wordmark',
  displayVersion: 'Arms and wordmark',
  source: 'PofBC’s coat-of-arms identity: the arms and BRITISH COLUMBIA wordmark extracted by scripts/build_crest.py (src/assets/crestMark.js) and the layout measured from twelve printed documents (src/crest/crestLayout.js).',
  status: 'A historical reconstruction for reference and study. It followed the flag identity; its years are not yet confirmed. Not the Province’s current identity.',
  colours: { black: '#000000', white: '#FFFFFF', paper: '#FFFFFF', blue: '#234075', green: '#006837' },
  colourNames: { blue: 'BC Blue', green: 'Forest green' },
  roles: { ink: 'black', paper: 'paper', muted: 'black', primary: 'black', light: '#F2F2F2', reverse: 'white', line: '#D9D9D9', rule: 'black', symbol: 'black', type: 'black' },
  print: { note: 'Every document measured sets the arms and wordmark dark on light, in one ink with the ministry. No colour specification has been found.' },
  colourways: {
    black: { label: 'Black', all: 'black' },
    blue: { label: 'BC Blue', all: 'blue' },
    reverse: { label: 'Reverse: white', all: 'white', ground: 'black' }
  },
  defaultColourway: 'black',
  logoColours: ['black', 'blue', 'white', 'currentColor'],
  rasterColours: ['black', 'blue', 'white'],
  fonts: {
    regular: HEROS.regular, bold: HEROS.bold, italic: HEROS.italic,
    body: HEROS.regular, display: HEROS.bold, displayRegular: HEROS.regular, extra: HEROS.bold, label: HEROS.regular
  },
  typography: {
    headlines: { family: 'Helvetica Bold', weight: 700, trackingEm: 0 },
    body: { family: 'Helvetica Regular', weight: 400 },
    labels: { family: 'Helvetica Regular', weight: 400, trackingEm: 0.04 },
    note: 'The arms and the wordmark are artwork, so only the ministry is typeset, in Helvetica (some documents Arial), regular or bold. TeX Gyre Heros stands in for Helvetica with the same widths.'
  },
  symbol,
  signatures: SIGNATURES,
  lockup: { canvasPadding: 0, clearspaceRecommendation: 'Arms and wordmark are always drawn together, at the proportions of one arrangement; the ministry is the only thing set.', minimumHorizontalWidthPx: 120, minimumHorizontalWidthMm: 25 },
  departments: { label: 'Ministry', field: 'ministry', folder: 'ministries', colourways: ['black'], items: ministries, note: 'Every ministry in PofBC’s ministry history between 1983 and 2011: the identity’s own years are not confirmed, so the list spans the flag identity to the BC mark.' },
  fields: {
    ministry: { label: 'Ministry', placeholder: 'Ministry of\nAbcdefghijk', multiline: true },
    extra: { label: 'Further line (a branch, a division, a region)', placeholder: '' }
  },
  copy: {
    svgDescription: 'Province of British Columbia coat-of-arms identity, reconstructed for reference. Not the Province’s current identity. Helvetica is set in TeX Gyre Heros.',
    templateDescription: 'Province of British Columbia, coat of arms and wordmark, reconstructed. Not the Province’s current identity.',
    logoLabel: 'Province of British Columbia arms signature',
    motifLabel: 'Arms of British Columbia',
    tagline: 'Splendor sine occasu.'
  },
  templates: [],
  web: {
    componentName: 'BcArmsSignature',
    symbolComponentName: 'BcArms',
    cssPrefix: 'bcarmswm',
    appIcon: { background: 'paper', colour: 'primary', size: 860 },
    favicon: { light: '#000000', dark: '#FFFFFF', size: 60, micro: false, title: '{name} favicon' },
    intro: { eyebrow: 'Arms and wordmark', headline: 'Province of\nBritish Columbia', body: 'The full coat of arms with the BRITISH COLUMBIA wordmark, and any ministry set against it, as measured from twelve printed documents. A historical reference, not the Province’s current identity.', edition: 'Arms-and-wordmark reconstruction', footer: 'Province of British Columbia, arms and wordmark. A reconstruction for reference; not the current provincial identity.' },
    landing: { eyebrow: 'Historical reference', headline: 'Province of\nBritish Columbia\narms and wordmark', body: 'The arms and BRITISH COLUMBIA, for every ministry.', cta: 'Open the signatures', contactEyebrow: 'Not current guidance', contactBody: 'For the Province’s current identity, see the Government of British Columbia.', footer: 'Arms and wordmark (reconstruction).' }
  },
  files: [{ to: 'README.md', from: 'docs/README.md' }, ...HEROS_FILES]
}

writeEraBrand(brand)
