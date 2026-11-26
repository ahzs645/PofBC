import {
  educationProvinceBadge, educationProvinceFolder, educationProvinceNewspaper, educationProvinceReport,
  educationProvinceReportPdf, educationProvinceWordmark
} from './educationProvinceArtwork.js'

const sources = [
  {
    id: 'annual-report', title: 'Annual Report 1999/2000', shortTitle: 'Annual Report 1999/2000',
    url: educationProvinceReport, date: '1999/2000',
    description: 'Ministry of Advanced Education, Training and Technology. The Legislative Library of British Columbia holds the report, which covers the fiscal year ended March 31, 2000.'
  },
  {
    id: 'newspaper', title: 'The Similkameen News Leader, October 13, 1998', shortTitle: 'The Similkameen News Leader',
    url: educationProvinceNewspaper, date: '1998-10-13',
    description: 'The provincial advanced education advertisement is on page 9. The Princeton Museum digitized the issue.'
  },
  {
    id: 'petter-release', title: 'MacLean’s Magazine Poll Shows Investments in Universities Paying Off', shortTitle: 'Ministry news release AE28-98',
    url: 'https://archive.news.gov.bc.ca/releases/archive/pre2001/1998/nrae28-98.asp', date: '1998-11-16',
    description: 'Minister Andrew Petter tied university rankings to the province’s reputation for education and cited new student places and the tuition freeze.'
  },
  {
    id: 'throne-speech', title: 'Journals of the Legislative Assembly, Fifth Session of the 36th Parliament', shortTitle: 'Legislative Assembly Journals',
    url: 'https://lims.leg.bc.ca/pdms/ldp/36th5th/Journals%20-%205th%20Session%2C%2036th%20Parliament%20%282001%29%20-%20Protected.pdf',
    date: '2001', description: 'The March 14 throne speech set out the education goal. The March 20 proceedings record the tabling of the 1999/2000 annual report.'
  },
  {
    id: 'access-debate', title: 'Hansard, March 20, 2001, morning sitting', shortTitle: 'Hansard, March 20, 2001',
    url: 'https://lims.leg.bc.ca/hdms/file/Debates/36th5th/20010320am-Hansard-v22n5.htm', date: '2001-03-20',
    description: 'The first reading of the Access to Education Act also refers to B.C. as Canada’s education province.'
  },
  {
    id: 'new-era-report', title: '2001/02 Annual Report — A New Era Update', shortTitle: '2001/02 Annual Report',
    url: 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2001_2002/aved.pdf', date: '2001/02',
    description: 'The Ministry of Advanced Education’s report uses a new page design.'
  }
]

const annualRef = (page, locator) => ({
  sourceId: 'annual-report', page, locator, url: educationProvinceReportPdf + '#page=' + page
})
const newspaperRef = { sourceId: 'newspaper', page: 9, locator: 'Page 9, provincial advanced education advertisement' }

const watermark = {
  file: educationProvinceWordmark.file,
  displayId: educationProvinceWordmark.id,
  alt: 'Large BC initials beside the stacked words The Education Province',
  label: 'Original watermark',
  caption: 'The annual report watermark, printed at 5% Pantone 287 CVU.',
  evidenceType: educationProvinceWordmark.evidenceType,
  sourceId: 'annual-report', sourceUrl: educationProvinceWordmark.sourcePage, sourcePage: 9,
  sourceLocator: educationProvinceWordmark.sourceLocator,
  dateLabel: '1999/2000 fiscal-year report'
}

const derivative = (colour, label, description) => ({
  ...watermark,
  file: educationProvinceFolder + 'education-province-' + colour + '.svg',
  displayId: undefined,
  label,
  caption: description,
  evidenceType: 'derived-vector-presentation',
  downloadLabel: label.toLowerCase() + ' SVG'
})

const badgeImage = {
  file: educationProvinceBadge.file,
  width: 144, height: 126,
  alt: 'BC – The Education Province stacked in a dark circular badge',
  caption: 'Circular badge on the October 13, 1998 advanced education advertisement.',
  evidenceType: educationProvinceBadge.evidenceType,
  sourceId: 'newspaper', sourcePage: 9, sourceLocator: educationProvinceBadge.sourceLocator,
  date: '1998-10-13', dateLabel: 'Newspaper publication date'
}

const marks = [
  {
    id: educationProvinceWordmark.id, kind: 'campaign-wordmark', title: educationProvinceWordmark.label,
    description: 'Oversized BC initials sit beside three lines of lettering. On the report’s right-hand interior pages the wordmark is printed as a pale-blue watermark, alongside a publication design that also uses the provincial coat-of-arms signature.',
    artworkNote: '22 original vector paths',
    dateNote: 'The report documents the horizontal design. Its designer, launch date and retirement date remain unknown.',
    sourceRefs: [annualRef(9, 'PDF page 9 (printed page vii), right margin')],
    images: [
      watermark,
      derivative('solid-blue', 'Solid blue derivative', 'A modern presentation of the same outlines using the report’s full-strength blue ink.'),
      derivative('black', 'Black derivative', 'A modern monochrome presentation of the same outlines.')
    ]
  },
  {
    id: educationProvinceBadge.id, kind: 'campaign-badge', title: educationProvinceBadge.label,
    description: 'The 1998 advertisement sets the slogan on three lines in a dark circle next to its youth information phone number and website. The newspaper scan is the surviving artwork for this layout.',
    artworkNote: 'Newspaper scan',
    sourceRefs: [newspaperRef],
    image: badgeImage
  }
]

const timeline = [
  {
    id: 'charting-a-new-course', date: '1996', title: 'Access and affordability become policy priorities',
    description: 'The province’s Charting a New Course plan set goals for the college, university college and institute system. The tuition freeze and expanded student places became central to how the government promoted its post-secondary policy.',
    sourceRefs: [annualRef(16, 'PDF page 16, Charting a New Course'), annualRef(6, 'PDF page 6, report highlights')]
  },
  {
    id: 'newspaper-ad', date: '1998-10-13', title: 'The slogan appears in a Princeton newspaper',
    description: 'An advanced education advertisement carrying the circular badge promotes student aid and frozen tuition. It credits the Premier’s Youth Office and the Ministry of Advanced Education, Training and Technology.',
    sourceRefs: [newspaperRef]
  },
  {
    id: 'university-rankings', date: '1998-11-16', title: 'Andrew Petter links the slogan to university rankings',
    description: 'Petter cited the Maclean’s rankings alongside education spending, new places and the tuition freeze. The published source of the slogan itself remains uncertain.',
    sourceRefs: [{ sourceId: 'petter-release' }]
  },
  {
    id: 'annual-report-wordmark', date: '1999/2000', title: 'The ministry uses a horizontal wordmark',
    description: 'The fiscal-year report uses the tint in its interior page design. It describes the fourth year of frozen tuition, student financial assistance, research and technology investment, and options for youth.',
    sourceRefs: [annualRef(9, 'PDF page 9, table of contents and watermark'), annualRef(6, 'PDF page 6, report highlights')]
  },
  {
    id: 'throne-speech', date: '2001-03-14', title: 'The throne speech calls for B.C. to become the education province',
    description: 'The government framed education as an economic investment. The wording also appears at the March 20 first reading of the Access to Education Act, the day the ministry’s annual report was tabled.',
    sourceRefs: [{ sourceId: 'throne-speech', locator: 'March 14 throne speech and March 20 proceedings' }, { sourceId: 'access-debate' }]
  },
  {
    id: 'new-era-report', date: '2001/02', title: 'The ministry publishes a redesigned report',
    description: 'A New Era Update uses a different layout and drops the watermark from the pages reviewed. The campaign’s formal retirement date remains unknown.',
    sourceRefs: [{ sourceId: 'new-era-report', page: 9, locator: 'PDF page 9 (printed page 4), interior page design' }]
  }
]

const publications = [
  {
    id: 'similkameen-news-leader-1998', kind: 'newspaper-advertisement', title: 'Advanced education — making it better for you',
    description: 'The October 13, 1998 advertisement in The Similkameen News Leader pairs the circular Education Province badge with the provincial signature and the youth information service.',
    sourceRefs: [newspaperRef],
    image: {
      ...badgeImage, file: educationProvinceFolder + 'education-province-newspaper-ad.png',
      width: 902, height: 1058,
      alt: 'Advanced education newspaper ad with a youth information phone number, a website and the Education Province badge',
      caption: 'The advertisement as printed on page 9 of The Similkameen News Leader.'
    }
  },
  {
    id: 'ministry-annual-report-1999-2000', kind: 'annual-report', title: 'Annual Report 1999/2000',
    description: 'The ministry report documents the horizontal watermark and describes its work on post-secondary access, affordability, skills training and youth opportunities. It was tabled on March 20, 2001.',
    sourceRefs: [annualRef(9, 'PDF page 9 (printed page vii), wordmark'), { sourceId: 'throne-speech', locator: 'March 20 proceedings' }]
  },
  {
    id: 'ministry-annual-report-2001-02', kind: 'annual-report', title: '2001/02 Annual Report — A New Era Update',
    description: 'A later report from the renamed Ministry of Advanced Education provides a comparison for the publication design.',
    sourceRefs: [{ sourceId: 'new-era-report' }]
  }
]

export const educationProvinceDetail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  relatedLinks: [
    { label: 'Ministry of Advanced Education, Training and Technology', to: { view: 'government', node: entry.relatedBodyIds[0], year: 2000 } },
    { label: 'Industry Training and Apprenticeship Commission', to: { view: 'government', node: 'industry-training-and-apprenticeship-commission', year: 2000 } }
  ],
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'The Education Province marks', records: marks },
    { id: 'timeline', label: 'Timeline', type: 'timeline', title: 'The campaign in public records', records: timeline },
    { id: 'publications', label: 'Publications', type: 'publications', title: 'Advertising and annual reports', records: publications },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Sources and open questions',
      description: 'Earlier ministry reports and surviving Premier’s Youth Office materials may help date the designs and identify their designer.', records: sources }
  ]
})
