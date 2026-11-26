// The signs, by series. Like the posters' catalogue (src/posters/catalogue.js): each sign names its
// series, each series lists its signs, and nothing here imports a drawing, so it can be tested
// without a browser. Adding a sign is a drawing and its parts (see forest-service/, tourism/ and parks/), an entry here,
// and a loader in SignsView.jsx.

import { bearAwareId, bearAwareTitle, bearAwareWindowId, bearAwareWindowMeta } from '../initiatives/bearAwareArtwork.js'
import { ENTRY_CARDS } from './entering-bc/signs.js'

export const SIGN_SERIES = [
  { id: bearAwareId, title: bearAwareTitle, kind: 'Window sign · 1997', signs: [bearAwareWindowId] },
  {
    id: 'forest-service',
    title: 'British Columbia Forest Service',
    kind: 'Fire protection',
    signs: ['fire-day', 'lookout', 'forest-closure']
  },
  {
    id: 'entering-bc',
    title: 'Entering British Columbia',
    kind: 'Highway information signs',
    signs: Object.keys(ENTRY_CARDS)
  },
  {
    id: 'tourism',
    title: 'Province of British Columbia',
    kind: 'Welcome signs',
    signs: ['super-natural', 'super-natural-bordered']
  },
  {
    id: 'fish-wildlife',
    title: 'British Columbia Fish & Wildlife Branch',
    kind: 'Angling notices',
    signs: ['cheakamus-notice-to-anglers']
  },
  {
    id: 'parks',
    title: 'Provincial Parks Branch',
    kind: 'Proposed park symbols',
    signs: ['proposed-park-symbols'],
    // A sheet of proposals from an annual report, not a sign that stood: it is shown under BC
    // Parks in the Visual Guides (src/guides/guides.js), and its page here, each symbol with its
    // history, is reached from there by its address.
    unlisted: true
  }
]

export const SIGNS = {
  ...ENTRY_CARDS,
  [bearAwareWindowId]: { ...bearAwareWindowMeta, id: bearAwareWindowId, series: bearAwareId },
  'fire-day': {
    id: 'fire-day', series: 'forest-service', title: 'TO-DAY IS A FIRE DAY',
    when: 'Photographed in Powell River, July 1938', view: { x: 0, y: 0, w: 550, h: 424 },
    page: { w: 11, h: 8.48 }
  },
  lookout: {
    id: 'lookout',
    series: 'forest-service',
    title: 'LOOKOUT',
    when: 'Undated',
    view: { x: 21, y: 121, w: 1347, h: 766 },
    page: { w: 13.47, h: 7.66 }
  },
  'forest-closure': {
    id: 'forest-closure',
    series: 'forest-service',
    title: 'FOREST CLOSURE, Zone 3',
    when: '1960, from the Protection Bulletin',
    view: { x: 0, y: 0, w: 1000, h: 1030.025404 },
    page: { w: 10, h: 10.3 }
  },
  'super-natural': {
    id: 'super-natural',
    series: 'tourism',
    title: 'Super, Natural British Columbia',
    when: 'Flag era, about 1983–2001',
    view: { x: 0, y: 0, w: 1200, h: 1150 },
    page: { w: 12, h: 11.5 }
  },
  'super-natural-bordered': {
    id: 'super-natural-bordered',
    series: 'tourism',
    title: 'Super, Natural British Columbia · blue-bordered sign',
    when: 'Undated · photographic reconstruction',
    view: { x: 0, y: 0, w: 814, h: 440 },
    page: { w: 10, h: 5.405 }
  },
  'cheakamus-notice-to-anglers': {
    id: 'cheakamus-notice-to-anglers',
    series: 'fish-wildlife',
    title: 'Notice to Anglers, Cheakamus River',
    when: 'Undated · photographic reconstruction',
    view: { x: 0, y: 0, w: 1060, h: 720 },
    page: { w: 10.6, h: 7.2 }
  },
  'proposed-park-symbols': {
    id: 'proposed-park-symbols',
    series: 'parks',
    title: 'Proposed park symbols',
    when: '1971, proposed in the annual report',
    view: { x: 0, y: 0, w: 1000, h: 1500 },
    page: { w: 10, h: 15 }
  }
}

export const signIds = () => SIGN_SERIES.flatMap((series) => series.signs)
