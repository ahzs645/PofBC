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
import lifted from './liftedGlyphs.js'
import extra from './generated/nameGlyphsExtra.js'
import { EXTENTS, KERNING, LIGATURES, TRACKING, WIDTHS } from './nameMetrics.js'

/**
 * The letterforms available to set a name with.
 *
 * `nameGlyphs.js` holds the letters the Province's own published marks are drawn with, recovered
 * from that artwork and committed, so the official wording always works. `liftedGlyphs.js` adds the
 * capitals those marks never happen to use, taken from older marks the Province drew in the same
 * alphabet — committed too, for the same reason. `generated/` holds the
 * rest of the alphabet, built from a licensed Adobe Garamond Pro and gitignored — a full alphabet
 * of outlines is the typeface however it is stored. Without it this is simply a smaller alphabet,
 * and `unsupported()` says which letters are missing rather than dropping them silently.
 */
const glyphs = { ...extra, ...lifted, ...published }

/** Width of a missing glyph. A name should not contain one, but it should not collapse either. */
const FALLBACK_WIDTH = 500

/**
 * Text with Adobe Garamond's f-ligatures substituted in.
 *
 * Not cosmetic: the published marks are set with them, so "Affairs" is four letterforms wide and
 * not six. Leaving them out puts every following letter in the wrong place.
 *
 * A typewriter apostrophe becomes a typographer's one on the way, as it would in any typesetting:
 * every mark the Province published sets ’, and names typed or listed with ' — "Women's Equality"
 * — would otherwise ask for a letterform the marks never drew.
 */
export const foldLigatures = (text) => LIGATURES
  .reduce((out, [from, to]) => out.split(from).join(to), String(text).replace(/'/g, '’'))

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
// The opening is the word "Ministry"/"Ministère" and its following preposition, and no more. Not
// "de la" — the Province sets "Ministère de" then "la Santé" — and not a bare elision either, since
// l’ stays with the word it elides: "Ministère de" then "l’Agriculture et de".
const OPENINGS = [/^Minist(?:ry|ère)\s+(?:of|des|du|de)\b/i]

export const splitOpening = (text) => {
  const trimmed = String(text).trim().replace(/\s+/g, ' ')
  for (const pattern of OPENINGS) {
    const match = pattern.exec(trimmed)
    if (match) return [match[0].trim(), trimmed.slice(match[0].length).trim()].filter(Boolean)
  }
  return [trimmed]
}

/**
 * Greedy line breaking on a measure, in 1/1000 em. Used only for wording that overruns the
 * Province's own three-line shape, which their own names never do.
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
 * The width, in 1/1000 em, above which the ministry proper takes two lines instead of one.
 *
 * Measured, not chosen. Across the Province's 46 marks the two cases do not overlap at all: every
 * name that stays on one line measures at most 7793, and every name that is split measures at
 * least 8085. Anything in between would do; 8000 is the round number in the gap.
 */
export const MEASURE = 8000

/**
 * The width, in 1/1000 em, above which a two-line split is still too wide, so the ministry proper
 * takes three lines.
 *
 * The current marks never need it: the widest line any of them sets after an even split measures
 * 12296. The mark for Forests, Lands, Natural Resource Operations and Rural Development does — an
 * even split of its name would make a line of 13579, and the Province set it on three lines of at
 * most 9113 instead. 13000 is the round number in the gap. One mark is thin evidence, so this is
 * the least that reproduces it rather than a rule the artwork proves.
 */
export const THREE_LINE_MEASURE = 13000

/**
 * How even the two halves must be for the conjunction rule below to apply.
 *
 * Half is a natural floor — below it one line is a stub beside the other — and it is not a fitted
 * number: anything from 0.4 to 0.5 reproduces the same marks.
 */
const MIN_EVENNESS = 0.5

// French does not leave "et" hanging at the end of a line, and breaks before it where it can.
// English is happy to stand "and" at a line end — "Education and", "Jobs and", "Mining and" are
// all the Province's own — so this applies to French only.
const CONJUNCTION = { fr: 'et' }

// The word that closes an English list: "Water, Land and Resource Stewardship".
const LIST_CONJUNCTION = { en: 'and' }

/**
 * Whether a name is a list of items, and so should break between them rather than inside one.
 *
 * A comma is what gives it away. "Jobs, Economic Development and Innovation" is three items, and
 * the Province breaks it "Jobs, Economic Development / and Innovation" although "Jobs, Economic /
 * Development and Innovation" is the more even of the two. With no comma the "and" can sit inside
 * a single item: "Children and Family Development" is one thing, and its mark breaks it
 * "Children and Family / Development", which is the even split. The two misses are the same size,
 * about 100/1000 em, so no width rule can tell them apart; the comma can.
 */
const isList = (words, language) => Boolean(LIST_CONJUNCTION[language]) &&
  words.slice(0, -1).some((word) => word.endsWith(','))

/**
 * Splits the ministry proper across two lines the way the Province's own marks do.
 *
 * The base rule is to even the two lines up. English lists break only between items: after a
 * comma, or on either side of the "and" that closes the list, and the evenest of those breaks is
 * the one taken. French needs two rules of its own: never end a line on "et", and prefer to begin
 * the second line with it, so long as that does not leave one line less than half the other.
 */
const splitBody = (body, language) => {
  const words = body.split(' ')
  if (words.length < 2) return [body]

  const conjunction = CONJUNCTION[language]
  const listConjunction = LIST_CONJUNCTION[language]
  const list = isList(words, language)
  const candidates = []

  for (let i = 1; i < words.length; i += 1) {
    if (conjunction && words[i - 1].toLowerCase() === conjunction) continue
    const first = words.slice(0, i).join(' ')
    const second = words.slice(i).join(' ')
    const one = measureLine(first)
    const two = measureLine(second)
    candidates.push({
      lines: [first, second],
      widest: Math.max(one, two),
      evenness: Math.min(one, two) / Math.max(one, two),
      opensWithConjunction: Boolean(conjunction) && words[i].toLowerCase() === conjunction,
      betweenItems: words[i - 1].endsWith(',') ||
        [words[i - 1], words[i]].some((word) => word.toLowerCase() === listConjunction)
    })
  }

  // Every break was forbidden — a two-word body joined by "et" — so the rule has to yield.
  if (!candidates.length) return [body]

  const preferred = candidates
    .filter((c) => c.opensWithConjunction && c.evenness >= MIN_EVENNESS)
    .sort((a, b) => b.evenness - a.evenness)[0]
  if (preferred) return preferred.lines

  const allowed = list ? candidates.filter((c) => c.betweenItems) : candidates
  return (allowed.length ? allowed : candidates)
    .reduce((best, c) => (c.widest < best.widest ? c : best)).lines
}

/**
 * Splits the ministry proper across three lines, for the names too long for two.
 *
 * The same aim as the two-line split — even the lines up, which is to say make the widest as
 * narrow as it can be — and the same French rule against ending a line on "et".
 */
const splitBodyThree = (body, language) => {
  const words = body.split(' ')
  if (words.length < 3) return splitBody(body, language)

  const conjunction = CONJUNCTION[language]
  const endsOnConjunction = (index) => Boolean(conjunction) && words[index - 1].toLowerCase() === conjunction
  let best = null

  for (let i = 1; i < words.length - 1; i += 1) {
    if (endsOnConjunction(i)) continue
    for (let j = i + 1; j < words.length; j += 1) {
      if (endsOnConjunction(j)) continue
      const lines = [words.slice(0, i), words.slice(i, j), words.slice(j)].map((part) => part.join(' '))
      const widest = Math.max(...lines.map(measureLine))
      if (!best || widest < best.widest) best = { lines, widest }
    }
  }

  return best ? best.lines : splitBody(body, language)
}

/**
 * A name broken into lines, by the rules the Province's own marks follow.
 *
 * Those rules, read off all 46 published marks:
 *
 *   1. the opening — "Ministry of", "Ministère de/des/du" — takes a line of its own, however
 *      short what follows is. "Ministry of Health" is two lines.
 *   2. the ministry proper stays on one line up to MEASURE, and splits in two above it.
 *   3. the split evens the two lines up, with the French conjunction rules in splitBody. An
 *      English name with a comma is a list, and breaks only between its items.
 *   4. a name so long that even two lines would pass THREE_LINE_MEASURE takes three, evened the
 *      same way. No current mark is that long; the Forests, Lands, Natural Resource Operations and
 *      Rural Development mark was, and this reproduces it.
 *
 * Together they reproduce 44 of the 46 published marks exactly — every English one, and all but
 * two French. A newline in the text overrides the lot, which is how those two are carried and how
 * anyone setting their own wording gets the breaks they want.
 */
export const nameLines = (text, { language = 'en', measure = MEASURE } = {}) => {
  const forced = String(text).split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  if (forced.length > 1) return forced

  const [opening, ...rest] = splitOpening(forced[0] ?? '')
  if (!opening) return []

  const body = rest.join(' ')
  if (!body) return wrapText(opening, measure)
  if (measureLine(body) <= measure) return [opening, body]
  const two = splitBody(body, language)
  if (Math.max(...two.map(measureLine)) <= THREE_LINE_MEASURE) return [opening, ...two]
  return [opening, ...splitBodyThree(body, language)]
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
 * @param {number} [options.measure]   Width above which the ministry proper takes two lines.
 */
export const layoutLockup = ({ text, language = 'en', measure = MEASURE }) => {
  const mark = CURRENT_MARK[language] ?? CURRENT_MARK.en
  const lines = nameLines(text, { language, measure })
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
    // A letter whose counter is wound the same way as its outline needs an even-odd fill, or the
    // hole fills in. Two of the French wordmark's letters are drawn that way.
    const rule = shape.rule ? ` fill-rule="${escapeXml(shape.rule)}"` : ''
    parts.push(`<path data-role="${shape.role}"${rule} d="${shape.d}" fill="${escapeXml(fill)}"/>`)
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
