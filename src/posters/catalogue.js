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
    id: 'bc-ferries',
    title: 'British Columbia Ferries',
    kind: 'Car decals',
    posters: ['go-bc-ferries', 'queen-of-sidney']
  }
]

/**
 * Every poster's catalogue card. `view` is the drawing's own viewBox; `page` is the export page in
 * inches. `when` is the short answer to when it was printed; its panels give the evidence.
 */
export const POSTERS = {
  'coastal-forest': {
    id: 'coastal-forest',
    series: 'environment',
    title: 'Coastal Forest',
    when: '1979–86',
    view: { x: 0, y: 0, w: 2400, h: 3600 },
    page: { w: 24, h: 36 },
    background: '#121411'
  },
  'reward-living-forest': {
    id: 'reward-living-forest',
    series: 'forest-service',
    title: 'REWARD: A Living Forest',
    when: 'Before about 1973',
    view: { x: 80, y: 67, w: 930, h: 1308 },
    page: { w: 11.69, h: 16.45 },
    background: '#f4f1e8'
  },
  'enjoy-protect-forests': {
    id: 'enjoy-protect-forests',
    series: 'forest-service',
    title: 'Enjoy & Protect our Forests',
    when: 'Before about 1973',
    view: { x: 0, y: 0, w: 1122, h: 1402 },
    page: { w: 11.22, h: 14.02 },
    background: '#f6efdf'
  },
  'dont-drop-it': {
    id: 'dont-drop-it',
    series: 'fire-prevention',
    title: 'DON’T DROP IT!',
    when: 'Undated',
    view: { x: 0, y: 0, w: 1254, h: 1254 },
    page: { w: 12, h: 12 },
    background: null
  },
  'dont-gamble-with-fire': {
    id: 'dont-gamble-with-fire',
    series: 'fire-prevention',
    title: 'Don’t gamble with FIRE',
    when: 'Undated',
    view: { x: 0, y: 0, w: 1233, h: 1233 },
    page: { w: 12, h: 12 },
    background: null
  },
  'go-bc-ferries': {
    id: 'go-bc-ferries',
    series: 'bc-ferries',
    title: 'GO B.C. FERRIES',
    when: '1960–64, from its wording',
    view: { x: 0, y: 0, w: 1354, h: 1161 },
    page: { w: 5.4, h: 4.63 },
    background: null
  },
  'queen-of-sidney': {
    id: 'queen-of-sidney',
    series: 'bc-ferries',
    title: 'Queen of Sidney',
    when: 'Undated',
    view: { x: 0, y: 0, w: 1305, h: 1206 },
    page: { w: 5.2, h: 4.81 },
    background: null
  }
}

export const posterIds = () => SERIES.flatMap((series) => series.posters)
export const seriesOf = (posterId) => SERIES.find((series) => series.posters.includes(posterId)) ?? null

/** The posters either side of one in reading order, across series. */
export const neighbours = (posterId) => {
  const ids = posterIds()
  const i = ids.indexOf(posterId)
  return { previous: i > 0 ? ids[i - 1] : null, next: i >= 0 && i < ids.length - 1 ? ids[i + 1] : null }
}
