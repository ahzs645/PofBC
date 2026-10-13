// The Forest Service posters and badges: their parts, where each sits in its drawing, and what the
// panel says about it. Data only — the drawings are attached in ./index.js — so the boxes can be
// checked without a browser.
//
// Boxes are in each drawing's own units, measured from its named layers. A part with `hit: 'shape'`
// is found by the ink of its `layer` rather than by its box, for badges whose parts overlap.
//
// Panels are blocks: a string is a paragraph, and { h }, { facts }, { note }, { palette } and
// { links } are what they say. A link's `to` is a place on the site (see site/navigation.jsx).

import { POSTERS } from '../catalogue.js'

// ── Shared context ──────────────────────────────────────────────────────────────────────────────

const EMBLEM_LINK = {
  label: 'The evergreen emblem',
  note: 'Internal Logos · Forests — its colourways, history and the other posters it is on',
  to: { view: 'internal', internal: 'forests', 'internal-logo': 'forest-service-emblem' }
}
const OVALS_LINK = {
  label: 'The Forest Service’s later marks',
  note: 'Internal Logos · Forests — the tree oval and the wildlife ovals',
  to: { view: 'internal', internal: 'forests' }
}
const DEPARTMENT_LINK = {
  label: 'Department of Lands, Forests and Water Resources',
  note: 'Government · 1970 — the department the Forest Service sat in from 1962 to 1976',
  to: { view: 'government', year: 1970, node: 'department-of-lands-forests-and-water-resources-1962' }
}
const MINISTRY_OF_FORESTS_LINK = {
  label: 'Ministry of Forests',
  note: 'Government · 1979 — the ministry the service became part of',
  to: { view: 'government', year: 1979, node: 'ministry-of-forests-1976' }
}
const poster = (id, part, note) => ({
  label: POSTERS[id].title,
  note,
  to: { view: 'posters', poster: id, part }
})

const TIMELINE_SOURCE = {
  label: 'BC Forest Service Centenary Society, BC Forest Service timeline',
  href: 'https://bcfs100.for.gov.bc.ca/bscripts/timeline.asp'
}

const box = (id) => POSTERS[id].view

// ── DON’T DROP IT! ──────────────────────────────────────────────────────────────────────────────

export const DONT_DROP_IT = {
  id: 'dont-drop-it',
  spotlight: { keep: ['field', 'borders'] },
  regions: ['lettering', 'cigarette', 'credit'],
  parts: {
    overview: {
      label: 'Whole badge',
      box: box('dont-drop-it'),
      pad: 0.07,
      panel: {
        eyebrow: 'B. C. Forest Service · fire-prevention badge',
        heading: 'Three words and a cigarette',
        lede: 'A roundel of dark forest green with a cream double border. DON’T DROP IT! runs downhill across it, a lit cigarette lies through the words, and the service signs it along the lower rim.',
        blocks: [
          'The badge makes one cause of forest fire its whole message: a cigarette, still burning, dropped. There is no picture of a forest and no fire; the smoke curling off both ends is enough.',
          { facts: [
            ['Issued by', 'B. C. Forest Service, from the credit on the badge'],
            ['Date', 'not established'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1254 × 1254 units, six named layers, all lettering outlined']
          ] },
          { palette: [
            { name: 'Forest green', value: '#003E2D' },
            { name: 'Main cream', value: '#F8E3BB' },
            { name: 'Footer ivory', value: '#F1F0DE' }
          ] },
          { note: 'The colours were chosen from the photograph, not taken from a verified ink specification. Its texture, irregular edge and ash speckle were cleaned up rather than copied.' },
          { h: 'In the same series' },
          { links: [poster('dont-gamble-with-fire', 'overview', 'The other badge, set in this one’s green')] }
        ]
      }
    },
    lettering: {
      label: 'Lettering',
      hint: 'three words, tilted 21 degrees',
      box: { x: 126, y: 157, w: 936, h: 921 },
      pad: 0.06,
      layer: '#main-lettering',
      hit: 'shape',
      panel: {
        eyebrow: 'The lettering',
        heading: 'DON’T DROP IT!',
        em: 'drawn, not set',
        lede: 'Each word is its own group, turned 21 degrees anticlockwise about its own centre, so the three step down the badge parallel to the cigarette.',
        blocks: [
          'The letters are hand-authored straight and cubic-Bézier paths, fitted to the photograph for proportion and optical alignment rather than traced from it. Their counters — the holes in D, O, R and P — are openings in compound paths, not green patches laid on top, so the field shows through them in any colour.',
          'The exclamation mark is drawn on its own, larger and steeper than the words, as the badge has it.',
          { facts: [
            ['Groups', 'word-dont, word-drop, word-it, exclamation'],
            ['Rotation', '−21° each'],
            ['Fill', '#F8E3BB, even-odd'],
            ['Typeface', 'none: custom display letters']
          ] }
        ]
      }
    },
    cigarette: {
      label: 'Cigarette',
      hint: 'and the smoke from both ends',
      box: { x: 123, y: 115, w: 888, h: 783 },
      pad: 0.06,
      layer: '#cigarette, #smoke',
      hit: 'shape',
      panel: {
        eyebrow: 'The picture',
        heading: 'A cigarette, lit',
        em: 'and smoke from both ends',
        lede: 'The wrapper is a single long band laid diagonally from lower left to upper right, with a cut end at one tip and a burning ash end at the other.',
        blocks: [
          'Two smooth stroked Bézier paths make the upper smoke, looping over DON’T; a filled flourish curls under the D. Both are cream on the green, the only lines on the badge that are not lettering.',
          { facts: [
            ['Layers', 'cigarette (wrapper, cut end, ash end), smoke'],
            ['Upper smoke', 'two stroked paths, 12.6 units wide'],
            ['Simplified', 'the smallest ash flecks, deliberately']
          ] }
        ]
      }
    },
    credit: {
      label: 'Credit',
      hint: '“B. C. Forest Service”, on the rim',
      box: { x: 241, y: 957, w: 564, h: 195 },
      pad: 0.25,
      layer: '#credit',
      panel: {
        eyebrow: 'The credit',
        heading: 'B. C. Forest Service',
        em: 'on a curve',
        lede: 'Seventeen glyphs set one by one along the inside of the lower border, in an ivory slightly cooler than the cream above them.',
        blocks: [
          'The original’s typeface has not been identified. The credit is re-typeset with outlines of Lato Heavy as a close substitute, each letter placed optically on the arc rather than at even spacing.',
          'The badge names the service, not a department: through these decades the Forest Service was a branch of a larger department, and it kept its own name and its own marks.',
          { facts: [
            ['Glyphs', '17, individually positioned'],
            ['Substitute face', 'Lato Heavy (800), outlined'],
            ['Colour', '#F1F0DE']
          ] },
          { h: 'Where the service sat' },
          { links: [DEPARTMENT_LINK, MINISTRY_OF_FORESTS_LINK, OVALS_LINK] },
          { sources: [TIMELINE_SOURCE] }
        ]
      }
    }
  },
  order: ['overview', 'lettering', 'cigarette', 'credit']
}

// ── Don’t gamble with FIRE ──────────────────────────────────────────────────────────────────────

export const DONT_GAMBLE = {
  id: 'dont-gamble-with-fire',
  spotlight: { keep: ['field'] },
  regions: ['headline', 'dice', 'fire', 'caption'],
  parts: {
    overview: {
      label: 'Whole badge',
      box: box('dont-gamble-with-fire'),
      pad: 0.07,
      panel: {
        eyebrow: 'B. C. Forest Service · fire-prevention badge',
        heading: 'Don’t gamble with FIRE',
        lede: 'A pair of thrown dice between a rounded “don’t gamble!” and a block “FIRE”, with the service’s name down the left side of the rim.',
        blocks: [
          'The joke is in the type: “don’t gamble!” is soft and lowercase, almost cheerful; “FIRE” is square capitals, and “with” is laid over the dice to tie the two together.',
          { facts: [
            ['Issued by', 'B. C. Forest Service, from the caption'],
            ['Date', 'not established'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1233 × 1233 units; 43 paths, 10 circles, 12 ellipses']
          ] },
          { palette: [
            { name: 'Forest green (series)', value: '#003E2D' },
            { name: 'Warm cream', value: '#F1D8AC' }
          ] },
          { note: 'Printed blue. The photographed badge and its reconstruction are a deep blue (#01375D); here the field, the pips and the outline of “with” are set in DON’T DROP IT!’s forest green so the two badges read as one series. The cream is the badge’s own.' },
          { h: 'In the same series' },
          { links: [poster('dont-drop-it', 'overview', 'The green this one now shares')] }
        ]
      }
    },
    headline: {
      label: 'Headline',
      hint: '“don’t gamble!”',
      box: { x: 236, y: 79, w: 794, h: 378 },
      pad: 0.08,
      layer: '#headline',
      hit: 'shape',
      panel: {
        eyebrow: 'The headline',
        heading: 'don’t gamble!',
        em: 'in a soft, heavy lowercase',
        lede: 'Two lines of rounded display letters, each one drawn as its own shape from straight segments and Bézier curves — no font, and no automatic tracing.',
        blocks: [
          'The exclamation mark leans out to the right past the edge of the line, as on the badge. Each main letter is a separate, editable shape, so spacing can be adjusted letter by letter.',
          { facts: [
            ['Groups', 'word-dont, word-gamble'],
            ['Fill', '#F1D8AC, even-odd'],
            ['Typeface', 'none: custom display letters']
          ] }
        ]
      }
    },
    dice: {
      label: 'Dice',
      hint: 'two dice, faces and pips',
      box: { x: 242, y: 424, w: 670, h: 485 },
      pad: 0.08,
      layer: '#dice',
      hit: 'shape',
      panel: {
        eyebrow: 'The picture',
        heading: 'Two dice',
        em: 'mid-roll',
        lede: 'A rear die and a foreground die, each built from separate face shapes with elliptical pips, so they read as cubes turned in space rather than flat squares.',
        blocks: [
          'The rear die shows one, five and four; the foreground die one, three and two. Every pip is its own circle or ellipse, foreshortened with the face it sits on.',
          { facts: [
            ['Rear die', 'pips 1 / 5 / 4'],
            ['Foreground die', 'pips 1 / 3 / 2'],
            ['Outline', '3.4 units, in the field colour']
          ] }
        ]
      }
    },
    fire: {
      label: 'with FIRE',
      hint: 'the knockout and the block capitals',
      box: { x: 385, y: 719, w: 559, h: 374 },
      pad: 0.1,
      layer: '#word-with, #word-fire',
      hit: 'shape',
      panel: {
        eyebrow: 'The punchline',
        heading: 'with FIRE',
        lede: '“with” sits over the corner of the foreground die, outlined in the field colour so it cuts cleanly across it. “FIRE” closes the badge in heavy square capitals.',
        blocks: [
          'The outline on “with” is painted under its fill, so the letters keep their full width and the die stops short of them on every side.',
          { facts: [
            ['“with”', 'cream with a 3.8-unit knockout stroke'],
            ['“FIRE”', 'four custom outlined capitals']
          ] }
        ]
      }
    },
    caption: {
      label: 'Caption',
      hint: '“B. C. Forest Service”, down the rim',
      box: { x: 80, y: 454, w: 215, h: 580 },
      pad: 0.12,
      layer: '#forest-service-caption',
      panel: {
        eyebrow: 'The caption',
        heading: 'B. C. Forest Service',
        em: 'down the left side',
        lede: 'Where DON’T DROP IT! puts the service along the bottom, this badge runs it down the left of the rim, reading downwards.',
        blocks: [
          'The caption is individually placed, outlined glyphs of DejaVu Sans Bold — a substitute, not an identification of the historical face — with each full stop a separate circle.',
          { facts: [
            ['Glyphs', 'individually rotated along the arc'],
            ['Substitute face', 'DejaVu Sans Bold, outlined']
          ] },
          { h: 'Where the service sat' },
          { links: [DEPARTMENT_LINK, MINISTRY_OF_FORESTS_LINK, OVALS_LINK] },
          { sources: [TIMELINE_SOURCE] }
        ]
      }
    }
  },
  order: ['overview', 'headline', 'dice', 'fire', 'caption']
}

// ── REWARD — A Living Forest ────────────────────────────────────────────────────────────────────

const EMBLEM_PANEL = (others) => ({
  eyebrow: 'The emblem',
  heading: 'The evergreen emblem',
  em: 'before about 1973',
  lede: 'A rounded green badge holding a white silhouette of British Columbia, its three largest islands, and a dark evergreen standing over the mainland’s eastern edge.',
  blocks: [
    'This was the Forest Service’s mark before the oval designs. It is the same drawing on every poster in this series: one vector reconstruction, shared, rather than a fresh copy for each.',
    'It also dates the poster. With no printed date, the emblem is the best evidence for when this was issued — before about 1973, the date the emblem is believed to have been replaced, which has not yet been confirmed by a source.',
    { facts: [
      ['Badge', '#278F38'],
      ['Map and islands', '#FFFFFF'],
      ['Evergreen', '#00240B'],
      ['Drawing', 'badge, mainland, three islands, crown and trunk']
    ] },
    { h: 'See it as a logo' },
    { links: [EMBLEM_LINK, ...others, OVALS_LINK] }
  ]
})

export const REWARD = {
  id: 'reward-living-forest',
  spotlight: { keep: ['paper'] },
  regions: ['illustration', 'headline', 'bird', 'bear', 'message', 'service', 'emblem'],
  parts: {
    overview: {
      label: 'Whole poster',
      box: box('reward-living-forest'),
      pad: 0.03,
      panel: {
        eyebrow: 'British Columbia Forest Service · campfire poster',
        heading: 'REWARD',
        em: 'a living forest',
        lede: 'It reads like a wanted poster, and the reward is the forest itself: a bird and a bear under blue boughs, for anyone who observes the campfire regulations.',
        blocks: [
          'Navy lettering on warm paper, with the illustration in flat blues, yellows and lime inside an open rectangular frame that the bear’s paw and the boughs break out of.',
          { facts: [
            ['Issued by', 'British Columbia Forest Service'],
            ['Date', 'not printed; the emblem places it before about 1973'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '347 paths, no images; 297 × 417.7 mm']
          ] },
          { note: 'An interpretive reconstruction: paper damage, uneven light and print noise were left out, and fine feather, bark and face details are simplified. The emblem is the shared emblem drawing in its full colours; the photographed print shows it in a lighter lime.' },
          { h: 'In the same series' },
          { links: [poster('enjoy-protect-forests', 'overview', 'The other poster with the evergreen emblem')] }
        ]
      }
    },
    headline: {
      label: 'Headline',
      hint: 'REWARD ✱ A LIVING FOREST.',
      box: { x: 139, y: 132, w: 815, h: 239 },
      pad: 0.08,
      layer: '#reward-title, #asterisk, #living-forest',
      panel: {
        eyebrow: 'The headline',
        heading: 'REWARD',
        em: '✱ A LIVING FOREST.',
        lede: 'REWARD is custom-drawn, in heavy bracketed capitals; the line under it is a fitted sans, and a six-point asterisk ties the two together like a footnote.',
        blocks: [
          'The asterisk is the poster’s whole argument in one mark: the reward is qualified, and the qualification is the forest.',
          { facts: [
            ['REWARD', 'custom letters, outlined'],
            ['Second line', 'a fitted, slightly emboldened sans substitute'],
            ['Asterisk', 'six points, drawn'],
            ['Ink', 'navy #00264F']
          ] }
        ]
      }
    },
    illustration: {
      label: 'Illustration',
      hint: 'frame, boughs, trunk and ferns',
      box: { x: 200, y: 410, w: 631, h: 596 },
      pad: 0.05,
      layer: '#forest-illustration',
      panel: {
        eyebrow: 'The illustration',
        heading: 'Under the boughs',
        lede: 'An open navy frame holds a single trunk with blue boughs fanning off it, lime ferns along the bottom, and the two animals.',
        blocks: [
          'Everything is flat colour: separate panels for the plumage and foliage, designed bark ribbons clipped to the trunk, and needles clipped to each blade of bough. A few bough facets use partial opacity; there are no gradients.',
          { facts: [
            ['Layers', 'frame, boughs, trunk, bird, bear, foliage, paw'],
            ['Paths', '265 in the illustration alone'],
            ['Method', 'hand-authored Bézier curves; no tracing']
          ] }
        ]
      }
    },
    bird: {
      label: 'Bird',
      hint: 'body, plumage, eye, beak and feet',
      box: { x: 200, y: 410, w: 356, h: 342 },
      pad: 0.08,
      layer: '#bird',
      panel: {
        eyebrow: 'The bird',
        heading: 'A bird on the bough',
        lede: 'Blue, with an orange head, a yellow breast, lime shoulder markings and orange feet, perched on the upper left bough and looking out of the frame.',
        blocks: [
          'Its feathers are separate inlaid panels — tail, wing and shoulder — so each colour is its own shape rather than a stroke over a fill. The eye is geometric: concentric circles.',
          { facts: [
            ['Groups', 'tail feathers, feet, shoulder markings, wing panels, eye'],
            ['Simplified', 'the finest feather detail']
          ] }
        ]
      }
    },
    bear: {
      label: 'Bear',
      hint: 'head, mask, muzzle and paw',
      box: { x: 532, y: 688, w: 245, h: 318 },
      pad: 0.08,
      layer: '#bear, #bear-foreleg',
      panel: {
        eyebrow: 'The bear',
        heading: 'A bear in the ferns',
        lede: 'A round yellow bear with a brown eye mask, peering out from behind the ferns with one paw over the bottom of the frame.',
        blocks: [
          'The foreleg is a layer of its own, drawn last, so the paw sits in front of the foliage and the frame — the one place the illustration steps out of its box.',
          { facts: [
            ['Layers', 'bear (head, mask, muzzle), foreleg and paw'],
            ['Order', 'paw above the foreground foliage']
          ] }
        ]
      }
    },
    message: {
      label: 'Message',
      hint: 'OBSERVE CAMPFIRE REGULATIONS',
      box: { x: 152, y: 1042, w: 786, h: 165 },
      pad: 0.1,
      layer: '#observe-campfire, #regulations',
      panel: {
        eyebrow: 'The message',
        heading: 'OBSERVE CAMPFIRE REGULATIONS',
        lede: 'The instruction the reward is for, in two centred lines of condensed bold capitals.',
        blocks: [
          'The supporting lettering is a fitted, slightly emboldened sans-serif substitute converted to glyph paths; the original typeface has not been identified. A live-text version of the drawing keeps these lines editable in Nimbus Sans Bold.',
          { facts: [
            ['Lines', '2, centred'],
            ['Ink', 'navy #00264F'],
            ['Substitute face', 'Nimbus Sans Bold, outlined']
          ] }
        ]
      }
    },
    service: {
      label: 'Service name',
      hint: 'BRITISH COLUMBIA FOREST SERVICE',
      box: { x: 141, y: 1270, w: 650, h: 36 },
      pad: 0.3,
      layer: '#forest-service-name',
      panel: {
        eyebrow: 'The signature',
        heading: 'British Columbia Forest Service',
        lede: 'The poster is signed by the service, set in full on one line beside its emblem.',
        blocks: [
          'Through the years of this emblem the Forest Service was a branch within a provincial department rather than a ministry of its own. The Department of Forests was separated from the Department of Lands in 1976, and the Ministry of Forests Act came into force on 1 January 1979.',
          { h: 'Where the service sat' },
          { links: [DEPARTMENT_LINK, MINISTRY_OF_FORESTS_LINK] },
          { sources: [TIMELINE_SOURCE] }
        ]
      }
    },
    emblem: {
      label: 'Emblem',
      hint: 'the evergreen emblem, before about 1973',
      box: { x: 831, y: 1221, w: 112, h: 113 },
      pad: 0.5,
      layer: '#forest-service-emblem',
      panel: EMBLEM_PANEL([poster('enjoy-protect-forests', 'emblem', 'The same emblem on the sign')])
    }
  },
  order: ['overview', 'headline', 'illustration', 'bird', 'bear', 'message', 'service', 'emblem']
}

// ── Enjoy & Protect our Forests ─────────────────────────────────────────────────────────────────

export const ENJOY_PROTECT = {
  id: 'enjoy-protect-forests',
  spotlight: { keep: ['sign-background'] },
  regions: ['tree', 'character', 'headline', 'service', 'emblem'],
  parts: {
    overview: {
      label: 'Whole sign',
      box: box('enjoy-protect-forests'),
      pad: 0.03,
      panel: {
        eyebrow: 'British Columbia Forest Service · sign',
        heading: 'Enjoy & Protect our Forests',
        lede: 'A rounded cream panel in a tan border: a smiling evergreen with its branch around a red-hatted figure, red flowers at their feet, and the service’s name and emblem along the bottom.',
        blocks: [
          'Where REWARD bargains, this one simply asks: two verbs, the friendlier one first.',
          { facts: [
            ['Issued by', 'British Columbia Forest Service'],
            ['Date', 'not printed; the emblem places it before about 1973'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1122 × 1402 units; 78 paths, six named layers']
          ] },
          { note: 'A visual remake: the source texture, irregular edge and shading are replaced by flat colour and smooth curves. The face, the small map and the lettering are reconstructed approximations.' },
          { h: 'In the same series' },
          { links: [poster('reward-living-forest', 'overview', 'The campfire poster with the same emblem')] }
        ]
      }
    },
    headline: {
      label: 'Headline',
      hint: 'Enjoy & Protect our Forests',
      box: { x: 105, y: 109, w: 914, h: 87 },
      pad: 0.1,
      layer: '#reconstructed-headline',
      panel: {
        eyebrow: 'The headline',
        heading: 'Enjoy & Protect our Forests',
        lede: 'One line of tight, condensed bold lettering across the top of the panel, in mixed case — unusually soft for a government sign.',
        blocks: [
          'The headline uses custom, reconstructed letter shapes rather than a font. A live-text version sets it in Roboto Condensed Bold as a substitute; that is a stand-in, not an identification of the historical lettering.',
          { facts: [
            ['Letters', 'custom, outlined'],
            ['Live-text stand-in', 'Roboto Condensed Bold']
          ] }
        ]
      }
    },
    tree: {
      label: 'Smiling evergreen',
      hint: 'a tree with a face',
      box: { x: 239, y: 197, w: 701, h: 1023 },
      pad: 0.04,
      layer: '#smiling-tree',
      panel: {
        eyebrow: 'The tree',
        heading: 'A smiling evergreen',
        lede: 'A tall green conifer of stacked, swept-back tiers on a black trunk, with two round eyes and a wide smile set into its crown.',
        blocks: [
          'Its lowest branch reaches down and around the figure’s shoulders. That branch belongs to the figure’s layer, not the tree’s, so it can pass in front of the red shirt.',
          { facts: [
            ['Layers', 'crown, trunk, face'],
            ['Colours', 'flat green on a black trunk']
          ] }
        ]
      }
    },
    character: {
      label: 'Figure and flowers',
      hint: 'the red-hatted figure',
      box: { x: 172, y: 792, w: 606, h: 429 },
      pad: 0.06,
      layer: '#forest-character, #flowers',
      panel: {
        eyebrow: 'The figure',
        heading: 'Arms out, in a red hat',
        lede: 'A cartoon figure in a red hat and shirt, black trousers and cream boots, arms flung wide, beside the tree — with a clump of red flowers between them.',
        blocks: [
          'The cream face, hands and boots are solid shapes, not holes, so the drawing can sit on any background without the panel showing through them.',
          { facts: [
            ['Groups', 'feet, trousers, hands, hat and shirt; flowers'],
            ['Overlap', 'the tree’s branch is drawn in this layer']
          ] }
        ]
      }
    },
    service: {
      label: 'Service name',
      hint: 'BRITISH COLUMBIA FOREST SERVICE',
      box: { x: 140, y: 1275, w: 704, h: 31 },
      pad: 0.3,
      layer: '#service-name',
      panel: {
        eyebrow: 'The signature',
        heading: 'British Columbia Forest Service',
        lede: 'The service’s name along the foot of the panel in plain capitals, lighter than the headline.',
        blocks: [
          'It is outlined substitute lettering (Roboto Condensed Regular in the live-text version). As on REWARD, the name is the service’s, not a department’s.',
          { h: 'Where the service sat' },
          { links: [DEPARTMENT_LINK, MINISTRY_OF_FORESTS_LINK] },
          { sources: [TIMELINE_SOURCE] }
        ]
      }
    },
    emblem: {
      label: 'Emblem',
      hint: 'the evergreen emblem, before about 1973',
      box: { x: 896, y: 1171, w: 130, h: 131 },
      pad: 0.5,
      layer: '#forest-service-emblem',
      panel: EMBLEM_PANEL([poster('reward-living-forest', 'emblem', 'The same emblem on the campfire poster')])
    }
  },
  order: ['overview', 'headline', 'tree', 'character', 'service', 'emblem']
}

export const FOREST_SERVICE_POSTERS = {
  'dont-drop-it': DONT_DROP_IT,
  'dont-gamble-with-fire': DONT_GAMBLE,
  'reward-living-forest': REWARD,
  'enjoy-protect-forests': ENJOY_PROTECT
}
