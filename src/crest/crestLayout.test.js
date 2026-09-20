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
  ARMS_ASPECT, CREST_ARRANGEMENTS, CREST_LAYOUTS, CREST_PLACEMENTS, MINISTRY_CAP, WORDMARK_ASPECT,
  crestLockupMarkup, layoutCrestLockup
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

test('stacked centres both on one axis, and draws the arms much larger', () => {
  const { arms, wordmark } = layoutCrestLockup({ arrangement: 'vertical', size: 100 })

  const armsCentre = arms.x + arms.width / 2
  const wordmarkCentre = wordmark.x + wordmark.width / 2
  assert.ok(Math.abs(armsCentre - wordmarkCentre) < 0.01, 'centred on a common axis')
  assert.ok(wordmark.y > arms.y + arms.height, 'the wordmark sits below')
  // 2.3 times its height stacked, against a little over one side by side.
  assert.ok(arms.height / wordmark.height > 2, `ratio ${(arms.height / wordmark.height).toFixed(2)}`)
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

test('the ministry is set at the height both sources measured', () => {
  // 0.163 of the arms on the vector page, 0.164 on the raster.
  assert.ok(MINISTRY_CAP > 0.16 && MINISTRY_CAP < 0.167)
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
