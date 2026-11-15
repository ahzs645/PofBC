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

test('rasterizing and distance fields', async () => {
  const { distanceTo, rasterize } = await import('./stipple.js')
  // A 10 × 10 mm square with a 4 × 4 mm hole (nonzero: the hole winds the other way), at 4 px/mm.
  const outer = [[0, 0], [10, 0], [10, 10], [0, 10]]
  const hole = [[3, 3], [3, 7], [7, 7], [7, 3]]
  const mask = rasterize([outer, hole], 40, 40, 4)
  assert.equal(mask[2 * 40 + 2], 1)
  assert.equal(mask[20 * 40 + 20], 0)
  assert.equal(mask.reduce((a, b) => a + b, 0), 40 * 40 - 16 * 16)
  const d = distanceTo(mask, 40, 40, 0, 4)
  assert.ok(Math.abs(d[20 * 40 + 9] - 0.75) < 0.01)
})

test('pebbled fields keep the edge band and the relief halo smooth, and are deterministic', async () => {
  const { TEXTURES, distanceTo, fieldTexture, placeBumps, rasterize } = await import('./stipple.js')
  const field = [[[0, 0], [30, 0], [30, 30], [0, 30]]]
  const raised = [[[12, 12], [18, 12], [18, 18], [12, 18]]]
  const recipe = { ...TEXTURES.pebbled, pxPerMm: 8 }
  const px = 8
  const w = 240
  const h = 240
  const edge = distanceTo(rasterize(field, w, h, px), w, h, 0, px)
  const relief = distanceTo(rasterize(raised, w, h, px), w, h, 1, px)
  const bumps = placeBumps(recipe, { w, h, px, edge, raised: relief })
  assert.ok(bumps.length > 150, `${bumps.length} bumps`)
  assert.deepEqual(placeBumps(recipe, { w, h, px, edge, raised: relief }), bumps)
  for (const b of bumps) {
    const k = Math.floor(b.y) * w + Math.floor(b.x)
    assert.ok(edge[k] >= b.r / px + recipe.bandMm - 1e-6)
    assert.ok(relief[k] >= b.r / px + recipe.haloMm - 1e-6)
  }
  // Irregular: sizes and shapes vary.
  const radii = bumps.map((b) => b.r / px)
  assert.ok(Math.max(...radii) - Math.min(...radii) > 0.25, 'bump sizes vary')
  assert.ok(bumps.some((b) => b.aspect < 0.85))
  const tex = fieldTexture('pebbled', { width: 30, height: 30, field, raised })
  assert.equal(tex.data.length, tex.width * tex.height * 4)
  // The middle of the raised square and the edge band face straight out.
  const flat = (x, y) => [...tex.data.slice((y * tex.width + x) * 4, (y * tex.width + x) * 4 + 3)]
  assert.deepEqual(flat(Math.round(tex.width / 2), Math.round(tex.height / 2)), [128, 128, 255])
  assert.deepEqual(flat(3, Math.round(tex.height / 2)), [128, 128, 255])
})
