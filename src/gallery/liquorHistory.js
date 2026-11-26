// Dates on publications attest designs. Legislative dates describe the bodies' powers.
const source = (title, url) => ({ title, url })
const statute = (title, id) => source(title, 'https://free.bcpublications.ca/civix/document/id/hstats/hstats/' + id)
const order = (number) => source('Order in Council ' + number + '/1976', 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/' + number + '_1976')
const library = (title, handle) => source(title, 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/' + handle)
const law1921 = statute('Government Liquor Act, S.B.C. 1921, c. 30', '929176308')
const law1973 = statute('Government Liquor Amendment Act, S.B.C. 1973, c. 37', '787618959')
const licensingAct = statute('Liquor Control and Licensing Act, S.B.C. 1975, c. 38', '1305767717')
const distributionAct = statute('Liquor Distribution Act, S.B.C. 1975, c. 39', '706478044')
const centenary = source('BC Liquor Stores centenary, June 15, 2021', 'https://news.gov.bc.ca/releases/2021FIN0038-001103')
const hansard = source('Hansard, September 1, 1977, question 97', 'https://lims.leg.bc.ca/hdms/file/Debates/31st2nd/31p_02s_770901a.htm')
const rename = source('Provincial licensing announcement, July 5, 2018', 'https://news.gov.bc.ca/releases/2018AG0053-001343')
const retail2015 = source('Provincial wholesale pricing and internal separation', 'https://news.gov.bc.ca/releases/2014JAG0319-001743')
const cannabis = source('LDB 2018/19 annual report, cannabis operations', 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2018_2019/pdf/agency/ldb.pdf')
const oldDirective = source('Policy Directive 18-07, December 4, 2018', 'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/liquor-regulation-licensing/policy-directives/18-07_dormancy.pdf')
const newDirective = source('Policy Directive 21-20, October 4, 2021', 'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/liquor-regulation-licensing/policy-directives/21-20_-_extension_to_the_moratorium_on_new_licensee_retail_store_lrs_licences.pdf')
const signature2026 = source('BCLIQUOR fall 2026 retail guide, Signature stores', 'https://www.bcliquorstores.com/sites/default/files/flipbook/psr-fall-2026/index.html')
const signature = source('CIPO, BC Signature Liquor Store & Design, 0916319', 'https://ised-isde.canada.ca/cipo/trademark-search/916319')
const board = 'liquor-control-board'
const distribution = 'liquor-distribution-branch'
const licensing = 'liquor-control-and-licensing-branch'
const regulator = 'sub-liquor-and-cannabis-regulation-branch'
const appeals = 'british-columbia-liquor-board'
const governmentStores = 'government-liquor-stores'
const signatureStores = 'bc-signature-liquor-store'
const retail = 'sub-bcliquor'
const relation = (subject, type, label) => ({ subject, type, label })

export const LIQUOR_BOARD_COLLECTION = `collected-${board}`
export const LIQUOR_DISTRIBUTION_COLLECTION = `collected-${distribution}`

export const LIQUOR_SUCCESSION = [
  { from: board, to: distribution, type: 'services', date: '1976-12-31', note: 'Purchasing, distribution and government stores.', source: order(3494) },
  { from: board, to: licensing, type: 'services', date: '1976-12-31', note: 'Licensing and enforcement.', source: order(3490) },
  { from: licensing, to: regulator, type: 'renamed', date: '2018-07-05', note: 'The Province announced the new name and the addition of private cannabis retail licensing.', source: rename }
]

const addition = (id, name, kind, details) => ({
  id, name, label: name, kind, family: 'liquor-distribution',
  graphNode: null, aliases: [], collectionIds: [], salaryEmployers: [], priority: 2, scope: 'core',
  ...details
})

export const LIQUOR_SUBJECTS = [
  addition(licensing, 'Liquor Control and Licensing Branch', 'government-branch', {
    aliases: ['LCLB'], identityStatus: 'shared-identity',
    sources: [licensingAct, order(3490), hansard, rename, oldDirective],
    relations: [relation(board, 'received-operations-from', 'Regulatory succession'), relation(regulator, 'renamed-to', 'Name changed by July 5, 2018')],
    note: 'Section 2 of the 1975 Act created the licensing branch on December 31, 1976. It administered licences and enforcement, while the distribution branch ran the stores. A December 2018 directive still pairs the earlier branch heading with a provincial signature.',
    nextAction: 'Find dated regulator stationery from before the provincial sunburst.'
  }),
  addition(regulator, 'Liquor and Cannabis Regulation Branch', 'government-branch', {
    graphNode: regulator, aliases: ['LCRB'], identityStatus: 'shared-identity',
    sources: [rename, newDirective, source('Liquor Control and Licensing Act, S.B.C. 2015, c. 19', 'https://www.bclaws.gov.bc.ca/civix/document/id/lc/statreg/15019'), source('Cannabis Control and Licensing Act, S.B.C. 2018, c. 29', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/18029')],
    relations: [relation(licensing, 'renamed-from', 'Former licensing branch')],
    note: 'By July 5, 2018, the licensing branch had taken its new name and responsibility for licensing private non-medical cannabis retailers. Its 2021 directive displays the standard provincial signature alongside a separate branch heading.',
    nextAction: 'Compare additional regulatory forms for any branch-specific artwork.'
  }),
  addition(appeals, 'British Columbia Liquor Board', 'independent-board', {
    aliases: ['BC Liquor Board'], identityStatus: 'distinct-unconfirmed',
    sources: [law1973, licensingAct],
    relations: [relation(board, 'related-to', 'Appeals following the 1973 reorganization'), relation(licensing, 'related-to', 'Statutory appeals and hearings')],
    note: 'The 1973 amendments established an appeals board. Sections 32–34 of the 1975 licensing Act provided for a three-member British Columbia Liquor Board to hear appeals and hold directed hearings. The similarly named Liquor Control Board had operated stores.',
    nextAction: 'Locate an attributable appeals decision or letterhead carrying its own signature.'
  }),
  addition(governmentStores, 'Government liquor stores', 'service-brand', {
    identityStatus: 'distinct-unconfirmed', sources: [law1921, centenary, distributionAct],
    relations: [relation(board, 'operated-by', 'Original government store network'), relation(distribution, 'operated-by', 'Stores continued under the distribution statute'), relation(retail, 'related-to', 'Later provincial retail identities')],
    note: 'The first nine stores opened on June 15, 1921. Section 8 of the 1975 distribution Act provided for government stores, and section 26 continued the store managers and employees. The term identifies the retail operation.',
    nextAction: 'Locate dated early storefront signs or printed retail artwork.'
  }),
  addition(signatureStores, 'BC Signature Liquor Store', 'service-brand', {
    aliases: ['Signature Stores'], sources: [signature, signature2026, source('LDB 2007 service plan, retail strategy', 'https://www.bcbudget.gov.bc.ca/2007/sp/pdf/agency/bcldb.pdf')],
    relations: [relation(retail, 'part-of', 'Signature stores in the provincial liquor retail network'), relation(distribution, 'service-of', 'Operated by the distribution branch')],
    note: 'The general manager filed the Signature store design on November 24, 2004. The federal register dates public notice to March 23, 2005. The 2007 service plan describes existing Signature Stores. The retailer still used the store designation in its fall 2026 guide.',
    nextAction: 'Locate early store signage and date later versions of the Signature graphic.'
  })
]

export const LIQUOR_BOARD_RELATIONS = [
  relation(distribution, 'transferred-operations-to', 'Government stores, purchasing and distribution'),
  relation(licensing, 'transferred-operations-to', 'Licensing and enforcement'),
  relation(appeals, 'related-to', 'Separate appeals board')
]

const histories = {
  [LIQUOR_BOARD_COLLECTION]: [
    {
      id: 'lcb-formation', years: '1917–1922', label: 'From prohibition to government stores',
      note: 'Prohibition began on October 1, 1917. On October 20, 1920, voters chose government sale. The Government Liquor Act received assent on April 2, 1921. Nine government stores opened on June 15. The Board’s first annual report covers that opening through March 31, 1922. Its title page bears the provincial arms above the printer’s imprint.',
      sources: [source('Legislative Assembly, prohibition referendum', 'https://www.leg.bc.ca/learn/discover-your-legislature/1917-prohibition-begins-by-referendum'), law1921, centenary, library('First annual report, 1921/22', '242418')], marks: []
    }, {
      id: 'lcb-letterhead', years: '1941', label: 'The Board’s letterhead',
      note: 'The Board’s name and provincial coat of arms appear together on official letterhead dated November 14, 1941. The specimen comes from page 2 of the order, with a second impression on page 3. The Board’s 1950/51 report uses the provincial arms above the printer’s imprint.',
      sources: [source('Order in Council 1609/1941', 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1609_1941#page=2'), library('Thirtieth annual report, 1950/51', '242417')], marks: ['source-recovered-followup-liquor-control-board-letterhead-1941']
    }, {
      id: 'lcb-succession', years: '1973–1977', label: 'Stores, licensing and appeals',
      note: 'In 1973, the Province transferred Board powers to a general manager and established the British Columbia Liquor Board for appeals. The 1975 distribution and licensing Acts both received assent on June 26. Section 2 of each new Act came into force and the Government Liquor Act was repealed on December 31, 1976. Purchasing and the government stores continued under the Liquor Distribution Branch. Licensing and enforcement passed to the Liquor Control and Licensing Branch. Their budgets separated on April 1, 1977.',
      sources: [law1973, licensingAct, distributionAct, order(3490), order(3493), order(3494), hansard, centenary], marks: []
    }
  ],
  [LIQUOR_DISTRIBUTION_COLLECTION]: [
    {
      id: 'ldb-establishment', years: '1973–1977', label: 'From the Board to two branches',
      note: 'After the 1973 reforms, the Liquor Administration Branch kept the government stores running and the British Columbia Liquor Board heard appeals. The distribution and licensing Acts received royal assent on June 26, 1975. Their provisions establishing the two branches took effect on December 31, 1976. The Liquor Distribution Branch took over purchasing, distribution and the stores. The Liquor Control and Licensing Branch took over licensing and enforcement. Their budgets separated on April 1, 1977.',
      sources: [law1973, distributionAct, licensingAct, order(3494), order(3490), hansard, centenary], marks: []
    }, {
      id: 'ldb-script', years: '1998/99–2007', label: 'BCL script monogram',
      note: 'The earliest verified LDB artwork in this collection is the black-and-magenta script monogram in the 1998/99 annual report. Later reports place it beside the full branch name. The 2004 cover carries a red-L raster variant. A February 20, 2007 letter still uses the monogram during the year the stacked wordmark appeared in the service plan.',
      sources: [library('1998/99 annual report', '274295'), library('2001/02 annual report', '274302'), source('2004 service plan', 'https://www.bcbudget.gov.bc.ca/2004/sp/crownagency/bcldb.pdf'), source('February 2007 letter, FOI package p. 15', 'https://docs.openinfo.gov.bc.ca/Response_Package_JAG-2015-50638.pdf#page=15')], marks: ['liquor-bcl-1998-99','liquor-bcl-signature-2000-01']
    }, {
      id: 'ldb-stacked', years: '2007–2008', label: 'Corporate and retail names on one cover',
      note: 'The service plans print the red three-line corporate name beside the separate BC Liquor Stores wordmark. The latter belongs to the retail collection.',
      sources: [source('2007 service plan', 'https://www.bcbudget.gov.bc.ca/2007/sp/pdf/agency/bcldb.pdf'), source('2008 service plan', 'https://www.bcbudget.gov.bc.ca/2008/sp/pdf/agency/bcldb.pdf')], marks: ['liquor-stacked-2007']
    }, {
      id: 'ldb-slogan', years: '2009 and 2012', label: 'Provincial signature with slogan',
      note: 'The sunburst and The Best Place on Earth appear beside the stacked branch name in the 2009 service plan. The statements for the year ended March 31, 2012 carry a monochrome version.',
      sources: [source('2009 service plan', 'https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/bcldb.pdf'), library('2011/12 statements of financial information','309901')], marks: ['liquor-sunburst-slogan-2009']
    }, {
      id: 'ldb-divisions', years: '2015–2026', label: 'Retail, wholesale and cannabis',
      note: 'On April 1, 2015, the LDB separated its retail and wholesale operations under a common wholesale price. In 2018, the licensing branch became the Liquor and Cannabis Regulation Branch and took on private non-medical cannabis retail licensing. The LDB began cannabis wholesale and retail operations on October 17, 2018, opening a Kamloops store and launching online sales. A May 7, 2026 FAQ shows the provincial sunburst and stacked branch name without the earlier slogan.',
      sources: [retail2015, rename, cannabis, source('May 2026 refreshment beverage FAQ','https://www.bcldb.com/sites/default/files/2026-05/RegulatoryFAQ_RefreshmentBeverageDirectDelivery_7May2026.pdf')], marks: ['source-expanded-liquor-distribution-branch-wholesale-site-lockup']
    }
  ]
}

export function withLiquorHistory(collection) {
  const history = histories[collection.id]
  if (!history) return collection
  const eras = history.map(({ marks, ...era }) => ({
    ...era, entries: collection.entries.filter((entry) => marks.includes(entry.id))
  }))
  const placed = new Set(eras.flatMap((era) => era.entries))
  const additional = collection.entries.filter((entry) => !placed.has(entry))
  if (additional.length) eras.push({
    id: 'liquor-additional-specimens', label: 'Additional specimens', years: '',
    note: 'Each specimen records its own source and date.', entries: additional
  })
  if (collection.id === LIQUOR_BOARD_COLLECTION) return { ...collection, eras, showInGalleryIndex: false }
  return {
    ...collection, eras,
    intro: 'The Liquor Control Board opened British Columbia’s first nine government liquor stores in 1921. When the Province divided the Board’s former responsibilities, the Liquor Distribution Branch inherited purchasing, distribution and the stores. Licensing and enforcement went to a separate branch. The artwork dates below show when each design was documented.'
  }
}
