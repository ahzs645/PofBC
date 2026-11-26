// Each row describes a documented relationship. Both endpoints use the same date, description and citation.
const source = (title, url) => ({ title, url })
const uploads = 'https://rccbc.ca/wp-content/uploads/'
export const ruralSources = {
  story: source('RCCbc, Our Story', 'https://rccbc.ca/about-us/our-story/'),
  registry: source('Registrar of Companies, March 10, 2022 incorporations', 'https://www.bclaws.gov.bc.ca/civix/document/id/corpreg/corpreg/soc0317soc0522'),
  jsc: source('Ministry of Health, Rural Practice Partners', 'https://www2.gov.bc.ca/gov/content/health/practitioner-professional-resources/physician-compensation/rural-practice-programs/6815'),
  guide: source('JSC, Rural Physician Programs Guide, February 2013, p. 25', 'https://www.doctorsofbc.ca/sites/default/files/rural_guide_mar_2013finalweb.pdf#page=27'),
  education: source('JSC, Rural Physician Programs Guide, April 2016, p. 25', 'https://www.doctorsofbc.ca/sites/default/files/rural_guide_2016_final.pdf#page=27'),
  chair: source('Province of BC, establishment of the UBC Chair in Rural Health', 'https://archive.news.gov.bc.ca/releases/news_releases_2013-2017/2016HLTH0082-002358.htm'),
  forum: source('Third Annual Rural Locum Forum, May 2017 report, p. 1', 'https://divisionsbc.ca/sites/default/files/user/hkullar/Rural%20Locum%20Forum_Report_0417_v5.pdf#page=1'),
  visits: source('RCCbc, Rural Site Visits Project, September 2019, pp. 1–2', 'https://bcruralcentre.org/wp-content/uploads/2020/01/RCCbc-Site-Visits-Community-Feedback-Report-2_Jun-2017-Jun-2019.pdf'),
  northern: source('UNBC Health Research Institute, rural research partnership', 'https://www.unbc.ca/health-research-institute/rccbc-rural-coordination-centre-bc'),
  reconciliation: source('RCCbc, reconciliation progress report, Q4 2021, p. 6', uploads + '2022/09/TRC-Report-Card_Revised-Final_100921.pdf#page=6'),
  network: source('UBC Department of Family Practice, About RHSRNbc', 'https://rhsrnbc.med.ubc.ca/about-rhsrnbc/'),
  networkPredecessor: source('UNBC, New Rural Health Research Network Launched at UNBC, July 18, 2005', 'https://www.unbc.ca/releases/2005/07-18rural'),
  networkAward: source('Michael Smith Health Research BC, BC Rural and Remote Health Research Network award', 'https://www.healthresearchbc.ca/award/bc-rural-and-remote-health-research-network/'),
  networkNewsletter: source('RHSRNbc, first newsletter, June 2011', 'https://med-fom-rhsrnbc.sites.olt.ubc.ca/files/2018/11/June-2011.pdf'),
  networkContact: source('UBC Department of Family Practice, Connect to RHSRNbc', 'https://rhsrnbc.med.ubc.ca/connect/contact-us/'),
  conference: source('BC Rural Health Conference, May 2022 brochure, cover', 'https://ubccpd.ca/sites/default/files/documents/RHC-2022-Brochure_1.pdf#page=1'),
  launch: source('RCCbc, website and visual identity announcement, November 26, 2022', 'https://rccbc.ca/story/rccbc-launches-new-online-home-for-rural-doctors-other-network-partners/'),
  filing: source('RCCBC application 927757, filing history', 'https://www.trademarkelite.com/canada/trademark/trademark-detail/927757/RCCBC'),
  officialMark: source('CIPO, Trademarks Journal, October 18, 2023, p. 1522', 'https://www.ic.gc.ca/opic-cipo/tmj/eng/18Oct2023_en.pdf?edition=10-18&year=2023#page=1522'),
  rtvs: source('RCCbc, RTVS visual identity guidelines, August 2024', uploads + '2022/10/RTVS-Logo-Brand-Identity-Guidelines-August-2024.pdf'),
  rtvsResources: source('RCCbc, RTVS logos and resources', 'https://rccbc.ca/initiatives/rtvs/rtvs-media-resources/rtvs-resources/'),
  media: source('RCCbc, media inquiries and toolkit access', 'https://rccbc.ca/connect/media/'),
  banner: source('RCCbc, The new RCCbc banner!, photographed May 10, 2018', 'https://www.flickr.com/photos/54624077@N07/42451137062/')
}

export const rccbc = 'rural-coordination-centre-bc'
export const jsc = 'joint-standing-committee-on-rural-issues'
export const division = 'rural-and-remote-division-of-family-practice'
export const researchNetwork = 'rural-health-services-research-network-bc'
export const rtvs = 'real-time-virtual-support'
const doctors = 'doctors-of-bc'
const ministry = 'ministry-of-health-2011'
const ubc = 'university-of-british-columbia'
const unbc = 'university-of-northern-bc'
const s = ruralSources

const body = (id, name, shortName, kind, description, sources, extra = {}) => ({
  id, name, shortName, kind, aliases: [], checked: '2026-11-25', description, sources, salaryEmployers: [], ...extra
})
export const RURAL_HEALTH_BODIES = [
  body(rccbc, 'Rural Coordination Centre of British Columbia', 'RCCbc', 'nonprofit-society',
    'Four rural physicians and two staff members founded RCCbc in 2007 to improve rural medical training. Its physician-led network now supports rural practice, research and community health across BC.',
    [s.story, s.registry, s.guide, s.education, s.visits, s.launch, s.filing, s.officialMark, s.media],
    { aliases: ['Rural Coordination Centre of BC (Society)', 'S0076197'], officialUrl: 'https://rccbc.ca/',
      historyNote: 'The society incorporated on March 10, 2022 as S0076197. It filed application 927757 for the word RCCBC on August 25, 2022. The Canadian Trademarks Journal published the official mark notice under section 9(1)(n)(iii) on October 18, 2023.' }),
  body(jsc, 'Joint Standing Committee on Rural Issues', 'JSC', 'joint-committee',
    'Formed in 2001 under the Rural Practice Subsidiary Agreement, the committee brings together the Ministry of Health, Doctors of BC and health authority representatives to develop and manage rural physician programs.', [s.jsc, s.guide, s.conference]),
  body(doctors, 'Doctors of BC', 'Doctors of BC', 'professional-association',
    'British Columbia’s professional association of physicians represents doctors on the Joint Standing Committee on Rural Issues.', [s.jsc, s.conference],
    { aliases: ['British Columbia Medical Association', 'BCMA'], officialUrl: 'https://www.doctorsofbc.ca/' }),
  body(division, 'Rural and Remote Division of Family Practice', 'Rural and Remote Division', 'medical-division',
    'The division and RCCbc jointly hosted the third Rural Locum Forum on February 25, 2017. Each used its own signature in the forum report.', [s.forum],
    { aliases: ['RRDFP'], officialUrl: 'https://divisionsbc.ca/rural-and-remote' }),
  body(researchNetwork, 'Rural Health Services Research Network of BC', 'RHSRNbc', 'health-research-network',
    'Established under Dr. Stefan Grzybowski in May 2010, the network supports rural health services research. UBC’s Department of Family Practice hosts it, with RCCbc support through the JSC.',
    [s.network, s.networkPredecessor, s.networkAward, s.networkNewsletter, s.networkContact],
    { officialUrl: 'https://rhsrnbc.med.ubc.ca/',
      historyNote: 'The BC Rural and Remote Health Research Network launched at UNBC in 2005 with Michael Smith Foundation funding. Its award ended in 2010. The June 2011 RHSRNbc newsletter shows the blue mountain-and-river emblem with and without the full network name.' }),
  body(rtvs, 'Real-Time Virtual Support', 'RTVS', 'clinical-network',
    'RCCbc and its partners connect rural healthcare providers with clinical support through RTVS. Coast Salish artist Douglas “Bear” Horne designed its hummingbird and sun.', [s.rtvs, s.rtvsResources],
    { officialUrl: 'https://rccbc.ca/initiatives/rtvs/' })
]

const names = new Map(RURAL_HEALTH_BODIES.map(({ id, name }) => [id, name]))
for (const [id, name] of [[ministry, 'Ministry of Health'], [ubc, 'University of British Columbia'], [unbc, 'UNBC Health Research Institute'],
  ['northern-health', 'Northern Health'], ['first-nations-health-authority', 'First Nations Health Authority']]) names.set(id, name)

const link = (from, to, period, role, note, source) => ({ from, to, period, role, note, source })
export const RURAL_HEALTH_LINKS = [
  link(jsc, ministry, 'Current agreement', 'Committee representation', 'The Ministry of Health represents the provincial government on the JSC.', s.jsc),
  link(jsc, doctors, 'Current agreement', 'Committee representation', 'Doctors of BC represents physicians on the JSC. Its signature appears with the provincial symbol on the 2022 conference brochure.', s.jsc),
  link(rccbc, jsc, '2013', 'Funding and accountability', 'The committee’s rural physician guide identifies the JSC as RCCbc’s funder and the body to which RCCbc was accountable.', s.guide),
  link(rccbc, jsc, '2017', 'Site visits commission', 'The JSC asked RCCbc to visit every community covered by the Rural Practice Subsidiary Agreement. The September 2019 report documents what participating communities shared.', s.visits),
  link(rccbc, ubc, 'April 2016', 'Rural medical education', 'The rural physician guide describes RCCbc coordinating rural health education with UBC’s Faculty of Medicine.', s.education),
  link(rccbc, ubc, '2016', 'Chair in Rural Health', 'RCCbc proposed the chair that UBC established in its Department of Family Practice.', s.chair),
  link(jsc, ubc, '2016', 'Research chair endowment', 'The JSC funded the $5 million endowment for the UBC Chair in Rural Health.', s.chair),
  link(rccbc, division, 'February 2017', 'Forum co-hosts', 'RCCbc and the Rural and Remote Division co-hosted the Rural Locum Forum. Both signed the published report.', s.forum),
  ...[unbc, 'northern-health'].map(id => link(rccbc, id, 'Documented in 2018', 'Northern research partnership',
    'RCCbc, UNBC’s Health Research Institute and Northern Health worked together on rural physician research grants and community site visits.', s.northern)),
  link(rccbc, 'first-nations-health-authority', '2019', 'Memorandum of understanding', 'RCCbc and FNHA formalized a commitment to work with First Nations on the design and delivery of health services.', s.reconciliation),
  link(rccbc, researchNetwork, 'Documented in 2023', 'Research network support', 'RHSRNbc identifies RCCbc as its supporter through JSC funding.', s.network),
  link(researchNetwork, ubc, 'Documented in 2023', 'Research affiliation', 'UBC’s Department of Family Practice hosts the network. Its director also co-directs UBC’s Centre for Rural Health Research.', s.network),
  link(rtvs, ubc, 'RTVS program resources', 'Continuing medical education', 'UBC Continuing Professional Development offers credits to physicians for eligible time consulting a virtual provider through RTVS.', s.rtvsResources),
  link(rccbc, rtvs, 'Documented in 2024', 'Virtual care initiative', 'RCCbc published the RTVS identity guide for the partners delivering virtual support. The guide credits Douglas Bear Horne with the hummingbird and sun.', s.rtvs)
]

export const ruralConnectionsOf = (id) => RURAL_HEALTH_LINKS.filter(row => row.from === id || row.to === id).map(row => {
  const target = row.from === id ? row.to : row.from
  return { id: target, label: names.get(target), description: row.note, period: row.period, role: row.role, source: row.source }
})
