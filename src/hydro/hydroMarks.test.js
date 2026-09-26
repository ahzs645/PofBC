// BC Hydro's 1990 and current marks: lifted whole, and offered only in the colours each may take.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { HYDRO_MARKS } from '../assets/hydroMarks.js'
import {
  CURRENT_VARIANT_ORDER, CURRENT_VARIANTS, HYDRO_PALETTE, MARK_1990_PRESETS, renderCurrentHydroSvg,
  renderHydroMarkSvg, symbolWidth
} from './hydroMarks.js'
import { entriesOf, findGalleryEntry, GALLERY_COLLECTIONS } from '../gallery/collections.js'

const fills = (svg) => [...svg.matchAll(/data-role="(\w+)"[^>]*fill="([^"]+)"/g)].map(([, role, fill]) => [role, fill])
const count = (id, role) => HYDRO_MARKS[id].shapes.filter((shape) => shape.role === role).length

test('each mark has the parts it was drawn with', () => {
  assert.equal(count('bc-hydro-1990', 'bc'), 2)
  assert.equal(count('bc-hydro-1990', 'hydro'), 5)
  assert.equal(count('bc-hydro-2016', 'wordmark'), 7)
  assert.equal(count('bc-hydro-2016', 'tagline'), 10)
  for (const id of ['bc-hydro-1990', 'bc-hydro-2016', 'bc-hydro-2016-symbol', 'bc-hydro-2016-symbol-border']) {
    assert.equal(count(id, 'upper'), 1, `${id} upper half`)
    assert.equal(count(id, 'lower'), 1, `${id} lower half`)
  }
  assert.equal(count('bc-hydro-2016-symbol-border', 'border'), 1)
})

test('the current logo is only ever drawn in the guidelines’ own colours', () => {
  const allowed = new Set([HYDRO_PALETTE.grass, HYDRO_PALETTE.sea, HYDRO_PALETTE.granite, HYDRO_PALETTE.ice, '#000000'])
  for (const variant of CURRENT_VARIANT_ORDER) {
    for (const [role, fill] of fills(renderCurrentHydroSvg({ variant }).svg)) {
      assert.ok(allowed.has(fill), `${variant}: ${role} is ${fill}`)
    }
  }
  // The symbol's halves are always Grass over Sea wherever the logo is in colour.
  for (const variant of ['colour', 'signage', 'symbol', 'symbol-border']) {
    const drawn = Object.fromEntries(fills(renderCurrentHydroSvg({ variant }).svg))
    assert.equal(drawn.upper, HYDRO_PALETTE.grass)
    assert.equal(drawn.lower, HYDRO_PALETTE.sea)
  }
})

test('the signage version drops the tagline and nothing else', () => {
  const roles = fills(renderCurrentHydroSvg({ variant: 'signage' }).svg).map(([role]) => role)
  assert.ok(!roles.includes('tagline'))
  assert.equal(roles.filter((role) => role === 'wordmark').length, 7)
})

test('clear space is one symbol’s width on every side', () => {
  const tight = renderCurrentHydroSvg({ variant: 'colour', clearSpace: 'none' }).view
  const spaced = renderCurrentHydroSvg({ variant: 'colour', clearSpace: 'symbol' }).view
  const unit = symbolWidth('bc-hydro-2016')
  assert.ok(Math.abs(spaced.width - tight.width - 2 * unit) < 1e-9)
  assert.ok(Math.abs(spaced.height - tight.height - 2 * unit) < 1e-9)
})

test('the 1990 mark keeps its even-odd fills and takes any colour', () => {
  const { svg } = renderHydroMarkSvg({ id: 'bc-hydro-1990', colours: { bc: '#123456' } })
  assert.ok(svg.includes('fill-rule="evenodd"'))
  assert.ok(fills(svg).some(([role, fill]) => role === 'bc' && fill === '#123456'))
  for (const preset of MARK_1990_PRESETS) assert.ok(renderHydroMarkSvg({ id: 'bc-hydro-1990', colours: preset.colours }).svg)
})

test('the gallery lists BC Hydro’s three eras, and every entry opens', () => {
  const hydro = GALLERY_COLLECTIONS.find((collection) => collection.id === 'bc-hydro')
  assert.deepEqual(hydro.eras.map((era) => era.years), ['1961–1990', '1990–2016', '2016–present'])
  for (const entry of entriesOf(hydro)) assert.equal(findGalleryEntry(entry.id), entry)
  assert.equal(hydro.eras[2].entries.length, Object.keys(CURRENT_VARIANTS).length)
})
