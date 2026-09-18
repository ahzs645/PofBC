// The current era serves finished artwork rather than drawing it, so what needs testing is the one
// thing the app does to it: apply a colourway. The extraction that produced the files is checked
// by scripts/current-marks.test.mjs.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  BCID, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, markSize, recolour, recommendedVariant, renderCurrentSvg
} from './currentMarks.js'

// A miniature of the real artwork's shape: every role, one of each.
const ARTWORK = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 30"><title>x</title>' +
  '<path data-role="sun" fill="#e3a82b" d="M0 0"/>' +
  '<path data-role="knockout" fill="#ffffff" d="M1 1"/>' +
  '<path data-role="mountains" fill="#234075" d="M2 2"/>' +
  '<path data-role="wordmark" fill="#234075" d="M3 3"/>' +
  '<rect data-role="divider" x="1" y="1" width="1" height="1" fill="#e3a82b"/>' +
  '<path data-role="name" fill="#234075" d="M4 4"/></svg>'

const fillsIn = (svg) => [...svg.matchAll(/data-role="(\w+)"[^>]*fill="([^"]+)"/g)]
  .reduce((all, [, role, fill]) => ({ ...all, [role]: fill }), {})

test('every colourway covers every role', () => {
  const roles = ['sun', 'mountains', 'knockout', 'wordmark', 'divider', 'name']

  for (const id of CURRENT_VARIANT_ORDER) {
    for (const role of roles) {
      assert.ok(role in CURRENT_VARIANTS[id].fills, `${id} says nothing about ${role}`)
    }
  }
})

test('the reverse colourway parts the mountains from the wordmark', () => {
  // They are the same blue in the artwork; reverse lightens one and whitens the other. This is the
  // whole reason the extraction labels shapes rather than going by fill.
  const { fills } = CURRENT_VARIANTS.reverse

  assert.equal(fills.mountains, BCID.blueTint)
  assert.equal(fills.wordmark, BCID.white)
  assert.notEqual(fills.mountains, fills.wordmark)
})

test('recolouring rewrites by role and leaves the geometry alone', () => {
  const reversed = recolour(ARTWORK, 'reverse')
  const fills = fillsIn(reversed)

  assert.equal(fills.sun, BCID.gold)
  assert.equal(fills.mountains, BCID.blueTint)
  assert.equal(fills.wordmark, BCID.white)
  assert.equal(fills.name, BCID.white)
  // The path data is untouched — this is official artwork, not something to redraw.
  for (const d of ['M0 0', 'M2 2', 'M4 4']) assert.ok(reversed.includes(d), d)
})

test('the solid colourways drop the knockout so the background shows through', () => {
  // Painting it white instead would ring the mark with a white halo on anything but a white page.
  for (const id of ['black', 'white']) {
    const out = recolour(ARTWORK, id)
    assert.ok(!out.includes('data-role="knockout"'), `${id} kept the knockout`)
    assert.equal(fillsIn(out).sun, id === 'black' ? BCID.black : BCID.white)
  }

  assert.ok(recolour(ARTWORK, 'colour').includes('data-role="knockout"'), 'colour keeps it')
})

test('an unknown colourway falls back rather than producing nothing', () => {
  assert.deepEqual(fillsIn(recolour(ARTWORK, 'chartreuse')), fillsIn(recolour(ARTWORK, 'colour')))
})

test('the artwork reports its own size', () => {
  assert.deepEqual(markSize(ARTWORK), { width: 40, height: 30 })
})

test('clear space and background wrap the artwork without moving it', () => {
  const svg = renderCurrentSvg({ source: ARTWORK, background: '#006837', padding: 5 })

  assert.ok(svg.includes('viewBox="-5 -5 50 40"'), svg.slice(0, 160))
  assert.ok(svg.includes('<rect x="-5" y="-5" width="50" height="40" fill="#006837"/>'))
  // The original wrapper and title are replaced, not nested.
  assert.equal((svg.match(/<svg/g) || []).length, 1)
  assert.ok(!svg.includes('<title>x</title>'))
})

test('a transparent background paints nothing', () => {
  const svg = renderCurrentSvg({ source: ARTWORK, background: 'none', padding: 0 })
  assert.ok(!svg.includes('<rect x="0"'), 'no backdrop rectangle')
})

test('a pixel width sets both dimensions to the artwork’s ratio', () => {
  const svg = renderCurrentSvg({ source: ARTWORK, pixelWidth: 800 })
  assert.ok(svg.includes('width="800" height="600"'), svg.slice(0, 200))
})

test('the guidance’s background pairings are offered', () => {
  // Straight off the colour-accessibility page: reverse on BC Blue and black, solid black on the
  // golds and the tint, colour on nothing in particular.
  assert.equal(recommendedVariant(BCID.blue), 'reverse')
  assert.equal(recommendedVariant(BCID.black), 'reverse')
  assert.equal(recommendedVariant(BCID.gold), 'black')
  assert.equal(recommendedVariant(BCID.blueTint), 'black')
  assert.equal(recommendedVariant('none'), 'colour')
  assert.equal(recommendedVariant('#123456'), null, 'it says nothing about colours it does not list')
})
