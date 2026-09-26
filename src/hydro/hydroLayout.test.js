// The historical BC Hydro signatures: the manual's rules, and the layouts they produce.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  allHydroDefaults, cleanHydroSettings, effectiveMode, hydroDefaults, hydroPalette, hydroScene, HYDRO_PRESETS,
  pairedPreset, readHydroProject, recommendedMode, updateHydroSettings, validateHydro
} from './hydroLayout.js'
import { renderHydroSheet, renderHydroSvg } from './renderHydroSvg.js'
import { capHeightAt, missingLetters, setRun } from './hydroType.js'

const close = (actual, expected, message) => assert.ok(Math.abs(actual - expected) < 1e-6, `${message}: ${actual} ≠ ${expected}`)
const errors = (settings) => validateHydro(settings).filter((note) => note.kind === 'error')

test('every preset lays out and draws, and its defaults break none of the manual’s rules', () => {
  for (const [id, settings] of Object.entries(allHydroDefaults())) {
    const scene = hydroScene(settings)
    assert.ok(scene.view.width > 0 && scene.view.height > 0, id)
    assert.deepEqual(errors(settings), [], `${id} breaks a rule as it starts`)
    assert.ok(renderHydroSvg(settings).svg.startsWith('<svg'), id)
  }
})

test('a sign’s border sits half a cap height off the signature, and a full one above the Gas flame', () => {
  for (const id of ['sign-office', 'sign-gas']) {
    const { border, metrics, signatureBox } = hydroScene(hydroDefaults(id))
    const above = id === 'sign-gas' ? 1 : 0.5
    close(metrics.capTop - border.y, above * metrics.capHeight, `${id} top`)
    close(signatureBox.x - border.x, 0.5 * metrics.capHeight, `${id} side`)
    close(border.bottom - metrics.baseline, 0.5 * metrics.capHeight, `${id} bottom`)
  }
})

test('a facility name starts one x-height below the signature and ends the sign half a cap below', () => {
  const { metrics, border } = hydroScene(hydroDefaults('sign-plant'))
  close(metrics.facilityFirstTop, metrics.baseline + metrics.xHeight, 'name top')
  assert.equal(metrics.facilityLineBoxes.length, 3)
  close(border.bottom - metrics.facilityLastBaseline, 0.5 * metrics.capHeight, 'bottom border')
  // Descenders only just clear the line below: no leading beyond that.
  const [first, second] = metrics.facilityLineBoxes
  assert.ok(second.y > first.bottom && second.y - first.bottom < 0.02 * metrics.capHeight)
})

test('the manual’s value thresholds: 20/80 on general backgrounds, 30/31 on vehicles', () => {
  const general = { ...hydroDefaults('positive-light'), autoTreatment: true }
  assert.equal(recommendedMode({ ...general, backgroundValue: 20 }), 'black')
  assert.equal(recommendedMode({ ...general, backgroundValue: 50 }), null)
  assert.equal(recommendedMode({ ...general, backgroundValue: 80 }), 'white')
  // The vehicle rule must not stand in for the missing general one.
  assert.ok(errors({ ...general, backgroundValue: 50 }).some((note) => /21–79/.test(note.text)))

  const vehicle = hydroDefaults('vehicle-corporate-positive')
  assert.equal(recommendedMode({ ...vehicle, backgroundValue: 30 }), 'black')
  assert.equal(recommendedMode({ ...vehicle, backgroundValue: 31 }), 'white')
  assert.equal(effectiveMode({ ...vehicle, backgroundValue: 31 }), 'white')
  assert.ok(errors({ ...vehicle, autoTreatment: false, mode: 'black', backgroundValue: 60 }).length)
})

test('the alternative ink needs white ground and at least 70% value', () => {
  const ink = hydroDefaults('positive-ink')
  assert.deepEqual(errors(ink), [])
  assert.ok(errors({ ...ink, inkValue: 60 }).length)
  assert.ok(errors({ ...ink, backgroundColour: '#eeeeee' }).length)
})

test('in corporate colour only the symbol is coloured, and the Gas H matches its flame', () => {
  const corporate = hydroPalette(hydroDefaults('standard'))
  assert.equal(corporate.ink, '#000000')
  assert.notEqual(corporate.upper, corporate.lower)
  const { svg } = renderHydroSvg(hydroDefaults('gas'), { prefix: 'g' })
  const flame = svg.match(/id="g-emblem-1-flame" fill="([^"]+)"/)[1]
  assert.equal(svg.match(/id="g-emblem-1-upper" fill="([^"]+)"/)[1], flame)
  assert.equal(svg.match(/id="g-emblem-1-lower" fill="([^"]+)"/)[1], flame)
})

test('lettering is outlined by default and live on request', () => {
  const settings = hydroDefaults('sign-freight')
  const outlined = renderHydroSvg(settings).svg
  assert.ok(!outlined.includes('<text'))
  assert.ok(outlined.includes('data-text="Huntingdon Freight Office"'))
  const live = renderHydroSvg(settings, { outline: false }).svg
  assert.ok(live.includes('>Huntingdon Freight Office</text>'))
})

test('the fitted wordmark is used for B.C.Hydro, and other wording is typeset', () => {
  assert.equal(hydroScene(hydroDefaults('standard')).runs.length, 9)
  const custom = { ...hydroDefaults('standard'), wordmark: 'B.C.Transit' }
  const scene = hydroScene(custom)
  assert.equal(scene.runs.length, 1)
  assert.ok(validateHydro(custom).some((note) => /Custom wording/.test(note.text)))
})

test('kerning applies to typeset runs, not to the hand-placed wordmark letters', () => {
  const kerned = setRun('AV', { x: 0, y: 0, size: 1000 })
  const placed = setRun('AV', { x: 0, y: 0, size: 1000, optical: true })
  assert.ok(kerned.positions[1] < placed.positions[1])
  close(capHeightAt(1000), 662, 'cap height')
})

test('letters the serif lacks are named, and the run falls back to live text', () => {
  assert.deepEqual(missingLetters('Hydro 水'), ['水'])
  const settings = { ...hydroDefaults('standard'), wordmark: 'Hydro 水' }
  assert.ok(renderHydroSvg(settings).svg.includes('<text'))
  assert.ok(validateHydro(settings).some((note) => note.text.includes('水')))
})

test('a vehicle pair moves together while it is linked', () => {
  assert.equal(pairedPreset('vehicle-gas-positive'), 'vehicle-gas-reverse')
  assert.equal(pairedPreset('positive-white'), null)
  const next = updateHydroSettings(allHydroDefaults(), 'vehicle-gas-positive', 'textScale', 120)
  assert.equal(next['vehicle-gas-reverse'].textScale, 120)
  const unlinked = updateHydroSettings(
    updateHydroSettings(allHydroDefaults(), 'vehicle-gas-positive', 'linkVehiclePair', false),
    'vehicle-gas-positive', 'textScale', 120)
  assert.equal(unlinked['vehicle-gas-reverse'].textScale, 100)
})

test('settings from a file are held within bounds, and v1 files come across', () => {
  const clean = cleanHydroSettings({ textScale: 999, mode: 'neon', wordmark: 'A\u0007B', ink: 'red' }, 'standard')
  assert.equal(clean.textScale, 145)
  assert.equal(clean.mode, 'colour')
  assert.equal(clean.wordmark, 'A B')
  assert.equal(clean.ink, hydroDefaults('standard').ink)

  const { templates, active, note } = readHydroProject({
    schema: 'bc-hydro-templates/v1', active: 'droplet', templates: { droplet: { textScale: 110 } }
  })
  assert.equal(active, 'gas')
  assert.equal(templates.gas.textScale, 110)
  assert.equal(templates.gas.screenPalette, 'legacy')
  assert.ok(note)
  assert.throws(() => readHydroProject({ schema: 'something-else' }))
})

test('the specimen sheet carries every preset of a group', () => {
  const all = allHydroDefaults()
  const sheet = renderHydroSheet(all, 'vehicle')
  const vehicles = Object.values(HYDRO_PRESETS).filter((preset) => preset.group === 'vehicle')
  for (const preset of vehicles) assert.ok(sheet.includes(`>${preset.name}<`))
  assert.ok(!sheet.includes('>Office identification<'))
})

test('two renders never share an id', () => {
  const ids = (svg) => [...svg.matchAll(/ id="([^"]+)"/g)].map(([, id]) => id)
  const a = ids(renderHydroSvg(hydroDefaults('standard')).svg)
  const b = new Set(ids(renderHydroSvg(hydroDefaults('standard')).svg))
  assert.ok(a.every((id) => !b.has(id)))
})
