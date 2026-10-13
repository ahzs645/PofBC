// The Forest Service's signs: their parts, where each sits in its drawing, and what the panel says.
// Data only, in the posters' format (see src/posters/forest-service/posters.js): a string block is a
// paragraph; { h }, { facts }, { note }, { palette }, { links } and { sources } are what they say.

import { SIGNS } from '../catalogue.js'

const LOOKOUT_RELEASE = {
  label: 'B.C. news release, “Wildfire history preserved through lookout restorations”, 26 September 2012',
  href: 'https://news.gov.bc.ca/releases/2012FOR0178-001437'
}

const SERVICE_LINKS = [
  {
    label: 'The Forest Service’s marks',
    note: 'Internal Logos · Forests: the Lands Department seal, the evergreen emblem and the ovals',
    to: { view: 'internal', internal: 'forests' }
  },
  {
    label: 'The Forest Service’s posters',
    note: 'Posters · REWARD: A Living Forest, signed by the service beside its emblem',
    to: { view: 'posters', poster: 'reward-living-forest', part: 'service' }
  },
  {
    label: 'Its fire-prevention badges',
    note: 'Posters · DON’T DROP IT! and Don’t gamble with FIRE',
    to: { view: 'posters', poster: 'dont-drop-it' }
  }
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
          { links: SERVICE_LINKS }
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

export const FOREST_SERVICE_SIGNS = { lookout: LOOKOUT }
