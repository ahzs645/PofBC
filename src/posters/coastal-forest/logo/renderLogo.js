// The logo studio's model, on top of the generator.
//
// Crest era: renderLockupSvg() draws any of the four lockups for any wording, with the type
// converted to outlines from the generator's own glyph table so nothing depends on Helvetica. The
// table is loaded once, before the poster opens (see ../index.jsx); without it the type stays live.
// Current era: renderCurrentSvg() sets a ministry name beside the Province's published mark.

import { renderLockupSvg } from '../../../logo/renderLogoSvg.js'
import { LAYOUT_ORDER, MARK_ALIGNMENT_ORDER, alignsVertically, clearSpacePadding } from '../../../logo/layouts.js'
import { BRAND_COLORS, contrastRatio } from '../../../logo/logoColors.js'
import { BCID, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, renderCurrentSvg } from '../../../current/currentMarks.js'
import { MINISTRIES as CURRENT_MINISTRIES, findMinistry } from '../../../current/ministries.js'
import { MINISTRIES as CREST_MINISTRIES } from '../../../ministries/ministries.js'

let outlines = null
/** Hands over the generator's glyph outlines, or null to keep the type live. */
export const setLogoOutlines = (table) => { outlines = table ?? null }

export const CREAM = '#eee3c0'
export const POSTER_BLACK = '#121411'

export { LAYOUT_ORDER, MARK_ALIGNMENT_ORDER, alignsVertically, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, BCID, CURRENT_MINISTRIES, CREST_MINISTRIES, contrastRatio }

export const LAYOUT_INFO = {
  columns: { label: 'Side by side', note: 'The one on the poster. Reconstructed from a photograph of signage; no vector original survives.' },
  horizontal: { label: 'Horizontal', note: 'Mark to the left, wordmark and ministry stacked beside it. From the supplied Illustrator export.' },
  stacked: { label: 'Stacked', note: 'Mark above a left-aligned text column. The tallest of the four.' },
  centred: { label: 'Centred', note: 'Mark centred above centred text, drawn without the province wordmark.' }
}

export const CREST_SWATCHES = [
  { name: 'Poster cream', value: CREAM },
  { name: 'White', value: BRAND_COLORS.white },
  { name: 'Black', value: BRAND_COLORS.black },
  { name: 'Forest green', value: BRAND_COLORS.green },
  { name: 'Blue', value: BRAND_COLORS.blue },
  { name: 'Red', value: BRAND_COLORS.red },
  { name: 'Gold', value: BRAND_COLORS.gold },
  { name: 'Silver', value: BRAND_COLORS.silver }
]

export const PREVIEW_BACKGROUNDS = [
  { name: 'Poster black', value: POSTER_BLACK },
  { name: 'White', value: '#ffffff' },
  { name: 'Forest green', value: BRAND_COLORS.green },
  { name: 'BC Blue', value: BCID.blue },
  { name: 'BC Gold', value: BCID.gold }
]

/** The Ministry of Environment's current wording, with the Province's own line breaks. */
export const CURRENT_ENV = findMinistry('ENV')

export const DEFAULT_LOGO = {
  era: 'crest',
  layout: 'columns',
  ministry: 'Ministry of\nEnvironment',
  program: '',
  wordmark: true,
  markAlign: 'top',
  markColor: CREAM,
  textColor: CREAM,
  language: 'en',
  variant: 'reverse',
  currentCode: 'ENV',
  currentText: CURRENT_ENV.en
}

/** True when the configuration is the logo the poster already carries. */
export const isOriginalLogo = (c) =>
  c.era === 'crest' && c.layout === 'columns' && c.ministry === DEFAULT_LOGO.ministry && !c.program &&
  c.wordmark && c.markAlign === 'top' && c.markColor === CREAM && c.textColor === CREAM

/**
 * The logo as a standalone SVG string.
 * `background` and `clearSpace` (a fraction of the mark's width) are for files; the poster gets
 * the transparent, unpadded version.
 */
export const renderLogo = (c, { background = 'none', clearSpace = 0 } = {}) => {
  if (c.era === 'current') {
    return renderCurrentSvg({
      text: c.currentText,
      language: c.language,
      variant: c.variant,
      background,
      clearSpaceFactor: clearSpace,
      title: `British Columbia — ${c.currentText.replace(/\n/g, ' ')}`
    })
  }
  return renderLockupSvg({
    layout: c.layout,
    ministry: c.ministry,
    program: c.program,
    wordmark: c.wordmark,
    markColor: c.markColor,
    textColor: c.textColor,
    markAlign: c.markAlign,
    background,
    padding: clearSpace ? clearSpacePadding('standard') * (clearSpace / 0.25) : 0,
    ...(outlines ? { glyphs: outlines } : {})
  })
}

/** A short tag for file names, e.g. "crest-columns" or "current-en-reverse". */
export const logoTag = (c) => (c.era === 'current' ? `current-${c.language}-${c.variant}` : `crest-${c.layout}`)

/** The viewBox of an SVG string, as numbers. */
export const viewBoxOf = (svg) => {
  const m = /viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"/.exec(svg)
  return m ? { x: +m[1], y: +m[2], w: +m[3], h: +m[4] } : { x: 0, y: 0, w: 1, h: 1 }
}
