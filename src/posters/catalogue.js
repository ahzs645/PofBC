// The posters, by series.
//
// A series is a run of printed pieces that belong together: one issuer, one look, one purpose. Each
// poster names its series; each series lists its posters in the order they are shown. Adding a
// poster is three steps: its drawing and its parts in a folder of its own (see forest-service/ for
// the data-only kind, coastal-forest/ for one with panels of its own), an entry here, and a loader
// in LOADERS (PostersView.jsx). A new series is one more entry in SERIES.
//
// Nothing here imports a drawing, so the catalogue can be read and tested without a browser.

export const SERIES = [
  {
    id: 'environment',
    title: 'Ministry of Environment',
    kind: 'Habitat posters',
    posters: ['coastal-forest']
  },
  {
    id: 'forest-service',
    title: 'British Columbia Forest Service',
    kind: 'Campaign posters and signs',
    posters: ['reward-living-forest', 'enjoy-protect-forests']
  },
  {
    id: 'fire-prevention',
    title: 'B. C. Forest Service badges',
    kind: 'Fire prevention',
    posters: ['dont-drop-it', 'dont-gamble-with-fire']
  },
  {
    id: 'forest-practices',
    title: 'Ministry of Forests',
    kind: 'Forest Practices Branch',
    posters: ['wildlife-trees']
  },
  {
    id: 'noxious-weeds',
    title: 'Noxious Weeds',
    kind: 'Ministry of Forests campaign · PDFs made in 1999 and 2000',
    posters: ['beware-these-alien-invaders', 'shattering-the-environment', 'explosion-in-slow-motion']
  },
  {
    id: 'bc-ferries',
    title: 'British Columbia Ferries',
    kind: 'Car decals',
    posters: ['go-bc-ferries', 'queen-of-sidney']
  },
  // Unlisted: left off the shelf, but its address opens it (?view=posters&poster=expo-86-davidson).
  {
    id: 'expo-86',
    title: 'Expo 86',
    kind: 'Art poster · unlisted',
    unlisted: true,
    posters: ['expo-86-davidson']
  }
]

/**
 * Every poster's catalogue card. `view` is the drawing's own viewBox; `page` is the export page in
 * inches. `when` is the short answer to when it was printed, worded no more firmly than the
 * evidence in its panels: a date read off a file or a mark says so. `made` is what the drawing is
 * made of — 'vector', or 'mixed' where it keeps photographs — and words its exports. A drawing too
 * large to fetch on spec says `prefetch: false`, and is loaded only when opened.
 *
 * `issuer`, `subject` and `format` are what the shelf filters by (FACETS, below), in a few broad
 * words each; `blurb` is one line on what the piece asks or says, shown on its card.
 */
export const POSTERS = {
  'coastal-forest': {
    id: 'coastal-forest',
    issuer: 'Ministry of Environment',
    subject: 'Forests and habitat',
    format: 'Poster',
    blurb: 'One forest as timber, habitat, a place to be and the source of fish-bearing water.',
    series: 'environment',
    title: 'Coastal Forest',
    when: '1979–86 or 1988–91, from its wording',
    made: 'mixed',
    view: { x: 0, y: 0, w: 2400, h: 3600 },
    page: { w: 24, h: 36 },
    background: '#121411'
  },
  'reward-living-forest': {
    id: 'reward-living-forest',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Poster',
    blurb: 'Follow the campfire rules, and the reward is the forest itself.',
    series: 'forest-service',
    title: 'REWARD: A Living Forest',
    when: 'Undated · evergreen-emblem design',
    made: 'vector',
    view: { x: 80, y: 67, w: 930, h: 1308 },
    page: { w: 11.69, h: 16.45 },
    background: '#f4f1e8'
  },
  'enjoy-protect-forests': {
    id: 'enjoy-protect-forests',
    issuer: 'BC Forest Service',
    subject: 'Forests and habitat',
    format: 'Sign',
    blurb: 'An invitation first: enjoy the forest, and look after it.',
    series: 'forest-service',
    title: 'Enjoy & Protect our Forests',
    when: 'Undated · evergreen-emblem design',
    made: 'vector',
    view: { x: 0, y: 0, w: 1122, h: 1402 },
    page: { w: 11.22, h: 14.02 },
    background: '#f6efdf'
  },
  'dont-drop-it': {
    id: 'dont-drop-it',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Badge',
    blurb: 'Three words and a lit cigarette: one cause of fire, named.',
    series: 'fire-prevention',
    title: 'DON’T DROP IT!',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1254, h: 1254 },
    page: { w: 12, h: 12 },
    background: null
  },
  'dont-gamble-with-fire': {
    id: 'dont-gamble-with-fire',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Badge',
    blurb: 'Carelessness as a bet, with the dice already in the air.',
    series: 'fire-prevention',
    title: 'Don’t gamble with FIRE',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1233, h: 1233 },
    page: { w: 12, h: 12 },
    background: null
  },
  'wildlife-trees': {
    id: 'wildlife-trees',
    issuer: 'Ministry of Forests',
    subject: 'Forests and habitat',
    format: 'Poster',
    blurb: 'Which dead and dying trees to leave standing, and the animals that need them.',
    series: 'forest-practices',
    title: 'Wildlife Trees',
    when: 'Undated · the artist’s mark suggests 2001',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 2997.159090909091 },
    page: { w: 11.44, h: 34.288 },
    background: null,
    prefetch: false
  },
  'beware-these-alien-invaders': {
    id: 'beware-these-alien-invaders',
    issuer: 'Ministry of Forests',
    subject: 'Invasive plants',
    format: 'Screen leaflet',
    blurb: 'Four weeds to know on sight, as a five-page linked PDF.',
    series: 'noxious-weeds',
    title: 'Beware These Alien Invaders',
    when: 'Undated · PDF made March 1999',
    made: 'mixed',
    view: { x: 0, y: 0, w: 684, h: 2483 },
    page: { w: 9.5, h: 34.486 },
    background: null
  },
  'shattering-the-environment': {
    id: 'shattering-the-environment',
    issuer: 'Ministry of Forests',
    subject: 'Invasive plants',
    format: 'Poster',
    blurb: 'Giant weeds in a cracked valley: invasion as a broken landscape.',
    series: 'noxious-weeds',
    title: 'Shattering the Environment',
    when: 'Undated · PDF made March 2000',
    made: 'mixed',
    view: { x: 0, y: 0, w: 2592, h: 1944 },
    page: { w: 36, h: 27 },
    background: null
  },
  'explosion-in-slow-motion': {
    id: 'explosion-in-slow-motion',
    issuer: 'Ministry of Forests',
    subject: 'Invasive plants',
    format: 'Poster',
    blurb: 'Ten weeds as specimens, and how each one spreads.',
    series: 'noxious-weeds',
    title: 'Explosion in Slow Motion',
    when: 'Undated · PDF made March 2000',
    made: 'mixed',
    view: { x: 0, y: 0, w: 1584, h: 2592 },
    page: { w: 22, h: 36 },
    background: null
  },
  'go-bc-ferries': {
    id: 'go-bc-ferries',
    issuer: 'BC Ferries',
    subject: 'Coastal travel',
    format: 'Decal',
    blurb: 'The ferry system sold as a trip to the coast, its routes round the rim.',
    series: 'bc-ferries',
    title: 'GO B.C. FERRIES',
    when: '1960–64, from its wording',
    made: 'vector',
    view: { x: 0, y: 0, w: 1354, h: 1161 },
    page: { w: 5.4, h: 4.63 },
    background: null
  },
  'queen-of-sidney': {
    id: 'queen-of-sidney',
    issuer: 'BC Ferries',
    subject: 'Coastal travel',
    format: 'Decal',
    blurb: 'One ship as a souvenir, seen through a ship’s wheel.',
    series: 'bc-ferries',
    title: 'Queen of Sidney',
    when: 'Undated · the ship took this name in 1963',
    made: 'vector',
    view: { x: 0, y: 0, w: 1305, h: 1206 },
    page: { w: 5.2, h: 4.81 },
    background: null
  },
  'expo-86-davidson': {
    id: 'expo-86-davidson',
    issuer: 'Expo 86 Corporation',
    subject: 'Expo 86',
    format: 'Poster',
    blurb: 'Robert Davidson’s formline design for the 1986 World Exposition.',
    series: 'expo-86',
    title: 'Expo 86 — Robert Davidson',
    when: 'Artwork signed 1985; for the fair of 1986',
    made: 'vector',
    view: { x: 0, y: 0, w: 1200, h: 1600 },
    page: { w: 23.62, h: 31.5 },
    background: '#FBE5C1'
  }
}

/** What the shelf can be filtered by: a card's field, and what to call it. */
export const FACETS = [
  { key: 'issuer', label: 'Issuer' },
  { key: 'subject', label: 'Subject' },
  { key: 'format', label: 'Format' }
]

export const posterIds = () => SERIES.flatMap((series) => series.posters)
/** The posters on the shelf, in reading order: every series but the unlisted ones. */
export const listedPosterIds = () => SERIES.filter((series) => !series.unlisted).flatMap((series) => series.posters)
export const seriesOf = (posterId) => SERIES.find((series) => series.posters.includes(posterId)) ?? null

/** The posters either side of one in reading order, across series. */
export const neighbours = (posterId) => {
  const ids = listedPosterIds()
  const i = ids.indexOf(posterId)
  return { previous: i > 0 ? ids[i - 1] : null, next: i >= 0 && i < ids.length - 1 ? ids[i + 1] : null }
}
