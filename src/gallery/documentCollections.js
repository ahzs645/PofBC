import { documentSpecimens, reports } from './documentSpecimens.js'

const source = (title, url) => ({ title, url })
const publication = (key) => source(reports[key].title, reports[key].sourcePage)
const related = (subject, label, type = 'related-to') => ({ subject, label, type })
const gallery = (label, logos) => ({ label, to: { view: 'gallery', logos } })
const injuryUnit = 'bc-injury-research-and-prevention-unit'
const headline = (key, title) => source(title, 'https://www.injuryresearch.bc.ca/' + key)

const records = [
  {
    id: 'leading-edge-bc', name: 'Leading Edge British Columbia', kind: 'nonprofit-society', shelf: 'partners',
    family: 'innovation-training', aliases: ['Leading Edge BC', 'Market Technology Society'], current: false, from: 2003,
    notes: 'Incorporated on July 15, 2003 as the Market Technology Society, Leading Edge BC marketed the province’s technology industries. The Province announced its launch on December 9. The BC Innovation Council contributed $10,000 to its B.C. Capital Study in 2004/05. Provincial funding ended in 2006. The society’s legal dissolution date is still open.',
    sources: [publication('leading'), source('Province announces the industry partnership', 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2003OTP0111-001082.htm'),
      source('Ministry records the transfer of technology marketing responsibilities', 'https://www.bcbudget.gov.bc.ca/annual_reports/2003_2004/sbed/sbed_role.htm'),
      source('Research Money reports withdrawal of provincial funding, May 2006', 'https://dev.researchmoneyinc.com/article/leading-edge-bcs-funding-terminated-by-province')],
    fundingHistory: [{
      period: '2004/05', role: 'Project contribution', organizations: [gallery('BC Innovation Council', 'collected-bc-innovation-council')],
      note: 'The society’s financial statements record a $10,000 contribution to the B.C. Capital Study on library PDF page 35.', source: publication('leading')
    }],
    relations: [related('bc-innovation-council', 'Contributed to the B.C. Capital Study in 2004/05')],
    nextAction: 'Locate the launch identity kit and the society’s dissolution record.', cover: 'leading-edge-2005', assets: documentSpecimens.leading
  }, {
    id: 'islands-trust', name: 'Islands Trust', kind: 'regional-government', shelf: 'bodies',
    family: 'regional-government', aliases: ['Islands Trust Council'], current: true, from: 1974,
    notes: 'Created in 1974 to preserve and protect the islands, the Trust is a federation of local trust committees and Bowen Island Municipality. Its Council approved a corporate-logo policy in 1999. The 2005/06 report prints its green landscape above the blue signature of the conservation fund.',
    sources: [publication('trust'), source('Islands Trust timeline', 'https://islandstrust.bc.ca/about-us/islands-trust-timeline/'),
      source('Islands Trust Policy 7.1.6, Corporate Logo', 'https://islandstrust.bc.ca/about-us/accountability/policies/'),
      source('September 2017 Trust Council agenda, visual identity and website changes', 'https://islandstrust.bc.ca/wp-content/uploads/2020/06/tc_2017-09-12_AGD_PKG.pdf')],
    relations: [related('municipality-bowen-island', 'Island municipality represented on Trust Council'), related('islands-trust-conservancy', 'Conservation arm of the federation')],
    nextAction: 'Locate the graphic standards and signed artwork behind the 1999 policy and 2017 changes.', assets: documentSpecimens.trust
  }, {
    id: 'islands-trust-conservancy', name: 'Islands Trust Conservancy', kind: 'independent-board', shelf: 'bodies',
    family: 'regional-government', aliases: ['Islands Trust Fund', 'Islands Trust Fund Board', 'Islands Trust Conservancy Board'], current: true, from: 1990,
    notes: 'Established in 1990, the Islands Trust Fund protected land through acquisitions and conservation covenants. Its blue 2005/06 signature echoes the Trust’s green landscape. The Fund and Board took the Conservancy name on May 31, 2018. By December 2018 a new signature with native plants appeared in committee papers. The Trust’s November 2019 open-house board supplies the native artwork.',
    sources: [publication('trust'), source('Islands Trust legal name change and agreements', 'https://islandstrust.bc.ca/about-us/accountability/agreements/'),
      publication('boards'), source('December 2018 committee papers with the Conservancy signature', 'https://islandstrust.bc.ca/wp-content/uploads/2020/06/ltc_2018-12-13_gm_agenda.pdf')],
    relations: [related('islands-trust', 'Conservation arm of the Islands Trust federation', 'part-of')],
    nextAction: 'Locate the design commission and an original dated launch file for the Conservancy identity.', cover: 'conservancy-landscape-2019', assets: documentSpecimens.fund
  }, {
    id: 'bc-ground-water-association', name: 'British Columbia Ground Water Association', kind: 'professional-association', shelf: 'partners',
    family: 'affiliated-organizations', aliases: ['BCGWA', 'British Columbia Water Well Drillers’ Association'], current: true, yearsLabel: 'Founded in 1970 or 1971',
    notes: 'The association traces its origins to the British Columbia Water Well Drillers’ Association. Its 2017 letter gives 1970. Its general manager’s 2022 presentation gives 1971 and dates its work on the first provincial well record form to 1972. It co-published the Well Protection Toolkit with the Province and Environment Canada in 2000. The December 2005 Pumphandle example puts their three signatures together. In 2015 it worked with the Province on certification for well drillers and pump installers.',
    sources: [publication('well'), source('Association account of its history and provincial work', 'https://www.bcgwa.org/wp-content/uploads/BCGWA_Artesian_wells_FINAL_-_22Feb2017.pdf'),
      source('Provincial design guidelines, section 4.3.11 on the toolkit', 'https://www2.gov.bc.ca/assets/gov/environment/air-land-water/water/water-licensing-and-rights/water-utilities/design_guidelines_rural_residential_water_mar2012.pdf'),
      source('General manager’s October 2022 presentation, page 5', 'https://www.bcgwa.org/wp-content/uploads/BCGWA_Overview_2022-PG_PDF-version.pdf'),
      source('Association website and current identity', 'https://www.bcgwa.org/')],
    fundingHistory: [{
      period: '2000–2005', role: 'Joint publication', organizations: [{ label: 'Province of British Columbia' }, { label: 'Environment Canada' }],
      note: 'The provincial guidelines identify the three toolkit publishers. All three signatures appear together on the Pumphandle example.',
      source: publication('well')
    }],
    relations: [related('industry-training-authority', 'Partner on 2015 certification for well drillers and pump installers')], nextAction: 'Locate the incorporation record, date the change of name and establish the first use of the current colour signature.', cover: 'bcgwa-website', assets: documentSpecimens.water
  }, {
    id: 'fish-wildlife-compensation-program', name: 'Fish & Wildlife Compensation Program', kind: 'service-brand', shelf: 'initiatives',
    family: 'hydro', aliases: ['FWCP', 'Columbia Basin Fish & Wildlife Compensation Program', 'Peace/Williston Fish & Wildlife Compensation Program'], current: true, from: 1988,
    notes: 'BC Hydro funds compensation work in watersheds affected by its dams. The governance manual dates the Peace program to 1988 and Columbia to 1993. Columbia’s own anniversary badge counts from 1995. The reports identify the Province, Fisheries and Oceans Canada, First Nations and the public as participants, with Columbia Basin Trust partnering on East Kootenay work. ' +
      'The program describes itself as a partnership of BC Hydro, the Province, Fisheries and Oceans Canada, First Nations and public interest holders, funded annually by BC Hydro: in the Columbia and Peace regions it is how BC Hydro meets its water licence conditions, and in the Coastal region BC Hydro’s contribution is voluntary. Its site names the Province’s ministry once, in 2019: the Ministry of Forests, Lands, Natural Resource Operations and Rural Development managed that year’s evaluation and financial audit. It names no later ministry.',
    sources: [publication('columbia'), publication('columbiaAnnual'), publication('peace'),
      source('Program governance manual, 2024', 'https://fwcp.ca/app/uploads/2024/04/FWCP-Governance-Manual-2024.pdf'),
      source('Peace/Williston wildlife report 40, early regional signature', 'https://a100.gov.bc.ca/pub/acat/documents/r40730/pwfwcp_report_no_040_1388807711941_8805259919.pdf'),
      source('FWCP, Our Story', 'https://fwcp.ca/our-story.html'),
      source('FWCP, Columbia Region', 'https://fwcp.ca/regions/columbia.html'),
      source('FWCP, Evaluation & Financial Audit 2019', 'https://fwcp.ca/our-story/evaluation---financial-audit---2019.html')],
    fundingHistory: [{
      period: 'Annually', role: 'Funder', organizations: [gallery('BC Hydro', 'bc-hydro')],
      note: 'BC Hydro funds the program each year to meet its water licence conditions in the Columbia and Peace regions, and voluntarily in the Coastal region. Several Columbia contracts are administered by BC Hydro on the program’s behalf.',
      source: source('FWCP, Our Story', 'https://fwcp.ca/our-story.html')
    }, {
      period: '2019', role: 'Provincial partner', organizations: [{
        label: 'Ministry of Forests, Lands, Natural Resource Operations and Rural Development',
        to: { view: 'government', node: 'ministry-of-forests-lands-natural-resource-operations-and-rural-development-2017', year: 2019 }
      }],
      note: 'Named for the Province of B.C. as managing the 2019 evaluation and financial audit. Columbia projects are also delivered with the Province through a letter of agreement. No later ministry is named.',
      source: source('FWCP, Evaluation & Financial Audit 2019', 'https://fwcp.ca/our-story/evaluation---financial-audit---2019.html')
    }, {
      period: '2013/14', role: 'Regional project partner', organizations: [gallery('Columbia Basin Trust', 'collected-columbia-basin-trust')],
      note: 'Page 3 credits joint work in the East Kootenay. BC Hydro is the compensation program’s funder.', source: publication('columbiaAnnual')
    }],
    relations: [related('bc-hydro', 'Funds compensation for the effects of hydroelectric dams')],
    nextAction: 'Recover the early Peace/Williston regional signature and locate a dated Coast-region example.', cover: 'fwcp-peace-2015', assets: documentSpecimens.wildlife
  }, {
    id: injuryUnit, name: 'BC Injury Research and Prevention Unit', kind: 'health-agency', shelf: 'initiatives',
    family: 'specialist-health', aliases: ['BCIRPU'], current: true, from: 1997,
    notes: 'Established in August 1997, the unit opened in 1998. It belongs to the Evidence to Innovation theme at BC Children’s Hospital Research Institute. The Ministry of Health, PHSA and UBC Pediatrics are named partners. The October 11, 2023 symposium marked 25 years of work.',
    sources: [publication('injury'), headline('about', 'Unit history, partners and priorities'), headline('about/25-years-of-the-bcirpu', 'Anniversary timeline in five parts')],
    relations: [related('university-of-british-columbia', 'Academic partnership with UBC Pediatrics'), related('provincial-health-services-authority', 'Provincial health-system partner'),
      related('sub-bc-childrens-hospital', 'Based at BC Children’s Hospital Research Institute')],
    nextAction: 'Locate the unit’s earliest letterhead and date the introduction of the orange-and-blue signature.', cover: 'bcirpu-2024', assets: documentSpecimens.injury
  }
]

// The report’s resource panel credits five projects. Their own names and relationships keep
// a research team’s tool, a hospital program and a university partner from sharing one identity.
const resources = [
  {
    id: 'concussion-awareness-training-tool', name: 'Concussion Awareness Training Tool', aliases: ['CATT'], from: 2013, assets: documentSpecimens.catt,
    notes: 'BCIRPU launched the first CATT course for medical professionals in 2013. Its online courses now reach coaches, parents, educators, athletes and workers.',
    sources: [source('UBC Pediatrics on CATT and its relaunch', 'https://pediatrics.med.ubc.ca/2018/01/19/new-concussion-awareness-training-tool-website-catt-website-launched/')],
    relations: [related(injuryUnit, 'Developed by BCIRPU', 'service-of')]
  }, {
    id: 'prevent-shaken-baby-syndrome-bc', name: 'Prevent Shaken Baby Syndrome BC', aliases: ['PSBSBC'], from: 2009, assets: documentSpecimens.psbs,
    notes: 'This provincial BC Children’s Hospital program is based at BCIRPU. The hospital formed a steering committee in 2003. Provincial delivery of the Period of PURPLE Crying program began in 2009.',
    sources: [source('Program history and education resources', 'https://www.dontshake.ca/about?tab=about-tab2')],
    relations: [related(injuryUnit, 'Based at the injury research unit'), related('sub-bc-childrens-hospital', 'Provincial hospital program', 'service-of')]
  }, {
    id: 'active-safe-central', name: 'Active & Safe Central', aliases: ['Active and Safe Central'], from: 2018, assets: documentSpecimens.active,
    notes: 'BCIRPU and its sport and injury-prevention partners launched Active & Safe Central on May 10, 2018. The resource covers more than fifty sports and recreation activities.',
    sources: [source('Project team and partners', 'https://activesafe.ca/about/'), source('May 2018 launch announcement', 'https://www.bcchr.ca/news-events/new-website-helps-keep-active-kids-safe-from-common-sport-injuries/')],
    relations: [related(injuryUnit, 'Developed with sport and injury-prevention partners')]
  }, {
    id: 'cost-of-injury', name: 'Cost of Injury', aliases: ['Costofinjury.ca'], from: 2022, assets: documentSpecimens.cost,
    notes: 'BCIRPU announced the interactive tool on November 20, 2022. The team modelled it on the national report it developed with Parachute. The annual-report mark credits BCIRPU as presenter.',
    sources: [source('Cost of Injury data resource', 'https://costofinjury.ca/'), headline('news/new-website-outlines-financial-and-human-cost-of-injury-in-bc', 'BCIRPU announces the interactive tool')],
    relations: [related(injuryUnit, 'Credited presenter on the 2023/24 signature')]
  }, {
    id: 'outside-play', name: 'Outside Play', aliases: ['OutsidePlay.org'], from: 2017, assets: documentSpecimens.outside,
    notes: 'Mariana Brussoni’s UBC team launched the parent decision tool in 2017. BCIRPU’s 2023/24 annual report features the project among its injury-prevention resources.',
    sources: [source('UBC announces the decision tool', 'https://www.med.ubc.ca/news/tool-launched-to-help-parents-allow-risky-play/')],
    relations: [related('university-of-british-columbia', 'Developed by the UBC research team'), related(injuryUnit, 'Featured as a resource by BCIRPU')]
  }
]
const islands2050 = {
  id: 'islands-2050', name: 'Islands 2050', kind: 'service-brand', shelf: 'initiatives', family: 'regional-government',
  aliases: ['Islands 2050 Policy Statement Amendment Project'], from: 2019, current: true, assets: documentSpecimens.islands2050,
  notes: 'Islands Trust began public engagement on amendments to its Policy Statement in 2019. The first open-house boards carry a project signature and the tagline “The Future of the Trust Area.” The Trust reports further engagement in 2021, 2022 and 2025/26.',
  sources: [publication('boards'), source('Islands Trust project history and frequently asked questions', 'https://islandstrust.bc.ca/programs/islands-2050/islands-2050-frequently-asked-questions/')],
  relations: [related('islands-trust', 'Policy Statement review led by Islands Trust', 'service-of')],
  nextAction: 'Compare the later engagement materials for changes to the project identity.'
}
const all = [...records, islands2050, ...resources.map((resource) => ({
  ...resource, sources: [publication('injury'), ...resource.sources], current: true, shelf: 'initiatives', family: 'specialist-health', kind: 'service-brand',
  nextAction: 'Locate the original identity files and the earliest documented use of the signature.'
}))]

export const DOCUMENT_COLLECTIONS = all.map((record) => ({ ...record, graphNode: null, status: 'asset-collected' }))
export const DOCUMENT_SUBJECTS = all.map(({ id, name, kind, family, aliases, sources, relations, notes, nextAction }) => ({
  id, name, label: name, kind, family, graphNode: null, scope: 'institution', priority: 2, aliases, salaryEmployers: [],
  collectionIds: ['collected-' + id], sources, relations, note: notes, nextAction
}))
