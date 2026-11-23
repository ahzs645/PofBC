// The political parties catalogue, read for the Parties view.
//
// Every record keeps the package's distinctions: a dated specimen proves use on a day, not adoption;
// a Commons upload or Drive timestamp dates a file, not a design; a registered-name change is an
// organizational event, not a logo change. Parties without recovered artwork stay in the roster with
// their gaps, so an absence reads as unresearched or unfound rather than as never having had a logo.

import { PARTY_DATA } from './partyData.js'
import { partyPlace } from './partyLinks.js'
export { partyIdFor, partyPlace, partyPlaceFor } from './partyLinks.js'

export const PARTIES_AS_OF = PARTY_DATA.asOf
export const PARTY_SCOPE = PARTY_DATA.scope
export const PARTY_SOURCES = PARTY_DATA.sources
export const PARTY_GROUPS = PARTY_DATA.groups
export const PARTY_EVENTS = PARTY_DATA.events

const assetById = new Map(PARTY_DATA.assets.map((asset) => [asset.id, asset]))
export const partyAsset = (id) => assetById.get(id) ?? null

const sortKey = (value) => String(value ?? '9999')

/**
 * A party's designs, oldest first. A design is one arrangement; its colourways and formats are its
 * files. The lineage cards give each design's order; a design they leave out falls back to its
 * earliest dated file.
 */
const designsOf = (partyId) => {
  const files = PARTY_DATA.assets.filter((asset) => asset.party === partyId)
  const cards = new Map(PARTY_GROUPS.flatMap((group) => group.designs).map((card) => [card.id, card]))
  const ids = [...new Set(files.map((asset) => asset.design))]
  return ids.map((id) => {
    const assets = files.filter((asset) => asset.design === id)
    const card = cards.get(id)
    const representative = (card && assetById.get(card.representative)) ?? assets[0]
    const sortDate = card?.sortDate ?? assets.map((asset) => asset.dateFrom).filter(Boolean).sort()[0] ?? null
    return { id, representative, assets: [representative, ...assets.filter((asset) => asset !== representative)], sortDate }
  }).sort((a, b) => sortKey(a.sortDate).localeCompare(sortKey(b.sortDate)))
}

const groupOf = (partyId) => PARTY_GROUPS.find((group) => group.parties.includes(partyId)) ?? null

export const PARTIES = PARTY_DATA.parties.map((record) => {
  const designs = designsOf(record.id)
  return {
    ...record,
    designs,
    files: designs.reduce((sum, design) => sum + design.assets.length, 0),
    // The latest design stands for the party on its card; its earliest stands for where the record begins.
    logo: designs.at(-1)?.representative ?? null,
    group: groupOf(record.id)?.id ?? null
  }
})

const byId = new Map(PARTIES.map((party) => [party.id, party]))
export const partyById = (id) => byId.get(String(id ?? '')) ?? null

/** The other parties shown in the same lineage — CCF beside the NDP, BC Liberal beside BC United. */
export const lineageOf = (party) => {
  const group = PARTY_GROUPS.find((entry) => entry.id === party.group)
  return group ? { ...group, members: group.parties.map(partyById).filter(Boolean) } : null
}

const EVENT_LABELS = {
  'observed-visual-use': 'Logo seen in use',
  'specimen-observation': 'Logo specimen',
  'logo-specimen': 'Logo specimen',
  'logo-observed': 'Logo seen in use',
  'name-observed': 'Name seen in print',
  'organizational-name-observation': 'Name seen in print',
  'brand-launch': 'Brand launched',
  'registered-name-change': 'Registered name changed',
  deregistration: 'Deregistered',
  'legislative-representation': 'Seats in the Legislature',
  'formation-reorganisation': 'Formed or reorganized',
  'fragmentation-electoral-labels': 'Electoral labels divided',
  split: 'Split',
  'successor-party-formation': 'Successor party formed',
  'party-formation': 'Party formed',
  formation: 'Party formed',
  'campaign-suspension': 'Campaign suspended',
  'caucus-joining': 'Members joined caucus',
  'caucus-departures': 'Members left caucus'
}
export const eventLabel = (event) => EVENT_LABELS[event.type] ?? event.type.replace(/-/g, ' ').replace(/^./, (c) => c.toUpperCase())

/** A party's dated events, oldest first; undated ones last. */
export const partyHistory = (party) => PARTY_EVENTS
  .filter((event) => event.parties.includes(party.id))
  .sort((a, b) => sortKey(a.dateFrom).localeCompare(sortKey(b.dateFrom)) || Number(a.visual) - Number(b.visual))

/** Every source a party's page rests on, each once, in the package's numbering. */
export const partySources = (party) => {
  const ids = [
    ...party.sourceIds,
    ...partyHistory(party).flatMap((event) => event.sourceIds),
    ...party.designs.flatMap((design) => design.assets.map((asset) => asset.source.id))
  ].filter(Boolean)
  const known = [...new Set(ids)].map((id) => ({ id, ...PARTY_SOURCES[id] })).filter((source) => source.url)
  const urls = new Set(known.map((source) => source.url))
  // A file whose source has no number in the bibliography still names its page.
  const unnumbered = party.designs.flatMap((design) => design.assets)
    .filter((asset) => !asset.source.id && asset.source.url && !urls.has(asset.source.url))
    .map((asset) => ({ id: null, url: asset.source.url, title: asset.source.title }))
  return [...known, ...new Map(unnumbered.map((source) => [source.url, source])).values()]
    .sort((a, b) => sortKey(a.id).localeCompare(sortKey(b.id)))
}

const STATUS_LABELS = {
  'researched-gap': 'Researched, no artwork found',
  'no-authenticated-logo': 'No authenticated logo',
  'no-separate-logo-verified': 'No separate logo verified',
  'not-a-single-party-identity': 'Not a single party',
  'name-specimens-only': 'Name specimens only',
  'dated-campaign-lettering-only': 'Campaign lettering only',
  partial: 'Partial collection',
  'dated-emblems-and-name-specimens-found': 'Dated emblems and specimens',
  'selected-originals-and-historical-specimens': 'Originals and historical specimens',
  'current-originals-and-selected-historical-specimens': 'Current originals and historical specimens',
  'current-original-suite-and-selected-historical-logos': 'Current suite and historical logos'
}
export const statusLabel = (party) => STATUS_LABELS[party.status] ?? party.status.replace(/-/g, ' ')

const ASSET_CLASSES = {
  'official-original': 'Official original',
  'source-extraction': 'Cropped from a dated source',
  'archival-raster': 'Archival image',
  'third-party-vector': 'Third-party vector'
}
export const assetClassLabel = (asset) => ASSET_CLASSES[asset.assetClass] ?? asset.assetClass

const KINDS = {
  'party-logo': 'Party logo',
  logo: 'Party logo',
  'party-logo-specimen': 'Party logo, dated specimen',
  'leader-lockup': 'Leader lockup',
  'riding-campaign-lockup': 'Riding campaign lockup',
  'campaign-wordmark': 'Campaign wordmark',
  'campaign-wordmark-specimen': 'Campaign lettering',
  'name-specimen': 'Name specimen'
}
export const kindLabel = (asset) => KINDS[asset.kind] ?? 'Logo'

/** Browsers show these; EPS files are offered for download only. */
export const isViewable = (asset) => ['PNG', 'JPG', 'SVG', 'WEBP'].includes(asset.format)

const fold = (value) => String(value ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLocaleLowerCase('en-CA').replace(/[^\p{L}\p{N}]+/gu, ' ')

/** Parties matching a search, in the roster's order: those with artwork first, by how much. */
export const searchParties = ({ query = '', scope = 'artwork' } = {}) => {
  const words = fold(query).trim().split(/\s+/).filter(Boolean)
  return PARTIES.filter((party) => {
    if (scope === 'artwork' && !party.files) return false
    if (scope === 'gaps' && party.files) return false
    const text = fold([party.name, party.id, ...party.aliases].join(' '))
    return words.every((word) => text.includes(word))
  })
}

export const PARTY_COUNTS = {
  parties: PARTIES.length,
  withArtwork: PARTIES.filter((party) => party.files).length,
  files: PARTY_DATA.assets.length,
  designs: PARTIES.reduce((sum, party) => sum + party.designs.length, 0),
  sources: Object.keys(PARTY_SOURCES).length,
  events: PARTY_EVENTS.length
}

/** A date as precise as its source: a year stays a year. */
export const formatPartyDate = (date) => {
  if (!date) return 'Date unknown'
  if (/^\d{4}$/.test(date)) return date
  if (/^\d{4}-\d{2}$/.test(date)) return new Intl.DateTimeFormat('en-CA', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${date}-01T00:00:00Z`))
  if (/^\d{4}-\d{2}-\d{2}$/.test(date)) return new Intl.DateTimeFormat('en-CA', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${date}T00:00:00Z`))
  return date
}

