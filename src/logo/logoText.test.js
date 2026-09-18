// Measurement is checked against the source artwork itself.
//
// Illustrator wrote each word's position into the <tspan x> attributes of the files in artwork/.
// Those numbers are an independent record of where the type actually sits, produced by a different
// program from a different model — so agreeing with them to two decimal places is real evidence
// that this measuring code is right, in a way that asserting against its own output would not be.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { layoutBlock, measureLine, measureWidth, positionWords, wrapText } from './logoText.js'
import { CLEAR_SPACE, CLEAR_SPACE_ORDER, clearSpacePadding } from './layouts.js'
import { getFaceMetrics } from './fontMetrics.js'

// artwork/lockup-stacked.svg: font-size 122.2, word gaps tracked +0.027 em.
const STACKED_BOLD = { fontSize: 122.2, weight: 'bold', wordSpacing: 0.027 }
const STACKED_REGULAR = { fontSize: 122.2, weight: 'regular', wordSpacing: 0.027 }

const closeTo = (actual, expected, tolerance, message) => {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `${message}: expected ${expected} ± ${tolerance}, got ${actual}`
  )
}

test('advance widths match the positions Illustrator wrote into the artwork', () => {
  // <tspan x="516.19"> — where the space after "Province" begins on the first bold line.
  closeTo(measureWidth('Province', STACKED_BOLD), 516.19, 0.01, 'Province')
  // <tspan x="420.9"> on the regular line.
  closeTo(measureWidth('Ministry', STACKED_REGULAR), 420.9, 0.01, 'Ministry')
  // "British Columbia" runs from x=0 to 424.26 + the width of "Columbia".
  closeTo(measureWidth('British Columbia', STACKED_BOLD), 980.96, 0.01, 'British Columbia')
})

test('word spacing is applied once, at the gaps', () => {
  const words = positionWords('Province of British Columbia', STACKED_BOLD)

  assert.deepEqual(words.map((word) => word.text), ['Province', 'of', 'British', 'Columbia'])
  // Straight from artwork/lockup-stacked.svg's second <tspan x>.
  closeTo(words[1].x, 553.44, 0.01, 'start of "of"')

  // Positioning word by word must agree with measuring the line in one go, or a centred lockup
  // would be centred on one number and drawn at another.
  const last = words.at(-1)
  closeTo(
    last.x + measureWidth(last.text, STACKED_BOLD),
    measureWidth('Province of British Columbia', STACKED_BOLD),
    0.001,
    'summed word positions'
  )
})

test('a line with no word spacing is emitted as a single run', () => {
  const words = positionWords('Ministry of Forests', { fontSize: 121, weight: 'regular' })
  assert.equal(words.length, 1)
  assert.equal(words[0].x, 0)
})

test('wrapping reproduces the line breaks in the source artwork', () => {
  // Twice the mark's width, the measure both left-aligned lockups are set to.
  const measure = 2 * 497.02

  assert.deepEqual(
    wrapText('Province of British Columbia', measure, STACKED_BOLD),
    ['Province of', 'British Columbia']
  )
  assert.deepEqual(
    wrapText('Ministry of Forests', measure, STACKED_REGULAR),
    ['Ministry of', 'Forests']
  )
})

test('explicit newlines are honoured over the measure', () => {
  assert.deepEqual(
    wrapText('Ministry of\nForests', 99999, STACKED_REGULAR),
    ['Ministry of', 'Forests']
  )
})

test('a word longer than the measure overflows rather than being broken', () => {
  const lines = wrapText('Supercalifragilistic', 10, STACKED_REGULAR)
  assert.deepEqual(lines, ['Supercalifragilistic'])
})

test('letter spacing falls between characters, not after the last', () => {
  const plain = measureWidth('ABCD', { fontSize: 1000, weight: 'regular' })
  const tracked = measureWidth('ABCD', { fontSize: 1000, weight: 'regular', letterSpacing: 0.1 })
  closeTo(tracked - plain, 300, 0.001, 'three gaps between four characters')
})

test('ink bounds stop at the letterforms on every side', () => {
  const line = measureLine('Ho', STACKED_REGULAR)
  const metrics = getFaceMetrics('regular')
  const scale = STACKED_REGULAR.fontSize / 1000

  // Left: the H's side bearing. Right: the o's ink edge, not the pen position after it. Getting
  // this wrong on one side only is what leaves a lockup looking off-centre in its own box.
  closeTo(line.inkLeft, metrics.bearings.get(72) * scale, 0.001, 'left')
  const advance = metrics.widths.get(72) + metrics.widths.get(111)
  closeTo(line.inkRight, (advance - (metrics.widths.get(111) - metrics.rights.get(111))) * scale, 0.001, 'right')
  assert.ok(line.inkRight < line.advance, 'the o has air after it that is not ink')
})

test('ink bounds exclude blank glyphs and include descenders', () => {
  const withDescender = measureLine('Ministry of', STACKED_REGULAR)
  const without = measureLine('Ministry', STACKED_REGULAR)

  assert.ok(withDescender.inkBottom < 0, 'the y of "Ministry" descends below the baseline')
  assert.equal(without.inkBottom, withDescender.inkBottom, 'both lines contain the same y')

  // A trailing space adds advance but no ink.
  const spaced = measureLine('Ministry ', STACKED_REGULAR)
  closeTo(spaced.inkRight, without.inkRight, 0.001, 'ink right ignores the trailing space')
  assert.ok(spaced.advance > without.advance, 'advance does include it')
})

test('ink left is the first glyph side bearing, which is what the mark aligns to', () => {
  // The artwork sets the mark's left edge 9.74 units right of the text origin, which is exactly
  // the side bearing of a bold "P" at this size.
  const line = measureLine('Province', STACKED_BOLD)
  closeTo(line.inkLeft, 9.73, 0.02, 'bold P side bearing')
})

test('a block reports the union of its lines and a uniform leading', () => {
  const block = layoutBlock([
    { text: 'Province of', style: STACKED_BOLD },
    { text: 'British Columbia', style: STACKED_BOLD },
    { text: 'Ministry of', style: STACKED_REGULAR },
    { text: 'Forests', style: STACKED_REGULAR }
  ], 146.64)

  assert.equal(block.lines.length, 4)
  block.lines.forEach((line, index) => closeTo(line.baseline, index * 146.64, 0.001, `baseline ${index}`))
  // "British Columbia" is the widest line. The figure is its *ink* — from the left side bearing of
  // the B to the right edge of the a — not its advance, which would run on past the a by that
  // glyph's trailing side bearing.
  closeTo(block.inkRight - block.inkLeft, 968.43, 0.01, 'widest line is "British Columbia"')
})

test('empty text produces an empty block rather than a phantom line', () => {
  assert.deepEqual(wrapText('', 500, STACKED_REGULAR), [])
  assert.deepEqual(wrapText(null, 500, STACKED_REGULAR), [])

  const block = layoutBlock([], 146.64)
  assert.equal(block.lines.length, 0)
  assert.equal(block.height, 0)
})

test('clear space presets scale with the mark rather than the page', () => {
  assert.equal(clearSpacePadding('none'), 0)
  // Every preset is a fraction of the mark's width, so a letterhead and a billboard get the same
  // proportions from the same choice.
  for (const key of CLEAR_SPACE_ORDER) {
    assert.equal(clearSpacePadding(key), CLEAR_SPACE[key].factor * 497.02)
  }
  assert.equal(clearSpacePadding('nonsense'), 0, 'an unknown preset is no margin, not NaN')
})
