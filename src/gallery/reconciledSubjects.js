import { bearAwareGalleryId, bearAwareId, bearAwareReport, bearAwareTitle } from '../initiatives/bearAwareArtwork.js'
import { environmentYouthCorpsAd, environmentYouthCorpsGalleryId, environmentYouthCorpsId, environmentYouthCorpsReprint } from '../initiatives/environmentYouthCorpsArtwork.js'
import { fireSmartGuide } from './fireSmart.js'
import { strongerBCGuide, strongerBCMatrix } from './strongerBC.js'
import { buyBCStandards } from './buyBC.js'
import { ecosystemsAtRiskSources } from './ecosystemsAtRisk.js'
import { RESWEST_SOURCES } from './resWest.js'

// Owners for artwork the gallery already held without a register subject (the 15 November 2026
// gallery audit: 53 entries in 12 collections plus BC Cancer Foundation's two marks).
//
// Each subject owns only the entries recorded under it. A program brand on the BC mark is not its
// ministry's corporate logo, and a foundation's mark is not the health agency's. Where a subject is
// an atlas body its id is the atlas id, so the gallery's existing entry owners resolve to it.
// PROGRAM_ENTRY_OWNERS gives the entries that had no owner at all an explicit one.

export const RECONCILED_FAMILIES = [
  {
    id: 'affiliated-organizations', label: 'Affiliated organizations',
    description: 'Independent organizations with a documented formal relationship to a provincial body.'
  },
  {
    id: 'provincial-programs',
    label: 'Provincial branches, services and programs',
    description: 'Ministry branches, online services, programs and campaigns, many shown on or beside the BC mark. Each specimen keeps its own owner.'
  }
]

/** Entries that were held with no owner: each is given the program it was published for. */
export const PROGRAM_ENTRY_OWNERS = {
  // BC Lands is not a body in the atlas, so its badge is owned by its register subject.
  'bc-lands': 'bc-lands',
  'welcome-bc': 'welcome-bc',
  'vector-welcomebc-2016': 'welcome-bc',
  'vector-welcomebc-current': 'welcome-bc',
  'environmental-reporting-bc': 'environmental-reporting-bc',
  'environmental-lab-bc': 'environmental-lab-bc',
  'stronger-bc': 'stronger-bc',
  'vector-BCID_StrongerBC_RGB_pos': 'stronger-bc',
  'strongerbc-for-everyone-endorsed': 'stronger-bc',
  'strongerbc-for-everyone-wordmark': 'stronger-bc',
  'vector-StrongerBC_RGB_pos': 'stronger-bc',
  'vector-StrongerBC_Solid_pos': 'stronger-bc',
  'pacific-gateway': 'pacific-gateway',
  'vector-canada-starts-here-2012': 'pacific-gateway',
  'vector-canada-starts-here-bc-jobs-plan-2012': 'pacific-gateway',
  'best-place-on-earth': 'best-place-on-earth',
  'bc-150-years': 'bc-150-years',
  'ecosystems-at-risk-badge': 'ecosystems-at-risk',
  'bc-travel-industry-ca-1970': 'department-of-travel-industry-1967',
  // Ministries' flag-years marks: owned by the ministry's node on the government map.
  'bc-environment-flag-years': 'ministry-of-environment-1988',
  'tourism-recreation-culture-1986': 'ministry-of-tourism-recreation-and-culture-1986',
  // A ministry program's mark: owned by the program's subject, which links to the ministry's node.
  'superhost-1986': 'superhost',
  // The Department of Recreation and Conservation is a ministry, not an atlas body, so its marks are
  // owned by its register subject. BC Parks' copies of the Parks Branch's two are BC Parks' own.
  ...Object.fromEntries(['drc-dogwood-oval-1970', 'drc-department', 'drc-fish-wildlife', 'drc-parks', 'drc-museum',
    'drc-fisheries', 'drc-fw-oval-1973', 'drc-fw-lockup-1973', 'drc-parks-shield-1973']
    .map((id) => [id, 'department-of-recreation-and-conservation'])),
  // The Fish and Wildlife Branch's copies of its three marks are its own.
  ...Object.fromEntries(['fwb-1971-square', 'fwb-1973-oval', 'fwb-1973-lockup'].map((id) => [id, 'fish-and-wildlife-branch'])),
  'bceid-reversed': 'bceid',
  'bceid-reversed-rebuilt': 'bceid'
}

const subject = ({ id, label, name = label, kind, family = 'provincial-programs', graphNode = null, collectionIds = [], aliases = [], salaryEmployers = [], priority = 2, scope = 'core', sources, nextAction, note, relations = [], ...rest }) => ({
  id, label, name, kind, family, graphNode, aliases, collectionIds, salaryEmployers, priority, scope, sources, nextAction, note, relations, ...rest
})

export const RECONCILED_SUBJECTS = [
  subject({
    id: 'bc-150-years', label: 'BC 150 Years', kind: 'service-brand',
    collectionIds: ['bc-mark'],
    sources: [{ title: 'Balanced Budget 2008 Highlights, front cover', url: 'https://www.bcbudget.gov.bc.ca/2008/highlights/2008_Highlights.pdf' }],
    note: 'The Province’s 2008 anniversary campaign used a blue-and-gold mark with a sunburst and the Best Place on Earth tagline.',
    nextAction: 'Locate the campaign’s original artwork package or graphic standards.'
  }),
  subject({
    id: 'ecosystems-at-risk', label: 'Ecosystems at Risk', name: 'Ecosystems in British Columbia at Risk', kind: 'service-brand',
    collectionIds: ['specimens-ecosystems-at-risk'], sources: ecosystemsAtRiskSources,
    note: 'The B.C. Conservation Data Centre used this badge on public brochures about threatened habitats.',
    nextAction: 'Check other dated brochures in the series for additional uses of the badge.'
  }),
  subject({
    id: bearAwareId, label: bearAwareTitle, kind: 'service-brand',
    collectionIds: [bearAwareGalleryId], aliases: ['Be Bear Aware', 'We Are Bear Aware', 'Revelstoke Bear Aware'],
    sources: [{ title: 'Revelstoke Bear Awareness Program, 1997 Final Report', url: bearAwareReport }],
    note: 'Revelstoke’s wildlife education campaign used the paw on its checklists and the sign awarded to participating properties.',
    nextAction: 'Ask the Revelstoke Bear Aware Society or Revelstoke Museum & Archives about original campaign production artwork.'
  }),
  subject({
    id: environmentYouthCorpsId, label: 'Environment Youth Corps', kind: 'service-brand',
    collectionIds: [environmentYouthCorpsGalleryId], aliases: ['Environment Youth Corps of British Columbia'],
    sources: [environmentYouthCorpsAd, environmentYouthCorpsReprint],
    note: 'The provincial youth employment and training program used this mark in its June 1990 recruitment advertisements.',
    nextAction: 'Locate original production artwork or printed program material with the same mark.'
  }),
  subject({
    id: 'firesmart-bc', label: 'FireSmart BC', kind: 'service-brand',
    collectionIds: ['specimens-firesmart-bc'], aliases: ['BC FireSmart Committee', 'Ember the FireSmart Fox'],
    sources: [{ title: 'FireSmart BC Brand Guidelines, July 2025', url: fireSmartGuide }],
    note: 'The BC FireSmart Committee directs the provincial program. Its guide documents the provincial signature, four sub-brands and Ember the FireSmart Fox.',
    nextAction: 'Locate publisher artwork for the black and white options mentioned on page 5 of the July 2025 guide.'
  }),
  subject({
    id: 'sub-buy-bc', label: 'Buy BC', kind: 'service-brand', graphNode: 'sub-buy-bc',
    aliases: ['buyBC', 'Buy BC Partnership Program'], collectionIds: ['specimens-buy-bc'],
    sources: [{ title: 'Buy BC Graphic Standards', url: buyBCStandards }],
    note: 'The provincial food and beverage marketing program licenses its landscape emblem for use on packaging and in stores.',
    nextAction: 'Locate a dated example of the graphics licensed to BC Agriculture Council in 2002.'
  }),
  subject({
    id: 'provincial-emergency-program',
    name: 'Provincial Emergency Program',
    label: 'Provincial Emergency Program',
    kind: 'service-brand',
    family: 'provincial-administration',
    graphNode: null,
    aliases: ['PEP'],
    collectionIds: ['specimens-provincial-emergency-program'],
    sources: [
      { title: 'Joint Emergency Preparedness Program Guidelines, revised July 1993', url: 'https://www.publicsafety.gc.ca/lbrr/archives/ua%20929.c2%20b75%201993-eng.pdf' },
      { title: 'Provincial compliments slip received October 16, 1997', url: 'https://docs.openinfo.gov.bc.ca/d37393013a_response_package_fnr-2013-00153.pdf#page=50' }
    ],
    note: 'British Columbia’s Provincial Emergency Program used the striped PEP initials and processed applications and claims for the federal Joint Emergency Preparedness Program.',
    nextAction: 'Identify the designer and original lettering from a dated identity specification.'
  }),
  subject({
    id: 'bchealthcare', label: 'BCHealthCare', kind: 'service-brand',
    aliases: ['BC Health Care'], collectionIds: ['health-program-signatures'],
    sources: [{ title: 'Abbotsford Hospital and Cancer Centre request for expressions of interest, January 23, 2003', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/307972' }],
    note: 'Provincial health-care communications signature. The project cover separately names the Ministry of Health Services and its partners.',
    nextAction: 'Locate the design standard or an earlier dated use of the signature.'
  }),
  subject({
    id: 'bcpharmacare', label: 'BCPharmaCare', kind: 'service-brand',
    aliases: ['BC PharmaCare', 'Fair PharmaCare'], collectionIds: ['health-program-signatures'],
    sources: [
      { title: 'Your new Fair PharmaCare program, 2003', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/301527' },
      { title: 'Ministry of Health Services PharmaCare overview, February 24, 2003', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2003HSER0013-000192-Attachment2.htm' }
    ],
    note: 'The provincial drug coverage program began in 1974. The 2003 Fair PharmaCare plan introduced income-based coverage. Its registration material carried the BCPharmaCare program signature.',
    nextAction: 'Locate the design standard and establish when the arms-based signature first appeared.'
  }),
  subject({
    id: 'workers-compensation-board',
    label: 'WorkSafeBC',
    name: 'Workers’ Compensation Board of British Columbia',
    kind: 'agency',
    family: 'regulators-administration',
    graphNode: 'workers-compensation-board',
    aliases: ['Workers’ Compensation Board', 'WCB', 'WorkSafe'],
    collectionIds: ['worksafebc'],
    salaryEmployers: ['workers-compensation-board'],
    priority: 1,
    sources: [
      { title: 'WorkSafeBC 2024 annual report and 2025–2027 service plan', url: 'https://www.worksafebc.com/en/resources/about-us/annual-report-statistics/2024-annual-report/2024-annual-report-2025-2027-service-plan?lang=en' },
      { title: 'WorkSafeBC 2003 annual report and 2004–2006 service plan', url: 'https://www.worksafebc.com/en/resources/about-us/annual-report-statistics/2003-annual-report-and-2004-2006-service-plan/2003-annual-report-and-2004-2006-service-plan?lang=en' }
    ],
    nextAction: 'Date the 1983 Workers’ Compensation Board symbol from a primary specimen and seek the original WorkSafeBC vector masters.',
    note: 'The legal name stayed the Workers’ Compensation Board; WorkSafeBC is its operating name. The 1983 board mark and the WorkSafeBC marks are separate eras of one owner.'
  }),
  subject({
    id: 'sub-bc-timber-sales',
    label: 'BC Timber Sales',
    kind: 'government-branch',
    graphNode: 'sub-bc-timber-sales',
    aliases: ['BCTS', 'Small Business Forest Enterprise Program'],
    collectionIds: ['bcts'],
    sources: [{ title: 'BC Timber Sales brochure, 2004, Legislative Library', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/308267' }, { title: 'BC Timber Sales business plan 2023/24–2025/26', url: 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bcts_business_plan_2023-2024_to_2025-2026_final.pdf' }],
    nextAction: 'Seek an introduction date or design credit for the serif acronym lockup documented in 2004, and an original file for the current mark.',
    note: 'A ministry branch with its own marks. The Small Business Forest Enterprise Program it replaced is a predecessor program, not an alias for the same artwork.'
  }),
  subject({
    id: 'sub-bc-parks',
    label: 'BC Parks',
    kind: 'government-branch',
    graphNode: 'sub-bc-parks',
    collectionIds: ['bc-parks'],
    sources: [
      { title: 'bcparks.ca', url: 'https://bcparks.ca/' },
      { title: 'BC Archives, GR-3888, BC Parks in-house materials master files', url: 'https://search-bcarchives.royalbcmuseum.bc.ca/bc-parks-in-house-materials-master-files' }
    ],
    nextAction: 'Compare the archival master files with the earlier marks and date the banner and “Best Place on Earth” versions.',
    note: 'Park signage, the branch’s corporate marks and campaign lockups are kept as separate entries.'
  }),
  subject({
    id: 'bc-lands',
    label: 'BC Lands',
    kind: 'government-branch',
    collectionIds: ['bc-lands'],
    sources: [{
      title: 'Ministry of Forests and Lands form, photocopied',
      citation: 'A form on an assignment, with its BC Lands badge, supplied as a screenshot; title, number and date not in the picture.'
    }, {
      title: 'Lands Operations Division, Vancouver Island Region, fax dated February 14, 1994, PDF page 17',
      url: 'https://docs.openinfo.gov.bc.ca/Response_Package_FIN-2016-64551.pdf#page=17'
    }],
    nextAction: 'Identify the badge’s introduction and last documented use.',
    note: 'The provincial crown lands administration used the flag badge on a Ministry of Forests and Lands form and on a 1994 Lands Operations Division fax under the Ministry of Environment, Lands and Parks.'
  }),
  subject({
    id: 'justice-institute',
    label: 'JIBC',
    name: 'Justice Institute of British Columbia',
    kind: 'public-institute',
    family: 'institutions',
    graphNode: 'justice-institute',
    aliases: ['Justice Institute of BC'],
    collectionIds: ['collected-justice-institute'],
    salaryEmployers: ['justice-institute-of-bc'],
    priority: 2,
    scope: 'institution',
    sources: [
      { title: 'JIBC mandate and founding', url: 'https://www.jibc.ca/about-us/mandate' },
      { title: 'Grant of arms, June 2003', url: 'https://www.gg.ca/en/heraldry/public-register/project/94' },
      { title: 'JIBC letterhead, July 2007', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/323794' },
      { title: '2009–10 accountability report', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/323806' },
      { title: 'JIBC unveils its eagle', url: 'https://www.jibc.ca/news/article/jibc-unveils-new-brand' }
    ],
    nextAction: 'Find a dated specimen for the badge monogram and the first use of the griffin with its tagline.',
    note: 'Its registered arms are a separate emblem in the Coats of Arms view, not a version of the logo.'
  }),
  subject({
    id: 'sub-bc-online',
    label: 'BC OnLine',
    kind: 'service-brand',
    graphNode: 'sub-bc-online',
    collectionIds: ['collected-sub-bc-online'],
    sources: [
      { title: 'BC OnLine data files (July 2005)', url: 'https://www.bconline.gov.bc.ca/pdf/DataFilesJul05.pdf' },
      { title: 'BC OnLine website terms and conditions', url: 'https://www.bconline.gov.bc.ca/pdf/websiteUseTandC.pdf' }
    ],
    nextAction: 'Find dated specimens between the 2005 emblem and the 2011 logo.',
    note: 'The emblem on the BC mark shelf and the two dated specimens belong to the same online service.'
  }),
  subject({
    id: 'shared-services-bc',
    label: 'Shared Services BC',
    kind: 'government-branch',
    graphNode: 'shared-services-bc',
    graphYear: 2015,
    aliases: ['SSBC', 'Solutions BC'],
    collectionIds: ['collected-shared-services-bc'],
    sources: [
      { title: 'Shared Services BC, Real Property Division brochure (2015)', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/real-estate-space/rpd_brochure.pdf' },
      { title: 'Revenue management project request for proposals (Solutions BC, 2003)', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/about-the-bc-government/strategic-partnerships/the-strategic-partnerships-office/high-value-service-contracts/jsrfp_revenue_management_project.pdf' }
    ],
    nextAction: 'Establish when Solutions BC became Shared Services BC and whether marks were used after 2015.',
    note: 'Solutions BC’s 2003 and 2006 marks and Shared Services BC’s 2006/07 and 2015 marks are dated specimens of one government organization under two names.'
  }),
  subject({
    id: 'bc-cancer-foundation',
    label: 'BC Cancer Foundation',
    kind: 'charitable-institution',
    family: 'specialist-health',
    collectionIds: ['collected-sub-bc-cancer'],
    priority: 2,
    scope: 'institution',
    sources: [
      { title: 'BC Cancer Foundation', url: 'https://bccancerfoundation.com/' },
      { title: 'BC Cancer Foundation 2018 annual report', url: 'https://bccancerfoundation.com/wp-content/uploads/2021/07/bccf_2018_annual_report_-_lowres_single_pages.pdf' }
    ],
    nextAction: 'Record earlier foundation marks without assigning them to BC Cancer.',
    note: 'A charitable foundation that raises money for BC Cancer. Its marks are kept in the BC Cancer collection for comparison, but they are the foundation’s, not the health agency’s.',
    relations: [{ subject: 'sub-bc-cancer', type: 'related-to', label: 'Fundraising foundation for' }]
  }),
  subject({
    id: 'sub-workbc',
    label: 'WorkBC',
    kind: 'service-brand',
    graphNode: 'sub-workbc',
    sources: [{ title: 'WorkBC logo, as served by workbc.ca', url: 'https://www.workbc.ca/themes/custom/workbc/logo.svg' }],
    nextAction: 'Date the first WorkBC lockup on the BC mark from a primary specimen.',
    note: 'A provincial employment service; its own marks and its lockup on the BC mark are separate entries.'
  }),
  subject({
    id: 'welcome-bc',
    label: 'WelcomeBC',
    kind: 'service-brand',
    sources: [{ title: 'WelcomeBC logo, as served by welcomebc.ca', url: 'https://www.welcomebc.ca/getmedia/ce0988e3-03e0-4fed-a743-8ace3a34d1ce/WelcomeBC_cmyk_pos_Print.svg' }],
    nextAction: 'Find dated specimens from before 2016.',
    note: 'An immigration and settlement program brand of the Province. It is not an atlas body, so it has no organization link.'
  }),
  subject({
    id: 'stronger-bc',
    label: 'StrongerBC',
    kind: 'campaign',
    sources: [
      { title: 'BC visual identity: download marks', url: 'https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks' },
      { title: 'StrongerBC graphic identity standards, March 2024', url: strongerBCGuide },
      { title: 'StrongerBC brand matrix, May 2022', url: strongerBCMatrix }
    ],
    aliases: ['StrongerBC for everyone'],
    relations: ['sub-cleanbc', 'sub-workbc', 'sub-buy-bc'].map((id) => ({ subject: id, type: 'related-to', label: 'Program named in the StrongerBC brand matrix' })),
    nextAction: 'Find a surviving copy of the January 2021 guide to verify the earliest colourways.',
    note: 'The economic plan uses both the plain StrongerBC name and a government-only “for everyone” signature. The brand matrix distinguishes economic-plan messaging from the specific work of CleanBC, WorkBC, ChildCareBC and Buy BC.'
  }),
  subject({
    id: 'pacific-gateway',
    label: 'Pacific Gateway / Canada Starts Here',
    name: 'Canada’s Pacific Gateway and Canada Starts Here',
    kind: 'campaign',
    aliases: ['Canada’s Pacific Gateway', 'Canada Starts Here', 'BC Jobs Plan'],
    collectionIds: ['specimens-pacific-gateway'],
    priority: 3,
    sources: [{ title: 'Canada Starts Here: The BC Jobs Plan (2012)', url: 'https://www.amssa.org/wp-content/uploads/2015/05/BC-Jobs-Plan.pdf' }],
    nextAction: 'Find a primary government copy of the 2012 plan and a dated Pacific Gateway specimen.',
    note: 'Two successive campaign identities of the Province. The 2012 jobs-plan lockup is a separate specimen from the 2008–2011 gateway mark.'
  }),
  subject({
    id: 'best-place-on-earth',
    label: 'The Best Place on Earth',
    kind: 'campaign',
    aliases: ['Best Place on Earth'],
    priority: 3,
    sources: [{ title: 'The Tyee, “What happened to the Best Place on Earth?”, 4 October 2011', url: 'https://thetyee.ca/Mediacheck/2011/10/04/BC-Best-Place-On-Earth/' }],
    nextAction: 'Find the 2006 trademark registration and an original file of the slogan lockup.',
    note: 'A provincial slogan, launched in 2005 and dropped in 2011. It is not a body; its lockup sits on the BC mark shelf.'
  }),
  subject({
    id: 'department-of-travel-industry',
    label: 'Department of Travel Industry',
    graphNode: 'department-of-travel-industry-1967',
    entryOwner: 'department-of-travel-industry-1967',
    graphYear: 1970,
    collectionIds: ['specimens-travel-industry'],
    kind: 'government-branch',
    priority: 3,
    sources: [{ title: '“This is British Columbia”, published by the Department of Travel Industry, undated [about 1970]', citation: 'Print publication; no online copy recorded.' }],
    nextAction: 'Find dated publications of the department, 1967–1975, that show the map-and-dogwood mark.',
    note: 'A provincial department, 1967–1975. Its map-and-dogwood mark is held as a reconstruction from a photograph of an undated book. The department is a ministry in the government atlas, not a separate agency.'
  }),
  subject({
    id: 'ministry-of-environment-1988',
    label: 'BC Environment',
    name: 'Ministry of Environment, 1988–1991',
    kind: 'government-branch',
    graphNode: 'ministry-of-environment-1988',
    graphYear: 1989,
    aliases: ['BC Environment', 'Ministry of Environment'],
    collectionIds: ['bc-environment'],
    priority: 3,
    sources: [{
      title: 'An undated printed cover with the BC Environment band',
      citation: 'Supplied as a scan; its title and date are not in the picture.'
    }],
    nextAction: 'Find a dated publication with the BC Environment band, and whether it was used under Environment and Parks before 1988 or Environment, Lands and Parks after 1991.',
    note: 'The ministry between Environment and Parks (1986–1988) and Environment, Lands and Parks (1991–2001). Its mark names it in the way BC Parks’ and BC Lands’ badges name theirs, so it is held as a reconstruction on the gallery’s own flag artwork.',
    relations: [
      { subject: 'sub-bc-parks', type: 'related-to', label: 'Badges of the same flag-years identity' },
      { subject: 'bc-lands', type: 'related-to', label: 'Badges of the same flag-years identity' }
    ]
  }),
  subject({
    id: 'ministry-of-tourism-recreation-and-culture-1986',
    label: 'Tourism, Recreation and Culture',
    name: 'Ministry of Tourism, Recreation and Culture, 1986–1988',
    kind: 'government-branch',
    graphNode: 'ministry-of-tourism-recreation-and-culture-1986',
    graphYear: 1987,
    aliases: ['Ministry of Tourism, Recreation and Culture', 'Tourism, Recreation and Culture'],
    collectionIds: ['tourism-recreation-culture'],
    priority: 3,
    sources: [{
      title: 'The ministry’s logo with “HON. BILL REID, MINISTER”',
      citation: 'Supplied as a screenshot; the document it was taken from is not recorded.'
    }],
    nextAction: 'Find the printed source of the logo, and its colour, in the ministry’s publications of 1986–1988.',
    note: 'A ministry from November 1986 to July 1988, with one minister, Bill Reid, whose name its logo carries. The Province’s tourism marketing was later Tourism BC’s.',
    relations: [
      { subject: 'department-of-travel-industry', type: 'related-to', label: 'An earlier department for the Province’s tourism' }
    ]
  }),
  subject({
    id: 'expo-86-corporation',
    label: 'Expo 86 Corporation',
    kind: 'crown-corporation',
    family: 'historical-research',
    graphNode: 'expo-86-corporation',
    graphYear: 1985,
    aliases: ['Expo 86', 'Transpo 86', 'The 1986 World Exposition'],
    collectionIds: ['collected-expo-86-corporation'],
    sources: [
      { title: 'Expo 86 Corporation Act', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/80059' },
      RESWEST_SOURCES[1]
    ],
    note: 'The provincial Crown corporation organized the 1986 World Exposition in Vancouver. Its 1985 brochure identifies ResWest as the official accommodation agency.',
    nextAction: 'Locate dated identity standards for the symbol and wordmark used in the fair’s publications.'
  }),
  subject({
    id: 'reswest',
    label: 'ResWest',
    kind: 'service-brand',
    family: 'tourism-destination-management',
    aliases: ['Res West', 'Expo 86 accommodation reservations'],
    collectionIds: ['reswest'],
    sources: RESWEST_SOURCES,
    note: 'A privately operated provincial reservation service and the official accommodation agency for Expo 86. The fair advertised provincewide bookings for a single $5 charge.',
    nextAction: 'Identify the original colour advertisement, designer, artwork master and service end date.',
    relations: [{ subject: 'expo-86-corporation', type: 'used-by', label: 'Promoted by ·', source: RESWEST_SOURCES[1] }]
  }),
  subject({
    id: 'superhost',
    label: 'SuperHost',
    name: 'SuperHost, the Ministry of Tourism’s hospitality-training program',
    kind: 'service-brand',
    graphNode: 'ministry-of-tourism-1980',
    // The map's Ministry of Tourism ends in 1986, when Tourism, Recreation and Culture takes over.
    graphYear: 1985,
    aliases: ['SuperHost', 'Super Host', 'Expect the most'],
    collectionIds: ['superhost'],
    priority: 3,
    sources: [
      {
        title: 'A SuperHost newspaper advertisement credited to Claude Richmond, Minister of Tourism/Expo 86',
        citation: 'Supplied as a screenshot; the package cites the Squamish Times, 29 April 1986, page 19.'
      },
      { title: 'CIPO record 0904301, SuperHost & Design', url: 'https://ised-isde.canada.ca/cipo/trademark-search/0904301?lang=eng' }
    ],
    nextAction: 'Find when SuperHost began and the printed colours of its “Expect the most” mark.',
    note: 'The Ministry of Tourism’s training program for front-line hospitality staff, run in the Expo 86 years. It later went with the Province’s tourism marketing to Tourism BC and Destination BC, whose 2013 transfer lists a later SuperHost figure mark.',
    relations: [
      { subject: 'ministry-of-tourism-recreation-and-culture-1986', type: 'related-to', label: 'The ministry that followed, from November 1986' }
    ]
  }),
  subject({
    id: 'department-of-recreation-and-conservation',
    label: 'Department of Recreation and Conservation',
    kind: 'government-branch',
    aliases: ['Recreation and Conservation', 'Provincial Parks Branch', 'Commercial Fisheries Branch', 'Marine Resources Branch'],
    collectionIds: ['recreation-conservation'],
    priority: 3,
    sources: [
      { title: 'Department of Recreation and Conservation, Annual Report 1970', url: 'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1970.pdf' },
      { title: 'Department of Recreation and Conservation, Annual Report 1971', url: 'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf' },
      { title: 'Department of Recreation and Conservation, Annual Report 1972, Fish and Wildlife promotional activities, printed Z56', url: 'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1972.pdf#page=57' },
      { title: 'Department of Recreation and Conservation, Annual Report 1973', url: 'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf' }
    ],
    nextAction: 'Find who designed the five square symbols, and any identity manual; date the 1970 oval beyond its one report.',
    note: 'A provincial department, 1957–1976. Its 1970 oval, the five square symbols of its 1971–1973 reports and the separate Fish and Wildlife oval and Parks shield are held as reconstructions from the reports. The oval also appears on the 1972–73 hunting regulations cover. The department is a ministry in the government atlas, not a separate agency, and its branches have no atlas bodies of their own, so their marks sit with it; the Parks Branch’s two are also on BC Parks’ timeline.'
  }),
  subject({
    id: 'fish-and-wildlife-branch',
    label: 'Fish and Wildlife Branch',
    kind: 'government-branch',
    aliases: ['Fish & Wildlife Branch', 'F&W', 'Fish and Game Branch'],
    collectionIds: ['fish-wildlife-branch'],
    priority: 3,
    relations: [
      // The Game Commission it grew from is in the commissions register, which relations do not reach;
      // the note names it.
      { subject: 'department-of-recreation-and-conservation', type: 'part-of', label: 'A branch of the department, 1957–1976' }
    ],
    sources: [
      { title: 'BC Archives, British Columbia. Fish and Game Branch (authority record)', url: 'https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-fish-and-game-branch-2' },
      { title: 'BC Archives, British Columbia. Game Commission (authority record)', url: 'https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-game-commission' },
      { title: 'Department of Recreation and Conservation, Annual Report 1973, Fish and Wildlife Branch divider', url: 'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1973.pdf#page=22' }
    ],
    nextAction: 'Trace the branch after the department ended in 1976, and its marks under the later ministries.',
    note: 'The Department of Recreation and Conservation’s fish and wildlife branch: the Game Commission became its Fish and Game Branch on 1 April 1957, named the Fish and Wildlife Branch in 1966. Its square in the department’s 1971–1973 set, its F&W oval of the 1972–73 hunting regulations and its emblem beside its name in the 1973 report are held as reconstructions, shared with the department’s collection.'
  }),
  subject({
    id: 'bceid',
    label: 'BCeID',
    kind: 'service-brand',
    priority: 3,
    sources: [{ title: 'BCeID', url: 'https://www.bceid.ca/' }],
    nextAction: 'Obtain the BCeID wordmark as vector artwork and its positive version.',
    note: 'An online identity service of the Province. The held file is the reversed website image.'
  }),
  subject({
    id: 'environmental-reporting-bc',
    label: 'Environmental Reporting BC',
    kind: 'service-brand',
    priority: 3,
    sources: [{ title: 'Environmental Reporting BC', url: 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/reporting/environmental-reporting-bc' }],
    nextAction: 'Date later uses of the 2012–2016 lockup, if any.',
    note: 'The Province’s environmental-indicator reporting program.'
  }),
  subject({
    id: 'environmental-lab-bc',
    label: 'Environmental Lab BC',
    name: 'B.C. Environmental Laboratory',
    kind: 'government-branch',
    aliases: ['Analytical Laboratory'],
    priority: 3,
    sources: [{ title: 'B.C. Environmental Laboratory', url: 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/research/bc-environmental-lab' }],
    nextAction: 'Date the first use of the laboratory’s mark.',
    note: 'The Ministry of Environment’s analytical laboratory.'
  }),
  subject({
    id: 'sub-bc-stats',
    label: 'BC Stats',
    kind: 'government-branch',
    graphNode: 'sub-bc-stats',
    priority: 3,
    sources: [{ title: 'BC Stats', url: 'https://www2.gov.bc.ca/gov/content/data/about-data-management/bc-stats' }],
    nextAction: 'Seek original files of the BC Stats lockups.',
    note: 'The Province’s statistics agency; its marks are lockups on the BC mark.'
  }),
  subject({
    id: 'sub-bc-wildfire-service',
    label: 'BC Wildfire Service',
    kind: 'government-branch',
    graphNode: 'sub-bc-wildfire-service',
    aliases: ['BCWS', 'Wildfire Management Branch'],
    priority: 2,
    sources: [{ title: 'Cultural and Prescribed Fire annual summary report, 2025', url: 'https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prescribed-burning/annual_summary_report_crx_fire_2025.pdf' }],
    nextAction: 'Seek an original file of the shield and date its introduction.',
    note: 'The stacked and one-line lockups are two arrangements of one mark.'
  }),
  subject({
    id: 'sub-bc-coroners-service',
    label: 'BC Coroners Service',
    kind: 'government-branch',
    graphNode: 'sub-bc-coroners-service',
    priority: 3,
    sources: [{ title: 'BC Coroners Service strategic plan (2012)', url: 'https://oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-2012-10a-bccs-strategic-plan.pdf' }],
    nextAction: 'Find dated specimens before 2012.',
    note: 'A lockup on the BC mark.'
  }),
  subject({
    id: 'sub-bc-bid',
    label: 'BC Bid',
    kind: 'service-brand',
    graphNode: 'sub-bc-bid',
    priority: 3,
    sources: [{ title: 'BC Bid', url: 'https://www.bcbid.gov.bc.ca/' }],
    nextAction: 'Date the lockup from a primary specimen.',
    note: 'The Province’s procurement-notice service.'
  }),
  subject({
    id: 'sub-preparedbc',
    label: 'PreparedBC',
    kind: 'service-brand',
    graphNode: 'sub-preparedbc',
    priority: 3,
    sources: [{ title: 'PreparedBC', url: 'https://www2.gov.bc.ca/gov/content/safety/emergency-management/preparedbc' }],
    nextAction: 'Date the lockup and record any standalone campaign marks.',
    note: 'The Province’s emergency-preparedness program.'
  }),
  subject({
    id: 'bc-public-service-agency',
    label: 'BC Public Service',
    name: 'BC Public Service Agency',
    kind: 'central-agency',
    graphNode: 'bc-public-service-agency',
    aliases: ['Where ideas work'],
    priority: 2,
    sources: [{ title: 'BC Public Service corporate plan (2023)', url: 'https://www2.gov.bc.ca/assets/gov/careers/about-the-bc-public-service/corporate-digital/corporateplan_2023.pdf' }],
    nextAction: 'Find the earliest “Where ideas work” specimen.',
    note: 'The public service’s employer brand. The agency is its owner; the brand describes the whole public service, not the agency alone.'
  }),
  subject({
    id: 'sub-healthlink-bc',
    label: 'HealthLink BC',
    kind: 'health-service',
    family: 'specialist-health',
    graphNode: 'sub-healthlink-bc',
    priority: 2,
    sources: [{ title: 'HealthLink BC logo, as served by healthlinkbc.ca', url: 'https://www.healthlinkbc.ca/themes/custom/kb_bootstrap5/logo.svg' }],
    nextAction: 'Find dated earlier HealthLink BC marks.',
    note: 'A provincial health information service. Its logo is a lockup on the BC mark.'
  })
]
