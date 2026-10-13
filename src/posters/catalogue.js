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
    description: 'Educational posters signed by the ministry in the crest identity, the Province’s mark before the rising sun. Coastal Forest is the first here; others the ministry issued can join it.',
    posters: ['coastal-forest']
  },
  {
    id: 'forest-service',
    title: 'British Columbia Forest Service',
    kind: 'Campaign posters and signs',
    description: 'Posters signed “British Columbia Forest Service” beside the service’s evergreen emblem, the mark it used, it seems, until about 1973. Click the emblem on either one to see it among the Forests logos.',
    posters: ['reward-living-forest', 'enjoy-protect-forests']
  },
  {
    id: 'fire-prevention',
    title: 'B. C. Forest Service fire-prevention badges',
    kind: 'Round badges',
    description: 'Two-colour roundels with a one-line warning and a curved “B. C. Forest Service” credit. Both are set in the same forest green here.',
    posters: ['dont-drop-it', 'dont-gamble-with-fire']
  }
]

/**
 * Every poster's catalogue card. `view` is the drawing's own viewBox; `page` is the export page in
 * inches. `dated` says what is known about when it was printed, and how.
 */
export const POSTERS = {
  'coastal-forest': {
    id: 'coastal-forest',
    series: 'environment',
    title: 'Coastal Forest',
    issuer: 'Province of British Columbia · Ministry of Environment',
    dated: '1979–86, dated by the ministry name in its logo',
    summary: 'A photograph of a coastal stand over four columns of copy, a swash Bookman title, the crest lockup and the ministry’s slogan.',
    view: { x: 0, y: 0, w: 2400, h: 3600 },
    page: { w: 24, h: 36 },
    background: '#121411'
  },
  'reward-living-forest': {
    id: 'reward-living-forest',
    series: 'forest-service',
    title: 'REWARD — A Living Forest',
    issuer: 'British Columbia Forest Service',
    dated: 'Date not printed; the emblem places it before about 1973',
    summary: 'A campfire poster: a bird and a bear under the boughs, and the promise that the reward for observing the regulations is a living forest.',
    view: { x: 80, y: 67, w: 930, h: 1308 },
    page: { w: 11.69, h: 16.45 },
    background: '#f4f1e8'
  },
  'enjoy-protect-forests': {
    id: 'enjoy-protect-forests',
    series: 'forest-service',
    title: 'Enjoy & Protect our Forests',
    issuer: 'British Columbia Forest Service',
    dated: 'Date not printed; the emblem places it before about 1973',
    summary: 'A rounded sign: a smiling evergreen with its arm around a red-hatted figure, above the service’s name and emblem.',
    view: { x: 0, y: 0, w: 1122, h: 1402 },
    page: { w: 11.22, h: 14.02 },
    background: '#f6efdf'
  },
  'dont-drop-it': {
    id: 'dont-drop-it',
    series: 'fire-prevention',
    title: 'DON’T DROP IT!',
    issuer: 'B. C. Forest Service',
    dated: 'Date not established',
    summary: 'A lit cigarette laid across three tilted words on a forest-green roundel.',
    view: { x: 0, y: 0, w: 1254, h: 1254 },
    page: { w: 12, h: 12 },
    background: null
  },
  'dont-gamble-with-fire': {
    id: 'dont-gamble-with-fire',
    series: 'fire-prevention',
    title: 'Don’t gamble with FIRE',
    issuer: 'B. C. Forest Service',
    dated: 'Date not established',
    summary: 'Two thrown dice between a rounded “don’t gamble!” and a block “FIRE”, recoloured here into the series’ forest green.',
    view: { x: 0, y: 0, w: 1233, h: 1233 },
    page: { w: 12, h: 12 },
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
