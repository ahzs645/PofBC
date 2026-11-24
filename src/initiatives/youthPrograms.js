import { ADVANCED_EDUCATION_1986, EDUCATION_1979, ENVIRONMENT_1988, SOCIAL_SERVICES_1986 } from './youthProgramsIndex.js'

const youthDebate = {
  id: 'youth-debate-1989', title: 'Debate on youth, May 12, 1989', shortTitle: 'B.C. Hansard',
  date: '1989-05-12', publisher: 'Legislative Assembly of British Columbia',
  url: 'https://lims.leg.bc.ca/hdms/file/Debates/34th3rd/34p_03s_890512a.htm#06750',
  note: 'Stan Hagen, Minister Responsible for Youth, described three programs and the work of the Youth Advisory Council.'
}
const debateRef = { sourceId: youthDebate.id, locator: 'p. 6750' }
const employerAd = {
  id: 'driftwood-1989-03-29', title: 'Challenge ’89 employer notice in the Gulf Islands Driftwood',
  shortTitle: 'Gulf Islands Driftwood', date: '1989-03-29', publisher: 'Gulf Islands Driftwood, via Salt Spring Archives',
  url: 'https://www.saltspringarchives.com/driftwood/1989/v30n13March29-1989A.pdf'
}
const federalChronology = {
  id: 'youth-unemployment-82-4e', title: 'Youth Unemployment in Canada, background paper 82-4E',
  publisher: 'Library of Parliament', shortTitle: 'Library of Parliament',
  url: 'https://publications.gc.ca/Pilot/LoPBdP/CIR/824-e.htm',
  note: 'The chronology records the federal announcement of January 27, 1989.'
}
const educationReport = {
  id: 'education-report-1990-91', title: 'B.C. Ministry of Education annual report, July 1990 to June 1991',
  publisher: 'Ministry of Education, via ERIC', date: '1990/91', shortTitle: 'Ministry of Education annual report',
  url: 'https://files.eric.ed.gov/fulltext/ED369660.pdf'
}
const ombudsmanReport = {
  id: 'ombudsman-report-1990', title: '1990 Annual Report of the Ombudsman',
  publisher: 'Office of the Ombudsman, British Columbia', date: '1990', shortTitle: 'Ombudsman annual report',
  url: 'https://bcombudsperson.ca/assets/media/1990-Annual-Report-of-the-Ombudsman-web.pdf'
}
const budgetDebate = {
  id: 'budget-speech-1989', title: '1989 budget speech', publisher: 'Legislative Assembly of British Columbia',
  date: '1989-03-30', shortTitle: 'B.C. budget speech',
  url: 'https://lims.leg.bc.ca/hdms/file/Debates/34th3rd/34p_03s_890330p.htm'
}

const government = (label, node, year) => ({ label, to: { view: 'government', node, year } })
// The atlas's 1989 snapshot shows the later ministry. Its 1988 snapshot opens the episode named in the ads.
const advancedEducation = government('Ministry of Advanced Education and Job Training', ADVANCED_EDUCATION_1986, 1988)
const adRef = { sourceId: employerAd.id, page: 22, locator: 'p. A22' }
const schoolsRef = { sourceId: educationReport.id, page: 33, locator: 'printed p. 34' }
const ombudsmanRef = { sourceId: ombudsmanReport.id, page: 48, locator: 'p. 48' }

const evidence = {
  'challenge-89': {
    sources: [employerAd, youthDebate, federalChronology],
    relatedLinks: [advancedEducation],
    timeline: [
      { id: 'challenge-federal-announcement', date: '1989-01-27', dateRole: 'federal announcement', title: 'Canada announces summer employment funding', description: 'The federal government announced $198.9 million for Challenge ’89 across Canada.', sourceRefs: [{ sourceId: federalChronology.id, locator: 'Chronology, January 27, 1989' }] },
      { id: 'challenge-employer-call', date: '1989-03-29', dateRole: 'advertisement', title: 'B.C. recruits employers', description: 'A provincial advertisement offered employers help with wages for new jobs and directed applications to the local Job Training Area Office.', sourceRefs: [adRef] },
      { id: 'challenge-bc-funding', date: '1989-05-12', dateRole: 'minister’s statement', title: 'Hagen describes the B.C. budget', description: 'Hagen put the federal contribution in B.C. at approximately $19 million and the provincial contribution at $10 million. He estimated that about 6,000 young people would find summer work.', sourceRefs: [debateRef] }
    ]
  },
  'passport-to-apprenticeship': {
    sources: [youthDebate, educationReport],
    relatedLinks: [advancedEducation, government('Ministry of Education', EDUCATION_1979, 1989)],
    timeline: [
      { id: 'passport-announced', date: '1989-02', dateRole: 'program announcement', title: 'Two ministries introduce a route into the trades', description: 'Hagen told the legislature in May that Advanced Education and Job Training and the Ministry of Education had announced the program in February. It offered workplace training for secondary-school students specializing in trades.', sourceRefs: [debateRef] },
      { id: 'passport-participation', date: '1990/91', dateRole: 'reported participation', title: 'Ninety students take part', description: 'The Ministry of Education’s annual report counted 90 participants. It described employers willing to train students who wanted to enter an apprenticeship.', sourceRefs: [schoolsRef] }
    ]
  },
  'environment-youth-corps': {
    sources: [budgetDebate, youthDebate, ombudsmanReport],
    relatedLinks: [government('Ministry of Environment', ENVIRONMENT_1988, 1989), government('Ministry of Social Services and Housing', SOCIAL_SERVICES_1986, 1990)],
    timeline: [
      { id: 'corps-budget', date: '1989-03-30', dateRole: 'budget announcement', title: 'Environmental youth employment enters the provincial budget', description: 'The budget speech assigned an environmental youth services program to the minister responsible for Environment. The Ombudsman subsequently dated the establishment of the Environment Youth Corps to 1989.', sourceRefs: [{ sourceId: budgetDebate.id }, ombudsmanRef] },
      { id: 'corps-first-target', date: '1989-05-12', dateRole: 'employment target', title: 'Environment plans work for young people', description: 'Hagen described a target of about 1,000 jobs in B.C. for people aged 16–24.', sourceRefs: [debateRef] },
      { id: 'corps-projects', date: '1990', dateRole: 'annual report', title: 'The Ombudsman reports more than 2,000 participants', description: 'The report counted about 350 projects, including fish and wildlife habitat work and recreation improvements. Environment and Social Services and Housing funded the program. The Corps provided payroll and training, while community sponsors supplied project ideas, tools and materials.', sourceRefs: [ombudsmanRef] }
    ]
  }
}

export const youthProgramDetail = (entry) => {
  const data = evidence[entry.id]
  const sections = [{ id: 'timeline', label: 'Timeline', type: 'timeline', title: 'Program history', records: data.timeline }]
  if (entry.id === 'challenge-89') {
    sections.push({
      id: 'advertisement', label: 'Advertisement', type: 'publications', title: 'The provincial employer notice',
      records: [{
        id: 'challenge-employer-ad-1989', title: 'B.C. employers', kind: 'newspaper-advertisement',
        description: 'The employer notice carries the diamond-shaped British Columbia Summer Employment Program emblem and identifies the issuing ministry in the footer.',
        image: {
          ...entry.cover, width: 691, height: 1331, date: employerAd.date, dateLabel: 'Advertisement publication',
          evidenceType: 'printed-source-crop', sourceId: employerAd.id, sourceUrl: employerAd.url, sourcePage: 22,
          sourceLocator: 'p. A22, lower right', sha256: '45528b01ab008916e346dc0c0e3a2d2de3b49ee821e022c3bb593d1cbf59768f'
        },
        sourceRefs: [adRef]
      }]
    })
  }
  sections.push({ id: 'sources', label: 'Sources', type: 'sources', title: 'Sources', records: data.sources })
  return {
    id: entry.id, title: entry.title,
    hero: { eyebrow: entry.subtitle, title: entry.title, description: entry.summary, image: entry.cover, caption: entry.cover?.caption },
    relatedLinks: [...data.relatedLinks, { label: 'BC Youth and the Youth Advisory Council', to: { view: 'initiatives', initiative: 'bc-youth' } }],
    sources: data.sources, sections
  }
}
