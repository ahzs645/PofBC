// The province's program funders, the industry council and its delivery company appear
// together in publications. Each mark belongs to the organization named on it.
const iaf = 'investment-agriculture-foundation'
const ard = 'bc-agricultural-research-development-corporation'
const council = 'bc-agriculture-council'
const wali = 'western-agriculture-labour-initiative'
const classroom = 'bc-agriculture-in-the-classroom-foundation'
const iafName = 'Investment Agriculture Foundation of British Columbia'
const ardName = 'BC Agricultural Research & Development Corporation'
const archive = 'https://iafbc.ca/wp-content/uploads/2026/07/'
const waterGuide = 'https://www.bcclimatechangeadaptation.ca/app/uploads/BF01-Resource-Summary-Water-Management-Resources-Agriculture-BC-2021.pdf'
const waterPage = 'https://www.bcclimatechangeadaptation.ca/library/transferring-knowledge-about-water-management/'
const councilReport = 'https://bcac.ca/wp-content/uploads/2022/04/BCAC-Annual-Report-2022.pdf'
const audit = 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/agriculture-and-seafood/animal-and-crops/crop-production/tree-fruit-stabilization-plan/analysis_and_audit_of_organizations.pdf'
const anniversary = 'https://bcac.ca/wp-content/uploads/2022/04/2022-Gala-Program.pdf'
const climate = 'https://www.bcclimatechangeadaptation.ca/about-us/'
const orgbook = 'https://orgbook.gov.bc.ca/api/v4/topic/'
const launch = archive + 'IAF-2020-AnnualReport_FINAL.pdf'
const report2010 = archive + 'IAFBC_2010_AR_English_web.pdf'
const report2019 = archive + 'IAF-2019-AnnualReport_Web_Updated_compressed.pdf'
const report2021 = archive + 'Annual-Report-2021-Final_Web.pdf'
const registerLink = (title, url) => ({ title, url })
const transferSource = registerLink('BC Agriculture Council, Annual Report 2021, p. 18. The board’s decision and December handover', councilReport)
const auditSource = registerLink('BC tree fruit sector review, Analysis + Audit of Organizations (2021), pp. 3–4, 11', audit)

const iafHistory = 'Incorporated as a BC nonprofit society in October 1996, the Foundation manages federal and provincial funding for agriculture. In 1997 it funded the working group that established BC Agriculture Council. Canada’s 2007 inventory listed IAF as a shared-governance corporation with one federally appointed director out of 15. From 2008 IAF and the Council, through ARDCorp, jointly delivered climate adaptation programming. In December 2021 IAF took over delivery of the Environmental Farm Plan, Beneficial Management Practices and Climate & Agriculture Initiative BC programs. Its 2023/24 accounts identify 15 member organizations and a board of ten directors from across agriculture.'
const ardHistory = 'BC Corporate Registry dates the company’s registration to January 1984. By 2011 BC Agriculture Council wholly owned ARDCorp. It delivered government-funded programs for farmers, including environmental farm planning, climate adaptation and food traceability. The Council chose to concentrate on advocacy in June 2021. With the ministry’s agreement, three programs moved to IAF in December. The registry continues to list the company as active.'

export const AGRICULTURAL_PARTNER_FAMILY = {
  id: 'agricultural-partners', label: 'Agricultural program partners',
  description: 'Industry organizations and nonprofit societies that administer publicly funded agricultural programs, and their documented relatives.'
}

const subject = (id, name, kind, fields) => ({
  id, name, label: name, kind, family: AGRICULTURAL_PARTNER_FAMILY.id, scope: 'institution',
  graphNode: null, priority: 3, salaryEmployers: [], collectionIds: [], relations: [], ...fields
})

export const AGRICULTURAL_PARTNER_SUBJECTS = [
  subject(iaf, iafName, 'nonprofit-society', {
    aliases: ['IAF', 'B.C. Investment Agriculture Foundation'], collectionIds: ['collected-' + iaf],
    relations: [
      { type: 'related-to', subject: council, label: 'Funded the working group that established the Council in 1997' }
    ],
    sources: [
      registerLink('IAF 2023/24 audited statements, note 1, p. 20. Society, members, directors and funding', archive + 'IAF-Annual-Report-2023-24.pdf'),
      registerLink('BC Corporate Registry, society S0036049', orgbook + '2156151/credential-set'),
      registerLink('Treasury Board of Canada, 2007 Crown Corporations and Other Corporate Interests of Canada, p. 146', 'https://publications.gc.ca/collections/collection_2008/tb-ct/BT1-15-2007E.pdf'),
      registerLink('BC Agriculture Council’s 25th anniversary account, p. 6', anniversary),
      registerLink('Climate Change Adaptation Program history, joint delivery from 2008', climate),
      registerLink('IAF announcement of EFP and BMP transfer, January 2022', 'https://iafbc.ca/cap-efp-bmp-program-update/'),
      transferSource, registerLink('IAF 2020 Annual Report, back cover. New logo launched in January 2021', launch),
      registerLink('IAF logo use guidelines and current colourways', 'https://iafbc.ca/wp-content/uploads/2026/08/IAF-Logo-Use-Guidelines.pdf')
    ],
    note: iafHistory, nextAction: 'Identify the designer and introduction date of the curled leaves, and locate the original colour master.'
  }),
  subject(ard, ardName, 'corporate-subsidiary', {
    aliases: ['ARDCorp', 'B.C. Agricultural Research & Development Corporation'], collectionIds: ['collected-' + ard],
    relations: [
      { type: 'owned-by', subject: council, label: 'Wholly owned subsidiary documented in 2011 and 2021' },
      { type: 'transferred-operations-to', subject: iaf, label: 'Environmental Farm Plan, Beneficial Management Practices and Climate & Agriculture Initiative BC, December 2021' }
    ],
    sources: [
      registerLink('BC Corporate Registry, company BC0273604. Registration and status', orgbook + '279398/credential-set'),
      registerLink('Province of BC, November 2011. ARDCorp ownership and the agrifood portal', 'https://news.gov.bc.ca/releases/2011AGRI0043-001537'),
      registerLink('BC Bioenergy Network, ARDCorp’s Renewable Agri-Energy Initiative established in 2009', 'https://bcbioenergy.ca/what-we-do/capacity-building-portfolio/ardcorp/'),
      auditSource, transferSource, registerLink('BC Agriculture Council, October 2022. Separating advocacy and program delivery', 'https://bcac.ca/wp-content/uploads/2023/02/MLA-Newsletter-October-2022.pdf'),
      registerLink('ARDCorp’s own notice of the handover', 'https://ardcorp.ca/')
    ],
    note: ardHistory, nextAction: 'Identify the company’s original owners, when the Council acquired it, and the first use of the field-furrows logo.'
  }),
  subject(council, 'BC Agriculture Council', 'nonprofit-society', {
    aliases: ['BCAC', 'B.C. Agriculture Council'],
    sources: [registerLink('BC Agriculture Council history, 2022 gala program, p. 6', anniversary), transferSource,
      registerLink('Province of BC, Buy BC licensing agreement with BCAC, 2002', 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002AGF0019-000822.htm')],
    note: 'Industry advocacy council established in 1997. BCAC owned ARDCorp and WALI and took responsibility for managing Buy BC under a 2002 agreement.',
    nextAction: 'Compare the Council’s corporate logos across its own annual reports.'
  }),
  subject(wali, 'Western Agriculture Labour Initiative', 'corporate-subsidiary', {
    aliases: ['WALI', 'Western Agriculture Labour Initiative Corporation'],
    relations: [{ type: 'owned-by', subject: council, label: 'Labour-services subsidiary named in the 2021 sector audit' }],
    sources: [auditSource, registerLink('BCAC submission to the Select Standing Committee on Finance, June 2020', 'https://bcac.ca/wp-content/uploads/2021/04/2020-6-26-BCAC-Submission-to-the-Select-Standing-Committee-on-Finance.pdf'), registerLink('WALI website and visual identity', 'https://walicanada.ca/')],
    note: 'A separate Council subsidiary works with employers and governments on agricultural labour, including seasonal workers.',
    nextAction: 'Locate dated WALI artwork issued in its own name.'
  }),
  subject(classroom, 'BC Agriculture in the Classroom Foundation', 'nonprofit-society', {
    aliases: ['BCAITC'],
    sources: [registerLink('Foundation history, charitable status and provincial school fruit and vegetable program', 'https://www.bcaitc.ca/our-story')],
    note: 'Founded in 1992 and registered as a society in 1999, this charity works with provincial ministries on the BC School Fruit & Vegetable Nutritional Program.',
    nextAction: 'Document the foundation’s own marks separately from the school program and national organization.'
  })
]

const observedDate = '2026-11-25'
const record = (owner, file, fields) => ({
  file: 'identity-collected/' + owner + '/' + file, format: file.split('.').pop(), isVector: file.endsWith('.svg'),
  observedDate, ...fields
})
const vector = { evidenceType: 'native-pdf-vector-extraction', publisher: iafName }
const annual = 'https://iafbc.ca/reports/'
const water2021 = { date: '2021', label: '2021 water-management guide, PDF p. 2. Joint funding acknowledgements', source: waterGuide }
const ardAssets = 'https://ardcorp.ca/wp-content/uploads/'
export const AGRICULTURAL_PARTNER_BODIES = [
  {
    id: iaf, name: iafName, shortName: 'Investment Agriculture Foundation', kind: 'nonprofit-society',
    shelf: 'partners', cover: 'iaf-curled-leaves', graphNode: null, current: true, from: 1996, notes: iafHistory, status: 'asset-collected',
    assets: [
      record(iaf, 'curled-leaves-horizontal.png', {
        id: 'iaf-curled-leaves', label: 'Curled leaves and stacked name', designLabel: 'Curled leaves and stacked name',
        versionLabel: 'Sage and black', publisher: 'BC Climate Change Adaptation Program',
        sourcePage: waterPage, sourceUrl: waterGuide, sourceLocator: 'Funding acknowledgements, PDF p. 2', specimenDate: '2021',
        sha256: '3c72c6f9e373cb59b3d93d3bcc559b147e364b2416f8ab5081696b5cb27782e5',
        notes: 'Two curled leaves form a circle beside three lines of lettering and the italic “of British Columbia”. The guide identifies IAF and ARDCorp as joint administrators of the project funding.',
        fidelityNote: '192 × 96 pixel crop of the original embedded colour acknowledgement strip. The library dates the resource to 2021. The available PDF has a later cover and February 2022 metadata.'
      }),
      record(iaf, 'curled-leaves-horizontal-white.svg', {
        ...vector, id: 'iaf-curled-leaves-white', label: 'White curled leaves and name', variantOf: 'iaf-curled-leaves', versionLabel: 'White',
        sourcePage: annual, sourceUrl: report2019, sourceLocator: '2019 Annual Report, front cover', specimenDate: '2019', darkBackground: true,
        sha256: '4b8dde6bdfe50a253b160c886ec8c54c4048955506d5d81eb448dd212d09f765',
        notes: 'The Foundation used a white version of the horizontal curled leaves on its 2019 annual report.',
        fidelityNote: 'All 52 original white vector paths isolated from the cover.'
      }),
      record(iaf, 'curled-leaves-stacked.svg', {
        ...vector, id: 'iaf-curled-leaves-stacked', label: 'Curled leaves above the name',
        sourcePage: annual, sourceUrl: report2010, sourceLocator: '2010 Annual Report, front cover', specimenDate: '2010',
        sha256: 'd85062df7ea8f6f5c14857d7617aede64d950855fca3f2d73af9829efd267b7e',
        notes: 'In the 2010 report the leaf emblem sits above the stacked name on a green cover panel.',
        fidelityNote: 'Original 52 vector paths. The white and black artwork retains its published inks.'
      }),
      record(iaf, 'iaf-monogram.svg', {
        ...vector, publisher: 'BC Climate Change Adaptation Program', id: 'iaf-field-monogram', label: 'IAF monogram',
        sourcePage: waterPage, sourceUrl: waterGuide, sourceLocator: 'Replacement cover, PDF p. 1', specimenDate: '2022',
        alsoSeen: [{ date: '2021', label: '2020 Annual Report, front and back covers. January 2021 launch', source: launch }],
        sha256: '67e257b281f1ab98bf5e36938da900182775a7ef539910ef6466a3cc386a6e8e',
        notes: 'A field crosses the IAF initials beside the full name. The Foundation dates the new design’s launch to January 2021.',
        fidelityNote: '35 original coloured paths from the available guide’s cover. The PDF metadata dates that edition to February 2022.'
      }),
      record(iaf, 'iaf-25-years-white.svg', {
        ...vector, id: 'iaf-25-years', label: 'IAF 25th anniversary',
        sourcePage: annual, sourceUrl: report2021, sourceLocator: '2021 Annual Report, front cover', specimenDate: '2021', darkBackground: true,
        sha256: 'b08214b2349533c737e1ae658bf364ca7a659edbae61f839711426205102c92c',
        notes: 'A thin rule divides the new IAF name and monogram from “25 YEARS 1996–2021”.',
        fidelityNote: 'Original 53 outlined shapes from the Foundation’s anniversary report.'
      })
    ]
  },
  {
    id: ard, name: ardName, shortName: 'ARDCorp', kind: 'corporate-subsidiary',
    shelf: 'partners', graphNode: null, current: true, from: 1984, notes: ardHistory, status: 'asset-collected',
    assets: [
      record(ard, 'field-furrows.png', {
        id: 'ardcorp-field-furrows', label: 'ARDCorp field furrows', designLabel: 'ARDCorp field furrows', versionLabel: 'Full colour',
        publisher: ardName, sourcePage: 'https://ardcorp.ca/ardcorp_logo_cymk/', sourceUrl: ardAssets + '2018/09/ARDCORP_Logo_CYMK.png', sourceDate: '2018-09-21',
        alsoSeen: [water2021, { date: '2021', label: 'BC Agriculture Council, Annual Report 2021, p. 18', source: councilReport }],
        sha256: '36f02345fd80e9ed56d9f9f9cbb579c4db2b6e73481d476d4d0ccf7e5ded9c7a',
        notes: 'Three green furrows sweep beneath the grey lowercase name. The small lettering identifies the BC Agricultural Research & Development Corporation.',
        fidelityNote: 'Original transparent 917 × 555 PNG published by ARDCorp. The date is the media-library record.'
      }),
      record(ard, 'field-furrows-reversed.png', {
        id: 'ardcorp-field-furrows-reversed', variantOf: 'ardcorp-field-furrows', versionLabel: 'White', label: 'White field furrows',
        publisher: ardName, sourcePage: 'https://ardcorp.ca/ardcorp_logo_rev/', sourceUrl: ardAssets + '2017/11/ARDCORP_Logo_REV.png', sourceDate: '2017-11-08', darkBackground: true,
        sha256: '30b7ffa0b8286b0aad2878279eb31c52c104a7e29562e6abe2d04a690ed1c34d',
        notes: 'The white signature retains the expanded name and all three field furrows.',
        fidelityNote: 'Original transparent 917 × 555 reversed PNG published by ARDCorp. The date is the media-library record.'
      })
    ]
  }
]
