import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, existsSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { COLLECTING } from './collectingData.js'
import { COLLECTED_BODIES } from './collectedData.js'
import { COLLECTED_COLLECTIONS, CONTINUATIONS, assetUrl, nodesOf, researchLabel } from './collectedCollections.js'
import { GALLERY_COLLECTIONS, collectionById, collectionOfNode, entriesOf, entriesOfNode } from './collections.js'
import { HISTORICAL_BODIES } from '../government/historyData.js'

const root = new URL('../../', import.meta.url)

test('every requested body is accounted for without inventing collected artwork', () => {
  assert.deepEqual(COLLECTED_BODIES.map((body) => body.id).sort(), COLLECTING.map((body) => body.id).sort())
  assert.equal(new Set(COLLECTED_BODIES.map((body) => body.id)).size, COLLECTED_BODIES.length)
  for (const body of COLLECTED_BODIES) {
    if (body.status !== 'asset-collected') assert.equal(body.assets.length, 0, body.id)
    if (body.assets.length) {
      const collection = collectionOfNode(body.id)
      assert.ok(collection, body.id)
      // Every file of the body is in the collection that holds it, under that body.
      const shown = new Set(entriesOfNode(collection, body.id).map((entry) => entry.id))
      for (const asset of body.assets) assert.ok(shown.has(asset.id), `${body.id}: ${asset.id}`)
    }
  }
})

test('files are local and match their recorded source checksums', () => {
  for (const body of COLLECTED_BODIES) for (const asset of body.assets) {
    assert.match(asset.file, /^identity-collected\/[a-z0-9._/-]+$/)
    assert.ok(!asset.file.includes('..'), asset.file)
    const data = readFileSync(new URL(`public/${asset.file}`, root))
    assert.equal(createHash('sha256').update(data).digest('hex'), asset.sha256, asset.file)
    if (asset.preview) assert.ok(existsSync(new URL(`public/${asset.preview}`, root)), asset.preview)
    assert.ok(asset.supplied || /^https:\/\//.test(asset.sourcePage || asset.sourceUrl), asset.id)
    assert.ok(asset.fidelityNote && asset.publisher && asset.observedDate, asset.id)
  }
})

test('a raster wrapper is never described as pure vector and source files have no active content', () => {
  for (const body of COLLECTED_BODIES) for (const asset of body.assets) {
    if (asset.format !== 'svg') continue
    const svg = readFileSync(new URL(`public/${asset.file}`, root), 'utf8')
    assert.doesNotMatch(svg, /<(?:script|foreignObject)\b|\son[a-z]+\s*=/i, asset.file)
    if (/<(?:\w+:)?image\b/i.test(svg)) assert.equal(asset.isVector, false, asset.id)
  }
})

test('collected entries date sightings rather than claiming logo adoption', () => {
  const entries = COLLECTED_COLLECTIONS.flatMap(entriesOf)
  assert.ok(entries.length > 0)
  for (const entry of entries) {
    assert.equal(entry.kind, 'collected')
    assert.ok(['unknown', 'dated_specimen'].includes(entry.identity.applicability.kind), entry.id)
    if (entry.asset.reconstruction) assert.equal(entry.identity.provenance,
      entry.asset.reconstructionBy === 'project' ? 'reconstructed' : 'third_party_reconstruction')
    if (entry.asset.supplied && !entry.asset.sourceDate) assert.equal(entry.identity.applicability.kind, 'unknown')
  }
})

test('asset links respect both root and project deployments; leads stay uncollected', () => {
  assert.equal(assetUrl('identity-collected/example.svg', '/PofBC/'), '/PofBC/identity-collected/example.svg')
  assert.equal(assetUrl('identity-collected/example.svg', '/'), '/identity-collected/example.svg')
  assert.equal(researchLabel({ status: 'source-found' }), 'Source located · artwork wanted')
  assert.equal(researchLabel({ status: 'unresolved' }), 'Wanted · searched')
  assert.equal(researchLabel({ status: 'not-searched' }), 'Wanted')
})

test('BC Place keeps its archival deep link beside separately identified project reconstructions', () => {
  const collection = collectionById('collected-bc-place-ltd')
  assert.ok(collection)
  const entries = entriesOf(collection)
  const original = entries.find((entry) => entry.id === 'source-bc-place-ltd-bc-place-1983-logo-png')
  assert.ok(original, 'the existing gallery deep link still resolves')
  assert.equal(original.asset.file, 'identity-collected/bc-place-ltd/bc-place-1983-logo.png')
  assert.equal(original.asset.sha256, '81f8e81394f8682fb210e8dc99f6b40e4b22fda5a046f7b0e7753e7bcee4785e')
  assert.equal(original.identity.provenance, 'published_raster')

  const redraws = entries.filter((entry) => entry.asset.reconstructionBy === 'project')
  for (const file of ['bc-place-1982-monogram-reconstruction.svg', 'bc-place-1982-lockup-reconstruction.svg']) {
    assert.ok(redraws.some((entry) => entry.asset.file === `identity-collected/bc-place-ltd/${file}`), file)
  }
  for (const entry of redraws) {
    assert.equal(entry.asset.reconstruction, true, entry.id)
    assert.equal(entry.identity.provenance, 'reconstructed', entry.id)
    assert.equal(entry.identity.applicability.kind, 'dated_specimen', entry.id)
    assert.match(entry.identity.applicability.note, /not a verified first use or adoption date/, entry.id)
    assert.match(entry.asset.sourceDate, /1982/, entry.id)
    assert.ok(/^https:\/\//.test(entry.asset.sourcePage || entry.asset.sourceUrl), entry.id)
    const svg = readFileSync(new URL(`public/${entry.asset.file}`, root), 'utf8')
    assert.match(svg, /<(?:path|circle|ellipse|rect|polygon|polyline)\b/, entry.id)
    assert.doesNotMatch(svg, /<(?:\w+:)?(?:image|text|foreignObject)\b|(?:href|src)=["'](?:https?:|data:)/i, entry.id)
  }
})

test('a body folded into a later name is a one-to-one line in the government history', () => {
  const history = new Map(HISTORICAL_BODIES.map((body) => [body.id, body]))
  const held = new Set(COLLECTED_BODIES.filter((body) => body.assets.length).map((body) => body.id))
  const folded = [...CONTINUATIONS, ...GALLERY_COLLECTIONS.filter((collection) => collection.eras && collection.graphNodes)
    .flatMap((collection) => collection.graphNodes.slice(1).map((node) => [node, null]))]
  for (const [from, to] of folded) {
    const became = history.get(from)?.became
    assert.ok(became, `${from} became something`)
    if (to) assert.equal(became, to, from)
    // Many to one: no other body with logos here became the same one — that is an amalgamation.
    const others = HISTORICAL_BODIES.filter((body) => body.became === became && body.id !== from && held.has(body.id))
    assert.deepEqual(others.map((body) => body.id), [], from)
    // One to many: nothing else counts this body among its predecessors, nor took its services over.
    const heirs = HISTORICAL_BODIES.filter((body) => body.id !== became && body.predecessors?.includes(from))
    assert.deepEqual(heirs.map((body) => body.id), [], from)
    assert.ok(!(history.get(from).servicesPassedTo ?? []).some((id) => id !== became), from)
  }
})

test('a link to a folded body’s old collection opens the collection that holds it now', () => {
  for (const collection of GALLERY_COLLECTIONS) for (const alias of collection.aliases ?? []) {
    assert.equal(collectionById(alias), collection, alias)
    assert.ok(!GALLERY_COLLECTIONS.some((other) => other.id === alias), alias)
  }
  for (const collection of GALLERY_COLLECTIONS) assert.equal(new Set(nodesOf(collection)).size, nodesOf(collection).length)
  const nodes = GALLERY_COLLECTIONS.flatMap(nodesOf)
  assert.equal(new Set(nodes).size, nodes.length, 'each body is held by one collection')
})
