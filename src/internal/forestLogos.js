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

// The posters that carry the evergreen emblem, as places in the Posters view.
const onPoster = (poster, title, note) => ({ title, note, to: { view: 'posters', poster, part: 'emblem' } })

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
      'The artwork is a vector reconstruction from a supplied image: the engraving rebuilt as measured, variable-width strokes, the trunk, roots and 43 letters as separately fitted outlines, and the oval as a measured ellipse. The letters are reconstructed shapes, not an identified typeface. The site shows a lighter copy of the master, its coordinates rounded to a tenth of a unit.',
      'The BC Forestry Patch Atlas photographs the seal four times, on a card, a Fire Emergency Ration notice and printed matter, as its pine-bough seal (S10-O01). It is a printed seal, not a patch, so the Patches view leaves it out and it is kept here, as a logo.'
    ],
    sources: [
      forestServiceTimeline,
      atlasPhoto('S08', 'Lands Department badge, card and campfire decal', '15JI44htPICcRkrgZc4gI2Mt3X3la3wQ0'),
      atlasPhoto('S10', 'pine-bough Lands Department / Forest Service seal', '1B5Vn00JKHVSN6sVozNnuriihbWPNv6nT'),
      atlasPhoto('S23', 'Fire Emergency Ration notice', '1xrjjiufOriYvletlkS_aZhNQVg1VFPJP'),
      atlasPhoto('S24', 'signs, manuals and insignia', '1-QVWbIQg6MrkZRVLNYN1qmXptWJfsTMt')
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
      'In the emblem’s last years the Forest Service sat within the Department of Lands, Forests and Water Resources (1962–1976). The Department of Forests was separated from it in 1976, and the Ministry of Forests Act came into force on 1 January 1979.',
      'The artwork is a vector reconstruction from a supplied image: seven shapes (the badge, the mainland, three islands, the crown and the trunk) with flat colours chosen from the image, not verified ink specifications. The same drawing is used on both Forest Service posters in the Posters view.',
      'The separately reconstructed black-and-white examples show a rounded outlined frame, a dark province-and-tree silhouette with a real negative-space conifer, and two discernible detached island marks. This new geometric reconstruction was measured against both supplied prints, but its simplified ink edges are an interpretation rather than a contemporary vector master.',
      'An undated newspaper clipping headed “Identity crisis for Socreds?” compares a Social Credit League provincial-profile emblem to the B.C. Forest Service symbol without its tree. This is historical evidence of a visual comparison, not proof of shared artwork, authorization, or the Forest Service logo’s introduction date.'
    ],
    article: {
      title: 'Identity crisis for Socreds?',
      excerpt: 'reminiscent of the B.C. Forest Service logo without the tree',
      context: 'The report describes a new stylized provincial-profile design among several competing symbols for the B.C. Social Credit League. Grace McCarthy is quoted explaining that the profile indicates a B.C. party rather than a national affiliation.',
      citation: 'Undated newspaper clipping supplied for this collection. Publication, issue date, page, and byline not yet identified.',
      qualification: 'Evidence for a contemporary visual comparison only. The paper does not establish who designed either symbol, a transfer of artwork, or a Forest Service adoption date.'
    },
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
    id: 'forest-service-yellow-sky',
    kind: 'drawing',
    artwork: 'forest-service-yellow-sky.svg',
    name: 'Forest Service, yellow-sky oval',
    description: 'A tall, wind-shaped conifer against a yellow sky, ringed by FOREST SERVICE and BRITISH COLUMBIA.',
    evidence: 'Seen in two photographs · adoption date unverified',
    comments: [
      '“FOREST SERVICE” arcs over the top and “BRITISH COLUMBIA” under the bottom, with a dot on each side between them. Inside, a slender conifer with wind-shaped upper boughs rises from a lakeshore in front of snow-capped mountains and a band of distant forest, against a flat yellow sky.',
      'Two photographs show it printed in two colourways: a green ring around a strong yellow sky, and a cream ring around a paler one. It shares its wording and lone conifer with the Forest Service tree oval, but has dots where that oval has diamonds, and a different tree. When either was in use, and how the two ovals relate, is not established.',
      'The artwork is an independent redraw from the two small photographs: analytic ellipses, custom condensed block letters (not an identified typeface), and drawn landscape and tree paths. Fine conifer detail, terrain marks and colours are approximate. The package also held a bolder redraw of a generated preview image; it is not shown here, since a generated image is not evidence of the original.'
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
    { id: 'archival-one-ink', study: true, name: 'One ink · islands separate', artwork: 'forest-service-emblem-one-ink.svg', recolour: {}, note: 'New geometric reconstruction of the black-and-white prints: Bézier frame, dark BC silhouette and a transparent white-tree cutout. Two detached island marks are visible in the prints. Reference-based, not an authenticated master.' },
    { id: 'joined-islands', study: true, name: 'Joined island group', artwork: 'forest-service-emblem-joined-islands.svg', recolour: {}, note: 'The two detached island marks seen in the black-and-white prints are joined into one hand-constructed Bézier silhouette. The connection is a proposed modern interpretation, not a verified historic treatment.' },
    { id: 'joined-coast', study: true, name: 'Islands joined to mainland', artwork: 'forest-service-emblem-joined-coast.svg', recolour: {}, note: 'Earlier exploratory bridge based on the separate colour-master geometry, not the new measured black-and-white master. A design experiment, not geographical or historical evidence.' },
    { id: 'reverse', study: true, name: 'Reversed · white on black', artwork: 'forest-service-emblem-reverse.svg', recolour: {}, note: 'One-ink separated-island drawing reversed for use on a dark ground. Newly generated treatment.' },
    { id: 'reverse-joined', study: true, name: 'Reversed · joined islands', artwork: 'forest-service-emblem-reverse-joined-islands.svg', recolour: {}, note: 'White-on-black reversal of the single connected-island silhouette. Proposed inversion, not documented historic use.' },
    { id: 'profile-study', study: true, name: 'Without the tree · comparison', artwork: 'forest-service-emblem-profile-study.svg', recolour: {}, note: 'An earlier tree-free colour-master interpretation for discussing the clipping, not a reconstruction of an authenticated Social Credit Party logo or the new monochrome geometry.' }
  ],
  'forest-service-yellow-sky.svg': [
    { id: 'colour', name: 'Green, as in the first photograph', recolour: {}, note: 'A green ring around a strong yellow sky. Colours approximated from a small photograph.' },
    { id: 'cream', name: 'Cream, as in the second photograph', recolour: { '#12763A': '#CCC98B', '#F4DD04': '#F0D17B', '#F4F0D3': '#F5EBC4', '#DEE6C5': '#CBD5B9', '#0B3024': '#282E1B', '#18553A': '#235950', '#2C7252': '#3E7C6D', '#0D3527': '#163E37', '#19392A': '#333D2A', '#1B5841': '#25594E' }, note: 'The same drawing with a cream ring around a paler yellow sky, the colourway of the second photograph. Approximate, as above.' }
  ],
  'forest-service-green-gold.svg': [
    { id: 'colour', name: 'Full colour', recolour: {}, note: 'The reconstruction’s flat colours: badge green, gold, and the landscape’s greens, blue and grey.' },
    { id: 'black-gold', name: 'Black & gold', recolour: { '#00381E': '#000000' }, note: 'The oval and its keylines in black, the gold and the landscape kept. A generated recolour after the tree oval’s black-and-gold treatment.' },
    { id: 'black', name: 'Black & white', recolour: { '#00381E': '#000000', '#080C0A': '#000000', '#E6C786': '#FFFFFF', '#005737': '#FFFFFF', '#0FB4E0': '#FFFFFF', '#8D8F8D': '#FFFFFF' }, note: 'One ink: the oval and every outline in black, the lettering and the landscape left white. A generated recolour.' }
  ]
}
const drawingVariants = (logo) => {
  const variants = DRAWING_VARIANTS[logo.artwork].map((variant) => ({ ...variant, artwork: variant.artwork ?? logo.artwork, padding: logo.padding }))
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
