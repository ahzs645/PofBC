import artwork from './tourismPartnerArtwork.json' with { type: 'json' }
import sectorArtwork from './tourismSectorArtwork.json' with { type: 'json' }
import { TOURISM_SECTOR_RECORDS } from './tourismSectorPartners.js'
import { NORTHERN_TRAVEL_GUIDE_ARTWORK, NORTHERN_TRAVEL_GUIDE_RECORDS } from './northernTravelGuides.js'

const checked = '2026-11-25'
const dbc = 'https://www.destinationbc.ca/'
const climate = dbc + 'what-we-do/destination-management/bc-tourism-climate-resiliency-initiative/'
const vcmPage = dbc + 'who-we-are/regional-community-industry-partner/vancouver-coast-mountain/'
const regions = ['cariboo-chilcotin-coast-tourism', 'kootenay-rockies-tourism', 'northern-bc-tourism', 'thompson-okanagan-tourism', '4tvi-stewardship', 'vancouver-coast-mountains']
const [cariboo, kootenay, north, tota, island, vcm] = regions
const formerVCM = 'vancouver-coast-mountains-tourism-society'
const group = '4vi-group'
const formerIsland = 'tourism-vancouver-island'
const itbc = 'indigenous-tourism-bc'
const secretariat = 'bc-regional-tourism-secretariat'
const sustainability = 'bc-tourism-sustainability-network'
const resiliency = 'bc-tourism-resiliency-network'
const initiative = 'bc-tourism-climate-resiliency-initiative'
const source = (title, url) => ({ title, url })
const regionalDirectory = source('Destination BC regional partner directory', dbc + 'who-we-are/regional-community-industry-partner/')
const province2003 = source('Province of BC regional tourism associations backgrounder, March 2003', 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2003CSE0028-000289-Attachment1.htm')
const governance = source('Kootenay Rockies Tourism governance manual, regional partnership history', 'https://www.krtourism.ca/wp-content/uploads/2024/12/Governance-Manual-January-26-2024.pdf')
const caribooReport = source('CCCTA and CCCTMA Annual Service Report 2022–2023', 'https://industry.landwithoutlimits.com/resources/uploads/2023/11/CCCT-CCCTMA-2023-Annual-Report-Low-Res_email_ver.pdf')
const vcmContract = source('Destination BC agreement and amendments with society No. 9836', dbc + 'content/uploads/2018/06/VCM-FY1415-Contracts_Combined.pdf')
const vcmNewsletter = source('Destination BC VCM newsletter, February 2024', dbc + 'newsletters/2024/02/vcm-february-1-2024.html')
const islandGroup = source('4VI Group social enterprise model', 'https://www.4vigroup.com/home')
const launch2020 = source('Destination BC network launch announcement, April 2020', dbc + 'news/bc-tourism-resiliency-network/')
const partner = (subject, label = 'Regional program partner', type = 'related-to') => ({ subject, label, type })
const regionalPartner = partner('destination-bc', 'Regional partner of Destination BC')
const withRegion = partner(vcm, 'Community destination partner in the VCM region')
const operation = partner(group, 'Operation within the 4VI social enterprise group', 'part-of')
const organization = 'tourism-association'
const program = 'tourism-initiative'

export const TOURISM_PARTNER_FAMILY = {
  id: 'tourism-destination-management',
  label: 'Tourism and destination management',
  description: 'Regional and community tourism organizations, Indigenous tourism, and province-wide tourism partnerships and sector campaigns.'
}

const records = [
  {
    id: vcm, name: 'Vancouver, Coast & Mountains Tourism Region', shortName: 'Vancouver, Coast & Mountains', kind: 'tourism-region',
    aliases: ['VCM', 'Vancouver Coast and Mountains', 'South West BC'], officialUrl: vcmPage,
    description: 'Destination BC directly manages this regional tourism operation serving Metro Vancouver, the Sunshine Coast, the Sea-to-Sky Corridor, and the Fraser Valley and Fraser Canyon.',
    history: 'Destination BC’s industry announcement documents its regional delivery role in 2020. The 2023 Sustainability Playbook and 2024 Sustainability Toolkit show the stylized VCM initials. The 2024 toolkit credits the regional team and GreenStep Solutions. The handover date and the mark’s first use remain open.',
    relations: [partner('destination-bc', 'Regional operation managed by Destination BC', 'operated-by')],
    sources: [source('Destination BC regional program and governance', vcmPage), launch2020,
      source('Destination BC Sustainability Playbook, July 2023, cover and credits', dbc + 'content/uploads/2023/07/The-Vancouver-Coast-Mountains-Sustainability-Playbook_Final_July-25-V5.pdf'),
      source('Destination BC VCM Sustainability Toolkit release, April 2024', dbc + 'newsletters/2024/04/vcm-april-18-2024.html')],
    cover: 'vcm-stacked'
  },
  {
    id: formerVCM, name: 'Vancouver, Coast and Mountains Tourism Region', shortName: 'Former VCM tourism society', kind: organization,
    aliases: ['Vancouver Coast and Mountains Tourism Association', 'VCM tourism society', 'vcmbc.com', 'coastandmountains.bc.ca'], historical: true,
    description: 'A separate nonprofit society with its own board represented tourism businesses and communities across the region.',
    history: 'An August 1996 fax documents the association and its executive director. The Province described its board and nonprofit status in 2003. Destination BC’s contract names the society and incorporation certificate No. 9836. The 2014 amendments document transition funding and extend the contract through July 31, 2015. A regional governance account records the end of the independent association following Destination BC’s creation in 2013. The incorporation, handover and legal dissolution dates remain open.',
    relations: [partner(vcm, 'Earlier independent organization serving the same region', 'predecessor-of'), partner('destination-bc', 'Contracted regional delivery documented in 2012–2015')],
    sources: [source('Doug Banner correspondence, August 12, 1996, PDF p. 20', 'https://bcnature.org/wp-content/uploads/2020/10/44-PAS-Framework-for-Effective-Discussion-and-Negotiation-044.pdf#page=20'), province2003, vcmContract, governance],
    nextAction: 'Find a signed registry record and a verified logo in society-issued letterhead, archived vcmbc.com pages or regional visitor guides.'
  },
  {
    id: cariboo, name: 'Cariboo Chilcotin Coast Tourism Association', shortName: 'Cariboo Chilcotin Coast Tourism', kind: organization, from: 1962,
    aliases: ['CCCTA', 'Cariboo Tourist Association', 'Land Without Limits'],
    officialUrl: 'https://industry.landwithoutlimits.com/',
    description: 'This regional nonprofit works with Destination BC and represents rural tourism operators in the Cariboo, Chilcotin and Central Coast.',
    history: 'The association dates its history to 1962. Its 2022–23 service report is issued jointly with the Cariboo Chilcotin Coast Tourism Marketing Association. The shared report uses a mountain-and-river mark, while the February 2024 guidelines also document use of the earlier maple-leaf design.',
    relations: [regionalPartner], sources: [regionalDirectory, province2003, caribooReport, vcmNewsletter],
    cover: 'cccta-mountains'
  },
  {
    id: 'cariboo-chilcotin-coast-tourism-marketing', name: 'Cariboo Chilcotin Coast Tourism Marketing Association', kind: organization,
    aliases: ['CCCTMA'], identityStatus: 'shared-identity',
    description: 'The regional marketing association uses Municipal and Regional District Tax proceeds for tourism marketing and related programs.',
    history: 'The 2022–23 Annual Service Report gives the two associations separate operating accounts and a common cover featuring the mountain-and-river signature. The marketing association describes that year as its sixth year of investing the tax proceeds.',
    relations: [partner(cariboo, 'Joint service report uses one regional signature', 'shares-identity-with')],
    sources: [caribooReport],
    nextAction: 'Check marketing-association publications and tax-program records for a signature used in its own name.'
  },
  {
    id: kootenay, name: 'Kootenay Rockies Tourism Association', shortName: 'Kootenay Rockies Tourism', kind: organization, from: 1978,
    aliases: ['KRT', 'Tourism Rockies', 'BC Rockies'], officialUrl: 'https://www.krtourism.ca/company-profile/',
    description: 'The regional nonprofit provides development, marketing and industry support in southeastern BC.',
    history: 'Kootenay Rockies Tourism dates its operation to 1978. The Province called the funding partner Tourism Rockies in 2003. From April 2015 its partner projects moved away from the integrated Kootenay Rockies and Super, Natural BC logo. Its separate mountain-and-river signature is documented in horizontal and stacked layouts.',
    relations: [regionalPartner], sources: [source('Kootenay Rockies Tourism company profile', 'https://www.krtourism.ca/company-profile/'), province2003, governance,
      source('Kootenay Rockies Tourism notice on the 2015 partner logo transition', 'https://www.krtourism.ca/february-2015-newsletter/')],
    cover: 'krt-horizontal'
  },
  {
    id: north, name: 'Northern British Columbia Tourism Association', shortName: 'Northern BC Tourism', kind: organization,
    aliases: ['NBCTA', 'Northern BC Tourism Association', 'Travel Northern BC'], officialUrl: 'https://www.travelnbc.com/about-us/',
    description: 'The regional nonprofit supports and promotes tourism from Haida Gwaii to the Rockies and north to the territorial borders.',
    history: 'The Province lists the association as a regional funding partner in 2003. Its 2012–15 travel guides show the historical map and regional co-brand, plus the Northern BC app. The circular tree-and-water symbol appears in the stacked 2024 specimen and the association’s horizontal signature.',
    relations: [regionalPartner], sources: [province2003, regionalDirectory, source('Northern BC Tourism Association, About us', 'https://www.travelnbc.com/about-us/')],
    cover: 'nbcta-horizontal'
  },
  {
    id: tota, name: 'Thompson Okanagan Tourism Association', kind: organization, from: 1957,
    aliases: ['TOTA', 'Okanagan Valley Tourist Association', 'Okanagan Similkameen Tourist Association'], officialUrl: 'https://www.totabc.org/about',
    description: 'The industry-led nonprofit society coordinates destination development, stewardship and marketing in the Thompson Okanagan region.',
    history: 'Founded in 1957 and incorporated in 1963, the association began as the Okanagan Valley Tourist Association, later became the Okanagan Similkameen Tourist Association, and adopted its current name in 1997. It moved to a no-fee stakeholder model in 2009.',
    relations: [regionalPartner],
    sources: [source('TOTA association history and governance', 'https://www.totabc.org/about'), source('TOTA stakeholder model', 'https://www.totabc.org/join-tota'),
      source('TOTA Sustainable Tourism Observatory annual reports', 'https://www.totabc.org/legacy-stewardship-projects/insto-member')],
    cover: 'tota-stacked-current'
  },
  {
    id: formerIsland, name: 'Tourism Association of Vancouver Island', shortName: 'Tourism Vancouver Island / 4VI', kind: organization, historical: true,
    aliases: ['Tourism Vancouver Island', 'TVI', 'TAVI', '4VI'],
    description: 'Tourism Vancouver Island was the former public-facing name of the regional tourism society. The society began doing business as 4VI in April 2022 as it shifted to a nonprofit social enterprise.',
    history: 'The 2003 provincial backgrounder identifies Tourism Vancouver Island as the regional funding organization. A 2021 society meeting notice records the legal name. The earlier Tourism Vancouver Island and 2022-era 4VI signatures predate the newer group and 4TVI lockups. The earlier trading identities are documented here independently of the current group structure.',
    relations: [partner(group, 'The group grew out of the 2022 social enterprise transition'), partner(island, 'Current regional stewardship operation')],
    sources: [province2003, source('Tourism Association of Vancouver Island 2021 AGM notice', 'https://forvi.ca/notice-of-annual-general-meeting/'),
      source('Destination BC account of the April 2022 shift', dbc + 'newsletters/2022/07/destination-bc-directions-july-28-2022.html'), islandGroup],
    cover: '4vi-2022'
  },
  {
    id: group, name: '4VI Social Enterprise Group', shortName: '4VI Group', kind: 'tourism-collaboration',
    aliases: ['4VI'], officialUrl: 'https://www.4vigroup.com/',
    description: 'The Vancouver Island social enterprise group brings together 4TVI Stewardship, 4EVER Strategies and 4GOOD Social Impact Fund.',
    history: 'The group traces its model to the April 2022 transition from Tourism Vancouver Island to 4VI. Its group signature accompanies three distinct operating identities.',
    sources: [islandGroup, source('Destination BC account of the April 2022 shift', dbc + 'newsletters/2022/07/destination-bc-directions-july-28-2022.html')], cover: '4vi-group-signature'
  },
  {
    id: island, name: '4TVI Stewardship', kind: organization, aliases: ['4TVI', 'Tourism Vancouver Island'], officialUrl: 'https://www.4vigroup.com/destination-stewardship',
    description: 'The nonprofit regional tourism operation in the 4VI Group continues Vancouver Island’s destination stewardship and tourism-industry services.',
    history: 'Destination BC’s regional directory identifies 4TVI as the Vancouver Island partner. The group’s separate 4TVI Stewardship branding was in use by 2024.',
    relations: [regionalPartner, operation], sources: [regionalDirectory, islandGroup,
      source('Vancouver Island Destination Stewardship Strategy', 'https://www.4vigroup.com/destination-stewardship')], cover: '4tvi-stewardship-lockup'
  },
  {
    id: '4ever-strategies', name: '4EVER Strategies', kind: 'tourism-enterprise', aliases: ['4EVER Strategies Inc.', '4EVER'],
    description: 'The 4VI Group’s professional services company works on sustainability, storytelling and strategic planning.',
    relations: [operation], sources: [islandGroup], cover: '4ever-strategies-lockup'
  },
  {
    id: '4good-social-impact-fund', name: '4GOOD Social Impact Fund', kind: program, aliases: ['4GOOD'],
    description: 'The 4VI Group’s social investment operation supports community projects in the Vancouver Island region.',
    relations: [operation], sources: [islandGroup], cover: '4good-impact-lockup'
  },
  {
    id: itbc, name: 'Indigenous Tourism BC', kind: organization, from: 1996,
    aliases: ['ITBC', 'Aboriginal Tourism BC', 'Aboriginal Tourism Association of British Columbia', 'AtBC'], officialUrl: 'https://www.indigenousbc.com/corporate/who-we-are/',
    description: 'An Indigenous-led nonprofit that supports Indigenous tourism businesses and communities across British Columbia.',
    history: 'The organization dates its beginnings to 1996. The Province listed the Aboriginal Tourism Association of British Columbia as a funding partner in 2003. The northern travel guides show the full association name in 2012 and the short Aboriginal Tourism BC name in 2013. Its 2017–18 report uses Indigenous Tourism BC beside gold hands. The later corporate signature adds a Corporate line beneath the name.',
    relations: [partner('destination-bc', 'Provincial Indigenous tourism partner')],
    sources: [source('Indigenous Tourism BC origin and explanation of the corporate mark', 'https://www.indigenousbc.com/corporate/who-we-are/'), province2003, vcmNewsletter],
    cover: 'itbc-corporate-horizontal'
  },
  {
    id: 'tourism-industry-association-bc', name: 'Tourism Industry Association of BC', shortName: 'Tourism Industry Association of BC', kind: organization, from: 1976,
    aliases: ['TIABC', 'Council of Regional Tourism Associations', 'Council of Tourism Associations', 'COTA'], officialUrl: 'https://tiabc.ca/',
    description: 'The provincial industry advocacy association represents tourism businesses and member organizations in government relations and policy.',
    history: 'The association formed in 1976. It operated as the Council of Regional Tourism Associations after 1989 and later the Council of Tourism Associations before returning to the Tourism Industry Association of BC name.',
    relations: [partner(resiliency, 'Industry association supported the 2020 network')],
    sources: [source('Destination BC account of TIABC’s first 50 years', dbc + 'news/tourism-industry-association-of-bc-celebrates-50-years-of-leadership-and-advocacy/'), launch2020],
    cover: 'tiabc-website'
  },
  {
    id: secretariat, name: 'BC Regional Tourism Secretariat', kind: 'tourism-collaboration', aliases: ['BCRTS', 'British Columbia Regional Tourism Secretariat'],
    officialUrl: 'https://tourismsustainability.ca/bcrts/',
    description: 'A regional tourism collaboration that coordinates industry support and shared programs.',
    history: 'The secretariat worked with regional organizations and provincial partners on the 2020 resiliency response. It presented its emergency management, business support and sustainability work to a legislative committee in 2021. It later operated the Sustainability Network with the six regions.',
    relations: regions.map((id) => partner(id, 'Regional partner in the Sustainability Network')),
    sources: [source('BC Regional Tourism Secretariat partnership and program role', 'https://tourismsustainability.ca/bcrts/'), launch2020,
      source('BC Legislative Assembly committee evidence, September 2021', 'https://api.lims.leg.bc.ca/hdms/file/Committees/42nd2nd/fgs/20210929pm-Finance-Nanaimo-n31.html')],
    cover: 'bcrts-colour'
  },
  {
    id: resiliency, name: 'BC Tourism Resiliency Network', kind: program, historical: true, from: 2020,
    aliases: ['BCTRN', 'British Columbia Tourism Resiliency Network', 'Tourism Resiliency Program'],
    description: 'The pandemic-response partnership helped tourism businesses navigate relief resources and access one-on-one advice.',
    history: 'The regional and provincial partners activated the network in April 2020. Its red square signature appears in the case-study material for businesses.',
    relations: [partner(secretariat, 'Regional coordinating partner'), partner(vcm, 'Delivered a Vancouver, Coast & Mountains program'), partner(itbc, 'Indigenous tourism partner')],
    sources: [launch2020, source('BCRTS Tweedsmuir Park Lodge case study, p. 4', 'https://tourismsustainability.ca/app/uploads/2021/02/TweedsmuirCaseStudy-February08_Final-1.pdf#page=4')],
    cover: 'bctrn-square'
  },
  {
    id: sustainability, name: 'BC Tourism Sustainability Network', kind: program, from: 2022,
    aliases: ['BCTSN'], officialUrl: 'https://tourismsustainability.ca/',
    description: 'A provincial collaboration that gives tourism operators practical support for sustainability and climate adaptation.',
    history: 'The network began in 2022 under the BC Regional Tourism Secretariat and regional partners. Destination BC’s 2024 account describes how the Climate Resiliency Initiative built on the earlier network. The network later received support through that initiative.',
    relations: [partner(secretariat, 'Operated by the BC Regional Tourism Secretariat', 'operated-by'), partner(initiative, 'Supported through the climate initiative')],
    sources: [vcmNewsletter, source('Sustainability Network partnership and delivery model', 'https://tourismsustainability.ca/bcrts/')],
    cover: 'bctsn-horizontal'
  },
  {
    id: initiative, name: 'BC Tourism Climate Resiliency Initiative', kind: program, historical: true,
    aliases: ['BCTCRI', 'BC Tourism Climate Resilience Initiative'], officialUrl: climate,
    description: 'A two-year provincial pilot funded through the Destination Development Fund to help tourism businesses and communities prepare for climate impacts.',
    history: 'The $3 million pilot began in fiscal 2023/24. It supported adaptation plans, micro-grants, sustainability data and network coordination. Destination BC’s published guidelines and program page identify the work through program text and partner signatures.',
    relations: [partner('destination-bc', 'Led in collaboration with Destination BC and the Province'), partner(itbc, 'Provincial delivery partner'), ...regions.map((id) => partner(id))],
    sources: [source('Destination BC pilot overview and completion', climate), vcmNewsletter,
      source('February 2024 Micro-Grants Program Guidelines, cover', dbc + 'content/uploads/2024/02/BC-Tourism-Climate-Resiliency-Initiative-Grant-Program-Guidelines-February-2024-FINAL.pdf')],
    nextAction: 'Check the pilot’s program files for evidence of a standalone mark. The partners’ separately attributed logos are held in their own collections.'
  },
  {
    id: 'destination-vancouver', name: 'Destination Vancouver', kind: organization, from: 1902,
    aliases: ['Tourism Vancouver', 'Greater Vancouver Tourist Association', 'Greater Vancouver Convention and Visitors Bureau'],
    officialUrl: 'https://www.destinationvancouver.com/',
    description: 'The city’s destination organization promotes Vancouver and supports the development of visitor experiences.',
    history: 'In 2021, as it entered its 119th year, Tourism Vancouver adopted the Destination Vancouver name and a new destination development and promotion mandate. Both the former and current signatures are documented.',
    relations: [withRegion], sources: [source('Destination Vancouver 2021 name and mandate announcement', 'https://www.destinationvancouver.com/inspirations/events/tourism-vancouver-enters-its-119th-year-with-a-new-name-and-mandate'),
      source('UBCM 2019 convention partner listing', 'https://www.ubcm.ca/convention-resolutions/past-conventions/2019-conventions/2019-program-partner-things-do')],
    cover: 'destination-vancouver-wordmark'
  },
  {
    id: 'tourism-whistler', name: 'Tourism Whistler', kind: organization, from: 1980,
    aliases: ['Whistler Resort Association'], officialUrl: 'https://www.whistler.com/about-us/',
    description: 'Whistler’s member-based nonprofit destination organization is legally the Whistler Resort Association.',
    history: 'Provincial legislation enabled a resort association in 1979. It began operations in 1980. In October 2020 Tourism Whistler launched new place-brand creative with a refreshed logo.',
    relations: [withRegion], sources: [source('Tourism Whistler origins and member assessment model', 'https://www.whistler.com/about-us/'),
      source('Tourism Whistler brand creative announcement, 2020', 'https://media.whistler.com/media-releases/2020/tourism-whistler-launches-new-brand-creative/')],
    cover: 'tourism-whistler-stacked'
  },
  {
    id: 'sunshine-coast-tourism', name: 'Sunshine Coast Tourism', kind: organization, from: 2008,
    aliases: ['SCT'], officialUrl: 'https://www.sunshinecoastcanada.com/industry/',
    description: 'A nonprofit society promoting BC’s Sunshine Coast and working with local tourism businesses and governments.',
    history: 'The society incorporated in 2008 to serve the Sunshine Coast and qathet regional districts. Its 2024 annual report documents the branded Sunshine Coast signature. In 2026 the society issued a request for proposals to refresh the brand.',
    relations: [withRegion], sources: [source('Sunshine Coast Tourism history and board, December 2023', 'https://www.sunshinecoastcanada.com/articles/post/sunshine-coast-tourism-returning-board-reinforces-commitment-at-agm/'),
      source('Sunshine Coast Tourism 2026 brand refresh RFP', 'https://www.sunshinecoastcanada.com/brand-refresh-visual-identity-rfp/')],
    cover: 'sunshine-coast-signature'
  },
  {
    id: 'tourism-chilliwack', name: 'Tourism Chilliwack', kind: 'tourism-enterprise', from: 2006,
    aliases: ['This is Chilliwack', 'Chilliwack Tourism'], officialUrl: 'https://tourismchilliwack.com/about-us-2/',
    description: 'The local destination organization promotes Chilliwack and works on regional tourism development.',
    history: 'Tourism Chilliwack incorporated in 2006 with the City of Chilliwack as its sole shareholder. Its 2022–2027 strategy records a branding exercise begun in 2017.',
    relations: [withRegion], sources: [source('Tourism Chilliwack organizational overview', 'https://tourismchilliwack.com/about-us-2/'),
      source('Chilliwack Tourism Strategic Plan 2022–2027', 'https://tourismchilliwack.com/wp-content/uploads/2022/05/CHWK20520Year20Strategic20Plan202022-202720-20Final-compressed.pdf')],
    cover: 'tourism-chilliwack-website'
  },
  {
    id: 'discover-naramata', name: 'Discover Naramata', kind: organization,
    aliases: ['Naramata', 'Naramata Bench'], officialUrl: 'https://discovernaramata.com/about-the-society/',
    description: 'The local tourism society promotes the community of Naramata and the Naramata Bench.',
    history: 'The provincial Bear Smart brochure shows the society’s illustrated oval badge. Discover Naramata launched a new identity with ReThink in May 2022, introducing the arched landscape emblem used on its website.',
    sources: [source('Discover Naramata society overview', 'https://discovernaramata.com/about-the-society/'),
      source('BC Conservation Officer Service Bear Smart brochure, p. 3', 'https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/conservation-officer-service/bearsmart_brchr.pdf#page=3'),
      source('Discover Naramata Five Year Strategic Plan, cover', 'https://static1.squarespace.com/static/5c2cff8c36099b4c27b18294/t/644c1bebc54c2b4461a433d5/1682709485621/DN%2B-%2BStrategic%2B%2BPlan_MRDT_FINAL_Web.pdf#page=1'),
      source('Discover Naramata’s May 2022 rebrand announcement', 'https://www.hatchcomms.ca/post/discover-naramata-evolves')],
    nextAction: 'Seek the original artwork for the illustrated oval badge.',
    cover: 'discover-naramata-website-wordmark'
  },
  ...TOURISM_SECTOR_RECORDS,
  ...NORTHERN_TRAVEL_GUIDE_RECORDS
]

const note = ({ description, history }) => history ? `${description} ${history}` : description
const assetsOf = (id) => artwork[id] ?? sectorArtwork[id] ?? []
const hasArtwork = (id) => Boolean(assetsOf(id).length || NORTHERN_TRAVEL_GUIDE_ARTWORK[id]?.length)
const names = new Map(records.map(({ id, name }) => [id, name]))
names.set('destination-bc', 'Destination BC')

const partnerSubjects = records.map((record) => {
  const { id, name, kind, aliases = [], relations = [], sources, nextAction } = record
  return {
    id, name, label: name, kind, aliases, relations, sources,
    nextAction: nextAction ?? ([...assetsOf(id), ...(NORTHERN_TRAVEL_GUIDE_ARTWORK[id] ?? [])].some(({ isVector }) => isVector)
      ? 'Check dated publications for the first documented use of each signature.'
      : 'Locate the publisher’s matching vector artwork.'),
    family: TOURISM_PARTNER_FAMILY.id,
    scope: 'institution',
    graphNode: id, priority: 3, salaryEmployers: [],
    ...(record.identityStatus ? { identityStatus: record.identityStatus } : {}),
    collectionIds: hasArtwork(id) ? [`collected-${id}`] : [],
    note: note(record)
  }
})

export const TOURISM_PARTNER_SUBJECTS = [{
  id: 'destination-bc', name: 'Destination BC Corp.', label: 'Destination BC', kind: 'crown-corporation',
  aliases: ['Destination British Columbia', 'DBC'], family: TOURISM_PARTNER_FAMILY.id, scope: 'core',
  graphNode: 'destination-bc', priority: 1, salaryEmployers: [], relations: [],
  collectionIds: ['tourism-bc-destination-bc'],
  sources: [regionalDirectory, source('Destination BC corporate document archive', dbc + 'who-we-are/corporate-document/')],
  note: 'The provincial tourism Crown corporation began operations in April 2013. It manages the Vancouver, Coast & Mountains region directly and works with regional destination organizations elsewhere in the province.',
  nextAction: 'Compare the corporation’s co-branding rules and dated regional partner signatures across the agreement archive.'
}, ...partnerSubjects]

export const TOURISM_PARTNER_BODIES = records.filter(({ id }) => hasArtwork(id)).map((record) => ({
  id: record.id, name: record.name, shortName: record.shortName, kind: record.kind,
  graphNode: null, shelf: 'tourism', current: !record.historical, from: record.from,
  cover: record.cover, initiativeId: record.initiativeId, notes: note(record), status: 'asset-collected', assets: assetsOf(record.id)
}))

export const TOURISM_RELATED_BODIES = records.map((record) => ({
  id: record.id, name: record.name, shortName: record.shortName ?? record.name, aliases: record.aliases ?? [],
  kind: record.kind, officialUrl: record.officialUrl, historical: record.historical,
  description: record.description, historyNote: record.history, checked,
  sources: record.sources, salaryEmployers: [],
  relationships: (record.relations ?? []).filter(({ subject }) => names.has(subject)).map(({ subject, label }) => ({
    id: subject, label: names.get(subject), description: label,
    ...(subject === 'destination-bc' ? { year: 2026 } : {})
  }))
}))
