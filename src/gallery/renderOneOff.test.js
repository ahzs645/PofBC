// The one-off marks: drawn from their published shapes, recoloured by part.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'
import { ONE_OFFS } from './oneOffs.js'
import { ONE_OFF_ROLES, hasGlow, renderOneOffSvg, rolesOf } from './renderOneOff.js'

const roleFills = (svg) => Object.fromEntries(
  [...svg.matchAll(/data-role="(\w+)"[^>]*fill="([^"]+)"/g)].map(([, role, fill]) => [role, fill]))

test('every mark has a sun, mountains and the wordmark, lifted from its artwork', () => {
  for (const [id, mark] of Object.entries(ONE_OFF_MARKS)) {
    const roles = rolesOf(id)
    for (const role of ['sun', 'mountains', 'wordmark']) assert.ok(roles.includes(role), `${id} has no ${role}`)
    for (const { role } of mark.shapes) assert.ok(ONE_OFF_ROLES.includes(role), `${id}: unknown part ${role}`)
    assert.ok(mark.width > 0 && mark.height > 0)
  }
})

test('the marks beside a name have a divider and a name; the stacked mark has neither', () => {
  for (const id of ['welcome-bc', 'work-bc', 'bc-stats', 'environmental-reporting-bc', 'stronger-bc', 'public-service', 'pacific-gateway']) {
    assert.ok(rolesOf(id).includes('divider'), `${id} has no divider`)
    assert.ok(rolesOf(id).includes('name'), `${id} has no name`)
  }
  assert.ok(!rolesOf('best-place-on-earth').includes('divider'))
  assert.ok(rolesOf('best-place-on-earth').includes('tagline'))
})

test('“BC” is picked out in gold where the published marks pick it out', () => {
  // Print gold (#fdb913), WorkBC's warmer #f6aa0d and the screen gold (#e3a82b) all count.
  for (const id of ['welcome-bc', 'work-bc', 'bc-stats', 'environmental-reporting-bc', 'stronger-bc']) {
    assert.ok(rolesOf(id).includes('accent'), `${id} has no accent`)
    const { svg } = renderOneOffSvg({ id, idPrefix: 't' })
    const [r, g, b] = [1, 3, 5].map((i) => parseInt(roleFills(svg).accent.slice(i, i + 2), 16))
    assert.ok(r > 200 && g > 140 && g < 200 && b < 60, `${id}'s accent is not gold`)
  }
})

test('the published sun glows with gradients, and one ink draws it flat', () => {
  const glow = renderOneOffSvg({ id: 'welcome-bc', idPrefix: 'g' }).svg
  assert.match(glow, /<radialGradient id="g-sun"/)
  assert.match(glow, /<radialGradient id="g-rays"/)
  assert.equal(roleFills(glow).rays, 'url(#g-rays)')

  const flat = renderOneOffSvg({ id: 'welcome-bc', sun: 'flat', colours: { sun: '#000000', light: '#ffffff' } }).svg
  assert.doesNotMatch(flat, /radialGradient/)
  assert.equal(roleFills(flat).sun, '#000000')
  assert.equal(roleFills(flat).rays, '#ffffff', 'the rays are cut out of the sun in the light colour')
})

test('a glow runs from the light at the core to the sun’s colour at the rim', () => {
  const stops = ONE_OFF_MARKS['best-place-on-earth'].gradients.sun
  assert.ok(stops[0][1] < 0.2, 'the core is nearly the light colour')
  assert.ok(stops.at(-1)[1] > 0.8, 'the rim is nearly the sun’s colour')
  const svg = renderOneOffSvg({ id: 'best-place-on-earth', colours: { sun: '#ff0000', light: '#0000ff' }, idPrefix: 'x' }).svg
  assert.match(svg, /stop-color="#[0-9a-f]{6}"/)
  assert.doesNotMatch(svg, /stop-color="#fdb/, 'the gradient follows the chosen colours, not the printed gold')
})

test('a sun with no light colour to fade to is drawn flat, not guessed at', () => {
  const svg = renderOneOffSvg({ id: 'welcome-bc', colours: { light: 'none' } }).svg
  assert.doesNotMatch(svg, /radialGradient/)
  assert.ok(!('rays' in roleFills(svg)), 'a transparent light leaves the rays out')
})

test('gradient ids do not collide between marks on one page', () => {
  const a = renderOneOffSvg({ id: 'welcome-bc' }).svg.match(/radialGradient id="([^"]+)"/)[1]
  const b = renderOneOffSvg({ id: 'welcome-bc' }).svg.match(/radialGradient id="([^"]+)"/)[1]
  assert.notEqual(a, b)
})

test('every gallery preset colours every part its mark has', () => {
  for (const entry of ONE_OFFS.filter((e) => e.kind === 'artwork')) {
    for (const preset of entry.presets) {
      const fills = roleFills(renderOneOffSvg({ id: entry.mark, colours: preset.colours, sun: preset.sun, idPrefix: 'p' }).svg)
      for (const role of rolesOf(entry.mark)) {
        assert.ok(fills[role], `${entry.id} / ${preset.id}: ${role} is not drawn`)
      }
    }
  }
})

test('the clear space is a margin around the mark, not a scale', () => {
  const { box } = renderOneOffSvg({ id: 'work-bc', clearSpaceFactor: 0.1 })
  const mark = ONE_OFF_MARKS['work-bc']
  assert.ok(Math.abs(box.width - mark.width * 1.2) < 1e-6)
  assert.ok(Math.abs(box.x + mark.width * 0.1) < 1e-6)
})

test('a mark published with a flat sun draws it flat, and offers no glow', () => {
  assert.equal(hasGlow('stronger-bc'), false)
  assert.equal(hasGlow('welcome-bc'), true)
  // Asked for the glow anyway, it still draws the disc in the light and the rays in the sun's gold.
  const fills = roleFills(renderOneOffSvg({ id: 'stronger-bc', sun: 'glow' }).svg)
  assert.equal(fills.core, '#ffffff')
  assert.equal(fills.sun, '#fdb913')
  assert.equal(fills.divider, '#a7a9ac', 'StrongerBC’s divider is grey')
})
