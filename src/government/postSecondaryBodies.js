// The public universities, colleges and institutes whose audited statements the Province publishes but
// which had no site record (research/finance/public-accounts-23-1/README.md, "Built from this
// research"). UBC, SFU, UVic, UNBC and BCIT are in relatedBodies.js; JIBC is an atlas body.
//
// Each is a catalogue record, like the rest of relatedBodies.js. Its id is the identity register's
// subject id (research/identity/postsecondary-2026-11-24/source-register.json), so the record opens
// its gallery collection and register entry, and the collection's "Open in Government" opens it.
// Earlier names and predecessors stay register subjects (`lineage`); only bodies the site holds are
// connections. A date is given only where a cited instrument, statement or history page states it.

export const POST_SECONDARY_BODIES_CHECKED = '2026-11-27'

const source = (title, url) => ({ title, url })
const employer = (slug, label) => ({ slug, label })
const link = (id, label, description, extra = {}) => ({ id, label, description, ...extra })
/** An earlier name, a predecessor or a successor, by its identity register subject. */
const lineage = (subject, name, relation, period) => ({ subject, name, relation, ...(period ? { period } : {}) })

const ROSTER = source('Province of BC — Public post-secondary institutions', 'https://www2.gov.bc.ca/gov/content/education-training/post-secondary-education/find-a-program-or-institution/find-an-institution')
const BCNET_MEMBERS = source('BCNET — Current members', 'https://www.bc.net/our-members')
const OIC_421 = source('Order in Council 421/2026 — ministry reorganization and ministerial responsibilities (Appendix B)', 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/oic_cur/0421_2026')
const BCCAT = source('BCCAT — History of the B.C. post-secondary system', 'https://www.bccat.ca/system/history/')
const FS = 'https://www2.gov.bc.ca/assets/gov/education/post-secondary-education/institution-resources-administration/financial-reporting/audited-financial-statements/25-26/'
/** The institution's audited statements for 2025-26, from the ministry's page. */
const statements = (file, name) => source(`${name}, audited financial statements 2025-26`, FS + file)
const oic = (number, year, what) => source(`Order in Council ${number}/${year} — ${what}`, `https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/${String(number).padStart(4, '0')}_${year}`)
/** The 1978 order designating a college under the Colleges and Provincial Institutes Act, s. 6 (1); all were approved on 24 November 1978. */
const designation1978 = (number, name) => oic(number, 1978, `${name} designated under the Colleges and Provincial Institutes Act, approved 24 November 1978`)
const TEACHING_UNIVERSITIES = source('B.C. Regulation 220/2008 — Designation of Special Purpose, Teaching Universities Regulation (effective 1 September 2008)', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/220_2008')
const OIC_578 = oic(578, 2008, 'University Amendment Act, 2008 in force and B.C. Reg. 220/2008 made, effective 1 September 2008')
const TEACHING_NOTE = 'B.C. Regulation 220/2008, made by Order in Council 578/2008, designated it a special purpose teaching university under the University Act, effective 1 September 2008.'

const COLLEGE_ACT = { name: 'College and Institute Act', item: 68 }
const UNIVERSITY_ACT = { name: 'University Act', item: 628 }
const RRU_ACT = { name: 'Royal Roads University Act', item: 545 }
const TRU_ACT = { name: 'Thompson Rivers University Act', item: 607 }
const MINISTRY = 'ministry-of-post-secondary-education-and-labour-2026'

const KIND_WORDS = { 'public-college': 'public college', 'public-university': 'public university', 'public-institute': 'public institute' }

/** A record, with the connections every one of them has: its ministry and BCNET. */
const institution = ({ act, connections = [], salary, sources, ...body }) => ({
  ...body,
  act: act.name,
  salaryEmployers: salary ? [employer(salary, body.name)] : [],
  sources: [...sources, ROSTER, OIC_421, BCNET_MEMBERS],
  relationships: [
    link(MINISTRY, 'Ministry of Post-Secondary Education and Labour', `Its minister has been responsible for the ${act.name} since 20 November 2026 (Appendix B, item ${act.item})`, { year: 2026, mode: 'graph', source: OIC_421 }),
    link('bcnet', 'BCNET', 'Member institution', { source: BCNET_MEMBERS }),
    ...connections
  ],
  checked: POST_SECONDARY_BODIES_CHECKED
})

const describe = (kind, act, place) => `A ${KIND_WORDS[kind]} ${place}, governed by the ${act.name}. The Province includes its audited statements in the government reporting entity.`

export const POST_SECONDARY_RELATED_BODIES = [
  // ── Universities ────────────────────────────────────────────────────────────────────────────────
  institution({
    id: 'capilano-university', name: 'Capilano University', shortName: 'CapU', aliases: ['CapU', 'Capilano College'],
    kind: 'public-university', act: UNIVERSITY_ACT, officialUrl: 'https://www.capilanou.ca/',
    description: describe('public-university', UNIVERSITY_ACT, 'in North Vancouver'),
    historyNote: `Capilano College opened in 1968. Order in Council 2971/1978 designated it under the Colleges and Provincial Institutes Act, effective 1 December 1978. ${TEACHING_NOTE}`,
    lineage: [lineage('capilano-college', 'Capilano College', 'Earlier name', '1968–2008')],
    sources: [statements('capu_fs_2526_signed.pdf', 'Capilano University'), TEACHING_UNIVERSITIES, OIC_578, designation1978(2971, 'Capilano College'), BCCAT, source('Capilano University — Our history', 'https://www.capilanou.ca/about-capu/get-to-know-us/our-history/')],
    salary: 'capilano-university'
  }),
  institution({
    id: 'emily-carr-university', name: 'Emily Carr University of Art and Design', shortName: 'Emily Carr', aliases: ['ECU', 'ECUAD', 'Emily Carr University of Art + Design', 'Emily Carr Institute of Art and Design', 'Emily Carr College of Art'],
    kind: 'public-university', act: UNIVERSITY_ACT, officialUrl: 'https://www.ecuad.ca/',
    description: describe('public-university', UNIVERSITY_ACT, 'of art and design in Vancouver'),
    historyNote: `The Vancouver School of Art was part of Vancouver City College from 1965. Order in Council 169/1978, approved on 20 January 1978, designated the Vancouver School of Art of the Vancouver Community College a provincial institute named the Emily Carr College of Art. It later became the Emily Carr College of Art and Design. Order in Council 807/1994, approved on 16 June 1994, renamed it the Emily Carr Institute of Art and Design. ${TEACHING_NOTE}`,
    lineage: [
      lineage('vancouver-school-of-art', 'Vancouver School of Art', 'Predecessor', '1925–1978'),
      lineage('emily-carr-college-of-art', 'Emily Carr College of Art', 'Earlier name', 'from 20 January 1978'),
      lineage('emily-carr-college-of-art-and-design', 'Emily Carr College of Art and Design', 'Earlier name'),
      lineage('emily-carr-institute-of-art-and-design', 'Emily Carr Institute of Art and Design', 'Earlier name', '16 June 1994–1 September 2008')
    ],
    connections: [link('vancouver-community-college', 'Vancouver Community College', 'Its art school became the Emily Carr College of Art in 1978', { source: oic(169, 1978, 'Emily Carr College of Art designated a provincial institute, approved 20 January 1978') })],
    sources: [statements('ecuad_fs_2526_signed.pdf', 'Emily Carr University of Art and Design'), TEACHING_UNIVERSITIES, OIC_578, oic(169, 1978, 'Emily Carr College of Art designated a provincial institute, approved 20 January 1978'), oic(807, 1994, 'renamed the Emily Carr Institute of Art and Design, approved 16 June 1994'), source('Emily Carr University — Our history', 'https://ecuad.ca/our-history/')],
    salary: 'emily-carr-university'
  }),
  institution({
    id: 'kwantlen-polytechnic-university', name: 'Kwantlen Polytechnic University', shortName: 'KPU', aliases: ['KPU', 'Kwantlen University College', 'Kwantlen College'],
    kind: 'public-university', act: UNIVERSITY_ACT, officialUrl: 'https://www.kpu.ca/',
    description: describe('public-university', UNIVERSITY_ACT, 'in Surrey, Richmond and Langley'),
    historyNote: `Order in Council 626/1981 designated Kwantlen College, for the school districts south of the Fraser that Douglas College had served, effective 1 April 1981. Order in Council 126/1995, approved on 2 February 1995, designated it Kwantlen University College. ${TEACHING_NOTE}`,
    lineage: [
      lineage('kwantlen-college', 'Kwantlen College', 'Earlier name', '1 April 1981–1995'),
      lineage('kwantlen-university-college', 'Kwantlen University College', 'Earlier name', '1995–2008')
    ],
    connections: [link('douglas-college', 'Douglas College', 'Kwantlen College took over four of its school districts on 1 April 1981', { source: oic(626, 1981, 'Kwantlen College designated, effective 1 April 1981') })],
    sources: [statements('kpu_fs_2526_signed.pdf', 'Kwantlen Polytechnic University'), TEACHING_UNIVERSITIES, OIC_578, oic(626, 1981, 'Kwantlen College designated, effective 1 April 1981'), oic(126, 1995, 'Kwantlen University College designated, approved 2 February 1995'), BCCAT, source('KPU Library — Archives', 'https://libguides.kpu.ca/Archives/about')],
    salary: 'kwantlen-polytechnic-university'
  }),
  institution({
    id: 'royal-roads-university', name: 'Royal Roads University', shortName: 'Royal Roads', aliases: ['RRU'],
    kind: 'public-university', act: RRU_ACT, officialUrl: 'https://www.royalroads.ca/',
    description: describe('public-university', RRU_ACT, 'in Colwood, near Victoria'),
    historyNote: 'The Royal Roads University Act (S.B.C. 1995, c. 44) received Royal Assent on 29 June 1995. Order in Council 835/1995, approved on 13 July 1995, brought most of it into force. The university stands on the site of the federal Royal Roads Military College, which closed in 1995. It is a new provincial institution, not the military college renamed.',
    lineage: [lineage('royal-roads-military-college', 'Royal Roads Military College', 'Earlier institution on the site', 'to 1995')],
    sources: [statements('rru_fs_2526_signed.pdf', 'Royal Roads University'), source('Royal Roads University Act, RSBC 1996, c. 409', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96409_01'), source('Legislative Assembly — Progress of Bills, 35th Parliament, 4th session (Bill 49, Royal Assent 29 June 1995)', 'https://lims.leg.bc.ca/hdms/file/Index/35th4th/bills_prog.htm'), oic(835, 1995, 'Royal Roads University Act in force except sections 21 and 23, approved 13 July 1995'), source('Royal Roads University — Chapters of our history', 'https://www.royalroads.ca/about/history-traditions/chapters-our-history')],
    salary: 'royal-roads-university'
  }),
  institution({
    id: 'thompson-rivers-university', name: 'Thompson Rivers University', shortName: 'TRU', aliases: ['TRU', 'University College of the Cariboo', 'Cariboo College', 'TRU Open Learning'],
    kind: 'public-university', act: TRU_ACT, officialUrl: 'https://www.tru.ca/',
    description: describe('public-university', TRU_ACT, 'in Kamloops, with Open Learning across the province'),
    historyNote: 'Cariboo College opened in 1970. Order in Council 2959/1978 designated it under the Colleges and Provincial Institutes Act, effective 1 December 1978. It took the name University College of the Cariboo in 1991. The Thompson Rivers University Act received Royal Assent on 3 March 2005 and continued it as Thompson Rivers University. The Act came into force on 31 March 2005 (Order in Council 364/2005), and the transition took place on 1 April 2005. BC Open University’s operations moved to TRU then; the Open Learning Agency as a whole did not.',
    lineage: [
      lineage('cariboo-college', 'Cariboo College', 'Earlier name', '1970–1991'),
      lineage('university-college-of-the-cariboo', 'University College of the Cariboo', 'Earlier name', '1991–2005'),
      lineage('bc-open-university', 'British Columbia Open University', 'Operations transferred to TRU', '2005')
    ],
    connections: [link('open-learning-agency', 'Open Learning Agency', 'BC Open University’s operations moved to TRU in 2005', { year: 2005, mode: 'graph', source: source('Thompson Rivers University Act, section 2 (1) and section 11', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/05017_01') })],
    sources: [statements('tru_fs_2526_signed.pdf', 'Thompson Rivers University'), source('Thompson Rivers University Act, SBC 2005, c. 17', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/05017_01'), oic(364, 2005, 'Thompson Rivers University Act in force 31 March 2005'), designation1978(2959, 'Cariboo College'), source('TRU — The University College of the Cariboo and BC Open University become Thompson Rivers University', 'https://inside.tru.ca/2005/03/01/the-university-college-of-the-cariboo-and-bc-open-university-become-thompson-rivers-university/')],
    salary: 'thompson-rivers-university'
  }),
  institution({
    id: 'university-of-the-fraser-valley', name: 'University of the Fraser Valley', shortName: 'UFV', aliases: ['UFV', 'University College of the Fraser Valley', 'Fraser Valley College'],
    kind: 'public-university', act: UNIVERSITY_ACT, officialUrl: 'https://www.ufv.ca/',
    description: describe('public-university', UNIVERSITY_ACT, 'in Abbotsford and Chilliwack'),
    historyNote: `Fraser Valley College opened in 1974. Order in Council 2963/1978 designated it, effective 1 December 1978. UFV’s own account dates its university-college status to 1991; Order in Council 44/1995 designated it the University College of the Fraser Valley, effective 15 January 1995. ${TEACHING_NOTE}`,
    lineage: [
      lineage('fraser-valley-college', 'Fraser Valley College', 'Earlier name', 'from 1974'),
      lineage('university-college-of-the-fraser-valley', 'University College of the Fraser Valley', 'Earlier name', 'to 1 September 2008')
    ],
    sources: [statements('ufv_fs_2526_signed.pdf', 'University of the Fraser Valley'), TEACHING_UNIVERSITIES, OIC_578, designation1978(2963, 'Fraser Valley College'), oic(44, 1995, 'University College of the Fraser Valley designated, effective 15 January 1995'), BCCAT, source('UFV — Getting university-college status for Fraser Valley College', 'https://blogs.ufv.ca/blog/2011/12/rocky-road-getting-university-college-status-for-fraser-valley-college-was-no-easy-task/')],
    salary: 'university-of-the-fraser-valley'
  }),
  institution({
    id: 'vancouver-island-university', name: 'Vancouver Island University', shortName: 'VIU', aliases: ['VIU', 'Malaspina University-College', 'Malaspina College'],
    kind: 'public-university', act: UNIVERSITY_ACT, officialUrl: 'https://www.viu.ca/',
    description: describe('public-university', UNIVERSITY_ACT, 'in Nanaimo, with campuses on Vancouver Island'),
    historyNote: 'Malaspina College opened in 1969. Order in Council 2964/1978 designated it, effective 1 December 1978. It gained university-college status in 1989; Order in Council 45/1995 designated it Malaspina University-College, effective 15 January 1995. B.C. Regulation 220/2008 designated Malaspina University-College a special purpose teaching university named Vancouver Island University, effective 1 September 2008.',
    lineage: [
      lineage('malaspina-college', 'Malaspina College', 'Earlier name', 'from 1969'),
      lineage('malaspina-university-college', 'Malaspina University-College', 'Earlier name', 'to 1 September 2008')
    ],
    sources: [statements('viu_fs_2526_signed.pdf', 'Vancouver Island University'), TEACHING_UNIVERSITIES, OIC_578, designation1978(2964, 'Malaspina College'), oic(45, 1995, 'Malaspina University-College designated, effective 15 January 1995'), BCCAT],
    salary: 'vancouver-island-university'
  }),

  // ── Institute ───────────────────────────────────────────────────────────────────────────────────
  institution({
    id: 'nicola-valley-institute-of-technology', name: 'Nicola Valley Institute of Technology', shortName: 'NVIT', aliases: ['NVIT'],
    kind: 'public-institute', act: COLLEGE_ACT, officialUrl: 'https://www.nvit.ca/',
    description: `An Indigenous public post-secondary institute in Merritt, governed as a provincial institute under the ${COLLEGE_ACT.name}. The Province includes its audited statements in the government reporting entity.`,
    historyNote: 'Five Nicola Valley bands founded the institute in 1983. Order in Council 1069/1995, approved on 1 September 1995, designated it a provincial institute under the College and Institute Act.',
    sources: [statements('nvit_fs_2526_signed.pdf', 'Nicola Valley Institute of Technology'), oic(1069, 1995, 'Nicola Valley Institute of Technology designated a provincial institute, approved 1 September 1995'), source('NVIT — Notice of position, 2025 (founding and designation)', 'https://www.nvit.ca/wp-content/uploads/2025/11/Notice-of-Position-2025.pdf'), BCCAT]
  }),

  // ── Colleges ────────────────────────────────────────────────────────────────────────────────────
  institution({
    id: 'camosun-college', name: 'Camosun College', shortName: 'Camosun', aliases: ['Camosun'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://camosun.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Victoria'),
    historyNote: 'Camosun College opened on 7 September 1971. It brought together the Institute for Adult Studies, the B.C. Vocational School at Interurban and the Junction campus. Order in Council 2958/1978 designated it under the Colleges and Provincial Institutes Act.',
    lineage: [
      lineage('institute-for-adult-studies', 'Institute for Adult Studies', 'Predecessor', 'to 1971'),
      lineage('bc-vocational-school-interurban', 'British Columbia Vocational School — Interurban', 'Predecessor', 'to 1971'),
      lineage('junction-campus', 'Junction campus', 'Predecessor', 'to 1971')
    ],
    sources: [statements('cam_fs_2526_signed.pdf', 'Camosun College'), designation1978(2958, 'Camosun College'), source('Camosun College — Camosun College opens on September 7, 1971', 'https://50.camosun.ca/camosun-college-opens-on-september-7-1971/'), source('Camosun College — Timeline', 'https://50.camosun.ca/camosun-timeline/')],
    salary: 'camosun-college'
  }),
  institution({
    id: 'coast-mountain-college', name: 'Coast Mountain College', shortName: 'CMTN', aliases: ['CMTN', 'Northwest Community College', 'NWCC'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://www.coastmountaincollege.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in northwestern British Columbia, based in Terrace'),
    historyNote: 'Order in Council 2967/1978 designated Northwest Community College under the Colleges and Provincial Institutes Act. Order in Council 208/2018, approved on 23 April 2018, renamed it Coast Mountain College effective 18 June 2018. The college continued; it was not merged into another.',
    lineage: [lineage('northwest-community-college', 'Northwest Community College', 'Earlier name', 'to 18 June 2018')],
    sources: [statements('cmtn_fs_2526_signed.pdf', 'Coast Mountain College'), designation1978(2967, 'Northwest Community College'), oic(208, 2018, 'Northwest Community College renamed Coast Mountain College, effective 18 June 2018'), source('Province of BC — Northwest Community College renamed (news release 2018AEST0056)', 'https://news.gov.bc.ca/releases/2018AEST0056-000708'), source('Coast Mountain College — Northwest Community College is now Coast Mountain College', 'https://www.coastmountaincollege.ca/about-cmtn/news-media/news/northwest-community-college-is-now-coast-mountain-college')],
    salary: 'coast-mountain-college'
  }),
  institution({
    id: 'college-of-new-caledonia', name: 'College of New Caledonia', shortName: 'CNC', aliases: ['CNC'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://cnc.bc.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Prince George, with campuses in the central interior'),
    historyNote: 'The College of New Caledonia was officially opened on 10 October 1969. Its 1973–74 calendar records its amalgamation with the B.C. Vocational School in Prince George on 9 July 1971. Order in Council 2960/1978 designated it under the Colleges and Provincial Institutes Act.',
    lineage: [lineage('bc-vocational-school-prince-george', 'British Columbia Vocational School — Prince George', 'Amalgamated with it', '9 July 1971')],
    sources: [statements('cnc_fs_2526_signed.pdf', 'College of New Caledonia'), designation1978(2960, 'College of New Caledonia'), source('CNC — History', 'https://www.cnc.bc.ca/about/history'), source('CNC — 1973–74 calendar, institutional history (PDF page 2)', 'https://www.cnc.bc.ca/docs/calendars/academiccalendar-1973-1974.pdf?sfvrsn=ca4762cc_1#page=2')],
    salary: 'college-of-new-caledonia'
  }),
  institution({
    id: 'college-of-the-rockies', name: 'College of the Rockies', shortName: 'COTR', aliases: ['COTR', 'East Kootenay Community College'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://cotr.bc.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Cranbrook, serving the East Kootenay'),
    historyNote: 'East Kootenay Community College opened in 1975. Order in Council 2962/1978 designated it, effective 1 December 1978. Order in Council 1329/1995, approved on 2 November 1995, renamed it College of the Rockies.',
    lineage: [lineage('east-kootenay-community-college', 'East Kootenay Community College', 'Earlier name', '1975–1995')],
    sources: [statements('cotr_fs_2526_final.pdf', 'College of the Rockies'), oic(2962, 1978, 'East Kootenay Community College designated effective 1 December 1978'), oic(1329, 1995, 'East Kootenay Community College renamed College of the Rockies'), source('College of the Rockies — College history', 'https://cotr.bc.ca/about-us/college-history/')],
    salary: 'college-of-the-rockies'
  }),
  institution({
    id: 'douglas-college', name: 'Douglas College', shortName: 'Douglas', aliases: ['Douglas'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://www.douglascollege.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in New Westminster and Coquitlam'),
    historyNote: 'Douglas College opened in 1970. Order in Council 2961/1978 designated it for eight school districts. From 1 April 1981 four of them were served by the new Kwantlen College (Order in Council 626/1981); Douglas carried on.',
    connections: [link('kwantlen-polytechnic-university', 'Kwantlen Polytechnic University', 'Kwantlen College took over four of its school districts on 1 April 1981', { source: oic(626, 1981, 'Kwantlen College designated, effective 1 April 1981') })],
    sources: [statements('doug_fs_2526_signed.pdf', 'Douglas College'), designation1978(2961, 'Douglas College'), oic(626, 1981, 'Kwantlen College designated, effective 1 April 1981'), BCCAT],
    salary: 'douglas-college'
  }),
  institution({
    id: 'langara-college', name: 'Langara College', shortName: 'Langara', aliases: ['Langara', 'snəw̓eyəɬ leləm̓'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://langara.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Vancouver'),
    historyNote: 'The West 49th Avenue campus opened in 1970 as part of Vancouver Community College. Order in Council 77/1994, approved on 12 January 1994, designated Langara College a public college of its own, effective 1 April 1994.',
    connections: [link('vancouver-community-college', 'Vancouver Community College', 'Langara was VCC’s campus until 1 April 1994', { source: oic(77, 1994, 'Langara College designated effective 1 April 1994') })],
    sources: [statements('lang_fs_2526_signed.pdf', 'Langara College'), oic(77, 1994, 'Langara College designated effective 1 April 1994'), source('Langara College — About Langara', 'https://langara.ca/about-langara'), BCCAT],
    salary: 'langara-college'
  }),
  institution({
    id: 'north-island-college', name: 'North Island College', shortName: 'NIC', aliases: ['NIC'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://www.nic.bc.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Courtenay, Campbell River, Port Alberni and Port Hardy'),
    historyNote: 'Order in Council 1660/1975, approved on 8 May 1975, let four school districts set up a college; later orders name it North Island College. Order in Council 2965/1978 designated it under the Colleges and Provincial Institutes Act.',
    sources: [statements('nic_fs_2526_signed.pdf', 'North Island College'), oic(1660, 1975, 'school districts 71, 72, 84 and 85 may establish a college, approved 8 May 1975'), designation1978(2965, 'North Island College'), source('North Island College — History', 'https://nic.bc.ca/about/about-nic/history.html'), BCCAT],
    salary: 'north-island-college'
  }),
  institution({
    id: 'northern-lights-college', name: 'Northern Lights College', shortName: 'NLC', aliases: ['NLC'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://www.nlc.bc.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Dawson Creek, Fort St. John and northeastern British Columbia'),
    historyNote: 'Northern Lights College was founded in 1975. The Dawson Creek vocational school of 1966 came before it. Order in Council 2966/1978 designated it under the Colleges and Provincial Institutes Act.',
    sources: [statements('nlc_fs_2526_signed.pdf', 'Northern Lights College'), designation1978(2966, 'Northern Lights College'), source('Northern Lights College — History', 'https://www.nlc.bc.ca/history/')],
    salary: 'northern-lights-college'
  }),
  institution({
    id: 'okanagan-college', name: 'Okanagan College', shortName: 'Okanagan College', aliases: ['OC', 'Okanagan University College', 'OUC'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://www.okanagan.bc.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Kelowna, Vernon, Penticton and Salmon Arm'),
    historyNote: 'The original Okanagan College was established under an instruction approved on 6 May 1965 and opened in 1968. Order in Council 46/1995 designated it Okanagan University College. Order in Council 1123/2004 designated a new Okanagan College, effective 26 November 2004. Okanagan University College’s accounts record its operations passing to the new college and to UBC’s Okanagan campus effective 1 July 2005. This was a split, not a rename.',
    lineage: [
      lineage('okanagan-college-original', 'Okanagan College (original institution)', 'Earlier name of its predecessor', 'from 1965'),
      lineage('okanagan-university-college', 'Okanagan University College', 'Split into this college and UBC Okanagan', 'to 1 July 2005')
    ],
    connections: [link('university-of-british-columbia', 'University of British Columbia', 'Took Okanagan University College’s other work, as UBC Okanagan, on 1 July 2005', { source: source('Okanagan University College, audited accounts 2006–07, notes 1 and 3 (PDF pages 7–8)', 'https://www.okanagancollege.ca/sites/default/files/2020-02/audit_2006_2007_ouc_states.pdf#page=7') })],
    sources: [statements('okan_fs_2526_signed.pdf', 'Okanagan College'), oic(1123, 2004, 'Okanagan College designated, effective 26 November 2004'), oic(693, 2005, 'Okanagan College region set, approved 22 September 2005'), source('Okanagan University College, audited accounts 2006–07, notes 1 and 3 (PDF pages 7–8)', 'https://www.okanagancollege.ca/sites/default/files/2020-02/audit_2006_2007_ouc_states.pdf#page=7'), BCCAT],
    salary: 'okanagan-college'
  }),
  institution({
    id: 'selkirk-college', name: 'Selkirk College', shortName: 'Selkirk', aliases: ['Selkirk', 'Kootenay School of the Arts'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://selkirk.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Castlegar, Nelson and the West Kootenay'),
    historyNote: 'Selkirk College opened in 1966. Order in Council 2969/1978 designated it under the Colleges and Provincial Institutes Act. The Kootenay School of the Arts became part of the college in July 2006.',
    lineage: [lineage('kootenay-school-of-the-arts', 'Kootenay School of the Arts', 'Joined the college', 'July 2006')],
    sources: [statements('selk_fs_2526_signed.pdf', 'Selkirk College'), designation1978(2969, 'Selkirk College'), BCCAT, source('Province of BC — 2006 Kootenay School of the Arts agreement (2006AE0008)', 'https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2006ae0008-000076.htm')],
    salary: 'selkirk-college'
  }),
  institution({
    id: 'vancouver-community-college', name: 'Vancouver Community College', shortName: 'VCC', aliases: ['VCC', 'Vancouver City College'],
    kind: 'public-college', act: COLLEGE_ACT, officialUrl: 'https://www.vcc.ca/',
    description: describe('public-college', COLLEGE_ACT, 'in Vancouver'),
    historyNote: 'Vancouver City College was formed in 1965 from the city’s vocational, art and adult-education schools. It was renamed Vancouver Community College in 1974. Order in Council 2970/1978 designated it under the Colleges and Provincial Institutes Act; its statements give its incorporation as 28 November 1978. The art school left in 1978 and Langara became a college of its own on 1 April 1994.',
    lineage: [lineage('vancouver-city-college', 'Vancouver City College', 'Earlier name', '1965–1974')],
    connections: [
      link('langara-college', 'Langara College', 'Its Langara campus became a college of its own on 1 April 1994', { source: oic(77, 1994, 'Langara College designated effective 1 April 1994') }),
      link('emily-carr-university', 'Emily Carr University of Art and Design', 'Its art school became the Emily Carr College of Art in 1978', { source: oic(169, 1978, 'Emily Carr College of Art designated a provincial institute, approved 20 January 1978') })
    ],
    sources: [statements('vcc_fs_2526_signed.pdf', 'Vancouver Community College'), designation1978(2970, 'Vancouver Community College'), BCCAT, source('Vancouver School Board heritage — The Vancouver School of Art: a brief history', 'https://blogs.vsb.bc.ca/heritage/2018/01/03/the-vancouver-school-of-art-a-brief-history/')],
    salary: 'vancouver-community-college'
  })
]
