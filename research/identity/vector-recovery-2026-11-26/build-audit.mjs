/** Rebuild the inventory audit from the frozen baseline and current gallery.
 * No application data, artwork, source receipts or baseline files are changed.
 * Run from any directory: node research/identity/vector-recovery-2026-11-26/build-audit.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'
import { DOMParser } from '@xmldom/xmldom'
import { IDENTITY_COVERAGE, COVERAGE_FAMILIES } from '../../../src/gallery/identityCoverage.js'
import { GALLERY_COLLECTIONS, entriesOf } from '../../../src/gallery/collections.js'

const directory = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(directory, '../../..')
const read = (file) => JSON.parse(fs.readFileSync(path.join(directory, file), 'utf8'))
const write = (file, value) => fs.writeFileSync(path.join(directory, file), JSON.stringify(value, null, 2) + '\n')
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex')
const fingerprint = (file) => ({ file, sha256: hash(fs.readFileSync(path.join(root, file))) })
const basename = (p) => String(p).replaceAll('\\', '/').split('/').at(-1)
const unique = (items) => [...new Set(items)]
const groupBy = (items, key) => items.reduce((map, item) => {
  const k = key(item)
  map.set(k, [...(map.get(k) ?? []), item])
  return map
}, new Map())
const countBy = (items, key) => Object.fromEntries([...groupBy(items, key)].map(([k, v]) => [k, v.length]))
const sorted = (items) => [...items].sort((a, b) => String(a.label ?? a.name ?? a.id ?? a.subjectId).localeCompare(String(b.label ?? b.name ?? b.id ?? b.subjectId), 'en-CA'))
const pick = (object, fields) => Object.fromEntries(fields.filter((key) => object?.[key] !== undefined).map((key) => [key, object[key]]))
const base = read('baseline.json')
const acquisition = read('acquisitions.json')
const integration = JSON.parse(fs.readFileSync(path.join(root, 'src/gallery/vectorRecoveryData.json'), 'utf8'))
const research = read('source-ledgers/research-activity.json')
const airportResearch = read('source-ledgers/airport-followup.json')
const municipalResearch = read('source-ledgers/municipal-audit-summary.json')
const asOf = acquisition.asOf
const vectorProvenance = new Set(['original_supplied', 'published_vector', 'extracted_from_official_vector'])
const reconstructedProvenance = new Set(['reconstructed', 'third_party_reconstruction', 'synthetic_name_variant'])
const nativeAsset = (asset) => Boolean(asset?.isVector && !asset.reconstruction && !asset.containsRaster)
const entryAssets = (entry) => entry.versions ?? (entry.asset ? [entry.asset] : [])
const nativeEntry = (entry) => {
  const assets = entryAssets(entry)
  return assets.some(nativeAsset) || (!assets.length && vectorProvenance.has(entry.identity?.provenance))
}
const assetFields = ['id', 'label', 'file', 'format', 'isVector', 'containsRaster', 'reconstruction', 'publisher', 'sourceUrl', 'sourcePage', 'sourceLocator', 'sourceDate', 'specimenDate', 'dateNote', 'role', 'variantOf', 'preferredVector', 'notes', 'fidelityNote', 'alsoSeen']

// Use registered entry ownership, not geographic or parent relationships, to
// assign coverage. The same shared-shelf entry is counted once by its ID.
const subjects = sorted(IDENTITY_COVERAGE)
const subjectMap = new Map(subjects.map((subject) => [subject.id, subject]))
const beforeSubjectMap = new Map(base.subjects.map((subject) => [subject.id, subject]))
const owners = new Map()
for (const subject of subjects) for (const entry of subject.entries) {
  owners.set(entry.id, unique([...(owners.get(entry.id) ?? []), subject.id]))
}
const designMap = new Map()
for (const collection of GALLERY_COLLECTIONS) for (const entry of entriesOf(collection)) {
  let design = designMap.get(entry.id)
  if (!design) {
    design = {
      id: entry.id, label: entry.label ?? entry.title ?? entry.name ?? entry.id,
      collections: [], subjectIds: owners.get(entry.id) ?? [], kind: entry.kind,
      provenance: entry.identity?.provenance, sourceVector: nativeEntry(entry),
      aliases: entry.aliases ?? [], assets: [], assetMap: new Map(),
    }
    designMap.set(entry.id, design)
  }
  design.collections = unique([...design.collections, collection.id])
  design.sourceVector ||= nativeEntry(entry)
  for (const asset of entryAssets(entry)) design.assetMap.set(asset.id ?? asset.file, pick(asset, assetFields))
}
const designs = sorted([...designMap.values()].map(({ assetMap, ...design }) => ({ ...design, assets: [...assetMap.values()] })))
const currentDesignMap = new Map(designs.map((design) => [design.id, design]))
const beforeDesignMap = new Map(base.designs.map((design) => [design.id, design]))
const allAssets = new Map(designs.flatMap((design) => design.assets.map((asset) => [asset.id, asset])))
const freshMap = new Map(research.subjects.map((record) => [record.subjectId, record]))
const familyLabels = new Map(COVERAGE_FAMILIES.map((family) => [family.id, family.label]))
const gaps = subjects.filter((subject) => !subject.entries.some(nativeEntry))
const designGaps = designs.filter((design) => !design.sourceVector)
const baselineSubjectsWithoutNative = base.subjects.filter((subject) => subject.state !== 'native-vector')

const statusDescription = {
  'raster-held': 'Published raster artwork held; source-native artwork still wanted.',
  reconstruction: 'Reconstructed artwork held; authentic source-native artwork still wanted.',
  'artwork-held': 'Artwork held, but accepted native-vector evidence is not established.',
  'source-located': 'A source or acquisition route is recorded; accepted artwork is still missing.',
  'shared-identity': 'Shared identity documented; a separate subject-specific mark is not established.',
  'distinct-unconfirmed': 'A distinct identity is not established by current evidence.',
  'artwork-missing': 'No accepted artwork is held for this registered subject.',
  'not-catalogued': 'Candidate subject still requires identity/source cataloguing.',
}
const genericAction = (subject) => {
  if (subject.state === 'shared-identity') return 'Verify the documented shared-identity relationship and whether any separately used mark exists; do not substitute the parent’s artwork as this subject’s own.'
  if (subject.state === 'distinct-unconfirmed') return 'Locate dated official publications or an archive record that establishes whether this subject used a distinct mark before acquiring or assigning artwork.'
  if (subject.state === 'reconstruction') return 'Locate original publisher artwork or a dated native-vector publication; compare symbol, lettering and layout against the reconstruction before accepting a source replacement.'
  if (subject.state === 'raster-held') return 'Inspect the cited publisher’s brand resources and dated publications for a matching native logo; preserve the documented raster and source colourway until a match is verified.'
  if (subject.state === 'artwork-held') return 'Inspect the held file and its original source to establish whether the logo is native geometry, an embedded bitmap or a reconstruction, then record its provenance.'
  if (subject.state === 'source-located') return 'Retrieve the recorded primary source or catalogue item; inspect the logo itself for native geometry and establish subject ownership before promoting it to accepted artwork.'
  return 'Locate a dated official or archival specimen, establish the subject’s own identity, then seek original vector masters or native geometry in publications.'
}
const focusedAction = (subject) => {
  const id = subject.id
  if (id === 'nicola-valley-institute-of-technology') return 'Seek an original rider/eagle master or a native-logo publication; the five accepted dated specimens are raster. Compare rider-circle, rider-with-initials, eagle, and eagle-with-full-name layouts separately. Do not infer the exact rider-to-eagle adoption date from these sightings.'
  if (id === 'regional-district-bulkley-nechako') return 'Follow the official 2022 committee-agenda lead to an authorized/public release of the district’s AI master; the inspected 2021 and 2025 publications contain raster seals. Do not treat an internal filename as acquired artwork.'
  if (id === 'municipality-daajing-giids') return 'Seek original village artwork from official publisher resources or a public native brand package; the inspected Cinnamon Toast case study contains JPEG/MP4 applications and unrelated agency/UI SVGs.'
  if (['school-district-20', 'school-district-49', 'school-district-81'].includes(id)) return 'Seek an original district logo file or another source-native publication; the entire inspected strategic-plan PDF uses raster district artwork.'
  if (id === 'school-district-69') return 'Find the district’s own native logo source; the inspected six-path inline SVG spells rally and belongs to the website agency, so it cannot fill this identity gap.'
  if (id.startsWith('airport-')) {
    const row = airportResearch.coverage.find((record) => `airport-${record.subjectId.toLowerCase()}` === id)
    if (row?.result === 'searched-source-unavailable') return 'Revisit the official airport/association source when publicly retrievable and look for a published guide, annual report or original logo file. The current raster remains the only verified artwork; failed retrieval does not establish absence.'
    return 'Continue from the airport-specific source checks in source-ledgers/airport-followup.json. Seek original logo masters or a new official publication; existing checked PDFs/header files are raster, unrelated operator/municipal marks, or unavailable. Preserve historical layouts and colourways separately.'
  }
  return genericAction(subject)
}
const activityFor = (id) => {
  const record = freshMap.get(id)
  if (!record) return { status: 'inventory-audited-only', freshSourceResearch: false, note: 'Included in the whole-inventory comparison; no documented fresh source search or retrieval for this exact subject in the bundled ledgers.' }
  return {
    status: 'documented-fresh-source-activity', freshSourceResearch: true,
    workstreams: record.workstreams, inspectionLevels: record.inspectionLevels,
    evidence: unique(record.observations.map((observation) => observation.evidence)),
    scopeNote: 'These records can include homepage discovery or an unavailable retrieval; they do not imply that every design, source or historical era was inspected.',
  }
}
const subjectGaps = gaps.map((subject) => ({
  ...pick(subject, ['id', 'name', 'label', 'family', 'kind', 'scope', 'priority', 'state', 'stateLabel', 'hasArtwork', 'evidence', 'identityStatus', 'note']),
  status: subject.state,
  statusExplanation: statusDescription[subject.state],
  baselineState: beforeSubjectMap.get(subject.id)?.state ?? 'not-in-baseline',
  designIds: unique(subject.entries.map((entry) => entry.id)),
  collections: subject.collections.map((collection) => collection.id),
  sources: subject.sources ?? [], relations: subject.relations ?? [],
  researchThisPass: activityFor(subject.id),
  registeredNextAction: subject.nextAction ?? null,
  nextAction: focusedAction(subject),
}))
const classifiedDesignGaps = designGaps.map((design) => {
  const reconstructed = design.assets.some((asset) => asset.reconstruction) || reconstructedProvenance.has(design.provenance)
  const raster = design.assets.some((asset) => !asset.reconstruction && (!asset.isVector || asset.containsRaster)) || ['published_raster', 'archival_raster'].includes(design.provenance)
  const status = raster ? 'raster-without-native-version' : reconstructed ? 'reconstruction-without-native-source' : 'native-source-evidence-unclassified'
  return {
    ...design, status, baselineSourceVector: beforeDesignMap.get(design.id)?.sourceVector ?? null,
    researchThisPass: {
      designInspectionStatus: 'not-inferred-from-subject-research',
      subjectsWithDocumentedActivity: design.subjectIds.filter((id) => freshMap.has(id)),
      note: 'Subject-level research does not prove this particular design/colourway was freshly inspected. See asset source locators and the linked subject ledger.',
    },
    nextAction: raster
      ? 'Find a source-native version of this specific symbol, wording and layout. Compare its documented colourway and historical treatment; keep the published raster if no matching source is verified.'
      : reconstructed
        ? 'Locate and compare original artwork for this design; retain the reconstruction label until authentic geometry is verified.'
        : 'Inspect the source and held artwork to classify the logo’s geometry/provenance before counting it as a source vector.',
  }
})

// A native colourway makes a gallery design vector-covered but does not prove
// an exact-vector replacement for every original raster version.
const rasterVersionFollowups = []
for (const design of designs.filter((item) => item.sourceVector)) for (const asset of design.assets) {
  if (nativeAsset(asset) || asset.reconstruction || (!asset.file && asset.isVector === undefined)) continue
  const preferred = typeof asset.preferredVector === 'string' ? allAssets.get(asset.preferredVector) : null
  if (preferred && nativeAsset(preferred)) continue
  rasterVersionFollowups.push({
    designId: design.id, designLabel: design.label, subjectIds: design.subjectIds,
    asset: pick(asset, assetFields), status: 'raster-version-without-explicit-exact-vector-match',
    nativeVersionIdsInDesign: design.assets.filter(nativeAsset).map((item) => item.id),
    nextAction: 'Compare source geometry, lettering, layout and colourway with the held native versions. Add preferredVector only when an exact documented match is verified; otherwise retain this raster colourway as unresolved.',
    note: 'No explicit exact-match link is recorded. This is a metadata/research follow-up, not proof that the held native versions are visually unrelated.',
  })
}

const summarize = (subjectRows, designRows) => ({
  subjects: subjectRows.length,
  subjectsWithArtwork: subjectRows.filter((subject) => subject.hasArtwork).length,
  subjectsWithNativeVector: subjectRows.filter((subject) => subject.state === 'native-vector').length,
  subjectsWithoutNativeVector: subjectRows.filter((subject) => subject.state !== 'native-vector').length,
  subjectStates: countBy(subjectRows, (subject) => subject.state),
  galleryCollections: unique(designRows.flatMap((design) => design.collections ?? [])).length,
  galleryDesigns: designRows.length,
  designsWithSourceVector: designRows.filter((design) => design.sourceVector).length,
  designsWithoutSourceVector: designRows.filter((design) => !design.sourceVector).length,
})
const before = summarize(base.subjects, base.designs)
const after = summarize(subjects, designs)
const delta = Object.fromEntries(Object.keys(before).filter((key) => typeof before[key] === 'number').map((key) => [key, after[key] - before[key]]))
const changedSubjects = subjects.filter((subject) => beforeSubjectMap.get(subject.id)?.state !== subject.state).map((subject) => ({
  id: subject.id, name: subject.name ?? subject.label, family: subject.family,
  before: beforeSubjectMap.get(subject.id)?.state ?? 'not-in-baseline', after: subject.state,
  acceptedAssetIds: acquisition.assets.filter((row) => row.subjectId === subject.id).map((row) => row.asset.id),
}))
const existingDesignsGainedNative = designs.filter((design) => beforeDesignMap.has(design.id) && !beforeDesignMap.get(design.id).sourceVector && design.sourceVector).map((design) => ({ id: design.id, label: design.label, subjectIds: design.subjectIds }))
const newlyCataloguedDesigns = designs.filter((design) => !beforeDesignMap.has(design.id))
const missingBaselineDesigns = base.designs.filter((design) => !currentDesignMap.has(design.id)).map((design) => design.id)
const nativeCoverageRegressions = base.designs.filter((design) => design.sourceVector && currentDesignMap.has(design.id) && !currentDesignMap.get(design.id).sourceVector).map((design) => design.id)
const subjectNativeDisagreements = subjects.filter((subject) => (subject.state === 'native-vector') !== subject.entries.some(nativeEntry)).map((subject) => subject.id)

const validation = { acceptedFiles: acquisition.assets.length, missingFiles: [], hashMismatches: [], invalidNativeSvg: [], nativeSvgFilesChecked: 0, rasterFilesChecked: 0, pendingVisualReviewReceipts: [], unspecifiedVisualReviewReceipts: [] }
const integratedAssets = Object.values(integration.additions).flat()
const acquisitionIds = new Set(acquisition.assets.map((row) => row.asset.id))
const integrationIds = new Set(integratedAssets.map((asset) => asset.id))
validation.unintegratedAcceptedAssetIds = [...acquisitionIds].filter((id) => !integrationIds.has(id))
validation.integratedAssetIdsMissingFromAcquisitions = [...integrationIds].filter((id) => !acquisitionIds.has(id))
for (const row of acquisition.assets) {
  const asset = row.asset
  const file = path.join(root, 'public', asset.file)
  if (!fs.existsSync(file)) { validation.missingFiles.push(asset.id); continue }
  const bytes = fs.readFileSync(file)
  if (asset.sha256 && hash(bytes) !== asset.sha256) validation.hashMismatches.push(asset.id)
  if (nativeAsset(asset)) {
    validation.nativeSvgFilesChecked++
    const errors = []
    const doc = new DOMParser({ onError: (level, message) => { if (level === 'error' || level === 'fatalError') errors.push(message) } }).parseFromString(bytes.toString('utf8'), 'image/svg+xml')
    const tags = [...Array.from(doc.getElementsByTagName('*'))]
    const forbidden = tags.filter((element) => ['image', 'text', 'script', 'foreignObject'].includes(element.localName ?? element.tagName)).map((element) => element.localName ?? element.tagName)
    const geometric = tags.filter((element) => ['path', 'polygon', 'polyline', 'circle', 'ellipse', 'rect', 'line', 'use'].includes(element.localName ?? element.tagName))
    const external = tags.flatMap((element) => Array.from(element.attributes ?? []).filter((attribute) => ['href', 'xlink:href'].includes(attribute.name) && attribute.value && !attribute.value.startsWith('#')).map((attribute) => attribute.value))
    if (doc.documentElement?.localName !== 'svg' || errors.length || forbidden.length || external.length || !geometric.length) validation.invalidNativeSvg.push({ id: asset.id, errors, forbiddenElements: forbidden, externalReferences: external, geometryElements: geometric.length })
  } else validation.rasterFilesChecked++
  if (row.visualReview === 'pending') validation.pendingVisualReviewReceipts.push(asset.id)
  else if (!row.visualReview) validation.unspecifiedVisualReviewReceipts.push(asset.id)
}
validation.preservation = { missingBaselineDesignIds: missingBaselineDesigns, nativeCoverageRegressions, subjectNativeDisagreements }
validation.scope = 'File existence/hash checks and native-SVG structure for newly accepted assets only. Original-logo fidelity uses the source receipts; legacy holdings and gallery UI are not independently revalidated by this script.'
const fails = ['missingFiles', 'hashMismatches', 'invalidNativeSvg', 'unintegratedAcceptedAssetIds', 'integratedAssetIdsMissingFromAcquisitions'].some((key) => validation[key].length) || missingBaselineDesigns.length || nativeCoverageRegressions.length || subjectNativeDisagreements.length
if (fails) throw new Error('Audit validation failed: ' + JSON.stringify(validation, null, 2))

const registeredActivity = research.subjects.filter((record) => subjectMap.has(record.subjectId))
const unregisteredActivity = research.subjects.filter((record) => !subjectMap.has(record.subjectId))
const allFamilies = unique(subjects.map((subject) => subject.family))
const perFamily = allFamilies.map((id) => {
  const current = subjects.filter((subject) => subject.family === id)
  const prior = base.subjects.filter((subject) => subject.family === id)
  const nativeBefore = prior.filter((subject) => subject.state === 'native-vector').length
  const nativeAfter = current.filter((subject) => subject.state === 'native-vector').length
  return { id, label: familyLabels.get(id) ?? id, subjectsBefore: prior.length, subjectsAfter: current.length, nativeBefore, nativeAfter, nativeChange: nativeAfter - nativeBefore, subjectsWithoutNativeAfter: current.length - nativeAfter, freshResearchActivitySubjects: current.filter((subject) => freshMap.has(subject.id)).length }
}).sort((a, b) => a.label.localeCompare(b.label, 'en-CA'))
const addedNative = acquisition.assets.filter((row) => nativeAsset(row.asset))
const airportAssets = acquisition.assets.filter((row) => row.subjectId.startsWith('airport-'))
const airportSubjects = subjects.filter((subject) => subject.family === 'airport-identities')
const airportGaps = airportSubjects.filter((subject) => subject.state !== 'native-vector')
const acquiredBySubject = sorted([...groupBy(acquisition.assets, (row) => row.subjectId)].map(([id, rows]) => ({
  id, name: subjectMap.get(id)?.label ?? subjectMap.get(id)?.name ?? id,
  family: subjectMap.get(id)?.family ?? null, assets: rows.length,
  nativeSvg: rows.filter((row) => nativeAsset(row.asset)).length,
  raster: rows.filter((row) => !nativeAsset(row.asset)).length,
  assetIds: rows.map((row) => row.asset.id),
})))
const alsoSeen = acquisition.corroboratingSources.map((item) => ({
  subjectId: 'metro-vancouver-transit-police', existingAssetId: item.asset.variantOf,
  sourceDate: item.asset.sourceDate, sourceUrl: item.asset.sourceUrl, sourceLocator: item.asset.sourceLocator,
  researchFile: item.file, treatment: 'alsoSeen-only; no additional gallery artwork',
  dateLimit: 'Earlier documented appearance, not an adoption date. No byte-exact or path-exact identity claim.',
}))
const inputs = [
  'research/identity/vector-recovery-2026-11-26/baseline.json',
  'research/identity/vector-recovery-2026-11-26/acquisitions.json',
  'src/gallery/vectorRecoveryData.json', 'src/gallery/identityCoverage.js', 'src/gallery/collections.js',
  'research/identity/vector-recovery-2026-11-26/source-ledgers/research-activity.json',
].map(fingerprint)

const limits = [
  'The complete registered inventory was compared mechanically. It is not a claim that all 851 subjects received fresh source searches.',
  'A source-native flag for one gallery design/colourway does not complete all of that subject’s designs, colourways or historical eras.',
  'Legacy native-vector classifications are inherited from repository metadata and provenance; every old file was not independently revalidated in this pass.',
  'Fresh research activity includes homepage discovery, targeted search and failed retrieval as well as inspection of source artwork. The bundled ledgers preserve those differences.',
  'A missing vector or unsuccessful retrieval is an open gap, not proof that an original logo/vector never existed.',
  'Source specimens retain their publication/observation dates. Adoption, retirement and exclusive periods of use are not inferred from the upload directory or first located specimen.',
  'Raster originals, mixed raster/vector treatments and reconstructions are not promoted to native-vector artwork. No raster tracing or invented geometry was used for the new native acquisitions.',
  'Parent, municipal, shared operator and proposed tourism identities are not automatically substituted for a different registered subject.',
  'Most unresolved municipal records received discovery-level work; 35 municipal/school subjects had candidate source bytes inspected by that workstream.',
  'Only 28 of the 34 airport gallery subjects received fresh research. All 22 originally wholly raster-only collections were searched; six already-vector-covered airport collections remained baseline review only.',
  'Of the 53 additional facilities in the earlier 87-facility airport inventory, three received fresh searches and 50 were not independently searched here.',
  'This audit does not claim a complete historical-era search. Unseen or uncatalogued designs do not become counted gaps until identified.',
]
const report = {
  schemaVersion: 1, asOf, baselineCommit: base.baseCommit,
  title: 'PofBC source-vector recovery: inventory audit and remaining gaps',
  definitions: { subject: 'A registered identity subject; ownership is separate from gallery placement.', design: 'A unique gallery-entry ID, potentially with several source files/colourways.', nativeVector: base.definitions.nativeVector, freshResearch: research.definition, countLimit: 'Asset counts, design counts and subject counts measure different things.' },
  inputs, before, after, delta,
  acquisitionSummary: { acceptedAssets: acquisition.assets.length, nativeSvgAssets: addedNative.length, rasterAssets: acquisition.assets.length - addedNative.length, subjectsReceivingAssets: acquiredBySubject.length, artworkBodyRecordsAdded: integration.newBodies.length, formatCounts: countBy(acquisition.assets, (row) => row.asset.format), acceptedBySubject: acquiredBySubject },
  coverageChanges: { changedSubjects, existingDesignsGainedNative, newlyCataloguedDesigns: { total: newlyCataloguedDesigns.length, native: newlyCataloguedDesigns.filter((design) => design.sourceVector).length, withoutNative: newlyCataloguedDesigns.filter((design) => !design.sourceVector).length, ids: newlyCataloguedDesigns.map((design) => design.id) }, baselineDesignsPreserved: base.designs.length - missingBaselineDesigns.length },
  perFamily,
  researchCoverage: { registeredInventoryAudited: subjects.length, registeredSubjectsWithDocumentedFreshActivity: registeredActivity.length, registeredSubjectsWithoutDocumentedFreshActivity: subjects.length - registeredActivity.length, additionalUnregisteredResearchSubjects: unregisteredActivity.map((record) => record.subjectId), workstreamsOverlap: true, uniqueRegisteredSubjectsByWorkstream: Object.fromEntries(unique(registeredActivity.flatMap((record) => record.workstreams)).sort().map((stream) => [stream, registeredActivity.filter((record) => record.workstreams.includes(stream)).length])), activityLedger: 'source-ledgers/research-activity.json', municipalSummary: municipalResearch.summary },
  airportSummary: { gallerySubjects: airportSubjects.length, nativeSubjectsBefore: base.subjects.filter((subject) => subject.family === 'airport-identities' && subject.state === 'native-vector').length, nativeSubjectsAfter: airportSubjects.filter((subject) => subject.state === 'native-vector').length, acceptedAssets: airportAssets.length, acceptedNativeSvg: airportAssets.filter((row) => nativeAsset(row.asset)).length, acceptedRasters: airportAssets.filter((row) => !nativeAsset(row.asset)).length, remainingWithoutNative: airportGaps.length, remainingSubjectIds: airportGaps.map((subject) => subject.id), freshGallerySubjects: airportSubjects.filter((subject) => freshMap.has(subject.id)).length, originalRasterOnlySubjectsSearched: 22, broaderInventoryFacilities: 87, additionalFacilities: 53, additionalFacilitiesFreshlySearched: 3, additionalFacilitiesNotFreshlySearched: 50 },
  researchOnly: { proposedTourismVariants: acquisition.relatedProposals.map((item) => pick(item, ['id', 'name', 'subjectId', 'sourceUrl', 'sourceLocator', 'sourceDate', 'file', 'status'])), unregisteredPortArtwork: acquisition.relatedArtwork, excludedFromAcceptedAssetCounts: acquisition.relatedProposals.length + acquisition.relatedArtwork.length },
  alsoSeen,
  gapRegister: { file: 'remaining-gaps.json', subjectsWithoutNative: subjectGaps.length, designsWithoutNative: classifiedDesignGaps.length, rasterVersionsInNativeDesignsWithoutExplicitExactMatch: rasterVersionFollowups.length },
  validation,
  limitations: limits,
}
write('report.json', report)
write('remaining-gaps.json', {
  schemaVersion: 1, asOf, baselineCommit: base.baseCommit,
  scope: 'Every current registered subject lacking native-vector artwork and every current gallery design lacking a source-native version. Also lists raster versions inside vector-covered designs where no explicit preferredVector match is recorded.',
  counts: pick(report.gapRegister, ['subjectsWithoutNative', 'designsWithoutNative', 'rasterVersionsInNativeDesignsWithoutExplicitExactMatch']),
  definitions: { nativeVector: report.definitions.nativeVector, inventoryOnly: 'Mechanically reviewed but no fresh research record for this exact subject.', status: 'Current strongest accepted evidence; not an assertion that a source does not exist.', designResearch: 'Never inferred from a subject-level source search.', rasterVersionFollowup: 'No explicit exact-match vector link; a metadata/research follow-up, not proof that a matching native source is absent.' },
  subjectGaps, designGaps: classifiedDesignGaps, rasterVersionFollowups,
})

const sign = (value) => value > 0 ? `+${value}` : String(value)
const link = (url, text) => `[${text}](${url})`
const nvit = acquisition.assets.filter((row) => row.subjectId === 'nicola-valley-institute-of-technology')
const md = [
  '# Source-vector recovery audit — 26 November 2026', '',
  `The complete **${after.subjects}-subject inventory** was compared with baseline commit \`${base.baseCommit}\`. This pass added **${acquisition.assets.length} accepted artwork files: ${addedNative.length} native SVGs and ${acquisition.assets.length - addedNative.length} authentic rasters, across ${acquiredBySubject.length} subjects**. Subject-level native coverage increased from **${before.subjectsWithNativeVector} to ${after.subjectsWithNativeVector}**. **${after.subjectsWithoutNativeVector} subjects and ${after.designsWithoutSourceVector} gallery designs still lack source-native artwork.**`, '',
  `The inventory audit is broader than the source research. Bundled receipts document fresh discovery, retrieval attempts or source inspection for **${registeredActivity.length} registered subjects**, with varying inspection depth, plus **${unregisteredActivity.length} unregistered airport-inventory facilities**. The other **${subjects.length - registeredActivity.length} registered subjects** were included in the metadata comparison without a documented fresh source search. Neither the 851-subject audit nor the new vectors imply that all historical eras are complete.`, '',
  '## Before and after', '',
  '| Measure | Baseline | Current | Change |', '|---|---:|---:|---:|',
  ...[['Registered identity subjects', 'subjects'], ['Subjects with any accepted artwork', 'subjectsWithArtwork'], ['Subjects with at least one native-vector design', 'subjectsWithNativeVector'], ['Subjects without native-vector artwork', 'subjectsWithoutNativeVector'], ['Collections holding gallery designs', 'galleryCollections'], ['Distinct gallery designs', 'galleryDesigns'], ['Designs with a source-native version', 'designsWithSourceVector'], ['Designs without a source-native version', 'designsWithoutSourceVector']].map(([label, key]) => `| ${label} | ${before[key]} | ${after[key]} | ${sign(delta[key])} |`), '',
  `All **${base.designs.length} baseline design IDs remain present**, and no baseline native design lost native coverage. **${existingDesignsGainedNative.length} existing designs** gained a native version. **${newlyCataloguedDesigns.length} new design entries** were catalogued: ${newlyCataloguedDesigns.filter((design) => design.sourceVector).length} with native artwork and ${newlyCataloguedDesigns.filter((design) => !design.sourceVector).length} without it. The non-vector design count can therefore increase when newly found historical rasters are preserved. Assets, designs and subjects are different counts: several genuine source colourways can belong to one design.`, '',
  'A design is vector-covered when at least one accepted source-native version exists. This does not mean every raster colourway has an exact vector replacement. The gap register separately flags those raster-version follow-ups; it does not manufacture colour matches.', '',
  '## Significant source recoveries', '',
  '- **Post-secondary identities:** official source files and native publication geometry cover current institutions and separately owned predecessor identities, including Kwantlen College/University College, Cariboo College/University College of the Cariboo, Capilano College, Okanagan University College, Fraser Valley College/University College of the Fraser Valley, Emily Carr Institute and the Kootenay School of the Arts. These are dated specimens, not inferred rebrand dates. UBC Okanagan campus signatures retain their actual official ZIP-member layouts and colourways.',
  '- **Municipal identities:** 26 native assets across seven municipalities, including Sparwood, Sooke, Tofino, North Cowichan, Nakusp, Radium Hot Springs and Colwood. Source books, EPS and PDFs supplied geometry; distinct source colourways and historical layouts remain separate. Current website designs at Nakusp and Radium are not automatically replaced by different historical lockups.',
  '- **Regional and public bodies:** official ALC and Doctors of BC SVGs, Forest Appeals Commission and Electoral Boundaries Commission publication geometry, and Squamish-Lillooet Regional District native colour/black source files. SLRD’s source blue/gold differs from its website raster and is retained separately.',
  '- **Transit:** the 24 March 2022 TransLink board deck supplied white CMBC, West Coast Express, SkyTrain and TransLink source variants. Differently coloured rasters are preserved; a white vector is not asserted to be an exact colour replacement.',
  '- **BC Treaty Commission:** the initially unavailable official white SVG was retrieved successfully. The bounded follow-up also recovered a gold/charcoal stacked design from the **proceedings of the November 2007 conference (PDF created in March 2008)**, and a white vertical/right-aligned design from the 2018 annual report. A printed 2008 publication date was not independently verified. Later upload-directory dates are not treated as publication or adoption dates.', '',
  'The accepted asset list, publisher URLs, page/file locators, dates, hashes and extraction notes are in [acquisitions.json](acquisitions.json). [report.json](report.json) lists every subject receiving assets and all coverage-state changes.', '',
  '### NVIT: rider and eagle history preserved as raster evidence', '',
  'The NVIT material is significant historical evidence, but **none of these five acquired specimens is a native vector**. Printed/scanned texture and the actual source colours were retained. No rider or eagle was traced or redrawn.', '',
  '| Source specimen | Evidence and date limit |', '|---|---|',
  ...nvit.map((row) => `| ${link(row.asset.sourcePage ?? row.asset.sourceUrl, row.asset.label)} | ${row.asset.sourceDate}. ${row.asset.notes} |`), '',
  'The rider-circle design is documented in the 26 May 1989 advertisement; the rider-with-initials layout is documented in April 1999; the eagle appears in the March 2006 advertisement. The **2012 reporting-year Carbon Neutral Action Report was compiled into a PDF in June 2013**. Its reporting year therefore does not establish a 2012 printing/adoption date. These sightings do not establish the exact rider-to-eagle transition or prove exclusive periods of use.', '',
  '## Airports', '',
  `The airport work added **${airportAssets.length} files: ${report.airportSummary.acceptedNativeSvg} native SVGs and ${report.airportSummary.acceptedRasters} authentic raster specimens**. Native artwork is now held for **${report.airportSummary.nativeSubjectsAfter} of ${airportSubjects.length} gallery airport collections**, up from ${report.airportSummary.nativeSubjectsBefore}. **${airportGaps.length} airport collections still lack a native vector.**`, '',
  'The native finds include Nanaimo’s 2005 mountain/aircraft wordmark, 2010–2015 flight-path colourways and complete tagline layouts, its later black treatment, YVR’s 2007 “Beyond, Every Day.” reverse lockup, and the 2016 Pacific Heliport Services operator emblem. The PHS mark is the shared operator identity held under Vancouver Harbour Heliport; its source blue differs from the existing 2022 raster. Historical rasters include Nanaimo’s 2004 blue mark, Smithers’ 2014 alphorn design, Campbell River’s earlier eagle and later stacked layout, Delta’s illustrated airpark mark, and the Columbia Valley wing/script layout.', '',
  'All **22 originally wholly raster-only airport collections** received a source/publication search. One, Vancouver Harbour Heliport/PHS, gained native artwork. The remaining 21 are listed below. “Unresolved” means a suitable source was not verified; original vectors may still exist.', '',
  '| Airport still without native artwork | Current research result |', '|---|---|',
  ...airportGaps.map((subject) => { const row = airportResearch.coverage.find((record) => `airport-${record.subjectId.toLowerCase()}` === subject.id); return `| ${subject.label ?? subject.name} | ${row?.finding ?? 'See airport source ledger.'} |` }), '',
  'Fresh research covered **28 of the 34 gallery airport subjects**; six already-vector-covered subjects were baseline review only. The earlier repository research also records **53 additional facilities**. Northern Rockies, Dawson Creek and Powell River received fresh targeted searches; the other **50 were not independently searched in this pass**. This is not an exhaustive new search of all 87 facilities or the larger provincial directory.', '',
  'See [the airport coverage ledger](source-ledgers/airport-followup.json) and [airport research notes](source-ledgers/airport-research-notes.md) for exact source inspections, unavailable requests and unsearched facilities.', '',
  '## Research-only material and earlier sightings', '',
  '- **Three Tourism Radium native variants** — colour, black and white — remain under [related-proposals](related-proposals). The 2012 guide labels them proposed/suggested Tourism organizational artwork. Independent use/adoption was not established, so they are not counted as municipal gallery assets.',
  '- **Nanaimo Port Authority’s 2016 sail/wordmark SVG** remains under [related-artwork](related-artwork). It contains 29 original native paths, but no registered port subject was found. It is not assigned to Nanaimo Airport or the municipality and is excluded from gallery acquisition counts.',
  '- **Metro Vancouver Transit Police’s 2022 white lockup** corroborates the existing reversed design as an earlier `alsoSeen` source. The [source extraction](corroborating-sources/metro-vancouver-transit-police-2022-white.svg) is retained for research, not added as duplicate gallery artwork. The earlier sighting does not establish adoption, and differences in source serialization/placement are not described as byte/path identity.', '',
  'These four proposed/unregistered specimens and the Transit Police corroborating extraction are **excluded from the accepted acquisition count**.', '',
  '## Coverage by family', '',
  '“Fresh activity” below includes discovery and failed retrieval as well as actual source-logo inspection. It does not mean all eras/designs within that family were checked.', '',
  '| Family | Subjects | Native before | Native now | Still without native | Fresh activity |', '|---|---:|---:|---:|---:|---:|',
  ...perFamily.map((family) => `| ${family.label} | ${family.subjectsAfter} | ${family.nativeBefore} | ${family.nativeAfter} | ${family.subjectsWithoutNativeAfter} | ${family.freshResearchActivitySubjects} |`), '',
  '## Complete gap register and next actions', '',
  `[remaining-gaps.json](remaining-gaps.json) includes **every one of the ${subjectGaps.length} current subjects without native artwork** and **every one of the ${classifiedDesignGaps.length} gallery designs without a native version**. Each subject has its current status, source leads, registered next action, a focused next step, and whether its research in this pass went beyond the inventory audit. Each design retains its individual source records and a next action.`, '',
  `It also records **${rasterVersionFollowups.length} raster versions within vector-covered designs** that have no explicit verified exact-match \`preferredVector\` link. These are source-comparison follow-ups, not an assertion that all such rasters lack any equivalent held vector.`, '',
  'The next useful work is to inspect specific remaining sources and original masters, while preserving subject ownership and historical distinctions. Shared identities and unconfirmed distinct identities are research questions, not invitations to borrow a parent logo. Raster-only NVIT specimens, internal-master leads such as Bulkley-Nechako, blocked public sources, and unresolved airport originals remain explicit open work.', '',
  '## Verification and scope limits', '',
  `The audit checked all **${validation.acceptedFiles} accepted files** for presence and recorded SHA256 agreement. The **${validation.nativeSvgFilesChecked} newly accepted native SVGs** parsed successfully, contained native geometry, and had no image, live-text, script or foreignObject elements or external href dependencies. These structural checks complement the source/extraction evidence; they do not independently prove fidelity or validate all pre-existing gallery files.`, '',
  'The current application modules, frozen baseline and acquisition manifest are fingerprinted in report.json. Rebuilding the audit also checks that every baseline design remains present, no baseline native design loses coverage, and acquisition IDs agree with integration data. Gallery UI/display/download testing is documented separately in [VALIDATION.md](VALIDATION.md).', '',
  ...(validation.pendingVisualReviewReceipts.length || validation.unspecifiedVisualReviewReceipts.length ? [`Visual-review receipt status: ${validation.pendingVisualReviewReceipts.length} accepted records still say pending and ${validation.unspecifiedVisualReviewReceipts.length} do not contain a top-level visualReview field. The audit does not convert those metadata states into a claim of completed universal visual review. Source-specific notes and separate QA evidence remain authoritative.`, ''] : []),
  ...limits.map((limit) => `- ${limit}`), '',
  '## Files and reproducibility', '',
  '- [baseline.json](baseline.json): frozen 851-subject / 1,083-design starting inventory.',
  '- [acquisitions.json](acquisitions.json): integrated source assets and separately retained research-only material.',
  '- [report.json](report.json): machine-computed before/after counts, family summaries, changed coverage, accepted-file validation and input hashes.',
  '- [remaining-gaps.json](remaining-gaps.json): complete current subject/design gap register and explicit raster-version follow-ups.',
  '- [source-ledgers/index.json](source-ledgers/index.json): curated source-check receipts and research notes, normalized to remove temporary absolute paths.',
  '- [source-ledgers/research-activity.json](source-ledgers/research-activity.json): exact subject-level fresh-activity records and inspection levels.',
  '- [build-audit.mjs](build-audit.mjs): recomputes report.json, remaining-gaps.json and this README without changing app data or artwork.', '',
  'Run `node research/identity/vector-recovery-2026-11-26/build-audit.mjs` from the repository. The compact source ledgers intentionally omit downloaded PDFs, raw HTML and large intermediate images. `unbundled/` names in receipts identify omitted working files; publisher URLs, source locators and available hashes are retained. Working-note totals may precede final duplicate reconciliation; this audit and acquisitions.json supply the integrated totals.', '',
]
fs.writeFileSync(path.join(directory, 'README.md'), md.join('\n'))
console.log(JSON.stringify({ before, after, acquisitions: report.acquisitionSummary.acceptedAssets, nativeSvg: report.acquisitionSummary.nativeSvgAssets, rasters: report.acquisitionSummary.rasterAssets, freshRegisteredSubjects: registeredActivity.length, subjectGaps: subjectGaps.length, designGaps: classifiedDesignGaps.length, rasterVersionFollowups: rasterVersionFollowups.length, preservedBaselineDesigns: report.coverageChanges.baselineDesignsPreserved }, null, 2))
