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

export const CREST_ARRANGEMENTS = ['horizontal', 'vertical']

export const CREST_ARRANGEMENT_LABELS = { horizontal: 'Side by side', vertical: 'Stacked' }

export const CREST_ARRANGEMENT_HINTS = {
  horizontal: 'The arms, then the wordmark beside them.',
  vertical: 'The arms above the wordmark, both centred.'
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
    centred: false
  },
  vertical: {
    // Stacked, the arms are drawn much larger against the wordmark — 2.3 times its height rather
    // than a little over one — and everything centres on a common axis.
    wordmarkHeight: 0.433,
    gap: 0.09,
    centred: true
  }
}

/** Ministry cap height, as a share of the arms'. Both sources agree: 0.163 and 0.164. */
export const MINISTRY_CAP = 0.1635

/** Ministry leading, as a multiple of the type size. 1.222 em on the vector page. */
const LEADING = 1.222

/** Gap from the lockup to the ministry, per placement. */
const PLACEMENT_GAP = { beside: 1.407, below: 0.179 }

/** What the ministry wraps to, in multiples of the arms' height. */
export const MINISTRY_MEASURE = 3.6

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
  const cap = MINISTRY_CAP * size
  const style = bold
    ? { fontSize: sizeForCap(cap, BOLD), weight: 'bold' }
    : { fontSize: sizeForCap(cap, REGULAR) }
  const wrapTo = measure ?? MINISTRY_MEASURE * size

  const blocks = []
  if (String(ministry).trim()) blocks.push(wrapText(ministry, wrapTo, style))
  if (String(extra).trim()) blocks.push(wrapText(extra, wrapTo, style))

  const leading = style.fontSize * LEADING
  const entries = []
  let pen = 0
  blocks.forEach((block, index) => {
    if (index) pen += leading * 0.5
    for (const text of block) {
      entries.push({ text, offset: pen, ink: measureLine(text, style) })
      pen += leading
    }
  })

  const gap = (PLACEMENT_GAP[placement] ?? PLACEMENT_GAP.beside) * size
  const blockHeight = entries.length ? entries.at(-1).offset + cap : 0

  // Under a stacked lockup the ministry either centres on the mark's axis or sits flush with the
  // wordmark's left edge; beside it, it simply follows the mark.
  const centreLines = plan.centred && placement === 'below' && align === 'centre'
  const flushLeft = plan.centred && placement === 'below' && align === 'left'

  let originX
  let firstBaseline
  if (placement === 'beside') {
    originX = markRight + gap
    // Centred against the mark, which is what the documents do when it stands beside them.
    firstBaseline = (markBottom - blockHeight) / 2 + cap
  } else {
    originX = flushLeft ? wordmark.x : 0
    firstBaseline = markBottom + gap + cap
  }

  const lines = entries.map((entry) => ({
    text: entry.text,
    style,
    x: centreLines
      // Each line centred in its own right, on the mark's own axis.
      ? (markRight - (entry.ink.inkRight - entry.ink.inkLeft)) / 2 - entry.ink.inkLeft
      : originX - entry.ink.inkLeft,
    y: firstBaseline + entry.offset,
    words: positionWords(entry.text, style),
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
