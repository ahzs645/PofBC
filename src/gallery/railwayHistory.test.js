import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { COLLECTED_BODIES } from './collectedData.js'
import { APPLICABILITY, collectionById, collectionOfNode, entriesOf, entriesOfNode, findGalleryEntry } from './collections.js'
import { RAILWAY_HISTORY } from './railwayHistoryData.js'

const root = new URL('../../', import.meta.url)
const railway = collectionById('collected-bc-railway-company')
const bodies = ['pacific-great-eastern-railway', 'bc-railway-company']

test('researched railway eras preserve the existing collection and individual artwork links', () => {
  assert.equal(collectionById('collected-pacific-great-eastern-railway'), railway)
  assert.equal(railway.railwayHistory, RAILWAY_HISTORY)
  for (const body of bodies) assert.equal(collectionOfNode(body), railway)
  for (const [id, owner] of [
    ['source-pacific-great-eastern-railway-pge-brochure-logo-png', bodies[0]],
    ['source-pacific-great-eastern-railway-pge-scenic-route-brochure-logo-png', bodies[0]],
    ['source-bc-railway-company-bc-railway-company-png', bodies[1]]
  ]) {
    const entry = findGalleryEntry(id)
    assert.ok(entry, id)
    assert.equal(entry.owner, owner, id)
    assert.ok(entriesOf(railway).includes(entry), id)
  }
})

test('every railway logo appears once, with its own owner, and design dates carry sources', () => {
  const entries = entriesOf(railway)
  // A design's other colourways are versions inside its entry, not entries of their own.
  const designs = (assets) => assets.filter((asset) => !asset.variantOf)
  const expected = designs(COLLECTED_BODIES.filter((body) => bodies.includes(body.id)).flatMap((body) => body.assets))
  assert.deepEqual(entries.map((entry) => entry.id).sort(), expected.map((asset) => asset.id).sort())
  assert.equal(new Set(entries.map((entry) => entry.id)).size, entries.length)
  for (const body of bodies) {
    const actual = entriesOfNode(railway, body).map((entry) => entry.id).sort()
    assert.deepEqual(actual, designs(COLLECTED_BODIES.find((record) => record.id === body).assets).map((asset) => asset.id).sort())
  }
  for (const era of railway.eras) {
    assert.equal(era.entries.length > 0, era.status === 'held', era.id)
    assert.ok(era.applicability.kind in APPLICABILITY, era.id)
    assert.ok(era.applicability.note && era.years && era.note, era.id)
    assert.ok(era.sources.length > 0, `${era.id}: no dating evidence`)
  }
})

test('corporate events and relationships retain their own dates and source evidence', () => {
  assert.ok(RAILWAY_HISTORY.events.length > 0)
  assert.ok(RAILWAY_HISTORY.connections.length > 0)
  for (const records of [RAILWAY_HISTORY.events, RAILWAY_HISTORY.connections]) {
    assert.equal(new Set(records.map((record) => record.id)).size, records.length)
    for (const record of records) {
      assert.ok(record.date && record.description, record.id)
      assert.ok(record.sources.length > 0, `${record.id}: no source`)
      for (const source of record.sources) {
        assert.ok(source.title, record.id)
        assert.match(source.url, /^https:\/\//, record.id)
      }
    }
  }
  for (const connection of RAILWAY_HISTORY.connections) {
    assert.ok(connection.from && connection.to && connection.relationship, connection.id)
  }
})

test('magazine reproductions retain their publication date and supporting images are not logo entries', () => {
  const entries = entriesOf(railway)
  const reproduced = entries.filter((entry) => entry.asset.sourceReproduction)
  assert.ok(reproduced.length > 0)
  for (const entry of reproduced) {
    assert.equal(entry.asset.sourceDate, '1991-01', entry.id)
    assert.equal(entry.identity.applicability.kind, 'dated_specimen', entry.id)
    assert.equal(entry.asset.isVector, false, entry.id)
    assert.match(entry.asset.sourceLocator, /page|p\./i, entry.id)
    assert.equal(entry.years, `${entry.asset.historicalDateLabel} · reproduced 1991-01`, entry.id)
    assert.equal(entry.identity.applicability.years, '1991-01', entry.id)
    assert.match(entry.identity.applicability.note, /publication reproducing/, entry.id)
  }
  assert.ok(RAILWAY_HISTORY.evidence.some((item) => item.role === 'decorative-context'))
  for (const item of RAILWAY_HISTORY.evidence) {
    assert.ok(!entries.some((entry) => entry.asset.file === item.file), `${item.id}: context counted as a logo`)
    assert.ok(existsSync(new URL(`public/${item.file}`, root)), item.id)
    assert.ok(item.caption && item.sourceLocator, item.id)
    assert.match(item.sourceUrl, /^https:\/\//, item.id)
  }
})
