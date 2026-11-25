// The Forest Service's cards: their parts, where each sits in its drawing, what the panel says and
// what each part says in story mode. Data only, in the signs' format (src/signs/forest-service/signs.js):
// a string block is a paragraph; { h }, { facts }, { note }, { links } and { sources } are what they
// say. A source with no `href` is a printed one, cited by its title. `storySources` are what a
// story chapter rests on (src/posters/ui/StoryRail.jsx).

import { CARDS } from '../catalogue.js'

// ── Sources ─────────────────────────────────────────────────────────────────────────────────────
// Named as the research notes name them; no address is given where the notes give none.

const NAM = { label: 'National Army Museum, London: British recruiting poster, “England Expects Every Man to do His Duty and Join the Army To-day”, 1914' }
const TE_PAPA = { label: 'Te Papa: the same recruiting poster, catalogued October 1914, and a 1939 national-service poster using “England expects”' }
const MACMILLAN = { label: 'H. R. MacMillan, “The Forest Fire: A National Danger and Its Remedy”, The Canadian Magazine, April 1915, pp. 549–553' }
const PARMINTER = {
  label: 'John Parminter, “Protection as conservation: safeguarding British Columbia’s forests from fire, 1874–1921”, Ministry of Forests, 1981',
  href: 'https://www.for.gov.bc.ca/hfd/library/documents/bib30294.pdf'
}
const ROOT_AND_BRANCH = { label: 'Root and Branch, vol. II, no. 12, cover, catalogued as 1924' }
const FOREST_SERVICE_TIMELINE = {
  label: 'BC Forest Service Centenary Society, BC Forest Service timeline',
  href: 'https://bcfs100.for.gov.bc.ca/bscripts/timeline.asp'
}

// ── Links ───────────────────────────────────────────────────────────────────────────────────────

const SEAL_LINK = {
  label: 'The Lands Department seal',
  note: 'Departmental Logos · Forests: the seal on its own, its colourways and history',
  to: { view: 'internal', internal: 'forests', 'internal-logo': 'forest-service-lands-department' }
}
const DEPARTMENT_LINK = {
  label: 'Department of Lands',
  note: 'Government · 1924: the department the Forest Service sat in',
  to: { view: 'government', year: 1924, node: 'department-of-lands-1908' }
}
const FIRE_LINKS = [
  {
    label: 'The fire-prevention badges and decals',
    note: 'Posters · DON’T DROP IT!, Don’t gamble with FIRE and Be Careful',
    to: { view: 'posters', poster: 'dont-drop-it' }
  },
  {
    label: 'Be Careful: Prevent Forest Fires',
    note: 'Posters · a 1960 decal with the same plea across its base',
    to: { view: 'posters', poster: 'be-careful' }
  },
  {
    label: 'LOOKOUT',
    note: 'Signs · the service’s triangular lookout sign',
    to: { view: 'signs', sign: 'lookout' }
  },
  {
    label: 'FOREST CLOSURE, Zone 3',
    note: 'Signs · a 1960 closure sign with a changeable strip',
    to: { view: 'signs', sign: 'forest-closure' }
  }
]

// ── England Expects ─────────────────────────────────────────────────────────────────────────────

export const ENGLAND_EXPECTS = {
  id: 'england-expects',
  spotlight: { keep: ['fsc-paper'] },
  variations: {
    label: 'Print',
    options: [
      { id: 'paper', label: 'Warm paper', note: 'The card’s paper as photographed, #E8DDB4, with dark ink #282C20. An interpretation, not a measured colour.' },
      {
        id: 'white',
        label: 'Black on white',
        note: 'The same drawing in black on white, as the package also supplies it.',
        changed: 'in black on white',
        swap: [['#E8DDB4', '#FFFFFF'], ['#282C20', '#000000']]
      }
    ]
  },
  // The border's box takes the bare card; the seal and the two lines sit over it.
  regions: ['border', 'emblem', 'duty', 'yours'],
  parts: {
    overview: {
      label: 'Whole card',
      box: CARDS['england-expects'].view,
      pad: 0.05,
      panel: {
        eyebrow: 'British Columbia Forest Service · card',
        heading: 'England Expects',
        em: 'Do Yours',
        lede: 'Nelson’s call to duty over a plea to prevent forest fires, under the Forest Service’s Lands Department seal.',
        blocks: [
          { facts: [
            ['Issued by', 'British Columbia Forest Service, from its seal'],
            ['Date', 'undated; the seal’s wording points to about 1912–1945'],
            ['Rebuilt from', 'one supplied photograph'],
            ['Drawing', '1050 × 500 units: paper, border, seal, and the lettering by line and word']
          ] },
          { note: 'The year, designer, printer and size are not known, and a department’s name cannot rule out later printing or old stock. The lettering is rebuilt from condensed C059 Bold, not an identified typeface.' },
          { h: 'The same service' },
          { links: [SEAL_LINK, ...FIRE_LINKS] }
        ]
      },
      story: [
        'An undated card from the British Columbia Forest Service: two lines of lettering under the service’s seal.',
        'Read it from the borrowed line, to the instruction, to the seal that signs it.'
      ]
    },
    duty: {
      label: 'England Expects…',
      hint: 'the first line',
      box: { x: 155, y: 310, w: 742, h: 36 },
      pad: 0.12,
      layer: '#fsc-type-text-line-1',
      panel: {
        eyebrow: 'The first line',
        heading: '“England Expects Every Man to Do His Duty.”',
        lede: 'Nelson’s signal before Trafalgar, in the short form it took in later use.',
        blocks: [
          { facts: [
            ['Signal, 1805', '“England expects that every man will do his duty.”'],
            ['Recruiting poster, 1914', '“England Expects Every Man to do His Duty”'],
            ['Lettering', 'outlined, rebuilt word by word']
          ] },
          { note: 'The card does not say why the service borrowed the line. A First World War link is plausible, not established.' },
          { sources: [NAM, TE_PAPA] }
        ]
      },
      story: [
        'On 21 October 1805, before Trafalgar, Nelson signalled “England expects that every man will do his duty.” The card uses the familiar shortened form.',
        'A 1914 British recruiting poster set the same words over “and Join the Army To-day”, and “England expects” was still on a national-service poster in 1939.'
      ],
      storySources: [NAM, TE_PAPA]
    },
    yours: {
      label: 'Do Yours',
      hint: 'the second line',
      box: { x: 266, y: 368, w: 515, h: 31 },
      pad: 0.15,
      layer: '#fsc-type-text-line-2',
      panel: {
        eyebrow: 'The second line',
        heading: 'Do Yours: Prevent Forest Fires.',
        lede: 'The card’s own instruction: the duty of the first line, pointed at carelessness with fire.',
        blocks: [
          { facts: [
            ['After the colon', 'a wide space, as photographed'],
            ['Lettering', 'the first line’s alphabet, smaller']
          ] },
          { note: 'Reading it as an appeal to citizenship is an interpretation. Nothing on the card explains the choice.' },
          { sources: [MACMILLAN] }
        ]
      },
      story: [
        'The second line turns that duty on the reader’s own conduct in the woods: Do Yours: Prevent Forest Fires.',
        'In April 1915 H. R. MacMillan wrote that prevention depended on people’s “pride of citizenship”, carried by roadside and trail signs, pictures for schools, cinema slides and even whetstones. His article does not mention this card, but the card makes that kind of appeal.'
      ],
      storySources: [MACMILLAN, PARMINTER]
    },
    emblem: {
      label: 'Seal',
      hint: 'Forest Service, Lands Department',
      box: { x: 279, y: 33, w: 498, h: 244 },
      pad: 0.08,
      layer: '#fsc-forest-service-logo',
      panel: {
        eyebrow: 'The seal',
        heading: 'Forest Service, Lands Department',
        lede: 'The service’s engraved seal: a conifer through the lettering, with boughs and cones on either side.',
        blocks: [
          { facts: [
            ['Lettering', 'BRITISH COLUMBIA · FOREST SERVICE · LANDS DEPARTMENT'],
            ['Wording', 'the Department of Lands, 1912 to 1945'],
            ['Dated use', 'Root and Branch, vol. II, no. 12, catalogued as 1924']
          ] },
          { note: 'This is the site’s own drawing of the seal, its boughs and cones moved and scaled to the card. The card’s engraving differs in detail.' },
          { links: [SEAL_LINK, DEPARTMENT_LINK] }
        ]
      },
      story: [
        'The seal names the Lands Department. The Forest Act of 1912 set up a Forest Branch within the Department of Lands, and in 1945 the department was renamed the Department of Lands and Forests, so the wording belongs to about 1912–1945.',
        'The same seal is on the cover of Root and Branch, vol. II, no. 12, catalogued as 1924: that dates the seal’s use, not the card.'
      ],
      storySources: [FOREST_SERVICE_TIMELINE, ROOT_AND_BRANCH]
    },
    border: {
      label: 'Border',
      hint: 'one printed rule',
      box: { x: 95, y: 137, w: 860, h: 313 },
      pad: 0.06,
      layer: '#fsc-border',
      panel: {
        eyebrow: 'The frame',
        heading: 'Border',
        lede: 'One printed rule around the lettering, open at the top where the seal sits.',
        blocks: [
          { facts: [
            ['Rule', '3 units, in the card’s ink'],
            ['Size', '210 × 100 mm, an export size, not a measurement']
          ] },
          { h: 'The same plea' },
          { links: FIRE_LINKS }
        ]
      },
      story: [
        'Still unknown: the year, the designer, the printer and how the card was handed out.',
        'A photograph of its back, its size or the original photograph’s caption would narrow it.'
      ]
    }
  },
  order: ['overview', 'duty', 'yours', 'emblem', 'border']
}

export const FOREST_SERVICE_CARDS = { 'england-expects': ENGLAND_EXPECTS }
