// The three lockups, as geometry.
//
// Every number here was measured off the supplied artwork in artwork/ and is expressed in that
// artwork's own units — the space the mark is drawn in, where it is 497.02 × 497.19. Keeping the
// native scale means each constant can be checked against the source file it came from, and
// `npm run compare` does exactly that.
//
// The three lockups are not simply the same drawing at three aspect ratios: they were set
// individually, and they disagree about type size, leading and tracking. Those disagreements are
// preserved rather than averaged away, because matching the supplied artwork is the point.

import { PROVINCIAL_MARK } from '../assets/markup.js'
import { measureWidth } from './logoText.js'

export const MARK_BOX = PROVINCIAL_MARK.viewBox

/** The fixed wordmark. The ministry line beneath it is the part that varies. */
export const PROVINCE_WORDMARK = 'Province of British Columbia'

// In the two left-aligned lockups the text column is twice the width of the mark. That measure is
// what breaks "Province of British Columbia" after "of" and "Ministry of Forests" after "of" in
// the source files: at 122.2 units, "British Columbia" needs 8.03 em and "Ministry of Forests"
// needs 8.17, and twice the mark width is 8.13 — between the two.
const COLUMN_MEASURE = 2 * MARK_BOX.width

/**
 * @typedef {object} Layout
 * @property {string} id
 * @property {string} label          For the UI.
 * @property {string} source         The artwork file these numbers were measured from.
 * @property {number} fontSize       In artwork units.
 * @property {number} leading        Baseline to baseline, in artwork units.
 * @property {number} letterSpacing  In em.
 * @property {number} wordSpacing    Extra space at each word gap, in em.
 * @property {'left'|'centre'} align
 * @property {'below'|'beside'} markPlacement
 * @property {boolean} wordmarkByDefault  Whether the source artwork for this lockup carries the
 *                                        province wordmark. The centred one does not.
 * @property {number} gap            Mark to text, in artwork units. Vertical for 'below'
 *                                   (mark's bottom edge to the cap height of the first line),
 *                                   horizontal for 'beside' (mark's right edge to the text's ink).
 * @property {(options: {hasWordmark: boolean}) => number} measure  Wrap width, in artwork units.
 */

/** @type {Record<string, Layout>} */
export const LAYOUTS = {
  stacked: {
    id: 'stacked',
    label: 'Stacked',
    description: 'Mark above a left-aligned text column. The tallest of the three.',
    source: 'artwork/lockup-stacked.svg',
    fontSize: 122.2,
    leading: 146.64,        // 1.2 em
    letterSpacing: 0,
    wordSpacing: 0.027,     // Illustrator tracking of 27/1000, written out as ".03em"
    align: 'left',
    markPlacement: 'below',
    gap: 96.22,
    wordmarkByDefault: true,
    measure: () => COLUMN_MEASURE
  },

  centred: {
    id: 'centred',
    label: 'Centred',
    description: 'Mark centred above centred text, without the province wordmark.',
    source: 'artwork/lockup-centred.svg',
    fontSize: 121,
    leading: 125.53,        // 1.0374 em — tighter than the other two, as drawn
    letterSpacing: -0.02,   // this lockup alone is tracked in slightly
    wordSpacing: 0,
    align: 'centre',
    markPlacement: 'below',
    gap: 75.23,
    // The one lockup drawn without the province wordmark: artwork/lockup-centred.svg sets the
    // ministry and its second line alone under the mark.
    wordmarkByDefault: false,
    measure: () => COLUMN_MEASURE
  },

  horizontal: {
    id: 'horizontal',
    label: 'Horizontal',
    description: 'Mark to the left of the text. The widest of the three, for narrow headers and letterheads.',
    source: 'artwork/lockup-horizontal.svg',
    fontSize: 121.64,
    leading: 145.968,       // 1.2 em
    letterSpacing: 0,
    wordSpacing: 0.027,
    align: 'left',
    markPlacement: 'beside',
    gap: 86.07,
    wordmarkByDefault: true,
    // The wordmark sets the column width here, so a long ministry name wraps beneath it rather
    // than running the lockup off the page. Without the wordmark there is nothing to measure
    // against, so the width it would have occupied is used instead and the geometry stays put.
    measure: ({ hasWordmark }) => (hasWordmark
      ? measureWidth(PROVINCE_WORDMARK, horizontalWordmarkStyle)
      : HORIZONTAL_FALLBACK_MEASURE)
  }
}

const horizontalWordmarkStyle = { fontSize: 121.64, weight: 'bold', wordSpacing: 0.027 }
const HORIZONTAL_FALLBACK_MEASURE = measureWidth(PROVINCE_WORDMARK, horizontalWordmarkStyle)

export const LAYOUT_ORDER = ['stacked', 'centred', 'horizontal']

export const getLayout = (id) => LAYOUTS[id] || LAYOUTS.stacked

// ── Clear space ──────────────────────────────────────────────────────────────────────────────────

/**
 * Margin presets, as a fraction of the mark's width.
 *
 * Measuring clear space against the mark rather than in absolute units is what makes it hold at
 * any size: the same preset gives a letterhead and a billboard the same proportions. Where the
 * lockup has a background colour, that colour extends to fill the margin, so this also decides how
 * much of a coloured panel the export is.
 *
 * `none` is a genuine option — a logo being placed into someone else's layout wants to be trimmed
 * to its own ink — but it is not the default, because type set hard against the edge of a coloured
 * panel reads as a mistake.
 */
export const CLEAR_SPACE = {
  none: { label: 'None', factor: 0 },
  snug: { label: 'Snug', factor: 0.125 },
  standard: { label: 'Standard', factor: 0.25 },
  generous: { label: 'Generous', factor: 0.5 }
}

export const CLEAR_SPACE_ORDER = ['none', 'snug', 'standard', 'generous']

export const DEFAULT_CLEAR_SPACE = 'snug'

/** A clear-space key as padding in artwork units, for `resolveLockup({ padding })`. */
export const clearSpacePadding = (key) => (CLEAR_SPACE[key]?.factor ?? 0) * MARK_BOX.width
