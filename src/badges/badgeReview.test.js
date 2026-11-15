import { test } from 'node:test'
import assert from 'node:assert/strict'
import { badgeReviewAssetUrl, badgeReviewSources } from './badgeReview.js'
import { BADGE_VIEW_DEFAULTS, badgeModeFor, loadBadgeView, saveBadgeView } from './badgeView.js'

const badge = { id: 'S01-O01' }
const source = {
  occurrenceId: 'S01-O01', url: 'https://drive.google.com/file/d/reference/view',
  cropUrl: 'badge-review/crops/S01-O01.webp', width: 539, height: 607,
  sourceFileSha256: 'a'.repeat(64), cropSha256: 'b'.repeat(64)
}

test('source review requires the matching badge and a measured, hashed reference', () => {
  const review = { id: badge.id, sources: [source] }
  assert.deepEqual(badgeReviewSources(badge, review), [source])
  assert.deepEqual(badgeReviewSources(badge, { ...review, id: 'S51-O01' }), [])
  for (const change of [{ cropSha256: null }, { sourceFileSha256: 'invalid' }, { width: 0 }, { height: NaN }, { cropUrl: '' }, { occurrenceId: '' }]) {
    assert.deepEqual(badgeReviewSources(badge, { ...review, sources: [{ ...source, ...change }] }), [])
  }
  assert.deepEqual(badgeReviewSources(badge, { ...review, sources: [null] }), [])
  assert.deepEqual(badgeReviewSources(badge, null), [])
})

test('a saved comparison without a reference uses Vector and keeps the 3D preferences', () => {
  const entries = new Map()
  const storage = { getItem: (key) => entries.get(key) ?? null, setItem: (key, value) => entries.set(key, value) }
  for (const mode of ['source', 'compare']) {
    const settings = { mode, curvature: 'dome', rise: 6.5, camera: 'side' }
    saveBadgeView(storage, settings)
    assert.deepEqual(loadBadgeView(storage), settings)
    assert.equal(badgeModeFor(loadBadgeView(storage).mode, false), 'vector')
    assert.equal(badgeModeFor(loadBadgeView(storage).mode, true), mode)
    assert.deepEqual(loadBadgeView(storage), settings, 'a visible fallback must not overwrite stored choices')
  }
  assert.deepEqual(loadBadgeView(null), BADGE_VIEW_DEFAULTS)
  assert.equal(BADGE_VIEW_DEFAULTS.mode, 'metal', 'the existing 3D default remains available')
  assert.equal(badgeModeFor('metal', false), 'metal')
  assert.equal(badgeModeFor('vector', true), 'vector')
})

test('source crops resolve under the production base path', () => {
  assert.equal(badgeReviewAssetUrl(source.cropUrl, '/PofBC/'), '/PofBC/badge-review/crops/S01-O01.webp')
  assert.equal(badgeReviewAssetUrl('/badge-review/crops/S01-O01.webp', '/PofBC/'), '/PofBC/badge-review/crops/S01-O01.webp')
  assert.equal(badgeReviewAssetUrl('https://example.org/source.webp', '/PofBC/'), 'https://example.org/source.webp')
  assert.equal(badgeReviewAssetUrl(undefined, '/PofBC/'), null)
})
