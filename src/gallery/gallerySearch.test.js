import { test } from 'node:test'
import assert from 'node:assert/strict'
import { GALLERY_COLLECTIONS, childCollectionsOf, collectionById } from './collections.js'
import { GALLERY_TYPE_OPTIONS, browseGallery, gallerySections, isSearchShortcut, searchGallery, wordsOf } from './gallerySearch.js'

test('an empty query finds nothing', () => {
  assert.deepEqual(searchGallery(''), { collections: [], marks: [] })
  assert.deepEqual(searchGallery('   '), { collections: [], marks: [] })
  assert.deepEqual(wordsOf(' BC  Hydro '), ['bc', 'hydro'])
})

test('a collection is found by its name, every word anywhere in it', () => {
  const { collections } = searchGallery('hydro')
  assert.ok(collections.some((collection) => collection.id === 'bc-hydro'))
  assert.ok(searchGallery('housing commission').collections.some((collection) => collection.id === 'collected-bc-housing'))
})

test('tourism websites and brands find their connected collection without duplicate logo results', () => {
  for (const query of ['HelloBC', 'WorldHost', 'BC Escapes', 'Near Me BC', 'hellobc.co.uk', '100BCMoments']) {
    const result = searchGallery(query)
    assert.equal(result.collections.filter((collection) => collection.id === 'tourism-bc-destination-bc').length, 1, query)
    assert.ok(!result.marks.some(({ collection }) => collection.id === 'tourism-bc-destination-bc'), query)
  }
})

test('an inventory-only tourism address is not indexed as a named website record', () => {
  const result = searchGallery('commmunitytourismfoundations.com')
  assert.ok(!result.collections.some((collection) => collection.id === 'tourism-bc-destination-bc'))
})

test('a logo is found by its title, with the collection it opens in, once', () => {
  const { marks } = searchGallery('coroners')
  const found = marks.find(({ entry }) => entry.id === 'coroners-service')
  assert.ok(found, 'the Coroners Service lockup')
  assert.equal(found.collection.id, 'bc-mark')
  const ids = marks.map(({ entry }) => entry.id)
  assert.equal(new Set(ids).size, ids.length)
})

test('accents and case do not matter', () => {
  assert.deepEqual(wordsOf('Société'), ['societe'])
  assert.ok(searchGallery('WORKSAFE').collections.length > 0)
})

test('organization types narrow both collection and identity matches for the same name', () => {
  const schools = browseGallery('Vancouver', 'schools')
  const municipalities = browseGallery('Vancouver', 'local')
  assert.ok(schools.collections.some(({ id }) => id === 'collected-school-district-39'))
  assert.ok(schools.subjects.every(({ schoolDistrict }) => schoolDistrict))
  assert.ok(municipalities.collections.some(({ id }) => id === 'collected-municipality-vancouver'))
  assert.ok(!municipalities.collections.some(({ id }) => id === 'collected-school-district-39'))
  assert.ok(!municipalities.subjects.some(({ schoolDistrict }) => schoolDistrict))
})

test('type-only browsing includes held artwork and records still awaiting their own collection', () => {
  const { collections, subjects } = browseGallery('', 'postsecondary')
  assert.ok(collections.some(({ id }) => id === 'collected-university-of-northern-bc'))
  assert.ok(subjects.some(({ id, hasArtwork }) => id === 'douglas-college' && !hasArtwork))
  assert.ok(browseGallery('', 'crowns').collections.some(({ id }) => id === 'bc-hydro'))
  assert.deepEqual(browseGallery('BC Hydro', 'postsecondary'), { collections: [], marks: [], subjects: [] })
})

test('All sections match the filter order and show each browsable collection once', () => {
  const sections = gallerySections('')
  assert.equal(sections[0].value, 'crowns')
  assert.deepEqual(sections.map(({ value, label }) => ({ value, label })), GALLERY_TYPE_OPTIONS.slice(1))
  const ids = sections.flatMap(({ collections }) => collections.map(({ id }) => id))
  assert.deepEqual(ids.sort(), GALLERY_COLLECTIONS
    .filter(({ foldedUnder, showInGalleryIndex }) =>
      !['collected-translink', 'collected-metro-vancouver'].includes(foldedUnder) && showInGalleryIndex !== false)
    .map(({ id }) => id).sort())
  const transit = sections.find(({ value }) => value === 'transport')
  for (const id of ['collected-translink', 'bc-transit', 'bc-ferries']) {
    assert.ok(transit.collections.some((collection) => collection.id === id))
  }
})

test('the Geological Survey groups its products while product searches still find them', () => {
  const parent = 'collected-sub-british-columbia-geological-survey'
  const [province] = gallerySections('provincial')
  const children = childCollectionsOf(parent)
  assert.deepEqual(children.map(({ id }) => id), ['collected-bcgs-mapplace', 'collected-bcgs-minfile'])
  for (const child of children) {
    assert.equal(child.foldedUnder, parent)
    assert.ok(province.collections.includes(child))
    assert.ok(browseGallery(child.label, 'provincial').collections.includes(child))
  }
  assert.ok(!children.some(({ id }) => id === 'collected-geoscience-bc'))
})

test('the historical Liquor Control Board remains searchable by name', () => {
  const board = collectionById('collected-liquor-control-board')
  assert.ok(board)
  assert.ok(!gallerySections('').some(({ collections }) => collections.includes(board)))
  assert.ok(searchGallery('Liquor Control Board').collections.includes(board))
})

test('TransLink service searches lead to TransLink and the service collections stay on its page', () => {
  const [transit] = gallerySections('transport')
  const children = childCollectionsOf('collected-translink')
  assert.ok(children.some(({ id }) => id === 'collected-compass'))
  assert.ok(!transit.collections.some((collection) => children.includes(collection)))
  for (const query of ['Compass', 'SkyTrain', 'HandyDART', 'T marker']) {
    const { collections, marks, subjects } = browseGallery(query, 'transport')
    assert.equal(collections.filter(({ id }) => id === 'collected-translink').length, 1, query)
    assert.ok(!collections.some((collection) => children.includes(collection)), query)
    assert.ok(!marks.some(({ collection }) => children.includes(collection)), query)
    assert.ok(!subjects.some(({ id }) => children.some((child) => child.id === `collected-${id}`)), query)
  }
})

test('Regional Parks is browsed through Metro Vancouver, including from a service search', () => {
  const metro = collectionById('collected-metro-vancouver')
  const parks = collectionById('collected-metro-vancouver-regional-parks')
  assert.ok(childCollectionsOf(metro.id).includes(parks))
  assert.ok(!gallerySections('local').some(({ collections }) => collections.includes(metro)))
  for (const type of ['', 'regional-districts']) {
    const cards = gallerySections(type).flatMap(({ collections }) => collections)
    assert.ok(cards.includes(metro))
    assert.ok(!cards.includes(parks))
    const { collections, marks, subjects } = browseGallery('Regional Parks', type)
    assert.equal(collections.filter((collection) => collection === metro).length, 1)
    assert.ok(!collections.includes(parks))
    assert.ok(!marks.some(({ collection }) => collection === parks))
    assert.ok(!subjects.some(({ id }) => id === 'metro-vancouver-regional-parks'))
  }
})

test('the shortcut is Cmd-K or Ctrl-K, and nothing else', () => {
  assert.ok(isSearchShortcut({ metaKey: true, key: 'k' }))
  assert.ok(isSearchShortcut({ ctrlKey: true, key: 'K' }))
  assert.ok(!isSearchShortcut({ key: 'k' }))
  assert.ok(!isSearchShortcut({ metaKey: true, shiftKey: true, key: 'k' }))
  assert.ok(!isSearchShortcut({ ctrlKey: true, key: 'j' }))
})
