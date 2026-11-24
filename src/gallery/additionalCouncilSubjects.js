// Official appointments, statutes and reports document these councils. Artwork is catalogued separately.
export const ADDITIONAL_COUNCIL_SUBJECTS = [
  {
    id: 'seniors-advisory-council',
    name: 'Seniors Advisory Council',
    family: 'specialist-health',
    aliases: ["Seniors' Advisory Council"],
    note: 'The 1989 Seniors Advisory Council Act established a council appointed by provincial Cabinet. It represented seniors across B.C., advised the responsible minister and reported at least annually. The Act was repealed on August 28, 2003.',
    sources: [
      { title: 'Seniors Advisory Council Act, 1989, sections 2–4', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/91consol15/91consol15/89037' },
      { title: 'Ministry of Health, 1998 council appointments', url: 'https://archive.news.gov.bc.ca/releases/archive/pre2001/1998/158.asp' },
      { title: 'BC Laws, effective date of repeal', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/consol40/consol40/96423_pit' }
    ],
    nextAction: 'Check the council’s annual reports to the minister for a dated letterhead or cover signature.'
  },
  {
    id: 'health-professions-council',
    name: 'Health Professions Council',
    family: 'regulators-administration',
    aliases: [],
    note: 'B.C.’s Health Professions Act established a Cabinet-appointed council to investigate applications for professional designation and advise the minister. Its 2001 Safe Choices report reviewed the regulation of health professions. The provisions establishing the council were repealed on December 31, 2002.',
    sources: [
      { title: 'Health Professions Act, 1990, sections 2–3', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/92consol16/92consol16/90050' },
      { title: 'Ministry of Health, release of the Safe Choices report, March 26, 2001', url: 'https://archive.news.gov.bc.ca/releases/archive/pre2001/2001/185.asp' },
      { title: 'BC Laws, repeal of Part 1 of the Health Professions Act', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/consol29/consol29/96183_pit' }
    ],
    nextAction: 'Inspect the original printed cover and title page of Safe Choices for a council signature.'
  },
  {
    id: 'advisory-council-children-youth-support-needs',
    name: 'Minister’s Advisory Council on Children and Youth with Support Needs',
    family: 'provincial-administration',
    aliases: ['CYSN MAC'],
    note: 'In 2021 the Ministry of Children and Family Development formed this council to advise on services for children and youth with support needs. The minister chaired it, with places for a youth representative, an Indigenous Elder, families and service organizations.',
    sources: [
      { title: 'Ministry of Children and Family Development, council remit and recruitment, January 2021', url: 'https://news.gov.bc.ca/releases/2021CFD0006-000146' },
      { title: 'Ministry of Children and Family Development, council membership and work since May 2021', url: 'https://news.gov.bc.ca/releases/2022CFD0023-001539' }
    ],
    nextAction: 'Look for dated council-issued meeting materials that show how members identified the council.'
  },
  {
    id: 'multicultural-advisory-council',
    name: 'Multicultural Advisory Council',
    family: 'provincial-administration',
    aliases: ['Advisory Council on Multiculturalism'],
    note: 'The Multiculturalism Act continued the Advisory Council on Multiculturalism under this name. Cabinet appointed its members to advise the minister. The Province’s final Report on Multiculturalism records the transfer of this work to the Provincial Committee on Anti-Racism.',
    sources: [
      { title: 'Multiculturalism Act, sections 4–5, 2022 consolidation', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/consol40/consol40/00_96321_01' },
      { title: 'Province of British Columbia, 2023/24 Report on Multiculturalism', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/multiculturalism-anti-racism/funding/2023-2024_report_on_multiculturalism.pdf' }
    ],
    nextAction: 'Check council correspondence under both statutory names for a dated identity specimen.'
  },
  {
    id: 'ministers-advisory-council-on-indigenous-women',
    name: 'Minister’s Advisory Council on Indigenous Women',
    family: 'provincial-administration',
    graphNode: 'sub-ministers-advisory-council-on-indigenous-women',
    aliases: ['MACIW'],
    note: 'The Minister of Indigenous Relations and Reconciliation appoints members to advise the Province on issues affecting Indigenous women. The council’s annual report records its work on Indigenous gender-based analysis and B.C.’s response to gender-based violence.',
    sources: [
      { title: 'Council terms of reference, June 2022', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/indigenous-people/aboriginal-peoples-documents/maciw_terms_of_reference_-_june_24_2022_-_final.pdf' },
      { title: 'Minister’s Advisory Council on Indigenous Women, 2022/23 annual report', url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/indigenous-people/aboriginal-peoples-documents/maciw_annual_report_2022-23.pdf' }
    ],
    nextAction: 'Review the annual report for a separately identifiable council mark and any artwork credit.'
  }
].map((subject) => ({
  kind: 'advisory-council', scope: 'core', priority: 2, graphNode: null,
  label: subject.name, collectionIds: [], salaryEmployers: [], relations: [],
  ...subject
}))
