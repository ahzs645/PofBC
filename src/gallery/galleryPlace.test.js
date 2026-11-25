import { test } from 'node:test'
import assert from 'node:assert/strict'
import { movedGalleryUrl, TRAVEL_PLACE } from './movedGalleryPlaces.js'
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

test('moved gallery links open the corresponding department, initiative record, or one-off', () => {
  const moved = (search) => movedGalleryUrl('https://example.test/PofBC/?view=gallery&' + search)
  const travel = moved('logos=bc-mark&mark=bc-travel-industry-ca-1970')
  assert.equal(travel.pathname, '/PofBC/')
  assert.deepEqual(Object.fromEntries(travel.searchParams), TRAVEL_PLACE)
  assert.deepEqual(Object.fromEntries(moved('mark=bc-travel-industry-ca-1970').searchParams), TRAVEL_PLACE)
  assert.equal(moved('logos=collected-bc-youth').search, '?view=initiatives&initiative=bc-youth')
  for (const mark of ['bc-youth-right-flag', 'bc-youth-left-flag']) {
    assert.equal(moved('logos=collected-bc-youth&mark=' + mark).search,
      '?view=initiatives&initiative=bc-youth&section=marks&record=' + mark)
  }
  const gcpe = 'collected-government-communications-and-public-engagement'
  const published = 'source-recovered-followup-government-communications-and-public-engagement-estimate-notes-2024'
  assert.equal(moved('logos=' + gcpe).search, '?view=gallery&logos=bc-mark&mark=gcpe-estimate-notes-2024-rebuilt')
  assert.equal(moved('logos=' + gcpe + '&mark=' + published).searchParams.get('mark'), published)
  assert.equal(moved('logos=bc-mark&mark=welcome-bc'), null)
  assert.equal(moved('subject=bc-youth'), null)
})
