// The one-off marks: drawn from their published shapes, recoloured by part.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'
import { BCTS_ENTRIES, BCTS_FOREST, BCTS_TEAL, ONE_OFFS } from './oneOffs.js'
import { ONE_OFF_ROLES, hasGlow, renderOneOffSvg, rolesOf } from './renderOneOff.js'
import { renderCurrentSvg } from '../current/currentMarks.js'
import { unsupported } from '../current/currentLayout.js'

const roleFills = (svg) => Object.fromEntries(
  [...svg.matchAll(/data-role="(\w+)"[^>]*fill="([^"]+)"/g)].map(([, role, fill]) => [role, fill]))

// BCTS's earlier wordmark is set without the BC mark.
const WITHOUT_MARK = ['bcts-wordmark-earlier']

test('every mark has a sun, mountains and the wordmark, lifted from its artwork', () => {
  for (const [id, mark] of Object.entries(ONE_OFF_MARKS)) {
    if (WITHOUT_MARK.includes(id)) continue
    const roles = rolesOf(id)
    for (const role of ['sun', 'mountains', 'wordmark']) assert.ok(roles.includes(role), `${id} has no ${role}`)
    for (const { role } of mark.shapes) assert.ok(ONE_OFF_ROLES.includes(role), `${id}: unknown part ${role}`)
    assert.ok(mark.width > 0 && mark.height > 0)
  }
})

test('the marks beside a name have a divider and a name; the stacked mark has neither', () => {
  for (const id of ['welcome-bc', 'work-bc', 'bc-stats', 'environmental-reporting-bc', 'environmental-lab-bc', 'stronger-bc', 'bc-wildfire-service', 'bc-wildfire-service-one-line', 'public-service', 'pacific-gateway']) {
    assert.ok(rolesOf(id).includes('divider'), `${id} has no divider`)
    assert.ok(rolesOf(id).includes('name'), `${id} has no name`)
  }
  assert.ok(!rolesOf('best-place-on-earth').includes('divider'))
  assert.ok(rolesOf('best-place-on-earth').includes('tagline'))
})

test('“BC” is picked out in gold where the published marks pick it out', () => {
  // Print gold (#fdb913), WorkBC's warmer #f6aa0d and the screen gold (#e3a82b) all count.
  for (const id of ['welcome-bc', 'work-bc', 'bc-stats', 'environmental-reporting-bc', 'environmental-lab-bc', 'stronger-bc', 'bc-wildfire-service', 'bc-wildfire-service-one-line']) {
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
  const entries = [...ONE_OFFS, ...BCTS_ENTRIES.earlier, ...BCTS_ENTRIES.current]
  for (const entry of entries.filter((e) => e.kind === 'artwork')) {
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

test('BC Wildfire Service keeps its reversed colours, and turns to BC blue on white', () => {
  // Both arrangements were lifted from reversed artwork: white type, and mountains lightened so
  // they read against the dark. On white they take the blue the Province's own positive file uses.
  for (const id of ['bc-wildfire-service', 'bc-wildfire-service-one-line']) {
    assert.equal(hasGlow(id), false)
    const published = roleFills(renderOneOffSvg({ id }).svg)
    assert.equal(published.name, '#ffffff', id)
    assert.equal(published.accent, '#fdb913', id)
    assert.equal(published.mountains, '#4c5d91', id)

    const onWhite = ONE_OFFS.find((e) => e.id === id).presets.find((p) => p.id === 'colour')
    assert.ok(onWhite, `${id}, published reversed, offers a version on white`)
    assert.equal(onWhite.colours.name, '#004b8d')
  }
  // Two lines are about half as wide for their height as one.
  const ratio = (id) => ONE_OFF_MARKS[id].width / ONE_OFF_MARKS[id].height
  assert.ok(ratio('bc-wildfire-service') < 0.8 * ratio('bc-wildfire-service-one-line'))
})

test('BCTS sets its name in green over a descriptor in a colour of its own', () => {
  for (const id of ['bcts', 'bcts-wordmark-earlier']) {
    assert.deepEqual(rolesOf(id).filter((role) => ['name', 'descriptor', 'accent'].includes(role)), ['name', 'descriptor'], id)
    const fills = roleFills(renderOneOffSvg({ id }).svg)
    assert.equal(fills.descriptor, '#231f20', `${id}: “BC Timber Sales” is near-black`)
  }
  assert.equal(roleFills(renderOneOffSvg({ id: 'bcts' }).svg).name, BCTS_FOREST)
  assert.equal(roleFills(renderOneOffSvg({ id: 'bcts-wordmark-earlier' }).svg).name, '#008450')
  // A Province mark with one colour beside the mark keeps it all as the name.
  assert.ok(!rolesOf('stronger-bc').includes('descriptor'))
})

test('the earlier BCTS wordmark has no mark, so no sun or light to colour', () => {
  const mark = ONE_OFF_MARKS['bcts-wordmark-earlier']
  assert.equal(mark.sun, null)
  assert.equal(hasGlow('bcts-wordmark-earlier'), false)
  assert.ok(!('sun' in mark.printed) && !('light' in mark.printed))
  assert.doesNotMatch(renderOneOffSvg({ id: 'bcts-wordmark-earlier' }).svg, /data-role="(sun|core|divider)"/)
})

test('BCTS reversed is the same mark with white type and the initials in teal', () => {
  // Its picture has white type on a transparent ground, so on a white page it looks like the
  // symbol and “BCTS” alone. It is a colourway of the one mark, not a mark of its own.
  const entry = BCTS_ENTRIES.current.find((e) => e.id === 'bcts')
  const reversed = entry.presets.find((p) => p.id === 'teal-reversed')
  const fills = roleFills(renderOneOffSvg({ id: 'bcts', colours: reversed.colours }).svg)
  assert.equal(fills.wordmark, '#ffffff')
  assert.equal(fills.descriptor, '#ffffff')
  assert.equal(fills.name, BCTS_TEAL)
  assert.equal(fills.mountains, '#4d5d92')
  assert.notEqual(reversed.colours.background, '#ffffff')
})

test('every BCTS mark starts from either green', () => {
  for (const entry of [...BCTS_ENTRIES.earlier, ...BCTS_ENTRIES.current]) {
    const greens = entry.presets.map((preset) => preset.colours.name)
    assert.ok(greens.includes(BCTS_FOREST), `${entry.id} offers forest green`)
    assert.ok(greens.includes(BCTS_TEAL), `${entry.id} offers teal`)
  }
})

test('PreparedBC is remade in the current identity, every letter from the ministry alphabet', () => {
  const entry = ONE_OFFS.find((e) => e.id === 'prepared-bc')
  assert.equal(entry.kind, 'current')
  assert.ok(!(entry.id in ONE_OFF_MARKS), 'nothing of it is lifted from artwork')
  assert.deepEqual(unsupported(entry.text), [])
  const svg = renderCurrentSvg({ text: entry.text })
  assert.match(svg, /^<svg /)
})
