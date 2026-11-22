// The Parks Branch's proposed park symbols of 1971: each pictogram, where it sits in the drawing, and
// what the panel says. Data only, in the same format as the Forest Service's signs (see
// ../forest-service/signs.js).
//
// The drawing is assembled by scripts/build-park-symbols-sign.mjs from the 22 reconstructions in
// artwork/recreation-conservation/park_symbols/, four to a row as the report prints them. The report
// heads its page PROPOSED PARK SYMBOLS, and nothing here claims any of them was adopted or put up.

import { SIGNS } from '../catalogue.js'

const REPORT_1971 = {
  label: 'Department of Recreation and Conservation, Annual Report 1971, PDF page 68 (printed DD67): “Proposed Park Symbols”',
  href: 'https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf#page=68'
}
const REPORT_1971_COLOUR = {
  label: 'The same report in colour, Royal BC Museum annual report archive',
  href: 'https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1971.pdf#page=68'
}

const LINKS = [
  {
    label: 'The department’s marks',
    note: 'Logos · Recreation and Conservation: the five square symbols, among them the Parks Branch’s spirals',
    to: { view: 'gallery', logos: 'recreation-conservation' }
  },
  {
    label: 'BC Parks, from 1971',
    note: 'Logos · BC Parks: the Parks Branch’s spirals and 1973 shield, then the marks since',
    to: { view: 'gallery', logos: 'bc-parks' }
  },
  {
    label: 'Department of Recreation and Conservation, 1971',
    note: 'Government · the department the Parks Branch belonged to',
    to: { view: 'government', year: 1971, node: 'department-of-recreation-and-conservation-1957' }
  }
]

// The 22, in the report's order: the manifest's name, the drawing's id, and the overlap of the
// reconstruction's ink with the scan's (whole symbol, then inside the ring) from the package's metrics.
const SYMBOLS = [
  ['fire-wood', 'Fire-wood', 'An axe in a chopping block.', 0.853, 0.882],
  ['water', 'Water', 'A tumbler, full to a wavy brim.', 0.822, 0.745],
  ['change-house', 'Change house', 'A coat hanger.', 0.785, 0.743],
  ['picnicking', 'Picnicking', 'A picnic table, seen end on.', 0.858, 0.859],
  ['amphitheatre', 'Amphitheatre', 'Three arcs over a small block.', 0.797, 0.758],
  ['tenting', 'Tenting', 'A tent with its poles crossed at the peak.', 0.846, 0.843],
  ['camping', 'Camping', 'A tent behind a trailer: the camper’s site rather than the tenter’s.', 0.825, 0.808],
  ['boat-launch', 'Boat launch', 'A boat on a trailer above a ramp.', 0.822, 0.789],
  ['sani-station', 'Sani-station', 'A trailer over a ground line, with an arrow down into a tank below it.', 0.888, 0.881],
  ['toilets', 'Toilets', 'A woman and a man, each on a door.', 0.831, 0.839],
  ['parking', 'Parking', 'A serif P.', 0.864, 0.891],
  ['boat-trailer-parking', 'Boat trailer parking', 'The P over a boat on its trailer.', 0.809, 0.762],
  ['fishing', 'Fishing', 'A fish and a hook.', 0.805, 0.765],
  ['nature-trail', 'Nature trail', 'A walker beside an interpretive sign, inside a dashed loop that ends in an arrow.', 0.767, 0.667],
  ['horse-trail', 'Horse-trail', 'A rider on a horse.', 0.79, 0.72],
  ['hiking-trail', 'Hiking trail', 'A hiker with a pack and a stick.', 0.807, 0.753],
  ['skiing', 'Skiing', 'A downhill skier, crouched, with a pole.', 0.781, 0.707],
  ['sledding', 'Sledding', 'A rider lying on a toboggan.', 0.749, 0.648],
  ['swimming', 'Swimming', 'A swimmer’s head and arm over the water.', 0.807, 0.753],
  ['water-skiing', 'Water skiing', 'A skier holding a tow rope, over waves.', 0.748, 0.611],
  ['winter-recreation-area', 'Winter recreation area', 'A snowflake.', 0.779, 0.738],
  ['cross-country-skiing', 'Cross-country skiing', 'A skier striding with two poles.', 0.777, 0.705]
]

// The figures, ropes and snowflake are where the package says it interpreted most.
const INTERPRETED = new Set(['nature-trail', 'horse-trail', 'hiking-trail', 'skiing', 'sledding', 'swimming',
  'water-skiing', 'winter-recreation-area', 'cross-country-skiing'])

const COLUMNS = 4
const PITCH = 250
const MARGIN = 25
const SIZE = 200

const percent = (value) => `${Math.round(value * 100)}%`

const part = ([key, name, what, whole, interior], index) => {
  const row = Math.floor(index / COLUMNS) + 1
  const column = (index % COLUMNS) + 1
  return [key, {
    label: name,
    hint: `${index + 1} of 22`,
    box: { x: MARGIN + (column - 1) * PITCH, y: MARGIN + (row - 1) * PITCH, w: SIZE, h: SIZE },
    pad: 0.15,
    layer: `#pps-${key}`,
    panel: {
      eyebrow: `Proposed park symbol ${index + 1} of 22 · 1971`,
      heading: name,
      em: 'proposed, not shown to be adopted',
      lede: `${what} Black, in a heavy ring.`,
      blocks: [
        INTERPRETED.has(key)
          ? 'One of the figures the package calls least certain: its people, animals, ropes and the snowflake were drawn small in the report, so their poses and details are interpreted from a printed circle about 165 pixels across.'
          : 'One of the simpler pictograms, whose shapes the package calls strongly supported by the scan.',
        { facts: [
          ['In the report', `row ${row}, ${column === 1 ? 'first' : column === 2 ? 'second' : column === 3 ? 'third' : 'fourth'} from the left`],
          ['Ink overlap with the scan', `${percent(whole)} with its ring, ${percent(interior)} inside it`]
        ] },
        { note: 'Overlap measures how much of the reconstruction’s ink lands on the scan’s, at the scan’s small size. It is not a percentage of historical accuracy.' }
      ]
    }
  }]
}

export const PROPOSED_PARK_SYMBOLS = {
  id: 'proposed-park-symbols',
  spotlight: { keep: ['pps-page'] },
  regions: SYMBOLS.map(([key]) => key),
  parts: {
    overview: {
      label: 'All 22',
      box: SIGNS['proposed-park-symbols'].view,
      pad: 0.03,
      panel: {
        eyebrow: 'Provincial Parks Branch · Department of Recreation and Conservation',
        heading: 'Proposed park symbols, 1971',
        lede: 'Twenty-two pictograms for park facilities and activities, each a black figure in a heavy ring, printed on a page of the department’s 1971 annual report headed PROPOSED PARK SYMBOLS.',
        blocks: [
          'They are proposals. The report shows them as a set for the parks, without saying who drew them, whether they were approved, or where any of them went up. Nothing here claims they were adopted or installed.',
          'They are laid out as the report prints them, four to a row, from fire-wood to cross-country skiing. Click one to open it.',
          { facts: [
            ['Source', 'Annual report for 1971 (printed 1972), PDF page 68, printed page DD67'],
            ['Symbols', '22, each about 165 pixels across in the scan'],
            ['Drawing', 'each rebuilt from circles, polygons, strokes and curves; no tracing'],
            ['Colour', 'black, as a working master; the report’s ink is not a specification']
          ] },
          { note: 'These are reconstructions, not original artwork. The package’s source crops and overlays are in research/identity/recreation-conservation-2026-11-21, and each symbol is in artwork/recreation-conservation/park_symbols as its own SVG.' },
          { h: 'Where they belong' },
          { links: LINKS },
          { sources: [REPORT_1971, REPORT_1971_COLOUR] }
        ]
      }
    },
    ...Object.fromEntries(SYMBOLS.map(part))
  },
  order: ['overview', ...SYMBOLS.map(([key]) => key)]
}

export const PARKS_SIGNS = { 'proposed-park-symbols': PROPOSED_PARK_SYMBOLS }
