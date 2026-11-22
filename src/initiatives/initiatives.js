// The index stays small: an initiative's sourced records are loaded only when it opens.
const tourismCover = {
  file: 'tourism/marks/super-natural-canada-stacked-spot-2005.svg',
  alt: 'Super, Natural British Columbia Canada — published 2005 identity',
  caption: 'From the published 2005 graphic standards'
}

export const INITIATIVES = [
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
  }
]

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

// Literal imports let the bundler keep each initiative's data in its own deferred chunk.
const LOADERS = {
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
