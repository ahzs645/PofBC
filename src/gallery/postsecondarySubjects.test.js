import { test } from 'node:test'
import assert from 'node:assert/strict'
import registry from '../../research/identity/postsecondary-2026-11-24/source-register.json' with { type: 'json' }
import { POSTSECONDARY_SUBJECTS } from './postsecondarySubjects.js'

test('all eleven public colleges have source leads without assuming held artwork', () => {
  const colleges = registry.records.filter(r => r.current && r.kind === 'public-college')
  assert.equal(colleges.length, 11)
  assert.ok(colleges.every(r => r.artworkCandidates.length))
  assert.equal(new Set(registry.records.map(r => r.id)).size, registry.records.length)
  const candidates = registry.records.flatMap(r => r.artworkCandidates)
  assert.equal(new Set(candidates.map(a => a.id)).size, candidates.length)
  assert.ok(candidates.every(a => a.sourceUrl.startsWith('https://') && a.sourcePage.startsWith('https://')))
  assert.ok(POSTSECONDARY_SUBJECTS.every(s => s.graphNode === null && s.collectionIds.length === 0))
})

test('splits, amalgamations and operations transfers are not one-to-one renames', () => {
  const byId = new Map(POSTSECONDARY_SUBJECTS.map(s => [s.id, s]))
  const targets = (id, type) => byId.get(id).relations.filter(r => r.type === type).map(r => r.subject)
  assert.deepEqual(targets('okanagan-university-college', 'split-into'), ['okanagan-college', 'ubc-okanagan-campus'])
  assert.deepEqual(targets('kwantlen-college', 'split-from'), ['douglas-college'])
  assert.deepEqual(targets('langara-college', 'split-from'), ['vancouver-community-college'])
  assert.deepEqual(targets('bc-vocational-school-prince-george', 'amalgamated-into'), ['college-of-new-caledonia'])
  assert.deepEqual(targets('bc-open-university', 'transferred-operations-to'), ['thompson-rivers-university'])
  assert.deepEqual(targets('royal-roads-military-college', 'site-succeeded-by'), ['royal-roads-university'])
  assert.equal(targets('royal-roads-military-college', 'renamed-to').length, 0)
})

test('review-only PDF specimens have precise provenance and do not become gallery holdings', async () => {
  const { default: review } = await import('../../research/identity/postsecondary-2026-11-24/artwork-review-candidates.json', { with: { type: 'json' } })
  const { POSTSECONDARY_IDENTITY_BODIES } = await import('./postsecondaryIdentityData.js')
  const subjectIds = new Set(registry.records.map(record => record.id))
  const importableIds = new Set(registry.records.flatMap(record => record.artworkCandidates.map(candidate => candidate.id)))
  const displayedIds = new Set(POSTSECONDARY_IDENTITY_BODIES.flatMap(body => body.assets.map(asset => asset.id)))
  const docs = review.documents
  const sha256 = /^[0-9a-f]{64}$/
  const kinds = { embedded: 0, vector: 0 }
  assert.equal(Object.keys(docs).length, 5)
  assert.equal(new Set(review.candidates.map(candidate => candidate.id)).size, review.candidates.length)
  for (const candidate of review.candidates) {
    const { extraction, id } = candidate
    assert.ok(subjectIds.has(candidate.subjectId), id)
    assert.equal(candidate.reviewStatus, 'source-only')
    assert.ok(!importableIds.has(id) && !displayedIds.has(id), id)
    assert.ok(Number.isInteger(candidate.pdfPage) && candidate.pdfPage > 0, id)
    assert.ok(docs[candidate.document]?.url.startsWith('https://'), id)
    assert.match(docs[candidate.document].sourceSha256, sha256)
    assert.ok(docs[candidate.document].rightsNote, id)
    if (extraction.type === 'embedded-image') {
      assert.ok([extraction.objectNumber, extraction.width, extraction.height].every(value => Number.isInteger(value) && value > 0), id)
      assert.match(extraction.extractedSha256, sha256)
      kinds.embedded++
    } else {
      assert.equal(extraction.type, 'native-vector-region')
      const [x0, y0, x1, y1] = extraction.rectPt
      assert.ok([x0, y0, x1, y1].every(Number.isFinite) && x1 > x0 && y1 > y0, id)
      kinds.vector++
    }
  }
  assert.deepEqual(kinds, { embedded: 7, vector: 6 })
})
