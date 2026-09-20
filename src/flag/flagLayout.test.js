// The BC Flag Symbol lockups.
//
// Five arrangements, all of them printed: the two the standards page sanctions — BC beside the
// flag, and the flag above BC — plus the flag standing alone, each with the wording under the
// symbol or beside it. The numbers pinned here are measured off the documents; a change that moves
// them is a change that stops matching what was printed.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { FLAG, FLAG_PALETTE } from '../assets/flagMark.js'
import {
  ARRANGEMENTS, FLAG_ASPECT, FLAG_SYMBOLS, LETTERS, NAME_CAP, NAME_MEASURE, NAME_PLACEMENTS,
  PROVINCE_LINE, flagLockupMarkup, layoutFlagLockup
} from './flagLayout.js'
import { FLAG_PALETTES, paletteFill, recommendedPalette } from './flagPalettes.js'
import { flagSize, renderFlagSvg } from './renderFlagSvg.js'

const INKS = { letterColor: '#111111', textColor: '#111111' }

test('the flag artwork is the Province’s, on its own ink box', () => {
  assert.equal(FLAG.shapes.length, 12)
  assert.deepEqual(FLAG_PALETTE, ['#013366', '#ad0000', '#fcba19'])
  assert.ok(Math.abs(FLAG_ASPECT - 1.301) < 0.002, `aspect is ${FLAG_ASPECT}`)
  for (const shape of FLAG.shapes) assert.ok(shape.d.startsWith('M'), 'absolute paths only')
})

test('every arrangement lays out, in both placements', () => {
  for (const symbol of FLAG_SYMBOLS) {
    for (const placement of NAME_PLACEMENTS) {
      const { box, lines } = layoutFlagLockup({
        symbol, placement, province: true, ministry: 'Ministry of Environment', cap: 100
      })
      assert.ok(box.width > 0 && box.height > 0, `${symbol}/${placement}`)
      assert.ok(lines.length >= 2, `${symbol}/${placement} should set both blocks`)
    }
  }
})

test('the horizontal lockup reproduces the reference’s proportions', () => {
  // 333 x 164 in the clearest document, at a 100px BC cap.
  const { box } = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })
  assert.ok(Math.abs(box.width - 333) < 4, `width ${box.width.toFixed(1)}`)
  assert.ok(Math.abs(box.height - 164) < 6, `height ${box.height.toFixed(1)}`)
})

test('horizontal hangs the flag from the baseline; vertical stands it on the cap line', () => {
  const across = layoutFlagLockup({ symbol: 'horizontal', ministry: 'x', cap: 100 })
  const down = layoutFlagLockup({ symbol: 'vertical', ministry: 'x', cap: 100 })

  // Across: the flag's foot is the letters' foot, and it sits to their right.
  assert.ok(Math.abs(across.flag.y + across.flag.height) < 0.01)
  assert.ok(across.flag.x > across.letters.ink.inkRight - across.letters.ink.inkLeft)

  // Down: the flag is above the cap line and flush with the letters' left edge.
  assert.ok(down.flag.y + down.flag.height <= -100 + 0.01 * 100 + 0.01)
  assert.equal(down.flag.x, 0)
  assert.ok(down.box.height > across.box.height, 'stacking makes it taller')
})

test('the flag-only arrangement draws no letters', () => {
  const alone = layoutFlagLockup({ symbol: 'flag', ministry: 'Ministry of Forests', cap: 100 })
  assert.equal(alone.letters, null)

  const { markup } = { markup: flagLockupMarkup({ layout: alone, ...INKS }) }
  assert.ok(!markup.includes('data-role="letters"'))
  assert.ok(markup.includes('data-role="flag"'))
  assert.ok(markup.includes('data-role="name"'))
})

test('beside puts the wording to the right; below puts it underneath', () => {
  const beside = layoutFlagLockup({ placement: 'beside', ministry: 'Ministry of Environment', cap: 100 })
  const below = layoutFlagLockup({ placement: 'below', ministry: 'Ministry of Environment', cap: 100 })

  const symbolRight = beside.flag.x + beside.flag.width
  assert.ok(beside.lines[0].x > symbolRight, 'beside clears the symbol')
  assert.ok(beside.box.width > below.box.width, 'beside is wider')
  // Beside, the wording's last line sits on the letters' baseline rather than being centred —
  // measured off a vector extraction whose two lines end within four tenths of a point of it.
  assert.ok(Math.abs(beside.lines.at(-1).y) < 0.01, 'last line on the baseline')
  // Below starts at the symbol's left edge and sits under the baseline.
  assert.ok(Math.abs(below.lines[0].x + below.lines[0].ink.inkLeft) < 0.01)
  assert.ok(below.lines[0].y > 0)
})

test('the wording can be set bold, as several of the documents do', () => {
  const plain = layoutFlagLockup({ ministry: 'Ministry of Environment', cap: 100 })
  const heavy = layoutFlagLockup({ ministry: 'Ministry of Environment', bold: true, cap: 100 })

  assert.equal(plain.lines[0].style.weight, undefined)
  assert.equal(heavy.lines[0].style.weight, 'bold')
  assert.ok(heavy.lines[0].ink.inkRight > plain.lines[0].ink.inkRight, 'bold is wider')
})

test('the province line is set in bold above the ministry', () => {
  const plain = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })
  const withProvince = layoutFlagLockup({ province: true, ministry: 'Ministry of Forests', cap: 100 })

  assert.ok(withProvince.lines.length > plain.lines.length)
  assert.equal(withProvince.lines[0].style.weight, 'bold')
  assert.equal(withProvince.lines.at(-1).style.weight, undefined, 'the ministry is not bold')
  assert.ok(PROVINCE_LINE.startsWith('Province of'))
  assert.ok(withProvince.lines[0].y < withProvince.lines.at(-1).y, 'the province line comes first')
})

test('a third line follows the ministry', () => {
  const lines = layoutFlagLockup({
    ministry: 'Ministry of Lands, Parks and Housing',
    extra: 'Honourable Anthony J. Brummet, Minister',
    cap: 100
  }).lines
  assert.ok(lines.some((line) => line.text.includes('Brummet')))
  assert.ok(lines.at(-1).text.includes('Minister'))
})

test('the wording wraps to its own measure, not the symbol’s', () => {
  // The first version wrapped to the symbol width, which put one word per line under the flag-only
  // lockup: the flag alone is barely two cap heights wide.
  const alone = layoutFlagLockup({
    symbol: 'flag', ministry: 'Ministry of Energy, Mines and Petroleum Resources', cap: 100
  })
  const longest = Math.max(...alone.lines.map((line) => line.ink.inkRight))
  assert.ok(longest > alone.flag.width, 'the wording is allowed past the flag')
  assert.ok(alone.lines.every((line) => line.text.trim().includes(' ') || line.text.length > 6),
    'no line is left holding a single short word')

  // Wide enough for the line nearly every document keeps whole. An earlier value of 3.4 broke it
  // in two, and was arrived at by dividing a flag's width by its height ratio — a slip.
  const province = layoutFlagLockup({ province: true, ministry: 'x', cap: 100 })
  assert.equal(province.lines[0].text, PROVINCE_LINE, 'the province line stays on one line')
  assert.ok(NAME_MEASURE > 5 && NAME_MEASURE < 6)
})

test('the lockup scales as one drawing', () => {
  const small = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 10 })
  const big = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 1000 })
  assert.ok(Math.abs(big.box.width / small.box.width - 100) < 1e-6)
  assert.ok(Math.abs(big.box.height / small.box.height - 100) < 1e-6)
})

test('the palettes are the standards page’s, the artwork’s, and one ink', () => {
  // "Official B.C. Flag Symbol Colours: Pantone Blue 072C, Red 032C, Yellow 109C."
  assert.deepEqual(Object.values(FLAG_PALETTES.official.fills), ['#10069f', '#ef3340', '#ffd100'])
  assert.deepEqual(Object.values(FLAG_PALETTES.modern.fills), FLAG_PALETTE)
  assert.equal(FLAG_PALETTES.ink.fills, null)

  assert.equal(paletteFill('official', '#013366'), '#10069f')
  assert.equal(paletteFill('modern', '#013366'), '#013366')
  assert.equal(paletteFill('ink', '#013366', '#ffffff'), '#ffffff', 'one ink overrides every shape')
})

test('a dark background calls for one ink, because the flag’s white is the page', () => {
  // Full colour on anything but white shows the background through every gap in the flag — which
  // is what the documents avoid by setting the whole thing in one ink.
  assert.equal(recommendedPalette('#006837'), 'ink')
  assert.equal(recommendedPalette('#000000'), 'ink')
  assert.equal(recommendedPalette('#ffffff'), null, 'white needs no help')
  assert.equal(recommendedPalette('none'), null, 'nor does transparent')
})

test('one ink paints the flag with the letters; the others leave it alone', () => {
  const layout = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })
  const official = flagLockupMarkup({ layout, ...INKS, flagPalette: 'official' })
  const ink = flagLockupMarkup({ layout, ...INKS, flagPalette: 'ink' })

  for (const shade of ['#10069f', '#ef3340', '#ffd100']) assert.ok(official.includes(shade))
  for (const shade of FLAG_PALETTE) assert.ok(!ink.includes(shade), `one ink drops ${shade}`)
  assert.equal((ink.match(/data-role="flag"/g) || []).length, FLAG.shapes.length)
})

test('an empty name still draws the symbol', () => {
  const { lines, box } = layoutFlagLockup({ ministry: '', cap: 100 })
  assert.deepEqual(lines, [])
  assert.ok(box.width > 0 && box.height > 0)
})

test('the rendered SVG frames the lockup, and clear space grows the frame', () => {
  const plain = renderFlagSvg({ ministry: 'Ministry of Forests' })
  const padded = renderFlagSvg({ ministry: 'Ministry of Forests', clearSpaceFactor: 0.25 })

  assert.ok(plain.svg.startsWith('<svg'))
  assert.equal(flagSize({ ministry: 'Ministry of Forests' }).width, plain.box.width)
  assert.ok(Math.abs(padded.box.width - plain.box.width * 1.5) < 0.01)
  assert.equal((padded.svg.match(/<svg/g) || []).length, 1)
})

test('a background paints the whole frame, and transparent paints nothing', () => {
  const filled = renderFlagSvg({ ministry: 'x', background: '#006837', clearSpaceFactor: 0.2 })
  assert.ok(filled.svg.includes('fill="#006837"'))
  assert.ok(!renderFlagSvg({ ministry: 'x', background: 'none' }).svg.includes('<rect'))
})

test('colours cannot break out of the attributes they are written into', () => {
  const svg = renderFlagSvg({
    ministry: 'Ministry of <script>',
    letterColor: '"/><script>alert(1)</script>',
    background: '"/><script>'
  }).svg

  assert.ok(!svg.includes('<script>'), svg.slice(0, 300))
  assert.ok(svg.includes('&lt;script&gt;'))
})

test('the constants are the ones measured, not tidied afterwards', () => {
  assert.equal(LETTERS, 'BC')
  assert.equal(ARRANGEMENTS.horizontal.flagHeight, 1.12)
  assert.equal(ARRANGEMENTS.vertical.flagHeight, 1.28)
  assert.ok(NAME_CAP > 0.25 && NAME_CAP < 0.32, 'inside the range the documents show')
})
