// Executive Council sworn in on 20 November 2026. Portfolio and secretary appointments
// follow OIC 420, transfers follow OIC 421, and deputy appointments follow OIC 427.
export const HANDOVER = '2026-11-20'
export const CABINET_CHECKED = '2026-11-25'
export const CABINET_SOURCE = { id: 's-cabinet', title: 'Executive Council and Parliamentary Secretaries of B.C.', url: 'https://www2.gov.bc.ca/gov/content/governments/organizational-structure/cabinet/cabinet-ministers' }
export const APPOINTMENTS = { id: 'oic-420-2026', title: 'Order in Council 420/2026 — cabinet portfolios and parliamentary secretaries', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/oic_cur/0420_2026' }
export const TRANSFERS = { id: 'oic-421-2026', title: 'Order in Council 421/2026 — ministry reorganization and ministerial responsibilities', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/oic_cur/0421_2026' }
export const DEPUTIES = { id: 'oic-427-2026', title: 'Order in Council 427/2026 — deputy minister appointments', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/oic_cur/0427_2026' }
export const mandateUrl = (filename) => 'https://www2.gov.bc.ca/assets/gov/government/ministries-organizations/premier-cabinet-mlas/minister-letter/' + filename

export const CABINET = {
  "Ministry of Agriculture": {
    minister: "Ian Paton",
    deputy: "Michelle Koski",
    officialUrl: "https://news.gov.bc.ca/ministries/agriculture/biography",
    mandate: "mandate_letter_ian_paton.pdf",
  },
  "Ministry of Attorney General": {
    minister: "Caroline Elliott",
    deputy: "Geoff Cowper",
    deputyTitle: "Deputy Attorney General",
    officialUrl: "https://news.gov.bc.ca/ministries/attorney-general/biography",
    mandate: "mandate_letter_caroline_elliott.pdf",
    title: "Attorney General",
  },
  "Ministry of Children and Family Development": {
    minister: "Kristina Loewen",
    deputy: "Kaye Krishna",
    officialUrl: "https://news.gov.bc.ca/ministries/children-and-family-development/biography",
    mandate: "mandate_letter_kristina_loewen.pdf",
    parliamentarySecretaries: [
      { person: "Margareta Dovgal", title: "Parliamentary Secretary for Children and Youth with Special Needs" }
    ],
  },
  "Ministry of Citizens’ Services and Technology": {
    minister: "Bruce Banman",
    deputy: "Silas Brownsey",
    officialUrl: "https://news.gov.bc.ca/ministries/citizens-services-and-technology/biography",
    mandate: "mandate_letter_bruce_banman.pdf",
    parliamentarySecretaries: [
      { person: "Sacha Peter", title: "Parliamentary Secretary for Technology and Innovation" }
    ],
  },
  "Ministry of Economic Development and Tourism": {
    minister: "Gavin Dew",
    deputy: "Fazil Mihlar",
    officialUrl: "https://news.gov.bc.ca/ministries/economic-development-and-tourism/biography",
    mandate: "mandate_letter_gavin_dew.pdf",
    ministersOfState: [
      { person: "Carson Binda", title: "Minister of State for Red Tape Reduction", mandate: "mandate_letter_carson_binda.pdf" },
      { person: "Anna Kindy", title: "Minister of State for Rural Development", mandate: "mandate_letter_anna_kindy.pdf" }
    ],
    parliamentarySecretaries: [
      { person: "Jody Toor", title: "Parliamentary Secretary for Tourism" }
    ],
  },
  "Ministry of Education and Child Care": {
    minister: "Lynne Block",
    deputy: "Bobbi Plecas",
    officialUrl: "https://news.gov.bc.ca/ministries/education-and-child-care/biography",
    mandate: "mandate_letter_lynne_block.pdf",
  },
  "Ministry of Energy, Mines and Petroleum Resources": {
    minister: "Larry Neufeld",
    deputy: "Nate Amann-Blake",
    officialUrl: "https://news.gov.bc.ca/ministries/energy-mines-and-petroleum-resources/biography",
    mandate: "mandate_letter_larry_neufeld.pdf",
    ministersOfState: [
      { person: "Pete Davis", title: "Minister of State for Mining", mandate: "mandate_letter_pete_davis.pdf" }
    ],
  },
  "Ministry of Environment": {
    minister: "Áʼa:líya Warbus",
    deputy: "Lori Halls",
    deputyTitle: "Deputy Minister and Chief Executive Assessment Officer",
    officialUrl: "https://news.gov.bc.ca/ministries/environment/biography",
    mandate: "mandate_letter_aaliya_warbus.pdf",
  },
  "Ministry of Finance": {
    minister: "Peter Milobar",
    deputy: "Heather Wood",
    officialUrl: "https://news.gov.bc.ca/ministries/finance/biography",
    mandate: "mandate_letter_peter_milobar.pdf",
    parliamentarySecretaries: [
      { person: "Steve Kooner", title: "Parliamentary Secretary for Insurance Corporation of British Columbia" }
    ],
  },
  "Ministry of Forests": {
    minister: "Kiel Giddens",
    deputy: "Janis Simpkins",
    officialUrl: "https://news.gov.bc.ca/ministries/forests/biography",
    mandate: "mandate_letter_kiel_giddens.pdf",
  },
  "Ministry of Health": {
    minister: "Ryan Peterson",
    deputy: "Peter Pokorny",
    officialUrl: "https://news.gov.bc.ca/ministries/health/biography",
    mandate: "mandate_letter_ryan_peterson.pdf",
    parliamentarySecretaries: [
      { person: "Tracy St. Claire", title: "Parliamentary Secretary for Rural Health" },
      { person: "Sharon Hartwell", title: "Parliamentary Secretary for Seniors" }
    ],
  },
  "Ministry of Indigenous Relations and Reconciliation": {
    minister: "Scott McInnis",
    deputy: "Alex MacLennan",
    officialUrl: "https://news.gov.bc.ca/ministries/indigenous-relations-and-reconciliation/biography",
    mandate: "mandate_letter_scott_mcinnis.pdf",
  },
  "Ministry of Local Government, Housing, Sport and Culture": {
    minister: "Cathie Ounsted",
    deputy: "Jonathan Dubé",
    officialUrl: "https://news.gov.bc.ca/ministries/local-government-housing-sport-and-culture/biography",
    mandate: "mandate_letter_cathie_ounsted.pdf",
    ministersOfState: [
      { person: "Zeeshan Wahla", title: "Minister of State for Housing", mandate: "mandate_letter_zeeshan_wahla.pdf" }
    ],
    parliamentarySecretaries: [
      { person: "Megan Knight", title: "Parliamentary Secretary for Metro Vancouver" },
      { person: "Mandeep Dhaliwal", title: "Parliamentary Secretary for Sport and Culture" }
    ],
  },
  "Ministry of Post-Secondary Education and Labour": {
    minister: "Korky Neufeld",
    deputy: "Trevor Hughes",
    officialUrl: "https://news.gov.bc.ca/ministries/post-secondary-education-and-labour/biography",
    mandate: "mandate_letter_korky_neufeld.pdf",
    ministersOfState: [
      { person: "Harman Bhangu", title: "Minister of State for Labour", mandate: "mandate_letter_harman_bhangu.pdf" }
    ],
  },
  "Ministry of Public Safety and Solicitor General": {
    minister: "Jessy Sahota",
    deputy: "Tara Richards",
    deputyTitle: "Deputy Solicitor General",
    officialUrl: "https://news.gov.bc.ca/ministries/public-safety-and-solicitor-general/biography",
    mandate: "mandate_letter_jessy_sahota.pdf",
    ministersOfState: [
      { person: "Ward Stamer", title: "Minister of State for Emergency Management", mandate: "mandate_letter_ward_stamer.pdf" }
    ],
    parliamentarySecretaries: [
      { person: "Rosalyn Bird", title: "Parliamentary Secretary for Armed Forces and Veterans Affairs" },
      { person: "Bryan Tepper", title: "Parliamentary Secretary for Urban Policing" }
    ],
  },
  "Ministry of Social Development": {
    minister: "Claire Rattée",
    deputy: "Teri Collins",
    officialUrl: "https://news.gov.bc.ca/ministries/social-development/biography",
    mandate: "mandate_letter_claire_rattee.pdf",
    title: "Minister of Social Development and Deputy Premier",
  },
  "Ministry of Transportation and Infrastructure": {
    minister: "Trevor Halford",
    deputy: "Keith Godin",
    officialUrl: "https://news.gov.bc.ca/ministries/transportation-and-infrastructure/biography",
    mandate: "mandate_letter_trevor_halford.pdf",
    parliamentarySecretaries: [
      { person: "Misty Van Popta", title: "Parliamentary Secretary for Infrastructure" },
      { person: "Harj Dhaliwal", title: "Parliamentary Secretary for TransLink" }
    ],
  },
  "Ministry of Water, Land and Natural Resource Operations": {
    minister: "Donegal Wilson",
    deputy: "Kevin Jardine",
    officialUrl: "https://news.gov.bc.ca/ministries/water-land-and-natural-resource-operations/biography",
    mandate: "mandate_letter_donegal_wilson.pdf",
  },
}

// Appendix A. The first destination carries the remaining functions except where the old
// portfolio was split by subject (Tourism, Arts, Culture and Sport). Those bodies are named below.
export const REORGANIZED = {
  'ministry-of-agriculture-and-food-2022': ['Agriculture'],
  'ministry-of-citizens-services-2017': ['Citizens’ Services and Technology'],
  'ministry-of-jobs-and-economic-growth-2025': ['Economic Development and Tourism'],
  'ministry-of-energy-and-climate-solutions-2024': ['Energy, Mines and Petroleum Resources', 'Environment'],
  'ministry-of-mining-and-critical-minerals-2024': ['Energy, Mines and Petroleum Resources'],
  'ministry-of-environment-and-parks-2024': ['Environment'],
  'ministry-of-housing-and-municipal-affairs-2024': ['Local Government, Housing, Sport and Culture'],
  'ministry-of-tourism-arts-culture-and-sport-2020': ['Local Government, Housing, Sport and Culture', 'Economic Development and Tourism'],
  'ministry-of-post-secondary-education-and-future-skills-2022': ['Post-Secondary Education and Labour', 'Economic Development and Tourism'],
  'ministry-of-labour-2017': ['Post-Secondary Education and Labour'],
  'ministry-of-social-development-and-poverty-reduction-2017': ['Social Development'],
  'ministry-of-transportation-and-transit-2024': ['Transportation and Infrastructure'],
  'ministry-of-infrastructure-2024': ['Transportation and Infrastructure', 'Citizens’ Services and Technology'],
  'ministry-of-water-land-and-resource-stewardship-2022': ['Water, Land and Natural Resource Operations'],
  'ministry-of-emergency-management-and-climate-readiness-2022': ['Public Safety and Solicitor General', 'Local Government, Housing, Sport and Culture']
}

// Exceptions to continuation of the predecessor’s functions. The locator is displayed on
// the receiving body so readers can follow the assignment back to the transfer order.
export const BODY_TRANSFERS = {
  'sub-crown-agencies-and-board-resourcing-office': ['Premier', 'Appendix A, section 2'],
  'bc-railway-company': ['Transportation and Infrastructure', 'Appendix B, item 38'],
  'technical-safety-bc': ['Local Government, Housing, Sport and Culture', 'Appendix B, item 549'],
  'northern-development-initiative-trust': ['Economic Development and Tourism', 'Appendix B, item 443'],
  'justice-institute': ['Post-Secondary Education and Labour', 'Appendix B, item 68'],
  'icbc': ['Finance', 'Appendix B, item 287'],
  'liquor-distribution-branch': ['Finance', 'Appendix B, item 346'],
  'sub-liquor-and-cannabis-regulation-branch': ['Public Safety and Solicitor General', 'Appendix B, items 52 and 345'],
  'innovate-bc': ['Economic Development and Tourism', 'Appendix B, item 282'],
  'skilledtradesbc': ['Economic Development and Tourism', 'Appendix A, section 11'],
  'sub-bc-provincial-nominee-program': ['Economic Development and Tourism', 'Appendix A, section 10'],
  'sub-bc-newcomers-services-program': ['Economic Development and Tourism', 'Appendix A, section 10'],
  'creative-bc': ['Economic Development and Tourism', 'Appendix A, section 12'],
  'destination-bc': ['Economic Development and Tourism', 'Appendix A, section 13'],
  'sub-mountain-resorts-branch': ['Economic Development and Tourism', 'Appendix A, section 13'],
  'sub-heritage-branch': ['Economic Development and Tourism', 'Appendix A, section 13 (heritage property management)'],
  'bc-pavilion-corporation': ['Economic Development and Tourism', 'Appendix B, item 27'],
  'bc-games-society': ['Local Government, Housing, Sport and Culture', 'Appendix A, section 32'],
  'royal-bc-museum': ['Local Government, Housing, Sport and Culture', 'Appendix B, item 425'],
  'knowledge-network': ['Local Government, Housing, Sport and Culture', 'Appendix B, item 309'],
  'sub-gender-equity-office': ['Attorney General', 'Appendix A, section 5'],
  'sub-real-property-division': ['Citizens’ Services and Technology', 'Appendix A, section 8'],
  'sub-climate-action-secretariat': ['Environment', 'Appendix A, section 19'],
  'sub-climate-solutions-council': ['Environment', 'Appendix A, section 19'],
  'sub-cleanbc': ['Environment', 'Appendix A, section 19 (provincial climate action framework)'],
  'sub-bc-output-based-pricing-system': ['Environment', 'Appendix B, item 234'],
  'bc-public-service-agency': ['Finance', 'Schedule 2', DEPUTIES],
  'government-communications-and-public-engagement': ['Finance', 'Schedule 2', DEPUTIES]
}
