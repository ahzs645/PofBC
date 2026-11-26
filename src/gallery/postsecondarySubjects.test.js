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
  assert.deepEqual(counts, { total: 49, held: 0, vector: 28, observedNonvector: 7, unverified: 14, shared: 1 })
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

test('CNC identity history distinguishes designation, arms and three dated specimens without counting arms as a logo', async () => {
  const { identitySubjectById } = await import('./identityCoverage.js')
  const { isLogoSource, summarizePostsecondaryArtwork } = await import('./postsecondaryArtwork.js')
  const cnc = identitySubjectById('college-of-new-caledonia')
  const { history, specimens } = cnc.artworkReview
  assert.deepEqual(history.map(({ type, date }) => [type, date]), [
    ['legal', '1978-12-01'], ['heraldic-grant', '1996-06-04'], ['logo-specimen', '2017-07'], ['logo-specimen', '2019'], ['logo-specimen', '2026']
  ])
  assert.match(history[0].url, /\/2960_1978$/)
  const historySpecimens = history.slice(1).map(({ specimenId }) => specimens.find(({ id }) => id === specimenId))
  assert.ok(historySpecimens.every((item) => item?.evidence === 'source-only'))
  assert.deepEqual(historySpecimens.map(isLogoSource), [false, true, true, true])
  assert.match(historySpecimens[0].url, /\/project\/616$/)
  assert.match(historySpecimens[0].note, /March 24, 2001/)
  assert.ok(historySpecimens.slice(1).every(({ format }) => format === 'native-vector'))
  assert.deepEqual(historySpecimens.slice(1).map(({ id, scope }) => [id, scope]), [
    ['cnc-2017-geometric-monogram', 'historical'],
    ['cnc-2019-fullname-variant', 'institutional'],
    ['official-college-of-new-caledonia-vector', 'institutional']
  ])
  const hrefs = [history[0].url, ...historySpecimens.map(({ url }) => url)]
  assert.equal(hrefs.length, new Set(hrefs).size)
  assert.ok(cnc.sources.every(({ url }) => !hrefs.includes(url)))
  assert.ok(!cnc.hasArtwork && cnc.entries.length === 0)
  assert.deepEqual(summarizePostsecondaryArtwork([{ artworkReview: { specimens: [historySpecimens[0]] } }]),
    { total: 1, held: 0, vector: 0, observedNonvector: 0, unverified: 1, shared: 0 })
})

test('BCIT extends its existing subject, not the 49-record family or the held website mark', async () => {
  const { identitySubjectById } = await import('./identityCoverage.js')
  const { isLogoSource } = await import('./postsecondaryArtwork.js')
  const { default: receipt } = await import('../../research/identity/postsecondary-2026-11-24/bcit-2007-extraction-receipt.json', { with: { type: 'json' } })
  const bcit = identitySubjectById('bcit')
  assert.equal(bcit.family, 'institutions')
  assert.ok(!POSTSECONDARY_SUBJECTS.some(({ id }) => id === 'bcit'))
  assert.deepEqual(bcit.entries.map(({ id }) => id), ['source-expanded-bcit-website-logo'])
  const { history, specimens } = bcit.artworkReview
  assert.deepEqual(history.map(({ date }) => date), [
    '1964', '1978', '1984-09-14', '1986', '1993-02-22', '1996-02-29', '2007-06-29', '2007-06-29', '2017'
  ])
  assert.deepEqual(history.map(({ specimenId }) => specimenId), specimens.map(({ id }) => id))
  assert.ok(specimens.every(({ evidence }) => evidence === 'source-only'))
  assert.deepEqual(specimens.slice(0, 2).map(({ format }) => format), ['raster-source', 'raster-source'])
  assert.equal(specimens.filter(({ note }) => /research reconstruction/.test(note)).length, 2)
  assert.deepEqual(specimens.filter((item) => !isLogoSource(item)).map(({ scope }) => scope), ['campaign', 'heraldry'])
  assert.match(specimens.find(({ scope }) => scope === 'heraldry').note, /November 23, 1996/)
  const vectors = specimens.filter(({ format }) => format === 'native-vector')
  assert.deepEqual(vectors.map(({ id }) => id), receipt.variants.map(({ specimenId }) => specimenId))
  assert.equal(receipt.status, 'source-only')
  assert.equal(receipt.physicalPdfPage, 1)
  assert.equal(receipt.printedPage, 12)
  assert.ok(vectors.every(({ url, sha256 }) => url === receipt.sourceUrl && sha256 === receipt.sourceSha256))
  assert.deepEqual(receipt.variants.map(({ outlinedSourceGlyphs }) => outlinedSourceGlyphs), [0, 36])
  assert.ok(receipt.variants.every(({ filteredPdfMatchesOriginalCropAt8x, svgThresholdedInkIoUAt8x }) =>
    filteredPdfMatchesOriginalCropAt8x && svgThresholdedInkIoUAt8x > 0.97))
})


test('early Kwantlen previews link to documented vector evidence for their own name era', async () => {
  const { identitySubjectById } = await import('./identityCoverage.js')
  const { EDITORIAL_LOGO_SPECIMENS } = await import('./editorialLogoSpecimens.js')
  for (const id of ['kwantlen-college', 'kwantlen-university-college']) {
    const subject = identitySubjectById(id)
    const [preview] = EDITORIAL_LOGO_SPECIMENS[id]
    const source = subject.artworkReview.specimens.find(({ id }) => id === preview.id)
    assert.equal(source.url, preview.url)
    assert.equal(source.format, 'native-vector')
    assert.equal(source.evidence, 'source-only')
    assert.equal(subject.hasArtwork, false)
  }
})

test('recovered historical previews reference matching sources without becoming artwork holdings', async () => {
  const { identitySubjectById } = await import('./identityCoverage.js')
  const { EDITORIAL_LOGO_SPECIMENS } = await import('./editorialLogoSpecimens.js')
  const selected = {
    'emily-carr-institute-of-art-and-design': ['ecuad-2002-curved-banner', 'ecuad-2004-framed-one-line'],
    'emily-carr-university': ['ecuad-2009-horizontal-wire', 'ecuad-2018-stacked-wire'],
    'capilano-college': ['capilano-2007-wordmark', 'capilano-2007-two-books'],
    'capilano-university': ['capilano-2008-wordmark', 'capilano-2009-curved-emblem'],
    'kootenay-school-of-the-arts': ['ksa-2004-cooperative', 'ksa-2009-may-selkirk-era', 'ksa-2009-august-selkirk-era'],
    'east-kootenay-community-college': ['ekcc-1988-recruitment'],
    'college-of-the-rockies': ['cotr-2006-monochrome', 'cotr-2016-old-letterhead'],
    'pacific-vocational-institute': ['pvi-1980-81-directory']
  }
  for (const [id, ids] of Object.entries(selected)) {
    const subject = identitySubjectById(id)
    const previews = EDITORIAL_LOGO_SPECIMENS[id]
    assert.deepEqual(previews.map(({ id }) => id), ids)
    assert.equal(subject.hasArtwork, false)
    for (const { id, url } of previews) {
      assert.ok(subject.artworkReview.specimens.some((s) =>
        s.id === id && s.url === url && s.evidence === 'source-only' && s.scope === 'historical'), id)
    }
    for (const event of subject.artworkReview.history) {
      if (event.specimenId) assert.ok(subject.artworkReview.specimens.some(s => s.id === event.specimenId))
    }
  }

  const ekcc = identitySubjectById('east-kootenay-community-college')
  assert.deepEqual(ekcc.artworkReview.history.filter(x => x.type === 'legal').map(x => x.date),
    ['1978-12-01', '1980-04-01', '1995-11-02'])
  const rockies = identitySubjectById('college-of-the-rockies')
  assert.match(rockies.artworkReview.history.find(x => x.date === '1995-11-02').url, /1329_1995$/)
  assert.equal(rockies.artworkReview.specimens.find(x => x.id === 'cotr-2000-arms').scope, 'heraldry')

  assert.equal(EDITORIAL_LOGO_SPECIMENS['pacific-marine-training-institute'], undefined)
  assert.ok(registry.records.find(x => x.id === 'pacific-marine-training-institute')
    .sources.some(x => x.title.includes('July 1994 transfer announcement')))
})
