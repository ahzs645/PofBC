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

test('post-secondary coverage counts subjects once, not their variants or visible links', async () => {
  const { IDENTITY_COVERAGE, identitySubjectById, searchIdentitySubjects } = await import('./identityCoverage.js')
  const { POSTSECONDARY_ARTWORK_FORMAT, POSTSECONDARY_ARTWORK_SCOPE, summarizePostsecondaryArtwork } = await import('./postsecondaryArtwork.js')
  const { default: ledger } = await import('../../research/identity/postsecondary-2026-11-24/artwork-coverage-evidence.json', { with: { type: 'json' } })
  const subjects = IDENTITY_COVERAGE.filter((subject) => subject.family === 'postsecondary-history')
  const counts = summarizePostsecondaryArtwork(subjects)
  assert.equal(counts.total, 49)
  assert.equal(counts.total, counts.vector + counts.observedNonvector + counts.unverified)
  assert.deepEqual(counts, { total: 49, held: 0, vector: 24, observedNonvector: 7, unverified: 18, shared: 1 })
  assert.deepEqual(summarizePostsecondaryArtwork(subjects.filter((subject) => subject.priority === 1 && subject.kind === 'public-college')),
    { total: 11, held: 0, vector: 11, observedNonvector: 0, unverified: 0, shared: 0 })

  const ids = subjects.flatMap(({ artworkReview }) => artworkReview.specimens.map(({ id }) => id))
  assert.equal(ids.length, new Set(ids).size)
  for (const item of ledger.specimens) {
    assert.ok(subjects.some(({ id }) => id === item.subjectId), item.id)
    assert.equal(item.evidence, 'source-only')
    assert.ok(POSTSECONDARY_ARTWORK_FORMAT[item.format] && POSTSECONDARY_ARTWORK_SCOPE[item.scope], item.id)
    assert.ok(item.publisher && item.label && item.locator, item.id)
    assert.equal(new URL(item.url).protocol, 'https:')
    if (item.sha256) assert.match(item.sha256, /^[a-f0-9]{64}$/)
  }
  const campus = identitySubjectById('ubc-okanagan-campus')
  assert.equal(campus.state, 'shared-identity')
  assert.equal(campus.artworkReview.shared.targetSubjectId, 'university-of-british-columbia')
  assert.ok(campus.artworkReview.specimens.some(({ format, scope }) => format === 'native-vector' && scope === 'campus'))
  assert.ok(!campus.hasArtwork && campus.entries.length === 0)

  const [school] = searchIdentitySubjects('Vancouver School of Decorative and Applied Arts', subjects)
  assert.equal(school.id, 'vancouver-school-of-art')
  assert.equal(school.state, 'distinct-unconfirmed')
  assert.equal(school.artworkReview.specimens[0].scope, 'cover-art')
  assert.ok(subjects.every(({ hasArtwork }) => !hasArtwork))
})


test('a held reconstruction and a shared vector do not inflate original artwork counts', async () => {
  const { summarizePostsecondaryArtwork } = await import('./postsecondaryArtwork.js')
  const original = { format: 'native-vector', scope: 'institutional' }
  const suppressed = { format: 'raster-source', scope: 'cover-art' }
  const result = summarizePostsecondaryArtwork([
    { hasArtwork: true, evidence: { reconstruction: 1 }, artworkReview: { specimens: [suppressed] } },
    { hasArtwork: false, artworkReview: { specimens: [original, original] } },
    { hasArtwork: false, artworkReview: { shared: { targetSubjectId: 'university' }, specimens: [{ ...original, scope: 'campus' }] } }
  ])
  assert.deepEqual(result, { total: 3, held: 1, vector: 1, observedNonvector: 0, unverified: 2, shared: 1 })
})
