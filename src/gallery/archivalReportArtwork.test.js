import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { collectionById, entriesOf, findGalleryEntry } from './collections.js'

test('the 2004 LWBC design opens its handbook vector and retains both prior versions', () => {
  const entry = findGalleryEntry('land-and-water-bc-2004-rebuilt')
  assert.equal(entry.asset.id, 'lwbc-handbook-2004-black')
  assert.equal(entry.asset.sourceDate, '2004-06')
  assert.ok(entry.versions.some((asset) => asset.reconstruction))
  assert.ok(entry.versions.some((asset) => asset.format === 'png'))
})

test('the 2014 retrospective designs belong to their respective institutions', () => {
  for (const [owner, id] of [
    ['university-college-of-the-fraser-valley', 'ucfv-initials-white-2014'],
    ['university-of-the-fraser-valley', 'ufv-wave-wordmark-white-2014'],
    ['university-of-the-fraser-valley', 'ufv-40-years-2014'],
  ]) {
    const collection = collectionById('collected-' + owner)
    const entry = entriesOf(collection).find((item) => item.id === id)
    assert.equal(entry.asset.role, 'historical')
    assert.equal(entry.asset.sourceDate, '2014')
    assert.equal(entry.asset.sourceGround, 'dark')
    if (owner === 'university-of-the-fraser-valley') assert.notEqual(collection.cover, id)
  }
})

test('archival source downloads are native outlined SVGs with the recorded checksums', () => {
  for (const id of ['lwbc-handbook-2004-black', 'ucfv-initials-white-2014', 'ufv-wave-wordmark-white-2014', 'ufv-40-years-2014']) {
    const { asset } = findGalleryEntry(id)
    const bytes = readFileSync(new URL('../../public/' + asset.file, import.meta.url))
    assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256)
    assert.match(bytes.toString(), /<path\b/)
    assert.doesNotMatch(bytes.toString(), /<(image|text|foreignObject|script)\b/)
  }
})
