// The pins and buttons, by series. Like the signs' catalogue (src/signs/catalogue.js): each pin
// names its series, each series lists its pins, and nothing here imports a drawing, so it can be
// tested without a browser. Adding a pin is a drawing and its parts (see interior-university/ and
// novelty/), an entry here, and a loader in PinsView.jsx.
//
// `view` is the drawing's own viewBox; `page` is the export page in inches, a convenient size
// rather than a measurement: no pin's real size is known. `made` words the exports.

export const PIN_SERIES = [
  {
    id: 'interior-university',
    title: 'Interior University Society',
    kind: 'Campaign pins and buttons',
    pins: ['ius-enamel-pin', 'northern-u-button', 'say-yes-button']
  },
  {
    id: 'novelty',
    title: 'Novelty and souvenir buttons',
    kind: 'Pin-back buttons',
    pins: ['welcome-bc-pattison']
  }
]

export const PINS = {
  'ius-enamel-pin': {
    id: 'ius-enamel-pin',
    series: 'interior-university',
    title: 'Interior University Society',
    blurb: 'The society’s name on orange enamel, each word over a bar.',
    format: 'Enamel pin',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1008, h: 748 },
    page: { w: 10.08, h: 7.48 }
  },
  'northern-u-button': {
    id: 'northern-u-button',
    series: 'interior-university',
    title: 'Northern U',
    blurb: 'A university for the North, said in one letter.',
    format: 'Button',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 1000 },
    page: { w: 10, h: 10 }
  },
  'say-yes-button': {
    id: 'say-yes-button',
    series: 'interior-university',
    title: 'I say yes to Northern Interior University',
    blurb: 'A pledge in the first person, and YES twice.',
    format: 'Button',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 1000 },
    page: { w: 10, h: 10 }
  },
  'welcome-bc-pattison': {
    id: 'welcome-bc-pattison',
    series: 'novelty',
    title: 'Welcome to B.C., A Division of Jim Pattison Enterprises',
    blurb: 'The whole province, credited as one more Pattison division.',
    format: 'Button',
    when: 'Undated',
    made: 'vector',
    view: { x: 0, y: 0, w: 1000, h: 1000 },
    page: { w: 10, h: 10 }
  }
}

export const pinIds = () => PIN_SERIES.flatMap((series) => series.pins)
