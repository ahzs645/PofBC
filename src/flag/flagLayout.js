// The flag identity: the BC Flag Symbol, with a ministry name set against it.
//
// The identity's own standards page — "B.C. Flag Symbol · Colour Usage · Vertical and Horizontal"
// — gives the symbol two configurations and no more: BC beside the flag, or the flag above BC.
// The documents that used it added a third, the flag standing alone, and set the name either under
// the symbol or beside it. All five arrangements are here, because all five were printed.
//
// Everything is proportional to one measurement — the cap height of the BC letters — so a lockup
// scales as a single drawing. The proportions are measured off the documents, and the documents
// disagree with each other: see ARRANGEMENTS for the spread.
//
// The letters are Arial Bold, named in the embedded font of a vector extraction of one document.
// Arial and Helvetica are metrically the same here — "BC" measures 1.844 cap heights of ink in one
// and 1.846 in the other — so the Helvetica this project already embeds draws them correctly.

import { FLAG } from '../assets/flagMark.js'
import { paletteFill } from './flagPalettes.js'
import { getFaceMetrics } from '../logo/fontMetrics.js'
import { LOGO_FONT_FAMILY } from '../logo/renderLogoSvg.js'
import { measureLine, positionWords, wrapText } from '../logo/logoText.js'
import { outlineTextMarkup } from '../logo/textOutline.js'

/** The flag's own proportions, from the artwork rather than from any measurement of a document. */
export const FLAG_ASPECT = FLAG.width / FLAG.height

export const LETTERS = 'BC'

/** The line the documents set above the ministry, where they set one. */
export const PROVINCE_LINE = 'Province of British Columbia'

/**
 * The configurations you can pick between: the two the standards page sanctions, and the one the
 * documents added.
 *
 * `badge` is deliberately not among them. It is not a way of arranging the symbol — it is one
 * particular mark, BC Parks, and it belongs in the gallery of one-offs rather than in a list of
 * general arrangements. It is still a valid value, because the gallery sets it.
 */
export const FLAG_SYMBOLS = ['horizontal', 'vertical', 'flag']

/** Every symbol the renderer understands, pickable or not. What a stored value is checked against. */
export const ALL_FLAG_SYMBOLS = [...FLAG_SYMBOLS, 'badge']

export const FLAG_SYMBOL_LABELS = {
  horizontal: 'Horizontal',
  vertical: 'Vertical',
  flag: 'Flag only',
  badge: 'Badge'
}

export const FLAG_SYMBOL_HINTS = {
  horizontal: 'BC, then the flag. One of the two the standards page sanctions.',
  vertical: 'The flag above BC. The standards page’s other configuration.',
  flag: 'The flag alone. Common in the documents, though the standard does not show it.',
  badge: 'Inside a rounded frame, the wording set at the same size as BC — the BC Parks mark.'
}

export const NAME_PLACEMENTS = ['below', 'beside']

export const NAME_PLACEMENT_LABELS = { below: 'Below', beside: 'Beside' }

export const NAME_PLACEMENT_HINTS = {
  below: 'The wording under the symbol, aligned to its left edge.',
  beside: 'The wording to the right of the symbol, centred against it.'
}

/**
 * How the symbol is built, per configuration. Distances are multiples of the BC cap height.
 *
 * These are applications rather than a specification: the standards page shows the symbol and its
 * colours but never a ministry name, so every number below is measured off a printed document, and
 * the documents disagree. The flag stands 1.12 cap heights tall in one, 1.28 in another and 1.58
 * in a third. What is consistent is the arrangement, and that is what these reproduce.
 */
export const ARRANGEMENTS = {
  // BC, then the flag, its foot on the letters' baseline. Measured off "Ministry of Forests".
  horizontal: { flagHeight: 1.12, gap: 0.04, letters: true, flagAbove: false },
  // The flag above BC, left edges flush, its foot on the letters' cap line. Measured off
  // "Province of British Columbia · Ministry of Environment".
  vertical: { flagHeight: 1.28, gap: 0.01, letters: true, flagAbove: true },
  // No letters at all. Sized as the vertical configuration's flag.
  flag: { flagHeight: 1.28, gap: 0, letters: false, flagAbove: false }
}

/**
 * Where the wording goes, again in cap heights.
 *
 * Measured between 0.13 and 0.24 for `below` across the documents, and between 0.19 and 0.45 for
 * `beside`. These sit inside both ranges.
 */
export const PLACEMENTS = {
  below: { gap: 0.18, nameCap: 0.27 },
  // Both documents that set the wording beside the symbol also draw the flag half again as large
  // against the letters — 1.58 cap heights in one, 1.63 in the other, against 1.12 where the
  // wording goes underneath. Two samples is a correlation rather than a rule, but reproducing what
  // was printed matters more here than theorising about why.
  // …and they open the space between the letters and the flag, 0.36 cap heights against the 0.04
  // that has them all but touching where the wording goes underneath.
  beside: { gap: 0.42, nameCap: 0.3, flagHeight: 1.6, symbolGap: 0.36 }
}

/**
 * Ministry cap height, as a fraction of the BC cap. The default; each placement has its own.
 *
 * The two placements really do differ, and not by a rounding: set beside the symbol the wording
 * runs at 0.30 of the BC cap — exactly, from a vector extraction that carries its text live and
 * sets "BC" at 40pt against a ministry at 12pt — and set underneath it runs smaller, between 0.25
 * and 0.28 across three documents. Forcing one value onto both pushes "Ministry of Forests" onto a
 * second line, which none of the references do.
 */
export const NAME_CAP = 0.27

/**
 * Width the wording wraps to, in cap heights.
 *
 * Not the symbol's width: where the symbol is the flag alone it is barely two cap heights across,
 * and wrapping to that puts one word on a line.
 *
 * The value was 3.4 and that was wrong — arrived at by dividing one document's flag *width* by its
 * height ratio, which is not a number that means anything. Measured properly the documents run
 * close to five: "Province of British Columbia", which nearly all of them set on one line, needs
 * 5.15 on its own. Above that the wording breaks where the sense does, and a newline forces a
 * break wherever a particular document put one.
 */
export const NAME_MEASURE = 5.5

/**
 * Leading, as a multiple of the type size.
 *
 * From the same vector extraction: its two ministry lines sit 13pt apart at 12pt, which is tighter
 * than the 1.2 this first used for want of anything better.
 */
const LEADING = 13 / 12

/** Extra space between the province line, the ministry and any third line, in lines. */
const BLOCK_GAP = 0.45

const BOLD = getFaceMetrics('bold')
const REGULAR = getFaceMetrics('regular')

/** The type size at which a face's capitals stand `cap` units tall. */
const sizeForCap = (cap, face) => cap * 1000 / face.capHeight

/**
 * Lays a lockup out, in units where the BC cap height is `cap`.
 *
 * The origin is the symbol's leftmost ink on the BC baseline, and y runs downward as SVG measures
 * it. Where there are no letters, the flag's own foot stands in for that baseline.
 *
 * @param {object} options
 * @param {string} [options.symbol]     'horizontal' | 'vertical' | 'flag'
 * @param {string} [options.placement]  'below' | 'beside'
 * @param {boolean} [options.province]  Set "Province of British Columbia" above the ministry.
 * @param {string} [options.ministry]   The ministry. Newlines break lines.
 * @param {string} [options.extra]      A third line — a minister, a place, a bulletin number.
 * @param {boolean} [options.bold]      Set the wording bold, as several of the documents do.
 * @param {number} [options.cap]        BC cap height, in whatever units the caller wants out.
 * @param {number} [options.measure]    Width to wrap to. Defaults to the symbol's own.
 */
export const layoutFlagLockup = ({
  symbol = 'horizontal',
  placement = 'below',
  province = false,
  ministry = '',
  extra = '',
  bold = false,
  cap = 100,
  measure
} = {}) => {
  const plan = ARRANGEMENTS[symbol] ?? ARRANGEMENTS.horizontal
  const where = PLACEMENTS[placement] ?? PLACEMENTS.below

  const lettersStyle = { fontSize: sizeForCap(cap, BOLD), weight: 'bold' }
  const letters = plan.letters ? measureLine(LETTERS, lettersStyle) : null
  const lettersWidth = letters ? letters.inkRight - letters.inkLeft : 0

  // A placement may set its own flag height, but only where there are letters to size it against.
  const flagHeight = (plan.letters ? (where.flagHeight ?? plan.flagHeight) : plan.flagHeight) * cap
  const flagWidth = flagHeight * FLAG_ASPECT

  // The symbol, in a space where the BC baseline is y = 0 and its own ink starts at x = 0.
  let flagX = 0
  let flagY = -flagHeight
  let lettersX = 0

  if (plan.letters) {
    lettersX = -letters.inkLeft
    if (plan.flagAbove) {
      // Flush left with the letters, standing on their cap line.
      flagY = -cap - plan.gap * cap - flagHeight
    } else {
      // Beside them, hanging from the baseline so their feet line up.
      flagX = lettersWidth + (where.symbolGap ?? plan.gap) * cap
    }
  }

  const symbolRight = Math.max(flagX + flagWidth, plan.letters && plan.flagAbove ? lettersWidth : 0)
  const symbolTop = Math.min(flagY, plan.letters ? -letters.inkTop : 0)

  // ── The wording ────────────────────────────────────────────────────────────────────────────
  const nameCap = (where.nameCap ?? NAME_CAP) * cap
  // Several documents set the ministry bold and several set it regular; it is a choice, not a rule.
  const nameStyle = bold
    ? { fontSize: sizeForCap(nameCap, BOLD), weight: 'bold' }
    : { fontSize: sizeForCap(nameCap, REGULAR) }
  const provinceStyle = { fontSize: sizeForCap(nameCap, BOLD), weight: 'bold' }
  const wrapTo = measure ?? NAME_MEASURE * cap

  const blocks = []
  if (province) {
    blocks.push(wrapText(PROVINCE_LINE, wrapTo, provinceStyle).map((text) => ({ text, style: provinceStyle })))
  }
  if (String(ministry).trim()) {
    blocks.push(wrapText(ministry, wrapTo, nameStyle).map((text) => ({ text, style: nameStyle })))
  }
  if (String(extra).trim()) {
    blocks.push(wrapText(extra, wrapTo, nameStyle).map((text) => ({ text, style: nameStyle })))
  }

  const leading = nameStyle.fontSize * LEADING
  const entries = []
  let pen = 0

  blocks.forEach((block, index) => {
    if (index) pen += leading * BLOCK_GAP
    for (const line of block) {
      entries.push({ ...line, offset: pen, ink: measureLine(line.text, line.style) })
      pen += leading
    }
  })

  const nameX = placement === 'beside' ? symbolRight + where.gap * cap : 0
  const firstBaseline = placement === 'beside'
    // The wording's last line sits on the letters' baseline, so the block grows upward as it
    // gains lines. Measured off the vector extraction, whose two lines end within four tenths of
    // a point of the BC baseline — the same rule the current era's marks follow.
    ? -(entries.length ? entries.at(-1).offset : 0)
    : where.gap * cap + nameCap

  const placed = entries.map((entry) => ({
    text: entry.text,
    style: entry.style,
    // Pulled so each line's own ink starts at the block's left edge.
    x: nameX - entry.ink.inkLeft,
    y: firstBaseline + entry.offset,
    words: positionWords(entry.text, entry.style),
    ink: entry.ink
  }))

  const right = Math.max(symbolRight, ...placed.map((line) => line.x + line.ink.inkRight))
  const bottom = Math.max(0, ...placed.map((line) => line.y - line.ink.inkBottom))
  const top = Math.min(symbolTop, ...placed.map((line) => line.y - line.ink.inkTop))

  return {
    cap,
    symbol,
    placement,
    letters: plan.letters ? { style: lettersStyle, x: lettersX, y: 0, ink: letters } : null,
    flag: { x: flagX, y: flagY, width: flagWidth, height: flagHeight },
    lines: placed,
    box: { x: 0, y: top, width: right, height: bottom - top }
  }
}

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value, places = 3) => {
  const factor = 10 ** places
  return Math.round(value * factor) / factor
}

/**
 * The flag artwork, scaled, positioned and coloured.
 *
 * The palette decides each shape's colour; 'ink' paints the whole flag in the lockup's own, which
 * is how the documents set it on anything but white.
 */
export const flagMarkup = ({ x, y, width }, palette = 'official', ink) => {
  const scale = width / FLAG.width
  const shapes = FLAG.shapes
    .map((shape) => `<path data-role="flag" d="${shape.d}" fill="${escapeXml(paletteFill(palette, shape.fill, ink))}"/>`)
    .join('')

  return `<g transform="translate(${round(x)} ${round(y)}) scale(${round(scale, 6)})">${shapes}</g>`
}

const textMarkup = (lines, fill, fontFamily, role) => lines.map((line) => {
  const content = line.words.length === 1
    ? escapeXml(line.words[0].text)
    : line.words.map((word) => `<tspan x="${round(line.x + word.x)}">${escapeXml(word.text)}</tspan>`).join('')
  const weight = line.style.weight === 'bold' ? ' font-weight="700"' : ''

  return `<text data-role="${role}" x="${round(line.x)}" y="${round(line.y)}" fill="${escapeXml(fill)}"` +
    ` font-family="${escapeXml(fontFamily)}" font-size="${round(line.style.fontSize)}"${weight}>${content}</text>`
}).join('')

/**
 * The lockup as an SVG fragment.
 *
 * Pass `glyphs` — the outline table from the font build — to draw the type as paths rather than as
 * live text. The layout is identical either way.
 */
export const flagLockupMarkup = ({
  layout, letterColor, textColor, flagPalette = 'official', fontFamily = LOGO_FONT_FAMILY, glyphs
}) => {
  const letters = layout.letters
    ? [{
        text: LETTERS,
        style: layout.letters.style,
        x: layout.letters.x,
        y: layout.letters.y,
        words: positionWords(LETTERS, layout.letters.style)
      }]
    : []

  const type = glyphs
    ? outlineTextMarkup(letters, glyphs, letterColor) + outlineTextMarkup(layout.lines, glyphs, textColor)
    : textMarkup(letters, letterColor, fontFamily, 'letters') +
      textMarkup(layout.lines, textColor, fontFamily, 'name')

  return flagMarkup(layout.flag, flagPalette, letterColor) + type
}
