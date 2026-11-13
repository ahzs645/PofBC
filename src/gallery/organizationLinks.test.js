import { test } from 'node:test'
import assert from 'node:assert/strict'
import { collectionById, collectionOfNode, collectionsOfNode, entriesOf, entriesOfNode, findGalleryEntry } from './collections.js'
import { logosFor } from './galleryLogos.js'

test('organizations discover their own marks on shared gallery shelves in both directions', () => {
  for (const [node, ids] of [
    ['sub-workbc', ['work-bc']],
    ['sub-bc-stats', ['bc-stats']],
    ['sub-bc-wildfire-service', ['bc-wildfire-service', 'bc-wildfire-service-one-line']],
    ['sub-bc-coroners-service', ['coroners-service']],
    ['sub-bc-bid', ['bc-bid']],
    ['bc-public-service-agency', ['public-service']],
    ['sub-healthlink-bc', ['healthlink-bc-logo']]
  ]) {
    const collection = collectionOfNode(node)
    assert.equal(collection.id, 'bc-mark', node)
    assert.deepEqual(entriesOfNode(collection, node).map((entry) => entry.id).sort(), [...ids].sort(), node)
    for (const id of ids) assert.equal(findGalleryEntry(id).graphNode, node, id)
    const logos = logosFor(node)
    // The program's published originals are found beside its one-off, from their specimen collection.
    const originals = { 'sub-workbc': ['vector-workbc-2016', 'vector-workbc-current'], 'bc-public-service-agency': ['vector-bc-public-service-where-ideas-work-2023-reverse'] }[node] ?? []
    assert.deepEqual(logos.entries.map((entry) => entry.id).sort(), [...ids, ...originals].sort(), node)
    for (const entry of logos.entries) assert.ok(entriesOf(collectionById(entry.collection)).some((candidate) => candidate.id === entry.id))
  }
})

test('a body can discover dedicated history and shared-shelf artwork without changing its canonical collection', () => {
  const node = 'sub-bc-online'
  assert.equal(collectionOfNode(node).id, 'collected-sub-bc-online')
  assert.deepEqual(collectionsOfNode(node).map((collection) => collection.id), ['collected-sub-bc-online', 'bc-mark'])
  const logos = logosFor(node, 'light', 100)
  assert.ok(logos.entries.some((entry) => entry.id === 'bc-online' && entry.collection === 'bc-mark'))
  for (const entry of logos.entries) assert.ok(entriesOfNode(collectionById(entry.collection), node).some((candidate) => candidate.id === entry.id))
  assert.equal(collectionOfNode('not-a-body'), undefined)
  assert.equal(logosFor('not-a-body'), null)
})

test('Knowledge Network uses its held SVG colourway while retaining the design download and deep link', () => {
  const id = 'source-knowledge-network-knowledge-network-colour-eps'
  const entry = findGalleryEntry(id)
  assert.equal(entry.asset.format, 'eps')
  for (const theme of ['light', 'dark']) {
    const logos = logosFor('knowledge-network', theme)
    assert.equal(logos.total, 1)
    assert.equal(logos.entries[0].id, id)
    assert.match(logos.entries[0].html, new RegExp(`identity-display/source-knowledge-network-knowledge-network-svg\\.${theme}\\.svg`))
  }
  assert.equal(entry.asset.format, 'eps', 'thumbnail selection must not mutate gallery downloads')
})

test('the Cancer Foundation keeps its own ownership within the shared visual family', () => {
  const collection = collectionById('collected-sub-bc-cancer')
  for (const id of ['bc-cancer-foundation-2018', 'bc-cancer-foundation-2026']) {
    const entry = findGalleryEntry(id)
    assert.ok(entriesOf(collection).includes(entry), id)
    assert.equal(entry.owner, 'bc-cancer-foundation', id)
    assert.ok(!entriesOfNode(collection, 'sub-bc-cancer').includes(entry), id)
    assert.ok(!entry.graphNode, 'the Foundation is not a provincial-government node')
  }
  assert.ok(entriesOfNode(collection, 'sub-bc-cancer').some((entry) => entry.id === 'bc-cancer-phsa'))
})

test('a body panel finds the original specimens of the program its one-off stands for', async () => {
  const { collectionsOfNode, entriesOfNode } = await import('./collections.js')
  const held = (node) => collectionsOfNode(node).flatMap((collection) => entriesOfNode(collection, node)).map((entry) => entry.id)
  assert.ok(['vector-workbc-2016', 'vector-workbc-current'].every((id) => held('sub-workbc').includes(id)))
  assert.ok(held('bc-public-service-agency').includes('vector-bc-public-service-where-ideas-work-2023-reverse'))
  const prepared = collectionsOfNode('sub-preparedbc').flatMap((collection) => entriesOfNode(collection, 'sub-preparedbc'))
  assert.deepEqual(prepared.map((entry) => entry.id), ['prepared-bc'])
  // Linking it does not make the remake read as the program's own lockup.
  assert.equal(prepared[0].identity.provenance, 'synthetic_name_variant')
})
