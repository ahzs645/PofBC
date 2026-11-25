const folder = 'initiatives/spirit-of-2010/'
const sources = [
  { id: 'resort', title: 'British Columbia Resort Strategy and Action Plan', publisher: 'Government of British Columbia', date: '2004', url: 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/natural-resource-use/all-seasons-resorts/actionplan.pdf' },
  { id: 'summit', title: 'British Columbia Tourism Strategy: Spirit of 2010, the Olympics and Beyond', publisher: 'Government of British Columbia · Legislative Library collection', date: '2004', url: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/307832' },
  { id: 'commerce', title: 'New Commerce Centre to help maximize 2010 opportunities', publisher: 'Office of the Premier', date: 'May 3, 2004', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2004OTP0036-000354.htm' },
  { id: 'trail', title: 'New “Spirit of 2010 Trail” launched to enhance tourism', publisher: 'British Columbia and Western Economic Diversification Canada', date: 'August 27, 2004', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2004sbed0034-000669.htm' },
  { id: 'playmaker', title: '2010 Business Opportunities: A Playmaker’s Guide', publisher: 'Government of Canada', date: '2006', url: 'https://publications.gc.ca/collections/collection_2023/isde-ised/iu4/Iu4-374-2006-eng.pdf' },
  { id: 'journal2004', title: 'Trade-marks Journal, volume 51, number 2593', publisher: 'Canadian Intellectual Property Office', date: 'July 7, 2004', url: 'https://publications.gc.ca/collections/Collection/RG42-2-51-2593.pdf' },
  { id: 'journal2014', title: 'Trade-marks Journal, volume 61, number 3112', publisher: 'Canadian Intellectual Property Office', date: 'June 18, 2014', url: 'https://cipo-opic.ic.gc.ca/opic-cipo/tmj/fra/18Jun2014.pdf?edition=06-18&year=2014' },
  { id: 'throne', title: 'Speech from the Throne, Fifth Session of the Thirty-Seventh Parliament', publisher: 'Legislative Assembly of British Columbia', date: 'February 10, 2004', url: 'https://lims.leg.bc.ca/pdms/ldp/37th5th/Throne_Speech_2004_5th_37th.pdf' },
  { id: 'debate', title: 'Debates of the Legislative Assembly, volume 25, number 16', publisher: 'Legislative Assembly of British Columbia', date: 'May 18, 2004', url: 'https://lims.leg.bc.ca/hdms/file/Debates/37th5th/20040518pm-Hansard-v25n16.htm' },
  { id: 'roads', title: 'Strategic Highway Infrastructure Program, Border Crossing Component, 2004/05 annual report', publisher: 'Canada–British Columbia Joint Management Committee', date: '2004–05', url: 'https://www2.gov.bc.ca/assets/gov/driving-and-transportation/reports-and-reference/reports-and-studies/planning-strategy-economy/transportation-reporting/provincial-federal/strategic-highway-infrastructure-fund/ship_ar_bcc-04-05.pdf' },
  { id: 'flag', title: 'Spirit of 2010 flag, observations by Dean McGee', publisher: 'Flags of the World', date: 'September 10, 2006', url: 'https://www.crwflags.com/fotw/flags/oly@w21.html' },
  { id: 'hockey', title: 'Ceremonial puck drop', publisher: 'Castanet · Rachael Kimola', date: 'March 21, 2008', url: 'https://www.castanetkamloops.net/news/Kelowna/38101/Ceremonial-puck-drop' },
  { id: 'ctf', title: 'CTF wants the Total Tally of Government Ads', publisher: 'Canadian Taxpayers Federation', date: 'January 17, 2005', url: 'https://www.taxpayer.com/news-room-archive/CTF%20wants%20the%20Total%20Tally%20of%20Government%20Ads%3A' }
]

export const spiritOf2010Detail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: 'Provincial promotional campaign', description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  relatedLinks: [{ label: 'Tourism campaigns and publications', to: { view: 'initiatives', initiative: 'tourism' } }],
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'The square emblem and the Business Summit lettering', records: [
      { id: 'square', title: 'Spirit of 2010 square', kind: 'campaign-identity',
        description: 'The frame encloses serif capitals, an italic “of” between rules, and four coloured numerals. The 2004 resort plan prints the rising-sun provincial signature separately on the same cover. The 2006 procurement handbook prints the square beside the B.C. Olympic and Paralympic Winter Games Secretariat credit.',
        artworkNote: 'Editable reconstruction with two dated reference images',
        dateNote: 'The earliest square verified here appears in 2004. Its designer, typeface and introduction date remain open.',
        images: [
          { file: folder + 'spirit-of-2010.svg', shortLabel: 'Reconstructed SVG', alt: 'Square Spirit of 2010 campaign emblem with blue, gold, green and red numerals', caption: 'Rebuilt from the 2004 cover using separate editable letterforms, rules and border.', evidenceType: 'vector-reconstruction', sourceId: 'resort', sourcePage: 1 },
          { file: folder + 'resort-strategy-2004.jpg', shortLabel: '2004 cover', alt: 'Colour square extracted from the resort strategy cover', caption: 'Original 200 × 201 pixel JPEG embedded in the front cover.', date: '2004', evidenceType: 'original-published-image', sourceId: 'resort', sourcePage: 1 },
          { file: folder + 'playmaker-2006.png', shortLabel: '2006 printing', alt: 'Screened monochrome printing of the square', caption: 'Native-resolution crop of the acknowledgements page in the digitized federal handbook.', date: '2006', evidenceType: 'printed-source-crop', sourceId: 'playmaker', sourcePage: 2 }
        ],
        links: [{ label: 'View the measured artwork overlays', url: (import.meta.env?.BASE_URL ?? '/') + folder + 'overlay.png' }],
        sourceRefs: [{ sourceId: 'resort', page: 1 }, { sourceId: 'playmaker', page: 2 }] },
      { id: 'summit-lettering', title: 'Unframed Business Summit lettering', kind: 'conference-identity',
        description: 'The summit presentation places “Business Summit” alongside a version with an open field around the type. Both the square border and the rules beside “of” are absent in this published arrangement.',
        image: { file: folder + 'business-summit-2004.png', alt: 'Spirit of 2010 lettering without the border or horizontal rules', caption: 'The original 400 × 375 pixel image embedded in the title slide. “Business Summit” is separate slide text.', evidenceType: 'original-published-image', sourceId: 'summit', sourceLocator: 'Title slide, PDF page 2 in the library copy', date: '2004' },
        sourceRefs: [{ sourceId: 'summit', locator: 'Title slide' }] }
    ] },
    { id: 'history', label: 'History', type: 'timeline', title: 'Promoting the province before the Games', records: [
      { id: 'speech', date: 'February 10, 2004', title: 'A tourism strategy for every region', description: 'The throne speech described provincial sport, arts, literacy and volunteer programs under the Spirit of 2010 heading and named an existing hockey tournament. The summit slides quote its commitment to spread the Games’ benefits across British Columbia.', sourceRefs: [{ sourceId: 'throne' }, { sourceId: 'summit', locator: 'Throne speech slide' }] },
      { id: 'business', date: 'May 3, 2004', title: 'Business opportunities', description: 'The Province announced the 2010 Commerce Centre and linked its strategies for tourism, investment, labour and procurement. The summit presentation lists “Be Here” as an international advertising campaign.', sourceRefs: [{ sourceId: 'commerce' }, { sourceId: 'summit', locator: 'Tourism investments slide' }] },
      { id: 'debate', date: 'May 18, 2004', title: 'Advertising debated in the Legislature', description: 'Opposition leader Joy MacPhail asked Premier Gordon Campbell about spending on the Spirit of 2010 advertising campaign. Campbell gave the wider advertising budget and said he had no spending breakdown for individual campaigns.', sourceRefs: [{ sourceId: 'debate' }] },
      { id: 'word-mark', date: 'July 7, 2004', title: 'The organizing committee’s use of the name', description: 'The Canadian Trade-marks Journal gave public notice that the Vancouver Organizing Committee for the 2010 Olympic and Paralympic Winter Games had adopted and used the words “SPIRIT OF 2010” as an official mark. The notice prints the words in plain capitals.', sourceRefs: [{ sourceId: 'journal2004', page: 274 }] },
      { id: 'trail', date: 'August 27, 2004', title: 'The Spirit of 2010 Trail', description: 'The Province and its partners used the name for a tourism trail. The announcement documents the name and the project.', sourceRefs: [{ sourceId: 'trail' }] },
      { id: 'resorts', date: '2004', title: 'British Columbia. Be Here.', description: 'The resort plan describes a national and international advertising campaign inviting people to invest, work and visit. Its cover provides the colour artwork for this reconstruction. The campaign wording appears in the text.', sourceRefs: [{ sourceId: 'resort', page: 5 }] },
      { id: 'signs', date: 'December 15, 2004', title: 'Proposed highway signage', description: 'The federal–provincial committee recorded B.C.’s commitment to prepare a Spirit of 2010 mock-up and discussed permission to use an Olympic logo. The minutes document a proposal.', sourceRefs: [{ sourceId: 'roads', page: 14 }] },
      { id: 'spending', date: 'January 17, 2005', title: 'Advertising expenditure challenged', description: 'The Canadian Taxpayers Federation criticized the campaign and reported a cost of more than $4 million based on freedom-of-information documents. This figure is the federation’s account.', sourceRefs: [{ sourceId: 'ctf' }] },
      { id: 'handbook', date: '2006', title: 'The square in procurement material', description: 'The federal handbook reproduces the square and describes the provincial Secretariat’s economic, cultural, sport and social work. It identifies VANOC as the organizing committee and Spirit of BC community committees as a separate network.', sourceRefs: [{ sourceId: 'playmaker', page: 2 }] },
      { id: 'flag', date: 'September 10, 2006', title: 'Sightings of a Spirit of 2010 flag', description: 'Dean McGee recorded seeing the flag in several locations. He described blue lettering and the four numerals in blue, yellow, green and red. Flags of the World preserves his eyewitness account.', sourceRefs: [{ sourceId: 'flag' }] },
      { id: 'hockey', date: 'March 21, 2008', title: 'The name on youth hockey souvenirs', description: 'Reporting from Kelowna, Rachael Kimola described a Spirit of 2010 hockey puck and a souvenir poster for registered players. The report documents the tournament name and merchandise.', sourceRefs: [{ sourceId: 'hockey' }] },
      { id: 'withdrawal', date: 'June 18, 2014', title: 'Withdrawal of the official word mark', description: 'The Trade-marks Journal published the organizing committee’s withdrawal of “SPIRIT OF 2010”. The notice concerns the words. The provincial publications preserve the square artwork.', sourceRefs: [{ sourceId: 'journal2014', page: 192 }] }
    ] },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Campaign publications and contemporary accounts', records: sources }
  ]
})
