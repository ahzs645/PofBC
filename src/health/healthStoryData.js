import { HEALTH_BOUNDARIES } from './healthBoundaries.generated.js'

export const BOUNDARIES = HEALTH_BOUNDARIES
export const AREAS = HEALTH_BOUNDARIES.areas
export const SOURCE_REPORT = 'https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf'
export const STATCAN_MAP = 'https://www150.statcan.gc.ca/n1/pub/82-221-x/00401/images/pdf/4195184-eng.pdf'
export const CONSOLIDATION_SOURCE = 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001'

// Each framework is one way the province was divided. The OAG exhibits and the
// Statistics Canada map are the printed sources; the 2001 layer is rebuilt
// from the boards and councils that amalgamated into each new authority.
export const FRAMEWORKS = [
  { id: 'boards', label: 'Regional boards', year: '1997', kind: 'Regional health board', title: 'Eleven regional health boards',
    blurb: 'Where population was concentrated, a regional board ran hospitals and community health services for its area.',
    source: { title: 'BC Auditor General, 1997/98 Report 3, Exhibit 3', url: `${SOURCE_REPORT}#page=28` } },
  { id: 'councils', label: 'Community councils', year: '1997', kind: 'Community health council', title: 'Thirty-four community health councils',
    blurb: 'Everywhere outside the board areas, local councils governed health services community by community.',
    source: { title: 'BC Auditor General, 1997/98 Report 3, Exhibit 4', url: `${SOURCE_REPORT}#page=29` } },
  { id: 'societies', label: 'Service societies', year: '1997', kind: 'Community health services society', title: 'Seven community health services societies',
    blurb: 'Societies delivered shared services, such as public health and home care, across groups of council areas.',
    source: { title: 'BC Auditor General, 1997/98 Report 3, Exhibit 5', url: `${SOURCE_REPORT}#page=30` } },
  { id: 'regions-2000', label: 'Statistical regions', year: '2000', kind: 'Statistical health region', title: 'Twenty statistical health regions',
    blurb: 'Statistics Canada reported health data for twenty regions, keeping some areas that had merged administratively apart.',
    source: { title: 'Statistics Canada, Health Indicators, April 2001', url: STATCAN_MAP } },
  { id: 'authorities-2001', label: 'Health authorities', year: '2001', kind: 'Regional health authority', title: 'Five health authorities, 12 December 2001',
    blurb: 'The boards and councils were amalgamated into five authorities. Their boundaries here are rebuilt from those predecessors.',
    source: { title: 'B.C. Reg. 293/2001, Regional Health Boards Regulation', url: CONSOLIDATION_SOURCE } },
]
export const OVERLAY_MAP = { boards: 'boards', councils: 'councils', societies: 'societies', 'regions-2000': 'regions-2000' }
export const DEFAULT_FRAMEWORK = 'boards'
export const DEFAULT_AREA_ID = 'northern-interior-regional-health-board'

export const frameworkById = (id) => FRAMEWORKS.find((framework) => framework.id === id) ?? null
export const areasIn = (framework) => AREAS.filter((area) => area.framework === framework)

// Accepts a boundary id or an organization record id (the government view links by record).
export const areaById = (id) => id ? AREAS.find((area) => area.id === id) ?? AREAS.find((area) => area.organization?.bodyId === id) ?? null : null

export function assetUrl(path, base = '/') {
  return `${base.replace(/\/?$/, '/')}health-geography/${path.replace(/^\/+/, '')}`
}

export function readHealthPlace(search = '') {
  const params = new URLSearchParams(search)
  const area = areaById(params.get('area'))
  const requested = frameworkById(params.get('layer'))?.id
  const framework = area ? area.framework : requested ?? DEFAULT_FRAMEWORK
  return { framework, area: area?.id ?? (framework === DEFAULT_FRAMEWORK ? DEFAULT_AREA_ID : null) }
}

export function healthMapLink(id) {
  const area = areaById(id)
  const params = new URLSearchParams({ view: 'health-map' })
  if (area) {
    params.set('layer', area.framework)
    params.set('area', area.id)
  }
  return `?${params}`
}

export function filterAreas(query, framework = 'all') {
  const words = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean)
  return AREAS.filter((area) => (framework === 'all' || area.framework === framework) && words.every((word) =>
    `${area.name} ${area.organization?.officialName ?? ''} ${(area.organization?.formerNames ?? []).join(' ')} ${area.lhaNames.join(' ')}`
      .toLocaleLowerCase().includes(word)))
}

const contains = (outer, inner) => inner.lhaCodes.length > 0 && inner.lhaCodes.every((code) => outer.lhaCodes.includes(code))
const overlaps = (a, b) => a.lhaCodes.some((code) => b.lhaCodes.includes(code))

// Relationships follow from the shared LHA building blocks, so a council's
// society is the one whose LHAs contain all of the council's.
export function relatedAreas(area) {
  if (!area) return []
  const groups = []
  const add = (label, areas) => { if (areas.length) groups.push({ label, areas }) }
  const authorityFor = (bodyIds) => areasIn('authorities-2001').filter((a) => bodyIds.includes(a.organization.bodyId))
  if (area.framework === 'councils') {
    add('Served by society', areasIn('societies').filter((s) => contains(s, area)))
    add('Part of the 2000 statistical region', areasIn('regions-2000').filter((r) => overlaps(r, area)))
    add('Amalgamated into', authorityFor(area.organization?.successorIds ?? []))
  } else if (area.framework === 'boards') {
    add('Part of the 2000 statistical regions', areasIn('regions-2000').filter((r) => overlaps(r, area)))
    add('Amalgamated into', authorityFor(area.organization?.successorIds ?? []))
  } else if (area.framework === 'societies') {
    add('Council areas it served', areasIn('councils').filter((c) => contains(area, c)))
    add('Services passed to', authorityFor(area.organization?.successorIds ?? []))
  } else if (area.framework === 'regions-2000') {
    add('Regional boards in this region', areasIn('boards').filter((b) => overlaps(b, area)))
    add('Community councils in this region', areasIn('councils').filter((c) => overlaps(c, area)))
  } else if (area.framework === 'authorities-2001') {
    const members = area.predecessorIds.map(areaById).filter(Boolean)
    add('Formed from regional boards', members.filter((m) => m.framework === 'boards'))
    add('Formed from community councils', members.filter((m) => m.framework === 'councils'))
    add('Took over services of', areasIn('societies').filter((s) => s.organization?.successorIds.includes(area.organization.bodyId)))
  }
  return groups
}

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
export function formatDate(value) {
  if (!value) return null
  const [year, month, day] = value.split('-').map(Number)
  if (!month) return String(year)
  return day ? `${day} ${MONTHS[month - 1]} ${year}` : `${MONTHS[month - 1]} ${year}`
}
