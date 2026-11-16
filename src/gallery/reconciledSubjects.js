// Owners for artwork the gallery already held without a register subject (the 15 November 2026
// gallery audit: 53 entries in 12 collections plus BC Cancer Foundation's two marks).
//
// Each subject owns only the entries recorded under it. A program brand on the BC mark is not its
// ministry's corporate logo, and a foundation's mark is not the health agency's. Where a subject is
// an atlas body its id is the atlas id, so the gallery's existing entry owners resolve to it.
// PROGRAM_ENTRY_OWNERS gives the entries that had no owner at all an explicit one.

export const RECONCILED_FAMILIES = [
  {
    id: 'provincial-programs',
    label: 'Provincial branches, services and programs',
    description: 'Ministry branches, online services, programs and campaigns, many shown on or beside the BC mark. Each specimen keeps its own owner.'
  }
]

/** Entries that were held with no owner: each is given the program it was published for. */
export const PROGRAM_ENTRY_OWNERS = {
  'welcome-bc': 'welcome-bc',
  'vector-welcomebc-2016': 'welcome-bc',
  'vector-welcomebc-current': 'welcome-bc',
  'environmental-reporting-bc': 'environmental-reporting-bc',
  'environmental-lab-bc': 'environmental-lab-bc',
  'stronger-bc': 'stronger-bc',
  'vector-BCID_StrongerBC_RGB_pos': 'stronger-bc',
  'vector-BCID_StrongerBC_RGB_rev': 'stronger-bc',
  'vector-BCID_StrongerBC_Solid_pos': 'stronger-bc',
  'vector-BCID_StrongerBC_Solid_rev': 'stronger-bc',
  'vector-StrongerBC_RGB_pos': 'stronger-bc',
  'vector-StrongerBC_Solid_pos': 'stronger-bc',
  'pacific-gateway': 'pacific-gateway',
  'vector-canada-starts-here-2012': 'pacific-gateway',
  'vector-canada-starts-here-bc-jobs-plan-2012': 'pacific-gateway',
  'best-place-on-earth': 'best-place-on-earth',
  'bc-travel-industry-ca-1970': 'department-of-travel-industry',
  'bceid-reversed': 'bceid',
  'bceid-reversed-rebuilt': 'bceid'
}

const subject = ({ id, label, name = label, kind, family = 'provincial-programs', graphNode = null, collectionIds = [], aliases = [], salaryEmployers = [], priority = 2, scope = 'core', sources, nextAction, note, relations = [], ...rest }) => ({
  id, label, name, kind, family, graphNode, aliases, collectionIds, salaryEmployers, priority, scope, sources, nextAction, note, relations, ...rest
})

export const RECONCILED_SUBJECTS = [
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
    sources: [{ title: 'BC Timber Sales business plan 2023/24–2025/26', url: 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bcts_business_plan_2023-2024_to_2025-2026_final.pdf' }],
    nextAction: 'Find the earliest dated slab-serif wordmark and an original file for the current mark.',
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
    sources: [{ title: 'Justice Institute of British Columbia', url: 'https://www.jibc.ca/' }],
    nextAction: 'Date the current logo and monogram and record earlier institutional marks.',
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
    collectionIds: ['specimens-work-bc'],
    sources: [{ title: 'WorkBC logo, as served by workbc.ca', url: 'https://www.workbc.ca/themes/custom/workbc/logo.svg' }],
    nextAction: 'Date the first WorkBC lockup on the BC mark from a primary specimen.',
    note: 'A provincial employment service; its own marks and its lockup on the BC mark are separate entries.'
  }),
  subject({
    id: 'welcome-bc',
    label: 'WelcomeBC',
    kind: 'service-brand',
    collectionIds: ['specimens-welcome-bc'],
    sources: [{ title: 'WelcomeBC logo, as served by welcomebc.ca', url: 'https://www.welcomebc.ca/getmedia/ce0988e3-03e0-4fed-a743-8ace3a34d1ce/WelcomeBC_cmyk_pos_Print.svg' }],
    nextAction: 'Find dated specimens from before 2016.',
    note: 'An immigration and settlement program brand of the Province. It is not an atlas body, so it has no organization link.'
  }),
  subject({
    id: 'stronger-bc',
    label: 'StrongerBC',
    kind: 'campaign',
    collectionIds: ['specimens-stronger-bc'],
    sources: [
      { title: 'BC visual identity: download marks', url: 'https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks' },
      { title: 'Use of the StrongerBC marks (January 2021)', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/corporate-identity-assets/visid-pdfs/bcid_use_of_strongerbc.pdf' }
    ],
    nextAction: 'Record when the StrongerBC marks were retired, if they have been.',
    note: 'A provincial economic-recovery plan and campaign identity, published as endorsed and standalone marks.'
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
    kind: 'government-branch',
    priority: 3,
    sources: [{ title: '“This is British Columbia”, published by the Department of Travel Industry, undated [about 1970]', citation: 'Print publication; no online copy recorded.' }],
    nextAction: 'Find dated publications of the department, 1967–1975, that show the map-and-dogwood mark.',
    note: 'A provincial department, 1967–1975. Its map-and-dogwood mark is held as a reconstruction from a photograph of an undated book. The department is a ministry in the government atlas, not a separate agency.'
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
    collectionIds: ['specimens-public-service'],
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
