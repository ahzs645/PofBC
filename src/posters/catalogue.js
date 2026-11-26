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
    kind: 'Campaign posters, signs and advertising',
    posters: ['reward-living-forest', 'enjoy-protect-forests', 'prevent-forest-fires', 'matches-not-for-children', 'use-your-ashtray', 'coons-age']
  },
  {
    id: 'fire-prevention',
    title: 'B. C. Forest Service badges and decals',
    kind: 'Fire prevention',
    posters: ['dont-drop-it', 'dont-gamble-with-fire', 'be-careful']
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
  {
    id: 'health', title: 'Ministry of Health', kind: 'Public health advertising',
    posters: ['new-carecard']
  },
  {
    id: 'tourism',
    title: 'Super, Natural British Columbia',
    kind: 'Tourism advertising',
    posters: ['super-natural-spring']
  },
  {
    id: 'expo-86',
    title: 'Expo 86',
    kind: 'Art posters and a pavilion film poster',
    posters: ['expo-86-davidson', 'expo-86-fiorucci', 'our-british-columbia']
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
  'super-natural-spring': {
    id: 'super-natural-spring', series: 'tourism', issuer: 'Province of British Columbia',
    subject: 'Coastal travel', format: 'Magazine ad', made: 'mixed',
    title: 'So many of our visitors return in Spring.', when: '1984, from the creators’ published account',
    blurb: 'Returning orcas introduce a spring invitation to British Columbia.',
    view: { x: 0, y: 0, w: 620, h: 418 },
    // An export size in the supplied reference’s proportions, not a measurement of the original.
    page: { w: 12.4, h: 8.36 },
    prefetch: false
  },
  'new-carecard': {
    id: 'new-carecard', series: 'health', issuer: 'Ministry of Health',
    subject: 'Health care', format: 'Newspaper ad', made: 'mixed',
    title: 'BC’s New CareCard.', when: '2 August 1989, Gulf Islands Driftwood',
    blurb: 'The Standard and Gold CareCards introduced to British Columbians.',
    view: { x: 0, y: 0, w: 891, h: 1215 }, page: { w: 11, h: 15 }
  },
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
    page: { w: 24, h: 36 }
  },
  'reward-living-forest': {
    id: 'reward-living-forest',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Poster',
    blurb: 'Follow the campfire rules, and the reward is the forest itself.',
    series: 'forest-service',
    title: 'REWARD: A Living Forest',
    when: 'Undated',
    made: 'vector',
    view: { x: 80, y: 67, w: 930, h: 1308 },
    page: { w: 11.69, h: 16.45 }
  },
  'enjoy-protect-forests': {
    id: 'enjoy-protect-forests',
    issuer: 'BC Forest Service',
    subject: 'Forests and habitat',
    format: 'Sign',
    blurb: 'An invitation first: enjoy the forest, and look after it.',
    series: 'forest-service',
    title: 'Enjoy & Protect our Forests',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1122, h: 1402 },
    page: { w: 11.22, h: 14.02 }
  },
  'prevent-forest-fires': {
    id: 'prevent-forest-fires',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Poster',
    blurb: 'A forest burning to the ground, and the cost counted in timber and in wages.',
    series: 'forest-service',
    title: 'Prevent Forest Fires: Fire Destroys Timber and Payrolls',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 1440 },
    // The package's 250 × 360 mm, an export size rather than a measurement of the print.
    page: { w: 9.843, h: 14.173 },
    // 1.6 MB: 7,821 paths of woodcut trees, flames and timber.
    prefetch: false
  },
  'matches-not-for-children': {
    id: 'matches-not-for-children',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Poster',
    blurb: 'A gallows built of matches, and a match figure hanging from it: a warning to keep matches from children.',
    series: 'forest-service',
    title: 'Matches Are Not for Children!!',
    when: 'About 1966–67, from its centenary captions',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 1400 },
    // 10 × 14 in, an export size in the drawing's 5:7, not a measurement of the print.
    page: { w: 10, h: 14 },
    // 4.2 MB, nearly all of it the paint's 740,000 outline points.
    prefetch: false
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
    page: { w: 12, h: 12 }
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
    page: { w: 12, h: 12 }
  },
  'use-your-ashtray': {
    id: 'use-your-ashtray',
    issuer: 'Fish and Game Branch',
    subject: 'Fire prevention',
    format: 'Printed notice',
    blurb: 'A reminder to motorists printed in the notes panel of the provincial game regulations.',
    series: 'forest-service',
    title: 'Keep B.C. Green— Use Your Ashtray.',
    when: '1961–62 game regulations',
    made: 'vector',
    view: { x: 0, y: 0, w: 754, h: 227 },
    page: { w: 2.5133, h: 0.7567 }
  },
  'coons-age': {
    id: 'coons-age',
    issuer: 'BC Forest Service',
    subject: 'Forests and habitat',
    format: 'Newspaper ad',
    blurb: 'A young raccoon, and a promise that managed forests will outlast it.',
    series: 'forest-service',
    title: 'A Coon’s Age',
    when: '2 December 1971, Gulf Islands Driftwood',
    made: 'mixed',
    view: { x: 0, y: 0, w: 565, h: 1044 },
    page: { w: 3.937, h: 7.275 }
  },
  'be-careful': {
    id: 'be-careful',
    issuer: 'BC Forest Service',
    subject: 'Fire prevention',
    format: 'Decal',
    blurb: 'B and C as the province and as Be Careful, over a forest turning to flame.',
    series: 'fire-prevention',
    title: 'Be Careful: Prevent Forest Fires',
    when: '1960, from the Protection Bulletin',
    made: 'vector',
    view: { x: 0, y: 0, w: 1234, h: 909 },
    page: { w: 12.854, h: 9.469 }
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
    prefetch: false
  },
  'beware-these-alien-invaders': {
    id: 'beware-these-alien-invaders',
    // Unlisted: left off the shelf, but its address and the links to it still open it.
    unlisted: true,
    issuer: 'Ministry of Forests',
    subject: 'Invasive plants',
    format: 'Screen leaflet',
    blurb: 'Four weeds to know on sight, as a five-page linked PDF.',
    series: 'noxious-weeds',
    title: 'Beware These Alien Invaders',
    when: 'Undated · PDF made March 1999',
    made: 'mixed',
    view: { x: 0, y: 0, w: 684, h: 2483 },
    page: { w: 9.5, h: 34.486 }
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
    page: { w: 36, h: 27 }
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
    page: { w: 22, h: 36 }
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
    page: { w: 5.4, h: 4.63 }
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
    page: { w: 5.2, h: 4.81 }
  },
  'expo-86-davidson': {
    id: 'expo-86-davidson',
    issuer: 'Expo 86 Corporation',
    subject: 'Expo 86',
    format: 'Poster',
    blurb: 'Robert Davidson’s formline design for the 1986 World Exposition.',
    series: 'expo-86',
    title: 'Expo 86: Robert Davidson',
    when: 'Artwork signed 1985; for the fair of 1986',
    made: 'vector',
    view: { x: 0, y: 0, w: 1200, h: 1600 },
    page: { w: 23.62, h: 31.5 }
  },
  'expo-86-fiorucci': {
    id: 'expo-86-fiorucci',
    issuer: 'Expo 86 Corporation',
    subject: 'Expo 86',
    format: 'Poster',
    blurb: 'Vittorio Fiorucci’s four bright shapes, each with a row of windows, for the 1986 World Exposition.',
    series: 'expo-86',
    title: 'Expo 86: Vittorio Fiorucci',
    when: 'Undated · for the fair of 1986',
    made: 'vector',
    view: { x: 0, y: 0, w: 1100, h: 1593.700787402 },
    // A dealer’s 635 × 920 mm for a matching copy, not a measurement of this one.
    page: { w: 25, h: 36.22 }
  },
  'our-british-columbia': {
    id: 'our-british-columbia',
    issuer: 'British Columbia Pavilion',
    subject: 'Expo 86',
    format: 'Poster',
    blurb: 'The province’s name in a sunburst of flag colours: the British Columbia Pavilion’s film at Expo 86.',
    series: 'expo-86',
    title: 'Our British Columbia',
    when: '1986, from its copyright line',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 1450 },
    // 10 × 14.5 in, an export size in the photograph’s working proportion; the sheet was not measured.
    page: { w: 10, h: 14.5 }
  }
}

/** What the shelf can be filtered by: a card's field, and what to call it. */
export const FACETS = [
  { key: 'issuer', label: 'Issuer' },
  { key: 'subject', label: 'Subject' },
  { key: 'format', label: 'Format' }
]

export const posterIds = () => SERIES.flatMap((series) => series.posters)
/** The posters on the shelf, in reading order: every series but the unlisted ones, less unlisted posters. */
export const listedPosterIds = () => SERIES.filter((series) => !series.unlisted).flatMap((series) => series.posters).filter((id) => !POSTERS[id].unlisted)
export const seriesOf = (posterId) => SERIES.find((series) => series.posters.includes(posterId)) ?? null

/**
 * The posters either side of one in reading order, across series. An unlisted series is read on its
 * own, its posters stepping among themselves; a poster unlisted alone has no neighbours.
 */
export const neighbours = (posterId) => {
  const own = seriesOf(posterId)
  const ids = own?.unlisted && !POSTERS[posterId].unlisted ? own.posters : listedPosterIds()
  const i = ids.indexOf(posterId)
  return { previous: i > 0 ? ids[i - 1] : null, next: i >= 0 && i < ids.length - 1 ? ids[i + 1] : null }
}
