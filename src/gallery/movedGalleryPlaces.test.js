import { test } from 'node:test'
import assert from 'node:assert/strict'
import { collectionById, entriesOf, GALLERY_COLLECTIONS } from './collections.js'
import { gallerySections } from './gallerySearch.js'
import { movedGalleryPlace, movedGalleryUrl, RECREATION_COLLECTION, RECREATION_MARKS, RECREATION_PLACE } from './movedGalleryPlaces.js'

test('the Recreation and Conservation redirect names exactly the collection’s marks', () => {
  const collection = collectionById(RECREATION_COLLECTION)
  assert.deepEqual(new Set(entriesOf(collection).map(({ id }) => id)), RECREATION_MARKS)
})

test('the department is no longer listed in the gallery, but its records still resolve', () => {
  const listed = gallerySections('').flatMap(({ collections }) => collections.map(({ id }) => id))
  assert.ok(!listed.includes(RECREATION_COLLECTION))
  assert.ok(GALLERY_COLLECTIONS.some(({ id }) => id === RECREATION_COLLECTION))
  // The museum and BC Parks keep their own copies of the shared marks, under their own ids.
  assert.ok(entriesOf(collectionById('royal-bc-museum')).some(({ id }) => id === 'rbcm-1971-bcpm'))
  assert.ok(entriesOf(collectionById('bc-parks')).some(({ id }) => id === 'bcp-1973-shield'))
})

test('gallery links to the department open in Departmental Logos', () => {
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: RECREATION_COLLECTION }), RECREATION_PLACE)
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: RECREATION_COLLECTION, mark: 'drc-parks' }),
    { ...RECREATION_PLACE, 'internal-logo': 'drc-parks' })
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', mark: 'drc-fw-oval-1973' }),
    { ...RECREATION_PLACE, 'internal-logo': 'drc-fw-oval-1973' })
  // The same design kept under BC Parks stays in BC Parks.
  assert.equal(movedGalleryPlace({ view: 'gallery', logos: 'bc-parks', mark: 'bcp-1973-shield' }), null)
  const url = movedGalleryUrl('https://example.test/PofBC/?view=gallery&logos=recreation-conservation&mark=drc-museum')
  assert.equal(url.search, '?view=internal&internal=recreation-conservation&internal-logo=drc-museum')
})
