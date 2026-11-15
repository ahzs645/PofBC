import { test } from 'node:test'
import assert from 'node:assert/strict'
import { GROUND_SHARE, bodyFor, hexToHsl, metalOf, partFor } from './badgeParts.js'
import { BADGE_VIEW_DEFAULTS, loadBadgeView, normalizeBadgeView, saveBadgeView } from './badgeView.js'

test('hexToHsl reads short and long hex and rejects anything else', () => {
  assert.deepEqual(hexToHsl('#fff'), { h: 0, s: 0, l: 1 })
  const green = hexToHsl('#006638')
  assert.ok(Math.abs(green.h - 153) < 1 && green.s > 0.9 && green.l < 0.25)
  assert.equal(hexToHsl('url(#silver)'), null)
  assert.equal(hexToHsl('none'), null)
})

test('the base metal follows the medium, a gradient’s name, then the lit paint by area', () => {
  assert.equal(metalOf({ medium: 'Leather badge', paints: [{ paint: '#b69552' }] }), 'leather')
  assert.equal(metalOf({ medium: 'Metal badge', paints: [{ paint: 'url(#silver)' }, { paint: '#b69552' }] }), 'silver')
  // S51-O01: a large dark olive field under gold lettering is a gold badge.
  assert.equal(metalOf({ medium: 'Metal badge', paints: [{ paint: '#514d3b', area: 50 }, { paint: '#b69552', area: 8 }] }), 'gold')
  assert.equal(metalOf({ medium: 'Metal badge', paints: [{ paint: '#65726c', area: 5 }, { paint: '#f1f3e8', area: 5 }] }), 'silver')
})

test('pieces take their part from the drawing’s markings, size and paint', () => {
  const metal = 'silver'
  assert.equal(partFor({ paint: 'url(#silver)', metal }).part, 'plate')
  assert.equal(partFor({ paint: 'url(#silver)', share: GROUND_SHARE + 0.1, metal }).part, 'ground')
  assert.equal(partFor({ paint: '#514d3b', border: true, share: 0.8, metal: 'gold' }).part, 'ground')
  assert.equal(partFor({ paint: '#006638', metal }).part, 'enamel')
  assert.equal(partFor({ paint: '#006638', metal }).metalness, 0)
  assert.equal(partFor({ paint: '#15241b', metal }).part, 'recess')
  assert.equal(partFor({ paint: '#f1f3e8', caption: 'PARK RANGER', metal }).part, 'lettering')
  assert.equal(partFor({ paint: '#b69552', kind: 'stroke', border: true, metal: 'gold' }).part, 'rim')
  assert.equal(partFor({ paint: '#b69552', kind: 'stroke', metal: 'gold' }).part, 'detail')
  assert.equal(partFor({ paint: '#b69552', metal: 'gold' }).part, 'emblem')
  // Gold paint on a gold badge is metal, never enamel.
  assert.equal(partFor({ paint: '#d3b777', metal: 'gold' }).metalness, 1)
})

test('lighter raised metal stands higher than darker, so lit faces sit on their shading', () => {
  const light = partFor({ paint: '#f1f3e8', caption: 'X', metal: 'silver' })
  const dark = partFor({ paint: '#65726c', caption: 'X', metal: 'silver' })
  assert.ok(light.thickness > dark.thickness)
})

test('leather is tooled, not metal: no metalness and shallower relief', () => {
  const tooled = partFor({ paint: '#ecb86e', caption: 'JUNIOR', metal: 'leather' })
  const struck = partFor({ paint: '#ecb86e', caption: 'JUNIOR', metal: 'gold' })
  assert.equal(tooled.metalness, 0)
  assert.ok(tooled.thickness < struck.thickness)
  assert.equal(bodyFor('leather').metalness, 0)
  assert.ok(bodyFor('leather').thickness > bodyFor('silver').thickness)
})

test('stored badge view settings are validated and survive missing storage', () => {
  assert.deepEqual(normalizeBadgeView(null), BADGE_VIEW_DEFAULTS)
  assert.deepEqual(normalizeBadgeView({ mode: 'x', curvature: 'dome', rise: 12.3, camera: 'top' }), { mode: 'metal', curvature: 'dome', rise: 8, camera: 'top' })
  assert.equal(normalizeBadgeView({ rise: 2.2 }).rise, 2)
  const map = new Map()
  const storage = { getItem: (k) => map.get(k) ?? null, setItem: (k, v) => map.set(k, v) }
  saveBadgeView(storage, { mode: 'vector', curvature: 'flat', rise: 3, camera: 'side' })
  assert.deepEqual(loadBadgeView(storage), { mode: 'vector', curvature: 'flat', rise: 3, camera: 'side' })
  assert.deepEqual(loadBadgeView({ getItem: () => { throw new Error('blocked') } }), BADGE_VIEW_DEFAULTS)
  saveBadgeView({ setItem: () => { throw new Error('quota') } }, BADGE_VIEW_DEFAULTS)
})
