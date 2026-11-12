import { test } from 'node:test'
import assert from 'node:assert/strict'
import { isSearchShortcut, searchGallery, wordsOf } from './gallerySearch.js'

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

test('the shortcut is Cmd-K or Ctrl-K, and nothing else', () => {
  assert.ok(isSearchShortcut({ metaKey: true, key: 'k' }))
  assert.ok(isSearchShortcut({ ctrlKey: true, key: 'K' }))
  assert.ok(!isSearchShortcut({ key: 'k' }))
  assert.ok(!isSearchShortcut({ metaKey: true, shiftKey: true, key: 'k' }))
  assert.ok(!isSearchShortcut({ ctrlKey: true, key: 'j' }))
})
