import { test } from 'node:test'
import assert from 'node:assert/strict'
import { BADGE_MODES, BADGE_VIEW_KEY, applyBadgeShape, badgeModeFor, badgeShapeFor, badgeShapeStatus, loadBadgeView, normalizeBadgeView, saveBadgeView } from './badgeView.js'

test('legacy 3D preferences survive comparison and a model-specific rise cap', () => {
  const stored = new Map([[BADGE_VIEW_KEY, JSON.stringify({ mode: 'metal', curvature: 'dome', rise: 7.5, camera: 'back' })]])
  const storage = { getItem: (key) => stored.get(key), setItem: (key, value) => stored.set(key, value) }
  const view = loadBadgeView(storage)
  assert.equal(view.mode, 'metal')
  assert.deepEqual(badgeShapeFor(view, 2.75), { mode: 'dome', rise: 2.75 })
  assert.deepEqual(badgeShapeFor(view, 8), { mode: 'dome', rise: 7.5 })
  saveBadgeView(storage, { ...view, mode: 'compare' })
  assert.equal(badgeModeFor(loadBadgeView(storage).mode, false), 'vector')
  assert.deepEqual(loadBadgeView(storage), { ...view, mode: 'compare' })
  assert.deepEqual(badgeShapeFor({ ...view, curvature: 'flat' }, 0), { mode: 'flat', rise: 0 })
  assert.equal(loadBadgeView(storage).rise, 7.5, 'caps and Flat must not overwrite the remembered rise')
})

test('zero and unusable geometry caps give a safe flat request', () => {
  for (const cap of [0, -1, NaN, Infinity]) {
    assert.deepEqual(badgeShapeFor({ curvature: 'cylinder', rise: 4 }, cap), { mode: 'flat', rise: 0 })
  }
  assert.deepEqual(badgeShapeFor({ curvature: 'dome', rise: 0 }, 8), { mode: 'flat', rise: 0 })
})

test('only the current model and successfully applied shape can be exported', () => {
  const scene = { bend: (mode, rise) => ({ mode, rise, radius: 100, span: 50 }) }
  const build = { patchId: 'S01-O01', scene }
  const shape = { mode: 'cylinder', rise: 4 }
  const applied = applyBadgeShape(build, shape)
  assert.equal(badgeShapeStatus(applied, build, shape), 'ready')
  assert.deepEqual(applied.result, { ...shape, radius: 100, span: 50 })
  // A remount/retry can use the same badge ID and still represent a completely different model.
  assert.equal(badgeShapeStatus(applied, { ...build }, shape), 'pending')
  assert.equal(badgeShapeStatus(applied, { patchId: 'S51-O01', scene }, shape), 'pending')
  assert.equal(badgeShapeStatus(applied, build, { mode: 'dome', rise: 4 }), 'pending')
  assert.equal(badgeShapeStatus(applied, build, { mode: 'cylinder', rise: 4.5 }), 'pending')
  assert.equal(badgeShapeStatus(null, build, shape), 'pending')
  assert.equal(badgeShapeStatus(applied, null, shape), 'pending')
})

test('failed or incomplete bending cannot reuse an earlier successful result', () => {
  const shape = { mode: 'dome', rise: 6 }
  const error = new RangeError('The curve is too deep')
  const build = { scene: { bend: () => { throw error } } }
  const failed = applyBadgeShape(build, shape)
  assert.equal(failed.error, error)
  assert.equal(failed.result, null)
  assert.equal(badgeShapeStatus(failed, build, shape), 'failed')
  for (const result of [null, { mode: 'flat', rise: 0 }, { mode: 'dome', rise: 4 }]) {
    const wrong = { scene: { bend: () => result } }
    const applied = applyBadgeShape(wrong, shape)
    assert.equal(applied.result, null)
    assert.equal(badgeShapeStatus(applied, wrong, shape), 'failed')
  }
  build.scene.bend = (mode, rise) => ({ mode, rise, radius: 90 })
  assert.equal(badgeShapeStatus(applyBadgeShape(build, shape), build, shape), 'ready', 'a successful retry restores export availability')
})

test('a reader who last used the retired Relief or Embroidery view lands on 3D', () => {
  assert.equal(normalizeBadgeView({ mode: 'relief' }).mode, 'metal')
  assert.equal(normalizeBadgeView({ mode: 'embroidery' }).mode, 'metal')
  assert.ok(!BADGE_MODES.includes('relief') && !BADGE_MODES.includes('embroidery'))
})
