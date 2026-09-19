// The current era composes a lockup rather than serving a finished file, so what needs testing is
// the composition: that every colourway reaches every role, that the roles it drops really are
// dropped, and that the wrapper honours background, clear space and size. The typesetting itself is
// covered by currentLayout.test.js.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  BCID, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, markSize, recommendedVariant, renderCurrentSvg
} from './currentMarks.js'

const ROLES = ['sun', 'mountains', 'knockout', 'wordmark', 'divider', 'name']

const TEXT = 'Ministry of\nForests'

const fillsIn = (svg) => [...svg.matchAll(/data-role="(\w+)"[^>]*fill="([^"]+)"/g)]
  .reduce((all, [, role, fill]) => ({ ...all, [role]: fill }), {})

test('every colourway covers every role', () => {
  for (const id of CURRENT_VARIANT_ORDER) {
    for (const role of ROLES) {
      assert.ok(role in CURRENT_VARIANTS[id].fills, `${id} says nothing about ${role}`)
    }
  }
})

test('the reverse colourway parts the mountains from the wordmark', () => {
  // They are the same blue in the artwork; reverse lightens one and whitens the other. This is the
  // whole reason every shape carries a role rather than being identified by its fill.
  const { fills } = CURRENT_VARIANTS.reverse

  assert.equal(fills.mountains, BCID.blueTint)
  assert.equal(fills.wordmark, BCID.white)
  assert.notEqual(fills.mountains, fills.wordmark)
})

test('a colourway reaches every role in the composed lockup', () => {
  const fills = fillsIn(renderCurrentSvg({ text: TEXT, variant: 'reverse' }))

  assert.equal(fills.sun, BCID.gold)
  assert.equal(fills.mountains, BCID.blueTint)
  assert.equal(fills.wordmark, BCID.white)
  assert.equal(fills.divider, BCID.gold)
  assert.equal(fills.name, BCID.white)
})

test('the solid colourways drop the knockout so the background shows through', () => {
  // Painting it white instead would ring the mark with a white halo on anything but a white page.
  for (const id of ['black', 'white']) {
    const svg = renderCurrentSvg({ text: TEXT, variant: id })
    assert.ok(!svg.includes('data-role="knockout"'), `${id} kept the knockout`)
    assert.equal(fillsIn(svg).sun, id === 'black' ? BCID.black : BCID.white)
  }

  assert.ok(renderCurrentSvg({ text: TEXT, variant: 'colour' }).includes('data-role="knockout"'))
})

test('an unknown colourway falls back rather than producing nothing', () => {
  assert.deepEqual(
    fillsIn(renderCurrentSvg({ text: TEXT, variant: 'chartreuse' })),
    fillsIn(renderCurrentSvg({ text: TEXT, variant: 'colour' }))
  )
})

test('the French wordmark is a different drawing, and a wider one', () => {
  const english = markSize({ text: 'Ministry of\nForests', language: 'en' })
  const french = markSize({ text: 'Ministère des\nForêts', language: 'fr' })

  assert.ok(french.width > english.width, `${french.width} should exceed ${english.width}`)
})

test('clear space grows the frame without moving the artwork', () => {
  const plain = renderCurrentSvg({ text: TEXT })
  const padded = renderCurrentSvg({ text: TEXT, clearSpaceFactor: 0.25 })

  const box = (svg) => svg.match(/viewBox="([-\d. ]+)"/)[1].split(' ').map(Number)
  const [, , width] = box(plain)
  const [x, , paddedWidth] = box(padded)

  assert.ok(x < 0, 'the frame opens to the left of the mark')
  assert.ok(Math.abs(paddedWidth - (width + 2 * 0.25 * width)) < 0.01)
  // Only one wrapper, and the mark's own path data is unchanged by the padding.
  assert.equal((padded.match(/<svg/g) || []).length, 1)
  assert.equal(
    (plain.match(/data-role="wordmark" d="([^"]+)"/) || [])[1],
    (padded.match(/data-role="wordmark" d="([^"]+)"/) || [])[1]
  )
})

test('a background paints the whole frame, and transparent paints nothing', () => {
  const filled = renderCurrentSvg({ text: TEXT, background: '#006837', clearSpaceFactor: 0.25 })
  const [x, y, width, height] = filled.match(/viewBox="([-\d. ]+)"/)[1].split(' ').map(Number)

  assert.ok(filled.includes(`<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="#006837"/>`))
  assert.ok(!renderCurrentSvg({ text: TEXT, background: 'none' }).includes('<rect x="0" y="0"'))
})

test('a pixel width sets both dimensions to the lockup’s own ratio', () => {
  const svg = renderCurrentSvg({ text: TEXT, pixelWidth: 800 })
  const { width, height } = markSize({ text: TEXT })
  const expected = Math.round(800 * height / width)

  assert.ok(svg.includes(`width="800" height="${expected}"`), svg.slice(0, 200))
})

test('a colour cannot break out of the attribute it is written into', () => {
  // Backgrounds arrive from share links, which arrive from anyone.
  const svg = renderCurrentSvg({ text: TEXT, background: '"/><script>alert(1)</script>' })

  assert.ok(!svg.includes('<script>'), svg.slice(0, 240))
  assert.ok(svg.includes('&quot;/&gt;&lt;script&gt;'))
})

test('the title is escaped too', () => {
  const svg = renderCurrentSvg({ text: TEXT, title: 'Forests & <Parks>' })
  assert.ok(svg.includes('<title>Forests &amp; &lt;Parks&gt;</title>'))
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
