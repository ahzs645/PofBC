// B.C.'s current municipalities as register subjects: 161 in the Province's legally defined
// administrative-areas layer, plus shíshálh Nation Government District, which is classified
// separately. Read from research/identity/municipalities-2026-11-15/municipalities.json, the
// 15 November 2026 gallery audit's join of that layer to CivicInfo BC's municipal directory.
//
// No municipal corporate logo is held yet. Salary, council-pay and heraldry links point to the
// site's existing records by their exact keys; none of them is evidence of a corporate logo, and
// none merges records. Arms granted to a predecessor stay the predecessor's. Regional-district
// membership is context, not ownership.

import { MUNICIPAL_IDENTITY_BODIES } from './municipalIdentityData.js'
import registry from '../../research/identity/municipalities-2026-11-15/municipalities.json' with { type: 'json' }

export const MUNICIPAL_REGISTRY_DIR = 'research/identity/municipalities-2026-11-15'
export const MUNICIPAL_AS_OF = registry.asOf

export const MUNICIPAL_FAMILIES = [
  {
    id: 'municipalities',
    label: 'Municipalities',
    description: 'B.C.’s 161 municipalities and shíshálh Nation Government District: corporate logos wanted, with links to their arms, council pay and salary records.'
  }
]

/** A municipality's legal classification, as the provincial layer gives it. */
export const MUNICIPAL_KIND_LABELS = {
  'municipal-city': 'City',
  'municipal-district': 'District municipality',
  'municipal-town': 'Town',
  'municipal-township': 'Township',
  'municipal-village': 'Village',
  'municipal-island': 'Island municipality',
  'municipal-regional': 'Regional municipality',
  'municipal-resort': 'Resort municipality',
  'municipal-mountain-resort': 'Mountain resort municipality',
  'self-government-district': 'Self-government district'
}

const KIND_OF_CLASSIFICATION = {
  City: 'municipal-city',
  District: 'municipal-district',
  Town: 'municipal-town',
  Township: 'municipal-township',
  Village: 'municipal-village',
  'Island Municipality': 'municipal-island',
  'Regional Municipality': 'municipal-regional',
  'Resort Municipality': 'municipal-resort',
  'Mountain Resort Municipality': 'municipal-mountain-resort',
  'Self-government district': 'self-government-district'
}

const slug = (text) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
export const municipalSubjectId = (name) => `municipality-${slug(name)}`

const https = (url) => typeof url === 'string' && url.startsWith('https://')
const uniqueFolded = (values) => {
  const seen = new Set()
  return values.filter((value) => {
    const key = value?.normalize('NFKC').toLocaleLowerCase('en-CA').trim()
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

const leadSources = (lead, collected) => {
  if (!lead) return []
  const checked = lead.checked ? `, checked ${lead.checked}` : ''
  return [
    https(lead.asset) && { title: `Official website logo (${lead.format})`, url: lead.asset, note: collected ? 'Archived in the gallery byte-for-byte. Its download date does not date the logo.' : `${lead.verification}${checked}. A located source, not yet accepted artwork; it does not date the logo.` },
    https(lead.sourcePage) && { title: 'Official source page', url: lead.sourcePage },
    https(lead.evidencePage) && lead.evidencePage !== lead.sourcePage && { title: 'Identity and history evidence', url: lead.evidencePage, note: lead.note },
    https(lead.guidePage) && { title: 'Visual identity guidance', url: lead.guidePage, note: lead.guideStatus },
    https(lead.guideFile) && { title: 'Visual identity guide file', url: lead.guideFile, note: lead.guideStatus }
  ].filter(Boolean)
}

const NO_LOGO = 'No corporate logo is held yet. Its arms, council pay and salary records are linked where the site has them; none of them is a corporate logo.'
const HELD = 'Its logo is held as its official website serves it. Arms, council pay and salary records are linked where the site has them.'
const COLLECTED = new Set(MUNICIPAL_IDENTITY_BODIES.map((body) => body.id))

const subjectOf = (record) => {
  const lead = record.logoLead
  const inLayer = record.provincialId.startsWith('bc-lgaa-')
  const legal = record.legalName && record.legalName !== record.name ? [record.legalName] : []
  const council = record.councilMunicipality && record.councilMunicipality !== record.name ? [record.councilMunicipality] : []
  const region = record.regionalDistrict && !/^No separate/.test(record.regionalDistrict) ? record.regionalDistrict : null
  const sources = [
    ...leadSources(lead, COLLECTED.has(municipalSubjectId(record.name))),
    inLayer
      ? { title: 'Provincial legally defined administrative area record', url: record.boundarySource, note: `Provincial identifier ${record.provincialId}.` }
      : { title: 'Enabling legislation', url: record.boundarySource, note: 'Not in the provincial municipal layer; recorded separately as a self-government district.' },
    https(record.namingSource) && { title: 'Provincial naming update', url: record.namingSource },
    { title: 'CivicInfo BC municipal directory', url: record.directorySource }
  ].filter(Boolean)
  const where = region ? `in the ${region}` : 'with no separate regional-district parent'
  return {
    id: municipalSubjectId(record.name),
    label: record.name,
    name: record.legalName || record.name,
    kind: KIND_OF_CLASSIFICATION[record.classification],
    family: 'municipalities',
    graphNode: null,
    aliases: uniqueFolded([...legal, ...council, ...(record.aliases ?? []), ...(record.historicalNames ?? [])]).filter((alias) => alias !== record.name),
    collectionIds: [],
    salaryEmployers: record.salaryEmployer ? [record.salaryEmployer] : [],
    priority: lead ? 1 : 2,
    scope: 'core',
    sources,
    nextAction: lead?.nextStep && lead.nextStep !== '—'
      ? lead.nextStep
      : 'Find the corporate logo on an official municipal source, then record the file, its source and any adoption evidence.',
    note: [
      `${MUNICIPAL_KIND_LABELS[KIND_OF_CLASSIFICATION[record.classification]]} ${where}.`,
      record.scope !== 'current municipality' ? record.auditNote : null,
      COLLECTED.has(municipalSubjectId(record.name)) ? HELD : NO_LOGO
    ].filter(Boolean).join(' '),
    relations: [],
    // A located logo file is a source lead; without one, the logo is still wanted.
    ...(lead ? {} : { identityStatus: 'artwork-missing' }),
    municipal: {
      provincialId: record.provincialId,
      inProvincialLayer: inLayer,
      classification: record.classification,
      regionalDistrict: region,
      website: record.website,
      councilMunicipality: record.councilMunicipality,
      historicalNames: record.historicalNames ?? [],
      heraldry: record.heraldry,
      scope: record.scope
    }
  }
}

export const MUNICIPAL_SUBJECTS = registry.municipalities.map(subjectOf)
  .sort((a, b) => a.label.localeCompare(b.label, 'en-CA'))

/** Dissolved municipalities: historical coverage only, never current subjects. */
export const HISTORICAL_MUNICIPALITIES = registry.historical

/** "Regional District of Central Kootenay" files under Central Kootenay; the no-parent row goes last. */
const regionKey = (region) => region === 'No separate regional district' ? '\uffff' : region.replace(/^Regional District of /, '').replace(/ Regional District$/, '')
export const MUNICIPAL_REGIONS = [...new Set(MUNICIPAL_SUBJECTS.map((subject) => subject.municipal.regionalDistrict ?? 'No separate regional district'))]
  .sort((a, b) => regionKey(a).localeCompare(regionKey(b), 'en-CA'))
