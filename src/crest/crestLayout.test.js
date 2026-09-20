// The coat-of-arms identity.
//
// Its proportions come from two independent sources that happen to agree: a vector page for the
// side-by-side arrangement, and a raster for the stacked one. The agreement is what these pin —
// the two drawings' aspects come out the same measured either way, which is the evidence that the
// readings are of the same artwork and not of something rescaled along the way.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ARMS, WORDMARK } from '../assets/crestMark.js'
import {
  ARMS_ASPECT, CREST_ARRANGEMENTS, CREST_LAYOUTS, CREST_PLACEMENTS, MINISTRY_MEASURE,
  MINISTRY_SIZES, MINISTRY_SIZE_ORDER, WORDMARK_ASPECT, crestLockupMarkup, layoutCrestLockup
} from './crestLayout.js'
import { crestSize, renderCrestSvg } from './renderCrestSvg.js'

const INK = { markColor: '#111111', textColor: '#111111' }

test('the artwork is vector, on its own ink box, with its counters intact', () => {
  // Both were lifted from a page extraction. The wordmark is outlines rather than text, so it
  // needs no font; the arms are the full achievement.
  assert.ok(ARMS.shapes.length >= 1)
  assert.ok(WORDMARK.shapes.length >= 1)
  assert.ok(ARMS.width > 0 && ARMS.height > 0)

  // A letter's counter is a contour wound against its outline. Emitting each contour as its own
  // path fills the holes in, so they have to stay together — which shows up as few paths holding
  // many subpaths.
  const subpaths = WORDMARK.shapes.reduce((n, shape) => n + (shape.d.match(/M/g) || []).length, 0)
  assert.ok(subpaths > WORDMARK.shapes.length * 5, `${subpaths} subpaths in ${WORDMARK.shapes.length} path(s)`)
})

test('the two sources agree on the drawings’ proportions', () => {
  // The vector page gives 0.831 and 2.523; a raster of the stacked arrangement, measured
  // independently, gives 0.82 and 2.48.
  assert.ok(Math.abs(ARMS_ASPECT - 0.831) < 0.02, `arms aspect ${ARMS_ASPECT.toFixed(3)}`)
  assert.ok(Math.abs(WORDMARK_ASPECT - 2.523) < 0.06, `wordmark aspect ${WORDMARK_ASPECT.toFixed(3)}`)
})

test('every arrangement lays out, in both placements', () => {
  for (const arrangement of CREST_ARRANGEMENTS) {
    for (const placement of CREST_PLACEMENTS) {
      const { box, lines } = layoutCrestLockup({
        arrangement, placement, ministry: 'Ministry of Forests', size: 100
      })
      assert.ok(box.width > 0 && box.height > 0, `${arrangement}/${placement}`)
      assert.ok(lines.length >= 1, `${arrangement}/${placement} sets the ministry`)
    }
  }
})

test('side by side puts the wordmark beside the arms, feet aligned', () => {
  const { arms, wordmark } = layoutCrestLockup({ arrangement: 'horizontal', size: 100 })

  assert.ok(wordmark.x > arms.x + arms.width, 'the wordmark clears the arms')
  // Their feet line up: the wordmark is nearly as tall as the arms and hangs from the same line.
  assert.ok(Math.abs((wordmark.y + wordmark.height) - (arms.y + arms.height)) < 0.01)
  assert.ok(Math.abs(wordmark.height / arms.height - CREST_LAYOUTS.horizontal.wordmarkHeight) < 1e-9)
})

test('both stacked forms centre on one axis, and differ only in how large the arms are drawn', () => {
  // Two proportions are printed. Three documents draw the two at much the same height (0.878,
  // 0.899, 0.891); a fourth draws the arms twice as large (0.433). Each was checked by aspect
  // first, so both are readings of the same two drawings.
  for (const arrangement of ['vertical', 'vertical-arms']) {
    const { arms, wordmark } = layoutCrestLockup({ arrangement, size: 100 })
    const armsCentre = arms.x + arms.width / 2
    const wordmarkCentre = wordmark.x + wordmark.width / 2
    assert.ok(Math.abs(armsCentre - wordmarkCentre) < 0.01, `${arrangement} centres on one axis`)
    assert.ok(wordmark.y > arms.y + arms.height, `${arrangement} puts the wordmark below`)
  }

  const common = layoutCrestLockup({ arrangement: 'vertical', size: 100 })
  const large = layoutCrestLockup({ arrangement: 'vertical-arms', size: 100 })
  assert.ok(Math.abs(common.arms.height / common.wordmark.height - 1.125) < 0.02)
  assert.ok(large.arms.height / large.wordmark.height > 2)
})

test('below the mark the ministry is set off the wordmark, not the arms', () => {
  // Against the arms the documents spread 0.125 to 0.397 and no constant fits. Against the
  // wordmark — the one drawing whose size holds across the arrangements — the stacked ones land
  // together, which is how the two stacked forms can share a gap.
  const common = layoutCrestLockup({ arrangement: 'vertical', placement: 'below', ministry: 'M', size: 100 })
  const large = layoutCrestLockup({ arrangement: 'vertical-arms', placement: 'below', ministry: 'M', size: 100 })

  // 'M' rises exactly a cap height, so its ink top is the gap's far edge.
  const drop = (l) => (l.lines[0].y - l.lines[0].ink.inkTop) - (l.wordmark.y + l.wordmark.height)
  assert.ok(Math.abs(drop(common) / common.wordmark.height - 0.44) < 0.01)
  assert.ok(Math.abs(drop(large) / large.wordmark.height - 0.44) < 0.01)
})

test('the ministry sits beside the mark or below it', () => {
  const beside = layoutCrestLockup({ placement: 'beside', ministry: 'Ministry of Forests', size: 100 })
  const below = layoutCrestLockup({ placement: 'below', ministry: 'Ministry of Forests', size: 100 })

  const markRight = Math.max(beside.arms.x + beside.arms.width, beside.wordmark.x + beside.wordmark.width)
  assert.ok(beside.lines[0].x > markRight, 'beside clears the mark')
  assert.ok(beside.box.width > below.box.width, 'beside is wider')
  assert.ok(below.box.height > beside.box.height, 'below is taller')
})

test('a second line follows the ministry', () => {
  const { lines } = layoutCrestLockup({
    ministry: 'Ministry of Forests', extra: 'Research Branch', size: 100
  })
  assert.ok(lines.some((line) => line.text === 'Research Branch'))
  assert.equal(lines.at(-1).text, 'Research Branch')
})

test('the ministry can be set bold, as many of the documents do', () => {
  const plain = layoutCrestLockup({ ministry: 'Ministry of Forests', size: 100 })
  const heavy = layoutCrestLockup({ ministry: 'Ministry of Forests', bold: true, size: 100 })

  assert.equal(plain.lines[0].style.weight, undefined)
  assert.equal(heavy.lines[0].style.weight, 'bold')
})

test('the ministry is sized against the wordmark, at one of the heights printed', () => {
  // Three settings, converted from band heights to cap heights: 0.212 in three documents, 0.263
  // in one, 0.294 in another. Against the wordmark, not the arms — it is the one drawing whose
  // size holds across the arrangements, so a share of it means the same in all three.
  assert.deepEqual(MINISTRY_SIZE_ORDER.map((key) => MINISTRY_SIZES[key]),
    [0.138, 0.212, 0.263, 0.294])

  const { lines, wordmark } = layoutCrestLockup({
    arrangement: 'vertical', ministry: 'M', ministrySize: 'medium', size: 100
  })
  assert.ok(Math.abs(lines[0].ink.inkTop / wordmark.height - 0.263) < 0.002)
})

test('every size holds its proportion whichever way the lockup is arranged', () => {
  // The point of measuring against the wordmark: the arms change size between the arrangements
  // and the wordmark does not, so one key means one size throughout.
  for (const arrangement of CREST_ARRANGEMENTS) {
    const { lines, wordmark } = layoutCrestLockup({ arrangement, ministry: 'M', size: 100 })
    assert.ok(Math.abs(lines[0].ink.inkTop / wordmark.height - MINISTRY_SIZES.small) < 0.002,
      arrangement)
  }
})

test('a trailing line can drop a step below the ministry, as two documents set it', () => {
  // 12.33.36 goes 0.263 to 0.212 and 12.32.35 goes 0.212 to 0.138 — one step each time.
  const same = layoutCrestLockup({ ministry: 'Ministry of Forests', extra: 'Research Branch', size: 100 })
  const dropped = layoutCrestLockup({
    ministry: 'Ministry of Forests', extra: 'Research Branch',
    ministrySize: 'medium', extraStep: 'smaller', size: 100
  })

  assert.equal(same.lines[0].style.fontSize, same.lines.at(-1).style.fontSize)
  const ratio = dropped.lines.at(-1).style.fontSize / dropped.lines[0].style.fontSize
  assert.ok(Math.abs(ratio - 0.212 / 0.263) < 0.005, `ratio ${ratio.toFixed(3)}`)

  // The smallest size has nothing below it to drop to.
  const floor = layoutCrestLockup({
    ministry: 'a', extra: 'b', ministrySize: 'xsmall', extraStep: 'smaller', size: 100
  })
  assert.equal(floor.lines[0].style.fontSize, floor.lines.at(-1).style.fontSize)
})

test('the lockup scales as one drawing', () => {
  const small = layoutCrestLockup({ ministry: 'Ministry of Forests', size: 10 })
  const big = layoutCrestLockup({ ministry: 'Ministry of Forests', size: 1000 })

  assert.ok(Math.abs(big.box.width / small.box.width - 100) < 1e-6)
  assert.ok(Math.abs(big.box.height / small.box.height - 100) < 1e-6)
})

test('markup carries a role on every part', () => {
  const layout = layoutCrestLockup({ ministry: 'Ministry of Forests', size: 100 })
  const markup = crestLockupMarkup({ layout, ...INK })
  const roles = new Set([...markup.matchAll(/data-role="(\w+)"/g)].map((m) => m[1]))

  assert.deepEqual([...roles].sort(), ['arms', 'name', 'wordmark'])
})

test('the rendered SVG frames the lockup, and clear space grows the frame', () => {
  const plain = renderCrestSvg({ ministry: 'Ministry of Forests' })
  const padded = renderCrestSvg({ ministry: 'Ministry of Forests', clearSpaceFactor: 0.25 })

  assert.ok(plain.svg.startsWith('<svg'))
  assert.equal(crestSize({ ministry: 'Ministry of Forests' }).width, plain.box.width)
  assert.ok(Math.abs(padded.box.width - plain.box.width * 1.5) < 0.01)
  assert.equal((padded.svg.match(/<svg/g) || []).length, 1)
})

test('colours cannot break out of the attributes they are written into', () => {
  const svg = renderCrestSvg({
    ministry: 'Ministry of <script>',
    markColor: '"/><script>alert(1)</script>',
    background: '"/><script>'
  }).svg

  assert.ok(!svg.includes('<script>'), svg.slice(0, 300))
  assert.ok(svg.includes('&lt;script&gt;'))
})

test('an empty ministry still draws the mark', () => {
  const { lines, box } = layoutCrestLockup({ ministry: '', size: 100 })
  assert.deepEqual(lines, [])
  assert.ok(box.width > 0 && box.height > 0)
})

test('a ministry broken by hand is set as typed, not re-wrapped', () => {
  // The documents break their ministries by hand and disagree about where, so the field has to
  // win over the measure. The same rule the current era follows.
  const { lines } = layoutCrestLockup({
    ministry: 'Ministry of Environment,\nLands and Parks', size: 100
  })
  assert.deepEqual(lines.map((line) => line.text), ['Ministry of Environment,', 'Lands and Parks'])
})

test('the measure is the widest line these documents print, not a narrower guess', () => {
  // "Ministry of Employment and Investment" is printed whole, 25.1 cap heights in its document
  // and 26.2 as this project sets it. Earlier values broke it in two — first because 3.6 arms
  // heights was too narrow, then because a measure in arms heights stopped tracking the type.
  assert.ok(MINISTRY_MEASURE > 26.2, `measure ${MINISTRY_MEASURE}`)

  const { lines } = layoutCrestLockup({
    ministry: 'Ministry of Employment and Investment', extra: 'Energy and Minerals Division',
    bold: true, size: 100
  })
  assert.deepEqual(lines.map((line) => line.text),
    ['Ministry of Employment and Investment', 'Energy and Minerals Division'])
})

test('the measure follows the type, so no size can make it cut a printed line', () => {
  // It was in arms heights once. Making the ministry's size a choice broke that immediately: the
  // largest setting overran a backstop that could not grow with it.
  for (const ministrySize of MINISTRY_SIZE_ORDER) {
    const { lines } = layoutCrestLockup({
      ministry: 'Ministry of Employment and Investment', bold: true, ministrySize, size: 100
    })
    assert.equal(lines.length, 1, `${ministrySize} keeps the longest printed line whole`)
  }
})
