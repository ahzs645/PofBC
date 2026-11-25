import { YOUTH_PROGRAMS } from './youthProgramsIndex.js'

// The index stays small: an initiative's sourced records are loaded only when it opens.
// The index card's cover sits on a light panel, so a logo made for a dark ground is shown there as
// the gallery's copy of its vector redrawn for a light page, not as the white file itself.
const gamesenseCover = {
  file: 'identity-display/source-recovered-gamesense-bclc-2025-reverse.light.svg',
  alt: 'GameSense capsule with the BCLC wordmark beneath',
  caption: 'BCLC’s 2025 retailer card, its white logo redrawn for a light ground'
}
const gamesenseLogo = {
  file: 'identity-recovered/gamesense/gamesense-reversed.png',
  alt: 'GameSense — white capsule logo',
  caption: 'The program’s logo as its website serves it, in white for a dark ground',
  darkBackground: true
}
const tourismCover = {
  file: 'tourism/marks/super-natural-canada-stacked-spot-2005.svg',
  alt: 'Super, Natural British Columbia Canada — published 2005 identity',
  caption: 'From the published 2005 graphic standards'
}

export const INITIATIVES = [
  {
    id: 'jepp', title: 'Joint Emergency Preparedness Program', subtitle: 'Federal–provincial cost sharing · 1980–2013',
    summary: 'JEPP helped provinces, territories and local governments fund emergency planning, training and equipment. British Columbia’s Provincial Emergency Program handled applications and claims.',
    cover: { file: 'initiatives/jepp/jepp-1993-cover.png', alt: 'Blue JEPP initials inside a screened square frame', caption: 'Cover of British Columbia’s revised July 1993 guidelines' },
    exploreLabel: 'Explore the 1993 guidelines and the two program marks',
    tags: ['Emergency preparedness', 'Program funding', 'Logos'],
    searchTerms: ['JEPP', 'PEP', 'Provincial Emergency Program', 'Emergency Preparedness Canada', 'Ministry of Attorney General']
  },
  {
    id: 'bc-youth', title: 'BC Youth', exploreLabel: 'Explore the youth grants, newspaper marks and ministry history', subtitle: 'Ministry of Advanced Education and Job Training',
    summary: 'Provincial youth grants, the Youth Advisory Council and the BC Youth mark that appeared in government advertisements.',
    cover: { file: 'identity-collected/bc-youth/right-flag.svg', alt: 'BC Youth wordmark and waving flag', caption: 'Reconstruction of the mark printed in October 1989' },
    tags: ['Youth grants', 'Logos', 'Timeline'],
    searchTerms: ['British Columbia Youth Advisory Council', 'The Next Step', 'Stanley B. Hagen', 'Minister Responsible for Youth', 'Youth Grants Program'],
    relatedBodyIds: ['bc-youth', 'bc-youth-advisory-council', 'ministry-of-labour-1976', 'ministry-of-advanced-education-and-job-training-1986']
  },
  ...YOUTH_PROGRAMS,
  {
    id: 'spirit-of-2010', title: 'Spirit of 2010', subtitle: 'Government of British Columbia',
    summary: 'British Columbia promoted tourism, trade and investment ahead of the Vancouver 2010 Olympic and Paralympic Winter Games. A framed Spirit of 2010 emblem appears in provincial and federal publications.',
    cover: { file: 'initiatives/spirit-of-2010/spirit-of-2010.svg', alt: 'Spirit of 2010 square campaign emblem', caption: 'Vector reconstruction of the colour emblem on the 2004 provincial resort strategy' },
    tags: ['Olympics', 'Logos', 'Tourism'],
    searchTerms: ['British Columbia. Be Here.', 'Spirit of 2010 Business Summit', 'Vancouver 2010', 'Olympic and Paralympic Winter Games Secretariat']
  },
  {
    id: 'tourism',
    title: 'Tourism',
    subtitle: 'Tourism BC · Destination BC',
    summary: 'Explore the websites, identities and campaigns that introduced British Columbia to the world, with the original artwork and records behind them.',
    cover: tourismCover,
    tags: ['Websites & apps', 'Logos & signs', 'Timeline', 'Publications'],
    searchTerms: [
      'Tourism BC', 'Tourism British Columbia', 'Destination BC', 'HelloBC',
      'hellobc.co.uk', 'SupernaturalBC.com', 'Super, Natural British Columbia',
      'Super Natural BC', 'SuperHost', 'WorldHost', 'Near Me BC', 'BC Escapes',
      'British Columbia Magazine', 'Share Your BC', 'Canada’s West',
      'Canada’s West Marketplace', 'Visitor Centre', 'Approved Accommodation',
      '100BCMoments', 'British Columbia Moments', 'Discover Camping',
      'Sun, sea and mountain', 'British Columbia Insider’s Guide'
    ],
    relatedBodyIds: ['tourism-bc', 'destination-bc']
  },
  {
    id: 'gamesense',
    title: 'GameSense',
    subtitle: 'British Columbia Lottery Corporation',
    summary: 'BCLC’s player health and responsible-gambling program, introduced in its casinos in 2009 and since licensed to lotteries and operators across North America.',
    cover: gamesenseCover,
    tags: ['Program', 'Logos', 'Timeline'],
    searchTerms: ['GameSense', 'Game Sense', 'BCLC', 'British Columbia Lottery Corporation', 'player health', 'responsible gambling', 'GameSense Advisor'],
    relatedBodyIds: ['bclc', 'gamesense']
  }
]

export const initiativesForBody = (id) => INITIATIVES.filter((initiative) => initiative.relatedBodyIds?.includes(id))

/** Lightweight metadata for a stable initiative ID, or null when it is unknown. */
export const initiativeById = (id) => INITIATIVES.find((initiative) => initiative.id === id) ?? null

const tourismDetail = (data) => {
  const heroImage = data.marks.flatMap((record) => record.images ?? [])
    .find((image) => image.id === 'super-natural-canada-stacked-spot-2005')
  return {
    id: 'tourism',
    title: 'Tourism',
    hero: {
      eyebrow: 'Tourism BC & Destination BC',
      title: 'Tourism, on screen\nand in print.',
      description: initiativeById('tourism').summary,
      image: heroImage ?? tourismCover,
      caption: tourismCover.caption
    },
    stats: [
      { value: data.digitalRecords.length, label: 'digital records' },
      { value: data.marks.length, label: 'identity records' },
      { value: data.domains.length, label: 'listed addresses' }
    ],
    sources: data.sources,
    domainNote: 'A listed address documents the name held in 2013; it does not establish a separate website or its launch date.',
    relatedLinks: [
      {
        label: 'Tourism BC & Destination BC corporate identities',
        to: { view: 'gallery', logos: 'tourism-bc-destination-bc' }
      },
      {
        label: 'Super, Natural welcome sign',
        to: { view: 'signs', sign: 'super-natural' }
      },
      {
        label: 'Tourism BC in government',
        to: { view: 'government', node: 'tourism-bc', year: 2009 }
      },
      {
        label: 'Destination BC in government',
        to: { view: 'government', node: 'destination-bc' }
      }
    ],
    sections: [
      {
        id: 'websites',
        label: 'Websites & apps',
        type: 'records',
        eyebrow: 'Digital collection',
        title: 'Websites, apps & campaigns',
        description: 'How British Columbia welcomed visitors online. Open a record for its specimens, dates and sources.',
        records: data.digitalRecords,
        featuredId: 'hellobc',
        searchable: true
      },
      {
        id: 'marks',
        label: 'Logos & signs',
        type: 'records',
        eyebrow: 'Visual identity',
        title: 'One family, many applications',
        description: 'Original vector specimens and printed references, connected to the services that used them.',
        notice: 'Read the specimen’s label. Native vector artwork, scanned source crops and names awaiting artwork retain their own evidence. A 2013 listing is not a design’s creation date.',
        records: data.marks,
        layout: 'marks'
      },
      {
        id: 'timeline',
        label: 'Timeline',
        type: 'timeline',
        eyebrow: 'Continuity & change',
        title: 'The brands and their custodians',
        description: 'Website launches, published specimens and organizational changes are different kinds of dates.',
        records: data.timeline
      },
      {
        id: 'publications',
        label: 'Publications',
        type: 'publications',
        eyebrow: 'Printed & moving images',
        title: 'Publications and creative work',
        description: 'Standards, guides and commissioning records connect the digital collection to its printed history.',
        records: data.publications,
        leads: data.leads
      },
      {
        id: 'sources',
        label: 'Sources & domains',
        type: 'sources',
        eyebrow: 'The evidence',
        title: 'A source for every record',
        description: 'The 2013 transfer order anchors this collection; later sources document the services and their changing appearance.',
        records: data.sources,
        inventory: {
          title: 'The 2013 address inventory',
          description: `${data.domains.length} listed entries, including aliases, technical hosts, duplicates and email addresses.`,
          entries: data.domains,
          sourceId: 'mo-68-2013',
          downloadTitle: 'Tourism BC 2013 address inventory',
          filename: 'tourism-bc-2013-address-inventory.json',
          dateLabel: 'As listed in 2013',
          matchingNote: 'spelling retained from the printed schedule'
        }
      }
    ]
  }
}

// GameSense is small enough to describe here: one held logo, its dated milestones and their sources.
// BCLC runs the program and owns the GAMESENSE mark; other organizations use it under licence, which
// does not make them part of BCLC or GameSense a body of its own.
const GAMESENSE_SOURCES = [
  {
    id: 'wla-gamesense-journey',
    title: 'Shaping tomorrow’s safer play: GameSense’s journey of continuous innovation (BCLC member news)',
    url: 'https://publications.world-lotteries.org/blog-posts/shaping-tomorrows-safer-play-gamesenses-journey-of-continuous-innovation',
    publisher: 'World Lottery Association',
    note: 'BCLC’s account: introduced to casinos in 2009, since extended to all its legal wagering including online; licensed to other gambling organizations, MGM Resorts the first commercial operator, in 2017.'
  },
  {
    id: 'globenewswire-connecticut-2016',
    title: 'BCLC’s GameSense adopted by Connecticut Lottery Corporation',
    url: 'https://www.globenewswire.com/news-release/2016/02/02/976435/0/en/BCLC-s-GameSense-Adopted-by-Connecticut-Lottery-Corporation.html',
    publisher: 'BCLC via GlobeNewswire',
    date: '2016-02-02'
  },
  {
    id: 'prnewswire-naspl-2020',
    title: 'BCLC offers free player health program to North American lottery jurisdictions',
    url: 'https://prnewswire.com/news-releases/bclc-offers-free-player-health-program-to-north-american-lottery-jurisdictions-300986935.html',
    publisher: 'BCLC via PR Newswire',
    date: '2020-01'
  },
  {
    id: 'uspto-gamesense',
    title: 'GAMESENSE, U.S. trademark serial 86625814, owner British Columbia Lottery Corporation',
    url: 'https://trademarks.justia.com/866/25/gamesense-86625814.html',
    publisher: 'USPTO record via Justia',
    note: 'Registered to BCLC. The Canadian record is not cited here.'
  },
  {
    id: 'gamesense-info-card-2025',
    title: 'GameSense Info Card, 2025',
    url: 'https://www.bclcretailerhub.com/content/dam/retailerhub/training/resources/GameSense_Info_Card-2025.pdf',
    publisher: 'BCLC Retailer Hub',
    date: '2025',
    note: 'BCLC’s card for its retailers; the endorsed logo below is its own vector artwork.'
  },
  {
    id: 'gamesense-website',
    title: 'GameSense website',
    url: 'https://www.gamesense.com/',
    publisher: 'British Columbia Lottery Corporation',
    note: 'The program’s public site, run by BCLC; the logo below is the file it serves.'
  }
]

const gamesenseDetail = () => ({
  id: 'gamesense',
  title: 'GameSense',
  hero: {
    eyebrow: 'A BCLC program',
    title: 'GameSense',
    description: initiativeById('gamesense').summary,
    image: gamesenseLogo,
    caption: gamesenseLogo.caption
  },
  stats: [
    { value: 2009, label: 'introduced in casinos' },
    { value: GAMESENSE_SOURCES.length, label: 'sources' }
  ],
  sources: GAMESENSE_SOURCES,
  relatedLinks: [
    { label: 'GameSense in the logo gallery', to: { view: 'gallery', logos: 'collected-gamesense' } },
    { label: 'BCLC’s logos', to: { view: 'gallery', logos: 'bclc' } },
    { label: 'BCLC in government', to: { view: 'government', node: 'bclc' } }
  ],
  sections: [
    {
      id: 'marks',
      label: 'Logo',
      type: 'records',
      eyebrow: 'Visual identity',
      title: 'The program’s logo',
      description: 'The logo held in the gallery, with its source. Licensees use the program’s identity under licence from BCLC.',
      layout: 'marks',
      records: [
        {
          id: 'gamesense-logo',
          title: 'GameSense logo',
          kind: 'program-identity',
          description: 'The capsule logo, in white for a dark ground: as the GameSense website serves it, and with BCLC’s endorsement on BCLC’s 2025 card for retailers. Collection and publication dates are not the logo’s adoption date.',
          images: [{
            id: 'source-recovered-gamesense-website',
            ...gamesenseLogo,
            width: 417,
            height: 93,
            evidenceType: 'official-published-website-image',
            sourceId: 'gamesense-website',
            sourceUrl: 'https://www.gamesense.com/',
            dateLabel: 'Website logo, collected 20 November 2026'
          }, {
            id: 'source-recovered-gamesense-bclc-2025-reverse',
            file: 'identity-recovered/gamesense/gamesense-bclc-2025-reverse.svg',
            alt: 'GameSense capsule with the BCLC wordmark beneath, in white',
            label: 'With BCLC’s endorsement, 2025 Info Card',
            darkBackground: true,
            evidenceType: 'native-pdf-vector-extraction',
            sourceId: 'gamesense-info-card-2025',
            sourceUrl: 'https://www.bclcretailerhub.com/content/dam/retailerhub/training/resources/GameSense_Info_Card-2025.pdf',
            sourcePage: 1,
            dateLabel: 'GameSense Info Card, 2025'
          }],
          sourceRefs: [{ sourceId: 'gamesense-website' }, { sourceId: 'gamesense-info-card-2025', page: 1 }],
          links: [{ label: 'Open in the logo gallery', url: '?view=gallery&logos=collected-gamesense' }]
        }
      ]
    },
    {
      id: 'timeline',
      label: 'Timeline',
      type: 'timeline',
      eyebrow: 'From one province to a continent',
      title: 'How the program spread',
      description: 'The program’s launch and the licences that took it beyond British Columbia.',
      records: [
        { id: 'gamesense-2009', date: '2009', dateRole: 'program launch', title: 'Introduced in BC casinos', description: 'BCLC introduces GameSense in its casinos, later extending it to lottery, sports and online play.', sourceRefs: [{ sourceId: 'wla-gamesense-journey' }] },
        { id: 'gamesense-2016', date: '2016-02-02', dateRole: 'announcement', title: 'Connecticut Lottery Corporation adopts it', description: 'A North American lottery takes the program under licence from BCLC.', sourceRefs: [{ sourceId: 'globenewswire-connecticut-2016' }] },
        { id: 'gamesense-2017', date: '2017', dateRole: 'licence', title: 'MGM Resorts, the first commercial operator', description: 'The first commercial gambling company in North America to adopt a program of this kind.', sourceRefs: [{ sourceId: 'wla-gamesense-journey' }] },
        { id: 'gamesense-2020', date: '2020-01', dateRole: 'announcement', title: 'Offered free to North American lotteries', description: 'BCLC makes the program available without charge to lottery jurisdictions in North America.', sourceRefs: [{ sourceId: 'prnewswire-naspl-2020' }] }
      ]
    },
    {
      id: 'sources',
      label: 'Sources',
      type: 'sources',
      eyebrow: 'The evidence',
      title: 'A source for every record',
      description: 'BCLC’s own accounts and announcements, the trademark record and the program’s website.',
      records: GAMESENSE_SOURCES
    }
  ]
})

// Literal imports let the bundler keep each initiative's data in its own deferred chunk.
const LOADERS = {
  jepp: async () => {
    const { jeppDetail } = await import('./jepp.js')
    return jeppDetail(initiativeById('jepp'))
  },
  ...Object.fromEntries(YOUTH_PROGRAMS.map((entry) => [entry.id, async () => {
    const { youthProgramDetail } = await import('./youthPrograms.js')
    return youthProgramDetail(entry)
  }])),
  'bc-youth': async () => {
    const { bcYouthDetail } = await import('./bcYouth.js')
    return bcYouthDetail(initiativeById('bc-youth'))
  },
  'spirit-of-2010': async () => {
    const { spiritOf2010Detail } = await import('./spiritOf2010.js')
    return spiritOf2010Detail(initiativeById('spirit-of-2010'))
  },
  gamesense: async () => gamesenseDetail(),
  tourism: async () => {
    const { TOURISM_COLLECTION } = await import('../gallery/tourismData.js')
    return tourismDetail(TOURISM_COLLECTION)
  }
}

/** Load an initiative's shared detail model; unknown IDs do not load any dataset. */
export const loadInitiative = async (id) => {
  if (!initiativeById(id)) return null
  return LOADERS[id]()
}
