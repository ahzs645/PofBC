import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, existsSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { COLLECTING } from './collectingData.js'
import { COLLECTED_BODIES } from './collectedData.js'
import { COLLECTED_COLLECTIONS, assetUrl, researchLabel } from './collectedCollections.js'
import { GALLERY_COLLECTIONS, entriesOf } from './collections.js'

const root = new URL('../../', import.meta.url)

test('every requested body is accounted for without inventing collected artwork', () => {
  assert.deepEqual(COLLECTED_BODIES.map((body) => body.id).sort(), COLLECTING.map((body) => body.id).sort())
  assert.equal(new Set(COLLECTED_BODIES.map((body) => body.id)).size, COLLECTED_BODIES.length)
  for (const body of COLLECTED_BODIES) {
    if (body.status !== 'asset-collected') assert.equal(body.assets.length, 0, body.id)
    if (body.assets.length) assert.ok(GALLERY_COLLECTIONS.some((collection) => collection.graphNode === body.id), body.id)
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
    if (entry.asset.reconstruction) assert.equal(entry.identity.provenance, 'third_party_reconstruction')
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
