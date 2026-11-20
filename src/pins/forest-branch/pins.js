// The Forest Branch's fire-prevention giveaways: their parts, where each sits in its drawing, what
// the panel says and what each part says in story mode. Data only, in the signs' format
// (src/signs/forest-service/signs.js). Boxes are in the drawing's own units, measured in Chromium
// from its named layers.

import { PINS } from '../catalogue.js'
import { diameterWords } from '../construction.js'

// ── Sources ─────────────────────────────────────────────────────────────────────────────────────

const PARMINTER = {
  label: 'John Parminter, “Protection as conservation: safeguarding British Columbia’s forests from fire, 1874–1921”, Ministry of Forests, 1981',
  href: 'https://www.for.gov.bc.ca/hfd/library/documents/bib30294.pdf'
}
const MACMILLAN = { label: 'H. R. MacMillan, “The Forest Fire: A National Danger and Its Remedy”, The Canadian Magazine, April 1915, pp. 549–553' }
const FOREST_SERVICE_TIMELINE = {
  label: 'BC Forest Service Centenary Society, BC Forest Service timeline',
  href: 'https://bcfs100.for.gov.bc.ca/bscripts/timeline.asp'
}

// ── Links ───────────────────────────────────────────────────────────────────────────────────────

const CARD_LINK = {
  label: 'England Expects: Prevent Forest Fires',
  note: 'Cards · a fire-prevention card under the Lands Department seal',
  to: { view: 'cards', card: 'england-expects' }
}
const SEAL_LINK = {
  label: 'The Lands Department seal',
  note: 'Internal Logos · Forests: the seal of the same years',
  to: { view: 'internal', internal: 'forests', 'internal-logo': 'forest-service-lands-department' }
}
const DEPARTMENT_LINK = {
  label: 'Department of Lands',
  note: 'Government · 1915: the department the Forest Branch sat in',
  to: { view: 'government', year: 1915, node: 'department-of-lands-1908' }
}
const BADGES_LINK = {
  label: 'The fire-prevention badges and decals',
  note: 'Posters · DON’T DROP IT!, Don’t gamble with FIRE and Be Careful',
  to: { view: 'posters', poster: 'dont-drop-it' }
}
const DECAL_LINK = {
  label: 'Be Careful: Prevent Forest Fires',
  note: 'Posters · a 1960 decal with the same plea across its base',
  to: { view: 'posters', poster: 'be-careful' }
}
const LOOKOUT_LINK = {
  label: 'LOOKOUT',
  note: 'Signs · the Forest Service’s triangular lookout sign',
  to: { view: 'signs', sign: 'lookout' }
}

// ── Prevent Forest Fires: Put Your Campfires Out ────────────────────────────────────────────────

// How the 3D view builds it (see ../construction.js). One photograph of the front is all there is.
// Its glare reads as a domed celluloid face; the size, the dome and the whole back are modelling
// choices, and the back may not be a pin at all.
const CAMPFIRES_CONSTRUCTION = {
  kind: 'printed-button',
  shape: 'oval',
  diameterMm: 42,
  aspect: 711 / 426,
  diameterStatus: 'illustrative',
  dome: 0.06,
  finish: 'celluloid',
  edge: 'rolled',
  back: 'tin-back',
  fitting: 'safety-pin',
  fittingStatus: 'generic',
  face: {
    svg: 'forest-branch-campfires.svg',
    background: '#E4D02B',
    view: { w: 1440, h: 880 },
    rim: { cx: 720, cy: 440, rx: 711, ry: 426 }
  },
  evidence: [
    'One photograph of the front; the back is not shown.',
    'A strong glare across a glossy, domed face: read as celluloid.',
    'The oval’s proportions are the reconstruction’s, 711 × 426, after a perspective correction estimated from one photograph.',
    'Celluloid-faced giveaways of the period were made as pin-back buttons and as pocket sharpening stones; the pin-back here is generic.'
  ],
  note: 'Illustrative: size, dome and back are not known. The back is not shown, and it may be a whetstone rather than a pin.'
}

const CAMPFIRES = {
  id: 'forest-branch-campfires',
  construction: CAMPFIRES_CONSTRUCTION,
  spotlight: { keep: ['fbc-oval-background'] },
  variations: {
    label: 'Face',
    options: [
      { id: 'photographed', label: 'As photographed', note: 'Yellow #E4D02B, red #851820 and a lighter credit line, #A36C23, as interpreted from the photograph.' },
      {
        id: 'one-red',
        label: 'Credit in red',
        note: 'The credit line in the same red as the rest, in case its lighter colour is thin or worn ink. An interpretation.',
        changed: 'with the credit line in red',
        swap: [['#A36C23', '#851820']]
      }
    ]
  },
  // The oval takes the bare face; the lettering sits over it, found by its own ink where the arcs'
  // boxes overlap.
  regions: ['oval', 'campfires', 'title', 'woods', 'matches', 'credit'],
  parts: {
    overview: {
      label: 'Whole oval',
      box: PINS['forest-branch-campfires'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'British Columbia Forest Branch · giveaway',
        heading: 'Prevent Forest Fires',
        em: 'Put Your Campfires Out',
        lede: 'A glossy yellow oval with six lines of red lettering, presented by the Forest Branch of the Lands Department.',
        blocks: [
          { facts: [
            ['Given by', 'the Forest Branch, Lands Department, Victoria, from its credit line'],
            ['Date', 'undated; its wording places it in 1912–1945'],
            ['Face', 'glossy and domed in the photograph: celluloid, on that reading'],
            ['Pin or whetstone', 'not known: the back is not shown'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1440 × 880 units: the oval and nine layers of outlined lettering, 129 shapes'],
            ['Size in 3D', diameterWords(CAMPFIRES_CONSTRUCTION)],
            ['Back in 3D', 'generic: a tin back and safety pin; the real back is unknown, and it may be a whetstone']
          ] },
          { note: 'The proportions come from a perspective correction estimated from one photograph, and the colours are interpreted, not measured. The lettering is redrawn, not an identified typeface.' },
          { h: 'The same campaign' },
          { links: [CARD_LINK, SEAL_LINK, DEPARTMENT_LINK, BADGES_LINK, DECAL_LINK, LOOKOUT_LINK] }
        ]
      },
      story: [
        'A yellow oval with six lines of red lettering: PREVENT FOREST FIRES over the top, PUT YOUR CAMPFIRES OUT across the middle, and a credit to the Forest Branch round the foot.',
        'Read it as a camper would: the warning, the place, the two instructions, and who handed it out.'
      ]
    },
    title: {
      label: 'PREVENT FOREST FIRES',
      hint: 'the arch',
      box: { x: 153, y: 64, w: 1090, h: 247 },
      pad: 0.06,
      layer: '#fbc-upper-title',
      hit: 'shape',
      panel: {
        eyebrow: 'The headline',
        heading: 'PREVENT FOREST FIRES',
        lede: 'Eighteen tall, condensed capitals on an arch that follows the top of the oval.',
        blocks: [
          { facts: [
            ['Lettering', 'custom outlines, drawn from the photograph'],
            ['Colour', '#851820, as photographed']
          ] },
          { links: [DECAL_LINK] }
        ]
      },
      story: [
        'PREVENT FOREST FIRES arches over the top in tall, condensed red capitals.',
        'The plea lasted: the same three words run across the base of the Forest Service’s Be Careful decal of 1960.'
      ]
    },
    woods: {
      label: 'WHEN IN THE WOODS',
      hint: 'where',
      box: { x: 348, y: 189, w: 743, h: 111 },
      pad: 0.1,
      layer: '#fbc-when-in-the-woods',
      hit: 'shape',
      panel: {
        eyebrow: 'Where',
        heading: 'WHEN IN THE WOODS',
        lede: 'Fourteen wide capitals on a gentler arch, under the headline.',
        blocks: [
          { facts: [['Letters', 'all rebuilt from the photograph: the pointed W, the broad T, the short E bars']] }
        ]
      },
      story: [
        'WHEN IN THE WOODS, in smaller and wider capitals, names the place the two instructions below are for.'
      ]
    },
    campfires: {
      label: 'PUT YOUR CAMPFIRES OUT',
      hint: 'the first instruction',
      box: { x: 93, y: 334, w: 1258, h: 192 },
      pad: 0.06,
      layer: '#fbc-main-put, #fbc-middle-your, #fbc-middle-campfires, #fbc-main-out',
      panel: {
        eyebrow: 'The first instruction',
        heading: 'PUT YOUR CAMPFIRES OUT',
        lede: 'PUT and OUT, the largest letters on the oval, either side of YOUR CAMPFIRES in two smaller lines.',
        blocks: [
          { facts: [
            ['PUT and OUT', 'custom outlines, 190 units tall'],
            ['Detail', 'a small opening in the A of CAMPFIRES, faint in the photograph, kept']
          ] }
        ]
      },
      story: [
        'Then the first instruction, in the largest letters on the oval: PUT and OUT at either end, with YOUR CAMPFIRES set small between them.',
        'Even from across a camp, PUT … OUT carries the message.'
      ]
    },
    matches: {
      label: 'DO NOT DROP…',
      hint: 'the second instruction',
      box: { x: 165, y: 532, w: 1118, h: 251 },
      pad: 0.06,
      layer: '#fbc-do-not-drop, #fbc-lower-display-lettering',
      hit: 'shape',
      panel: {
        eyebrow: 'The second instruction',
        heading: 'DO NOT DROP LIGHTED MATCHES OR TOBACCO',
        lede: 'DO NOT DROP in wide capitals, then the rest in heavy, condensed capitals curving along the lower rim.',
        blocks: [
          { facts: [['Lettering', 'custom outlines; the curve follows the oval']] },
          { links: [BADGES_LINK] }
        ]
      },
      story: [
        'The second instruction curves beneath it: DO NOT DROP, then LIGHTED MATCHES OR TOBACCO in heavy capitals along the lower rim.',
        'Campers get one line and smokers the other; the oval asks nothing else of its reader.'
      ]
    },
    credit: {
      label: 'Presented by Forest Branch',
      hint: 'the credit',
      box: { x: 165, y: 636, w: 1093, h: 186 },
      pad: 0.06,
      layer: '#fbc-attribution',
      hit: 'shape',
      panel: {
        eyebrow: 'The credit',
        heading: 'Presented by Forest Branch',
        em: 'Lands Dept., Victoria, B.C.',
        lede: 'One fine line in a lighter brown, following the rim: who gave the oval away.',
        blocks: [
          { facts: [
            ['Wording', 'PRESENTED BY FOREST BRANCH. LANDS DEPT. VICTORIA B.C.'],
            ['Forest Branch', 'created within the Department of Lands in February 1912'],
            ['Forest Service', 'its name from 1945, in the BC Forest Service timeline'],
            ['Lettering', 'fitted from Nimbus Sans outlines, not an identified typeface']
          ] },
          { note: 'The period after BRANCH and the last dot of B.C. are faint in the photograph. A department’s name dates the wording, not the making: old stock could be given out later.' },
          { links: [SEAL_LINK, DEPARTMENT_LINK, CARD_LINK] },
          { sources: [FOREST_SERVICE_TIMELINE] }
        ]
      },
      story: [
        'The fine line round the foot names the giver: PRESENTED BY FOREST BRANCH. LANDS DEPT. VICTORIA B.C.',
        'The Forest Act of 1912 set up a Forest Branch within the Department of Lands, and in 1915 its chief forester, H. R. MacMillan, wrote that prevention relied on the public’s “pride of citizenship”.',
        'Parminter’s history of those years records material sent to schools and cinemas, and whetstones for loggers and sportsmen that carried fire-prevention messages.'
      ],
      storySources: [FOREST_SERVICE_TIMELINE, MACMILLAN, PARMINTER]
    },
    oval: {
      label: 'Oval',
      hint: 'pin or whetstone?',
      box: { x: 9, y: 14, w: 1422, h: 852 },
      pad: 0.04,
      layer: '#fbc-oval-background',
      panel: {
        eyebrow: 'The object',
        heading: 'A glossy oval',
        em: 'pin or whetstone',
        lede: 'Yellow, domed and glossy in the photograph, which reads as a celluloid face. What is behind it is not known.',
        blocks: [
          { palette: [{ name: 'Yellow', value: '#E4D02B' }, { name: 'Red', value: '#851820' }, { name: 'Credit', value: '#A36C23' }] },
          { facts: [
            ['Face', 'domed and glossy, from the glare in the photograph'],
            ['Back', 'not shown'],
            ['Could be', 'a pin-back button, or a celluloid-topped pocket whetstone'],
            ['Oval', '711 × 426 units, completed symmetrically: the photograph clips its left edge']
          ] },
          { note: 'A whetstone is possible, not established: the Forest Branch did give whetstones out, but nothing on the front says this is one. The 3D view shows a generic pin-back.' },
          { sources: [PARMINTER, MACMILLAN] }
        ]
      },
      story: [
        'The photograph shows a glossy, domed oval with a strong glare, which reads as a celluloid face; its back is not shown.',
        'Celluloid-faced “Presented by” giveaways of the period were made both as pin-back buttons and as celluloid-topped pocket sharpening stones (round ones are well known; an oval one is not confirmed), and the Forest Branch did give whetstones out. Which this one is, the front cannot tell.'
      ],
      storySources: [PARMINTER, MACMILLAN]
    }
  },
  order: ['overview', 'title', 'woods', 'campfires', 'matches', 'credit', 'oval']
}

export const FOREST_BRANCH_PINS = { 'forest-branch-campfires': CAMPFIRES }
