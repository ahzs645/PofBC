// Known employer names and atlas associations. Renamed atlas entities retain their historical ids.
export const BODIES = {
  'B.C. Assessment': 'bc-assessment',
  'B.C. Housing': 'bc-housing',
  'B.C. Investment Management Corporation': 'bc-investment-management-corporation',
  'B.C. Investment Management Corporation (BCI)': 'bc-investment-management-corporation',
  'B.C. Lottery Corporation': 'bclc',
  'B.C. Lottery Corporation (BCLC)': 'bclc',
  'B.C. Oil and Gas Commission': 'oil-and-gas-commission',
  'B.C. Energy Regulator': 'bc-energy-regulator',
  'B.C. Pavilion Corporation': 'bc-pavilion-corporation',
  'B.C. Securities Commission': 'bc-securities-commission',
  'B.C. Transit': 'bc-transit',
  'B.C. Utilities Commission': 'bc-utilities-commission',
  'BC Hydro and Power Authority': 'bc-hydro',
  'B.C. Hydro': 'bc-hydro',
  'Columbia Basin Trust': 'columbia-basin-trust',
  'Columbia Power Corporation': 'columbia-power',
  'Community Living B.C.': 'community-living-bc',
  'Forestry Innovation Investsment': 'forestry-innovation-investment',
  'Forestry Innovation Investment': 'forestry-innovation-investment',
  'ICBC': 'icbc',
  'Legal Services Society': 'legal-aid-bc',
  'Legal Aid B.C.': 'legal-aid-bc',
  'Powerex Corporation': 'sub-powerex',
  'Powerex': 'sub-powerex',
  'Powertech Labs. Inc.': 'sub-powertech-labs',
  'PowerTech': 'sub-powertech-labs',
  'Columbia Hydro Constructors Ltd.': 'sub-columbia-hydro-constructors',
  'Royal B.C. Museum': 'royal-bc-museum',
  'Technical Safety B.C.': 'technical-safety-bc',
  'Worksafe B.C.': 'workers-compensation-board',
  'WorkSafe B.C.': 'workers-compensation-board',
  'B.C. Council for International Education': 'bc-council-for-international-education',
  'B.C. Financial Services Authority': 'bc-financial-services-authority',
  'B.C. Infrastructure Benefits': 'bc-infrastructure-benefits',
  'B.C. Liquor Distribution Branch': 'liquor-distribution-branch',
  'Liquor Distribution Branch': 'liquor-distribution-branch',
  'B.C. Pension Corp.': 'bc-pension-corporation',
  'Destination B.C.': 'destination-bc',
  "First Peoples' Cultural Council": 'first-peoples-cultural-council',
  'First Peoples’ Heritage, Language and Culture Council': 'first-peoples-cultural-council',
  'Forest Enhancement Society of B.C.': 'forest-enhancement-society',
  'InBC Investment Corp.': 'inbc',
  'Industry Training Authority of B.C.': 'industry-training-authority',
  'Skilled Trades B.C.': 'skilledtradesbc',
  'Infrastructure B.C.': 'infrastructure-bc',
  'Innovate B.C.': 'innovate-bc',
  'Knowledge Network': 'knowledge-network',
  'Transportation Investment Corporation': 'transportation-investment-corporation',
  'Fraser Health': 'fraser-health',
  'Interior Health': 'interior-health',
  'Northern Health': 'northern-health',
  'PHSA': 'provincial-health-services-authority',
  'Provincial Health Services Authority (PHSA)': 'provincial-health-services-authority',
  'Vancouver Coastal Health': 'vancouver-coastal-health',
  'Vancouver Island Health': 'island-health',
  'Island Health': 'island-health',
  // The public service, disclosed as one employer: shown on every ministry, and on its agency.
  'Provincial government': 'public-service'
}

export const EMPLOYER_ALIASES = { 'langley-city': 'city-of-langley' }
export const canonicalSlug = (slug) => EMPLOYER_ALIASES[slug] ?? slug
const SAME_EMPLOYER = {
  emilycarr: 'emily-carr-university', 'emily-carr': 'emily-carr-university', 'oakanagan-college': 'okanagan-college',
  'providence-health': 'providence-health-care', 'township-of-langley': 'langley-township', 'district-of-delta': 'city-of-delta',
  'district-of-mission': 'city-of-mission'
}
export const employerSlug = (name) => {
  if (BODIES[name]) return BODIES[name]
  const slug = String(name).toLowerCase()
    .replace(/\([^)]*\)/g, ' ').replace(/\bb\.\s*c\./g, 'bc').replace(/\bbritish columbia\b/g, 'bc').replace(/&/g, ' and ')
    .replace(/\bschool board\b/g, 'school district').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  return canonicalSlug(SAME_EMPLOYER[slug] ?? slug)
}
export const sectorOf = (sector) => [
  [/crown/i, 'Crown corporations'], [/health/i, 'Health authorities'], [/school/i, 'School districts'],
  [/universit|college/i, 'Universities and colleges'], [/police/i, 'Municipal police'], [/government/i, 'Government']
].find(([pattern]) => pattern.test(sector))?.[1] ?? sector
