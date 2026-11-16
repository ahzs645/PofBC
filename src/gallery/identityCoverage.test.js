import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  IDENTITY_COVERAGE, buildIdentityCoverage, coverageSummary, evidenceForEntries,
  filterIdentityCoverage, identitySubjectById, searchIdentitySubjects
} from './identityCoverage.js'
import { COLLECTING } from './collectingData.js'
import { GALLERY_COLLECTIONS, entriesOfNode } from './collections.js'

test('a successor vector, a charity mark and parent artwork never fill another subject’s gap', () => {
  const subjects = [
    { id: 'historic-authority', collectionIds: [], graphNode: 'historic-authority' },
    { id: 'current-operator', collectionIds: ['family'], graphNode: 'current-operator' },
    { id: 'charity', collectionIds: [], graphNode: null },
    { id: 'service', collectionIds: ['family'], graphNode: 'current-operator', sources: [{ url: 'https://example.org/service' }] }
  ]
  const collections = [{ id: 'family', graphNode: 'current-operator', entries: [
    { id: 'historic-scan', owner: 'historic-authority', asset: { isVector: false } },
    { id: 'operator-vector', owner: 'current-operator', asset: { isVector: true } },
    { id: 'charity-redraw', owner: 'charity', asset: { isVector: true, reconstruction: true } }
  ] }]
  const [historic, operator, charity, service] = buildIdentityCoverage(subjects, collections)
  assert.equal(historic.state, 'raster-held')
  assert.deepEqual(historic.entries.map((entry) => entry.id), ['historic-scan'])
  assert.equal(operator.state, 'native-vector')
  assert.equal(charity.state, 'reconstruction')
  assert.equal(service.state, 'source-located')
  assert.equal(service.hasArtwork, false)
  assert.deepEqual(service.collections, [])
})

test('source routes, shared identity and uncertainty are not counted as held artwork', () => {
  const subjects = [
    { id: 'source', sources: [{ url: 'https://example.org/media' }] },
    { id: 'shared', identityStatus: 'shared-identity', sources: [{ url: 'https://example.org/report' }] },
    { id: 'unconfirmed', identityStatus: 'distinct-unconfirmed', sources: [{ url: 'https://example.org/archive' }] },
    { id: 'known', graphNode: 'known' },
    { id: 'candidate' }
  ]
  const coverage = buildIdentityCoverage(subjects, [])
  assert.deepEqual(coverage.map((subject) => subject.state), ['source-located', 'shared-identity', 'distinct-unconfirmed', 'artwork-missing', 'not-catalogued'])
  assert.deepEqual(coverageSummary(coverage), { subjects: 5, held: 0, sources: 1, unresolved: 4 })
})

test('an SVG reconstruction is not a source vector; a real source variant retains its evidence', () => {
  assert.deepEqual(evidenceForEntries([
    { id: 'redraw', identity: { provenance: 'reconstructed' } },
    { id: 'wrapper', asset: { format: 'svg', isVector: false } },
    { id: 'variants', asset: { isVector: false }, versions: [{ isVector: false }, { isVector: true }] }
  ]), { vector: 1, raster: 1, reconstruction: 1, other: 0 })
})

test('the expanded register retains every earlier Crown and health target once', () => {
  const ids = new Set(IDENTITY_COVERAGE.map((subject) => subject.id))
  assert.equal(ids.size, IDENTITY_COVERAGE.length)
  for (const body of COLLECTING) assert.ok(ids.has(body.id), body.id)
  for (const subject of IDENTITY_COVERAGE) {
    for (const entry of subject.entries) {
      assert.ok(subject.collections.some((collection) => entriesOfNode(collection, subject.id).includes(entry)), `${subject.id}: ${entry.id}`)
    }
  }
})

test('historical transit specimens and BC Cancer keep their actual owners', () => {
  for (const id of ['bc-ferry-authority', 'urban-transit-authority']) {
    const subject = identitySubjectById(id)
    assert.ok(subject?.hasArtwork, id)
    assert.equal(subject.state, 'raster-held', id)
  }
  const cancer = identitySubjectById('sub-bc-cancer')
  assert.ok(cancer.hasArtwork)
  assert.ok(!cancer.entries.some((entry) => entry.owner === 'bc-cancer-foundation'))
  assert.ok(GALLERY_COLLECTIONS.some((collection) => entriesOfNode(collection, 'bc-cancer-foundation').length > 0), 'Foundation evidence remains in its existing family shelf')
})

test('aliases find the correct subject without treating an operator and service as the same identity', () => {
  const gvta = searchIdentitySubjects('GVTA').map((subject) => subject.id)
  assert.ok(gvta.includes('translink'))
  assert.ok(gvta.includes('metro-vancouver-transit-police'), 'the historic GVTA Police alias remains its own subject')
  assert.ok(!gvta.includes('british-columbia-rapid-transit-company'))
  assert.deepEqual(searchIdentitySubjects('BCRTC').map((subject) => subject.id), ['british-columbia-rapid-transit-company'])
  assert.ok(searchIdentitySubjects('Sea-Bus').some((subject) => subject.id === 'seabus'))
  assert.ok(!searchIdentitySubjects('SkyTrain').some((subject) => subject.id === 'translink'))
  assert.ok(filterIdentityCoverage(IDENTITY_COVERAGE, { family: 'transit', state: 'missing' }).every((subject) => !subject.hasArtwork && subject.family === 'transit'))
  assert.ok(filterIdentityCoverage(IDENTITY_COVERAGE, { scope: 'institution' }).length > 0)
  assert.ok(filterIdentityCoverage(IDENTITY_COVERAGE, { scope: 'institution' }).every((subject) => subject.scope === 'institution'))
})
