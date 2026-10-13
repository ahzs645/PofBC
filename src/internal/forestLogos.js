// History comments distinguish a pictured badge, related uses and an adoption date.
// Forest Oval provides the artwork; PofBC's existing research provides the dated context.
const forestOval = {
  title: 'Forest Oval reference collection',
  url: 'https://projects.ahmadjalil.com/forestoval/'
}

const forestServiceTimeline = {
  title: 'BC Forest Service Centenary Society · BC Forest Service timeline',
  url: 'https://bcfs100.for.gov.bc.ca/bscripts/timeline.asp'
}

// The posters that carry the evergreen emblem, as places in the Posters view.
const onPoster = (poster, title, note) => ({ title, note, to: { view: 'posters', poster, part: 'emblem' } })

export const FOREST_LOGOS = [
  {
    id: 'forest-service-emblem',
    kind: 'drawing',
    artwork: 'forest-service-emblem.svg',
    padding: '12%',
    name: 'Forest Service evergreen emblem',
    description: 'A dark evergreen over a white map of the province, on a rounded green badge.',
    evidence: 'Before about 1973 · dating unconfirmed',
    comments: [
      'The British Columbia Forest Service’s mark before the oval designs: the mainland and its three largest islands in white, with a geometric evergreen standing over the mainland’s eastern edge, on a badge whose sides bow gently outward.',
      'It is believed to have been in use until about 1973. No source in this collection yet confirms that date, or when the emblem was introduced; it is recorded here as the working date, to be replaced when a dated document turns up.',
      'In the emblem’s last years the Forest Service sat within the Department of Lands, Forests and Water Resources (1962–1976). The Department of Forests was separated from it in 1976, and the Ministry of Forests Act came into force on 1 January 1979.',
      'The artwork is a vector reconstruction from a supplied image: seven shapes (the badge, the mainland, three islands, the crown and the trunk) with flat colours chosen from the image, not verified ink specifications. The same drawing is used on both Forest Service posters in the Posters view.'
    ],
    sources: [forestServiceTimeline],
    seenOn: [
      onPoster('reward-living-forest', 'REWARD: A Living Forest', 'Campfire poster · bottom right, beside the service’s name'),
      onPoster('enjoy-protect-forests', 'Enjoy & Protect our Forests', 'Sign · bottom right, beside the service’s name')
    ]
  },
  {
    id: 'forests',
    name: 'Forests',
    description: 'The wildlife oval with the short Forests name.',
    evidence: 'Adoption date unverified',
    comments: [
      '“BRITISH COLUMBIA” and “FORESTS” surround the wildlife scene: an eagle, trees, a deer, mountains and a fish over water. The long ministry-name oval uses the same scene.',
      'Forest Oval retains a supplied vector reference and a raster specimen for this design. Those references establish its appearance; they do not establish when it was introduced or retired.'
    ],
    sources: [forestOval]
  },
  {
    id: 'long-ministry',
    name: 'Long ministry name',
    description: 'Forests, Lands and Natural Resource Operations.',
    evidence: 'Related uses documented in 2017–2022',
    comments: [
      'This version keeps the wildlife scene and wraps “Forests, Lands and Natural Resource Operations” around the lower oval. The ministry held that name from 2011 to 2017; its naming period does not establish the badge’s adoption date.',
      'PofBC’s research records this oval family beside BCTS on business-plan covers for 2017/18 through 2021/22. A version with a Wildfire Service ribbon is also documented in June 2021. These are related uses, rather than a verified lifespan for this standalone badge.',
      'The Forest Oval reconstruction of this standalone version was fitted to a small raster reference.'
    ],
    sources: [
      {
        title: 'BC Archives ministry history diagram',
        url: 'https://bcarchives.ca/wp-content/uploads/sites/2/2026/01/BC-Government-Ministry-History-Diagram.pdf'
      },
      {
        title: 'BCTS business plan 2017/18–2019/20 · cover',
        url: 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bp-201718-201920.pdf'
      },
      {
        title: 'BCTS business plan 2021/22–2023/24 · cover',
        url: 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bcts-business-plan_2021-22-to-2023-24.pdf'
      },
      {
        title: 'Wildfire Service ribbon version · June 2021',
        url: 'https://www.e-know.ca/regions/east-kootenay/wildfire-reported-southwest-of-canal-flats/attachment/bc-wildfire-service-logo/'
      },
      forestOval
    ]
  },
  {
    id: 'forest-service',
    name: 'Forest Service',
    description: 'The tree oval with diamond separators.',
    evidence: 'Adoption date unverified',
    comments: [
      '“FOREST SERVICE” and “BRITISH COLUMBIA” frame a single conifer and mountain landscape. Diamond separators and heavier lettering distinguish this design from the two wildlife ovals.',
      'Forest Oval retains a supplied vector reference for this tree oval. PofBC’s BCTS research also records a related round Forest Service tree badge on archived sites from 2005 to 2017. That related badge does not establish the introduction or retirement of this exact oval.'
    ],
    sources: [
      forestOval,
      {
        title: 'BC Timber Sales website · 12 May 2005',
        url: 'https://web.archive.org/web/20050512075023/http://www.for.gov.bc.ca/bcts/'
      },
      {
        title: 'BC Timber Sales website · 23 November 2017',
        url: 'https://web.archive.org/web/20171123201642/https://www.for.gov.bc.ca/bcts/'
      }
    ]
  },
  {
    id: 'forest-service-green-gold',
    kind: 'drawing',
    artwork: 'forest-service-green-gold.svg',
    name: 'Forest Service, green and gold',
    description: 'A dark green oval with gold rules around a lone evergreen, mountains and a lake.',
    evidence: 'Adoption date unverified',
    comments: [
      '“FOREST SERVICE” arcs over the top and “BRITISH COLUMBIA” under the bottom of a dark green oval with two gold rules. Inside the inner rim a single evergreen stands in front of snow-capped mountains, a band of distant forest and a lake, under a blue sky crossed by white cloud bands.',
      'It shares its wording and its lone conifer with the Forest Service tree oval, but not its construction: no diamond separators, gold rules in place of a plain ring, and a full-colour landscape. How the two designs relate, and which came first, is not established.',
      'The artwork is an independent vector reconstruction from a supplied image: concentric ellipses, 28 custom outlined letters and hand-drawn landscape paths, with no tracing. The colours are flat approximations of the image, not verified institutional colours, and the small landscape details are interpreted.'
    ],
    sources: []
  }
]

// Colourways are display treatments, not additional dated logo eras.
const oneInk = (foreground, background) => ({
  ink: foreground, paper: background, text: foreground, sky: background,
  water: background, wildlife: foreground, distant: background,
  earth: foreground, tree: foreground, word: foreground,
  descriptor: foreground, strip: foreground, stripText: background
})

// The supplied drawings' colourways, as maps from the drawing's own colours to new ones. The
// evergreen emblem's alternatives are the greens it is printed in on the photographed posters,
// sampled from those photographs, so they are approximate. The green-and-gold oval's are generated,
// after the treatments the tree oval is offered in.
const DRAWING_VARIANTS = {
  'forest-service-emblem.svg': [
    { id: 'colour', name: 'Full colour', recolour: {}, note: 'The reconstruction’s flat colours, chosen from the supplied emblem image.' },
    { id: 'reward-lime', name: 'Lime, as on REWARD', recolour: { '#278F38': '#8CBE0C' }, note: 'The badge green sampled from the photograph of the REWARD poster. Approximate: print and photograph both shift colour.' },
    { id: 'sign-green', name: 'Bright green, as on the sign', recolour: { '#278F38': '#2DB43C' }, note: 'The badge green sampled from the photograph of Enjoy & Protect our Forests. Approximate, as above.' }
  ],
  'forest-service-green-gold.svg': [
    { id: 'colour', name: 'Full colour', recolour: {}, note: 'The reconstruction’s flat colours: badge green, gold, and the landscape’s greens, blue and grey.' },
    { id: 'black-gold', name: 'Black & gold', recolour: { '#00381E': '#000000' }, note: 'The oval and its keylines in black, the gold and the landscape kept. A generated recolour after the tree oval’s black-and-gold treatment.' },
    { id: 'black', name: 'Black & white', recolour: { '#00381E': '#000000', '#080C0A': '#000000', '#E6C786': '#FFFFFF', '#005737': '#FFFFFF', '#0FB4E0': '#FFFFFF', '#8D8F8D': '#FFFFFF' }, note: 'One ink: the oval and every outline in black, the lettering and the landscape left white. A generated recolour.' }
  ]
}
const drawingVariants = (logo) => ({ colours: DRAWING_VARIANTS[logo.artwork].map((variant) => ({ ...variant, artwork: logo.artwork, padding: logo.padding })), related: [] })

export const variantsFor = (logo) => logo.kind === 'drawing' ? drawingVariants(logo) : ({
  colours: [
    { id: 'colour', name: 'Full colour', recipe: logo.id, note: 'The Forest Oval preset palette.' },
    { id: 'black', name: 'Black & white', recipe: logo.id, theme: 'mono', note: 'The Forest Oval single-colour palette.' },
    { id: 'green', name: 'Forest green', recipe: logo.id, theme: 'mono', colours: oneInk('#008450', '#ffffff'), note: 'A generated green recolour of the single-colour design.' },
    { id: 'reversed', name: 'White on green', recipe: logo.id, theme: 'mono', colours: oneInk('#ffffff', '#008450'), background: '#008450', note: 'A generated reversed recolour of the single-colour design.' },
    ...(logo.id === 'forest-service' ? [
      { id: 'black-gold', name: 'Black & gold', recipe: logo.id, theme: 'mono', colours: oneInk('#FFCA05', '#000000'), background: '#000000', note: 'Gold lettering and landscape on black. A generated recolour; an adoption date for this treatment is unverified.' },
      { id: 'navy-gold', name: 'Navy & gold', recipe: logo.id, theme: 'mono', colours: oneInk('#FFCA05', '#002950'), background: '#002950', note: 'The Airtanker package’s navy and gold applied to the standalone oval. A generated colourway.' }
    ] : [])
  ],
  related: logo.id === 'forest-service' ? [
    { id: 'wildfire-management', name: 'Wildfire Management', recipe: 'wildfire-management', note: 'Upper service ribbon. Forest Oval labels this as a photographic approximation.' },
    { id: 'airtanker-package', name: 'Airtanker Operations · shared crest', recipe: 'airtanker', composition: 'airtanker-package', note: 'The Airtanker package’s wings and band with the shared tree oval and mountain lines. A reference-based reconstruction; its adoption date is unverified.', source: { title: 'Airtanker reconstruction notes', url: 'https://github.com/ahzs645/forestoval/tree/44ec88fc53cd2e4eb45e1f15ab094a98582a0fc2/airtanker-operations' } }
  ] : [
    { id: 'wildfire', name: 'Wildfire Service', recipe: logo.id === 'forests' ? 'forests-wildfire' : 'long-wildfire', note: 'The same oval family with the Wildfire Service ribbon.' }
  ]
})
