// Drawing the type as paths instead of as text.
//
// A logo handed to a printer, dropped into someone else's layout, or opened in a tool that never
// heard of @font-face has to survive without the typeface. Outlining is the standard answer, and
// it is what "convert text to outlines" means in every design application.
//
// The pen arithmetic here deliberately mirrors measureLine() in logoText.js — same widths, same
// letter and word spacing, same rule about the gap after the last character. An outlined lockup
// and a live-text one have to be the same drawing, or the option is a trap rather than a choice.

import { FALLBACK_WIDTH, getFaceMetrics } from './fontMetrics.js'
import { escapeXml } from './renderLogoSvg.js'

const SPACE = 32

const round = (value) => Math.round(value * 100) / 100

/**
 * One laid-out line as a group of glyph paths.
 *
 * Glyph outlines are stored in the font's own units, so the group carries a single scale and each
 * glyph carries only its pen offset — which keeps the numbers integral and the markup about as
 * small as outlined type gets.
 *
 * @param {object} line          A line from `resolveLockup`: text, style, x and y.
 * @param {object} faces         The loaded outline table, keyed 'regular' / 'bold'.
 * @returns {string} SVG markup, or '' if the face is missing.
 */
export const outlineLineMarkup = (line, faces) => {
  const { style, text, x, y } = line
  const face = faces?.[style.weight === 'bold' ? 'bold' : 'regular']
  if (!face) return ''

  const { unitsPerEm, glyphs } = face
  const metrics = getFaceMetrics(style.weight)
  const characters = [...String(text)]

  const paths = []
  let pen = 0

  characters.forEach((character, index) => {
    const point = character.codePointAt(0)
    const outline = glyphs[point]

    if (outline) {
      // A glyph at the line's origin needs no transform at all, which is the common case for the
      // first one and worth not paying for.
      paths.push(pen === 0
        ? `<path d="${outline}"/>`
        : `<path transform="translate(${round(pen)} 0)" d="${outline}"/>`)
    }

    const width = metrics.widths.get(point) ?? FALLBACK_WIDTH
    // Widths are in 1/1000 em; the outlines are in font units.
    pen += width / 1000 * unitsPerEm
    if (point === SPACE) pen += (style.wordSpacing || 0) * unitsPerEm
    if (index < characters.length - 1) pen += (style.letterSpacing || 0) * unitsPerEm
  })

  if (!paths.length) return ''

  const scale = style.fontSize / unitsPerEm

  return `<g transform="translate(${x} ${y}) scale(${round(scale * 10000) / 10000})">${paths.join('')}</g>`
}

/** Every line of a lockup, outlined, under one fill. */
export const outlineTextMarkup = (lines, faces, fill) => {
  const body = lines.map((line) => outlineLineMarkup(line, faces)).join('')
  return body ? `<g fill="${escapeXml(fill)}">${body}</g>` : ''
}

/** True when the table has both faces and can actually replace live text. */
export const canOutline = (faces) => Boolean(faces?.regular?.glyphs && faces?.bold?.glyphs)
