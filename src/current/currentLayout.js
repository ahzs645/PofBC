// Setting a ministry name beside the BC mark.
//
// The published marks draw their wording as outlines, which means the wording cannot be changed —
// a ministry that is renamed, or one that never had a mark published, has nothing to use. This
// sets the name instead, from the same alphabet the Province's own artwork is drawn with, to the
// measurements taken off that artwork: the mark's alphabet, its tracking, its kerning, its
// leading, and the baseline its last line sits on.
//
// Everything here is plain string building over a table of numbers, so it runs in Node, in a
// worker and in the browser before anything has loaded — the same property the crest era's
// renderer has.

import { CURRENT_MARK, NAME_LEADING } from '../assets/currentMark.js'
import published from './nameGlyphs.js'
import extra from './generated/nameGlyphsExtra.js'
import { EXTENTS, KERNING, LIGATURES, TRACKING, WIDTHS } from './nameMetrics.js'

/**
 * The letterforms available to set a name with.
 *
 * `nameGlyphs.js` holds the letters the Province's own published marks are drawn with, recovered
 * from that artwork and committed, so the official wording always works. `generated/` holds the
 * rest of the alphabet, built from a licensed Adobe Garamond Pro and gitignored — a full alphabet
 * of outlines is the typeface however it is stored. Without it this is simply a smaller alphabet,
 * and `unsupported()` says which letters are missing rather than dropping them silently.
 */
const glyphs = { ...extra, ...published }

/** Width of a missing glyph. A name should not contain one, but it should not collapse either. */
const FALLBACK_WIDTH = 500

/**
 * Text with Adobe Garamond's f-ligatures substituted in.
 *
 * Not cosmetic: the published marks are set with them, so "Affairs" is four letterforms wide and
 * not six. Leaving them out puts every following letter in the wrong place.
 */
export const foldLigatures = (text) => LIGATURES
  .reduce((out, [from, to]) => out.split(from).join(to), String(text))

/** The characters of a string as the alphabet sees them — ligatures counted once. */
export const lettersOf = (text) => [...foldLigatures(text)]

const widthOf = (letter) => WIDTHS[letter] ?? FALLBACK_WIDTH

/** The characters of some wording that have no letterform available, in order, without repeats. */
export const unsupported = (text) => [...new Set(
  lettersOf(String(text).replace(/\s+/g, ' ')).filter((letter) => letter !== ' ' && !glyphs[letter])
)]

/**
 * How far the pen travels across a line, in 1/1000 em.
 *
 * Tracking is added after every letter but the last: it is space between letters, not a margin on
 * the end. Kerning is looked up on the folded pair, which is why the fold has to happen first.
 */
export const measureLine = (text) => {
  const letters = lettersOf(text)
  let pen = 0

  letters.forEach((letter, index) => {
    pen += widthOf(letter)
    const next = letters[index + 1]
    if (next === undefined) return
    pen += TRACKING + (KERNING[letter + next] ?? 0)
  })

  return pen
}

/** Where a line's ink starts and ends, in 1/1000 em, as opposed to where the pen does. */
export const inkOf = (text) => {
  const letters = lettersOf(text)
  if (!letters.length) return { left: 0, right: 0, top: 0, bottom: 0 }

  let pen = 0
  let left = Infinity
  let right = -Infinity
  let top = Infinity
  let bottom = -Infinity

  letters.forEach((letter, index) => {
    const extent = EXTENTS[letter]
    if (extent) {
      left = Math.min(left, pen + extent[0])
      right = Math.max(right, pen + extent[1])
      top = Math.min(top, extent[2])
      bottom = Math.max(bottom, extent[3])
    }
    pen += widthOf(letter)
    const next = letters[index + 1]
    if (next !== undefined) pen += TRACKING + (KERNING[letter + next] ?? 0)
  })

  return {
    left: Number.isFinite(left) ? left : 0,
    right: Number.isFinite(right) ? right : 0,
    top: Number.isFinite(top) ? top : 0,
    bottom: Number.isFinite(bottom) ? bottom : 0
  }
}

/**
 * The opening of a ministry name, which the published marks always give a line of its own.
 *
 * Every mark reads "Ministry of …" or "Ministère de/des/du/de la/de l'…" on its first line and
 * begins the ministry proper on the second, however short either is — "Ministry of Health" is two
 * lines. Reproducing that is the difference between a typeset name that matches the published ones
 * and one that merely says the same words.
 */
// "de la" is taken as part of the opening, but a bare elision is not: the published French marks
// read "Ministère de" then "l’Agriculture et de", keeping l’ with the word it elides.
const OPENINGS = [
  /^Minist(?:ry|ère)\s+de\s+la\b/i,
  /^Minist(?:ry|ère)\s+(?:of|des|du|de)\b/i
]

export const splitOpening = (text) => {
  const trimmed = String(text).trim().replace(/\s+/g, ' ')
  for (const pattern of OPENINGS) {
    const match = pattern.exec(trimmed)
    if (match) return [match[0].trim(), trimmed.slice(match[0].length).trim()].filter(Boolean)
  }
  return [trimmed]
}

/**
 * Greedy line breaking on a measure, in 1/1000 em.
 *
 * Greedy rather than balanced because that is what the published marks do: their lines run long
 * then break, rather than evening out.
 */
export const wrapText = (text, measure) => {
  const words = String(text).split(/\s+/).filter(Boolean)
  if (!words.length) return []

  const lines = []
  let current = words[0]

  for (const word of words.slice(1)) {
    const candidate = `${current} ${word}`
    if (measureLine(candidate) <= measure) current = candidate
    else { lines.push(current); current = word }
  }
  lines.push(current)
  return lines
}

/**
 * Default measure for text that does not say where to break, in 1/1000 em.
 *
 * The published marks do not share one: their widest body line runs from 2.3 em to 12.3 em, which
 * is to say a designer broke each of them by hand, by sense. No single measure reproduces more
 * than about half of them, so the official wording carries its own breaks and this is only the
 * fallback for wording that has none.
 */
export const MEASURE = 8500

/**
 * A name broken into lines.
 *
 * A newline in the text is a break, and is obeyed — that is how the official wording keeps the
 * line breaks the Province gave it, and how anyone editing a name can set their own. Wording with
 * no newlines gets its opening on a line of its own and the rest wrapped to the measure.
 */
export const nameLines = (text, measure = MEASURE) => {
  const forced = String(text).split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  // Breaks that were asked for are obeyed as given, never re-wrapped. Several of the Province's own
  // lines run wider than any sensible measure, and re-wrapping them would quietly overrule the
  // artwork — and, for anyone editing a name, quietly overrule them too.
  if (forced.length > 1) return forced

  const [opening, ...rest] = splitOpening(forced[0] ?? '')
  if (!opening) return []
  if (!rest.length) return wrapText(opening, measure)
  return [opening, ...wrapText(rest.join(' '), measure)]
}

/**
 * A full lockup: where the mark sits, where the rule sits, and where each line of the name goes.
 *
 * All coordinates are in points, in the mark's own space. The name is anchored from the bottom —
 * its last baseline is the wordmark's — so adding a line pushes the block upward and can make the
 * lockup taller than the mark.
 *
 * @param {object} options
 * @param {string} options.text        The ministry name, "Ministry of …" included.
 * @param {string} [options.language]  'en' | 'fr' — picks the wordmark and its measurements.
 * @param {number} [options.measure]   Wrap measure, in 1/1000 em.
 */
export const layoutLockup = ({ text, language = 'en', measure = MEASURE }) => {
  const mark = CURRENT_MARK[language] ?? CURRENT_MARK.en
  const lines = nameLines(text, measure)
  const size = mark.size
  const em = size / 1000

  const placed = lines.map((line, index) => ({
    text: line,
    x: mark.nameX,
    // The last line sits on the wordmark's baseline; earlier lines stack upward from it.
    baseline: mark.baseline - (lines.length - 1 - index) * NAME_LEADING,
    ink: inkOf(line)
  }))

  const right = placed.reduce((widest, line) => Math.max(widest, line.x + line.ink.right * em), mark.width)
  const top = placed.reduce((highest, line) => Math.min(highest, line.baseline + line.ink.top * em), 0)
  const bottom = placed.reduce((lowest, line) => Math.max(lowest, line.baseline + line.ink.bottom * em), mark.height)

  return {
    mark,
    lines: placed,
    size,
    box: { x: 0, y: Math.min(0, top), width: right, height: bottom - Math.min(0, top) }
  }
}

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

/** One line of type as SVG paths, positioned and scaled out of the alphabet. */
export const lineMarkup = (line, size, fill) => {
  const letters = lettersOf(line.text)
  const em = size / 1000
  const parts = []
  let pen = 0

  letters.forEach((letter, index) => {
    const d = glyphs[letter]
    if (d) {
      const x = line.x + pen * em
      // The alphabet is drawn on a 1000-unit em with y already running downward, so placing a
      // letter is a translate and a uniform scale — no flip, no per-glyph arithmetic.
      parts.push(`<path data-role="name" transform="translate(${round(x)} ${round(line.baseline)}) scale(${round(em, 5)})" d="${d}" fill="${escapeXml(fill)}"/>`)
    }
    pen += widthOf(letter)
    const next = letters[index + 1]
    if (next !== undefined) pen += TRACKING + (KERNING[letter + next] ?? 0)
  })

  return parts.join('')
}

const round = (value, places = 3) => {
  const factor = 10 ** places
  return Math.round(value * factor) / factor
}

/**
 * The whole lockup as SVG markup, ready to be coloured by a colourway.
 *
 * Every shape carries its data-role, exactly as the published files do, so the same recolouring
 * applies whether the wording came out of a PDF or was set here.
 */
export const lockupMarkup = ({ text, language = 'en', fills }) => {
  const layout = layoutLockup({ text, language })
  const { mark } = layout
  const parts = []

  for (const shape of mark.shapes) {
    const fill = fills[shape.role]
    // A role with no colour is dropped rather than painted, so the background shows through.
    if (fill === null || fill === undefined) continue
    parts.push(`<path data-role="${shape.role}" d="${shape.d}" fill="${escapeXml(fill)}"/>`)
  }

  if (fills.divider !== null && fills.divider !== undefined) {
    parts.push(`<rect data-role="divider" x="${mark.divider.x}" y="0" ` +
      `width="${mark.divider.width}" height="${mark.divider.height}" fill="${escapeXml(fills.divider)}"/>`)
  }

  if (fills.name !== null && fills.name !== undefined) {
    for (const line of layout.lines) parts.push(lineMarkup(line, layout.size, fills.name))
  }

  return { markup: parts.join(''), box: layout.box, lines: layout.lines.map((l) => l.text) }
}
