// Periods describe the named body or the event indicated. They do not date its artwork.
export const COMMISSION_FAMILY = {
  id: 'commissions', label: 'Commissions',
  description: 'Selected B.C. public commissions, their mandates and where their work went. The register includes continuing regulators, former agencies and jointly established bodies.'
}

export const COMMISSION_DIRECTORIES = [
  { title: 'B.C. Directory of Organizations', note: 'Current public appointments, mandates and board structures. The directory also covers boards and tribunals.', url: 'https://www.bcpublicsectorboardapplications.gov.bc.ca/s/directoryofagencies' },
  { title: 'Legislative Library’s royal and special commissions', note: 'Search inquiry reports from 1872 onward, with chronological checklists. Some early reports are missing and inquiries that ended without a report are omitted.', url: 'https://www.leg.bc.ca/learn/legislative-library/library-publications/library-royal-commissions' },
  { title: 'BC Archives government records', note: 'Find the records and administrative histories of former agencies under their names at the time.', url: 'https://bcarchives.ca/government-records/' }
]

const source = (title, url) => ({ title, url })
const laws = (title, id) => source(title, 'https://www.bclaws.gov.bc.ca/civix/document/id/' + id)
const libraryHistory = source('University of Victoria, history of the Public Library Commission', 'https://curric.library.uvic.ca/homeroom/content/topics/programs/plc.htm')
const humanRights = source('Courthouse Libraries BC, history of human rights decisions', 'https://www.courthouselibrary.ca/how-we-can-help/our-legal-knowledge-base/human-rights-decisions-bc')
const utilities = laws('Utilities Commission Act, 1980, including transitional provisions', '92consol16/92consol16/80060')
const energyHistory = source('Province of B.C., history of industrial electricity policy', 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/electricity-alternative-energy/electricity/iepr/ministry_discussion_paper_iepr.pdf')
const landHistory = source('Agricultural Land Commission, legislative chronology', 'https://www.alc.gov.bc.ca/assets/alc/assets/library/archived-publications/legislation-history/agricultural_land_commission_act_1973_to_2000.pdf')
const capitalReport = source('Provincial Capital Commission, final annual report', 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2013_2014/pdf/agency/pcc.pdf')

// graphYear selects an atlas snapshot. A record with atlas: false has no matching atlas node.
export const COMMISSION_HISTORIES = [
  {
    id: 'alcohol-and-drug-commission', name: 'Alcohol and Drug Commission of British Columbia', period: '1973–1983',
    history: 'The 1973 Act created a provincial Crown agent. Sections 2, 4, 10 and 11 of the 1979 revision continued the corporation with at least three appointed members, authorized treatment and education programs, and required annual reports to the minister.',
    outcome: 'Ministry of Health, Alcohol and Drug Programs. On October 3, 1983, the Health Minister said the ministry had integrated the program over the preceding two years and absorbed the staff. The Commission had been advising the program director. Repeal took effect October 26, 1983.',
    later: 'In 1996/97, Alcohol and Drug Services moved from Health to the Ministry for Children and Families. The programs subsequently returned to Health Services. In April 2002 the Province transferred responsibility for adult alcohol and drug services to regional health authorities.',
    sources: [laws('1973 founding Act', 'hstats/hstats/408463782'), laws('1979 revised Act, chapter 13 (supplied PDF)', 'hstats/hstats/333133237'), source('Hansard, October 3, 1983, pp. 2307–08', 'https://lims.leg.bc.ca/hdms/file/Debates/33rd1st/33p_01s_831003p.htm#02307'), laws('1983 repeal Act', 'hstats/hstats/577115892'), laws('BC Laws table of repeals, A', 'tos/tos/973948705'), source('Province, 1997 Financial and Economic Review', 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/financial-economic-review/financial-economic-review-1997.pdf'), source('Hansard, April 3, 2002, return to Health Services', 'https://lims.leg.bc.ca/hdms/file/Debates/37th3rd/20020403pm-Hansard-v5n6.htm'), source('Supreme Court of Canada, 2011 SCC 44, para. 14', 'https://bccla.org/wp-content/uploads/2012/03/20110930-Supreme-Court-Ruling-PHS.pdf')]
  },
  {
    id: 'agricultural-land-commission', name: 'Provincial Agricultural Land Commission', period: '1977 amendment, 1978 consolidation',
    history: 'The 1977 amendments changed the Commission’s name. The January 1978 consolidation carried the Agricultural Land Commission Act title.', outcome: 'Continues to administer the Agricultural Land Reserve.', sources: [landHistory, source('Agricultural Land Commission', 'https://www.alc.gov.bc.ca/')]
  },
  {
    id: 'bc-energy-commission', name: 'British Columbia Energy Commission', period: '1973–1980', graphYear: 1979, kind: 'independent-regulator',
    history: 'Took over energy regulation from the Public Utilities Commission in 1973.', outcome: 'The British Columbia Utilities Commission replaced it in 1980.', next: 'bc-utilities-commission', sources: [energyHistory, utilities]
  },
  {
    id: 'sub-bc-ferry-commission', name: 'British Columbia Ferry Commission', period: 'Since 2003',
    history: 'The Coastal Ferry Act introduced independent oversight of coastal ferry services in 2003.', outcome: 'Continues to set fare price caps and review major capital spending. BC Ferries operates the service.', sources: [source('BC Ferry Commission, mandate and history', 'https://www.bcferrycommission.ca/about/')]
  },
  {
    id: 'bc-film-commission', name: 'BC Film Commission', period: '1978–2013',
    history: 'The Province established a film office in 1978 to attract and support productions.', outcome: 'Its work and BC Film + Media came together in Creative BC in 2013. Creative BC continues to provide provincial film commission services.', next: 'creative-bc', sources: [source('Creative BC, motion picture history', 'https://creativebc.com/sector/motion-picture/')]
  },
  {
    id: 'bc-housing', name: 'British Columbia Housing Management Commission', period: 'Since 1967',
    history: 'The Province established the commission in 1967 to develop, administer and manage social housing.', outcome: 'Continues under the public name BC Housing.', sources: [source('BC Housing, 2024/25 annual service plan report', 'https://www.bchousing.org/sites/default/files/media/documents/Annual-Service-Plan-Report-2024-2025.pdf')]
  },
  {
    id: 'bc-human-rights-commission', name: 'British Columbia Human Rights Commission', period: '1997–2003', graphYear: 2002,
    history: 'This commission received and investigated complaints alongside a separate Human Rights Tribunal.', outcome: 'When the Commission closed in 2003, people began filing complaints directly with the existing BC Human Rights Tribunal.', sources: [source('BC Human Rights Tribunal, 2003–04 annual report', 'https://www.bchrt.bc.ca/app/uploads/sites/876/2023/03/2003-2004.pdf')]
  },
  {
    id: 'bc-power-commission', name: 'British Columbia Power Commission', period: '1945–1965',
    history: 'Brought electricity to communities outside BC Electric’s service area. The two systems began operating under the BC Hydro name in 1962.', outcome: 'The statutory amalgamation with the reconstituted BC Hydro and Power Authority took effect August 20, 1965.', next: 'bc-hydro', sources: [source('Supreme Court of Canada, case 29971, amalgamation agreement', 'https://www.scc-csc.gc.ca/cases-dossiers/search-recherche/29971/')]
  },
  {
    id: 'bc-securities-commission', name: 'British Columbia Securities Commission', period: 'Crown corporation since 1995',
    history: 'April 1, 1995 marks the creation of the present Crown corporation.', outcome: 'Continues to regulate B.C. capital markets under the Securities Act.', sources: [source('BC Securities Commission, annual service plan report', 'https://www.bcsc.bc.ca/-/media/PWS/New-Resources/About/Reports-and-Publications/BCSC-2023-2024-Annual-Service-Plan-Report.pdf')]
  },
  {
    id: 'bc-treaty-commission', name: 'British Columbia Treaty Commission', period: 'Since 1992',
    history: 'The First Nations Summit, Canada and British Columbia established this independent body together in 1992.', outcome: 'Continues to facilitate treaty negotiations among the parties.', sources: [source('BC Treaty Commission, Info Source', 'https://bctreaty.ca/info-source/')]
  },
  {
    id: 'bc-utilities-commission', name: 'British Columbia Utilities Commission', period: 'Since 1980', kind: 'independent-regulator',
    history: 'The Utilities Commission Act established the regulator in 1980 following the BC Energy Commission.', outcome: 'Continues to regulate energy utilities and other activities assigned by provincial legislation.', sources: [energyHistory, utilities]
  },
  {
    id: 'capital-improvement-district-commission', name: 'Capital Improvement District Commission', period: '1956–1977', graphYear: 1976,
    history: 'Funded improvements and beautification in the Victoria capital region.', outcome: 'Became the Provincial Capital Commission in 1977.', next: 'provincial-capital-commission', sources: [capitalReport, laws('BC Laws table of renamed statutes, C', 'tos/tos/1894637811')]
  },
  {
    id: 'childrens-commission', name: 'Children’s Commission', period: '1997–2002', atlas: false,
    history: 'Reviewed services and deaths involving children. Its enabling statute was repealed in 2002.', outcome: 'The Office for Children and Youth took on advocacy and service monitoring. Responsibility for child death review went to the BC Coroners Service.', sources: [laws('BC Laws table of replaced statutes, C', 'tos/tos/1894637811'), source('BC Coroners Service, Child Death Review Unit annual report', 'https://www2.gov.bc.ca/assets/gov/birth-adoption-death-marriage-and-divorce/deaths/coroners-service/child-death-review-unit/reports-publications/archive/2007-annual-report.pdf')]
  },
  {
    id: 'civil-service-commission', name: 'Civil Service Commission', period: '1917–1973', graphYear: 1972,
    history: 'Administered recruitment and promotion examinations for the provincial civil service.', outcome: 'The 1973 Public Service Act established the Public Service Commission and repealed the Civil Service Act.', sources: [laws('Civil Service Act, 1917', 'hstats/hstats/1337869437'), laws('Public Service Act, 1973, section 3 and repeal provision', 'hstats/hstats/1877354426')]
  },
  {
    id: 'electoral-boundaries-commission', name: 'Electoral Boundaries Commission', period: 'Periodic appointments', atlas: false,
    history: 'An independent commission is appointed after every second provincial general election to review electoral districts.', outcome: 'Each commission reports to the Legislative Assembly. The 2023 commission tabled its final report on April 3. The Assembly passed legislation establishing new boundaries in May.', sources: [source('Elections BC, Electoral Boundaries Commission and reports', 'https://www3.elections.bc.ca/resources/maps/electoral-boundaries-commission/')]
  },
  {
    id: 'emergency-health-services-commission', name: 'Emergency Health Services Commission', period: '1974–2013',
    history: 'Established in 1974 to organize provincial ambulance and emergency services. Its financial operations transferred to the Provincial Health Services Authority in 2011.', outcome: 'On April 1, 2013 it became British Columbia Emergency Health Services under PHSA. BC Ambulance Service continued as the ambulance service.', next: 'bc-emergency-health-services', sources: [source('BC Ambulance Service, provincial history', 'https://www.bcehs.ca/about/who-we-are/bc-ambulance-service'), source('PHSA, BC Emergency Health Services financial statements, note 1', 'https://www.phsa.ca/about-site/Documents/BC%20Emergency%20Health%20Services.pdf')]
  },
  {
    id: 'financial-institutions-commission', name: 'Financial Institutions Commission', period: '1989–2019', graphYear: 2018, kind: 'independent-regulator',
    history: 'FICOM regulated provincial financial institutions and other financial services.', outcome: 'The BC Financial Services Authority assumed FICOM’s regulatory responsibilities in November 2019.', next: 'bc-financial-services-authority', sources: [source('BC Financial Services Authority, history', 'https://www.bcfsa.ca/about-us/what-we-do/history')]
  },
  {
    id: 'sub-forest-appeals-commission', name: 'Forest Appeals Commission', period: 'Since 1995', kind: 'tribunal',
    history: 'Established in 1995 to hear appeals of provincial forestry decisions.', outcome: 'Continues as an independent appeal tribunal under the Forest and Range Practices Act.', sources: [source('Forest Appeals Commission, annual report', 'https://www.bcfac.ca/app/uploads/sites/837/2020/07/fac_ar01.pdf'), source('Forest Appeals Commission', 'https://www.bcfac.ca/')]
  },
  {
    id: 'game-commission', name: 'Game Commission', period: '1934–1957', graphYear: 1956,
    history: 'Succeeded the Provincial Game Commissioner in the administration of game laws.', outcome: 'In 1957 the provincial Game Department moved from the Attorney General to Recreation and Conservation as the Fish and Game Branch.', sources: [source('Conservation Officer Service, Game Department 1929–1957', 'https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/conservation-officer-service/game-department-1929-1957.pdf')]
  },
  {
    id: 'bc-hog-marketing-commission', name: 'British Columbia Hog Marketing Commission', period: '1980 marketing scheme', atlas: false,
    history: 'The 1980 provincial hog marketing scheme provided for this producer marketing commission.', outcome: 'Continues to exercise the powers assigned under the British Columbia Hog Marketing Scheme.', sources: [laws('British Columbia Hog Marketing Scheme, sections 4–6', 'complete/statreg/109_80')]
  },
  {
    id: 'human-rights-commission-1973', name: 'Human Rights Commission', period: '1973–1984', graphYear: 1983,
    history: 'The 1973 Human Rights Code established the first provincial commission of this name.', outcome: 'The BC Council of Human Rights replaced it in 1984. A later commission began in 1997.', next: 'bc-human-rights-commission', sources: [humanRights]
  },
  {
    id: 'industry-training-and-apprenticeship-commission', name: 'Industry Training and Apprenticeship Commission', period: 'Established 1997',
    history: 'Brought business, labour, education and government together to oversee apprenticeship and industry training.', outcome: 'The Industry Training Authority replaced ITAC in 2004. The authority subsequently became SkilledTradesBC in 2022.', next: 'industry-training-authority', sources: [source('Province, 1997 ITAC announcement', 'https://archive.news.gov.bc.ca/releases/archive/pre2001/1997/0614.asp'), source('Ministry service plan, 2023/24, p. 25', 'https://bcbudget.gov.bc.ca/2023/sp/pdf/ministry/psefs.pdf')]
  },
  {
    id: 'law-reform-commission', name: 'Law Reform Commission of British Columbia', period: '1969–1997', atlas: false,
    history: 'Created by statute in 1969, the Commission began work in 1970. Provincial program funding ended in March 1997.', outcome: 'The independent BC Law Institute took up law reform work and preserves the former Commission’s publications.', sources: [source('BC Law Institute, first annual report', 'https://www.bcli.org/sites/default/files/AR1998.pdf'), source('Courthouse Libraries BC, former Commission publications', 'https://www.courthouselibrary.ca/how-we-can-help/our-legal-knowledge-base/law-reform-commission-bc')]
  },
  {
    id: 'legal-services-commission', name: 'Legal Services Commission', period: '1975–1979', graphYear: 1978,
    history: 'Succeeded the Legal Services Division in 1975.', outcome: 'Merged with the Legal Aid Society of B.C. on October 1, 1979 to form the Legal Services Society, now known as Legal Aid BC.', next: 'legal-aid-bc', sources: [source('Legal Services Society, history of legal aid delivery', 'https://legalaid.bc.ca/sites/default/files/2019-03/pleReview_en.pdf'), source('Legal Aid BC, financial information and legal name', 'https://legalaid.bc.ca/sites/default/files/inline-files/Financial%20information%20statements%202024-LABC.pdf')]
  },
  {
    id: 'library-development-commission', name: 'Library Development Commission', period: '1968 legislation–1978', atlas: false,
    history: 'The 1968 amendment to the Public Libraries Act changed the name of the Public Library Commission.', outcome: 'Reorganized as the Library Services Branch in 1978.', sources: [libraryHistory]
  },
  {
    id: 'mediation-commission', name: 'Mediation Commission', period: '1968–1972', graphYear: 1971,
    history: 'Mediated provincial labour disputes under the Mediation Commission Act.', outcome: 'The Department of Labour’s Mediation Services Branch took over its functions in 1972.', sources: [source('Economic Council of Canada, history of labour regulation, p. 79', 'https://publications.gc.ca/collections/collection_2018/ecc/EC12-4-1981-19-eng.pdf'), source('Hansard, May 18, 1978, Mediation Services Branch', 'https://lims.leg.bc.ca/hdms/file/Debates/31st3rd/31p_03s_780518p.htm')]
  },
  {
    id: 'sub-medical-services-commission', name: 'Medical Services Commission', period: 'Since 1967', kind: 'independent-board',
    history: 'The 1967 Medical Services Act constituted the Commission. The provision establishing the Commission came into force on March 24, 1967, before the provincial Medical Services Plan began operating in 1968.', outcome: 'Continues to administer the Medical Services Plan under the Medicare Protection Act.', sources: [laws('Medical Services Act, 1967, section 3', 'hstats/hstats/30844302'), laws('Order in Council 964/1967', 'oic/arc_oic/0964_1967'), source('B.C. Ministry of Health, Medical Services Commission', 'https://www2.gov.bc.ca/gov/content/health/about-bc-s-health-care-system/partners/colleges-boards-and-commissions/medical-services-commission')]
  },
  {
    id: 'oil-and-gas-commission', name: 'BC Oil and Gas Commission', period: '1998–2023 under this name',
    history: 'Established in 1998 as the provincial oil and gas regulator.', outcome: 'Renamed the British Columbia Energy Regulator in 2023. Section 2 of the Energy Resource Activities Act continues the same corporation under its new name.', next: 'bc-energy-regulator', sources: [laws('Energy Resource Activities Act, section 2', 'complete/statreg/08036_01'), source('BC Energy Regulator, 2023 transition notice', 'https://www.bc-er.ca/news/transitioning-to-bc-energy-regulator-iu-2023-04/')]
  },
  {
    id: 'bc-police-commission', name: 'British Columbia Police Commission', period: 'Dissolved 1998', atlas: false,
    history: 'The Commission oversaw policing functions including complaints about municipal police.', outcome: 'The 1998 Police Act changes gave its complaints function to the Office of the Police Complaint Commissioner. The director of police services received separate statutory responsibilities.', next: 'police-complaint-commissioner', sources: [source('Province of B.C., policing history and oversight', 'https://www2.gov.bc.ca/assets/gov/law-crime-and-justice/about-bc-justice-system/inquiries/mmiw/bc-submission-app-g.pdf')]
  },
  {
    id: 'provincial-capital-commission', name: 'Provincial Capital Commission', period: '1977–2014', graphYear: 2013,
    history: 'Succeeded the Capital Improvement District Commission and managed capital-region heritage properties.', outcome: 'Dissolved March 25, 2014. Its assets, rights and obligations transferred to the provincial government.', sources: [capitalReport, laws('Provincial Capital Commission Dissolution Act, section 2', 'complete/statreg/00_14001_01')]
  },
  {
    id: 'provincial-land-commission', name: 'British Columbia Land Commission', period: 'Established 1973', graphYear: 1977,
    history: 'The Land Commission Act established the Commission and the Agricultural Land Reserve in 1973.', outcome: 'Became the Provincial Agricultural Land Commission under the 1977 amendments, reflected in the January 1978 consolidation.', next: 'agricultural-land-commission', sources: [landHistory]
  },
  {
    id: 'public-library-commission', name: 'Public Library Commission', period: 'Established 1919', graphYear: 1967,
    history: 'Supported public library associations and travelling libraries across B.C.', outcome: 'The 1968 legislation renamed it the Library Development Commission. Its work later moved into the Library Services Branch.', next: 'library-development-commission', sources: [libraryHistory]
  },
  {
    id: 'public-service-employee-relations-commission', name: 'Public Service Employee Relations Commission', period: 'Replaced 2003', atlas: false,
    history: 'Provided personnel and labour relations services for the provincial government.', outcome: 'The BC Public Service Agency replaced the Commission in April 2003.', sources: [source('BC Public Service Agency, first annual service plan report', 'https://www.bcbudget.gov.bc.ca/annual_reports/2003_2004/bcpsa/bcpsa_role.htm')]
  },
  {
    id: 'public-utilities-commission', name: 'Public Utilities Commission', period: '1938–1973', graphYear: 1972, kind: 'independent-regulator',
    history: 'Regulated utility rates and services under the Public Utilities Act.', outcome: 'Its energy functions passed to the BC Energy Commission in 1973, then to the BC Utilities Commission in 1980.', next: 'bc-energy-commission', sources: [energyHistory, utilities]
  },
  {
    id: 'bc-vegetable-marketing-commission', name: 'British Columbia Vegetable Marketing Commission', period: '1980 marketing scheme', atlas: false,
    history: 'The provincial vegetable marketing scheme established the Commission in 1980.', outcome: 'Continues to regulate the marketing of designated vegetables under that scheme.', sources: [laws('British Columbia Vegetable Scheme, section 3', 'complete/statreg/96_80')]
  }
]

export const commissionById = new Map(COMMISSION_HISTORIES.map((record) => [record.id, record]))
