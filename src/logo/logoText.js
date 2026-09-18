// Text measurement and line breaking for the lockups.
//
// Everything here works off the generated metrics table rather than a canvas or the DOM, so a
// lockup measures the same in Node, in a worker and in the browser — including on the very first
// paint, before the webfont has loaded. That is what lets the renderer emit a tight, correct
// viewBox in one pass instead of drawing, measuring, and reflowing.
//
// All measurements are in *artwork units*: the same space the mark is drawn in, where the mark is
// 497.02 × 497.19. Each layout supplies its own font size in those units.

import { FALLBACK_WIDTH, getFaceMetrics } from './fontMetrics.js'

/**
 * A run of text and how it should be set.
 *
 * @typedef {object} TextStyle
 * @property {number} fontSize       In artwork units.
 * @property {'regular'|'bold'} weight
 * @property {number} [letterSpacing] Added between characters, in em. Negative tightens.
 * @property {number} [wordSpacing]   Added at each space, in em. The province wordmark is set
 *                                    with a little extra air between words.
 */

const normalize = ({ fontSize, weight = 'regular', letterSpacing = 0, wordSpacing = 0 }) => ({
  fontSize,
  weight,
  letterSpacing,
  wordSpacing,
  face: getFaceMetrics(weight)
})

const SPACE = 32

/**
 * Measures a single line.
 *
 * `advance` is the pen distance from start to end — what the next thing on the line would be
 * placed at. The `ink*` values are where the letterforms actually reach, which is usually inset
 * from the advance (an 'o' has air on both sides) and is what the lockup's bounding box uses.
 *
 * @returns {{advance: number, inkLeft: number, inkRight: number, inkTop: number, inkBottom: number}}
 */
export const measureLine = (text, style) => {
  const { fontSize, letterSpacing, wordSpacing, face } = normalize(style)
  const characters = [...String(text)]

  let pen = 0
  let inkLeft = Infinity
  let inkRight = -Infinity
  let inkTop = 0
  let inkBottom = 0

  characters.forEach((character, index) => {
    const point = character.codePointAt(0)
    const width = face.widths.get(point) ?? FALLBACK_WIDTH
    const top = face.tops.get(point) ?? 0
    const bottom = face.bottoms.get(point) ?? 0

    // Blank glyphs contribute advance but no ink, so they must not drag the box outwards.
    if (top !== bottom) {
      const bearing = face.bearings.get(point) ?? 0
      inkLeft = Math.min(inkLeft, pen + bearing)
      // The ink edge, not the advance: the pen moves on past the right side bearing, but nothing
      // is drawn there, and a bounding box that included it would hug the letterforms on three
      // sides and leave a gap on the fourth.
      inkRight = Math.max(inkRight, pen + (face.rights.get(point) ?? width))
      inkTop = Math.max(inkTop, top)
      inkBottom = Math.min(inkBottom, bottom)
    }

    pen += width + (point === SPACE ? wordSpacing * 1000 : 0)
    // Letter spacing falls between characters; the notional gap after the last one is not ink and
    // would otherwise widen every measurement by one increment.
    if (index < characters.length - 1) pen += letterSpacing * 1000
  })

  const scale = fontSize / 1000

  return {
    advance: pen * scale,
    inkLeft: (inkLeft === Infinity ? 0 : inkLeft) * scale,
    inkRight: (inkRight === -Infinity ? 0 : inkRight) * scale,
    // Ink above the baseline is positive here; callers flip it into SVG's y-down space.
    inkTop: inkTop * scale,
    inkBottom: inkBottom * scale
  }
}

/** Convenience: the advance width of a line, in artwork units. */
export const measureWidth = (text, style) => measureLine(text, style).advance

/**
 * Breaks text to fit `maxWidth`, in artwork units.
 *
 * Explicit newlines are always honoured — a caller that has decided where the line should break
 * gets to keep that decision. A single word longer than the measure is left to overflow rather
 * than being hyphenated or scaled: silently mangling a ministry name is worse than a wide logo,
 * and the caller can see the overflow and widen the measure.
 */
export const wrapText = (text, maxWidth, style) => {
  const paragraphs = String(text ?? '').split(/\r?\n/)
  const lines = []

  for (const paragraph of paragraphs) {
    const words = paragraph.split(/\s+/).filter(Boolean)

    if (!words.length) {
      // A blank line in the input is a deliberate gap; keep it.
      if (paragraph.trim() === '' && paragraphs.length > 1) lines.push('')
      continue
    }

    let current = words[0]

    for (const word of words.slice(1)) {
      const candidate = `${current} ${word}`
      if (!maxWidth || measureWidth(candidate, style) <= maxWidth) current = candidate
      else { lines.push(current); current = word }
    }

    lines.push(current)
  }

  return lines
}

/**
 * Lays out already-wrapped lines into a text block.
 *
 * Each entry is `{ text, style }` — the lockups mix weights within one block (the province
 * wordmark is bold, the ministry line beneath it is not) while keeping a single uniform leading
 * across the whole thing, so the style travels with the line rather than with the block.
 *
 * Baselines are relative to the first line's, which is always 0. Vertical placement is left to the
 * layout, which knows whether the block hangs below the mark or sits centred beside it.
 */
export const layoutBlock = (entries, leading) => {
  const lines = entries.map((entry, index) => ({
    text: entry.text,
    style: entry.style,
    baseline: index * leading,
    ...measureLine(entry.text, entry.style)
  }))

  const inked = lines.filter((line) => line.inkRight > line.inkLeft)
  const span = (pick, reduce, fallback) => (inked.length ? reduce(...inked.map(pick)) : fallback)

  return {
    lines,
    advance: Math.max(0, ...lines.map((line) => line.advance)),
    inkLeft: span((line) => line.inkLeft, Math.min, 0),
    inkRight: span((line) => line.inkRight, Math.max, 0),
    // In SVG's y-down space, ink above the first baseline is negative.
    inkTop: span((line) => line.baseline - line.inkTop, Math.min, 0),
    inkBottom: span((line) => line.baseline - line.inkBottom, Math.max, 0),
    height: lines.length ? (lines.length - 1) * leading : 0
  }
}

/**
 * Word positions along a line, in artwork units from the line's origin.
 *
 * Word gaps are emitted as explicit coordinates rather than relying on the `word-spacing`
 * presentation attribute, which is unevenly supported once an SVG leaves the browser — the same
 * file has to survive a canvas rasteriser and a PDF writer. It is also what Illustrator itself
 * wrote into the source artwork.
 */
export const positionWords = (text, style) => {
  const { wordSpacing } = normalize(style)
  const source = String(text)

  // With no extra word spacing the line needs no splitting at all, and a single text node keeps
  // the output markup readable.
  if (!wordSpacing) return [{ text: source, x: 0 }]

  const words = []
  let pen = 0

  for (const [, word, gap] of source.matchAll(/(\S+)(\s*)/g)) {
    words.push({ text: word, x: pen })
    // measureLine already folds the word spacing into the advance of any space it is given, so
    // measuring "word + gap" is the whole step; adding the spacing again here would double it.
    pen += measureWidth(word + gap, style)
  }

  return words.length ? words : [{ text: source, x: 0 }]
}
