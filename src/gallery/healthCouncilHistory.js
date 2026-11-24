// The Society and the provincial service used different ribbon inscriptions.
const council = 'health-officers-council-bc'
const service = 'bc-public-health-service'
const department = 'department-of-health-services-and-hospital-insurance-1959'
const councilName = 'Health Officers Council of British Columbia'
const serviceName = 'British Columbia Public Health Service'
const senateLetter = 'https://sencanada.ca/content/sen/committee/421/LCJC/Briefs/HealthOffCouncilBC_e.pdf'
const constitution = 'https://www.healthofficerscouncil.net/wp-content/uploads/2012/12/const-and-bylaws-approved-jan-10-2012.pdf'
const societyHistory = 'https://www.healthofficerscouncil.net/about/overview-of-hoc/'
const heronPage = 'https://www.healthofficerscouncil.net/about-the-hoc-logo/'
const heronFile = 'https://www.healthofficerscouncil.net/wp-content/uploads/2025/11/HOC-Logo-Text-150x150-Transparent-11.27.2025.png'
const badgePage = 'https://bcnursinghistory.ca/war-medals-badges/'
const badgeFile = 'https://bcnursinghistory.ca/wp-content/uploads/2025/01/IMG_1697-2-300x225-1.jpg'
const departmentAct = 'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/681611917'
const healthReport = 'https://doi.org/10.14288/1.0377955'

const subject = { graphNode: null, priority: 3, salaryEmployers: [], family: 'specialist-health', scope: 'core' }
const societyNote = 'Founded in September 1947 and incorporated as a society in June 1998, the Council brings together public health physicians and advises on public health policy. Its members include medical health officers employed by regional health authorities.'
const serviceNote = 'The BC History of Nursing Society identifies the 1961 badge of provincial public health nursing director Monica Green as BC Public Health Service insignia. The provincial Health Branch had responsibility for public health at that date.'

export const HEALTH_COUNCIL_SUBJECTS = [
  {
    ...subject, id: council, name: councilName, label: councilName,
    kind: 'nonprofit-society', scope: 'institution', aliases: ['Health Officers Council of BC', 'HOC', 'HOCBC'],
    collectionIds: [`collected-${council}`], relations: [],
    sources: [
      { title: 'Council history, incorporation and mandate', url: societyHistory },
      { title: 'Council constitution and bylaws, 2012, p. 1', url: constitution },
      { title: 'Council submission to the Senate, March 9, 2017, p. 1', url: senateLetter },
      { title: 'Council explanation and designer credits for the herons and dogwood logo', url: heronPage }
    ],
    note: societyNote,
    nextAction: 'Identify the designer and first use of the crowned emblem, and date the adoption of the herons and dogwood.'
  },
  {
    ...subject, id: service, name: serviceName, label: 'BC Public Health Service',
    kind: 'health-service', aliases: ['BC Public Health Service insignia'],
    collectionIds: [`collected-${service}`],
    relations: [{ type: 'service-of', subject: department, label: 'Provincial department responsible for public health in 1961' }],
    sources: [
      { title: 'BC History of Nursing Society, Monica Green’s 1961 badge', url: badgePage },
      { title: 'BC History of Nursing Society, Monica Green and the provincial Public Health Nursing Division', url: 'https://bcnursinghistory.ca/project/green-monica-1917-2004/' },
      { title: 'Dorothy Slaughter fonds, additional Public Health Service crests and badge', url: 'https://bcnursinghistory.ca/project/dorothy-slaughter/' },
      { title: 'Department of Health Services and Hospital Insurance Act, RSBC 1960, c. 102, ss. 5–8', url: departmentAct },
      { title: 'Department of Health annual report for 1975, published 1976', url: healthReport, note: 'The departmental chart records the Division of Venereal Disease Control. The title page bears the provincial arms. The specific division publication said to reproduce the badge emblem remains to be identified.' }
    ],
    note: serviceNote,
    nextAction: 'Locate the separate 1975 division report or a dated departmental impression showing the Public Health Service ribbon.'
  },
  {
    ...subject, id: department, name: 'Department of Health Services and Hospital Insurance', label: 'Department of Health Services and Hospital Insurance',
    graphNode: department, graphYear: 1961, kind: 'government-branch', aliases: [], collectionIds: [], relations: [],
    sources: [{ title: 'Department of Health Services and Hospital Insurance Act, RSBC 1960, c. 102', url: departmentAct }],
    identityStatus: 'distinct-unconfirmed',
    note: 'In 1961 the department included the Health Branch, the Branch of Mental Health Services and the British Columbia Hospital Insurance Service. The Deputy Minister of Health had jurisdiction over the Health Branch and public health.',
    nextAction: 'Identify a dated signature issued in the department’s own name.'
  }
]

const observedDate = '2026-11-24'

export const HEALTH_COUNCIL_BODIES = [
  {
    id: council, name: councilName, kind: 'nonprofit-society', graphNode: null, from: 1947, current: true,
    status: 'asset-collected', notes: societyNote,
    assets: [
      {
        id: 'hocbc-crowned-emblem-2017', label: 'Council emblem on Senate letterhead', publisher: councilName,
        file: `identity-collected/${council}/emblem-2017.jpg`, format: 'jpg', isVector: false, observedDate,
        sourcePage: senateLetter, sourceLocator: 'March 9, 2017, pp. 1–2, letterhead', sourceDate: '2017-03-09',
        sourceFile: 'HealthOffCouncilBC_e.pdf, image object 83', sha256: '4b96cd80ac0862de6815b69ff4fdcaa504a5759ae1c7db9a56574a23ddf83bd0',
        alsoSeen: [{ label: 'Council constitution and bylaws, 2012, p. 1', source: constitution, date: '2012' }],
        notes: 'The ribbons read “HEALTH”, “OFFICERS” and “COUNCIL OF B.C.” beneath the crowned shield and winged staff.',
        fidelityNote: 'Original 238 × 274 JPEG extracted from the Senate’s copy of the signed letter. The 2012 constitution also shows this design.'
      },
      {
        id: 'hocbc-herons-and-dogwood', label: 'Herons and dogwood', publisher: councilName,
        file: `identity-collected/${council}/herons-and-dogwood.png`, format: 'png', isVector: false, observedDate,
        sourcePage: heronPage, sourceUrl: heronFile, sourceDate: '2025',
        dateNote: 'The Council’s published image file is dated November 2025. The adoption date is unconfirmed.',
        creator: 'Jenna Kelly and Selenna Ho of the Public Health Association of BC, in collaboration with Indigenous artist Andrea Fritz',
        sha256: '2e2ecb65794c1416ba639e45dfc83bbd671a7706585f4f6290342a76e4e90828',
        notes: 'Two herons flank a dogwood flower against a landscape of water, forest and mountains. Lettering around the landscape identifies the society of public health physicians and its founding year.',
        fidelityNote: 'Original transparent 604 × 607 PNG published by the Council.'
      }
    ]
  },
  {
    id: service, name: serviceName, kind: 'health-service', graphNode: null,
    status: 'asset-collected', notes: serviceNote,
    assets: [{
      id: 'bc-public-health-service-green-badge', label: 'Monica Green’s Public Health Service badge', publisher: 'BC History of Nursing Society',
      file: `identity-collected/${service}/monica-green-badge.jpg`, format: 'jpg', isVector: false, observedDate,
      sourcePage: badgePage, sourceUrl: badgeFile, specimenDate: '1961',
      dateNote: 'The Society dates the physical badge to 1961. The date of the catalogue photograph is unknown.',
      sha256: '4472e87e6002455fc1098a88921c76c0cb093cd1fd2a68615d5eab5494bad634',
      notes: 'The Society catalogues this gold-coloured badge under Monica Green. Its ribbons read “PUBLIC”, “HEALTH” and “SERVICE”. The photograph shows the badge on blue fabric.',
      fidelityNote: 'Published 300 × 225 catalogue photograph. The metal finish records the physical object’s appearance.'
    }]
  }
]
