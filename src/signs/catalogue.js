// The signs, by series. Like the posters' catalogue (src/posters/catalogue.js): each sign names its
// series, each series lists its signs, and nothing here imports a drawing, so it can be tested
// without a browser. Adding a sign is a drawing and its parts (see forest-service/), an entry here,
// and a loader in SignsView.jsx.

export const SIGN_SERIES = [
  {
    id: 'forest-service',
    title: 'British Columbia Forest Service',
    kind: 'Fire protection',
    signs: ['lookout']
  }
]

export const SIGNS = {
  lookout: {
    id: 'lookout',
    series: 'forest-service',
    title: 'LOOKOUT',
    when: 'Undated',
    view: { x: 21, y: 121, w: 1347, h: 766 },
    page: { w: 13.47, h: 7.66 },
    background: null
  }
}

export const signIds = () => SIGN_SERIES.flatMap((series) => series.signs)
