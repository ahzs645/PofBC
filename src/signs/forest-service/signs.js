// The Forest Service's signs: their parts, where each sits in its drawing, and what the panel says.
// Data only, in the posters' format (see src/posters/forest-service/posters.js): a string block is a
// paragraph; { h }, { facts }, { note }, { palette }, { links } and { sources } are what they say. A sign
// whose drawing has faces that change offers `variations` whose options `show` their own layers.

import { SIGNS } from '../catalogue.js'

const LOOKOUT_RELEASE = {
  label: 'B.C. news release, “Wildfire history preserved through lookout restorations”, 26 September 2012',
  href: 'https://news.gov.bc.ca/releases/2012FOR0178-001437'
}

const MARKS_LINK = {
  label: 'The Forest Service’s marks',
  note: 'Departmental Logos · Forests: the Lands Department seal, the evergreen emblem and the ovals',
  to: { view: 'internal', internal: 'forests' }
}
const BADGES_LINK = {
  label: 'Its fire-prevention badges',
  note: 'Posters · DON’T DROP IT! and Don’t gamble with FIRE',
  to: { view: 'posters', poster: 'dont-drop-it' }
}
const SERVICE_LINKS = [
  MARKS_LINK,
  {
    label: 'The Forest Service’s posters',
    note: 'Posters · REWARD: A Living Forest, signed by the service beside its emblem',
    to: { view: 'posters', poster: 'reward-living-forest', part: 'service' }
  },
  BADGES_LINK
]

export const LOOKOUT = {
  id: 'lookout',
  spotlight: { keep: ['panel'] },
  regions: ['frame', 'service', 'province', 'wordmark'],
  parts: {
    overview: {
      label: 'Whole sign',
      box: SIGNS.lookout.view,
      pad: 0.06,
      panel: {
        eyebrow: 'British Columbia Forest Service · sign',
        heading: 'LOOKOUT',
        lede: 'A white triangular sign framed twice in green: BRITISH COLUMBIA up its two sides, FOREST SERVICE along the base, and LOOKOUT in red inside the inner triangle.',
        blocks: [
          'Everything on it follows the triangle. The side lettering lies along the slopes, and the red word climbs to a tall K at the centre and falls away again, a peak inside a peak.',
          { facts: [
            ['Issued by', 'British Columbia Forest Service, from its lettering'],
            ['Date', 'not established'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1347 × 766 units; 38 paths in five layers, all lettering outlined']
          ] },
          { palette: [
            { name: 'Green', value: '#00543E' },
            { name: 'Red', value: '#C5001E' },
            { name: 'Panel', value: '#FFFFFF' }
          ] },
          { note: 'The colours are reconstruction choices, not verified paint. A softer palette sampled from the photograph (green #03513B, red #B70416, an off-white panel #E7ECEB) is kept with the source files. Lighting, grain and edge wear were left out, and no physical size is inferred.' },
          { h: 'The same service' },
          { links: [...SERVICE_LINKS, { label: 'FOREST CLOSURE, Zone 3', note: 'Signs · a 1960 closure sign with a changeable strip', to: { view: 'signs', sign: 'forest-closure' } }] }
        ]
      }
    },
    wordmark: {
      label: 'LOOKOUT',
      hint: 'the red wordmark',
      box: { x: 447, y: 365, w: 543, h: 350 },
      pad: 0.12,
      layer: '#lookout',
      hit: 'shape',
      panel: {
        eyebrow: 'The wordmark',
        heading: 'LOOKOUT',
        em: 'seven letters, three kinds of O',
        lede: 'Custom red letters that rise to the centre: three O forms in different proportions, a tall K at the peak, and an angled L, U and T at the ends, so the word itself makes the triangle’s slopes.',
        blocks: [
          'No typeface was substituted. Each letter is its own drawn path, named in the drawing, built to the photograph’s widths and placement.',
          { facts: [
            ['Letters', '7, each a separate path'],
            ['Red', '#C5001E'],
            ['Typeface', 'none: custom geometry']
          ] },
          { h: 'What a lookout was' },
          'Forest fire lookouts stood on high points across the province and played an instrumental role in finding wildfires early. They were later replaced by new technology, better public reporting and detection from the air, and many have become places to visit: for the Forest Service’s centennial in 2012 the Province restored lookouts near Terrace, Houston, Enderby, Kaslo and Boston Bar.',
          { sources: [LOOKOUT_RELEASE] }
        ]
      }
    },
    province: {
      label: 'British Columbia',
      hint: 'up the two slopes',
      box: { x: 311, y: 316, w: 826, h: 388 },
      pad: 0.06,
      layer: '#word-british, #word-columbia',
      hit: 'shape',
      panel: {
        eyebrow: 'The province',
        heading: 'BRITISH COLUMBIA',
        em: 'climbing both slopes',
        lede: 'BRITISH runs up the left side and COLUMBIA down the right, each word turned to lie along its slope between the two green triangles.',
        blocks: [
          'The green alphabet is drawn from straight segments and smooth curves, its letter widths and spacing matched to the photograph. The same alphabet sets FOREST SERVICE along the base.',
          { facts: [
            ['BRITISH', 'turned −46.85°'],
            ['COLUMBIA', 'turned 47.7°'],
            ['Green', '#00543E']
          ] }
        ]
      }
    },
    service: {
      label: 'Forest Service',
      hint: 'along the base',
      box: { x: 294, y: 767, w: 820, h: 74 },
      pad: 0.25,
      layer: '#word-forest-service',
      panel: {
        eyebrow: 'The signature',
        heading: 'FOREST SERVICE',
        lede: 'The service’s name along the base, level, in the same green capitals as the sides.',
        blocks: [
          'As on its posters and badges, the sign names the service itself rather than the department it sat in.',
          { h: 'The same service' },
          { links: SERVICE_LINKS }
        ]
      }
    },
    frame: {
      label: 'Frame',
      hint: 'two green triangles',
      box: { x: 39, y: 139, w: 1311, h: 730 },
      pad: 0.06,
      layer: '#outer-border, #inner-border',
      hit: 'shape',
      panel: {
        eyebrow: 'The panel',
        heading: 'Two triangles',
        lede: 'The panel is a triangle with rounded corners. A green border follows its edge, and a second, smaller triangle frames LOOKOUT.',
        blocks: [
          'Both are constructed rather than traced: the panel from a triangle with offset edges and circular corner arcs, the inner border as a pair of offset triangles. The straight edges are regularized where the photograph showed wear.',
          { facts: [
            ['Panel', 'triangle, corners rounded on a radius of 24 units'],
            ['Borders', 'offset rings, green #00543E'],
            ['Outside the panel', 'transparent']
          ] }
        ]
      }
    }
  },
  order: ['overview', 'wordmark', 'province', 'service', 'frame']
}

// ── FOREST CLOSURE, Zone 3 ──────────────────────────────────────────────────────────────────────
// One drawing holds both faces of the changeable strip; the overview's switch shows one or the other.

const BULLETIN = {
  label: 'BC Forest Service, Forest Service Protection Bulletin, 1960 no. 3, p. 4, “Forest Closure Zone Signs”',
  href: 'https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=21448'
}

const CLOSURE_LINKS = [
  {
    label: 'LOOKOUT',
    note: 'Signs · the service’s other triangle',
    to: { view: 'signs', sign: 'lookout' }
  },
  {
    label: 'Department of Lands and Forests',
    note: 'Government · 1960: the department the Forest Service sat in',
    to: { view: 'government', year: 1960, node: 'department-of-lands-and-forests-1945' }
  },
  BADGES_LINK
]

export const FOREST_CLOSURE = {
  id: 'forest-closure',
  spotlight: { keep: ['fc-main-board'] },
  variations: {
    label: 'Strip',
    options: [
      { id: 'open', label: 'OPEN', note: 'The strip as photographed open: dark letters on white.', show: '#fc-open-panel' },
      { id: 'closed', label: 'CLOSED', note: 'The strip as photographed closed: WOODS CLOSED TO TRAVEL, light on dark.', show: '#fc-closed-panel', changed: 'with its strip turned to CLOSED' }
    ]
  },
  // The plate comes first so the parts drawn on it sit over it: clicking bare white opens the plate.
  regions: ['plate', 'heading', 'boundary', 'zone', 'oval', 'strip'],
  parts: {
    overview: {
      label: 'Whole sign',
      box: SIGNS['forest-closure'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'British Columbia Forest Service · sign',
        heading: 'FOREST CLOSURE',
        em: 'Zone 3',
        lede: 'A white triangle marking the boundary of a closure zone, over a strip the local ranger could change from OPEN to WOODS CLOSED TO TRAVEL.',
        blocks: [
          { facts: [
            ['Issued by', 'British Columbia Forest Service'],
            ['Date', '1960, from the Protection Bulletin that pictures it'],
            ['Rebuilt from', 'the bulletin’s two photographs, one with each strip'],
            ['Drawing', '1000 × 1030 units, black on white; all lettering outlined, both strips in one drawing']
          ] },
          { note: 'The typeface is not identified: a heavy geometric sans in the Futura/Spartan tradition. How the strip changed, reversed or swapped, is not proven, and the sizes are normalized, not fabrication sizes. The photographs are black and white, so the colours are a choice.' },
          { sources: [BULLETIN] },
          { h: 'The same service' },
          { links: CLOSURE_LINKS }
        ]
      }
    },
    plate: {
      label: 'Plate',
      hint: 'a triangle in a triangle',
      box: { x: 0, y: 0, w: 1000, h: 866 },
      pad: 0.05,
      layer: '#fc-main-board, #fc-inner-rule',
      hit: 'shape',
      panel: {
        eyebrow: 'The plate',
        heading: 'A triangle in a triangle',
        lede: 'A white triangle with a thin black one inside it: the heading along the slopes, BOUNDARY under the base, the zone and the emblem within.',
        blocks: [
          { facts: [
            ['Plate', 'equilateral by convention, 1000 units wide'],
            ['Inner rule', 'concentric, 0.556 the size of the plate']
          ] }
        ]
      }
    },
    heading: {
      label: 'FOREST CLOSURE',
      hint: 'along the two slopes',
      box: { x: 133, y: 191, w: 738, h: 526 },
      pad: 0.08,
      layer: '#fc-word-forest, #fc-word-closure',
      hit: 'shape',
      panel: {
        eyebrow: 'The heading',
        heading: 'FOREST CLOSURE',
        lede: 'FOREST climbs the left slope and CLOSURE runs down the right, each turned 60° to lie along its side.',
        blocks: [
          { facts: [
            ['Letters', '13, outlined; each repeated letter is one shared drawing'],
            ['Typeface', 'not identified']
          ] }
        ]
      }
    },
    boundary: {
      label: 'BOUNDARY',
      hint: 'along the base',
      box: { x: 211, y: 762, w: 598, h: 86 },
      pad: 0.2,
      layer: '#fc-word-boundary',
      panel: {
        eyebrow: 'The base',
        heading: 'BOUNDARY',
        lede: 'Level along the base, under the inner rule, so the plate reads FOREST CLOSURE BOUNDARY.'
      }
    },
    zone: {
      label: 'ZONE 3',
      hint: 'inside the inner triangle',
      box: { x: 381, y: 481, w: 239, h: 239 },
      pad: 0.15,
      layer: '#fc-word-zone, #fc-word-zone-number',
      panel: {
        eyebrow: 'The zone',
        heading: 'ZONE 3',
        lede: 'The zone’s number, the largest figure on the sign. Its 3, with broad, unequal bowls, is drawn for this sign: no font tested matches it unchanged.'
      }
    },
    oval: {
      label: 'Forest Service oval',
      hint: 'at the top of the inner triangle',
      box: { x: 459, y: 338, w: 82, h: 108 },
      pad: 0.8,
      layer: '#fc-forest-service-oval',
      panel: {
        eyebrow: 'The emblem',
        heading: 'Forest Service oval',
        lede: 'FOREST SERVICE over BRITISH COLUMBIA, around a sparse, tall tree. It is not the evergreen emblem, and none of the service’s ovals in Departmental Logos is identified as this one.',
        blocks: [
          'Its tree, landscape and tiny lettering are simplified: the photographs show it only small.',
          { links: [MARKS_LINK] }
        ]
      }
    },
    strip: {
      label: 'Changeable strip',
      hint: 'OPEN or CLOSED',
      box: { x: 0, y: 900, w: 1000, h: 130 },
      pad: 0.1,
      layer: '#fc-open-panel, #fc-closed-panel',
      panel: {
        eyebrow: 'The strip',
        heading: 'OPEN or CLOSED',
        lede: 'The strip under the plate, changed by the local ranger. Switch faces with the Strip control on the whole sign.',
        blocks: [
          { facts: [
            ['OPEN', 'dark on white, set wide'],
            ['CLOSED', 'WOODS CLOSED TO TRAVEL, light on dark, set narrow with a smaller TO'],
            ['Size', '1000 × 130 units for both, a convention, not a measurement']
          ] }
        ]
      }
    }
  },
  order: ['overview', 'heading', 'boundary', 'zone', 'oval', 'strip', 'plate']
}

export const FOREST_SERVICE_SIGNS = { lookout: LOOKOUT, 'forest-closure': FOREST_CLOSURE }
