import assert from 'node:assert/strict'
import { test } from 'node:test'
import { collectionById, findGalleryEntry } from '../gallery/collections.js'
import { initiativeById, loadInitiative } from './initiatives.js'
import { initiativePlaceUrl, readInitiativePlace } from './initiativePlace.js'
import { searchInitiatives } from './initiativeModel.js'

test('Power Smart can be found and opened as an initiative with reciprocal artwork links', async () => {
  const entry = initiativeById('power-smart')
  assert.equal(searchInitiatives('BC Hydro PowerSmart', [entry])[0], entry)
  const url = initiativePlaceUrl('https://example.org/PofBC/?view=gallery', { initiative: entry.id })
  assert.equal(url.pathname, '/PofBC/')
  const detail = await loadInitiative(readInitiativePlace(url.href).initiative)
  assert.equal(detail.id, entry.id)
  const to = detail.relatedLinks[0].to
  assert.equal(collectionById(to.logos).initiativeId, detail.id)
  assert.equal(findGalleryEntry(to.mark).owner, 'power-smart')
  assert.equal(detail.relatedLinks[1].to.logos, 'bc-hydro')
  const sources = new Set(detail.sources.map(({ id }) => id))
  const timeline = detail.sections.find(({ type }) => type === 'timeline').records
  assert.deepEqual(timeline.map(({ date }) => date), ['1989', '2013-10-22', '2026-05'])
  assert.ok(timeline.every(({ sourceRefs }) => sourceRefs.every(({ sourceId }) => sources.has(sourceId))))
})
