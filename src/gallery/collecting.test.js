import { test } from 'node:test'
import assert from 'node:assert/strict'
import { COLLECTING } from './collectingData.js'
import { collectingFrom } from './collectingSource.js'
import { GALLERY_COLLECTIONS } from './collections.js'
import { CURRENT_BODIES } from '../government/currentData.js'
import { HISTORICAL_BODIES } from '../government/historyData.js'
import { governmentIn, PRESENT_YEAR } from '../government/snapshot.js'

test('the collecting list is the atlas’s, as last built (npm run build:collecting)', () => {
  assert.deepEqual(COLLECTING, collectingFrom(CURRENT_BODIES, HISTORICAL_BODIES))
})

test('it has every Crown corporation and health authority the diagram draws today, as today’s', () => {
  const today = governmentIn(PRESENT_YEAR).nodes.filter((node) => ['crown-corporation', 'health-authority'].includes(node.kind)).map((node) => node.id).sort()
  assert.deepEqual(COLLECTING.filter((body) => body.current).map((body) => body.id).sort(), today)
})

test('every collection of a Crown corporation or health authority leads from its body on the list', () => {
  const ids = new Set(COLLECTING.map((body) => body.id))
  for (const collection of GALLERY_COLLECTIONS) {
    if (!collection.graphNode || !ids.has(collection.graphNode)) continue
    assert.ok(COLLECTING.find((body) => body.id === collection.graphNode), collection.id)
  }
  // ICBC, BCLC, BC Transit and BC Ferries are collected, and found as such.
  for (const id of ['icbc', 'bclc', 'bc-transit', 'bc-ferry-corporation']) {
    assert.ok(GALLERY_COLLECTIONS.some((collection) => collection.graphNode === id), id)
  }
})
