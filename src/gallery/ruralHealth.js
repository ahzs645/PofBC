import artwork from '../../research/identity/rural-health/artwork.json' with { type: 'json' }
import { RURAL_HEALTH_BODIES, RURAL_HEALTH_LINKS, rccbc, jsc, division, researchNetwork, rtvs, ruralSources as s } from '../government/ruralHealth.js'

const eras = [
  { id: 'rccbc-integrated-lettering', label: 'RCCbc lettering in the landscape', years: 'Seen 2013–2017',
    note: 'The 2013 guide prints two taglines. The 2016 guide uses a shorter education line. The 2017 forum report places the horizontal signature in its header and the stacked signature in its footer.',
    marks: ['rccbc-original-horizontal', 'rccbc-original-education-tagline', 'rccbc-original-stacked'], sources: [s.guide, s.education, s.forum] },
  { id: 'rccbc-grey-mountains', label: 'Grey mountains above the river', years: 'Seen 2018–2023',
    note: 'RCCbc’s May 2018 banner already shows the grey peaks and circular sun. The green tagline appears on later publications, including a November 2023 report that continued to use this design after the website relaunch.',
    marks: ['rccbc-grey-mountain-landscape', 'rccbc-grey-mountain-tagline'], sources: [s.banner, s.visits, s.conference] },
  { id: 'rccbc-blue-mountains', label: 'Blue mountains beside the full name', years: 'Seen from 2022',
    note: 'RCCbc announced its updated identity on November 26, 2022 and credited Evelyn Alec with the First Nations elements in the logo. A December job description shows the blue mountains beside the stacked name.',
    marks: ['rccbc-blue-mountain-landscape'], sources: [s.launch] }
]
const details = {
  [rccbc]: { from: 2007, cover: 'rccbc-blue-mountain-landscape', eras },
  [jsc]: { from: 2001 },
  [researchNetwork]: { from: 2010, cover: 'rhsrnbc-mountains-river' }
}
export const RURAL_HEALTH_COLLECTIONS = RURAL_HEALTH_BODIES.filter(body => artwork[body.id]).map(body => ({
  id: body.id, name: body.name, shortName: body.shortName, kind: body.kind, current: true, status: 'asset-collected',
  notes: [body.description, body.historyNote].filter(Boolean).join(' '), ...details[body.id], assets: artwork[body.id]
}))

const next = {
  [rccbc]: 'Locate a native source for the 2016 education tagline, a credit for the original landscape, and dated records of its introduction and first redesign. The RCCbc communications team manages the media toolkit.',
  [division]: 'Locate the division’s dated identity standards for the GPSC signature.',
  [researchNetwork]: 'Ask the RHSRNbc team for the original blue and white logo files and for the designer and introduction date.',
  [rtvs]: 'Trace the original 2021 hummingbird signature in a dated launch publication.',
  [jsc]: 'Locate the joint signature in a native vector file.',
  'doctors-of-bc': 'Locate the association’s standalone signature and a dated identity guide.'
}
const kinds = { 'clinical-network': 'health-service', 'medical-division': 'health-agency', 'health-research-network': 'health-agency' }
const subjects = new Set([...RURAL_HEALTH_BODIES.map(body => body.id), 'university-of-british-columbia', 'university-of-northern-bc'])
export const RURAL_HEALTH_SUBJECTS = RURAL_HEALTH_BODIES.map(body => ({
  id: body.id, name: body.name, label: body.shortName, graphNode: body.id, aliases: body.aliases,
  family: 'specialist-health', scope: 'institution', kind: kinds[body.kind] ?? body.kind,
  priority: 2, ...(body.id === rccbc && { programDeliveryPartner: true }), salaryEmployers: [], collectionIds: artwork[body.id] ? ['collected-' + body.id] : [],
  sources: body.sources, note: body.description, nextAction: next[body.id],
  relations: RURAL_HEALTH_LINKS.filter(row => row.from === body.id && subjects.has(row.to))
    .filter((row, index, rows) => rows.findIndex(other => other.to === row.to) === index)
    .map(row => ({ subject: row.to, type: 'related-to', label: row.role }))
}))
