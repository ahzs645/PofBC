import { test } from 'node:test'
import assert from 'node:assert/strict'
import { galleryPlaceUrl, readCoverageFilters } from './galleryPlace.js'

test('a subject link leaves the prior mark, palette and register filters behind', () => {
  const url = galleryPlaceUrl('https://example.org/PofBC/?view=gallery&logos=old&mark=old-mark&colour=blue&coverage=1&identity-family=transit#railway-history', { subject: 'translink' })
  assert.equal(url.pathname, '/PofBC/')
  assert.equal(url.search, '?view=gallery&subject=translink')
  assert.equal(url.hash, '')
})

test('register filters round-trip in a shareable URL without changing the deployment base', () => {
  const filters = { family: 'municipalities', state: 'missing', scope: 'core', query: 'Sea Bus', region: 'Capital Regional District' }
  const url = galleryPlaceUrl('https://example.org/PofBC/?subject=translink', { coverage: true, filters })
  assert.equal(url.searchParams.get('view'), 'gallery')
  assert.equal(url.searchParams.get('coverage'), '1')
  assert.deepEqual(readCoverageFilters(url.search), filters)
  assert.equal(url.searchParams.has('subject'), false)
})

test('existing collection/mark links stay stable when leaving a subject', () => {
  const url = galleryPlaceUrl('https://example.org/?view=gallery&subject=translink', { collection: 'bc-hydro', mark: 'hydro-mark' })
  assert.equal(url.search, '?view=gallery&logos=bc-hydro&mark=hydro-mark')
  const home = galleryPlaceUrl(url.href)
  assert.equal(home.search, '?view=gallery')
})

test('a gallery page cannot carry a related-body or comparison mode into its next organization link', () => {
  const url = galleryPlaceUrl('https://example.org/PofBC/?view=government&mode=related&node=translink&year=1970&compare=2020&undated=0&local=1&instrument=old', { subject: 'bc-hydro' })
  assert.equal(url.search, '?view=gallery&subject=bc-hydro')
})

test('tourism sections and open records do not leak into another gallery page', () => {
  const url = galleryPlaceUrl('https://example.org/PofBC/?view=gallery&logos=tourism-bc-destination-bc#tourism-websites/hellobc', { collection: 'bc-hydro' })
  assert.equal(url.search, '?view=gallery&logos=bc-hydro')
  assert.equal(url.hash, '')
})
