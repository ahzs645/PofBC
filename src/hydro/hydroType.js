// Setting BC Hydro's lettering, from a table rather than a canvas.
//
// The studio this was ported from measured every letter by asking a browser canvas, which tied its
// layout to whichever serif the machine happened to have installed and made it impossible to run
// anywhere but a page. This measures against the committed TeX Gyre Termes table instead
// (src/hydro/serif.js), so a sign's borders come out the same in Node, in a test and in every
// browser — and the letters it draws are the ones it measured.
//
// A run is a line of type: where each letter's pen lands, and the box its ink covers. The
// arithmetic is the canvas's, kept deliberately: the fitted wordmark positions were measured with
// it, and changing how a box is taken would move every sign border.

import { CAP_HEIGHT, GLYPHS, KERNING, SERIF_FAMILY, X_HEIGHT } from './serif.js'

/** The font stack live text asks for: the face the layout was measured with, then its relatives. */
export const HYDRO_FONT_STACK = `"${SERIF_FAMILY}", "Nimbus Roman", "Times New Roman", Times, serif`

const FALLBACK = { w: 500 }
const glyphOf = (character) => GLYPHS[character] ?? FALLBACK

/** Cap height and x-height of the serif, in the units of a given size. */
export const capHeightAt = (size) => CAP_HEIGHT * size / 1000
export const xHeightAt = (size) => X_HEIGHT * size / 1000

/** Characters of some wording the serif has no letter for, in order, without repeats. */
export const missingLetters = (text) => [...new Set(
  Array.from(String(text)).filter((character) => character.trim() && !GLYPHS[character]?.d)
)]

const union = (box, next) => box
  ? {
      x: Math.min(box.x, next.x),
      y: Math.min(box.y, next.y),
      right: Math.max(box.right, next.right),
      bottom: Math.max(box.bottom, next.bottom)
    }
  : { ...next }

export { union as unionBox }

/**
 * Sets a line of type.
 *
 * @param {string} text
 * @param {object} options
 * @param {number} options.x, options.y  Where the pen starts, on the baseline.
 * @param {number} options.size          Font size, in the drawing's units.
 * @param {number} [options.sx=1]        Horizontal scale — the wordmark's letters are condensed.
 * @param {number} [options.sy=1]        Vertical scale.
 * @param {number} [options.tracking=0]  Added after every letter, in the size's units, before scale.
 * @param {boolean} [options.optical]    Letters placed by hand: no kerning between them.
 * @param {string} [options.id]
 */
export const setRun = (text, { x, y, size, sx = 1, sy = 1, tracking = 0, optical = false, id = 'text' }) => {
  const chars = Array.from(text)
  const k = size / 1000
  const positions = []
  let cursor = 0
  let box = null

  chars.forEach((character, i) => {
    if (!optical && i > 0) cursor += (KERNING[chars[i - 1] + character] ?? 0) * k
    positions.push(cursor)
    const glyph = glyphOf(character)
    if (character.trim() && glyph.box) {
      const [left, top, right, bottom] = glyph.box
      box = union(box, {
        x: x + (cursor + left * k) * sx,
        y: y + top * k * sy,
        right: x + (cursor + right * k) * sx,
        bottom: y + bottom * k * sy
      })
    }
    cursor += glyph.w * k + tracking
  })

  return {
    id,
    text,
    chars,
    positions,
    x,
    y,
    size,
    sx,
    sy,
    box: box ?? { x, y, right: x, bottom: y },
    advance: Math.max(0, cursor - tracking) * sx
  }
}

/** Moves a run, box and all. */
export const shiftRun = (run, dx, dy) => {
  run.x += dx
  run.y += dy
  run.box = { x: run.box.x + dx, y: run.box.y + dy, right: run.box.right + dx, bottom: run.box.bottom + dy }
  return run
}

const num = (value) => Number(value.toFixed(4))

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;')

/**
 * A run as SVG: its letters as outlines by default, so the drawing is the same everywhere, or as
 * live text in the serif stack when an editable file is wanted. A letter the serif lacks falls back
 * to live text for the whole run rather than going missing.
 */
export const runMarkup = (run, { fill, outline = true, id }) => {
  const matrix = `matrix(${num(run.sx)} 0 0 ${num(run.sy)} ${num(run.x)} ${num(run.y)})`
  const idAttribute = id ? ` id="${escapeXml(id)}"` : ''

  if (outline && missingLetters(run.text).length === 0) {
    const k = num(run.size / 1000)
    const letters = run.chars
      .map((character, i) => {
        const d = GLYPHS[character]?.d
        return d ? `<path transform="translate(${num(run.positions[i])} 0) scale(${k})" d="${d}"/>` : ''
      })
      .join('')
    // The wording rides along as data, so an outlined file still says what it says.
    return `<g${idAttribute} data-text="${escapeXml(run.text)}" transform="${matrix}" fill="${escapeXml(fill)}">${letters}</g>`
  }

  return `<text${idAttribute} xml:space="preserve" x="${run.positions.map(num).join(' ')}" y="0" transform="${matrix}" ` +
    `font-family="${escapeXml(HYDRO_FONT_STACK)}" font-size="${num(run.size)}" font-weight="400" font-style="normal" ` +
    `fill="${escapeXml(fill)}" style="font-kerning:none;font-variant-ligatures:none">${escapeXml(run.text)}</text>`
}

export { escapeXml, num }
