import { fireSmartGuide, fireSmartDesigns, fireSmartSpecimens } from '../gallery/fireSmart.js'
import { fireSmartParent } from './fireSmartIndex.js'

const site = 'https://firesmartbc.ca/'
const source = (id, title, path, date) => ({ id, title, url: new URL(path, site).href, date })
const sources = [
  source('guide', 'FireSmart BC Brand Guidelines, version two', fireSmartGuide, 'July 2025'),
  source('early-guide', 'FireSmart BC Brand Guidelines, earlier edition', 'wp-content/uploads/2023/04/07.01.22_FSBC_BrandGuidelines.pdf', 'January 2022 cover date'),
  source('strategy', 'BC FireSmart Committee Strategic Plan', 'wp-content/uploads/2022/07/BCFSC-Strategic-Plan_Final-Print-Ready.pdf', '2022'),
  source('website-2019', 'B.C. Flood and Wildfire Review action plan update', 'https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/emergency-preparedness-response-recovery/embc/abbott-chapman_action_plan_update_april_30_2019.pdf', 'April 30, 2019'),
  source('who', 'FireSmart BC — Who we are', 'who-we-are/'),
  source('programs', 'FireSmart BC — What is FireSmart?', 'what-is-firesmart/'),
  source('ember', 'FireSmart B.C. welcomes new mascot Ember the FireSmart Fox', 'wp-content/uploads/2021/03/FireSmart-BC-Ember-Press-Release.pdf', 'March 22, 2021'),
  source('review-2020', 'FireSmart BC looks back on 2020', 'firesmart-looks-back-on-2020/'),
  source('review-2021', 'FireSmart BC looks back on a difficult but groundbreaking year', 'firesmart-bc-looks-back-on-a-difficult-but-groundbreaking-year/'),
  source('report22', 'FireSmart BC Annual Report 2022', 'wp-content/uploads/2023/03/FireSmart-BC-2022-Annual-Report.pdf'),
  source('report23', 'FireSmart BC Annual Report 2023', 'wp-content/uploads/2024/04/FireSmart-BC-Annual-Report-2023.pdf'),
  source('report24', 'FireSmart BC Annual Report 2024', 'wp-content/uploads/2025/02/FireSmart_BC_2024_Annual_Report.pdf'),
  source('report25', 'FireSmart BC Annual Report 2025', 'wp-content/uploads/2026/04/FireSmart_AnnualReport2025_1C_FINAL.pdf'),
  source('hpp', 'Overview of the FireSmart Home Partners Program', 'wp-content/uploads/2024/03/2024-Home-Partners-Program.pdf'),
  source('wmp', 'FireSmart BC Wildfire Mitigation Program', 'wmp/'),
  source('lfcp', 'Local FireSmart Collective Program', 'lfcp/'),
  source('collective-process', 'How the Local FireSmart Collective Program works', 'lfcp/how-the-local-firesmart-collective-program-works/'),
  source('collective-intro', 'FireSmart BC introduces the Local FireSmart Collective Program', 'https://www.youtube.com/watch?v=j4e9IG9BJ3w', 'April 22, 2026'),
  source('deer-ridge', 'How Deer Ridge is Putting FireSmart on the Map', 'how-deer-ridge-is-putting-firesmart-on-the-map/'),
  source('plant-history', 'The FireSmart Plant Program Continues to Grow', 'the-firesmart-plant-program-continues-to-grow/'),
  source('plant', 'FireSmart BC Plant Program', 'landscaping-hub/plant-program/'),
  source('summit23', 'Exploring the 2023 Wildfire Resiliency and Training Summit', 'exploring-the-2023-wildfire-resiliency-and-training-summit/'),
  source('summit24', 'Insights from the 2024 Wildfire Resiliency and Training Summit', 'insights-from-the-2024-wildfire-resiliency-and-training-summit/'),
  source('summit', 'Wildfire Resiliency and Training Summit — Victoria 2026', 'wildfire-resiliency-and-training-summit/'),
  source('education', 'FireSmart BC Education Program and Classroom Contest', 'educationprogram/'),
  source('library', 'FireSmart BC Library Program and Readers’ Kit', 'resource/firesmart-bc-library-program/'),
  source('readers-kit', 'Wildfire Resiliency Readers’ Kit Catalogue', 'wp-content/uploads/2026/08/Wildfire-Resiliency-Readers-Kit-Catalogue.pdf'),
  source('farm', 'Farm and Ranch Wildfire Preparedness', 'farm-and-ranch/'),
  source('farm-form', 'FireSmart BC Farm & Ranch Assessment — completed example', 'wp-content/uploads/2024/12/FireSmart_FarmRanchAssessmentForm_Example-4.pdf'),
  source('cfrc', 'Community FireSmart and Resiliency Collaboratives', 'cfrc/'),
  source('funding', 'UBCM Community Resiliency Investment Program Guide', 'https://www.ubcm.ca/sites/default/files/2024-07/LGPS_CRI-FCFS_Application_2020%20ProgramGuide_2024-07.pdf'),
  source('representatives', 'Local FireSmart Representatives', 'local-firesmart-representatives/'),
  source('network', 'FireSmart BC Coordinator directory', 'firesmart-coordinators/'),
  source('research', 'FireSmart BC Research Corner', 'research-corner/'),
  source('cultural', 'Culturally Significant Sites and Green Spaces Guide', 'wp-content/uploads/2023/08/08.30.23_FSBC_CSSGS_Guide.pdf'),
  source('prep-day', 'Wildfire Community Preparedness Day', 'wildfire-community-preparedness-day-is-almost-here/'),
  source('podcast', 'The Get FireSmart Podcast', 'the-get-firesmart-podcast/'),
  source('campaign25', 'FireSmart BC 2025 spring campaign announcement', 'wp-content/uploads/2025/05/Press-Release_FireSmart-BC%E2%84%A2-2025-Spring-Campaign.pdf', 'May 13, 2025'),
  source('campaign26', 'See Through FireSmart Eyes', 'prepare/', '2026 summer campaign')
]
const ref = (sourceId, page) => ({ sourceId, ...(page ? { page } : {}) })
const event = (id, date, title, description, sourceRefs, program) => ({ id, date, title, description, sourceRefs, program })
const timeline = [
  event('alberta', '1990', 'The Canadian work begins in Alberta', 'The Alberta Forest Service convened a committee to study the risk where forests meet homes and settlements.', [ref('strategy', 9)]),
  event('early-bc', 'Late 1990s', 'FireSmart work reaches British Columbia', 'The provincial committee’s retrospective places early local activity in this period, before there was a province-wide coordinating body.', [ref('strategy', 9)]),
  event('national-brand', '1999–2008', 'A national identity takes shape', 'The FireSmart name dates to 1999. By 2008 a national program was in place.', [ref('strategy', 9)]),
  event('committee', 'May 2017', 'BC Wildfire Service initiates the BC FireSmart Committee', 'The committee brought agencies together to coordinate prevention work and the seven FireSmart disciplines across B.C.', [ref('ember'), ref('strategy', 9)]),
  event('home-pilot', '2017–2021', 'Home Partners tests professional assessments', 'Seven local authorities in western Canada piloted the assessment model. In 2022 the program became available to jurisdictions across B.C. and Canada.', [ref('hpp')], 'wildfire-mitigation'),
  event('cri', '2018', 'The Province starts Community Resiliency Investment', 'Its FireSmart Community Funding & Supports stream helped First Nations and local governments pay for prevention work.', [ref('funding', 1)]),
  event('website', 'By April 2019', 'A provincial FireSmart website goes online', 'The Province’s April action plan update records the launch of a website where residents could learn to identify wildfire risks and reduce them.', [ref('website-2019', 54)]),
  event('deer-ridge', '2019', 'Deer Ridge becomes B.C.’s 100th recognized neighbourhood', 'Residents cleared yard waste together and earned recognition through the FireSmart Canada Neighbourhood Recognition Program.', [ref('deer-ridge')], 'local-collective'),
  event('farm-outreach', '2020', 'FireSmart BC publishes resources for farmers and ranchers', 'Its year-end review records a dedicated farm and ranch web page alongside assessment resources for critical infrastructure.', [ref('review-2020')], 'farm-and-ranch'),
  event('ember-introduction', 'March 22, 2021', 'Ember makes her debut', 'A Canada-wide naming contest drew more than 500 submissions. Arlene S. of Swansea Point, B.C., submitted the winning name for the national mascot.', [ref('ember', 1)]),
  event('plant-pilot', 'Spring 2021', 'Plant tags appear in garden centres', 'Two Art Knapp stores piloted the landscaping guide and tags that identify fire-resistant plants for shoppers.', [ref('review-2021'), ref('plant-history')], 'plant-program'),
  event('national-centre', '2021', 'FireSmart Canada joins the Canadian Interagency Forest Fire Centre', 'The national centre became the institutional home for FireSmart Canada. The BC committee continued to coordinate the provincial work.', [ref('strategy', 9)]),
  event('collaboratives', '2021', 'Community FireSmart and Resiliency Collaboratives begin', 'The BC committee introduced local and regional forums for First Nations, fire departments, governments and other partners to plan across the seven disciplines.', [ref('cfrc')]),
  event('earlier-guide', 'January 2022', 'An earlier guide records the provincial identity', 'Its cover dates this edition to January 2022. It measures clear space by the flame icon and assigns a colour and icon to each of the seven disciplines.', [ref('early-guide', 1), ref('early-guide', 2), ref('early-guide', 9)]),
  event('library-start', 'Summer 2022', 'The Library Program begins in the Thompson-Nicola region', 'Reading lists, colouring contests and Read with Ember videos brought wildfire education into public libraries.', [ref('report22', 10)], 'library'),
  event('joint-summit', 'May 10–14, 2023', 'Two events meet in Vancouver', 'The FireSmart BC Conference and the Wildland-Urban Interface Symposium became one summit. Conference sessions in Vancouver were followed by field training in North Vancouver.', [ref('summit23'), ref('report23', 13)], 'training-summit'),
  event('school-launch', 'Late spring 2023', 'The Education Program opens to teachers', 'FireSmart BC developed classroom lessons with educators and published them on a dedicated site linked to the provincial curriculum.', [ref('report23', 11)], 'education'),
  event('summit-awards', '2024', 'The summit comes to Prince George', 'The Lynn Orstad Award continued and the first BC Wildland Firefighter Awards recognized firefighters at the gathering.', [ref('summit24')], 'training-summit'),
  event('wmp-transition', '2024', 'Home Partners becomes the B.C. Wildfire Mitigation Program', 'B.C. took on management of the former national program in the province and built its own assessment platform and training capacity.', [ref('report24', 7)], 'wildfire-mitigation'),
  event('farm-example', 'December 2024', 'A sample assessment maps the farm around its buildings', 'The example opens with an illustrated farm divided into three assessment zones around a barn. December 3 is the PDF creation date.', [ref('farm-form', 1)], 'farm-and-ranch'),
  event('class-contest', 'Spring 2025', 'The second classroom contest receives 63 entries', 'The contest gave classes a way to share their work. The program also added its teaching resources to the BC Teachers’ Federation classroom database.', [ref('report25', 9)], 'education'),
  event('brand-guide', 'July 2025', 'The guide brings four related identities together', 'The guide places the mitigation, collective and plant programs and the training summit under the provincial mark. It documents the collective identity while the program was still being developed.', [ref('guide', 16), ref('report25', 10)]),
  event('retail-expansion', '2025', 'The plant program extends its work with retailers', 'The team developed a landscaping course and explored partnerships with hardware retailers. Its annual report describes this work under Plant & Hardware Program.', [ref('report25', 11)], 'plant-program'),
  event('assessment-delivery', '2025', 'Home assessments pass 3,000 in a year', 'FireSmart BC reported participation by 180 agencies and training for 257 new Wildfire Mitigation Specialists that year.', [ref('report25', 10)], 'wildfire-mitigation'),
  event('strategy-renewal', '2025', 'The committee sets its direction through 2030', 'The 2026–2030 strategic plan sets priorities for provincial work. Three standing committees advised on research, Indigenous outreach and strategic direction during 2025.', [ref('report25', 4), ref('report25', 5)]),
  event('summit-victoria', '2026', 'Victoria hosts the training summit', 'More than 700 people gathered under the theme “Collective Action: Empowering Communities.”', [ref('summit')], 'training-summit'),
  event('collective-introduction', 'April 2026', 'FireSmart BC introduces the Local FireSmart Collective Program', 'The B.C. successor to national neighbourhood recognition also welcomes community organizations. A representative and an advocate develop an assessment and an action plan.', [ref('collective-intro'), ref('collective-process')], 'local-collective')
]

const marks = fireSmartDesigns.map(({ key, title, page, notes, poses }) => {
  const id = 'firesmart-bc-' + key
  const images = fireSmartSpecimens.assets.filter((asset) => asset.id === id || asset.variantOf === id).map((asset) => ({
    ...(poses ? { displayId: asset.id } : {}),
    ...(poses && asset.variantOf ? { formerRecordId: asset.id } : {}),
    file: asset.file, label: asset.versionLabel, alt: title + ' · ' + asset.versionLabel,
    sourceId: 'guide', sourcePage: page, caption: asset.sourceLocator, darkBackground: asset.darkBackground,
    date: asset.sourceDate, dateLabel: 'Guide edition', evidenceType: asset.evidenceType, sha256: asset.sha256
  }))
  return { id, key, title, kind: poses ? 'mascot' : 'visual-identity', description: notes, artworkStatus: 'native-vector-held', images,
    sourceRefs: poses ? [ref('guide', page), ref('guide', 14), ref('ember', 1)] : [ref('guide', page)],
    ...(poses ? { artworkNote: '4 published poses', links: [
      { label: 'Ember in print and online', url: '?view=initiatives&initiative=firesmart-bc&section=standards&record=mascot-use' }
    ] } : {}) }
})

const item = (id, title, description, sourceRefs, kind) => ({ id, title, description, sourceRefs, kind })
const activity = {
  'wildfire-mitigation': item('home-assessments', 'From assessment to certification', 'A Wildfire Mitigation Specialist visits a property and gives its resident a report on the home and its surroundings. Residents can use the recommendations to make changes and seek reassessment for certification. Local governments and Indigenous communities help deliver the program.', [ref('wmp'), ref('report25', 10)], 'home-assessment'),
  'local-collective': item('collective-action', 'How a collective earns recognition', 'A Collective Advocate and Local FireSmart Representative assess their shared area, prepare an action plan and renew participation annually. The four levels are Participating, Bronze, Silver and Gold. FireSmart BC delivers the program with BCAA.', [ref('lfcp'), ref('collective-process')], 'community-recognition'),
  'plant-program': item('plant-partners', 'What the tag tells a gardener', 'At a participating garden centre, a FireSmart tag identifies a plant selected for its fire-resistant characteristics. The program’s planting guidance also covers placement and upkeep. Even a tagged plant can burn.', [ref('plant'), ref('plant-history')], 'retail-program'),
  'training-summit': item('conference-and-field-training', 'A conference and a training ground', 'The 2023 summit joined three days of talks and workshops with two days of operational training. It hosted the first Lynn Orstad Award for women in wildfire resilience and an Indigenous Wildland Firefighter Honour Ceremony. FireSmart BC recorded 750 participants at the 2025 gathering.', [ref('summit23'), ref('report23', 13), ref('report25', 8)], 'annual-event'),
  education: item('classroom-lessons', 'Lessons from kindergarten to Grade 12', 'Teachers can choose resources by grade band, see how the lessons fit the B.C. curriculum and arrange a school visit. The spring classroom contest invites students to share what they learned.', [ref('education'), ref('report23', 11)], 'school-program'),
  'farm-and-ranch': item('farm-assessment', 'Planning around working farm buildings', 'The agricultural assessment covers structures such as barns. Farmers can also prepare an operations map and use the Farm & Ranch Wildfire Plan guide and workbook. Residential buildings use the home assessment process.', [ref('farm'), ref('farm-form', 1)], 'agricultural-program'),
  library: item('readers-kit', 'Stories, reading lists and activities', 'The Library Program offers a literacy kit for children. Its catalogue gives librarians the books’ authors, reading ages and publication details, with links to readings where available.', [ref('library'), ref('readers-kit', 1)], 'literacy-program')
}

const relatedWork = [
  item('seven-disciplines', 'The seven FireSmart disciplines', 'Education, legislation and planning, emergency planning, vegetation management, development considerations, training and interagency cooperation organize work across the program. The earlier guide gives each discipline its own icon and colour.', [ref('programs'), ref('early-guide', 8), ref('early-guide', 9)], 'program-framework'),
  item('committee-and-network', 'The committee and the people who deliver the work', 'The BC FireSmart Committee directs the provincial program. Its partners include BC Wildfire Service, FireSmart Canada, the First Nations’ Emergency Services Society and the Union of BC Municipalities. Coordinators organize local delivery, representatives support neighbourhoods and specialists carry out property assessments.', [ref('who'), ref('network'), ref('report25', 3)], 'governance-and-training'),
  item('professional-network', 'FireSmart Professional Network and representative training', 'Local FireSmart Representatives take FireSmart 101 before their workshop. The network also supports coordinators and Wildfire Mitigation Specialists. FireSmart BC introduced a monthly representative spotlight in 2023 and held quarterly webinars on funding and provincial programs.', [ref('representatives'), ref('report23', 10), ref('report23', 12)], 'professional-development'),
  item('community-collaboratives', 'Community FireSmart and Resiliency Collaboratives', 'These local and regional forums bring fire departments, First Nations, local governments and other agencies together to coordinate plans. A Local FireSmart Collective is a separate form of participation through which residents and organizations earn recognition for shared work.', [ref('cfrc'), ref('lfcp')], 'local-planning'),
  item('community-funding', 'FireSmart Community Funding & Supports', 'Through Community Resiliency Investment, the Province funds eligible work by local governments and First Nations. UBCM, FNESS and the Forest Enhancement Society of BC worked with the BC Wildfire Service to administer the funding stream.', [ref('funding', 1)], 'provincial-funding'),
  item('cultural-sites', 'Culturally Significant Sites and Green Spaces', 'A dedicated guide extends assessment and mitigation planning to places such as ceremonial sites and community green spaces. First Nations can withhold sensitive site information when reporting activities.', [ref('cultural', 2), ref('cultural', 15)], 'assessment-guide'),
  item('research', 'FireSmart research projects', 'The Research Corner records public-opinion studies, the Northwest Territories Structure Ignition Project and the Wildfire Ember Simulator developed with the University of Victoria, Camosun College and the BC Wildfire Service. The 2025 report documents prototype testing.', [ref('research'), ref('report25', 8)], 'research'),
  item('preparedness-day', 'Wildfire Community Preparedness Day', 'FireSmart BC promotes this annual day of local action. Its account of Sooke describes a fire department bringing residents together to learn about preparedness.', [ref('prep-day')], 'community-event'),
  item('campaigns', 'Public awareness campaigns', 'Everyday Chores Make Everyday Heroes appeared on television, billboards and digital media in 2023. The 2025 campaign was We’re Ready. The 2026 summer campaign invited residents to See Through FireSmart Eyes.', [ref('report23', 14), ref('campaign25', 1), ref('campaign26')], 'campaigns'),
  item('media', 'FireSmart BC Magazine and The Get FireSmart Podcast', 'The magazine began in 2020. The podcast brings practitioners and researchers into conversations about wildfire and community preparedness.', [ref('review-2020'), ref('podcast')], 'publications-and-audio')
]

const pageImage = (page, alt) => ({
  file: `initiatives/firesmart-bc/guide-page-${page}.webp`, alt,
  caption: `FireSmart BC Brand Guidelines, PDF page ${page}.`, sourceId: 'guide', sourcePage: page,
  evidenceType: 'published-page-render', date: '2025-07', dateLabel: 'Guide edition', downloadLabel: 'guide page image'
})
const guideItem = (id, title, description, pages, imagePage) => ({
  ...item(id, title, description, pages.map((page) => ref('guide', page)), 'brand-guidelines'),
  ...(imagePage ? { image: pageImage(imagePage, title + ' as shown in the brand guide') } : {})
})
const localGuide = (import.meta.env?.BASE_URL ?? '/') + 'initiatives/firesmart-bc/brand-guidelines.pdf'
const standards = [
  { ...guideItem('full-guide', 'FireSmart BC Brand Guidelines', 'The 24-page July 2025 edition covers the provincial signature, colours, typography, Ember and four sub-brands. An earlier edition has a January 2022 cover and June 2021 footers. Its clear-space diagram measures the flame height. The July 2025 guide uses the height of the lowercase e.', [2, 4, 16]),
    sourceRefs: [ref('guide', 2), ref('guide', 4), ref('early-guide', 1), ref('early-guide', 2)],
    links: [{ label: 'Open the complete July 2025 guide (PDF)', url: localGuide }] },
  guideItem('signature-use', 'Clear space, colourways and trademark', 'The guide measures a margin on all sides using the e in FireSmart. It shows colour-positive and colour-reverse signatures and specifies black and white options for monochrome reproduction. It calls for ™ on first mention and credits the FireSmart and Intelli-feu marks to the Canadian Interagency Forest Fire Centre.', [4, 5, 6]),
  guideItem('colour-and-type', 'The four colours and two type weights', 'Charcoal (#212A34) is used for text and dark fields. Yellow (#EFCB17) highlights actions. Blue/Gray (#DFE3EC) sets off white panels, and Off-White (#F8FAFE) supplies the page background. Headings use Neuzeit Grotesk Bold and body text uses Regular, with Arial Bold and Regular as alternatives.', [8, 9, 11], 9),
  guideItem('mascot-use', 'Ember in print and online', 'The guide shows two head-and-shoulders profiles and two full-body poses. Its examples include an illustrated colouring book, a brochure and a web page. It identifies FireSmart BC as the reviewer for materials using Ember.', [13, 14], 14),
  guideItem('mitigation-use', 'Wildfire Mitigation Program colours and website', 'Charcoal (#212A34) and WMP Red (#E83E25) distinguish the property assessment program. The website example places its reverse signature over a photograph.', [17, 18], 18),
  guideItem('collective-use', 'Local FireSmart Collective Program colours', 'The circular group of houses uses LFCP Dark Blue (#1E5093) and LFCP Light Blue (#57B3E5). The guide pairs these colours with Charcoal (#212A34) and shows both light- and dark-ground signatures.', [19]),
  guideItem('plant-use', 'Plant Program colours and nursery signs', 'Plant Green (#43B649) identifies the shield and retail materials. Page 20 labels the companion swatch FireSmart Purple and prints #212A34, the value given elsewhere for Charcoal. The dark specimen panel itself appears purple. Page 21 shows the identity on plant tags and signs in a nursery.', [20, 21], 21),
  guideItem('summit-use', 'Summit colours and event materials', 'WRTS Yellow (#EFCB17) and WRTS Orange (#F47521) appear in the house-and-flame mark. As on the Plant Program page, the purple swatch carries the printed value #212A34. A sponsorship sheet, an invitation and an event program show the mark in use.', [22, 23], 23)
]
const programGuide = {
  'wildfire-mitigation': 'mitigation-use', 'local-collective': 'collective-use',
  'plant-program': 'plant-use', 'training-summit': 'summit-use'
}
const coverSources = { education: 'education', 'farm-and-ranch': 'farm-form', library: 'readers-kit' }

export function fireSmartDetail(entry) {
  const parent = entry.id === fireSmartParent.id
  const records = parent ? marks : marks.filter((mark) => mark.key === entry.key)
  const guideRecords = parent ? standards : standards.filter((record) => record.id === programGuide[entry.key])
  const history = parent ? timeline : timeline.filter((record) => record.program === entry.key)
  const program = activity[entry.key]
  const coverSource = coverSources[entry.key]
  const sections = []
  if (program) sections.push({
    id: 'program', label: 'Program', type: 'publications', title: entry.title,
    records: [{ ...program, ...(coverSource ? { image: {
      ...entry.cover, sourceId: coverSource, ...(entry.key === 'education'
        ? { evidenceType: 'official-published-website-image', sourceImageUrl: site + 'wp-content/uploads/2023/02/educationbanner-revised3.jpg' }
        : { sourcePage: 1, evidenceType: 'published-page-render' }) } } : {}) }]
  })
  if (records.length) sections.push({ id: 'marks', label: parent ? 'Logos & Ember' : 'Logo', type: 'records',
    layout: 'marks', title: parent ? 'The provincial signature, sub-brands and mascot' : entry.title + ' identity',
    description: 'Select a specimen to view its source page and download the published artwork.',
    records })
  sections.push({ id: 'timeline', label: 'History', type: 'timeline', title: 'Program history', records: history })
  if (guideRecords.length) sections.push({ id: 'standards', label: 'Brand guide', type: 'publications', title: 'The July 2025 brand guidelines', records: guideRecords })
  if (parent) sections.push({ id: 'related-work', label: 'Connected work', type: 'publications', title: 'Funding, community projects and public outreach', records: relatedWork })
  const usedSources = new Set(sections.flatMap(({ records }) => records.flatMap((record) => [
    ...record.sourceRefs.map(({ sourceId }) => sourceId), ...(record.image ? [record.image.sourceId] : [])
  ])))
  const library = parent ? sources : sources.filter(({ id }) => usedSources.has(id))
  return {
    id: entry.id, title: entry.title, sources: library,
    hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
    sections: [...sections, { id: 'sources', label: 'Sources', type: 'sources', records: library }],
    relatedLinks: [
      { label: 'FireSmart BC logos', to: { view: 'gallery', logos: 'specimens-firesmart-bc', ...(programGuide[entry.key] ? { mark: 'firesmart-bc-' + entry.key } : {}) } },
      ...(parent ? [{ label: 'BC Wildfire Service', to: { view: 'government', node: 'sub-bc-wildfire-service' } }] : [])
    ]
  }
}
