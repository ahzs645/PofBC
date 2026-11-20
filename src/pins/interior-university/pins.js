// The Interior University Society's campaign pins and buttons: their parts, where each sits in its
// drawing, what the panel says and what each part says in story mode. Data only, in the signs'
// format (src/signs/forest-service/signs.js). The drawings are the society's reconstruction kit as
// served in public/unbc-origins/svg/, their ids prefixed on the stage (../prefixIds.js): `prefix` is
// that prefix, and every layer named here carries it.
//
// All three are modern reconstructions from photographs, as their records say
// (research/identity/unbc-origins/assets.json); none is an original master.

import { PINS } from '../catalogue.js'

// ── Sources ─────────────────────────────────────────────────────────────────────────────────────
// As the UNBC origins collection cites them (src/gallery/unbcHistoryData.js).

const INCORPORATION = {
  label: 'British Columbia Gazette, 17 December 1987, p. 1767: Incorporations, 1 December 1987, S-23084',
  href: 'https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz1/hbcgaz1/537064649'
}
const CAMPAIGN = {
  label: 'UNBC, The Public Campaign for a Northern University',
  href: 'https://www.unbc.ca/about-unbc/public-campaign-northern-university'
}
const ACT = {
  label: 'University of Northern British Columbia Act, SBC 1990, c. 28',
  href: 'https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/90028'
}

// ── Links ───────────────────────────────────────────────────────────────────────────────────────

const IUS_LINKS = [
  {
    label: 'The Interior University Society’s collection',
    note: 'Logos · all 26 reconstructions from the society’s kit, with their records',
    to: { view: 'gallery', logos: 'collected-interior-university-society' }
  },
  {
    label: 'The University of Northern British Columbia',
    note: 'Logos · the university the campaign helped create, and its marks',
    to: { view: 'gallery', subject: 'university-of-northern-bc' }
  }
]
const RECONSTRUCTED = 'reconstruction from a photograph'

// ── The society's enamel pin ────────────────────────────────────────────────────────────────────

const ENAMEL_PIN = {
  id: 'ius-enamel-pin',
  file: 'ius-enamel-pin.svg',
  prefix: 'iusp-',
  spotlight: {},
  regions: ['body', 'bars', 'lettering'],
  parts: {
    overview: {
      label: 'Whole pin',
      box: PINS['ius-enamel-pin'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'Interior University Society · pin',
        heading: 'Interior University Society',
        em: 'enamel pin',
        lede: 'The society’s name in three lines of black capitals, each over a burgundy bar, on orange enamel.',
        blocks: [
          { facts: [
            ['Society', 'incorporated 1 December 1987'],
            ['Date', 'undated'],
            ['Status', RECONSTRUCTED],
            ['Drawing', '1008 × 748 units, flat colour']
          ] },
          { note: 'A flat reconstruction, not a manufacturing drawing: the size, finish, colours and lettering weight are approximate.' },
          { h: 'The campaign' },
          { links: IUS_LINKS }
        ]
      },
      story: [
        'The Interior University Society incorporated on 1 December 1987 to campaign for a university in the North. Its pin carries nothing but its name.'
      ],
      storySources: [INCORPORATION]
    },
    lettering: {
      label: 'Lettering',
      hint: 'INTERIOR UNIVERSITY SOCIETY',
      box: { x: 164, y: 72, w: 768, h: 525 },
      pad: 0.08,
      layer: '#iusp-pin-word-interior, #iusp-pin-word-interior-optical-black-inlay, #iusp-pin-word-university, #iusp-pin-word-university-optical-black-inlay, #iusp-pin-word-society, #iusp-pin-word-society-optical-black-inlay',
      hit: 'shape',
      panel: {
        eyebrow: 'The lettering',
        heading: 'INTERIOR UNIVERSITY SOCIETY',
        lede: 'Heavy black capitals, each letter in a pale metal surround, set flush right.',
        blocks: [
          { facts: [
            ['Outlines', 'fitted from Nimbus Sans Bold'],
            ['Typeface', 'not identified']
          ] }
        ]
      },
      story: [
        'The name is stacked and set flush right, so the three words step out to the left as they get longer.'
      ]
    },
    bars: {
      label: 'Bars',
      hint: 'one under each word',
      box: { x: 75, y: 204, w: 865, h: 458 },
      pad: 0.06,
      layer: '#iusp-pin-bar-1, #iusp-pin-bar-2, #iusp-pin-bar-3',
      hit: 'shape',
      panel: {
        eyebrow: 'The bars',
        heading: 'Three bars',
        lede: 'A burgundy bar under each word, each shorter than the one above, its left end cut to the pin’s slanted edge.',
        blocks: [
          { palette: [{ name: 'Burgundy', value: '#78353A' }] }
        ]
      },
      story: [
        'Under each word a burgundy bar, shorter each time, following the pin’s long diagonal edge.'
      ]
    },
    body: {
      label: 'Body',
      hint: 'orange enamel, metal edge',
      box: { x: 4, y: 4, w: 1000, h: 740 },
      pad: 0.04,
      layer: '#iusp-metal-body, #iusp-enamel-field',
      panel: {
        eyebrow: 'The body',
        heading: 'Five sides',
        lede: 'A rectangle with its lower left corner cut away on a long diagonal: orange enamel in a pale metal edge.',
        blocks: [
          { palette: [
            { name: 'Enamel', value: '#C7722D' },
            { name: 'Metal', value: '#D8D4C8' },
            { name: 'Black', value: '#1D1D1B' }
          ] },
          { note: 'The outline is estimated from the photograph, not a measured die line, and the colours are uncalibrated.' }
        ]
      },
      story: [
        'Orange enamel in a pale metal edge. The size, the finish and the colours come from a photograph and are approximate.'
      ]
    }
  },
  order: ['overview', 'lettering', 'bars', 'body']
}

// ── Northern U ──────────────────────────────────────────────────────────────────────────────────

const NORTHERN_U = {
  id: 'northern-u-button',
  file: 'northern-u-button.svg',
  prefix: 'nub-',
  spotlight: {},
  regions: ['face', 'northern', 'u'],
  parts: {
    overview: {
      label: 'Whole button',
      box: PINS['northern-u-button'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'Interior University Society · button',
        heading: 'Northern U',
        lede: 'An orange campaign button: Northern in a soft, heavy serif, and one large U.',
        blocks: [
          { facts: [
            ['Campaign', 'Interior University Society'],
            ['Date', 'undated'],
            ['Status', RECONSTRUCTED],
            ['Drawing', '1000 × 1000 units, flat colour, no glare or dome']
          ] },
          { note: 'Version 1.2 of the reconstruction. The original typeface, the orange and the diameter are unconfirmed.' },
          { h: 'The campaign' },
          { links: IUS_LINKS }
        ]
      },
      story: [
        'In 1988, 16,000 people paid $5 to join the society in support of a university in the North. This button says what they wanted in two words.'
      ],
      storySources: [CAMPAIGN]
    },
    northern: {
      label: 'Northern',
      hint: 'the word',
      box: { x: 96, y: 327, w: 800, h: 137 },
      pad: 0.12,
      layer: '#nub-northern-serif-word',
      panel: {
        eyebrow: 'The word',
        heading: 'Northern',
        lede: 'A capital N drawn for the reconstruction, with Bookman-derived lowercase fitted to the photograph.',
        blocks: [
          { facts: [['Typeface', 'not identified; Bookman-like']] }
        ]
      },
      story: [
        'Northern, in a soft, heavy serif with a capital N drawn on its own.'
      ]
    },
    u: {
      label: 'U',
      hint: 'the large letter',
      box: { x: 340, y: 507, w: 320, h: 280 },
      pad: 0.12,
      layer: '#nub-large-U',
      panel: {
        eyebrow: 'The letter',
        heading: 'U',
        lede: 'One large U, built separately from the serif, stem and bowl seen in the photograph.'
      },
      story: [
        'And under it a single U: a university, in one letter.'
      ]
    },
    face: {
      label: 'Face',
      hint: 'orange',
      box: { x: 10, y: 10, w: 980, h: 980 },
      pad: 0.04,
      layer: '#nub-orange-button-face',
      panel: {
        eyebrow: 'The face',
        heading: 'Orange',
        lede: 'A plain orange face, its colour taken from the photograph.',
        blocks: [
          { palette: [{ name: 'Orange', value: '#DE8D3F' }, { name: 'Black', value: '#1D1D1B' }] }
        ]
      },
      story: [
        'All on orange. The orange, like the button’s size, is unconfirmed.'
      ]
    }
  },
  order: ['overview', 'northern', 'u', 'face']
}

// ── I say yes to Northern Interior University ───────────────────────────────────────────────────

const SAY_YES = {
  id: 'say-yes-button',
  file: 'say-yes-button.svg',
  prefix: 'syb-',
  spotlight: {},
  regions: ['face', 'pledge', 'name', 'yes'],
  parts: {
    overview: {
      label: 'Whole button',
      box: PINS['say-yes-button'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'Interior University Society · button',
        heading: 'I say yes',
        em: 'to Northern Interior University',
        lede: 'A cream button in a black ring: a pledge in the wearer’s own voice, with YES said twice.',
        blocks: [
          { facts: [
            ['Campaign', 'Interior University Society'],
            ['Date', 'undated'],
            ['Status', RECONSTRUCTED],
            ['Drawing', '1000 × 1000 units, the circle rebuilt without the photograph’s perspective']
          ] },
          { note: 'The typefaces, the paper tint and the size are approximate. Interior University was campaign wording, not an adopted name for a university.' },
          { h: 'The campaign' },
          { links: IUS_LINKS }
        ]
      },
      story: [
        'A button that asks its wearer to vote, in effect, for a university. Read it from the top.'
      ]
    },
    pledge: {
      label: 'I SAY YES TO',
      hint: 'the pledge',
      box: { x: 193, y: 65, w: 615, h: 242 },
      pad: 0.08,
      layer: '#syb-top-I, #syb-say-yes-to',
      hit: 'shape',
      panel: {
        eyebrow: 'The pledge',
        heading: 'I SAY YES TO',
        lede: 'Tall serif capitals, the I alone on the top line.',
        blocks: [
          { facts: [['Outlines', 'fitted from Nimbus Roman Bold']] }
        ]
      },
      story: [
        'I, alone at the top, then SAY YES TO: a pledge in the first person.'
      ]
    },
    name: {
      label: 'Northern Interior University',
      hint: 'three kinds of lettering',
      box: { x: 59, y: 326, w: 881, h: 607 },
      pad: 0.05,
      layer: '#syb-northern-geometric, #syb-interior-collegiate-outline, #syb-university-bottom-arc',
      hit: 'shape',
      panel: {
        eyebrow: 'The name',
        heading: 'NORTHERN INTERIOR UNIVERSITY',
        lede: 'NORTHERN in geometric capitals, INTERIOR in outlined collegiate letters, UNIVERSITY around the foot.',
        blocks: [
          { facts: [['NORTHERN and INTERIOR', 'drawn for the reconstruction'], ['UNIVERSITY', 'fitted serif outlines on an arc']] },
          { note: 'The university the legislature established in 1990 was named the University of Northern British Columbia.' },
          { sources: [ACT] }
        ]
      },
      story: [
        'NORTHERN, INTERIOR and UNIVERSITY, each in its own lettering. Interior University was the campaign’s wording; the university established by the 1990 Act was named the University of Northern British Columbia.'
      ],
      storySources: [ACT]
    },
    yes: {
      label: 'YES',
      hint: 'in the middle',
      box: { x: 346, y: 620, w: 308, h: 103 },
      pad: 0.15,
      layer: '#syb-center-yes',
      panel: {
        eyebrow: 'The answer',
        heading: 'YES',
        lede: 'YES again, inside the arc of UNIVERSITY.'
      },
      story: [
        'And YES again in the middle, in case the answer was not clear.'
      ]
    },
    face: {
      label: 'Face',
      hint: 'cream, in a black ring',
      box: { x: 10, y: 10, w: 980, h: 980 },
      pad: 0.04,
      layer: '#syb-outer-printed-ring, #syb-cream-button-face',
      panel: {
        eyebrow: 'The face',
        heading: 'Cream in a black ring',
        lede: 'A printed black ring around a cream face, the circle redrawn true.',
        blocks: [
          { palette: [{ name: 'Cream', value: '#F1E4C5' }, { name: 'Black', value: '#1D1D1B' }] }
        ]
      },
      story: [
        'A cream face in a black printed ring. The tint and the size are approximate.'
      ]
    }
  },
  order: ['overview', 'pledge', 'name', 'yes', 'face']
}

export const INTERIOR_UNIVERSITY_PINS = {
  'ius-enamel-pin': ENAMEL_PIN,
  'northern-u-button': NORTHERN_U,
  'say-yes-button': SAY_YES
}
