// The flag identity: "BC" set beside the waving provincial flag, with the ministry name beneath.
//
// This is the identity that carried the Spirit of BC flag — the letters BC in a bold sans, the
// stylised flag to their right, and the ministry name on its own line below, left-aligned under
// the B.
//
// Everything here is proportional to one measurement, the cap height of the BC letters, so the
// lockup scales as a single drawing. The proportions come from a screenshot of the logo, which is
// the only reference available; see FLAG_METRICS for what that reference could and could not
// settle.

import { FLAG } from '../assets/flagMark.js'
import { getFaceMetrics } from '../logo/fontMetrics.js'
import { LOGO_FONT_FAMILY } from '../logo/renderLogoSvg.js'
import { measureLine, positionWords, wrapText } from '../logo/logoText.js'
import { outlineTextMarkup } from '../logo/textOutline.js'

/** The flag's own proportions, from the artwork rather than from any measurement of the logo. */
export const FLAG_ASPECT = FLAG.width / FLAG.height

/**
 * The lockup's proportions, as multiples of the BC cap height.
 *
 * Measured off a screenshot of the logo, which is the only reference to hand and a degraded
 * one-colour trace at that. Two things follow from that, and both are worth knowing:
 *
 * The flag is sized by its height rather than its width. The screenshot's flag has an aspect of
 * 1.49 against the artwork's own 1.301 — the top of its Union Jack has been eaten by the trace —
 * so its width cannot be trusted. Taking the height and letting the artwork's real aspect give the
 * width puts the finished lockup at 334 × 163 against the reference's 333 × 164.
 *
 * The letters are wider here than in the logo. Set at the screenshot's cap height, Helvetica Bold
 * draws "BC" about a tenth wider than the reference does, so the logo's letters are a narrower
 * bold than the one this project embeds. Helvetica is what is here, and the shapes are right even
 * where the width is not.
 */
export const FLAG_METRICS = {
  /** Ministry name cap height. Screenshot: 28px against a 100px BC cap. */
  nameCap: 0.28,
  /** BC baseline down to the name's cap line. Screenshot: 15px. */
  nameGap: 0.15,
  /** BC ink right to the flag's left edge. The screenshot shows them all but touching. */
  flagGap: 0.04,
  /** Flag height. Its width follows from FLAG_ASPECT. Screenshot: 112px against a 100px cap. */
  flagHeight: 1.12,
  /** How far the flag's foot sits below the BC baseline. */
  flagDrop: 0
}

/**
 * Leading for a wrapped name, as a multiple of the type size.
 *
 * Every name in the reference fits one line, so this is not measured from it. It is what the crest
 * artwork is set with, and that is the closest thing to a house convention this project has.
 */
const LEADING = 1.2

const BOLD = getFaceMetrics('bold')
const REGULAR = getFaceMetrics('regular')

/** The type size at which a face's capitals stand `cap` units tall. */
const sizeForCap = (cap, face) => cap * 1000 / face.capHeight

export const LETTERS = 'BC'

/**
 * Lays the lockup out, in units where the BC cap height is `cap`.
 *
 * The origin is the BC letters' leftmost ink on their baseline, and y runs downward as SVG
 * measures it — so the capitals occupy negative y and the ministry name positive.
 *
 * @param {object} options
 * @param {string} options.ministry   The wording beneath. Newlines break lines.
 * @param {number} [options.cap]      BC cap height, in whatever units the caller wants out.
 * @param {number} [options.measure]  Width to wrap the wording to. Defaults to the lockup's own.
 */
export const layoutFlagLockup = ({ ministry = '', cap = 100, measure } = {}) => {
  const m = FLAG_METRICS

  const lettersStyle = { fontSize: sizeForCap(cap, BOLD), weight: 'bold' }
  const letters = measureLine(LETTERS, lettersStyle)

  const flagHeight = m.flagHeight * cap
  const flagWidth = flagHeight * FLAG_ASPECT
  const flagX = letters.inkRight + m.flagGap * cap
  // The flag hangs from the baseline rather than sitting on the cap line: its foot lines up with
  // the letters' feet and it overshoots them at the top, which is what the logo does.
  const flagY = m.flagDrop * cap - flagHeight

  const nameStyle = { fontSize: sizeForCap(m.nameCap * cap, REGULAR) }
  const lockupWidth = flagX + flagWidth - letters.inkLeft

  const lines = wrapText(ministry, measure ?? lockupWidth, nameStyle)
    .map((text) => ({ text, ...measureLine(text, nameStyle) }))

  // The name's cap line sits a fixed distance under the BC baseline, so a first line with no
  // ascender does not ride up and one with a descender does not push the block down.
  const firstBaseline = m.nameGap * cap + m.nameCap * cap
  // The reference names are all one line, so there is nothing to measure here. This is the same
  // leading the crest artwork is set with — 1.2 times the type size — which is the house
  // convention and looks it.
  const leading = nameStyle.fontSize * LEADING

  const placed = lines.map((line, index) => ({
    text: line.text,
    style: nameStyle,
    // Pulled so the wording's own ink starts where the B's does.
    x: letters.inkLeft - line.inkLeft,
    y: firstBaseline + index * leading,
    words: positionWords(line.text, nameStyle),
    ink: line
  }))

  const right = Math.max(
    flagX + flagWidth,
    ...placed.map((line) => line.x + line.ink.inkRight)
  )
  const bottom = placed.length
    ? placed.at(-1).y - placed.at(-1).ink.inkBottom
    : 0
  const top = Math.min(-letters.inkTop, flagY)

  return {
    cap,
    letters: { style: lettersStyle, x: 0 - letters.inkLeft, y: 0, ink: letters },
    flag: { x: flagX, y: flagY, width: flagWidth, height: flagHeight },
    lines: placed,
    box: {
      x: letters.inkLeft,
      y: top,
      width: right - letters.inkLeft,
      height: bottom - top
    }
  }
}

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value, places = 3) => {
  const factor = 10 ** places
  return Math.round(value * factor) / factor
}

/**
 * The flag artwork, scaled and positioned.
 *
 * `ink` paints every shape one colour instead of the flag's own three, which is how the logo is
 * used where a single colour is all there is.
 */
export const flagMarkup = ({ x, y, width, height }, ink) => {
  const scale = width / FLAG.width
  const shapes = FLAG.shapes
    .map((shape) => `<path data-role="flag" d="${shape.d}" fill="${escapeXml(ink ?? shape.fill)}"/>`)
    .join('')

  void height
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
  layout, letterColor, textColor, flagInk, fontFamily = LOGO_FONT_FAMILY, glyphs
}) => {
  const letters = [{
    text: LETTERS,
    style: layout.letters.style,
    x: layout.letters.x,
    y: layout.letters.y,
    words: positionWords(LETTERS, layout.letters.style)
  }]

  const type = glyphs
    ? outlineTextMarkup(letters, glyphs, letterColor) + outlineTextMarkup(layout.lines, glyphs, textColor)
    : textMarkup(letters, letterColor, fontFamily, 'letters') +
      textMarkup(layout.lines, textColor, fontFamily, 'name')

  return flagMarkup(layout.flag, flagInk) + type
}
