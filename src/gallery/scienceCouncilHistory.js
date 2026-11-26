import { ASI_ID, ASI_SOURCES } from './advancedSystemsInstitute.js'

const servicePlan = (year, agency) => ({
  title: `${year}/${String(year + 1).slice(2)} service plan`,
  url: `https://www.bcbudget.gov.bc.ca/${year}/sp/${year === 2003 ? 'crowncorps' : 'crownagency'}/${agency}.pdf`
})

const legislativeHistory = {
  title: 'Legislative history of the Innovate BC Act',
  url: 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96415tcb_01'
}
const rename2003 = {
  title: 'Council financial statements, 2003/04, note 1',
  url: 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2003-04/sup-e/innovation-science-council-fs-2003-04.pdf'
}

const launch = { ...servicePlan(2006, 'bcic'), title: 'BC Innovation Council service plan, Organizational Overview' }

export const COUNCIL_SUCCESSION = [
  {
    from: 'science-council-of-bc', to: 'bc-innovation-council', type: 'merger', date: '2004-10',
    note: 'The Innovation and Science Council of British Columbia merged with the Advanced Systems Institute of BC. The BC Innovation Council launched publicly in October 2004.',
    source: launch
  },
  {
    from: ASI_ID, to: 'bc-innovation-council', type: 'merger', date: '2004-10',
    note: 'ASI brought its technology funding, industry networks and mentoring programs to the new council.',
    source: launch
  },
  {
    from: 'bc-innovation-council', to: 'innovate-bc', type: 'legal-rename', date: '2018-03-15',
    note: 'The Province continued the BC Innovation Council under the name Innovate BC.',
    source: legislativeHistory
  }
]

export function withScienceCouncilHistory(collection) {
  if (collection.id !== 'collected-science-council-of-bc') return collection
  const earlier = 'source-recovered-science-council-2003'
  return {
    ...collection,
    graphYear: 2003,
    eras: [
      {
        id: 'science-council-original-name', years: '1978–March 2003', label: 'Science Council of British Columbia',
        note: 'Established in 1978 as a provincial Crown agency, the council funded research, helped companies commercialize technology and supported public science education.',
        sources: [servicePlan(2003, 'scbc')], entries: collection.entries.filter((entry) => entry.id === earlier)
      },
      {
        id: 'innovation-and-science-council', years: 'March 2003–October 2004', label: 'Innovation and Science Council of British Columbia',
        note: 'The council changed its legal name on March 12, 2003. Its 2004/05 service plan keeps the five-part emblem alongside the new name. The white cover signature and the teal-and-taupe contents-page version appear in the same publication.',
        sources: [rename2003, servicePlan(2004, 'iscbc')], entries: collection.entries.filter((entry) => entry.id === 'iscbc-2004')
      }
    ]
  }
}

const science = 'science-council-of-bc'
const bcic = 'bc-innovation-council'
const innovate = 'innovate-bc'
export const COUNCIL_TIMELINE_OWNERS = new Set([science, ASI_ID, bcic, innovate])

// Dates on publications record sightings. A name change or a merger has its own evidence.
export const COUNCIL_TIMELINE = [
  { date: '1978', title: 'Science Council of British Columbia established', owner: science, source: servicePlan(2003, 'scbc') },
  { date: '1986', title: 'Advanced Systems Institute founded', owner: ASI_ID, source: ASI_SOURCES.merger,
    note: 'ASI began as a separate nonprofit foundation working with researchers and technology companies.' },
  { date: 'March 2000', title: 'Square-and-triangles emblem at the ASI Exchange', owner: ASI_ID, source: ASI_SOURCES.exchange2000,
    note: 'The registration form shows a grey-and-black emblem above tall initials. The March 2003 Exchange guide prints this layout in black and magenta.',
    marks: ['asi-exchange-square'] },
  { date: 'May 2000', title: 'BC Advanced Systems Institute spells out its name', owner: ASI_ID, source: ASI_SOURCES.website2000,
    note: 'On the institute’s website, the three lines of the name step down beside the square emblem.', marks: ['asi-stepped-name'] },
  { date: 'December 2000', title: 'Square emblem over small, widely spaced initials', owner: ASI_ID, source: ASI_SOURCES.guidelines,
    note: 'The program guide’s PDF dates from December 2000. Its colour artwork identifies the emblem later used on the October 2002 letter.',
    marks: ['asi-letterhead'] },
  { date: 'June 2001', title: 'Fifteen years of ASI, 1986–2001', owner: ASI_ID, source: ASI_SOURCES.anniversary,
    note: 'ASI’s archived homepage shows the anniversary emblem in black and pink.', marks: ['asi-anniversary-web'] },
  { date: 'October 2002', title: 'ASI letterhead and anniversary signature', owner: ASI_ID, source: ASI_SOURCES.letter,
    note: 'The institute used its square emblem at the head of the letter and a separate fifteenth-anniversary design at the foot.',
    marks: ['asi-fifteen-years'] },
  { date: 'January 2003', title: 'ASI puts its initials beside the square', owner: ASI_ID, source: ASI_SOURCES.press,
    note: 'The January 14 Exchange announcement shows this horizontal version in magenta and black.', marks: ['asi-press-square'] },
  { date: 'March 2003', title: 'Science Council becomes the Innovation and Science Council of British Columbia', owner: science, source: rename2003,
    note: 'The 2003/04 plan shows the original name and tagline. The 2004/05 plan retains the emblem with the longer name.',
    marks: ['source-recovered-science-council-2003', 'iscbc-2004'] },
  { date: 'June–July 2003', title: 'ASI publishes the three-figure logo', owner: ASI_ID, source: ASI_SOURCES.newsletter,
    note: 'The June 23 board announcement carries the initials-only design. The July issue of LINX preserves its vector artwork.',
    marks: ['asi-nextphase'] },
  { date: 'November 2003', title: 'The full-name logo on ASI’s website', owner: ASI_ID, source: ASI_SOURCES.header,
    note: 'The web masthead adds “Advanced Systems Institute of BC” beneath the initials.', marks: ['asi-full-name-2004'] },
  { date: 'April 2004', title: 'Province announces the two partners will merge', owner: bcic, source: ASI_SOURCES.merger,
    note: 'The April 23 announcement names the Innovation and Science Council of British Columbia and the Advanced Systems Institute of BC.' },
  { date: 'June 2004', title: 'ASI’s three-figure identity in print', owner: ASI_ID, source: ASI_SOURCES.report,
    note: 'Rocket Builders credits ASI on June 25 using the full-name logo also seen in the institute’s November 2003 masthead.' },
  { date: 'October 2004', title: 'BC Innovation Council launches', owner: bcic, source: launch,
    note: 'The two organizations now operate together under the BC Innovation Council name.' },
  { date: 'March 2006', title: 'British Columbia Innovation Council becomes the statutory name', owner: bcic, source: legislativeHistory },
  { date: '2006/07–2007/08', title: 'BC Innovation Council with the loop emblem', owner: bcic,
    marks: ['bcic-orbit'], source: servicePlan(2006, 'bcic'),
    note: 'The 2006/07 plan shows the stacked short name in white. The 2007/08 plan shows it in colour.' },
  { date: '2008/09', title: 'Full name on a blue panel', owner: bcic, marks: ['source-recovered-bcic-2008-09'],
    source: { title: 'BCIC service plan, publication information', url: 'https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/bcic.pdf#page=2' } },
  { date: '2011/12–2012/13', title: 'BCIC initials replace the stacked name', owner: bcic, marks: ['bcic-horizontal-2011'],
    source: { title: '2011/12 BCIC service plan', url: 'https://www.bcbudget.gov.bc.ca/2011/sp/pdf/agency/bcic.pdf#page=2' } },
  { date: '2013/14 and 2017/18', title: 'Light-bulb logo on the council’s service plans', owner: bcic, marks: ['bcic-lightbulb-2013'],
    source: { title: '2013/14 BCIC service plan', url: 'https://www.bcbudget.gov.bc.ca/2013/sp/pdf/agency/bcic.pdf#page=1' } },
  { date: 'March 2018', title: 'BC Innovation Council becomes Innovate BC', owner: innovate, source: legislativeHistory },
  { date: 'July 2019', title: 'Innovate BC publishes its disc-and-wordmark logo', owner: innovate,
    source: { title: '2018/19 annual service plan report, published July 2019', url: 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2018_2019/pdf/agency/ibc.pdf#page=1' } },
  { date: '2024/25', title: 'Innovate BC impact report', owner: innovate, marks: ['innovate-bc-2024-colour'],
    note: 'The collected colour version uses a star-trail photograph inside the disc.',
    source: { title: '2024/25 impact report', url: 'https://www.innovatebc.ca/hubfs/Impact-Report_2024-2025_FINAL-PORTRAIT-1.pdf#page=1' } }
]
