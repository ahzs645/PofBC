import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { basename } from 'node:path'
import recovery from './vectorRecoveryData.json' with { type: 'json' }
import audit from '../../research/identity/vector-recovery-2026-11-26/acquisitions.json' with { type: 'json' }
import { withVectorRecovery } from './vectorRecovery.js'
import { ALL_COLLECTED_BODIES } from './collectedBodies.js'
import { COLLECTED_BODIES } from './collectedData.js'
import { EXPANDED_IDENTITY_BODIES } from './expandedIdentityData.js'
import { MUNICIPAL_IDENTITY_BODIES } from './municipalIdentityData.js'
import { RECOVERED_IDENTITY_BODIES } from './recoveredIdentityData.js'
import { POSTSECONDARY_IDENTITY_BODIES } from './postsecondaryIdentityData.js'
import { REGIONAL_DISTRICT_BODIES } from './regionalDistricts.js'
import { AIRPORT_BODIES } from '../airports/airportArtwork.js'
import { collectedEntriesOf, parseSpecimenDate } from './collectedCollections.js'
import { collectionById, collectionOfNode, entriesOf, entriesOfNode, findGalleryEntry } from './collections.js'
import { identitySubjectById } from './identityCoverage.js'

const root = new URL('../../', import.meta.url)
const additions = Object.entries(recovery.additions).flatMap(([owner, assets]) => assets.map((asset) => ({ owner, asset })))
const bodies = new Map(ALL_COLLECTED_BODIES.map((body) => [body.id, body]))
const versionsOf = (entry) => entry.versions ?? [entry.asset]
const sha256 = (data) => createHash('sha256').update(data).digest('hex')

test('recovered source files match the checksums, owners and provenance in the acquisition audit', () => {
  const records = new Map(audit.assets.map((record) => [record.asset.id, record]))
  assert.ok(additions.length > 0)
  assert.equal(records.size, audit.assets.length, 'audit IDs are unique')
  assert.deepEqual([...records.keys()].sort(), additions.map(({ asset }) => asset.id).sort())
  for (const { owner, asset } of additions) {
    assert.match(asset.file, /^identity-[a-z0-9._/-]+$/)
    assert.ok(!asset.file.split('/').includes('..'), asset.file)
    const data = readFileSync(new URL(`public/${asset.file}`, root))
    assert.equal(data.length, asset.bytes, asset.id)
    assert.equal(sha256(data), asset.sha256, asset.id)
    const record = records.get(asset.id)
    assert.equal(record.subjectId, owner, asset.id)
    for (const key of ['file', 'format', 'sha256', 'bytes', 'isVector', 'reconstruction', 'sourceUrl', 'sourcePage', 'sourceLocator', 'sourceDate', 'specimenDate', 'extraction']) {
      assert.deepEqual(record.asset[key], asset[key], `${asset.id}: audit ${key}`)
    }
    assert.ok(asset.publisher && asset.sourceLocator && asset.fidelityNote, asset.id)
    assert.equal(new URL(asset.sourceUrl).protocol, 'https:', asset.id)
    assert.equal(asset.reconstruction, false, asset.id)
  }
})

test('recovered vectors contain native geometry, while scans remain explicitly raster', () => {
  for (const { asset } of additions) {
    const data = readFileSync(new URL(`public/${asset.file}`, root))
    if (asset.format === 'svg') {
      const svg = data.toString('utf8')
      assert.match(svg, /<(?:\w+:)?svg\b/i, asset.id)
      assert.doesNotMatch(svg, /<(?:\w+:)?(?:script|foreignObject)\b|\son[a-z]+\s*=/i, asset.id)
      assert.equal(asset.isVector, true, asset.id)
      assert.notEqual(asset.containsRaster, true, asset.id)
      assert.doesNotMatch(svg, /<(?:\w+:)?(?:image|feImage)\b|data:image\/(?:png|jpe?g|gif|webp|bmp|tiff?)/i, `${asset.id}: a bitmap wrapper is not a vector`)
      assert.match(svg, /<(?:\w+:)?(?:path|polygon|polyline|rect|circle|ellipse|line)\b/i, `${asset.id}: native geometry`)
    } else {
      assert.equal(asset.isVector, false, asset.id)
      if (asset.format === 'png') assert.equal(data.subarray(0, 8).toString('hex'), '89504e470d0a1a0a', asset.id)
      else if (asset.format === 'jpg' || asset.format === 'jpeg') assert.equal(data.subarray(0, 3).toString('hex'), 'ffd8ff', asset.id)
      else assert.fail(`${asset.id}: verify the newly introduced ${asset.format} format`)
    }
  }
})

test('the recovery retains existing source IDs and files when adding a preferred vector', () => {
  const earlierBodies = [
    ...COLLECTED_BODIES, ...EXPANDED_IDENTITY_BODIES, ...MUNICIPAL_IDENTITY_BODIES,
    ...RECOVERED_IDENTITY_BODIES, ...POSTSECONDARY_IDENTITY_BODIES, ...REGIONAL_DISTRICT_BODIES, ...AIRPORT_BODIES
  ].filter((body) => recovery.additions[body.id] || body.assets?.some((asset) => recovery.assetPatches[asset.id]))
  assert.ok(earlierBodies.length > 0)
  for (const earlier of earlierBodies) {
    const body = bodies.get(earlier.id)
    assert.ok(body, earlier.id)
    for (const original of earlier.assets ?? []) {
      const retained = body.assets.filter(({ id }) => id === original.id)
      assert.equal(retained.length, 1, original.id)
      for (const key of ['id', 'file', 'format', 'sha256', 'bytes']) assert.equal(retained[0][key], original[key], `${original.id}: ${key}`)
      const entry = findGalleryEntry(original.id)
      assert.ok(entry, `${original.id}: original link still resolves`)
      assert.equal(entry.owner, earlier.id, original.id)
      assert.ok(versionsOf(entry).some(({ id }) => id === original.id), original.id)
    }
  }
  for (const [designId, patch] of Object.entries(recovery.assetPatches)) {
    if (!patch.preferredVector) continue
    const entry = findGalleryEntry(designId)
    assert.equal(entry.id, designId)
    assert.equal(findGalleryEntry(patch.preferredVector), entry)
    assert.equal(entry.asset.id, patch.preferredVector)
    assert.ok(versionsOf(entry).some((asset) => asset.id === designId && !asset.isVector), designId)
  }
})

test('every recovered variant belongs to a reachable design of the same body', () => {
  const ids = additions.map(({ asset }) => asset.id)
  assert.equal(new Set(ids).size, ids.length)
  for (const { owner, asset } of additions) {
    const body = bodies.get(owner)
    assert.ok(body, owner)
    assert.equal(body.assets.filter(({ id }) => id === asset.id).length, 1, asset.id)
    const collection = collectionOfNode(owner)
    assert.ok(collection, `${owner}: collection`)
    const entry = findGalleryEntry(asset.id)
    assert.ok(entry, `${asset.id}: detail link`)
    assert.equal(entry.owner, owner, asset.id)
    assert.ok(entriesOfNode(collection, owner).some((shown) => shown.id === entry.id), `${asset.id}: collection reachability`)
    assert.ok(versionsOf(entry).some(({ id }) => id === asset.id), asset.id)
    if (asset.variantOf) {
      const design = body.assets.find(({ id }) => id === asset.variantOf)
      assert.ok(design, `${asset.id}: same-body design ${asset.variantOf}`)
      assert.equal(design.variantOf, undefined, `${asset.id}: variants cannot form chains or cycles`)
      assert.equal(findGalleryEntry(asset.variantOf), entry, asset.id)
    }
  }
})

test('recovery creates no duplicate bodies and preserves an existing body record', () => {
  assert.equal(bodies.size, ALL_COLLECTED_BODIES.length)
  assert.equal(new Set(recovery.newBodies.map(({ id }) => id)).size, recovery.newBodies.length)
  const existing = {
    id: 'ubc-okanagan-campus', name: 'Existing campus record', current: true,
    cover: 'existing-campus-design', sources: [{ url: 'https://example.org/prior-source' }],
    assets: [{ id: 'existing-campus-design', file: 'existing.svg' }]
  }
  const before = structuredClone(existing)
  const result = withVectorRecovery([existing]).filter(({ id }) => id === existing.id)
  assert.equal(result.length, 1)
  assert.equal(result[0].name, existing.name)
  assert.equal(result[0].cover, existing.cover)
  assert.deepEqual(result[0].sources, existing.sources)
  assert.ok(result[0].assets.some(({ id }) => id === existing.assets[0].id))
  assert.deepEqual(existing, before, 'ingestion does not mutate its input')
})

test('new designs remain accessible when an existing collection has explicit sections or eras', () => {
  const priorSection = { id: 'prior', label: 'Existing artwork', marks: ['prior-logo'] }
  const original = {
    id: 'municipality-sparwood', assets: [{ id: 'prior-logo', file: 'prior.svg' }],
    artworkSections: [priorSection], eras: [{ ...priorSection, years: 'Earlier evidence' }]
  }
  const integrated = withVectorRecovery([original]).find(({ id }) => id === original.id)
  assert.deepEqual(integrated.artworkSections[0], priorSection)
  assert.deepEqual(integrated.eras[0], original.eras[0])
  const designs = recovery.additions[original.id].filter(({ variantOf }) => !variantOf)
  assert.ok(designs.length > 0)
  for (const design of designs) {
    assert.ok(integrated.artworkSections.some(({ marks }) => marks.includes(design.id)), design.id)
    assert.ok(integrated.eras.some(({ marks }) => marks.includes(design.id)), design.id)
  }
  for (const variant of recovery.additions[original.id].filter(({ variantOf }) => variantOf)) {
    assert.ok(!integrated.artworkSections.some(({ marks }) => marks.includes(variant.id)), `${variant.id}: versions stay under their design`)
  }
})

test('historical acquisitions do not replace the verified current collection covers', () => {
  const currentCovers = {
    'airport-cybl': 'airport-cybl-colour',
    'airport-cak3': 'airport-cak3-website-header',
    'airport-cycd': 'airport-cycd-signature',
    'airport-cyyd': 'airport-cyyd-signature',
    'airport-cyvr': 'airport-cyvr-signature',
    'municipality-north-cowichan': 'source-recovered-municipal-north-cowichan-website-logo',
    'municipality-radium-hot-springs': 'source-recovered-municipal-radium-hot-springs-website-logo',
    'capilano-university': 'recovered-official-capilano-university-vector',
    'selkirk-college': 'recovered-official-selkirk-college-vector',
    'vancouver-community-college': 'recovered-official-vancouver-community-college-vector',
    'college-of-new-caledonia': 'recovered-official-college-of-new-caledonia-vector',
    'vancouver-island-university': 'recovered-2024-rgb-viu-full-colour-logo',
    'nicola-valley-institute-of-technology': 'recovered-nvit-eagle-fullname-colour',
    'electoral-boundaries-commission': 'source-vector-electoral-boundaries-2023'
  }
  for (const [owner, cover] of Object.entries(currentCovers)) {
    const collection = collectionById(`collected-${owner}`)
    assert.equal(collection.cover, cover, owner)
    assert.equal(entriesOf(collection)[0].id, cover, owner)
    assert.notEqual(findGalleryEntry(cover).asset.role, 'historical', owner)
    for (const asset of recovery.additions[owner].filter(({ role }) => role === 'historical')) {
      assert.ok(findGalleryEntry(asset.id), `${asset.id}: historical artwork remains available`)
    }
  }
  // New recovery batches can introduce further histories. A current collection's
  // cover must retain non-historical evidence, even when a dated native source
  // is the preferred file for that same design.
  for (const [owner, assets] of Object.entries(recovery.additions)) {
    if (!bodies.get(owner).current || !assets.some(({ role }) => role === 'historical')) continue
    const collection = collectionOfNode(owner)
    const cover = findGalleryEntry(collection.cover)
    assert.ok(cover, `${owner}: current cover resolves`)
    assert.ok(versionsOf(cover).some((asset) => asset.role !== 'historical' && !asset.sourceReproduction),
      `${owner}: an exclusively historical specimen must not replace the current cover`)
  }
})

test('NVIT rider and eagle specimens retain the newspaper dates and distinct PDF and printed page references', () => {
  const specimens = [
    ['recovered-nvit-rider-circle-1989', '1989-05-26', 22, 22],
    ['recovered-nvit-rider-initials-1999', '1999-04', 54, 34],
    ['recovered-nvit-eagle-monochrome-2006', '2006-03', 33, 21]
  ]
  for (const [id, date, pdfPage, printedPage] of specimens) {
    const entry = findGalleryEntry(id)
    const asset = entry.asset
    assert.equal(asset.isVector, false, id)
    assert.equal(asset.format, 'png', id)
    assert.equal(asset.reconstruction, false, id)
    assert.equal(asset.role, 'historical', id)
    assert.equal(asset.sourceDate, date, id)
    assert.equal(new URL(asset.sourceUrl).hostname, 'windspeaker.com', id)
    assert.equal(new URL(asset.sourcePage).hash, `#page=${pdfPage}`, id)
    assert.match(asset.notes, new RegExp(`PDF page ${pdfPage}, printed page ${printedPage}\\b`), id)
    assert.equal(entry.identity.provenance, 'published_raster', id)
    assert.equal(entry.identity.applicability.kind, 'dated_specimen', id)
    assert.equal(entry.identity.applicability.years, date, id)
    assert.match(entry.identity.applicability.note, /not a verified first use or adoption date/, id)
  }
  assert.equal(identitySubjectById('nicola-valley-institute-of-technology').state, 'raster-held')
})

test('NVIT reporting, PDF creation, upload and retrieval years are not turned into adoption or specimen dates', () => {
  const report = findGalleryEntry('recovered-nvit-eagle-colour-2012-report')
  const current = findGalleryEntry('recovered-nvit-eagle-fullname-colour')
  assert.match(report.asset.sourceDate, /2012 reporting year/)
  assert.match(report.asset.sourceDate, /2013-06-27/)
  assert.match(current.asset.sourceUrl, /\/2024\/09\//)
  for (const entry of [report, current]) {
    assert.equal(parseSpecimenDate(entry.asset.specimenDate ?? entry.asset.sourceDate), null, entry.id)
    assert.equal(entry.identity.applicability.kind, 'unknown', entry.id)
    assert.equal(entry.identity.applicability.years, 'undated', entry.id)
    assert.equal(entry.years, 'Logo dates unestablished', entry.id)
    assert.equal(entry.asset.isVector, false, entry.id)
    assert.match(entry.asset.dateNote, /transition from rider to eagle remains unestablished/, entry.id)
  }
  assert.equal(current.asset.role, 'current')
  assert.equal(report.asset.role, 'historical')
})

test('UBC Okanagan keeps a shared university identity without inheriting parent or predecessor artwork', () => {
  const campus = identitySubjectById('ubc-okanagan-campus')
  assert.equal(campus.identityStatus, 'shared-identity')
  assert.equal(campus.state, 'native-vector', 'published campus signatures are held')
  assert.equal(bodies.get(campus.id).kind, 'education-campus')
  for (const type of ['part-of', 'shares-identity-with']) {
    assert.ok(campus.relations.some((relation) => relation.type === type && relation.subject === 'university-of-british-columbia'))
  }
  assert.ok(campus.entries.every(({ owner }) => owner === campus.id))
  const campusIds = new Set(campus.entries.flatMap(versionsOf).map(({ id }) => id))
  assert.deepEqual([...campusIds].sort(), recovery.additions[campus.id].map(({ id }) => id).sort())
  for (const id of ['university-of-british-columbia', 'okanagan-university-college']) {
    const subject = identitySubjectById(id)
    assert.ok(subject.entries.every(({ owner }) => owner === id), id)
    assert.ok(!subject.entries.flatMap(versionsOf).some(({ id: assetId }) => campusIds.has(assetId)), id)
  }
  const unresolvedCampus = identitySubjectById('junction-campus')
  assert.equal(unresolvedCampus.state, 'distinct-unconfirmed')
  assert.equal(unresolvedCampus.hasArtwork, false, 'the successor college does not fill a campus identity gap')
})

test('each UBC campus colourway cites its own EPS member rather than a copied standard-logo locator', () => {
  const assets = recovery.additions['ubc-okanagan-campus']
  const members = assets.map((asset) => asset.extraction.zipMember)
  assert.equal(new Set(members).size, assets.length)
  for (const asset of assets) {
    const { zipMember, memberSha256, sourceSha256 } = asset.extraction
    assert.equal(basename(zipMember), basename(asset.file, '.svg') + '.eps', asset.id)
    assert.ok(asset.sourceLocator.includes(zipMember), asset.id)
    assert.match(memberSha256, /^[a-f0-9]{64}$/, asset.id)
    assert.match(sourceSha256, /^[a-f0-9]{64}$/, asset.id)
    assert.notEqual(memberSha256, sourceSha256, `${asset.id}: ZIP and member hashes describe different files`)
    assert.notEqual(memberSha256, asset.sha256, `${asset.id}: the EPS and converted SVG retain separate checksums`)
  }
  assert.equal(collectedEntriesOf('ubc-okanagan-campus').length, 4, 'four layouts, with colourways grouped as versions')
})

test('a corroborating Transit Police source adds a sighting without duplicating the white crest artwork', () => {
  const id = 'source-expanded-metro-vancouver-transit-police-community-report-2025-reversed'
  const entry = findGalleryEntry(id)
  assert.equal(entry.id, id)
  assert.equal(entry.owner, 'metro-vancouver-transit-police')
  const sightings = versionsOf(entry).find((asset) => asset.id === id).alsoSeen
  assert.ok(sightings.some((seen) => seen.date === '2022-03-24' && seen.source.endsWith('2022_03_24_board_meeting_slide_deck.pdf#page=51')))
  assert.ok(!additions.some(({ owner }) => owner === 'metro-vancouver-transit-police'), 'the existing source vector is reused')
  assert.equal(bodies.get('metro-vancouver-transit-police').assets.filter((asset) => asset.id === id).length, 1)
})
