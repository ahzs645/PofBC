// Public bodies connected to the identity catalogue but outside the provincial-government
// chronology. These are current, sourced catalogue records; they are never projected backwards
// into a ministry's historical responsibility or drawn as members of the provincial executive.

export const RELATED_BODIES_AS_OF = '2026-11-15'

const source = (title, url) => ({ title, url })
const TRANSIT_OVERVIEW = source('TransLink — Corporate overview', 'https://www.translink.ca/about-us/about-translink/corporate-overview')
const TRANSIT_GOVERNANCE = source('TransLink — Governance model', 'https://www.translink.ca/about-us/about-translink/governance-model')
const TRANSIT_OPERATORS = source('TransLink — Operating companies', 'https://www.translink.ca/about-us/about-translink/operating-companies')
const CMBC = source('TransLink — Coast Mountain Bus Company', `${TRANSIT_OPERATORS.url}/coast-mountain-bus-company`)
const BCRTC = source('TransLink — British Columbia Rapid Transit Company', `${TRANSIT_OPERATORS.url}/british-columbia-rapid-transit-company`)
const WCE = source('TransLink — West Coast Express', `${TRANSIT_OPERATORS.url}/west-coast-express`)
const POLICE = source('TransLink — Transit Police', `${TRANSIT_OPERATORS.url}/transit-police`)
const METRO = source('Metro Vancouver — Governance structure', 'https://metrovancouver.org/boards/governance-structure')
const POSTSECONDARY = source('Province of BC — Public post-secondary institutions', 'https://www2.gov.bc.ca/gov/content/education-training/post-secondary-education/find-a-program-or-institution/find-an-institution')
const UNBC_HISTORY = source('UNBC — History', 'https://www.unbc.ca/about-unbc/history')
const UNBC_ACT = source('University of Northern British Columbia Act, SBC 1990, c.28', 'https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/90028')

export const RELATED_BODY_KINDS = {
  'regional-transportation-authority': 'Regional transportation authority',
  'transit-company': 'Transit operating company',
  'transit-police': 'Transit police service',
  'regional-federation': 'Regional federation',
  'ferry-authority': 'Ferry authority',
  'emergency-communications': 'Emergency communications corporation',
  'statutory-authority': 'Statutory authority',
  'independent-regulator': 'Independent regulator',
  'development-trust': 'Economic development trust',
  'development-society': 'Economic development society',
  'public-university': 'Public university',
  'public-institute': 'Public institute',
  'charitable-society': 'Charitable society',
  'corporate-subsidiary': 'Corporate subsidiary'
}

/**
 * How the directory lists them: a few families a reader would recognize, rather than one heading per
 * kind, since most kinds have a single member. Grouping is presentation only; each record keeps its
 * own kind and governance.
 */
export const RELATED_BODY_GROUPS = [
  { id: 'transit', label: 'Transit in Metro Vancouver', kinds: ['regional-transportation-authority', 'transit-company', 'transit-police'] },
  { id: 'services', label: 'Regional and public services', kinds: ['regional-federation', 'ferry-authority', 'emergency-communications', 'statutory-authority', 'independent-regulator', 'corporate-subsidiary'] },
  { id: 'development', label: 'Economic development', kinds: ['development-trust', 'development-society'] },
  { id: 'learning', label: 'Education and science', kinds: ['public-university', 'public-institute', 'charitable-society'] }
]

/** The given bodies in their groups, in catalogue order, leaving out groups with none of them. */
export const groupRelatedBodies = (bodies) => {
  const groups = RELATED_BODY_GROUPS.map((group) => ({ ...group, bodies: bodies.filter((body) => group.kinds.includes(body.kind)) }))
  const grouped = new Set(RELATED_BODY_GROUPS.flatMap((group) => group.kinds))
  const rest = bodies.filter((body) => !grouped.has(body.kind))
  if (rest.length) groups.push({ id: 'other', label: 'Other organizations', kinds: [], bodies: rest })
  return groups.filter((group) => group.bodies.length)
}

const employer = (slug, label, extra = {}) => ({ slug, label, ...extra })
const relation = (id, label, description, extra = {}) => ({ id, label, description, ...extra })
const university = (id, name, shortName, officialUrl, slug) => ({
  id, name, shortName, kind: 'public-university', aliases: [shortName], officialUrl,
  description: `${name} is a public post-secondary institution in British Columbia. Its institutional identity and disclosed employer records are connected here.`,
  sources: [POSTSECONDARY], salaryEmployers: [employer(slug, name)], relationships: []
})

export const RELATED_BODIES = [
  {
    id: 'translink', name: 'South Coast British Columbia Transportation Authority', shortName: 'TransLink',
    aliases: ['TransLink', 'Greater Vancouver Transportation Authority', 'GVTA', 'SCBCTA'],
    kind: 'regional-transportation-authority', officialUrl: 'https://www.translink.ca/',
    description: 'TransLink plans and manages transportation across Metro Vancouver. Its governance includes its Board of Directors and the Mayors’ Council on Regional Transportation. It delivers services through operating companies and contractors.',
    historyNote: 'Created in 1999. Greater Vancouver Transportation Authority is an earlier name; this current catalogue record does not reconstruct its governance in every earlier year.',
    sources: [TRANSIT_OVERVIEW, TRANSIT_GOVERNANCE],
    salaryEmployers: [employer('translink', 'TransLink', { sector: 'Regional transportation' })],
    relationships: [
      relation('coast-mountain-bus-company', 'Coast Mountain Bus Company', 'Operating company'),
      relation('british-columbia-rapid-transit-company', 'British Columbia Rapid Transit Company', 'Operating company'),
      relation('west-coast-express', 'West Coast Express', 'Operating company and service'),
      relation('metro-vancouver-transit-police', 'Metro Vancouver Transit Police', 'Transit policing within the TransLink enterprise'),
      relation('metro-vancouver', 'Metro Vancouver', 'Regional planning relationship')
    ]
  },
  {
    id: 'coast-mountain-bus-company', name: 'Coast Mountain Bus Company Ltd.', shortName: 'Coast Mountain Bus Company',
    aliases: ['CMBC', 'Coast Mountain BusLink', 'SeaBus', 'Transit Security'], kind: 'transit-company',
    officialUrl: CMBC.url,
    description: 'A TransLink operating company providing most regional bus services and SeaBus. Its support services include Transit Security, which is separate from Transit Police.',
    sources: [CMBC, TRANSIT_OPERATORS],
    salaryEmployers: [employer('coast-mountain-bus-company', 'Coast Mountain Bus Company', { sector: 'Regional transportation' })],
    relationships: [relation('translink', 'TransLink', 'TransLink operating company')]
  },
  {
    id: 'british-columbia-rapid-transit-company', name: 'British Columbia Rapid Transit Company Ltd.', shortName: 'BCRTC',
    aliases: ['BCRTC', 'SkyTrain'], kind: 'transit-company', officialUrl: BCRTC.url,
    description: 'BCRTC operates and maintains the Expo and Millennium SkyTrain lines and the West Coast Express service on behalf of TransLink. It also manages the agreement with InTransitBC for Canada Line operation and maintenance.',
    sources: [BCRTC],
    salaryEmployers: [employer('british-columbia-rapid-transit-company', 'British Columbia Rapid Transit Company', { sector: 'Regional transportation' })],
    relationships: [relation('translink', 'TransLink', 'TransLink operating company'), relation('west-coast-express', 'West Coast Express', 'Operates the commuter rail service')]
  },
  {
    id: 'west-coast-express', name: 'West Coast Express Limited', shortName: 'West Coast Express', aliases: ['WCE'],
    kind: 'transit-company', officialUrl: WCE.url,
    description: 'West Coast Express is the commuter rail service between Vancouver and Mission and a company within the TransLink enterprise. The service began in 1995; its operation is managed by BCRTC.',
    sources: [WCE, BCRTC, TRANSIT_OVERVIEW],
    salaryEmployers: [employer('west-coast-express', 'West Coast Express', { sector: 'Regional transportation' })],
    relationships: [relation('translink', 'TransLink', 'Part of the TransLink enterprise'), relation('british-columbia-rapid-transit-company', 'BCRTC', 'Service operation')]
  },
  {
    id: 'metro-vancouver-transit-police', name: 'Metro Vancouver Transit Police', shortName: 'Transit Police',
    aliases: ['Transit Police', 'TransLink Security Management Ltd.', 'TSML', 'South Coast British Columbia Transportation Authority Police Service'],
    kind: 'transit-police', officialUrl: 'https://transitpolice.ca/',
    description: 'A designated policing unit providing policing across Metro Vancouver’s transit system. Oversight comes from an independent Transit Police Board. Transit Security and Transit Police are separate services.',
    sources: [POLICE, CMBC, source('TransLink — 2025 Financial Information Act filing and remuneration report', 'https://www.translink.ca/-/media/translink/documents/about-translink/corporate-reports/translink_employee_remuneration/2025-financial-information-act-filing-and-remuneration-report.pdf')],
    salaryEmployers: [
      employer('transit-police', 'Transit Police / TransLink Security Management disclosures'),
      employer('metro-vancouver-transit-police', 'Metro Vancouver Transit Police, separately filed records')
    ],
    salaryNote: 'The salary catalogue retains two employer files. These links do not merge their observations or treat matching names as the same person. The official employee disclosures identify TransLink Security Management Ltd.',
    relationships: [relation('translink', 'TransLink', 'Transit policing within the TransLink enterprise')]
  },
  {
    id: 'metro-vancouver', name: 'Metro Vancouver', shortName: 'Metro Vancouver',
    aliases: ['GVRD', 'Greater Vancouver Regional District', 'MVRD', 'Metro Vancouver Regional District'],
    kind: 'regional-federation', officialUrl: 'https://metrovancouver.org/',
    description: 'Metro Vancouver coordinates regional services through four separate legal entities and boards: Metro Vancouver Regional District, Greater Vancouver Water District, Greater Vancouver Sewerage and Drainage District, and Metro Vancouver Housing Corporation.',
    sources: [METRO, source('Metro Vancouver — About us', 'https://metrovancouver.org/about-us')],
    salaryEmployers: [employer('metro-vancouver', 'Metro Vancouver')],
    relationships: [relation('translink', 'TransLink', 'Separate regional transportation authority')]
  },
  {
    id: 'bc-ferry-authority-2003', name: 'B.C. Ferry Authority', shortName: 'BC Ferry Authority',
    aliases: ['B.C. Ferry Authority', 'BC Ferry Authority 2003'], kind: 'ferry-authority',
    officialUrl: 'https://www.bcferryauthority.com/',
    description: 'The authority created under the 2003 coastal ferry governance model holds BC Ferries’ voting share and oversees its strategic direction in the public interest. BC Ferry Services Inc. provides the ferry service; the BC Ferries Commissioner is the separate regulator.',
    historyNote: 'This is the modern authority. The historical British Columbia Ferry Authority of 1964–1977 has its own atlas record and artwork.',
    sources: [source('B.C. Ferry Authority — About us and governance model', 'https://www.bcferryauthority.com/about-us/')],
    salaryEmployers: [],
    relationships: [
      relation('bc-ferry-corporation', 'BC Ferries', 'Holds the voting share of BC Ferry Services Inc., which succeeded the British Columbia Ferry Corporation in 2003', { year: 2002, mode: 'graph' }),
      relation('bc-ferry-authority', 'British Columbia Ferry Authority, 1964–1977', 'Earlier authority with a similar name', { year: 1970, mode: 'graph' })
    ]
  },
  {
    id: 'e-comm', name: 'E-Comm 9-1-1', shortName: 'E-Comm', aliases: ['E-Comm', 'EComm', 'E-Comm 911'],
    kind: 'emergency-communications', officialUrl: 'https://www.ecomm911.ca/',
    description: 'An emergency communications corporation serving local governments and public safety agencies. Its shareholders participate in its radio network and appoint its board. It operates on a cost-recovery basis.',
    sources: [source('E-Comm — Shareholders', 'https://www.ecomm911.ca/about-e-comm/shareholders/')], salaryEmployers: [], relationships: []
  },
  {
    id: 'land-title-and-survey-authority', name: 'Land Title and Survey Authority of British Columbia', shortName: 'LTSA', aliases: ['LTSA'],
    kind: 'statutory-authority', officialUrl: 'https://ltsa.ca/',
    description: 'A non-governmental, self-funded statutory corporation operating British Columbia’s land title and survey systems and other land-related registries. LandSure Systems Ltd. is its wholly-owned subsidiary.',
    sources: [source('LTSA — About us', 'https://ltsa.ca/about-ltsa/'), source('LTSA — Our mandate', 'https://ltsa.ca/about-ltsa/ltsa-mandate/')],
    salaryEmployers: [],
    relationships: [relation('landsure-systems', 'LandSure Systems Ltd.', 'Wholly-owned subsidiary that develops and operates LTSA’s land-registry technology')]
  },
  {
    id: 'landsure-systems', name: 'LandSure Systems Ltd.', shortName: 'LandSure', aliases: ['LandSure', 'LandSure Systems'],
    kind: 'corporate-subsidiary', officialUrl: 'https://www.landsure.ca/',
    description: 'A wholly-owned subsidiary of the Land Title and Survey Authority of British Columbia. It develops and operates LTSA’s mission-critical technology for land-related transactions, as part of the business model that funds LTSA’s continued improvement.',
    sources: [source('LandSure Systems — Welcome', 'https://www.landsure.ca/'), source('LTSA — About us', 'https://ltsa.ca/about-ltsa/')],
    salaryEmployers: [],
    relationships: [relation('land-title-and-survey-authority', 'Land Title and Survey Authority of British Columbia', 'Its parent and sole owner')]
  },
  {
    id: 'consumer-protection-bc', name: 'Consumer Protection BC', shortName: 'Consumer Protection BC', aliases: ['CPBC', 'Business Practices and Consumer Protection Authority'],
    kind: 'independent-regulator', officialUrl: 'https://www.consumerprotectionbc.ca/',
    description: 'A not-for-profit regulator administering consumer protection responsibilities delegated by the Province. It licenses and inspects regulated businesses, handles inquiries and investigates potential breaches.',
    sources: [source('Consumer Protection BC — About us', 'https://www.consumerprotectionbc.ca/about-us/'), source('Consumer Protection BC — Our authority and governance', 'https://www.consumerprotectionbc.ca/about-us/our-authority-governance/')], salaryEmployers: [], relationships: []
  },
  {
    id: 'etsi-bc', name: 'Economic Trust of the Southern Interior', shortName: 'ETSI-BC', aliases: ['ETSI-BC', 'SIDIT', 'Southern Interior Development Initiative Trust'],
    kind: 'development-trust', officialUrl: 'https://www.etsi-bc.ca/',
    description: 'A not-for-profit economic development trust serving the Southern Interior. Regional advisory committees and the Province appoint its directors.',
    historyNote: 'Established as SIDIT in 2006; the trust adopted the ETSI-BC name in March 2021. Those dates describe the organization and name, not adoption dates for particular logo files.',
    sources: [source('ETSI-BC — Who we are', 'https://www.etsi-bc.ca/about/')], salaryEmployers: [], relationships: []
  },
  {
    id: 'nechako-kitamaat-development-fund', name: 'Nechako-Kitamaat Development Fund Society', shortName: 'NKDF', aliases: ['NKDF', 'Nechako Kitamaat Development Fund'],
    kind: 'development-society', officialUrl: 'https://nkdf.org/',
    description: 'An economic development society supporting northern communities affected by the Kitimat-Kemano project and Nechako Reservoir. Its fund originated in contributions from the Province and Alcan; the society was incorporated in 1999.',
    sources: [source('NKDF — Program guidelines, updated June 2026', 'https://nkdf.org/how-to-apply/how-to-apply/program-guidelines')], salaryEmployers: [], relationships: []
  },
  {
    id: 'science-world', name: 'ASTC Science World Society', shortName: 'Science World', aliases: ['Science World', 'ASTC'],
    kind: 'charitable-society', officialUrl: 'https://www.scienceworld.ca/',
    description: 'Science World is a charitable non-profit science centre in Vancouver with learning programs across British Columbia. Its registered organization is ASTC Science World Society.',
    sources: [source('Science World — About us', 'https://www.scienceworld.ca/about/')], salaryEmployers: [], relationships: []
  },
  university('university-of-british-columbia', 'University of British Columbia', 'UBC', 'https://www.ubc.ca/', 'university-of-bc'),
  university('simon-fraser-university', 'Simon Fraser University', 'SFU', 'https://www.sfu.ca/', 'simon-fraser-university'),
  university('university-of-victoria', 'University of Victoria', 'UVic', 'https://www.uvic.ca/', 'university-of-victoria'),
  {
    ...university('university-of-northern-bc', 'University of Northern British Columbia', 'UNBC', 'https://www.unbc.ca/', 'university-of-northern-bc'),
    checked: '2026-11-19',
    description: 'UNBC is a public university established through legislation after a regional campaign led by the Interior University Society. Its origins and reconstructed campaign artwork are connected through the identity collection.',
    historyNote: 'The Interior University Society was incorporated on 1 December 1987. The UNBC Act passed on 22 June 1990, received assent on 6 July and came into force on 20 July. UNBC officially opened on 17 August 1994. The society and university were separate organisations; this was not a corporate rename.',
    sources: [POSTSECONDARY, UNBC_HISTORY, UNBC_ACT]
  },
  {
    id: 'bcit', name: 'British Columbia Institute of Technology', shortName: 'BCIT', aliases: ['BCIT'],
    kind: 'public-institute', officialUrl: 'https://www.bcit.ca/',
    description: 'BCIT is a public post-secondary institute in British Columbia. Its institutional identity and disclosed employer records are connected here.',
    sources: [POSTSECONDARY], salaryEmployers: [employer('bcit', 'BCIT')], relationships: []
  }
].map((body) => ({ ...body, checked: body.checked ?? RELATED_BODIES_AS_OF, chronology: 'current-catalogue' }))

const BY_ID = new Map(RELATED_BODIES.map((body) => [body.id, body]))
export const relatedBodyById = (id) => BY_ID.get(id) ?? null

/** Existing government deep links resolve these IDs to the current catalogue, never to an old year. */
export const relatedBodyPlace = (id) => relatedBodyById(id) ? { view: 'government', mode: 'related', node: id } : null

/** Name aliases aid discovery; they do not merge organizations or confer a historical identity. */
export const searchRelatedBodies = (query = '') => {
  const words = query.toLocaleLowerCase('en-CA').replace(/[^\p{L}\p{N}]+/gu, ' ').trim().split(/\s+/).filter(Boolean)
  return RELATED_BODIES.filter((body) => {
    const text = [body.name, body.shortName, ...(body.aliases ?? []), RELATED_BODY_KINDS[body.kind]].join(' ').toLocaleLowerCase('en-CA').replace(/[^\p{L}\p{N}]+/gu, ' ')
    return words.every((word) => text.includes(word))
  })
}

// Each original disclosure keeps its own employer slug and observations. Two files may link to
// the same organization, but this lookup never rewrites aliases, combines rows or matches people.
export const RELATED_SALARY_LINKS = Object.fromEntries(RELATED_BODIES.flatMap((body) => body.salaryEmployers.map((entry) => [entry.slug, { body: body.id, ...(entry.sector ? { sector: entry.sector } : {}) }])))

/** Add organization links to the two existing salary metadata shapes without changing source data. */
export const connectRelatedSalaryBodies = (index) => {
  if (!Array.isArray(index?.employers)) return index
  const entries = index.employers
  const sourceEmployerSectors = { ...index.sourceEmployerSectors }
  const connect = (entry, id) => {
    // Person index rows are [display name, sector, graph body, employer slug].
    if (Array.isArray(entry)) {
      const link = Object.hasOwn(RELATED_SALARY_LINKS, entry[3]) ? RELATED_SALARY_LINKS[entry[3]] : null
      if (!link || entry[2]) return entry
      const linked = [...entry]
      linked[2] = link.body
      if (link.sector) {
        sourceEmployerSectors[id] ??= entry[1]
        linked[1] = link.sector
      }
      return linked
    }
    const link = Object.hasOwn(RELATED_SALARY_LINKS, entry?.slug) ? RELATED_SALARY_LINKS[entry.slug] : null
    if (!link || entry.body) return entry
    return { ...entry, body: link.body, ...(link.sector ? { sourceSector: entry.sourceSector ?? entry.sector, sector: link.sector } : {}) }
  }
  return {
    ...index,
    employers: entries.map(connect),
    ...(Object.keys(sourceEmployerSectors).length ? { sourceEmployerSectors } : {})
  }
}
