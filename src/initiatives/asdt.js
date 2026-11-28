// Administrative Service Delivery Transformation (ASDT), 2012–2019, and the Administrative Services
// Collaborative (ASC) it became: the ministry responsible for post-secondary education, the 25 public
// institutions and BCNET sharing administrative services. Research and artwork provenance:
// research/identity/asdt-2026-11-27/README.md.

export const ASDT_ID = 'asdt'
export const ASC_ID = 'administrative-services-collaborative'

const GOV = 'https://www2.gov.bc.ca/assets/gov/education/post-secondary-education/institution-resources-administration/'
const WAYBACK = 'https://web.archive.org/web/'
const source = (id, title, url, date, extra = {}) => ({ id, title, url, date, ...extra })
const at = (sourceId, page, locator) => ({ sourceId, ...(page ? { page } : {}), ...(locator ? { locator } : {}) })

export const ASDT_SOURCES = [
  source('project-page-2013', 'Ministry of Advanced Education, Innovation and Technology · Administrative Service Delivery Transformation project page (Wayback capture)', WAYBACK + '20130211025658/http://www.aved.gov.bc.ca:80/administrative_service_delivery/welcome.htm', 'Captured February 11, 2013'),
  source('deloitte', 'Deloitte · BC Post-Secondary Administrative Service Delivery Transformation Opportunity Assessment Final Report', GOV + 'asdt/deloitte_report.pdf', 'February 12, 2013'),
  source('key-messages', 'Ministry of Advanced Education, Innovation and Technology · Key messages and Q&As on the Deloitte report (Wayback capture)', WAYBACK + '20130228124821/http://www.aved.gov.bc.ca:80/administrative_service_delivery/docs/key-messages-qas.pdf', 'February 22, 2013'),
  source('progress-2013-14', 'ASDT · 2013/14 Progress Report', GOV + 'asdt/asdt_2013-14_progress_report_final.pdf', 'August 2014'),
  source('release-2015-01', 'Ministry of Advanced Education · News release 2015AVED0002-000042 (natural gas and purchasing card contracts)', 'https://news.gov.bc.ca/releases/2015AVED0002-000042', 'January 19, 2015'),
  source('release-2015-12', 'Ministry of Advanced Education · News release 2015AVED0079-002147 (ASDT savings)', 'https://news.gov.bc.ca/releases/2015AVED0079-002147', 'December 22, 2015'),
  source('progress-2015-16', 'ASDT · 2015/16 Progress Report, Working Together Delivering Value', GOV + 'asdt/asdt_2015-16_progress_report_final.pdf', 'PDF made December 19, 2016'),
  source('bulletin-2017', 'ASDT Update, 3rd Quarter 2016/2017', 'https://www.ufv.ca/media/assets/chief-financial-officer-and-vice-president-administration-/ASDT-Communication-Bulletin---Q3-2016-17.pdf', 'PDF made March 30, 2017',
    { shortTitle: 'ASDT Update, Q3 2016/17', note: 'Posted by the University of the Fraser Valley. The copy the user supplied is the same file.' }),
  source('asr-2014-15', 'Ministry of Advanced Education · 2014/15 Annual Service Plan Report', 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2014_2015/pdf/ministry/aved.pdf', '2015'),
  source('asr-2015-16', 'Ministry of Advanced Education · 2015/16 Annual Service Plan Report', 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2015_2016/pdf/ministry/aved.pdf', '2016'),
  source('asr-2016-17', 'Ministry of Advanced Education · 2016/17 Annual Service Plan Report', 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2016_2017/pdf/ministry/aved.pdf', '2017'),
  source('bcnet-2017-18', 'BCNET · Annual Review 2017|2018', 'https://bc.net/annual-review-2017', '2018')
]

export const ASC_SOURCES = [
  source('asc-plan-2019', 'Administrative Services Collaborative · Strategic Plan 2019/20 – 2021/22', GOV + 'asc/04_asc_strategic_plan_2020.pdf', 'May 2019'),
  source('asc-infographic-2020', 'Administrative Services Collaborative · Infographic, updated November 2020', GOV + 'asc/03_asc_infographic_2020.pdf', 'November 2020'),
  source('asc-page-2020', 'Province of BC · Administrative Services Collaborative page (Wayback capture)', WAYBACK + '20200806140145/https://www2.gov.bc.ca/gov/content/education-training/post-secondary-education/institution-resources-administration/administrative-services-collaborative', 'Captured August 6, 2020'),
  source('asc-plan-2023', 'Administrative Services Collaborative · Strategic Plan 2022/23 – 2025/26', GOV + 'asc/asc_strategic_plan_2023.pdf', '2023'),
  source('asc-progress-2026', 'Administrative Services Collaborative · Progress Report', GOV + 'asc/10860_administrative_services_collaborative_progress_report_fn.pdf', 'PDF made April 13, 2026'),
  source('asc-page', 'Province of BC · Administrative Services Collaborative', 'https://www2.gov.bc.ca/gov/content/education-training/post-secondary-education/institution-resources-administration/administrative-services-collaborative', 'Updated April 27, 2026')
]

const path = 'initiatives/asdt/'

export const asdtMark = {
  id: 'asdt-wordmark', title: 'ASDT wordmark', kind: 'program-identity',
  description: 'Lower-case green “asdt” among five shaded circles joined by thin lines, like a network. Beneath it is the full name, “Post Secondary Administrative Service Delivery Transformation”.',
  artworkStatus: 'native-vector-held',
  images: [
    {
      file: path + 'asdt-2015-16-progress-report.svg', label: '2015/16 Progress Report, back cover', shortLabel: 'Report vector',
      alt: 'Green asdt wordmark among five shaded circles joined by lines, with the full name beneath',
      caption: 'From the back cover of the 2015/16 Progress Report: the report’s own paths, radial gradients and letter outlines.',
      sourceId: 'progress-2015-16', sourcePage: 58, sourceLocator: 'Back cover, PDF page 58, bottom centre',
      date: '2016-12', dateLabel: 'Seen in a report made December 19, 2016', evidenceType: 'native-pdf-vector-extraction', downloadLabel: 'source vector'
    },
    {
      file: path + 'asdt-wordmark-2017.png', label: 'ASDT Update masthead, 2017', shortLabel: 'Bulletin image',
      alt: 'The same wordmark as a small image in the bulletin masthead',
      caption: 'The bulletin’s own 424 × 123 image with its transparency.',
      sourceId: 'bulletin-2017', sourcePage: 1, sourceLocator: 'Page 1, top right; the same image heads every page',
      date: '2017-03', dateLabel: 'Seen in a bulletin made March 30, 2017', evidenceType: 'printed-source-crop', downloadLabel: 'source image'
    }
  ],
  sourceRefs: [at('progress-2015-16', 58, 'Back cover'), at('bulletin-2017', 1, 'Masthead'), at('progress-2013-14', 1, 'Cover, as a small image')]
}

export const ascMark = {
  id: 'asc-signature', title: 'ASC signature', kind: 'program-identity',
  description: 'White ASC in condensed capitals on a teal square, beside “Administrative Services Collaborative” in grey and “For British Columbia’s Public Post-Secondary Sector” in teal.',
  artworkStatus: 'native-vector-held',
  images: [{
    file: path + 'asc-2019-strategic-plan.svg', label: '2019 Strategic Plan, back page', shortLabel: 'Plan vector',
    alt: 'Teal square with white ASC beside the words Administrative Services Collaborative, For British Columbia’s Public Post-Secondary Sector',
    caption: 'From the back page of the May 2019 strategic plan: its own paths and letter outlines.',
    sourceId: 'asc-plan-2019', sourcePage: 11, sourceLocator: 'Back page, PDF page 11',
    date: '2019-05', dateLabel: 'Seen in a plan dated May 2019', evidenceType: 'native-pdf-vector-extraction', downloadLabel: 'source vector'
  }],
  sourceRefs: [at('asc-plan-2019', 11, 'Back page'), at('asc-plan-2019', 1, 'Cover'), at('asc-infographic-2020', 1)]
}

const work = (id, title, kind, description, ...sourceRefs) => ({ id, title, kind, description, sourceRefs })

export const asdtWork = [
  work('deloitte-assessment', 'Opportunity assessment', 'study',
    'Deloitte assessed where the institutions could share administrative services. Its February 2013 report sorted the opportunities into three tiers. The ministry and institutions went ahead with tiers 1 and 2.',
    at('deloitte', 1), at('deloitte', 8), at('key-messages')),
  work('governance', 'Steering committee and collaboration office', 'governance',
    'An executive committee of institution presidents and ministry executives, chaired by the deputy minister, oversaw the initiative. A steering committee of vice-presidents and ministry staff ran it. An ASDT Collaboration Office supported it from October 2013.',
    at('progress-2013-14', 3), at('progress-2013-14', 6), at('progress-2015-16', 52)),
  work('joint-procurement', 'Joint procurement and BCNETSource', 'shared-service',
    'A joint procurement consortium of all 25 institutions began in May 2014. From April 1, 2016 its work continued as BCNETSource, a two-year pilot within BCNET. It ran agreements for natural gas, purchasing cards, vending, travel, printers and trades equipment.',
    at('progress-2013-14', 6), at('release-2015-01'), at('progress-2015-16', 10), at('bulletin-2017', 6), at('bcnet-2017-18', 18)),
  work('bcnet-membership', 'Every institution joins BCNET', 'shared-service',
    'All 25 public institutions became members of BCNET in October 2013. BCNET-led IT contracts later made up most of the reported benefits.',
    at('progress-2013-14', 6), at('progress-2015-16', 40), at('bulletin-2017', 2)),
  work('finance-centre', 'Finance Centre of Expertise', 'working-group',
    'A sector group for shared finance work: the commercial card, card merchant fees and a central deposit program.',
    at('progress-2015-16', 37), at('bulletin-2017', 1), at('bulletin-2017', 3)),
  work('executive-lead', 'Sector Executive Lead', 'role',
    'A two-year pilot from April 1, 2015. Barry Coulson held the role on secondment from Langara College. The steering committee put it on hold from April 1, 2017.',
    at('bulletin-2017', 1), at('bulletin-2017', 2)),
  work('erp', 'Enterprise resource planning', 'study',
    'The December 2016 forum spent its afternoon on the institutions’ ERP systems, for a report to the steering committee in spring 2017.',
    at('bulletin-2017', 3), at('bulletin-2017', 4), at('asr-2016-17', 29)),
  work('dlrn', 'Digital Learning Resources Network', 'seed-funding',
    'A working group building a business case for a new e-textbook model. The steering committee gave it seed funding from February 2016 and extended it to March 31, 2017.',
    at('bulletin-2017', 5))
]

export const asdtTimeline = [
  { id: 'budget-2012', date: '2012', title: 'Budget 2012 sets savings targets', description: 'The budget targeted savings in non-academic administration: $20 million in 2013/14 and a further $30 million in 2014/15.', sourceRefs: [at('project-page-2013')] },
  { id: 'assessment-begins', date: '2012-06-25', title: 'The opportunity assessment begins', description: 'The ministry, then Advanced Education, Innovation and Technology, and the institutions began the first phase. Its 2013/14 progress report dates the launch to July 2012.', sourceRefs: [at('project-page-2013'), at('progress-2013-14', 6)] },
  { id: 'deloitte-report', date: '2013-02-12', title: 'Deloitte’s final report', description: 'The ministry posted it on February 22, 2013. Implementation began in March 2013.', sourceRefs: [at('deloitte', 1), at('key-messages')] },
  { id: 'forum-2013', date: '2013-06', title: 'First sector partnership forum', description: 'More than 60 people attended, from all 25 institutions.', sourceRefs: [at('progress-2013-14', 6)] },
  { id: 'bcnet-2013', date: '2013-10', title: 'All 25 institutions join BCNET', description: 'The ASDT Collaboration Office was set up the same month.', sourceRefs: [at('progress-2013-14', 6)] },
  { id: 'consortium', date: '2014-05', title: 'Joint procurement consortium', description: 'All 25 institutions were members.', sourceRefs: [at('progress-2013-14', 6), at('asr-2014-15', 23)] },
  { id: 'savings-2015', date: '2015-12-22', title: 'Savings reported', description: 'The ministry reported $10.5 million in 2013/14 and $30.66 million in 2014/15, against a goal of $50 million over three years.', sourceRefs: [at('release-2015-12')] },
  { id: 'bcnetsource', date: '2016-04-01', title: 'BCNETSource begins', description: 'Joint procurement moved to a two-year pilot within BCNET.', sourceRefs: [at('progress-2015-16', 10)] },
  { id: 'forum-2016', date: '2016-12-01', title: 'Partnership forum at SFU Harbour Centre', description: 'About 80 people attended. The 2015/16 progress report gave $36.64 million in benefits for that year; the bulletin gives $36.66 million.', sourceRefs: [at('bulletin-2017', 3), at('progress-2015-16', 40)] },
  { id: 'benefits-2017', date: '2017', title: '$77.9 million in benefits', description: 'The ministry’s 2016/17 report gave this total since the initiative began.', sourceRefs: [at('asr-2016-17', 29), at('bulletin-2017', 2)] },
  { id: 'renamed', date: '2019-05', title: 'Renamed the Administrative Services Collaborative', description: 'The new strategic plan adopted the name.', sourceRefs: [at('asc-plan-2019', 3), at('asc-plan-2019', 11)] }
]

export const ascTimeline = [
  { id: 'plan-2019', date: '2019-05', title: 'A new name and strategic plan', description: 'The steering committee’s co-chairs announced the new name. The plan says the initiative was founded in 2012/13 as ASDT.', sourceRefs: [at('asc-plan-2019', 3), at('asc-plan-2019', 4)] },
  { id: 'launch-2020', date: '2020', title: 'The collaborative launches', description: 'The November 2020 infographic says the collaborative was launched in 2020 with its new name and plan.', sourceRefs: [at('asc-infographic-2020', 2), at('asc-page-2020')] },
  { id: 'plan-2023', date: '2023', title: 'A second strategic plan', description: 'A three-year plan for 2022/23 to 2025/26, launched in early 2023.', sourceRefs: [at('asc-plan-2023', 3), at('asc-progress-2026', 2)] },
  { id: 'progress-2026', date: '2026-04', title: 'A progress report', description: 'The collaborative is now led by a leadership group of senior people from the institutions, BCNET and the ministry.', sourceRefs: [at('asc-progress-2026', 2), at('asc-page')] }
]

const RELATED = [
  { label: 'Ministry of Advanced Education in 2016', to: { view: 'government', node: 'ministry-of-advanced-education-2013', year: 2016 } },
  { label: 'BCNET', to: { view: 'government', mode: 'related', node: 'bcnet' } }
]

export const asdtDetail = (entry) => ({
  id: entry.id, title: entry.title,
  hero: { title: entry.title, eyebrow: 'Ministry of Advanced Education · public post-secondary institutions · BCNET', description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  sources: [...ASDT_SOURCES, ...ASC_SOURCES],
  relatedLinks: RELATED,
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'The ASDT wordmark', description: 'Its dates are the documents’, not the date the mark was adopted.', records: [asdtMark], featuredId: asdtMark.id },
    { id: 'work', label: 'Work', type: 'records', layout: 'text', title: 'What ASDT did', records: asdtWork },
    { id: 'timeline', label: 'Timeline', type: 'timeline', records: asdtTimeline },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Reports, releases and bulletins', records: [...ASDT_SOURCES, ...ASC_SOURCES] }
  ]
})

export const ascDetail = (entry) => ({
  id: entry.id, title: entry.title,
  hero: { title: entry.title, eyebrow: 'Ministry responsible for post-secondary education · public institutions · BCNET', description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  sources: ASC_SOURCES,
  relatedLinks: [
    { label: 'Ministry of Post-Secondary Education and Labour', to: { view: 'government', node: 'ministry-of-post-secondary-education-and-labour-2026', year: 2026 } },
    RELATED[1]
  ],
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'The ASC signature', description: 'Its date is the plan’s, not the date the mark was adopted. Later reports set ASC in other ways and a deeper teal.', records: [ascMark], featuredId: ascMark.id },
    { id: 'timeline', label: 'Timeline', type: 'timeline', records: ascTimeline },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Plans, reports and the ministry’s page', records: ASC_SOURCES }
  ]
})
