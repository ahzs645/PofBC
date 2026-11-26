// Collection eligibility is independent of an organization's legal kind. This register joins
// explicit identity subjects to actual gallery entries; a source lead is never counted as artwork.
import { IDENTITY_FAMILIES, IDENTITY_SUBJECTS } from './identitySubjects.js'
import { GALLERY_COLLECTIONS, entriesOfNode } from './collections.js'
import { COLLECTION_RESEARCH, nodesOf } from './collectedCollections.js'
import { COMMISSION_FAMILY, COMMISSION_HISTORIES, commissionById } from './commissionHistory.js'
import { COLLECTING } from './collectingData.js'

export const COVERAGE_STATES = {
  'native-vector': { label: 'Vector artwork held', description: 'At least one source vector is in the gallery. This does not establish every era or an adoption date.' },
  'raster-held': { label: 'Raster specimen held', description: 'A published image is held. A clean source vector is still wanted.' },
  reconstruction: { label: 'Reconstruction held', description: 'The gallery has a reconstruction, identified separately from original artwork.' },
  'artwork-held': { label: 'Artwork held', description: 'Artwork is in the gallery; its individual evidence record describes its provenance.' },
  'source-located': { label: 'Source located', description: 'A primary source or acquisition route is recorded. No accepted artwork is counted yet.' },
  'shared-identity': { label: 'Shares another identity', description: 'The subject uses a shared identity, with the relationship and evidence recorded.' },
  'distinct-unconfirmed': { label: 'Distinct identity unconfirmed', description: 'Research has not established a separate identity. This is not a claim that one never existed.' },
  'artwork-missing': { label: 'Artwork wanted', description: 'The organization is known, but accepted artwork has not been collected.' },
  'not-catalogued': { label: 'Not yet catalogued', description: 'A candidate is recorded for further research.' }
}

export const COVERAGE_FAMILIES = [
  COMMISSION_FAMILY, ...IDENTITY_FAMILIES,
  { id: 'atlas-crowns', label: 'Other Crown corporations', note: 'The existing Crown corporation acquisition register, including historical bodies.' },
  { id: 'atlas-health', label: 'Other health bodies', note: 'The existing health-authority register, including historical boards and councils.' }
]

const unique = (items, key = (item) => item.id) => [...new Map(items.map((item) => [key(item), item])).values()]
const fold = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
const words = (value) => fold(value).split(/[^\p{L}\p{N}]+/u).filter(Boolean)
const vectorProvenance = new Set(['original_supplied', 'published_vector', 'extracted_from_official_vector'])
const reconstructedProvenance = new Set(['reconstructed', 'third_party_reconstruction', 'synthetic_name_variant'])

/** The strongest file evidence held, without treating a reconstructed SVG as a source vector. */
export const evidenceForEntries = (entries) => {
  const evidence = { vector: 0, raster: 0, reconstruction: 0, other: 0 }
  for (const entry of unique(entries)) {
    const provenance = entry.identity?.provenance
    const assets = entry.versions ?? (entry.asset ? [entry.asset] : [])
    if (assets.some((asset) => asset.isVector && !asset.reconstruction) || (!assets.length && vectorProvenance.has(provenance))) evidence.vector++
    else if (assets.some((asset) => !asset.isVector && !asset.reconstruction) || ['published_raster', 'archival_raster'].includes(provenance)) evidence.raster++
    else if (assets.some((asset) => asset.reconstruction) || reconstructedProvenance.has(provenance)) evidence.reconstruction++
    else evidence.other++
  }
  return evidence
}

const stateOf = (subject, evidence) => {
  if (evidence.vector) return 'native-vector'
  if (evidence.raster) return 'raster-held'
  if (evidence.reconstruction) return 'reconstruction'
  if (evidence.other) return 'artwork-held'
  if (['shared-identity', 'distinct-unconfirmed'].includes(subject.identityStatus)) return subject.identityStatus
  if (subject.identityStatus === 'artwork-missing') return 'artwork-missing'
  if (subject.sources?.length) return 'source-located'
  return subject.graphNode ? 'artwork-missing' : 'not-catalogued'
}

/**
 * A subject's own entries establish coverage, including ones held in a shared historical shelf.
 * A graph link to a parent is context, never evidence that a child's logo has been collected.
 * Entry ownership prevents a successor's vector or a charity's design from filling another gap.
 */
export const buildIdentityCoverage = (subjects, collections) => subjects.map((subject) => {
  const ids = new Set([...(subject.collectionIds ?? []), `collected-${subject.id}`])
  const owner = subject.entryOwner ?? subject.id
  const preferred = (collection) => ids.has(collection.id) || collection.aliases?.some((id) => ids.has(id))
  const held = unique(collections.filter((collection) => entriesOfNode(collection, owner).length > 0))
    .sort((a, b) => Number(Boolean(preferred(b))) - Number(Boolean(preferred(a))))
  const entries = unique(held.flatMap((collection) => entriesOfNode(collection, owner)))
  const evidence = evidenceForEntries(entries)
  const state = stateOf(subject, evidence)
  return { ...subject, collections: held, entries, evidence, state, stateLabel: COVERAGE_STATES[state].label, hasArtwork: entries.length > 0 }
})

// Retain the complete earlier queue without making its two legal kinds the eligibility rule.
// The curated register takes precedence when it has a more specific account of the same subject.
const curatedIds = new Set(IDENTITY_SUBJECTS.map((subject) => subject.id))
export const LEGACY_IDENTITY_SUBJECTS = COLLECTING.filter((body) => !curatedIds.has(body.id)).map((body) => {
  const research = COLLECTION_RESEARCH.get(body.id)
  return {
    id: body.id, label: body.shortName || body.name, name: body.name, kind: body.kind,
    family: body.kind === 'health-authority' ? 'atlas-health' : 'atlas-crowns',
    graphNode: body.id, graphYear: body.current ? null : body.to ? body.to - 1 : body.from,
    aliases: [body.shortName].filter(Boolean), scope: 'core', priority: 3,
    collectionIds: GALLERY_COLLECTIONS.filter((collection) => nodesOf(collection).includes(body.id)).map((collection) => collection.id),
    entryOwner: body.id, sources: [], relations: [], salaryEmployers: [],
    identityStatus: research?.status === 'source-found' ? undefined : 'artwork-missing',
    // A source-found record may have a narrative rather than a structured URL. Preserve that
    // state below, without inventing a link or implying that the source contains accepted artwork.
    sourceLocated: research?.status === 'source-found',
    note: research?.notes || 'Retained from the atlas acquisition register.',
    nextAction: 'Find and compare a source specimen; establish whether a distinct identity was used.',
    current: body.current, from: body.from, to: body.to, legacy: true
  }
})

const registered = [...IDENTITY_SUBJECTS, ...LEGACY_IDENTITY_SUBJECTS]
const registeredIds = new Set(registered.map((subject) => subject.id))
const additionalCommissions = COMMISSION_HISTORIES.filter(({ id }) => !registeredIds.has(id)).map((record) => ({
  id: record.id, label: record.name, name: record.name, family: COMMISSION_FAMILY.id,
  kind: record.kind ?? 'agency', scope: 'core', priority: 3,
  graphNode: record.atlas === false ? null : record.id, graphYear: record.graphYear,
  aliases: [], collectionIds: [], salaryEmployers: [], relations: [], sources: [],
  identityStatus: 'artwork-missing', note: record.history,
  nextAction: 'Locate a dated publication bearing this commission’s own artwork.'
}))

export const IDENTITY_COVERAGE = buildIdentityCoverage([...registered, ...additionalCommissions], GALLERY_COLLECTIONS)
  .map((subject) => !subject.hasArtwork && subject.sourceLocated
    ? { ...subject, state: 'source-located', stateLabel: COVERAGE_STATES['source-located'].label }
    : subject)
const byId = new Map(IDENTITY_COVERAGE.map((subject) => [subject.id, subject]))
export const identitySubjectById = (id) => byId.get(id) ?? null
export const familyById = (id) => COVERAGE_FAMILIES.find((family) => family.id === id) ?? null
export const subjectsForCollection = (id) => IDENTITY_COVERAGE.filter((subject) => subject.collections.some((collection) => collection.id === id))

/** Aliases find their subject; family matches appear as context rather than interchangeable names. */
export const searchIdentitySubjects = (query, subjects = IDENTITY_COVERAGE) => {
  const terms = words(query)
  if (!terms.length) return []
  return subjects.filter((subject) => {
    const text = fold([subject.label, subject.name, commissionById.get(subject.id)?.name, ...(subject.aliases ?? [])].join(' '))
    return terms.every((word) => text.includes(word))
  })
}

export const coverageSummary = (subjects = IDENTITY_COVERAGE) => ({
  subjects: subjects.length,
  held: subjects.filter((subject) => subject.hasArtwork).length,
  sources: subjects.filter((subject) => subject.state === 'source-located').length,
  unresolved: subjects.filter((subject) => !subject.hasArtwork && subject.state !== 'source-located').length
})

/** A municipality's regional district, or the provincial layer's own wording when it has none. */
export const NO_REGIONAL_DISTRICT = 'No separate regional district'
export const regionOf = (subject) => subject.municipal ? subject.municipal.regionalDistrict ?? NO_REGIONAL_DISTRICT : null

export const filterIdentityCoverage = (subjects, { query = '', family = '', state = '', scope = '', region = '' } = {}) => {
  const matches = query.trim() ? new Set(searchIdentitySubjects(query, subjects).map((subject) => subject.id)) : null
  return subjects.filter((subject) => (!matches || matches.has(subject.id)) && (!family || subject.family === family || (family === COMMISSION_FAMILY.id && commissionById.has(subject.id))) &&
    (!region || regionOf(subject) === region) &&
    (!scope || subject.scope === scope) && (!state || (state === 'held' ? subject.hasArtwork : state === 'missing' ? !subject.hasArtwork : subject.state === state)))
}

// A relation is recorded once, on the subject it describes. Its other end shows the inverse, so a
// parent lists what points to it. Membership of a family is browsing context, not a relation.
export const INVERSE_RELATION_LABELS = {
  'co-publisher-with': 'Co-publisher with',
  'renamed-to': 'Renamed from',
  'amalgamated-into': 'Amalgamated with',
  'charitable-partner-of': 'Official charitable partner ·',
  'related-to': 'Related to',
  'part-of': 'Includes',
  'received-operations-from': 'Operations transferred to',
  'transferred-operations-to': 'Received operations from',
  'service-of': 'Provides the service',
  'owned-by': 'Owns',
  'shareholder-of': 'Voting share held by',
  'operated-by': 'Operates',
  'listed-by': '2024–25 sector roster',
  'used-by': 'Uses',
  'predecessor-of': 'Successor of',
  'successor-of': 'Predecessor of',
  'campaigned-for': 'Campaign led by',
  'shares-identity-with': 'Shares identity with'
}

const incoming = new Map()
for (const subject of IDENTITY_COVERAGE) {
  for (const relation of subject.relations ?? []) {
    if (!byId.has(relation.subject)) continue
    incoming.set(relation.subject, [...(incoming.get(relation.subject) ?? []), { type: relation.type, subject: subject.id, source: relation }])
  }
}

/** The subject's own relations, then those recorded on others that point to it, each with its target. */
export const relationsOf = (subject) => ({
  outgoing: (subject.relations ?? []).map((relation) => ({ ...relation, target: byId.get(relation.subject) })).filter((relation) => relation.target),
  incoming: (incoming.get(subject.id) ?? []).map((relation) => ({ ...relation, target: byId.get(relation.subject) }))
    .sort((a, b) => a.type.localeCompare(b.type) || a.target.label.localeCompare(b.target.label, 'en-CA'))
})
