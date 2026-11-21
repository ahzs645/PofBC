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

// Photographs in the BC Forestry Patch Atlas (the source of the Patches view), by its photo ids.
const atlasPhoto = (id, title, file) => ({
  title: `BC Forestry Patch Atlas, photo ${id}: ${title}`,
  url: `https://drive.google.com/file/d/${file}/view`
})

// The posters that carry a design, as places in the Posters view: each opens at the design.
const onPoster = (poster, title, note, part = 'emblem') => ({ title, note, to: { view: 'posters', poster, part } })

export const FOREST_LOGOS = [
  {
    id: 'forest-service-lands-department',
    kind: 'drawing',
    artwork: 'forest-service-lands-department.svg',
    padding: '2%',
    name: 'Forest Service, Lands Department',
    description: 'An engraved seal: a lone conifer through the lettering, with boughs and cones on either side.',
    evidence: 'Lands Department wording (1912–1945) · dating unconfirmed',
    comments: [
      '“BRITISH COLUMBIA” arcs over a white oval and “LANDS DEPARTMENT” under it, with “FOREST SERVICE” across the middle. A single conifer stands up through the lettering on a narrow trunk with spreading roots, and engraved boughs and cones spread out on both sides of the oval.',
      'Its wording is the best evidence of its age. The Forest Branch was created within the Department of Lands in February 1912, and the BC Forest Service timeline records it becoming the Forest Service in 1945, when forests became a department of their own under the Minister of Lands and Forests. A seal naming both the Forest Service and the Lands Department sits at that change, or shows the service’s name in use before the timeline’s date. Which of the two is not established.',
      'A dated use: the same seal is on the cover of Root and Branch, vol. II, no. 12, catalogued as 1924.',
      'The artwork is a vector reconstruction from a supplied image: the engraving rebuilt as measured, variable-width strokes, the trunk, roots and 43 letters as separately fitted outlines, and the oval as a measured ellipse. The letters are reconstructed shapes, not an identified typeface. The site shows a lighter copy of the master, its coordinates rounded to a tenth of a unit.',
      'The BC Forestry Patch Atlas photographs the seal four times, on a card, a Fire Emergency Ration notice and printed matter, as its pine-bough seal (S10-O01). It is a printed seal, not a patch, so the Patches view leaves it out and it is kept here, as a logo.'
    ],
    sources: [
      forestServiceTimeline,
      atlasPhoto('S08', 'Lands Department badge, card and campfire decal', '15JI44htPICcRkrgZc4gI2Mt3X3la3wQ0'),
      atlasPhoto('S10', 'pine-bough Lands Department / Forest Service seal', '1B5Vn00JKHVSN6sVozNnuriihbWPNv6nT'),
      atlasPhoto('S23', 'Fire Emergency Ration notice', '1xrjjiufOriYvletlkS_aZhNQVg1VFPJP'),
      atlasPhoto('S24', 'signs, manuals and insignia', '1-QVWbIQg6MrkZRVLNYN1qmXptWJfsTMt')
    ],
    seenOn: [
      { title: 'England Expects: Prevent Forest Fires', note: 'Card, undated · the seal over the lettering, its boughs spread to the card’s width', to: { view: 'cards', card: 'england-expects', part: 'emblem' } }
    ]
  },
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
      'In the emblem’s last years the Forest Service sat within the Department of Lands, Forests and Water Resources (1962–1975). The Department of Forests was separated from it in 1976, and the Ministry of Forests Act came into force on 1 January 1979.',
      'The artwork is a vector reconstruction from a supplied image: seven shapes (the badge, the mainland, three islands, the crown and the trunk) with flat colours chosen from the image, not verified ink specifications. The same drawing is used on two Forest Service posters in the Posters view, and in one ink on a 1971 newspaper advertisement there.',
      'The black-and-white print reconstructions use one fourfold-symmetric superellipse frame (exponent 3.25, constant stroke), a province-and-tree silhouette with an unpainted evergreen cutout, and two detached coastal island marks. Both prints show only two identifiable detached island components; the earlier coloured reconstruction has three. A separately labelled three-island variation is offered for comparing these distinct renderings, not as proof of a missing historical detail.',
      'An undated newspaper clipping headed “Identity crisis for Socreds?” compares a Social Credit League provincial-profile emblem to the B.C. Forest Service symbol without its tree. This is historical evidence of a visual comparison, not proof of shared artwork, authorization, or the Forest Service logo’s introduction date.'
    ],
    article: {
      title: 'Identity crisis for Socreds?',
      excerpt: 'reminiscent of the B.C. Forest Service logo without the tree',
      context: 'The report describes a new stylized provincial-profile design among several competing symbols for the B.C. Social Credit League. Grace McCarthy is quoted explaining that the profile indicates a B.C. party rather than a national affiliation.',
      citation: 'Undated newspaper clipping supplied for this collection. Publication, issue date, page, and byline not yet identified.',
      qualification: 'Evidence for a contemporary visual comparison only. The paper does not establish who designed either symbol, a transfer of artwork, or a Forest Service adoption date.'
    },
    // How closely the print reconstructions match, said with the sources rather than in the history.
    measurements: ['The revised two-island geometry gives about 92.4% and 90.8% full-image pixel intersection-over-union against the two prints after size registration; those scores remain sensitive to scans and are not evidence of official construction.'],
    sources: [forestServiceTimeline],
    seenOn: [
      onPoster('reward-living-forest', 'REWARD: A Living Forest', 'Campfire poster · bottom right, beside the service’s name'),
      onPoster('enjoy-protect-forests', 'Enjoy & Protect our Forests', 'Sign · bottom right, beside the service’s name'),
      onPoster('coons-age', 'A Coon’s Age', 'Newspaper advertisement, 1971 · in one ink, beside the service’s name')
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
      'Forest Oval retains a supplied vector reference for this tree oval. PofBC’s BCTS research also records a related round Forest Service tree badge on archived sites from 2005 to 2017. That related badge does not establish the introduction or retirement of this exact oval.',
      'It is printed, in one green beside the Ministry of Forests’ arms signature, on the Forest Practices Branch’s Wildlife Trees poster, whose artist’s mark reads “d.g.01”. If that is a year, the oval was in use in about 2001; it is an inference, and it does not date when the oval was introduced.'
    ],
    seenOn: [
      onPoster('wildlife-trees', 'Wildlife Trees', 'Forest Practices Branch poster, undated (its artist’s mark suggests 2001) · bottom right, beside the ministry’s signature', 'oval')
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
    id: 'forest-service-yellow-sky',
    kind: 'drawing',
    artwork: 'forest-service-yellow-sky.svg',
    name: 'Forest Service, yellow-sky oval',
    description: 'A lone conifer before mountains and a lake under a yellow sky, ringed by FOREST SERVICE and BRITISH COLUMBIA.',
    evidence: 'Seen in two photographs · adoption date unverified',
    comments: [
      '“FOREST SERVICE” arcs over the top and “BRITISH COLUMBIA” under the bottom, with a dot on each side between them. Inside, a slender conifer with wind-shaped upper boughs rises from a lakeshore in front of snow-capped mountains and a band of distant forest, against a flat yellow sky.',
      'Two photographs show it printed in two colourways: a green ring around a strong yellow sky, and a cream ring around a paler one. It shares its wording and lone conifer with the Forest Service tree oval, but has dots where that oval has diamonds, and a different tree. When either was in use, and how the two ovals relate, is not established.',
      'The artwork shown is a refined vector redraw that follows a generated restoration image of the emblem, not a photograph: cleaner lettering, borders and tree, but its tree shape, olive ring and lower scene are the generated image’s.'
    ],
    sources: []
  },
  {
    id: 'forest-service-one-ink-oval',
    kind: 'drawing',
    artwork: 'forest-service-one-ink-oval.svg',
    padding: '6%',
    name: 'Forest Service, one-ink oval seal',
    description: 'A dark oval ringed by FOREST SERVICE and BRITISH COLUMBIA in serif capitals, around a lone conifer, mountains and water.',
    evidence: 'Printed on a poster with 1966 and 1967 centenary captions · adoption date unverified',
    comments: [
      '“FOREST SERVICE” arcs over the top and “BRITISH COLUMBIA” under the bottom of a broad dark band, in open serif capitals. Inside a keyline, a full, even conifer stands over a low line of mountains and three bands of water, and the foot of the oval is solid ink.',
      'It is printed in one ink at the foot of the fire-prevention poster MATCHES ARE NOT FOR CHILDREN!!, whose captions name the centenaries of 1966 and 1967. That places this printing around those years; it does not date the seal’s introduction or retirement.',
      'It shares its wording and its lone conifer with the yellow-sky oval and the tree oval, but not their construction: no dots or diamonds between the words, serif rather than sans-serif lettering, and a symmetrical tree. How the designs relate is not established.',
      'The artwork is the seal from the poster’s vector reconstruction, drawn from one photograph: analytic ellipse rings, a hand-drawn tree and landscape, and lettering from URW Bookman Demi outlines fitted to the photographed letter positions. That typeface is a stand-in, not an identification. The lettering, rings and sky are open, as printed, so the poster’s paint shows through them.'
    ],
    seenOn: [
      onPoster('matches-not-for-children', 'Matches Are Not for Children!!', 'Fire-prevention poster F. P. 19, about 1966–67 · bottom right, beside the headline', 'seal')
    ],
    sources: []
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
  'forest-service-lands-department.svg': [
    { id: 'colour', name: 'As engraved', recolour: {}, note: 'Black ink on a white oval, as in the supplied image. Outside the oval the paper shows through.' },
    { id: 'green', name: 'Forest green', recolour: { '#000000': '#00381E' }, note: 'The ink in the green-and-gold oval’s badge green. A generated recolour.' },
    { id: 'reversed', name: 'White on green', recolour: { '#000000': '#FFFFFF', '#FFFFFF': '#00381E' }, background: '#00381E', note: 'The engraving in white, its oval filled with the same green. A generated recolour.' }
  ],
  'forest-service-emblem.svg': [
    { id: 'colour', name: 'Full colour', recolour: {}, note: 'The reconstruction’s flat colours, chosen from the supplied emblem image.' },
    { id: 'reward-lime', name: 'Lime, as on REWARD', recolour: { '#278F38': '#8CBE0C' }, note: 'The badge green sampled from the photograph of the REWARD poster. Approximate: print and photograph both shift colour.' },
    { id: 'sign-green', name: 'Bright green, as on the sign', recolour: { '#278F38': '#2DB43C' }, note: 'The badge green sampled from the photograph of Enjoy & Protect our Forests. Approximate, as above.' },
    { id: 'lettered', name: 'With its name around it', artwork: 'forest-service-emblem-lettered.svg', recolour: {}, padding: '4%', background: '#EFEDE8', note: 'The name around the badge, as on a glass printed with the emblem. Letters placed from a photograph of it; its typeface is unidentified, so a Helvetica-like face stands in.' },
    { id: 'archival-one-ink', study: true, name: 'Archival print study · two detached islands', artwork: 'forest-service-emblem-one-ink.svg', recolour: {}, note: 'Updated manually constructed monochrome geometry: standardized squircle, fuller lower coast, corrected evergreen slope and trunk opening. Both supplied black-and-white prints show two separate island components. This reconstruction is not an official vector master.' },
    { id: 'three-islands-separated', study: true, name: 'Three detached islands · colour-master comparison', artwork: 'forest-service-emblem-three-islands-separated.svg', recolour: {}, note: 'Optional interpretation carrying forward the three separate island shapes in the earlier coloured PofBC master. The third central island is not discernible in the two monochrome reference prints. No island is connected to another.' },
    { id: 'three-islands-green', study: true, name: 'Three detached islands · forest-green study', artwork: 'forest-service-emblem-three-islands-green.svg', recolour: {}, note: 'Generated forest-green colouring of the three-detached-island geometry. Neither the additional middle island nor this green ink is documented by the supplied black-and-white prints.' },
    { id: 'reverse', study: true, name: 'Reversed · white on black', artwork: 'forest-service-emblem-reverse.svg', recolour: {}, note: 'One-ink separated-island drawing reversed for use on a dark ground. Newly generated treatment.' },
  ],
  'forest-service-yellow-sky.svg': [
    { id: 'colour', name: 'Olive and cream', recolour: {}, note: 'The refined redraw as drawn: an olive band with a cream trim around a golden sky. It follows a generated restoration image, so these colours are that image’s, not the emblem’s.' },
    { id: 'green', name: 'Green, as in the first photograph', recolour: { '#CECF8F': '#12763A', '#E6DFC9': '#12763A', '#F2DF83': '#F4DD04' }, note: 'The refined drawing recoloured to the first photograph’s green ring and strong yellow sky. A generated recolour; colours approximated from a small photograph.' },
  ],
  'forest-service-one-ink-oval.svg': [
    { id: 'colour', name: 'One ink, as printed', recolour: {}, note: 'The seal in the poster’s dark ink. Its lettering, rings and sky are open: here the card shows through, on the poster the paint.' },
    { id: 'on-paint', name: 'On the poster’s yellow', recolour: {}, background: '#F2C209', note: 'Over the yellow ground of the poster’s reconstruction, as it sits in the paint. The yellow is fitted to a photograph, not a specified ink.' },
    { id: 'green', name: 'Forest green', recolour: { '#1D2424': '#00381E' }, note: 'The ink in the green-and-gold oval’s badge green. A generated recolour.' },
    { id: 'reversed', name: 'White on green', recolour: { '#1D2424': '#FFFFFF' }, background: '#00381E', note: 'The seal in white on the same green. A generated recolour.' }
  ],
  'forest-service-green-gold.svg': [
    { id: 'colour', name: 'Full colour', recolour: {}, note: 'The reconstruction’s flat colours: badge green, gold, and the landscape’s greens, blue and grey.' },
    { id: 'black-gold', name: 'Black & gold', recolour: { '#00381E': '#000000' }, note: 'The oval and its keylines in black, the gold and the landscape kept. A generated recolour after the tree oval’s black-and-gold treatment.' },
    { id: 'black', name: 'Black & white', recolour: { '#00381E': '#000000', '#080C0A': '#000000', '#E6C786': '#FFFFFF', '#005737': '#FFFFFF', '#0FB4E0': '#FFFFFF', '#8D8F8D': '#FFFFFF' }, note: 'One ink: the oval and every outline in black, the lettering and the landscape left white. A generated recolour.' }
  ]
}
const drawingVariants = (logo) => {
  const variants = DRAWING_VARIANTS[logo.artwork].map((variant) => ({ ...variant, artwork: variant.artwork ?? logo.artwork, padding: variant.padding ?? logo.padding }))
  return {
    colours: variants.filter((variant) => !variant.study),
    studies: variants.filter((variant) => variant.study),
    related: []
  }
}

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
