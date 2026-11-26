const siferp = 'Southern Interior Forest Extension and Research Partnership'
const partnership = 'Forest Research Extension Partnership'
const forum = 'Forum for Research and Extension in Natural Resources'
const formerSociety = 'Southern Interior Extension and Research Society'
const finalSociety = 'FORREX Forum for Research and Extension in Natural Resources Society'
const gazette = 'https://www.bclaws.gov.bc.ca/civix/document/id/'

export const forrexSources = {
  establishment: { title: 'BC Gazette, July 30, 1998, society incorporations for July 13', url: 'https://free.bcpublications.ca/civix/document/id/bcgaz1/hbcgaz1/984555176' },
  annual2002: { title: 'FORREX 2001–2002 Annual Report, chair’s report, treasurer’s report and back cover', url: 'https://epe.lac-bac.gc.ca/100/201/300/ar_forrex/2001-02.pdf?nodisclaimer=1' },
  rename2002: { title: 'BC Gazette, August 15, 2002, society name changes for July 29', url: 'https://free.bcpublications.ca/civix/document/id/bcgaz1/hbcgaz1/1973788911' },
  contract: { title: 'FORREX, FII Forestry Research Extension Program final report, April 2003, pp. 1 and 10', url: 'https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=13390' },
  planning: { title: 'Putting Information to Work in British Columbia’s Natural Resource Sector, World Forestry Congress, 2003', url: 'https://www.fao.org/4/XII/0132-A1.htm' },
  account: { title: 'Ministry of Forests and Range, 2005/06 service plan report, Forest Investment Account appendix', url: 'https://www.bcbudget.gov.bc.ca/annual_reports/2005_2006/for/Appendices_%28Part_A%29.htm' },
  annual2009: { title: 'FORREX 2008–2009 Annual Report, message from the chair, p. 2', url: 'https://epe.lac-bac.gc.ca/100/201/300/ar_forrex/2008-09.pdf?nodisclaimer=1' },
  rename2008: { title: 'BC Gazette, August 7, 2008, society name changes for July 26', url: gazette + 'bcgaz1/bcgaz1/1788810484' },
  initiative: { title: 'Future Forest Ecosystems Initiative strategic plan, roles and responsibilities, pp. 8–9', url: 'https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/nrs-climate-change/applied-science/ffei_strategic_plan.pdf' },
  archive: { title: 'FORREX website archive', url: 'https://web.archive.org/web/*/http://www.forrex.org/' },
  forests: { title: 'The State of British Columbia’s Forests 2010, p. 236', url: 'https://www2.gov.bc.ca/assets/gov/environment/research-monitoring-and-reporting/reporting/envreportbc/archived-reports/sof_2010.pdf' },
  notice: { title: 'Registrar of Companies, November 19, 2015, intent to dissolve', url: gazette + 'corpreg/corpreg/soc1119soc0815' },
  dissolution: { title: 'Registrar of Companies, December 31, 2015, involuntary dissolutions for December 22', url: gazette + 'corpreg/corpreg/soc1231soc0415' },
}

// The same dated observation is displayed on the recipient and provider records.
const provider = (label, node, year) => ({ label, to: { view: 'government', node, ...(year && { year }) } })

export const earlyFunding = [
  { period: '1998–2001/02', recipient: 'SIFERP', role: 'Founding and operating funding',
    organizations: [provider('Forest Renewal BC', 'forest-renewal-bc', 2001)],
    note: 'Forest Renewal BC helped establish SIFERP in 1998 and provided annual funding. In the 2001/02 annual report, published under the FORREX name, the treasurer credited Forest Renewal BC with 40% of the partnership’s operating funds.', source: forrexSources.annual2002 },
  { period: '2001/02', recipient: 'SIFERP', role: 'Office and administrative support',
    organizations: [provider('Ministry of Forests', 'ministry-of-forests-1988', 2001), { label: 'Canadian Forest Service' }, provider('UBC', 'university-of-british-columbia')],
    note: 'The Ministry of Forests’ Research Branch agreed to provide office and administrative support for the coastal watershed program. The Canadian Forest Service offered the same support for socio-economics, and UBC for landscape and conservation biology.', source: forrexSources.annual2002 }
]

export const forrexFunding = [
  ...earlyFunding,
  { period: '2002/03', recipient: 'FORREX', role: 'Research extension contract',
    organizations: [provider('Forestry Innovation Investment', 'forestry-innovation-investment', 2003)],
    note: 'The Province funded research extension contract X2003-0100 through its Forestry Innovation Investment Program. FORREX brought the research to forest practitioners through workshops, publications and field tours.', source: forrexSources.contract },
  { period: '2005/06', recipient: 'FORREX', role: 'Provincial Forest Extension Program',
    organizations: [{ label: 'Forest Investment Account' }, provider('Ministry of Forests and Range', 'ministry-of-forests-and-range-2005', 2006)],
    note: 'The Ministry of Forests and Range identified FORREX as the provincial extension provider. The account recorded $1.25 million in actual spending on extension within the Forest Science Program.', source: forrexSources.account },
  { period: '2008', recipient: 'FORREX', role: 'Research extension partner',
    organizations: [{ label: 'Future Forest Ecosystems Initiative' }, provider('Ministry of Forests and Range', 'ministry-of-forests-and-range-2005', 2008)],
    note: 'The provincial plan assigned research priorities to the Forest Science Board and named FORREX as the partner responsible for sharing the findings with practitioners.', source: forrexSources.initiative }
]

const supportByProvider = new Map()
for (const { period, organizations, recipient, role, note, source } of forrexFunding) {
  const recipientLink = { label: recipient, to: { view: 'gallery', logos: 'collected-' + recipient.toLowerCase() } }
  for (const { to } of organizations) {
    if (!to) continue
    if (!supportByProvider.has(to.node)) supportByProvider.set(to.node, [])
    supportByProvider.get(to.node).push({ period, organizations: [recipientLink], role, note, source })
  }
}

export const supportProvidedBy = (id) => supportByProvider.get(id)

export const FORREX_RELATED_BODY = {
  id: 'forrex', name: finalSociety, shortName: 'FORREX', kind: 'charitable-society',
  aliases: ['SIFERP', siferp, partnership, forum, formerSociety, 'Forrex Forest Research Extension Society', 'S-0038583'],
  historical: true, checked: '2026-11-25',
  description: 'FORREX was an independent charitable society in Kamloops governed by its own board of directors. It delivered British Columbia’s Provincial Forest Extension Program. Its 2002/03 report counted 24 staff and 63 partners.',
  fundingHistory: forrexFunding,
  historyNote: 'Incorporated on July 13, 1998 as the Southern Interior Extension and Research Society (S-0038583), it worked under the name Southern Interior Forest Extension and Research Partnership (SIFERP). Its June 2002 annual report used Forest Research Extension Partnership. The registered name changed on July 29, 2002. In 2007/08 the board broadened the public name to Forum for Research and Extension in Natural Resources. The legal change followed on July 26, 2008. The registrar published an intent to dissolve on November 19, 2015 and recorded dissolution on December 22, 2015.',
  sources: Object.values(forrexSources),
  relationships: [
    { id: 'ministry-of-forests-1988', year: 2003, label: 'Ministry of Forests', description: 'Research and extension partner listed in the 2002/03 final report.' },
    { id: 'forest-renewal-bc', year: 2000, label: 'Forest Renewal BC', description: 'Founding and operating funder. The partnership also helped identify provincial research needs.' },
    { id: 'forestry-innovation-investment', year: 2003, label: 'Forestry Innovation Investment', description: 'FORREX delivered the 2002/03 forestry research extension contract.' },
    { id: 'university-of-british-columbia', label: 'University of British Columbia', description: 'Institutional partner listed in the 2002/03 final report.' }
  ],
  salaryEmployers: []
}
