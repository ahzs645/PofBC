import { HISTORICAL_BODIES } from '../government/historyData.js'
import { GALLERY_COLLECTIONS } from './collections.js'
import { nodesOf } from './collectedCollections.js'
import { identitySubjectById } from './identityCoverage.js'
import { SIFERP_RENAME } from './forrex.js'
import { COUNCIL_SUCCESSION } from './scienceCouncilHistory.js'
import { LIQUOR_SUCCESSION } from './liquorHistory.js'

const regionalAuthorities = new Set(['fraser-health', 'interior-health', 'northern-health', 'vancouver-coastal-health', 'island-health'])
const reorganizationDate = '2001-12-12'
const amalgamationOrder = {
  title: 'Regional Health Boards Regulation, Schedule A',
  url: 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v44n25_293-2001#ScheduleA'
}
const reorganizationAnnouncement = {
  title: 'Regional health reorganization announcement',
  url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002HLTH0009-000402.htm'
}
const boundaryOrder = {
  title: 'Regional Health Boards Regulation amendment, B.C. Reg. 52/2002',
  url: 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v45n05_52-2002'
}
const cariboo = 'cariboo-community-health-services-society'
const upperIsland = 'upper-island-central-coast-community-health-services-society'
const serviceDetails = {
  [cariboo]: {
    'interior-health': {
      note: 'South Cariboo, Central Cariboo Chilcotin and Bella Coola initially went to Interior Health.',
      source: { title: 'Interior Health reorganization announcement', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002HLTH0005-000135.htm' }
    },
    'northern-health': {
      note: 'Northern Health took over the society’s Quesnel services.',
      source: { title: 'Health services bargaining agreement, Quesnel entry', url: 'https://negotech.service.canada.ca/eng/agreements/11/1118104a.pdf' }
    }
  },
  [upperIsland]: {
    'island-health': { note: 'Comox Valley, Campbell River/Nootka, Mount Waddington and the Central Coast initially went to Vancouver Island.' }
  },
  'kootenay-boundary-community-health-services-society': {
    'interior-health': {
      source: { title: 'Interior Health reorganization announcement', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002HLTH0005-000135.htm' }
    }
  },
  'coast-garibaldi-community-health-services-society': {
    'vancouver-coastal-health': {
      source: { title: 'Vancouver Coastal Health reorganization announcement', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002HLTH0003-000131.htm' }
    }
  }
}

const amalgamations = HISTORICAL_BODIES
  .filter((body) => body.ended === reorganizationDate && regionalAuthorities.has(body.became))
  .map(({ id, became }) => ({ from: id, to: became, type: 'amalgamated', date: reorganizationDate, source: amalgamationOrder }))

const serviceTransfers = HISTORICAL_BODIES.flatMap(({ id, servicesPassedTo }) => (servicesPassedTo ?? [])
  .filter((to) => regionalAuthorities.has(to))
  .map((to) => ({
    from: id, to, type: 'services', date: reorganizationDate, source: reorganizationAnnouncement, ...serviceDetails[id]?.[to]
  })))

const coastalTransfers = [
  ['bella-coola-and-district-transitional-health-authority', 'Bella Coola’s area moved from Interior Health.'],
  [cariboo, 'Bella Coola’s area, formerly served by the society, moved from Interior Health.'],
  ['central-coast-transitional-health-authority', 'The Central Coast area moved from Vancouver Island Health Authority.'],
  [upperIsland, 'The Central Coast area, formerly served by the society, moved from Vancouver Island Health Authority.']
].map(([from, note]) => ({ from, to: 'vancouver-coastal-health', type: 'territory', date: '2002-03-18', note, source: boundaryOrder }))

const relationships = [
  {
    from: 'provincial-apprenticeship-board', to: 'industry-training-and-apprenticeship-commission', type: 'replaced', date: '1997-11-28',
    note: 'The commission took over provincial apprenticeship governance when its Act came into force.',
    source: { title: 'Auditor General of British Columbia, Exhibit 4', url: 'https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-2008-11-01-major-renovation-trades-training-british-columbia.pdf#page=33' }
  },
  {
    from: 'industry-training-and-apprenticeship-commission', to: 'industry-training-authority', type: 'replaced', date: '2004-01-02',
    note: 'On the commission’s wind-up, the Industry Training Authority Act took effect.',
    source: { title: 'ITAC final financial statements, note 2', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2003-04/sup-e/industry-training-apprenticeship-commission-fs-2003-04.pdf#page=7' }
  },
  {
    from: 'industry-training-authority', to: 'skilledtradesbc', type: 'legal-rename', date: '2022-12-01',
    note: 'The authority continued under the name SkilledTradesBC.',
    source: { title: 'Province of British Columbia, December 2022 announcement', url: 'https://news.gov.bc.ca/releases/2022AEST0074-001775' }
  },
  ...LIQUOR_SUCCESSION,
  ...COUNCIL_SUCCESSION,
  SIFERP_RENAME,
  {
    from: 'bc-safety-authority', to: 'technical-safety-bc', type: 'renamed', date: '2017-09-20',
    note: 'BC Safety Authority adopted Technical Safety BC as its operating name.',
    source: { title: 'BC Safety Authority announcement', url: 'https://www.newswire.ca/news-releases/bc-safety-authority-is-now-technical-safety-bc-646053913.html' }
  },
  ...amalgamations,
  ...serviceTransfers,
  ...coastalTransfers
]

// History connects body IDs in either direction. Collection placement and artwork ownership stay
// with the gallery, so every reference to a body leads to the same collection or register entry.
const collectionsByBody = new Map(GALLERY_COLLECTIONS.flatMap((collection) => {
  const ids = collection.historyId ? [collection.historyId, ...nodesOf(collection)] : nodesOf(collection)
  return ids.map((id) => [id, collection])
}))
const historyByBody = new Map()
const empty = Object.freeze([])
const noHistory = Object.freeze({ predecessors: empty, successors: empty })

for (const relationship of relationships) {
  const { from, to } = relationship
  for (const [id, side, other] of [[from, 'successors', to], [to, 'predecessors', from]]) {
    const collection = collectionsByBody.get(other)
    const subject = identitySubjectById(other)
    if (!collection && !subject) throw new Error(`Missing gallery history record: ${other}`)
    if (!historyByBody.has(id)) historyByBody.set(id, { predecessors: [], successors: [] })
    historyByBody.get(id)[side].push({ ...relationship, id: other, label: subject?.label ?? collection.label, collection })
  }
}

// A collection that holds a line of names (CONTINUATIONS, and the researched histories with
// graphNodes) is read by its own id. That id answers for the whole line: every name's history,
// less the steps within the line, which its eras already show. So SkilledTradesBC's page keeps the
// commission its first name replaced, and Innovate BC's the 2004 merger that formed its first name.
for (const collection of GALLERY_COLLECTIONS) {
  const nodes = nodesOf(collection)
  const key = collection.historyId ?? collection.graphNode
  if (!key || nodes.length < 2) continue
  const ids = [...new Set([key, ...nodes])]
  const outside = (side) => ids.flatMap((id) => historyByBody.get(id)?.[side] ?? []).filter((row) => row.collection !== collection)
  const combined = { predecessors: outside('predecessors'), successors: outside('successors') }
  if (combined.predecessors.length || combined.successors.length) historyByBody.set(key, combined)
  else historyByBody.delete(key)
}

export const galleryHistoryOf = (id) => historyByBody.get(id) ?? noHistory
export const hasGalleryHistory = (id) => historyByBody.has(id)
