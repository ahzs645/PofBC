import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, existsSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { COLLECTING } from './collectingData.js'
import { COLLECTED_BODIES } from './collectedData.js'
import { ACQUIRED_VECTORS } from './acquiredVectorData.js'
import { LOGO_BRAND_GUIDELINES } from './logoBrandGuidelines.js'
import { COLLECTED_COLLECTIONS, CONTINUATIONS, REGISTER_CONTINUATIONS, assetUrl, collectedEntriesOf, nodesOf, parseSpecimenDate, researchLabel } from './collectedCollections.js'
import { GALLERY_COLLECTIONS, collectionById, collectionOfNode, entriesOf, entriesOfNode, findGalleryEntry } from './collections.js'
import { COLLECTED_PALETTES, paletteFor } from './collectedPalettes.js'
import { HISTORICAL_BODIES } from '../government/historyData.js'
import { IDENTITY_COVERAGE } from './identityCoverage.js'

const root = new URL('../../', import.meta.url)

test('every requested body is accounted for without inventing collected artwork', () => {
  const supplemental = ['sub-bc-housing-licensing-and-consumer-services']
  assert.deepEqual(COLLECTED_BODIES.map((body) => body.id).sort(), [...COLLECTING.map((body) => body.id), ...supplemental].sort())
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
    if (entry.asset.reconstruction) assert.ok(['reconstructed', 'third_party_reconstruction'].includes(entry.identity.provenance))
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

test('a matched source vector opens as the default under the existing design link', () => {
  const matches = [
    ['geoscience-bc-three-colours', 'geoscience-bc-three-colours-vector'],
    ['bcgs-anniversary-2020', 'bcgs-anniversary-vector-2020'],
    ['bcgs-founding-year-seal', 'bcgs-founding-year-vector-2022']
  ]
  for (const [designId, vectorId] of matches) {
    const entry = findGalleryEntry(designId)
    assert.equal(entry.id, designId)
    assert.equal(findGalleryEntry(vectorId), entry)
    assert.equal(entry.asset.id, vectorId)
    assert.equal(entry.identity.provenance, 'extracted_from_official_vector')
    assert.equal(entry.versions[0], entry.asset)
    assert.ok(entry.versions.some((version) => version.id === designId && !version.isVector))
  }
  assert.equal(findGalleryEntry('bcgs-survey-seal').asset.format, 'png')
})

test('active collection covers prefer verified vectors of the current identity', () => {
  const covers = {
    'collected-geoscience-bc': 'geoscience-bc-three-colours',
    'collected-sub-british-columbia-geological-survey': 'bcgs-founding-year-seal',
    'collected-legislative-library-bc': 'legislative-library-digital-collections',
    'collected-legislative-assembly': 'legislative-assembly-dome-signature',
    'collected-bc-assessment': 'bc-assessment-svg',
    'collected-municipality-fort-st-john': 'municipal-fort-st-john-ocp-2025-stacked',
    'collected-municipality-prince-george': 'municipal-prince-george-annual-report-2025-horizontal',
    'collected-municipality-prince-rupert': 'municipal-prince-rupert-community-assessment-2024',
    'collected-sub-bc-cancer': 'bc-cancer-phsa',
    'tourism-bc-destination-bc': 'source-destination-bc-destination-bc-svg'
  }
  for (const [collectionId, cover] of Object.entries(covers)) {
    const collection = collectionById(collectionId)
    assert.equal(collection.cover, cover, collectionId)
    assert.equal(entriesOf(collection)[0].id, cover, collectionId)
  }
  const geoscience = entriesOf(collectionById('collected-geoscience-bc'))
  assert.deepEqual(geoscience.map(({ id }) => id), ['geoscience-bc-three-colours', 'geoscience-bc-green-ridges'])
  assert.equal(geoscience[0].asset.id, 'geoscience-bc-three-colours-vector')

  const regulator = collectionById('collected-bc-energy-regulator')
  assert.equal(findGalleryEntry(regulator.cover).owner, 'bc-energy-regulator')
  assert.equal(regulator.eras[0].entries[0].owner, 'oil-and-gas-commission')
})

test('Prince George keeps the two horizontal colourways under the same vector cover', () => {
  const collection = collectionById('collected-municipality-prince-george')
  const [cover] = entriesOf(collection)
  assert.equal(collection.cover, cover.id)
  assert.equal(cover.years, 'Seen June 2026')
  assert.deepEqual(cover.versions.map(({ id }) => id), [
    cover.id, 'municipal-prince-george-annual-report-2025-horizontal-white'
  ])
  assert.ok(cover.versions.every(({ isVector }) => isVector))
  assert.equal(findGalleryEntry(cover.versions[1].id), cover)
  assert.equal(findGalleryEntry('source-municipal-prince-george-website-logo').asset.format, 'png')
})

test('Fort St. John features the stacked vector and preserves each documented specimen', () => {
  const collection = collectionById('collected-municipality-fort-st-john')
  const specimens = entriesOf(collection)
  assert.deepEqual(specimens.map(({ id, asset, years }) => [id, asset.format, years]), [
    ['municipal-fort-st-john-ocp-2025-stacked', 'svg', 'Seen 2025'],
    ['fort-st-john-energetic-black-2012', 'svg', 'Seen 2012'],
    ['fort-st-john-compass-2013', 'png', 'Seen 2013'],
    ['source-municipal-fort-st-john-website-logo', 'png', 'Logo dates unestablished']
  ])
  for (const entry of specimens) {
    assert.equal(findGalleryEntry(entry.id), entry)
    assert.equal(entry.versions, undefined)
  }
})

test('the gallery can feature a dated native specimen while preserving the current design link', () => {
  const goldTrail = collectionById('collected-school-district-74')
  assert.equal(goldTrail.cover, 'school-district-74-logo-current')
  const featured = findGalleryEntry(goldTrail.shelfSpecimen)
  assert.equal(featured.id, 'school-district-74-strategic-plan-gold-trail')
  assert.equal(featured.years, 'Seen 2021')
  assert.equal(findGalleryEntry(goldTrail.cover).asset.format, 'png')

  for (const collection of GALLERY_COLLECTIONS.filter((each) => each.shelfSpecimen)) {
    const entry = entriesOf(collection).find((each) => each.id === collection.shelfSpecimen)
    assert.ok(entry?.asset.isVector && !entry.asset.reconstruction && !entry.asset.containsRaster, collection.id)
    assert.notEqual(collection.shelfSpecimen, collection.cover)
  }
})

test('the Survey separates its current and earlier seals from anniversary artwork', () => {
  const survey = collectionById('collected-sub-british-columbia-geological-survey')
  const sections = survey.artworkSections.map(({ label, entries }) => [label, entries.map(({ id }) => id)])
  assert.deepEqual(sections, [
    ['Current seal', [survey.cover]],
    ['Earlier seal', ['bcgs-survey-seal']],
    ['Anniversary variants', ['bcgs-anniversary-2020', 'bcgs-centennial-1995']]
  ])
  assert.deepEqual(sections.flatMap(([, ids]) => ids).sort(), entriesOf(survey).map(({ id }) => id).sort())
  assert.equal(findGalleryEntry('bcgs-anniversary-2020').identity.provenance, 'extracted_from_official_vector')
  assert.equal(findGalleryEntry('bcgs-centennial-1995').asset.format, 'png')
  assert.match(findGalleryEntry(survey.cover).years, /2026/)
})

test('publication vectors keep existing design links, source files and colourways', () => {
  for (const [id, { asset, alternates = [], prefer }] of Object.entries(ACQUIRED_VECTORS)) {
    const entry = findGalleryEntry(id)
    assert.equal(entry.id, id)
    assert.ok(entry.versions.some((version) => !version.isVector), id)
    const vectorDefault = prefer || entry.asset.derivedFrom === asset.id
    assert.equal(entry.asset.isVector, vectorDefault, id)
    if (vectorDefault) {
      const provenance = entry.asset.evidenceType === 'official-website-svg' ? 'published_vector' : 'extracted_from_official_vector'
      assert.equal(entry.identity.provenance, provenance, id)
    }

    for (const version of [asset, ...alternates]) {
      assert.equal(findGalleryEntry(version.id), entry)
      assert.ok(entry.versions.some((item) => item.id === version.id && item.isVector), version.id)
      if (version.extraction.page) assert.equal(new URL(version.sourcePage).hash, `#page=${version.extraction.page}`, version.id)
      assert.ok(version.publisher && version.sourceLocator && version.extraction.method, version.id)

      const svg = readFileSync(new URL(`public/${version.file}`, root))
      assert.equal(createHash('sha256').update(svg).digest('hex'), version.sha256, version.file)
      assert.doesNotMatch(svg.toString(), /<(?:\w+:)?(?:image|script|foreignObject)\b|data:image/i, version.file)
    }
  }
})

test('brand guidelines link to the design across its artwork versions', () => {
  for (const [id, guide] of Object.entries(LOGO_BRAND_GUIDELINES)) {
    const entry = findGalleryEntry(id)
    assert.equal(entry.id, id)
    assert.deepEqual(entry.brandGuidelines, guide)
    assert.match(guide.url, /^https:\/\//)
    for (const version of entry.versions ?? []) assert.equal(findGalleryEntry(version.id).brandGuidelines, guide)
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

test('the BCEC prospectus link leads to the fixed-spacing reconstruction with the published image kept as a version', () => {
  const published = 'source-bc-enterprise-corporation-bc-enterprise-1988-logo-png'
  const vector = 'bc-enterprise-corporation-rebuilt-bw'
  const collection = collectionById('collected-bc-enterprise-corporation')
  const entry = findGalleryEntry(published)
  assert.equal(collection.cover, vector)
  assert.deepEqual(entriesOf(collection), [entry])
  assert.equal(entry.id, vector)
  assert.equal(entry.asset.reconstructionOf, published)
  assert.equal(entry.identity.provenance, 'third_party_reconstruction')
  assert.deepEqual(entry.versions.map(({ id, format }) => [id, format]), [[vector, 'svg'], [published, 'png']])
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
  const fromRegister = new Set(REGISTER_CONTINUATIONS.map(([from]) => from))
  for (const [from, to] of folded) {
    if (fromRegister.has(from)) continue
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

test('a college line is a one-to-one rename in the identity register', () => {
  const subjects = new Map(IDENTITY_COVERAGE.map((subject) => [subject.id, subject]))
  const renamed = (id) => (subjects.get(id)?.relations ?? []).filter(({ type }) => type === 'renamed-to').map(({ subject }) => subject)
  for (const [from, to] of REGISTER_CONTINUATIONS) {
    assert.ok(CONTINUATIONS.some(([a, b]) => a === from && b === to), from)
    assert.deepEqual(renamed(from), [to], from)
    // Many to one: no other subject was renamed to, merged into or became the same successor.
    const others = IDENTITY_COVERAGE.filter((subject) => subject.id !== from && subject.relations?.some((relation) =>
      relation.subject === to && ['renamed-to', 'merged-into', 'became', 'predecessor-of'].includes(relation.type)))
    assert.deepEqual(others.map(({ id }) => id), [], from)
    // One to many: the earlier name did not split or pass its work to anyone else.
    assert.ok(!(subjects.get(from).relations ?? []).some(({ type, subject }) => subject !== to &&
      ['split-into', 'merged-into', 'transferred-operations-to', 'became'].includes(type)), from)
  }
  // Each line is one collection, and every earlier name's link opens it.
  assert.equal(collectionById('collected-cariboo-college'), collectionById('collected-thompson-rivers-university'))
  assert.deepEqual(collectionById('collected-thompson-rivers-university').eras.map(({ years }) => years), ['1970–1991', '1991–2005', '2005–present'])
  assert.notEqual(collectionById('collected-bc-place-ltd'), collectionById('collected-bc-enterprise-corporation'))
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

test('reviewed colour families share an SVG master and retain old source links', () => {
  for (const [id, group] of Object.entries(COLLECTED_PALETTES)) {
    const entry = findGalleryEntry(id)
    assert.ok(entry, id)
    assert.equal(entry.asset.id, group.masterId, id)
    assert.equal(entry.asset.format, 'svg', id)
    assert.equal(entry.asset.isVector, true, id)
    for (const source of entry.versions) assert.equal(findGalleryEntry(source.id), entry, source.id)
    for (const palette of group.palettes) for (const alias of palette.sourceIds ?? []) {
      assert.equal(findGalleryEntry(alias), entry, alias)
      assert.equal(paletteFor(group, { sourceId: alias }).id, palette.id, alias)
    }
  }
})

test('palette consolidation keeps different lockups separate', () => {
  const northern = collectedEntriesOf('northern-health')
  assert.equal(northern.length, 2, 'tagline palettes share one entry; the no-tagline lockup remains separate')
  assert.equal(northern.filter((entry) => entry.paletteGroup).length, 1)
  assert.equal(northern.find((entry) => entry.paletteGroup).versions.length, 3)
  const knowledge = collectedEntriesOf('knowledge-network')
  assert.equal(knowledge.length, 1)
  assert.equal(knowledge[0].id, 'source-knowledge-network-knowledge-network-colour-eps', 'existing public link remains stable')
  assert.equal(knowledge[0].paletteGroup.palettes.length, 4)
  assert.ok(knowledge[0].versions.some((source) => source.format === 'eps'), 'print source is retained')
  const fpcc = collectedEntriesOf('first-peoples-cultural-council')
  assert.equal(fpcc.length, 2, 'different emblem proportions and lettering are not colour-only variants')
})
