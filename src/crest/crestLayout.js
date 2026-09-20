// The crest identity: the coat of arms with the BRITISH COLUMBIA wordmark, and a ministry set
// against it.
//
// This is the identity that followed the flag one. Both pieces are artwork — the arms as drawn,
// and the wordmark as outlines rather than as text — so nothing here is typeset except the
// ministry, which the documents set in Helvetica or Arial.
//
// Everything is proportional to one measurement, the height of the arms.
//
// The two arrangements are measured from different sources and agree with each other, which is the
// reassuring part: the horizontal one comes from a vector page, and the vertical from a raster —
// and the raster's arms and wordmark come out at aspects of 0.82 and 2.48 against the vector's own
// 0.831 and 2.523. Two independent readings of the same two drawings.

import { ARMS, WORDMARK } from '../assets/crestMark.js'
import { getFaceMetrics } from '../logo/fontMetrics.js'
import { measureLine, positionWords, wrapText } from '../logo/logoText.js'
import { LOGO_FONT_FAMILY } from '../logo/renderLogoSvg.js'
import { outlineTextMarkup } from '../logo/textOutline.js'

const REGULAR = getFaceMetrics('regular')
const BOLD = getFaceMetrics('bold')

export const ARMS_ASPECT = ARMS.width / ARMS.height
export const WORDMARK_ASPECT = WORDMARK.width / WORDMARK.height

export const CREST_ARRANGEMENTS = ['horizontal', 'vertical', 'vertical-arms']

export const CREST_ARRANGEMENT_LABELS = {
  horizontal: 'Side by side',
  vertical: 'Stacked',
  'vertical-arms': 'Stacked, large arms'
}

export const CREST_ARRANGEMENT_HINTS = {
  horizontal: 'The arms, then the wordmark beside them.',
  vertical: 'The arms above the wordmark, both centred, at much the same height.',
  'vertical-arms': 'Stacked, with the arms drawn more than twice the wordmark’s height.'
}

export const CREST_PLACEMENTS = ['beside', 'below']

/**
 * How the ministry lines up under a stacked lockup.
 *
 * Both occur, and it is not a matter of taste in the documents so much as of which document. Two
 * of them centre each line on the mark's axis; a third sets the block flush with the wordmark's
 * left edge. Nothing distinguishes them but the studio that set them.
 */
export const CREST_ALIGNMENTS = ['centre', 'left']

export const CREST_ALIGNMENT_LABELS = { centre: 'Centred', left: 'Flush left' }

export const CREST_PLACEMENT_LABELS = { beside: 'Beside', below: 'Below' }

/**
 * How each arrangement is built, in multiples of the arms' height.
 *
 * `horizontal` is measured off a vector page — the one file of its kind that carries the arms as
 * paths rather than as an embedded raster. `vertical` is measured off a raster, which is the only
 * form it survives in here.
 */
export const CREST_LAYOUTS = {
  horizontal: {
    // The wordmark stands almost as tall as the arms and sits beside them, their tops and feet
    // within four hundredths of each other.
    wordmarkHeight: 0.945,
    gap: 0.21,
    centred: false,
    belowGap: 0.132
  },
  vertical: {
    // Stacked, on a common axis, the two drawn at much the same height. Three documents agree:
    // 0.878, 0.899, 0.891. Each was checked by aspect first — the arms come out at 0.818–0.833
    // against this project's 0.831, and the wordmark at 2.483–2.511 against its 2.523 — so these
    // are readings of the same two drawings and not of something rescaled.
    wordmarkHeight: 0.889,
    gap: 0.05,
    centred: true,
    belowGap: 0.44
  },
  'vertical-arms': {
    // The same stack with the arms drawn about twice as large. Three documents: 0.493, 0.493 and
    // 0.433, the odd one out being the smallest image of the three and so the least certain.
    // 0.433 was the only stacked proportion the system had, which left the commoner form out.
    wordmarkHeight: 0.49,
    gap: 0.085,
    centred: true,
    belowGap: 0.44
  }
}

/**
 * Ministry cap height, as a share of the wordmark's height.
 *
 * Against the wordmark rather than the arms, for the reason `belowGap` gives: the wordmark is the
 * one drawing whose size holds across the arrangements, so a share of it means the same thing in
 * all three.
 *
 * It is a choice rather than a constant, because the documents disagree. Converting each reading
 * from a band height to a cap height — in Helvetica the ascenders reach 0.718 em against the cap
 * line's 0.717, so a line with ascenders and no descenders bands at exactly its cap height, and
 * one with descenders bands at cap plus 0.208 — gives three settings:
 *
 *   0.212   `selection-1 (6)`, `12.32.35`, and the side-by-side `12.33.18`
 *   0.263   `12.33.36`
 *   0.294   `selection-1 (2)`
 *
 * The fourth, below all of them, is where a trailing line lands when a document sets one smaller
 * than the ministry above it — see `MINISTRY_STEPS`.
 */
export const MINISTRY_SIZES = { xsmall: 0.138, small: 0.212, medium: 0.263, large: 0.294 }

export const MINISTRY_SIZE_ORDER = ['xsmall', 'small', 'medium', 'large']

export const MINISTRY_SIZE_LABELS = { xsmall: 'XS', small: 'S', medium: 'M', large: 'L' }

export const MINISTRY_SIZE_HINTS = {
  xsmall: 'The size a trailing line drops to in ‘12.32.35’.',
  small: 'Three documents: ‘(6)’, ‘12.32.35’ and ‘12.33.18’.',
  medium: 'As ‘12.33.36’ sets it.',
  large: 'As ‘selection-1 (2)’ sets it.'
}

export const DEFAULT_MINISTRY_SIZE = 'small'

/**
 * Whether a trailing line matches the ministry or drops a step below it.
 *
 * Two documents set it smaller, and both drop exactly one step on the scale above: `12.33.36`
 * goes 0.263 to 0.212, and `12.32.35` goes 0.212 to 0.138. The others set the two alike.
 */
export const MINISTRY_STEPS = ['match', 'smaller']

export const MINISTRY_STEP_LABELS = { match: 'Same size', smaller: 'A step smaller' }

/** Ministry leading, as a multiple of the type size. 1.222 em on the vector page. */
const LEADING = 1.222

/**
 * Gap from the lockup to the ministry when it stands beside it, in arms heights.
 *
 * Below the lockup the gap is measured against the wordmark instead — `belowGap` above — because
 * the wordmark is the one drawing whose size holds across the arrangements. Against the arms the
 * four documents spread 0.125 to 0.397; against the wordmark the three stacked ones land on 0.453,
 * 0.427 and 0.448, with the side-by-side ones at 0.132. The unit was the whole difference.
 */
const BESIDE_GAP = 1.407

/**
 * What the ministry wraps to, in cap heights of its own type.
 *
 * In the type's unit rather than the mark's, so that changing the ministry's size cannot make the
 * backstop cut a line it used to fit. An earlier value in arms heights did exactly that the moment
 * the size became a choice.
 *
 * The widest ministry line any of these documents prints is "Ministry of Employment and
 * Investment" — 563 units against a cap of 22.4, so 25.1 caps. This project sets the same line at
 * 26.2, about four hundredths wider in the face, so the backstop is put just above what we
 * produce: one that cuts a line the Province printed whole would be worse than one a shade wide.
 *
 * It is a backstop, not a rule. The documents break their ministries by hand and disagree with
 * each other about where, so a typed break wins over this — the same rule the current era follows.
 */
export const MINISTRY_MEASURE = 26.5

const sizeForCap = (cap, face) => cap * 1000 / face.capHeight

/**
 * Lays a crest lockup out, in units where the arms stand `size` tall.
 *
 * The origin is the lockup's top-left, and y runs downward as SVG measures it.
 *
 * @param {object} options
 * @param {string} [options.arrangement]  'horizontal' | 'vertical'
 * @param {string} [options.placement]    'beside' | 'below'
 * @param {string} [options.ministry]     The ministry. Newlines break lines.
 * @param {string} [options.extra]        A further line — a branch, a division, a region.
 * @param {boolean} [options.bold]        Set the ministry bold, as many of the documents do.
 * @param {string} [options.align]        'centre' | 'left' — how a stacked lockup's ministry sits.
 * @param {string} [options.ministrySize] A key of `MINISTRY_SIZES`. The documents disagree.
 * @param {string} [options.extraStep]    'match' | 'smaller' — the trailing line's size.
 * @param {number} [options.size]         The arms' height.
 * @param {number} [options.measure]      Width to wrap to.
 */
export const layoutCrestLockup = ({
  arrangement = 'horizontal',
  placement = 'beside',
  ministry = '',
  extra = '',
  bold = false,
  align = 'centre',
  ministrySize = DEFAULT_MINISTRY_SIZE,
  extraStep = 'match',
  size = 100,
  measure
} = {}) => {
  const plan = CREST_LAYOUTS[arrangement] ?? CREST_LAYOUTS.horizontal

  const armsHeight = size
  const armsWidth = armsHeight * ARMS_ASPECT
  const wordmarkHeight = plan.wordmarkHeight * size
  const wordmarkWidth = wordmarkHeight * WORDMARK_ASPECT

  let arms
  let wordmark

  if (plan.centred) {
    // Stacked on a common axis, the wider of the two deciding the block's width.
    const width = Math.max(armsWidth, wordmarkWidth)
    arms = { x: (width - armsWidth) / 2, y: 0, width: armsWidth, height: armsHeight }
    wordmark = {
      x: (width - wordmarkWidth) / 2,
      y: armsHeight + plan.gap * size,
      width: wordmarkWidth,
      height: wordmarkHeight
    }
  } else {
    // Side by side, their feet aligned.
    arms = { x: 0, y: 0, width: armsWidth, height: armsHeight }
    wordmark = {
      x: armsWidth + plan.gap * size,
      y: armsHeight - wordmarkHeight,
      width: wordmarkWidth,
      height: wordmarkHeight
    }
  }

  const markRight = Math.max(arms.x + arms.width, wordmark.x + wordmark.width)
  const markBottom = Math.max(arms.y + arms.height, wordmark.y + wordmark.height)

  // ── The ministry ───────────────────────────────────────────────────────────────────────────
  const index = Math.max(0, MINISTRY_SIZE_ORDER.indexOf(ministrySize))
  const step = extraStep === 'smaller' ? Math.max(0, index - 1) : index
  const capOf = (i) => MINISTRY_SIZES[MINISTRY_SIZE_ORDER[i]] * wordmarkHeight
  const styleOf = (cap) => bold
    ? { fontSize: sizeForCap(cap, BOLD), weight: 'bold' }
    : { fontSize: sizeForCap(cap, REGULAR) }

  // One column for both blocks, off the ministry's own cap height — a trailing line set smaller
  // still wraps to the same width rather than to a narrower one of its own.
  const wrapTo = measure ?? MINISTRY_MEASURE * capOf(index)

  // A block the user broke by hand is set as typed; one they did not is wrapped to the measure.
  // The documents were set line by line and disagree about where to break, so there is no rule to
  // infer — only a backstop for text nobody has broken yet.
  const setBlock = (text, style) => {
    const typed = String(text).split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
    return typed.length > 1 ? typed : wrapText(text, wrapTo, style)
  }

  // The ministry and the line under it are sized separately, because two of the documents set the
  // second smaller. Each block therefore carries its own style and its own leading.
  const blocks = []
  if (String(ministry).trim()) blocks.push({ text: ministry, cap: capOf(index) })
  if (String(extra).trim()) blocks.push({ text: extra, cap: capOf(step) })

  const entries = []
  let pen = 0
  blocks.forEach((block, position) => {
    const style = styleOf(block.cap)
    const leading = style.fontSize * LEADING
    if (position) pen += leading * 0.5
    for (const text of setBlock(block.text, style)) {
      entries.push({ text, style, cap: block.cap, offset: pen, ink: measureLine(text, style) })
      pen += leading
    }
  })

  const gap = placement === 'below' ? plan.belowGap * wordmarkHeight : BESIDE_GAP * size
  const firstCap = entries.length ? entries[0].cap : 0
  const blockHeight = entries.length ? entries.at(-1).offset + entries.at(-1).cap : 0

  // Under a stacked lockup the ministry either centres on the mark's axis or sits flush with the
  // wordmark's left edge; beside it, it simply follows the mark.
  const centreLines = plan.centred && placement === 'below' && align === 'centre'
  const flushLeft = plan.centred && placement === 'below' && align === 'left'

  let originX
  let firstBaseline
  if (placement === 'beside') {
    originX = markRight + gap
    // Centred against the mark, which is what the documents do when it stands beside them.
    firstBaseline = (markBottom - blockHeight) / 2 + firstCap
  } else {
    originX = flushLeft ? wordmark.x : 0
    firstBaseline = markBottom + gap + firstCap
  }

  const lines = entries.map((entry) => ({
    text: entry.text,
    style: entry.style,
    x: centreLines
      // Each line centred in its own right, on the mark's own axis.
      ? (markRight - (entry.ink.inkRight - entry.ink.inkLeft)) / 2 - entry.ink.inkLeft
      : originX - entry.ink.inkLeft,
    y: firstBaseline + entry.offset,
    words: positionWords(entry.text, entry.style),
    ink: entry.ink
  }))

  const right = Math.max(markRight, ...lines.map((line) => line.x + line.ink.inkRight))
  const bottom = Math.max(markBottom, ...lines.map((line) => line.y - line.ink.inkBottom))
  const top = Math.min(0, ...lines.map((line) => line.y - line.ink.inkTop))
  const left = Math.min(0, ...lines.map((line) => line.x + line.ink.inkLeft))

  return {
    size,
    arrangement,
    placement,
    arms,
    wordmark,
    lines,
    box: { x: left, y: top, width: right - left, height: bottom - top }
  }
}

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value, places = 3) => {
  const factor = 10 ** places
  return Math.round(value * factor) / factor
}

/** A drawing, scaled and positioned. Both are artwork, so both are just paths. */
const artworkMarkup = (drawing, box, role, fill) => {
  const scale = box.height / drawing.height
  const shapes = drawing.shapes
    .map((shape) => `<path data-role="${role}" d="${shape.d}" fill="${escapeXml(fill)}"/>`)
    .join('')

  return `<g transform="translate(${round(box.x)} ${round(box.y)}) scale(${round(scale, 6)})">${shapes}</g>`
}

const textMarkup = (lines, fill, fontFamily) => lines.map((line) => {
  const content = line.words.length === 1
    ? escapeXml(line.words[0].text)
    : line.words.map((word) => `<tspan x="${round(line.x + word.x)}">${escapeXml(word.text)}</tspan>`).join('')
  const weight = line.style.weight === 'bold' ? ' font-weight="700"' : ''

  return `<text data-role="name" x="${round(line.x)}" y="${round(line.y)}" fill="${escapeXml(fill)}"` +
    ` font-family="${escapeXml(fontFamily)}" font-size="${round(line.style.fontSize)}"${weight}>${content}</text>`
}).join('')

/**
 * The lockup as an SVG fragment.
 *
 * Pass `glyphs` to draw the ministry as paths rather than as live text. The arms and the wordmark
 * are paths either way — neither was ever text.
 */
export const crestLockupMarkup = ({
  layout, markColor, textColor, fontFamily = LOGO_FONT_FAMILY, glyphs
}) => (
  artworkMarkup(ARMS, layout.arms, 'arms', markColor) +
  artworkMarkup(WORDMARK, layout.wordmark, 'wordmark', markColor) +
  (glyphs
    ? outlineTextMarkup(layout.lines, glyphs, textColor)
    : textMarkup(layout.lines, textColor, fontFamily))
)
