// Organizations the Province consolidates in its Public Accounts that are not provincial
// executive bodies: societies the health and education families work through, a national blood
// operator, and a few short-lived societies and projects. They were found by the Public Accounts
// inventory (research/finance/public-accounts-23-1/missing.csv) and re-checked on 27 November 2026
// against their own financial statements and BC Registries (OrgBook BC). A date is said only where
// one of those sources gives it.
//
// These are catalogue records, like the rest of relatedBodies.js: they are never drawn as members of
// the provincial executive, and a link to an atlas body is a sourced connection, not a placement.

export const PUBLIC_ACCOUNTS_BODIES_CHECKED = '2026-11-27'

const PA = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/'
/** A Public Accounts statement, by fiscal year and file slug, with a title that says which year. */
const statement = (year, slug, name) => ({ title: `${name}, financial statements ${year} (Public Accounts)`, url: `${PA}${year}/sup-e/${slug}-fs-${year}.pdf` })
/** A BC Registries entity, as OrgBook BC shows it. */
const registry = (id, name) => ({ title: `BC Registries (OrgBook BC): ${name}, ${id}`, url: `https://orgbook.gov.bc.ca/entity/${id}` })
const employer = (slug, label, extra = {}) => ({ slug, label, ...extra })
/** A sourced connection to an atlas body or another related body. */
const link = (id, label, description, extra = {}) => ({ id, label, description, ...extra })

const HEALTH_AFFILIATE = 'A society that runs hospital or residential care under an agreement with its health authority, which passes on most of its funding. The Province consolidates its statements in the health sector.'

export const PUBLIC_ACCOUNTS_RELATED_BODIES = [
  // ── Health: affiliated and denominational societies ─────────────────────────────────────────────
  {
    id: 'providence-health-care', name: 'Providence Health Care Society', shortName: 'Providence Health Care',
    aliases: ['Providence', 'PHC', 'St. Paul’s Hospital', 'Mount Saint Joseph Hospital', 'S0041359'], kind: 'affiliated-health-society',
    officialUrl: 'https://www.providencehealthcare.org/',
    description: `A Catholic health care society in Vancouver, sponsored by the Sisters of Charity of Providence in British Columbia. It is funded mainly by the Ministry of Health through Vancouver Coastal Health. ${HEALTH_AFFILIATE}`,
    historyNote: 'BC Registries records the society as formed by amalgamation on 31 March 2000. Its statements are in the Public Accounts every year from 2004-05.',
    sources: [statement('2025-26', 'providence-health-care', 'Providence Health Care Society'), registry('S0041359', 'Providence Health Care Society')],
    salaryEmployers: [employer('providence-health-care', 'Providence Health Care')],
    relationships: [link('vancouver-coastal-health', 'Vancouver Coastal Health', 'Health authority through which the Ministry of Health funds it', { source: statement('2025-26', 'providence-health-care', 'Providence Health Care Society') })]
  },
  {
    id: 'mount-st-mary-hospital', name: 'Mount St. Mary Hospital', shortName: 'Mount St. Mary',
    aliases: ['Marie Esther Society', 'S0026756'], kind: 'affiliated-health-society',
    description: `A Victoria hospital founded by the Sisters of St. Ann, owned and operated by the Marie Esther Society. Under the Hospital Insurance Act it is funded by Island Health. ${HEALTH_AFFILIATE}`,
    historyNote: 'The society was incorporated under the Society Act on 19 October 1990. Its statements are in the Public Accounts from 2004-05.',
    sources: [statement('2025-26', 'mount-st-mary-hospital', 'Mount St. Mary Hospital'), registry('S0026756', 'The Marie Esther Society')],
    salaryEmployers: [],
    relationships: [link('island-health', 'Island Health', 'Health authority that funds it', { source: statement('2025-26', 'mount-st-mary-hospital', 'Mount St. Mary Hospital') })]
  },
  {
    id: 'louis-brier-home-and-hospital', name: 'Louis Brier Home and Hospital', shortName: 'Louis Brier',
    aliases: ['Jewish Home for the Aged of British Columbia'], kind: 'affiliated-health-society',
    description: `Residential health care run by the Jewish Home for the Aged of British Columbia, operating as Louis Brier Home and Hospital. Its main revenue is provincial funding through Vancouver Coastal Health. ${HEALTH_AFFILIATE}`,
    historyNote: 'Its statements are in the Public Accounts every year from 2004-05.',
    sources: [statement('2025-26', 'louis-brier-home-and-hospital', 'Louis Brier Home and Hospital')],
    salaryEmployers: [],
    relationships: [link('vancouver-coastal-health', 'Vancouver Coastal Health', 'Health authority that funds it', { source: statement('2025-26', 'louis-brier-home-and-hospital', 'Louis Brier Home and Hospital') })]
  },
  {
    id: 'menno-hospital', name: 'Mennonite Benevolent Society – Menno Hospital', shortName: 'Menno Hospital',
    aliases: ['Menno Home', 'Mennonite Benevolent Society', 'S0004343'], kind: 'affiliated-health-society',
    description: `A hospital and long-term care campus in Abbotsford run by the Mennonite Benevolent Society under an operating agreement with Fraser Health, which pays its operating grant. ${HEALTH_AFFILIATE}`,
    historyNote: 'The Mennonite Benevolent Society was registered on 1 September 1953. The hospital’s statements are in the Public Accounts from 2004-05.',
    sources: [statement('2025-26', 'menno-hospital', 'Menno Hospital'), registry('S0004343', 'Mennonite Benevolent Society')],
    salaryEmployers: [],
    relationships: [link('fraser-health', 'Fraser Health', 'Operating agreement and operating grant', { source: statement('2025-26', 'menno-hospital', 'Menno Hospital') })]
  },
  {
    id: 'st-michaels-centre', name: 'St. Michael’s Centre', shortName: 'St. Michael’s Centre',
    aliases: ["St. Michael's Centre", 'St Michaels Centre'], kind: 'affiliated-health-society',
    description: 'A health care society the Province consolidates in its health sector. Its statements are scanned images, so its programs and funding authority are not read here.',
    historyNote: 'Its statements are in the Public Accounts every year from 2004-05. Which registered society files them is not read from the scanned statements, so none is named here.',
    sources: [statement('2025-26', 'st-michaels-centre', 'St. Michael’s Centre'), statement('2004-05', 'st-michaels-centre', 'St. Michael’s Centre')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'st-josephs-general-hospital', name: 'St. Joseph’s General Hospital', shortName: 'St. Joseph’s, Comox',
    aliases: ["St. Joseph's General Hospital", 'Comox hospital'], kind: 'affiliated-health-society', historical: true,
    description: 'A Catholic hospital in Comox under the Bishop of Victoria, funded mainly by Island Health. On 1 October 2017 Island Health took over acute care at the new Comox Valley Hospital and St. Joseph’s kept hospice and long-term residential care.',
    historyNote: 'Its statements are in the Public Accounts from 2004-05 to 2018-19. Effective 31 March 2019 the Bishop of Victoria dissolved the hospital’s board of directors.',
    sources: [statement('2018-19', 'st-josephs-general-hospital', 'St. Joseph’s General Hospital'), statement('2004-05', 'st-josephs-general-hospital', 'St. Joseph’s General Hospital')],
    salaryEmployers: [],
    relationships: [link('island-health', 'Island Health', 'Funded it, and took over its acute care on 1 October 2017', { year: 2017, source: statement('2018-19', 'st-josephs-general-hospital', 'St. Joseph’s General Hospital') })]
  },
  ...[
    ['bella-coola-general-hospital', 'Bella Coola General Hospital', 'Bella Coola', 'vancouver-coastal-health', 'Vancouver Coastal Health', '2013-14', '2014-04-01', 'at fair market value'],
    ['rw-large-memorial-hospital', 'RW Large Memorial Hospital', 'Bella Bella (Waglisla)', 'vancouver-coastal-health', 'Vancouver Coastal Health', '2013-14', '2014-04-01', 'at fair market value'],
    ['wrinch-memorial-hospital', 'Wrinch Memorial Hospital', 'Hazelton', 'northern-health', 'Northern Health', '2015-16', '2016-04-01', 'at net book value']
  ].map(([id, name, place, authority, authorityName, lastYear, ended, basis]) => ({
    id, name, shortName: name, aliases: ['United Church Health Services Society', 'UCHSS'], kind: 'affiliated-health-society', historical: true,
    description: `A hospital in ${place}, established under the Hospital Act and run by the United Church Health Services Society under an affiliation agreement with ${authorityName}.`,
    historyNote: `Its statements are in the Public Accounts from 2004-05 to ${lastYear}. As of ${ended === '2014-04-01' ? '1 April 2014' : '1 April 2016'} the affiliation agreement was terminated and its assets and liabilities were to pass to ${authorityName} ${basis}.`,
    sources: [statement(lastYear, id, name), registry('S0053468', 'The United Church Health Services Society')],
    salaryEmployers: [],
    relationships: [link(authority, authorityName, `Affiliated health authority; took over its assets and liabilities from ${ended.slice(0, 4)}`, { year: Number(ended.slice(0, 4)), source: statement(lastYear, id, name) })]
  })),
  {
    id: 'nisgaa-valley-health-authority', name: 'Nisga’a Valley Health Authority', shortName: 'Nisga’a Valley Health Authority',
    aliases: ["Nisga'a Valley Health Authority", 'Nisgaa Valley Health Authority', 'Nisga’a Valley Health Board', 'NVHA', 'S0019586'], kind: 'affiliated-health-society',
    description: 'A Nisga’a health society funded by the Ministry of Health and the Nisga’a Lisims Government. The Province consolidates its statements in the health sector.',
    historyNote: 'Registered as the Nisga’a Valley Health Board on 16 October 1984 and renamed the Nisga’a Valley Health Authority on 31 August 2004. Its statements are in the Public Accounts from 2004-05.',
    sources: [statement('2025-26', 'nisgaa-valley-health-authority', 'Nisga’a Valley Health Authority'), registry('S0019586', 'Nisga’a Valley Health Authority')],
    salaryEmployers: [], relationships: []
  },

  // ── Health: sector-wide societies and services ──────────────────────────────────────────────────
  {
    id: 'canadian-blood-services', name: 'Canadian Blood Services', shortName: 'Canadian Blood Services',
    aliases: ['CBS', 'Blood services'], kind: 'national-nonprofit', officialUrl: 'https://www.blood.ca/',
    description: 'The national blood operator, a registered charity incorporated under Part II of the Canada Corporations Act on 16 February 1998. Its members are the ministers of health of the provinces and territories except Québec, who fund it with the federal and Québec governments. British Columbia includes it in the health sector of its Public Accounts; the Province does not own it alone.',
    historyNote: 'Its statements are in the Public Accounts from 1999-2000.',
    sources: [statement('2025-26', 'canadian-blood-services', 'Canadian Blood Services'), statement('1999-00', 'canadian-blood-services', 'Canadian Blood Services')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'bc-clinical-and-support-services-society', name: 'BC Clinical and Support Services Society', shortName: 'BCCSS',
    aliases: ['SSO Administration Society', 'SSO', 'Shared Services Organization', 'S0054278'], kind: 'health-sector-society', historical: true,
    description: 'A society of the health authorities that first coordinated shared services (as the SSO Administration Society) and from 1 April 2016 provided clinical, laboratory and support services, taking over the support services of Health Shared Services BC, a PHSA division. It was amalgamated with the Provincial Health Services Authority in 2018.',
    historyNote: 'Registered as the SSO Administration Society on 15 October 2008; its operations moved into PHSA’s Health Shared Services BC division on 17 September 2010; inactive until it began operating again as BCCSS on 1 April 2016; amalgamated with PHSA on 29 June 2018.',
    sources: [
      statement('2010-11', 'shared-services-organization', 'SSO Administration Society'),
      statement('2016-17', 'bc-clinical-support-services-society', 'BC Clinical and Support Services Society'),
      { title: 'BC Registries, society amalgamations, 5 July 2018 (PHSA and BCCSS)', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/corpreg/corpreg/soc0705soc0118' }
    ],
    salaryEmployers: [employer('bc-clinical-and-support-services-society', 'BC Clinical and Support Services Society')],
    relationships: [link('provincial-health-services-authority', 'Provincial Health Services Authority', 'Took over its shared services in 2010; amalgamated with it in 2018', { year: 2018 })]
  },
  {
    id: 'bc-health-services-purchasing-organization', name: 'British Columbia Health Services Purchasing Organization', shortName: 'BCHSPO',
    aliases: ['HSPO', 'BC Health Services Purchasing Organization', 'S0056172'], kind: 'health-sector-society', historical: true,
    description: 'A health-sector purchasing society incorporated on 12 January 2010. The Province consolidated its statements in the health sector from 2010-11 to 2012-13.',
    historyNote: 'BC Registries lists the society as dissolved on 6 January 2016.',
    sources: [statement('2010-11', 'bc-health-services-purchasing-org', 'British Columbia Health Services Purchasing Organization'), registry('S0056172', 'British Columbia Health Services Purchasing Organization')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'bc-health-care-ohs-society', name: 'BC Health Care Occupational Health and Safety Society', shortName: 'BC Health Care OHS Society',
    aliases: ['OHS Society', 'SafeCare BC', 'S0074096'], kind: 'health-sector-society',
    description: 'A society that promotes safe and healthy workplaces across the B.C. health care sector, bringing unions, employers and Doctors of BC together on a provincial health and safety framework. It was recommended by a working group set up under the 2019–2022 collective agreements.',
    historyNote: 'Incorporated under the Societies Act on 30 November 2020. Its statements are in the Public Accounts from 2021-22.',
    sources: [statement('2025-26', 'bc-health-care-ohs-society', 'BC Health Care Occupational Health and Safety Society'), registry('S0074096', 'BC Health Care Occupational Health and Safety Society')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'bc-academic-health-council', name: 'BC Academic Health Council', shortName: 'BCAHC',
    aliases: ['C.O.U.T.H.', 'COUTH', 'S0026973'], kind: 'health-sector-society', historical: true,
    description: 'A health-sector society, first registered as the Council of University Teaching Hospitals. The Province consolidated its statements in the health sector from 2010-11 to 2013-14.',
    historyNote: 'Registered on 19 December 1990 as C.O.U.T.H. Council of University Teaching Hospitals and renamed the BC Academic Health Council on 11 December 2002. BC Registries lists it as dissolved on 1 May 2014.',
    sources: [statement('2013-14', 'bc-academic-health-council', 'BC Academic Health Council'), registry('S0026973', 'BC Academic Health Council')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'bc-health-care-risk-management-society', name: 'B.C. Health Care Risk Management Society', shortName: 'Health Care Risk Management Society',
    aliases: ['BCHCRMS', 'S0021764'], kind: 'health-sector-society', historical: true,
    description: 'A health-sector society consolidated in the Province’s accounts for 1999-2000.',
    historyNote: 'Registered on 21 October 1986; BC Registries lists it as dissolved on 2 April 2003.',
    sources: [statement('1999-00', 'bc-health-care-risk-management', 'B.C. Health Care Risk Management Society'), registry('S0021764', 'B.C. Health Care Risk Management Society')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'health-facilities-association-of-bc', name: 'Health Facilities Association of British Columbia', shortName: 'Health Facilities Association',
    aliases: ['HFABC', 'S0011907'], kind: 'health-sector-society', historical: true,
    description: 'A society through which provincial capital contributions for health facilities passed: its 2000-01 statements show some $202 million of provincial contributions paid out as prepaid capital advances, with the debentures and mortgages behind them.',
    historyNote: 'Registered on 15 October 1975; BC Registries lists it as dissolved on 27 July 2001. Its statements are in the Public Accounts for 1999-2000 and 2000-01.',
    sources: [statement('2000-01', 'health-facilities-association', 'Health Facilities Association of British Columbia'), registry('S0011907', 'Health Facilities Association of British Columbia')],
    salaryEmployers: [], relationships: []
  },

  // ── Education ───────────────────────────────────────────────────────────────────────────────────
  {
    id: 'bcnet', name: 'BCNET', shortName: 'BCNET', aliases: ['BCNET Networking Society', 'BC Net', 'BC.NET'], kind: 'members-society',
    officialUrl: 'https://www.bc.net/',
    description: 'A not-for-profit owned by its members, the public universities and colleges, that runs the province’s research and education network and shared IT services. It is incorporated under the Canada Not-for-profit Corporations Act and prepares its statements under section 23.1 of the Budget Transparency and Accountability Act. Most of its revenue comes from its members, which are themselves in the government reporting entity.',
    historyNote: 'BCNET Networking Society was incorporated under the B.C. Society Act on 31 July 1995. BCNET was incorporated federally by letters patent dated 29 September 2005, took over the society’s assets and liabilities on 1 April 2006, and continued under the Canada Not-for-profit Corporations Act on 28 June 2013. Its statements are in the Public Accounts from 2015-16.',
    sources: [
      { title: 'BCNET, financial statements for the year ended 31 March 2024', url: 'https://bc.net/sites/default/files/2024-08/20240331_bcnet_financial_statements.pdf' },
      statement('2015-16', 'bcnet', 'BCNET'), statement('2025-26', 'bcnet', 'BCNET'), registry('S0034004', 'BCNET Networking Society')
    ],
    salaryEmployers: [],
    relationships: [
      link('university-of-british-columbia', 'University of British Columbia', 'Member institution'),
      link('simon-fraser-university', 'Simon Fraser University', 'Member institution'),
      link('university-of-victoria', 'University of Victoria', 'Member institution'),
      link('university-of-northern-bc', 'University of Northern British Columbia', 'Member institution'),
      link('bcit', 'British Columbia Institute of Technology', 'Member institution')
    ]
  },
  {
    id: 'trades-training-consortium-of-bc', name: 'Trades Training Consortium of British Columbia', shortName: 'Trades Training Consortium',
    aliases: ['TTC', 'S0049670'], kind: 'members-society', historical: true,
    description: 'A society of fifteen educational institutions offering trades training, formed to encourage communication and coordination between them and industry.',
    historyNote: 'Incorporated on 8 September 2005; dissolved as a society on 11 May 2015. It operated under its board until 31 July 2015, and its remaining net assets were to go to BCIT.',
    sources: [statement('2015-16', 'trades-training-consortium-of-bc', 'Trades Training Consortium of British Columbia'), registry('S0049670', 'Trades Training Consortium of British Columbia')],
    salaryEmployers: [],
    relationships: [link('bcit', 'BCIT', 'Member institution that received its remaining net assets', { source: statement('2015-16', 'trades-training-consortium-of-bc', 'Trades Training Consortium of British Columbia') })]
  },
  {
    id: 'institute-of-indigenous-government', name: 'Institute of Indigenous Government', shortName: 'IIG',
    aliases: ['IIG'], kind: 'public-institute', historical: true,
    description: 'A post-secondary institution designated as a public institute under the College and Institute Act. It formally began operating in August 1995 and depended on government funding.',
    historyNote: 'Its statements are in the Public Accounts for 2005-06 only.',
    sources: [statement('2005-06', 'institute-indigenous-government', 'Institute of Indigenous Government')],
    salaryEmployers: [], relationships: []
  },

  // ── Other ───────────────────────────────────────────────────────────────────────────────────────
  {
    id: 'real-estate-foundation-of-bc', name: 'Real Estate Foundation of British Columbia', shortName: 'Real Estate Foundation',
    aliases: ['REFBC'], kind: 'statutory-foundation', officialUrl: 'https://www.refbc.com/',
    description: 'A foundation incorporated under the Real Estate Services Act. Its statements describe it as a government not-for-profit organization.',
    historyNote: 'Its statements are in the Public Accounts from 2016-17 to 2021-22.',
    sources: [statement('2021-22', 'real-estate-foundation-of-bc', 'Real Estate Foundation of BC'), statement('2016-17', 'real-estate-foundation-of-bc', 'Real Estate Foundation of BC')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'vancouver-trade-and-convention-centre-authority', name: 'Vancouver Trade and Convention Centre Authority', shortName: 'VTCC Authority',
    aliases: ['Vancouver Trade and Convention Centre', 'VTCC', 'XS0039687'], kind: 'project-authority', historical: true,
    description: 'A not-for-profit corporation without share capital, most of whose directors the Province appointed, set up to finance, build and own an expanded convention centre at Canada Place. The Province cancelled the project on 5 October 1999 and the authority turned to winding up.',
    historyNote: 'Incorporated on 2 October 1998 under Part II of the Canada Corporations Act. Its statements are in the Public Accounts from 1999-2000 to 2005-06. BC Registries lists its extraprovincial registration as historical from 18 July 2017.',
    sources: [statement('1999-00', 'vancouver-trade-convention-centre', 'Vancouver Trade and Convention Centre Authority'), statement('2005-06', 'vancouver-trade-convention-centre', 'Vancouver Trade and Convention Centre Authority'), registry('XS0039687', 'Vancouver Trade and Convention Centre Authority')],
    salaryEmployers: [],
    relationships: [link('vancouver-convention-centre-expansion-project', 'Vancouver Convention Centre Expansion Project Ltd.', 'The later company that built the expansion, from 2003', { year: 2005 })]
  },
  {
    id: 'pacific-national-exhibition', name: 'Pacific National Exhibition', shortName: 'PNE', aliases: ['PNE', 'Playland', 'Hastings Park'], kind: 'exhibition-corporation',
    officialUrl: 'https://www.pne.ca/',
    description: 'A not-for-profit exhibition corporation incorporated under the Pacific National Exhibition Incorporation Act to further agriculture and other industries and promote community development. It operates on the City of Vancouver’s Hastings Park site.',
    historyNote: 'The Province consolidated it until ownership passed to the City of Vancouver, effective 1 January 2004, after provincial legislation was amended in 2003; the Province made a one-time grant to clear its net asset deficiency. Its statements are in the Public Accounts for three years from 1999-2000 to 2003-04.',
    sources: [statement('2003-04', 'pacific-national-exhibition', 'Pacific National Exhibition'), statement('1999-00', 'pacific-national-exhibition', 'Pacific National Exhibition')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'bc-festival-of-the-arts', name: 'B.C. Festival of the Arts Society', shortName: 'BC Festival of the Arts',
    aliases: ['BC Festival of the Arts', 'S0024020'], kind: 'provincial-society', historical: true,
    description: 'A society that produced, on behalf of the provincial government, a multidisciplinary arts festival with a host municipality, to develop promising B.C. artists and regional participation in the arts.',
    historyNote: 'Registered on 26 August 1988; BC Registries lists it as dissolved on 20 May 2005. Its statements are in the Public Accounts from 1999-2000 to 2002-03.',
    sources: [statement('2002-03', 'bc-festival-of-the-arts', 'BC Festival of the Arts'), registry('S0024020', 'B.C. Festival of the Arts Society')],
    salaryEmployers: [], relationships: []
  },
  {
    id: 'bc-society-for-the-distribution-of-gaming-revenue', name: 'BC Society for the Distribution of Gaming Revenue to Charities', shortName: 'Gaming revenue society',
    aliases: ['BC Society for the Distribution of Gaming Revenue', 'S0038580'], kind: 'provincial-society', historical: true,
    description: 'A society consolidated in the Province’s accounts from 1999-2000 to 2001-02, named for distributing gaming revenue to charities.',
    historyNote: 'Registered on 10 July 1998; BC Registries lists it as dissolved on 22 June 2004.',
    sources: [statement('1999-00', 'bc-society-distrib-gaming-revenue', 'BC Society for the Distribution of Gaming Revenue'), registry('S0038580', 'BC Society for the Distribution of Gaming Revenue to Charities')],
    salaryEmployers: [], relationships: []
  }
].map((body) => ({ ...body, checked: PUBLIC_ACCOUNTS_BODIES_CHECKED }))
