import { rainforestGuide } from './tourismBrandGuides.js'

const guidelines = {
  id: 'industry-guidelines-2024',
  title: 'Rainforest to Rockies Industry Brand Guidelines',
  shortTitle: 'Industry brand guidelines',
  publisher: 'Destination BC',
  date: 'March 2024',
  url: 'https://www.destinationbc.ca/content/uploads/2024/03/Rainforest-to-Rockies-Industry-Brand-Guidelines.pdf',
  description: 'Destination BC’s 38-page guide for tourism partners. The supplied PDF matches the publisher’s copy and was created on March 5, 2024.'
}

const toolkit = {
  id: 'industry-toolkit-2024',
  title: 'Rainforest to Rockies Industry Brand Toolkit',
  shortTitle: 'Industry brand toolkit',
  publisher: 'Destination BC',
  date: 'March 2024',
  url: 'https://www.destinationbc.ca/content/uploads/2024/03/Rainforest-to-Rockies-Industry-Brand-Toolkit.pdf',
  description: 'The companion toolkit prints the primary logo and both partner colourways on page 5.'
}
const sources = [guidelines, toolkit]
const sourcePage = (page) => ({ sourceId: guidelines.id, page })

const specimens = (name, colour, alt, guidePage, darkBackground = false) => [
  { source: toolkit, page: 5, filename: name + '-toolkit', edition: 'Toolkit' },
  { source: guidelines, page: guidePage, filename: name, edition: 'Guidelines' }
].map(({ source, page, filename, edition }) => ({
  file: `initiatives/rainforest-to-rockies/${filename}.png`,
  label: `${colour} · ${edition}`, alt, darkBackground, sourceId: source.id, sourcePage: page,
  evidenceType: 'original-published-image', date: '2024-03', dateLabel: 'Publication date',
  caption: `${colour}. Embedded image from page ${page} of the ${source.shortTitle.toLowerCase()}, extracted with its original transparency mask.`
}))

const marks = [
  {
    id: 'primary-logo', title: 'Primary logo', kind: 'destination-brand',
    description: 'The Wander Mark sits beside the word “Rockies”. Its branches form a mountain peak and an upward arrow, tracing the climb from sea to sky.',
    images: specimens('primary-white', 'Spirit Bear White', 'White Rainforest to Rockies wordmark with a green tree and mountain symbol', 19, true),
    sourceRefs: [sourcePage(19)]
  },
  {
    id: 'partner-lockup', title: 'Third-party partner logo', kind: 'partner-identity',
    description: 'Partners could place this version beside their own branding. The line below the logo identifies British Columbia, Canada in Great Forest small caps.',
    images: [
      ...specimens('partner-canopy-green', 'Canopy Green', 'Green Rainforest to Rockies logo above British Columbia, Canada', 20),
      ...specimens('partner-white', 'Spirit Bear White', 'White Rainforest to Rockies logo above British Columbia, Canada', 20, true)
    ],
    sourceRefs: [sourcePage(20)]
  }
]

export const rainforestToRockiesDetail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  sections: [
    {
      id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'The Wander Mark',
      description: 'Destination BC’s industry guide shows the route’s own logo and a version that names the province and country for partner audiences.',
      records: marks
    },
    {
      id: 'publications', label: 'Brand guide', type: 'publications', title: 'Industry brand guidelines · March 2024', guide: rainforestGuide,
      records: [
        { id: 'brand-family', kind: 'brand-strategy', title: 'A route in the Super, Natural British Columbia family',
          description: 'Through its Invest in Iconics strategy, Destination BC worked with Indigenous Tourism BC, the provincial tourism ministry and regional tourism organizations. The guide identifies Rainforest to Rockies and The Great Wilderness as the first two named members of the expanded brand family.',
          sourceRefs: [sourcePage(4), sourcePage(5)] },
        { id: 'travel-corridor', kind: 'travel-routes', title: 'From the Pacific coast to the Canadian Rockies',
          description: 'Travellers can head north through Whistler toward Mount Robson, follow Highway 1 through Revelstoke to Yoho National Park, or take the southern route through Osoyoos and Cranbrook toward Fernie.',
          sourceRefs: [sourcePage(8)] },
        { id: 'brand-colours', kind: 'visual-identity', title: 'The route’s three greens',
          description: 'Lush Moss, Alpine Emerald and Canopy Green form the primary palette. Spirit Bear White and Orca Black come from the parent brand.',
          sourceRefs: [sourcePage(32), sourcePage(33)] }
      ]
    },
    { id: 'sources', label: 'Sources', type: 'sources', records: sources }
  ],
  relatedLinks: [
    { label: 'Super, Natural British Columbia’s 2021 brand guide', to: { view: 'initiatives', initiative: 'tourism', section: 'publications', record: 'our-brand-2021' } },
    { label: 'Super, Natural roadside welcome sign', to: { view: 'signs', sign: 'super-natural' } },
    { label: 'Destination BC in government', to: { view: 'government', node: 'destination-bc' } }
  ]
})
