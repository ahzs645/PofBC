const archive = 'https://archive.news.gov.bc.ca'
const early = archive + '/releases/archive/2001-2005/'
const late = archive + '/releases/news_releases_2005-2009/'
const library = 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/'
const cipo = 'https://ised-isde.canada.ca/cipo/trademark-search/'
const path = 'initiatives/achieve-bc/'
const references = (...ids) => ids.map((sourceId) => ({ sourceId }))
const source = (id, title, url, date) => ({ id, title, url, date })

const designs = [
  { number: 915357, id: 'bringing-out-the-best', title: 'Bringing Out the Best', detail: 'The original colour graphic places a golden sunburst above the V, with ACHIEVE in red, BC in blue and the slogan below.' },
  { number: 915352, id: 'celebration-of-excellence', title: 'A Celebration of Excellence', detail: 'A medal hangs from a ribbon in the shape of the V.' },
  { number: 915353, id: 'skills-and-learning', title: 'Skills & Learning', detail: 'A computer monitor frames the V above the words SKILLS & LEARNING.' },
  { number: 915354, id: 'jobs-and-opportunities', title: 'Jobs & Opportunities', detail: 'The computer-monitor emblem also appears over the separate JOBS & OPPORTUNITIES legend.' },
  { number: 915355, id: 'education', title: 'Education', detail: 'An open book forms the V. The Ministry of Education’s 2004 Grad Planner preserves the coloured lettering and the photographed book.' }
]

const sources = [
  source('launch', 'Office of the Premier · New initiative to help British Columbians achieve goals', early + '2003OTP0081-000837.htm', 'September 19, 2003'),
  source('background', 'Office of the Premier · Achieve BC initiative backgrounder', early + '2003OTP0081-000837-Attachment1.htm', 'September 19, 2003'),
  source('journal', 'Trade-marks Journal, vol. 50, no. 2560, printed pages 311–312', 'https://epe.lac-bac.gc.ca/100/202/301/trade_marks_jrn-ef/2003/031119.pdf?nodisclaimer=1', 'November 19, 2003'),
  ...designs.map(({ number, title }) => source('cipo-' + number, 'CIPO · ' + number + ' · ' + title, cipo + number, 'Filed September 11, 2003')),
  source('cipo-915356', 'CIPO · 915356 · ACHIEVE BC word mark', cipo + '915356', 'Filed September 11, 2003'),
  source('driftwood', 'Gulf Islands Driftwood · With every step, we reach higher', 'https://saltspringarchives.com/driftwood/2003/v43n39ASept24-2003.pdf', 'September 24, 2003'),
  source('tour', 'Simon Fraser University Communiqué · My Co-op Adventure Around the Province', 'https://www.sfu.ca/communique/pdfs/Communique_Summer2004.pdf', 'Summer 2004'),
  source('literacy', 'Ministry of Education · Improving literacy no. 1 priority for school districts', early + '2004BCED0007-000110.htm', 'February 23, 2004'),
  source('estimates', 'Legislative Assembly · Ministry of Education estimates, pages 10189–90', 'https://lims.leg.bc.ca/hdms/file/Debates/37th5th/20040419pm-Hansard-v23n7.htm', 'April 19, 2004'),
  source('spaces', 'Ministry of Advanced Education · Prince George post-secondary spaces announcement', early + '2004mae0030-000462.pdf', 'June 4, 2004'),
  source('grad', 'Ministry of Education · Grad Planner, 2004 Graduation Program', library + '310162', '2004'),
  source('reading', 'Reading for Families · Kindergarten–Grade 1, Surrey Schools copy', 'https://media.surreyschools.ca/media/Default/medialib/reading-for-families.8c021722251.pdf', 'September 2005'),
  source('library-reading', 'Legislative Library of British Columbia · Reading for Families', library + '314000', '2005'),
  source('awards', 'Ministry of Advanced Education and Office of the Premier · Premier’s Excellence Awards backgrounder', late + '2006ae0001-000002-attachment1.pdf', 'January 28, 2006'),
  source('sizes', 'Ministry of Education · Report shows progress on class sizes', late + '2006EDU0002-000022.htm', 'February 9, 2006'),
  source('september', 'Ministry of Advanced Education · The facts about post-secondary education in B.C.', late + '2006ae0039-001082.pdf', 'September 6, 2006'),
  source('fall-news', 'Legislative Library · Achieve BC eNewsletter, Fall 2003', library + '310174', 'Fall 2003'),
  source('spring-news', 'Legislative Library · Achieve BC eNewsletter, issue 11', library + '310163', 'Spring 2007'),
  source('tips', 'Ministry of Education · Back to school tips to help students succeed', late + '2008EDUC0098-001279.htm', 'August 22, 2008'),
  source('archive', 'Province of British Columbia · Achieve BC news archive, 2005–2009', archive + '/archive/2005-2009/default.aspx?theme_obj_id=0800921e80010c4a', 'Latest indexed entries April 8, 2009'),
  source('guardian', 'Hospital Employees’ Union · The Guardian, fall 2004, back cover', 'https://www.heu.org/sites/default/files/uploads/resource/2004/10/15/04_Guardian_3Fall.pdf', 'Fall 2004'),
  source('tyee', 'The Tyee · “Achieve BC” Ads Don’t Add Up, opinion', 'https://thetyee.ca/Views/2004/10/07/BCAchiveAdsSuspect/', 'October 7, 2004'),
  source('budget', 'Canadian Taxpayers Federation · A Taxpayers Budget, committee submission', 'https://www.taxpayer.com/media/Budget%20submission%202007%20final.pdf', 'October 2006')
]

const specimen = (file, label, alt, sourceId, date, evidenceType, provenance = {}) => ({
  file: path + file, label, shortLabel: label, alt, sourceId, date, evidenceType, ...provenance
})

const records = designs.map(({ number, id, title, detail }) => {
  const sourceId = 'cipo-' + number
  const docket = specimen('official-mark-' + number + '.png', 'Official mark ' + number, 'Achieve BC — ' + title + ', monochrome design in the CIPO record',
    sourceId, '2003-11-19', 'original-published-image', { sourceImageUrl: cipo + 'media/' + number + '.png', dateLabel: 'Public notice' })
  return {
    id, title, kind: 'campaign-identity', description: detail,
    images: [docket],
    registrations: [{ territory: 'Canada', type: 'official mark', number }],
    sourceRefs: [{ sourceId }, { sourceId: 'journal', page: number <= 915354 ? 314 : 315 }]
  }
})

const umbrella = records.find((item) => item.id === 'bringing-out-the-best')
umbrella.images.unshift(specimen('bringing-out-the-best-2004.gif', '2004 government GIF', 'Red and blue Achieve BC wordmark with a golden sunburst over its V and Bringing Out the Best below',
  'literacy', '2004-02-23', 'official-published-website-image', { sourceImageUrl: early + '2004BCED0007-000110_files/image003.gif' }))
umbrella.images.push(
  specimen('driftwood-2003.png', '2003 newspaper', 'Sunburst and slogan in the newspaper advertisement', 'driftwood', '2003-09-24', 'printed-source-crop', { sourcePage: 17, sourceLocator: 'Page A17, bottom of the advertisement' }),
  specimen('bringing-out-the-best-2006.jpg', '2006 government JPEG', 'Colour sunburst and slogan on the class-size announcement', 'sizes', '2006-02-09', 'official-published-website-image', { sourceImageUrl: late + '2006EDU0002-000022_files/image004.jpg' })
)
umbrella.sourceRefs.push(...references('literacy', 'sizes'), { sourceId: 'driftwood', page: 17 })

const education = records.find((item) => item.id === 'education')
education.images.unshift(specimen('education-2004.svg', 'Grad Planner colour SVG', 'Red and blue Achieve BC with an open book replacing its V and EDUCATION below',
  'grad', '2004', 'mixed-pdf-artwork', { downloadLabel: 'source SVG', sourcePage: 2, sourceLocator: 'Front cover, PDF page 2 of Legislative Library copy' }))
education.sourceRefs.push({ sourceId: 'grad', page: 2 }, { sourceId: 'tour', page: 1 })
records.push({
  id: 'sun-and-mountains', title: 'Sun and mountains', kind: 'publication-identity',
  description: 'The 2005 Reading for Families cover pairs the provincial sun-and-mountains emblem with serif lettering. Achieve is blue and BC is gold. The ministry continued to publish the original sunburst in 2006.',
  images: [specimen('sun-and-mountains-2005.svg', 'Reading for Families SVG', 'Provincial sun over blue mountains followed by AchieveBC in blue and gold',
    'reading', '2005-09', 'native-pdf-vector-extraction', { sourcePage: 1, sourceLocator: 'Front cover, bottom centre' })],
  sourceRefs: [{ sourceId: 'reading', page: 1 }, { sourceId: 'library-reading' }, { sourceId: 'september', page: 1 }]
})

const event = (id, date, title, description, ...ids) => ({ id, date, title, description, sourceRefs: references(...ids) })
const history = [
  event('filing', 'September 11, 2003', 'The province files six official marks', 'The province, represented by the Premier, filed the ACHIEVE BC name and five designs. The four themed designs change the V and its accompanying words.', 'cipo-915356', 'cipo-915357', 'journal'),
  event('launch', 'September 19, 2003', 'A single place to find learning and career advice', 'Premier Gordon Campbell launched Achieve BC for families, students, workers and entrepreneurs. Fourteen publications, a website, an email newsletter, exhibits and ten Enquiry BC telephone operators offered advice from early childhood through employment and starting a business.', 'launch', 'background'),
  event('newspaper', 'September 24, 2003', 'The sunburst reaches the newspapers', 'The Gulf Islands Driftwood printed the province’s “With every step, we reach higher” advertisement. It carries both the Achieve BC sunburst and the provincial coat of arms.', 'driftwood'),
  event('notice', 'November 19, 2003', 'The designs appear together in the Trade-marks Journal', 'Pages 311–312 give public notice of adoption and use of five graphic marks and one word mark. The designs belong to one campaign family.', 'journal'),
  event('responsibility', 'April 19, 2004', 'Education’s minister explains his ministry’s part', 'In legislative estimates, Tom Christensen described Achieve BC as a cross-government initiative. Education helped develop the K–12 booklet. He told the legislature that the campaign’s advertising was funded outside his ministry.', 'estimates'),
  event('exhibit', '2003–June 2004', 'Seven people take the exhibition to schools and malls', 'Tour member Sharon Roberts described nine months on the road visiting more than 40 communities. Her account pictures an Achieve BC Education exhibition sign.', 'tour'),
  event('education-uses', '2004', 'Ministries use the identity in print', 'The Education wordmark appears on the Grad Planner. The sunburst accompanied school district literacy targets and the announcement of 600 new spaces at UNBC and 400 at the College of New Caledonia.', 'grad', 'literacy', 'spaces'),
  event('advertising', 'Fall 2004', 'The advertising draws criticism', 'An opinion article in The Tyee questioned the campaign’s claims about employment growth. The Hospital Employees’ Union used “Deceive BC” in its own campaign.', 'tyee', 'guardian'),
  event('signature', 'September 2005', 'Reading for Families carries a second signature', 'The family reading guide uses the provincial sun-and-mountains emblem beside AchieveBC.', 'reading', 'library-reading'),
  event('overlap', 'January–September 2006', 'Government continues to publish the original sunburst', 'The Premier’s Excellence Awards backgrounder, the February class-size release and a September fact sheet on post-secondary education carry Bringing Out the Best.', 'awards', 'sizes', 'september'),
  event('spending', 'October 2006', 'A budget submission reports the advertising cost', 'The Canadian Taxpayers Federation listed $2.481 million for Achieve BC in its table of provincial public affairs advertising for fiscal 2004/05, on page 24 of its submission.', 'budget'),
  event('newsletters', 'Spring 2007', 'The newsletter reaches issue 11', 'The Legislative Library preserves both the fall 2003 newsletter and issue 11 from spring 2007.', 'fall-news', 'spring-news'),
  event('school-tips', 'August 22, 2008', 'Back-to-school advice points families to AchieveBC.ca', 'The Ministry of Education directed families to the website for planning and career advice.', 'tips'),
  event('archive-ends', 'April 8, 2009', 'Latest entries in the Achieve BC news index', 'The province’s archive indexes 701 releases under the Achieve BC theme. Its latest entries are dated April 8, 2009. The formal closure date and the date the website went offline remain unknown.', 'archive')
]

export const achieveBCDetail = (entry) => ({
  id: entry.id, title: entry.title,
  hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  sources,
  relatedLinks: [
    { label: 'Premier of British Columbia in 2003', to: { view: 'government', node: 'premier', year: 2003 } },
    { label: 'Ministry of Education in 2004', to: { view: 'government', node: 'ministry-of-education-1998', year: 2004 } }
  ],
  sections: [
    { id: 'marks', label: 'Logos', title: 'Five 2003 designs and a 2005 publication signature', type: 'records', layout: 'marks', records, featuredId: umbrella.id, description: 'The federal official-mark notices identify the province as the owner. The designer and the advertising agency have yet to be identified.' },
    { id: 'history', label: 'History', title: 'Achieve BC in print, online and on the road', type: 'timeline', records: history },
    { id: 'related', label: 'Related artwork', title: 'The union’s response', type: 'records', records: [{
      id: 'deceive-bc', title: 'Deceive BC', kind: 'union-parody', description: 'The Hospital Employees’ Union adapted the sunburst and wordmark under the slogan “Promises Made. Promises Broken.” Its fall 2004 Guardian printed the graphic on the back cover.',
      images: [specimen('deceive-bc-2004.png', 'Guardian back cover', 'Deceive BC sunburst and Promises Made. Promises Broken.', 'guardian', '2004', 'printed-source-crop', { sourcePage: 17 })],
      sourceRefs: [{ sourceId: 'guardian', page: 17 }]
    }] },
    { id: 'sources', label: 'Sources', title: 'Official marks, publications and contemporary accounts', type: 'sources', records: sources }
  ]
})
