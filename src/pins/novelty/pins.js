// Novelty and souvenir buttons: their parts, where each sits in its drawing, what the panel says and
// what each part says in story mode. Data only, in the signs' format (src/signs/forest-service/signs.js).

import { PINS } from '../catalogue.js'
import { diameterWords } from '../construction.js'

// ── Sources ─────────────────────────────────────────────────────────────────────────────────────

const DNB = {
  label: 'Dun & Bradstreet business directory, Jim Pattison Enterprises Ltd.',
  href: 'https://www.dnb.com/business-directory/company-profiles/jim-pattison-enterprises-ltd.286615881405ae6e330780a939b5ed0a'
}
const ENCYCLOPEDIA_PATTISON = {
  label: 'The Canadian Encyclopedia, “James Allen Pattison”',
  href: 'https://www.thecanadianencyclopedia.ca/en/article/james-allen-pattison'
}
const WIKIPEDIA_GROUP = {
  label: 'Wikipedia, “Jim Pattison Group”',
  href: 'https://en.wikipedia.org/wiki/Jim_Pattison_Group'
}
const ENCYCLOPEDIA_EXPO = {
  label: 'The Canadian Encyclopedia, “Expo 86”',
  href: 'https://thecanadianencyclopedia.ca/index.php/en/article/expo-86'
}
const CBC = {
  label: 'CBC News, on Pattison and Expo 86',
  href: 'https://www.cbc.ca/1.3545161'
}
const MONITOR = {
  label: 'The Christian Science Monitor, 5 September 1986',
  href: 'https://csmonitor.com/1986/0905/oexpo.html'
}

// ── Links ───────────────────────────────────────────────────────────────────────────────────────

const WELCOME_LINKS = [
  {
    label: 'Expo 86, Robert Davidson’s poster',
    note: 'Posters · the fair Pattison ran, in its art poster',
    to: { view: 'posters', poster: 'expo-86-davidson' }
  },
  {
    label: 'Super, Natural British Columbia',
    note: 'Signs · the Province’s own welcome sign',
    to: { view: 'signs', sign: 'super-natural' }
  }
]

// ── Welcome to B.C. ─────────────────────────────────────────────────────────────────────────────

// How the 3D view builds it (see ../construction.js). One straight-on photograph is all there is:
// the size, the dome and the whole back are modelling choices. 1½ in is a common pin-back size.
const WELCOME_CONSTRUCTION = {
  kind: 'printed-button',
  diameterMm: 38,
  diameterStatus: 'illustrative',
  dome: 0.02,
  edge: 'rolled',
  back: 'tin-back',
  fitting: 'safety-pin',
  fittingStatus: 'generic',
  face: { svg: 'welcome-bc-pattison.svg', background: '#F1F2E9' },
  evidence: [
    'One straight-on photograph of the face; the back is not shown.',
    'The face is matte, with no glare and no distortion of the lettering: flat or very slightly domed.',
    'Shading only in a narrow band at the rim: a rolled edge.',
    'A scuffed face and small chips at the rim suggest ink printed on metal; an inference.'
  ]
}

const WELCOME_BC = {
  id: 'welcome-bc-pattison',
  construction: WELCOME_CONSTRUCTION,
  spotlight: { keep: ['wbc-pin-face'] },
  variations: {
    label: 'Face',
    options: [
      { id: 'warm', label: 'Pale warm', note: 'The face as interpreted from the photograph, #F1F2E9.' },
      { id: 'white', label: 'White', note: 'A pure white face, as the package also supplies it.', changed: 'on a white face', swap: [['#F1F2E9', '#FFFFFF']] }
    ]
  },
  // The face takes the bare button; the two blocks of lettering sit over it.
  regions: ['face', 'headline', 'division'],
  parts: {
    overview: {
      label: 'Whole button',
      box: PINS['welcome-bc-pattison'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'Novelty button',
        heading: 'Welcome to B.C.',
        em: 'A Division of Jim Pattison Enterprises',
        lede: 'A plain pin-back button: WELCOME TO B.C. in wide capitals over a rule, then a corporate credit in typewriter letters.',
        blocks: [
          { facts: [
            ['Maker', 'unknown'],
            ['Date', 'undated; no catalogue record found'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1000 × 1000 units: the face, six lines of outlined letters and the rule'],
            ['Size in 3D', diameterWords(WELCOME_CONSTRUCTION)],
            ['Back in 3D', 'generic: a plain tin back and safety pin, since the back is not shown']
          ] },
          { note: 'The typeface is unidentified: the headline letters are drawn for this button, the lower lines rebuilt from Latin Modern Mono and Nimbus Mono PS outlines. The diameter is unknown and the face colour is interpreted.' },
          { h: 'Related' },
          { links: WELCOME_LINKS }
        ]
      },
      story: [
        'A plain white pin-back button: WELCOME TO B.C. in wide capitals, underlined, then in typewriter letters “A Division of Jim Pattison Enterprises”.',
        'Its maker and date are unknown, and no catalogue record of it was found.'
      ]
    },
    division: {
      label: 'A Division of…',
      hint: 'the credit',
      box: { x: 216, y: 550, w: 658, h: 239 },
      pad: 0.08,
      layer: '#wbc-line-4, #wbc-line-5, #wbc-line-6',
      panel: {
        eyebrow: 'The credit',
        heading: 'A Division of Jim Pattison Enterprises',
        lede: 'Three lines in tight typewriter letters, worded the way the Pattison group named its own businesses.',
        blocks: [
          { facts: [['Lettering', 'rebuilt from Latin Modern Mono and Nimbus Mono PS outlines']] },
          { sources: [DNB] }
        ]
      },
      story: [
        '“A division of Jim Pattison Enterprises” is how the Pattison group’s own businesses were named, as in “Canadian Fishing Company, A Division of Jim Pattison Enterprises Ltd.”',
        'Jim Pattison is a Vancouver businessman, the chairman, chief executive and sole owner of the Jim Pattison Group.'
      ],
      storySources: [DNB, ENCYCLOPEDIA_PATTISON, WIKIPEDIA_GROUP]
    },
    headline: {
      label: 'WELCOME TO B.C.',
      hint: 'with its rule',
      box: { x: 207, y: 247, w: 683, h: 230 },
      pad: 0.08,
      layer: '#wbc-line-1, #wbc-line-2, #wbc-line-3, #wbc-underline',
      panel: {
        eyebrow: 'The headline',
        heading: 'WELCOME TO B.C.',
        lede: 'Three short lines of widely spaced capitals, a little right of centre, with a rounded rule under B.C.',
        blocks: [
          { facts: [
            ['W and M', 'drawn for this button'],
            ['Rule', 'a separate rounded bar, 406 × 8 units']
          ] }
        ]
      },
      story: [
        'Put over that credit, WELCOME TO B.C. treats the whole province as one more Pattison division.',
        'That is an interpretation: a joke, on this reading, about one businessman’s reach.'
      ]
    },
    face: {
      label: 'Face',
      hint: 'plain, undated',
      box: { x: 0, y: 0, w: 1000, h: 1000 },
      pad: 0.04,
      layer: '#wbc-pin-face',
      panel: {
        eyebrow: 'The face',
        heading: 'A plain face',
        em: 'and no date',
        lede: 'A pale face with nothing on it but the lettering: no maker’s mark and no year.',
        blocks: [
          { palette: [{ name: 'Face', value: '#F1F2E9' }, { name: 'Ink', value: '#141614' }] },
          { note: 'The face colour is an interpretation; switch to the white face on the whole button.' }
        ]
      },
      story: [
        'The province’s 1986 world’s fair was run by the Expo 86 Corporation, with Pattison as chairman of the board and later president, reportedly for $1 a year.',
        'It drew more than 22 million visitors; a contemporary report called him a hard-nosed entrepreneur, and the BIE’s final report criticised the fair’s “confrontational management style”.',
        'The Expo years are the likeliest setting for the joke, but nothing on the button dates it.'
      ],
      storySources: [ENCYCLOPEDIA_EXPO, CBC, MONITOR]
    }
  },
  order: ['overview', 'division', 'headline', 'face']
}

export const NOVELTY_PINS = { 'welcome-bc-pattison': WELCOME_BC }
