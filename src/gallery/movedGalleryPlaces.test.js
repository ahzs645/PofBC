import { test } from 'node:test'
import assert from 'node:assert/strict'
import { collectionById, entriesOf, GALLERY_COLLECTIONS } from './collections.js'
import { gallerySections } from './gallerySearch.js'
import {
  DEPARTMENTAL_COLLECTIONS, DEPARTMENTAL_MARKS, departmentalPlace, movedGalleryPlace, movedGalleryUrl,
  RECREATION_COLLECTION, RECREATION_MARKS, RECREATION_PLACE, TRAVEL_COLLECTION, TRAVEL_LOGO, TRAVEL_PLACE
} from './movedGalleryPlaces.js'

test('each department’s redirect names exactly its collection’s marks', () => {
  for (const [id, marks] of Object.entries(DEPARTMENTAL_MARKS)) {
    const collection = collectionById(id)
    assert.ok(collection, id)
    assert.equal(collection.id, id)
    assert.deepEqual(new Set(entriesOf(collection).map(({ id: mark }) => mark)), new Set(marks), id)
    // A bare mark link goes to its department only if no other collection holds the same mark.
    for (const mark of marks) {
      assert.deepEqual(GALLERY_COLLECTIONS.filter((other) => entriesOf(other).some((entry) => entry.id === mark)).map((other) => other.id), [id], mark)
    }
  }
  assert.deepEqual(new Set(entriesOf(collectionById(RECREATION_COLLECTION)).map(({ id }) => id)), RECREATION_MARKS)
})

test('the departments are no longer listed in the gallery, but their records still resolve', () => {
  const listed = new Set(gallerySections('').flatMap(({ collections }) => collections.map(({ id }) => id)))
  for (const id of DEPARTMENTAL_COLLECTIONS) {
    assert.ok(!listed.has(id), id)
    assert.equal(collectionById(id).shelf, 'departmental', id)
  }
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: 'bc-lands' }), departmentalPlace('bc-lands'))
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', mark: 'solutions-bc-2003-vector' }),
    departmentalPlace('collected-shared-services-bc', 'solutions-bc-2003-vector'))
})

test('the department’s shared marks stay with the museum and BC Parks', () => {
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

test('the Department of Travel Industry opens at its own address, as a department and as a mark', () => {
  assert.deepEqual(departmentalPlace(TRAVEL_COLLECTION), { view: 'internal', internal: 'travel-industry' })
  assert.deepEqual(TRAVEL_PLACE, { view: 'internal', internal: 'travel-industry', 'internal-logo': TRAVEL_LOGO })
  // The gallery's collection opens the department's page; its mark, wherever linked, the mark's.
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: TRAVEL_COLLECTION }), departmentalPlace(TRAVEL_COLLECTION))
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: TRAVEL_COLLECTION, mark: TRAVEL_LOGO }), TRAVEL_PLACE)
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: 'bc-mark', mark: TRAVEL_LOGO }), TRAVEL_PLACE)
  assert.deepEqual(movedGalleryPlace({ view: 'gallery', mark: TRAVEL_LOGO }), TRAVEL_PLACE)
  assert.equal(movedGalleryUrl('https://example.test/PofBC/?view=gallery&logos=specimens-travel-industry').search, '?view=internal&internal=travel-industry')
})

test('every department’s gallery links open its page in Departmental Logos', () => {
  for (const [id, marks] of Object.entries(DEPARTMENTAL_MARKS)) {
    assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: id }), departmentalPlace(id), id)
    for (const mark of marks) {
      assert.deepEqual(movedGalleryPlace({ view: 'gallery', logos: id, mark }), departmentalPlace(id, mark), mark)
      assert.deepEqual(movedGalleryPlace({ view: 'gallery', mark }), departmentalPlace(id, mark), mark)
    }
  }
})
