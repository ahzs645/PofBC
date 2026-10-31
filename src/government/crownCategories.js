// What kind of Crown corporation each is: commercial, or service delivery.
//
// The Province sorts its public sector organizations into kinds, and defines two of Crown
// corporation (gov.bc.ca, "Public sector organizations"): a commercial Crown delivers goods and
// services for profit and funds itself from what it earns; a service delivery Crown delivers them
// on government policy, and most are funded mainly by government. Which Crowns are commercial is
// named in the Budget: Table 1.4 of Budget 2025's fiscal plan lists the commercial Crown
// corporations' net income — BC Hydro, the Liquor Distribution Branch, BCLC and ICBC, with
// Columbia Power Corporation and BC Railway Company in its "Other" line. Every other Crown
// corporation the diagram draws is a service delivery Crown.
//
// The list is Budget 2025's, so it is drawn from 2025 on and not carried back: a Crown that was
// commercial in 1990 is not shown as such on the strength of a 2025 table.

export const CROWN_CATEGORIES_FROM = 2025

export const CROWN_CATEGORY_SOURCES = {
  definitions: {
    title: 'Government of British Columbia, “Public sector organizations”',
    url: 'https://www2.gov.bc.ca/gov/content/governments/services-for-government/public-sector-management/public-sector-organizations',
    locator: 'sections “Commercial Crown corporations” and “Service delivery Crown corporations”',
    checked: '2026-10-22'
  },
  list: {
    title: 'Budget 2025, Budget and Fiscal Plan 2025/26–2027/28',
    url: 'https://www.bcbudget.gov.bc.ca/2025/pdf/2025_Budget_and_Fiscal_Plan.pdf',
    locator: 'Table 1.4, Revenue by Source, “Commercial Crown corporation net income” and note 6 (printed p. 23; PDF p. 33)',
    checked: '2026-10-22'
  }
}

export const CROWN_CATEGORIES = {
  commercial: {
    label: 'Commercial Crown corporation',
    plural: 'Commercial Crown corporations',
    definition: 'Delivers goods and services on a commercial, for-profit basis, and funds its operations and debt from what it earns in the market.'
  },
  'service-delivery': {
    label: 'Service delivery Crown corporation',
    plural: 'Service delivery Crown corporations',
    definition: 'Delivers goods and services based on government policy; most receive all or most of their funding from government.'
  }
}

/** The Crown corporations Budget 2025 counts as commercial, by the diagram's ids. */
export const COMMERCIAL_CROWNS = ['bc-hydro', 'bclc', 'icbc', 'columbia-power', 'bc-railway-company']

/** A Crown corporation's category in `year`, or null before the list's year or for any other body. */
export const crownCategoryOf = (node, year) => {
  if (node.kind !== 'crown-corporation' || year < CROWN_CATEGORIES_FROM) return null
  return COMMERCIAL_CROWNS.includes(node.id) ? 'commercial' : 'service-delivery'
}
