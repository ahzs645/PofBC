import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, existsSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { COLLECTING } from './collectingData.js'
import { COLLECTED_BODIES } from './collectedData.js'
import { COLLECTED_COLLECTIONS, CONTINUATIONS, assetUrl, collectedEntriesOf, nodesOf, parseSpecimenDate, researchLabel } from './collectedCollections.js'
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
      const shown = new Set(entriesOfNode(collection, body.id).flatMap((entry) => (entry.versions ?? [entry.asset ?? entry]).map((each) => each.id)))
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
    if (entry.asset.reconstruction) assert.equal(entry.identity.provenance, 'third_party_reconstruction')
    // A supplied file is dated only by the sightings of its design it stands for.
    if (entry.asset.supplied && !entry.asset.sourceDate && !entry.asset.alsoSeen?.length) assert.equal(entry.identity.applicability.kind, 'unknown')
  }
})

test('an event year mentioned inside an undated report cannot date its logo', () => {
  const entries = collectedEntriesOf('bc-housing').filter((entry) => entry.asset.sourceDate?.startsWith('Undated report describing April 2019'))
  assert.equal(entries.length, 2, 'both BC Housing specimens remain covered by the regression')
  for (const entry of entries) {
    assert.equal(entry.years, 'Logo dates unestablished', entry.id)
    assert.equal(entry.identity.applicability.kind, 'unknown', entry.id)
    assert.equal(entry.identity.applicability.years, 'undated', entry.id)
    assert.match(entry.identity.applicability.note, /does not establish a dated specimen/)
    assert.doesNotMatch(entry.identity.applicability.note, /This is the date of the cited specimen/)
  }
})

test('specimen dates retain precision and fiscal boundaries without extracting years from prose', () => {
  const cases = [
    ['2017', 2017, 2017], ['2017-11', 2017, 2017], ['2017-11-15', 2017, 2017],
    ['1982/83', 1982, 1983], ['1999/00', 1999, 2000], ['2012/2013', 2012, 2013],
    ['FY2025/26', 2025, 2026], ['2000–2001', 2000, 2001], ['2023-2026', 2023, 2026],
    ['March 1999', 1999, 1999], ['April–May 2001', 2001, 2001], ['Spring 2000', 2000, 2000],
    ['c. 1970', 1970, 1970], ['about 1970', 1970, 1970]
  ]
  for (const [label, firstYear, lastYear] of cases) {
    assert.deepEqual(parseSpecimenDate(label), { label, firstYear, lastYear }, label)
  }
  for (const prose of ['Events in 2019', '2009 service plan update', '2014 annual report, published 2015',
    '2023–2026 accessibility plan', 'URL uploaded 2023/05', 'Undated report describing April 2019 events; no adoption date inferred']) {
    assert.equal(parseSpecimenDate(prose), null, prose)
  }
  for (const invalid of ['2023-13', '2023-02-29', '2023-04-31', '2000/99', '2026–2023', null, undefined]) {
    assert.equal(parseSpecimenDate(invalid), null, String(invalid))
  }
})

test('BCEC asset transfers do not fold its logos into PavCo as a former name', () => {
  const bcec = collectionById('collected-bc-enterprise-corporation')
  const pavco = collectionById('collected-bc-pavilion-corporation')
  const place = collectionById('collected-bc-place-ltd')
  assert.ok(bcec && pavco && place)
  assert.notEqual(bcec, pavco)
  assert.notEqual(place, pavco)
  assert.deepEqual(nodesOf(bcec), ['bc-enterprise-corporation'])
  assert.deepEqual(nodesOf(pavco), ['bc-pavilion-corporation'])
  assert.ok(!CONTINUATIONS.some(([from, to]) => from === 'bc-enterprise-corporation' && to === 'bc-pavilion-corporation'))
})

test('asset links respect both root and project deployments; leads stay uncollected', () => {
  assert.equal(assetUrl('identity-collected/example.svg', '/PofBC/'), '/PofBC/identity-collected/example.svg')
  assert.equal(assetUrl('identity-collected/example.svg', '/'), '/identity-collected/example.svg')
  assert.equal(researchLabel({ status: 'source-found' }), 'Source located · artwork wanted')
  assert.equal(researchLabel({ status: 'unresolved' }), 'Wanted · searched')
  assert.equal(researchLabel({ status: 'not-searched' }), 'Wanted')
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
