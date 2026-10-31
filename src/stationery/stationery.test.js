// The 1977 stationery: the specification's measurements, drawn by brandkit's engine.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { allFields, renderTemplate } from '../../vendor/brandkit/src/engine/index.js'
import { createStationeryBrand, ministryLines } from './bcStationery.js'
import { createHelveticaProvider } from './helveticaFonts.js'

const brand = createStationeryBrand()
const fonts = createHelveticaProvider(null)
const piece = (id) => brand.templates.find((template) => template.id === id)

test('each piece is its specified size', () => {
  assert.deepEqual(renderTemplate({ brand, fonts }, piece('calling-card')).physical, ['3.5in', '2in'])
  assert.deepEqual(renderTemplate({ brand, fonts }, piece('letterhead-general')).physical, ['8.5in', '11in'])
  assert.deepEqual(renderTemplate({ brand, fonts }, piece('envelope-no10')).physical, ['9.5in', '4.125in'])
})

test('the type hangs from the specified line, in the specified sizes', () => {
  const svg = renderTemplate({ brand, fonts }, piece('letterhead-general')).svg
  // 10 pt Helvetica's capitals hang from 9 mm: its first baseline is a cap height lower.
  assert.match(svg, /<text id="province-1" x="36" y="11\.53"[^>]*font-size="3\.527778" font-weight="700"/)
  assert.match(svg, /<text id="ministry-1" x="91" y="11\.53"/)
  assert.match(svg, /<path id="rule" d="M36 29L206\.9 29" stroke="#000000" stroke-width="0\.176389"\/>/)
})

test('a ministry wraps to each piece’s column, with "Ministry of" on its own line', () => {
  const values = { ministry: ministryLines('Ministry of Environment and Climate Change Strategy') }
  const lines = (id) => [...renderTemplate({ brand, fonts, values }, piece(id)).svg.matchAll(/<text id="ministry-\d"[^>]*>([^<]*)</g)].map((match) => match[1])
  assert.equal(lines('letterhead-general')[0], 'Ministry of')
  for (const id of ['letterhead-general', 'calling-card', 'envelope-no10']) assert.ok(lines(id).length <= 3, id)
  assert.notDeepEqual(lines('envelope-no10'), lines('letterhead-general'), 'the narrower envelope column breaks differently')
})

test('fields are shared: one name, address and telephone fill every piece', () => {
  const fields = allFields(brand.templates, brand)
  const byId = Object.fromEntries(fields.map((field) => [field.id, field]))
  assert.deepEqual(byId.city.templates.sort(), ['calling-card', 'envelope-no10', 'letterhead-general'])
  assert.equal(byId.telephone.label, 'Telephone')
  const values = { city: 'Victoria', address: '1450 Government Street', 'postal-code': 'V8W 9E2', telephone: '' }
  const envelope = renderTemplate({ brand, fonts, values }, piece('envelope-no10')).svg
  assert.match(envelope, />1450 Government Street, Victoria, British Columbia, V8W 9E2</)
  const letterhead = renderTemplate({ brand, fonts, values }, piece('letterhead-general')).svg
  assert.match(letterhead, />Victoria, British Columbia</)
  assert.doesNotMatch(letterhead, /Telephone:/, 'a cleared telephone takes its line with it')
})

test('the envelope is all in the symbol colour; the card sets its type in black', () => {
  const envelope = renderTemplate({ brand, fonts }, piece('envelope-no10')).svg
  assert.ok(!/fill="#000000"/.test(envelope))
  const black = createStationeryBrand({ symbolColour: '#000000' })
  assert.match(renderTemplate({ brand: black, fonts }, black.templates[0]).svg, /data-brand-symbol="provincial-symbol" data-size="standard" fill="#000000"/)
})

test('ministry names put "Ministry of" on its own line', () => {
  assert.equal(ministryLines('Ministry of Forests'), 'Ministry of\nForests')
  assert.equal(ministryLines('Office of the Premier'), 'Office of the Premier')
})
