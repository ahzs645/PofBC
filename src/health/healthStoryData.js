import { HEALTH_CATALOGUE } from './healthAreas.generated.js'

export const CATALOGUE = HEALTH_CATALOGUE
export const MAPS = HEALTH_CATALOGUE.maps
export const AREAS = HEALTH_CATALOGUE.areas
export const CHAPTERS = [
  { id: 'before-2001', label: 'Before 2001', title: 'A different health map', mapId: 'regions-2000' },
  { id: 'regional-boards', label: 'Regional boards', title: 'Eleven regional boards', mapId: 'boards' },
  { id: 'community-councils', label: 'Local councils', title: 'Care closer to home', mapId: 'councils' },
  { id: 'service-societies', label: 'Service societies', title: 'Shared community services', mapId: 'societies' },
  { id: 'consolidation', label: 'The consolidation', title: 'What changed in 2001', mapId: null },
  { id: 'compare-boundaries', label: 'Compare boundaries', title: 'Which boundaries still align?', mapId: null },
]
export const DEFAULT_AREA_ID = 'northern-interior-regional-health-board'
export const SOURCE_REPORT = 'https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf'
export const CONSOLIDATION_SOURCE = 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001'
export const PUBLIC_SOURCES = [
  { id: 'oag', title: 'Original board, council and society maps', detail: 'BC Auditor General, March 1998; printed pages 24–26.', url: `${SOURCE_REPORT}#page=28` },
  { id: 'statcan-2000', title: 'Twenty statistical health regions', detail: 'Statistics Canada, Health Indicators, April 2001. Statistical geography is separate from the legal board boundaries.', url: MAPS[0].sourceUrl },
  { id: '1995-order', title: 'The earlier twenty boards', detail: 'M597/1995: Schedule A lists the boards; Schedule B describes their territories.', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0597_1995#page=2' },
  { id: '2001-order', title: 'The December 2001 consolidation', detail: 'B.C. Reg. 293/2001, original deposited regulation.', url: CONSOLIDATION_SOURCE },
  { id: 'pgmaps', title: 'Existing PGMaps health boundaries', detail: 'Health authorities, health service delivery areas and local health areas.', url: 'https://pgmaps.ahmadjalil.com/data/boundaries/BCMoH/index.json' },
  { id: 'bc-data', title: 'BC Ministry of Health boundary data', detail: 'Contains information licensed under the Open Government Licence – British Columbia. The PGMaps snapshots are used as modern comparisons.', url: 'https://catalogue.data.gov.bc.ca/dataset/local-health-area-boundaries' },
]

export function assetUrl(path, base = '/') {
  return `${base.replace(/\/?$/, '/')}health-geography/${path.replace(/^\/+/, '')}`
}
export const areaById = (id) => AREAS.find((area) => area.id === id) ?? null
export const areasIn = (mapId) => AREAS.filter((area) => area.mapId === mapId)
export const mapById = (id) => MAPS.find((map) => map.id === id) ?? null
export const chapterForArea = (id) => CHAPTERS.find((chapter) => chapter.mapId === areaById(id)?.mapId)?.id ?? 'compare-boundaries'

export function readHealthPlace(search = '') {
  const params = new URLSearchParams(search)
  const requestedArea = params.get('area')
  const area = areaById(requestedArea)?.id ?? DEFAULT_AREA_ID
  const requestedChapter = params.get('chapter')
  const chapter = CHAPTERS.some((entry) => entry.id === requestedChapter)
    ? requestedChapter : requestedArea && areaById(requestedArea) ? chapterForArea(area) : CHAPTERS[0].id
  return { area, chapter }
}

export function healthMapLink(bodyId, chapter) {
  const area = areaById(bodyId)
  const params = new URLSearchParams({ view: 'health-map' })
  if (area) params.set('area', area.id)
  if (chapter) params.set('chapter', chapter)
  else if (area) params.set('chapter', chapterForArea(area.id))
  return `?${params}`
}

export function comparisonFor(comparison, areaId) {
  const area = areaById(areaId)
  const sourceMapId = { boards: 'oag-1997-98-exhibit-3', councils: 'oag-1997-98-exhibit-4', societies: 'oag-1997-98-exhibit-5' }[area?.mapId]
  return comparison?.bodyMatches?.find((entry) => area?.bodyId
    ? entry.bodyId === area.bodyId
    : area && entry.bodyId === null && entry.mapId === sourceMapId && entry.sourceLegendNumber === area.number) ?? null
}

export function candidateCodes(match, layer) {
  const key = { lha: 'candidateLhaCodes', hsda: 'candidateHsdaCodes', ha: 'candidateHaCodes', historical: 'historicalFeatureCodes' }[layer]
  return new Set((match?.[key] ?? []).map(String))
}

// Institutional names, modern geometry and historical legal territories are distinct evidence.
export function evidenceLabel(match) {
  if (!match) return 'Boundary match not assessed'
  return match.label || ({ candidate: 'Candidate boundary', candidate_aggregate: 'Candidate combination of modern areas',
    partial: 'Partial geographic correspondence', not_matched: 'No supported boundary match', unresolved: 'Boundary relationship unresolved' }[match.status] ?? 'Modern boundary candidate')
}

export function featuresFor(collection, codes) {
  return (collection?.features ?? []).filter((feature) => codes.has(String(feature.properties?.code ?? feature.id)))
}

export function filterAreas(query, mapId = 'all') {
  const words = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean)
  return AREAS.filter((area) => (mapId === 'all' || area.mapId === mapId) &&
    words.every((word) => `${area.name} ${area.sourceLabel} ${area.number}`.toLocaleLowerCase().includes(word)))
}
