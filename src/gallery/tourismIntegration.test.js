import { test } from 'node:test'
import assert from 'node:assert/strict'
import { HISTORICAL_BODIES } from '../government/historyData.js'
import { CONTINUATIONS, collectedEntriesOf, nodesOf } from './collectedCollections.js'
import { GALLERY_COLLECTIONS, collectionById, collectionOfNode, entriesOfNode } from './collections.js'

const tourismIds = ['tourism-bc', 'destination-bc']
const collectionId = 'tourism-bc-destination-bc'

test('both legacy tourism collection links resolve to the combined collection', () => {
  const collection = collectionById(collectionId)
  assert.equal(collection?.initiativeId, 'tourism')
  for (const id of tourismIds) {
    assert.equal(collectionById(`collected-${id}`), collection)
    assert.ok(!GALLERY_COLLECTIONS.some((each) => each.id === `collected-${id}`), `${id} has no duplicate shelf`)
  }
  assert.equal(GALLERY_COLLECTIONS.filter((each) => each.id === collectionId).length, 1)
})

test('the shared tourism collection preserves each graph node and its own artwork', () => {
  const collection = collectionById(collectionId)
  assert.deepEqual(nodesOf(collection), tourismIds)
  const artworkByNode = []
  for (const id of tourismIds) {
    assert.equal(HISTORICAL_BODIES.filter((body) => body.id === id).length, 1, `${id} remains a separate graph node`)
    assert.equal(collectionOfNode(id), collection, `${id} opens the connected collection`)
    const entries = entriesOfNode(collection, id)
    assert.ok(entries.length > 0, `${id} retains artwork`)
    assert.ok(entries.every((entry) => entry.owner === id), `${id} retains artwork ownership`)
    assert.deepEqual(entries.map((entry) => entry.id).sort(), collectedEntriesOf(id).map((entry) => entry.id).sort())
    artworkByNode.push(new Set(entries.map((entry) => entry.id)))
  }
  assert.ok([...artworkByNode[0]].every((id) => !artworkByNode[1].has(id)), 'the two bodies do not acquire each other’s artwork')
})

test('shared tourism material does not introduce a legal rename continuation', () => {
  assert.ok(!CONTINUATIONS.some((pair) => pair.some((id) => tourismIds.includes(id))))
  const tourism = HISTORICAL_BODIES.find((body) => body.id === 'tourism-bc')
  const destination = HISTORICAL_BODIES.find((body) => body.id === 'destination-bc')
  assert.notEqual(tourism, destination)
  assert.equal(tourism.ended, '2010-04-01')
  assert.equal(destination.established, '2012-11-02')
  assert.equal(tourism.became, null)
  assert.equal(destination.became, null)
})
