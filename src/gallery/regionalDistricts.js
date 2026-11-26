import districts from '../../research/identity/regional-districts-2026-11-25/districts.json' with { type: 'json' }
import artwork from '../../research/identity/regional-districts-2026-11-25/artwork.json' with { type: 'json' }
import { EXPANDED_IDENTITY_BODIES } from './expandedIdentityData.js'
import { NORTHERN_TRAVEL_GUIDE_ARTWORK } from './northernTravelGuides.js'

export const REGIONAL_DISTRICT_FAMILY = {
  id: 'regional-districts',
  label: 'Regional districts',
  description: 'Corporate logos, earlier designs and municipal membership across British Columbia’s 27 regional districts.'
}

const incorporationSource = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/local-governments/finance/local-government-statistics/local_government_legal_name_and_incorporation_dates_2023.pdf'
const metro = EXPANDED_IDENTITY_BODIES.find(({ id }) => id === 'metro-vancouver')
const guideArtworkOf = (id) => NORTHERN_TRAVEL_GUIDE_ARTWORK[id] ?? []
// Preserve the two related-body routes originally added with the travel-guide coverage.
const relatedDistricts = new Set(['regional-district-bulkley-nechako', 'regional-district-fraser-fort-george'])

const putDistrict = ({ id, name, incorporated, dissolved, website, label = name, aliases = [], history, historySources = [], relations = [], nextAction }) => {
  const assets = [...(artwork[id] ?? []), ...guideArtworkOf(id), ...(id === metro.id ? metro.assets : [])]
  return {
    id, name, label, aliases, relations,
    kind: 'regional-district', family: REGIONAL_DISTRICT_FAMILY.id, scope: 'core', priority: 2,
    graphNode: id === metro.id || relatedDistricts.has(id) ? id : null,
    salaryEmployers: id === metro.id ? [id] : [],
    collectionIds: assets.length ? [`collected-${id}`] : [],
    regionalDistrict: { incorporated, dissolved, current: !dissolved },
    note: history ?? `Incorporated on ${new Date(incorporated).toLocaleDateString('en-CA', { dateStyle: 'long', timeZone: 'UTC' })}.`,
    sources: [
      ...(website ? [{ title: 'Official district website', url: website }, { title: 'Provincial incorporation register', url: incorporationSource }] : []),
      ...historySources,
      ...[...new Map(assets.map(({ sourceUrl, sourceLocator, specimenDate, role }) => [
        sourceUrl, { title: role === 'historical' ? 'Historical artwork source' : 'Logo source', url: sourceUrl, note: [sourceLocator, specimenDate].filter(Boolean).join(' · ') }
      ])).values()]
    ],
    nextAction: nextAction ?? 'Compare earlier dated letterheads and publications for distinct designs and adoption records.'
  }
}

export const REGIONAL_DISTRICT_SUBJECTS = districts.map(putDistrict)
const byName = new Map(REGIONAL_DISTRICT_SUBJECTS.filter((subject) => subject.regionalDistrict.current).map((subject) => [subject.name, subject]))
export const regionalDistrictOf = (municipal) => byName.get(municipal?.regionalDistrict)

export const REGIONAL_DISTRICT_RELATED_BODIES = REGIONAL_DISTRICT_SUBJECTS.filter(({ id }) => relatedDistricts.has(id))
  .map(({ id, name, label, aliases, note, sources }) => ({
    id, name, shortName: label, aliases, kind: 'regional-federation', officialUrl: sources[0].url,
    description: note, sources, salaryEmployers: [], relationships: []
  }))

export const REGIONAL_DISTRICT_BODIES = REGIONAL_DISTRICT_SUBJECTS.map((subject) => {
  const { id, label, name, regionalDistrict, graphNode } = subject
  const newAssets = artwork[id] ?? []
  const currentAssets = [...(id === metro.id ? metro.assets : []), ...newAssets.filter(({ role }) => role !== 'historical')]
  const addedHistory = newAssets.filter(({ role }) => role === 'historical')
  const historicalAssets = [...addedHistory, ...guideArtworkOf(id)]
  const section = (id, label, assets) => ({ id, label, marks: assets.filter(({ variantOf }) => !variantOf).map(({ id, designId }) => designId ?? id) })
  return {
    id, name, graphNode,
    shortName: label, kind: 'regional-district', shelf: REGIONAL_DISTRICT_FAMILY.id,
    from: Number(regionalDistrict.incorporated?.slice(0, 4)) || undefined,
    to: regionalDistrict.dissolved,
    current: regionalDistrict.current, notes: subject.note, status: 'asset-collected',
    cover: id === metro.id ? 'source-expanded-metro-vancouver-wordmark' : currentAssets.find(({ variantOf }) => !variantOf)?.id,
    artworkSections: [
      section('regional-current', 'Current artwork', currentAssets),
      section('regional-historical', 'Historical artwork', historicalAssets)
    ],
    // Northern travel-guide artwork is appended by the shared collected-body loader.
    assets: [...currentAssets, ...addedHistory]
  }
}).filter(({ assets }) => assets.length)
