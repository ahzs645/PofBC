import { test } from 'node:test'
import assert from 'node:assert/strict'
import { movedGalleryUrl, TRAVEL_PLACE } from './movedGalleryPlaces.js'
import { galleryPlaceUrl, readCoverageFilters } from './galleryPlace.js'

test('a subject link leaves the prior mark, palette and register filters behind', () => {
  const url = galleryPlaceUrl('https://example.org/PofBC/?view=gallery&logos=old&mark=old-mark&colour=blue&coverage=1&identity-family=transit&identity-category=transport#railway-history', { subject: 'translink' })
  assert.equal(url.pathname, '/PofBC/')
  assert.equal(url.search, '?view=gallery&subject=translink')
  assert.equal(url.hash, '')
})

test('register filters round-trip in a shareable URL without changing the deployment base', () => {
  const filters = { family: 'municipalities', state: 'missing', scope: 'core', query: 'Sea Bus', region: 'Capital Regional District', category: 'local' }
  const url = galleryPlaceUrl('https://example.org/PofBC/?subject=translink', { coverage: true, filters })
  assert.equal(url.searchParams.get('view'), 'gallery')
  assert.equal(url.searchParams.get('coverage'), '1')
  assert.equal(url.searchParams.get('identity-category'), 'local')
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
  const publicService = 'vector-bc-public-service-where-ideas-work-2023-reverse'
  for (const search of ['logos=specimens-public-service', 'logos=specimens-public-service&mark=' + publicService]) {
    assert.equal(moved(search).search, '?view=gallery&logos=bc-mark&mark=' + publicService)
  }
  assert.equal(moved('logos=bc-mark&mark=' + publicService), null)
  for (const [program, specimen] of [['welcome-bc', 'vector-welcomebc-2016'], ['work-bc', 'vector-workbc-2016'], ['stronger-bc', 'vector-BCID_StrongerBC_RGB_rev']]) {
    assert.equal(moved('logos=specimens-' + program).search, `?view=gallery&logos=bc-mark&mark=${program}`)
    assert.equal(moved(`logos=specimens-${program}&mark=${specimen}`).search, `?view=gallery&logos=bc-mark&mark=${specimen}`)
  }
  assert.equal(moved('logos=specimens-pacific-gateway').search, '?view=initiatives&initiative=pacific-gateway&section=marks')
  const jobsPlan = 'vector-canada-starts-here-bc-jobs-plan-2012'
  assert.equal(moved('logos=specimens-pacific-gateway&mark=' + jobsPlan).search,
    `?view=initiatives&initiative=pacific-gateway&section=marks&record=${jobsPlan}`)
  assert.equal(moved('logos=specimens-bc-the-education-province').search,
    '?view=initiatives&initiative=bc-the-education-province')
  assert.equal(moved('logos=specimens-bc-the-education-province&mark=education-province-wordmark').search,
    '?view=initiatives&initiative=bc-the-education-province&section=marks&record=education-province-wordmark')
  assert.equal(moved('logos=collected-bcgs-minfile&mark=minfile-early-web'), null)
  assert.equal(moved('logos=collected-bcgs-mapplace'), null)
  assert.equal(moved('logos=bc-mark&mark=welcome-bc'), null)
  assert.equal(moved('subject=bc-youth'), null)
})

test('an era fragment closes when moving to another gallery page', () => {
  const url = galleryPlaceUrl('https://example.org/PofBC/?view=gallery&logos=collected-forrex#era-forrex-natural-resources', { collection: 'collected-siferp' })
  assert.equal(url.search, '?view=gallery&logos=collected-siferp')
  assert.equal(url.hash, '')
})

test('2019 endorsed guide links open BC Mark and preserve explicit source versions', () => {
  const old = 'https://example.test/PofBC/?view=gallery&logos=collected-endorsed-marks-2019'
  assert.equal(movedGalleryUrl(old).search, '?view=gallery&logos=bc-mark')
  assert.equal(movedGalleryUrl(old + '&mark=endorsed-2019-province-grey-reverse').search,
    '?view=gallery&logos=bc-mark&mark=endorsed-2019-province-grey-reverse')
})
