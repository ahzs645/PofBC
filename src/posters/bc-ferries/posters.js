// The BC Ferries car decals: their parts, where each sits in its drawing, and what the panel says
// about it. Data only — the drawings are attached in ./index.js — as for the Forest Service posters
// (see ../forest-service/posters.js for the shape of a part and a panel).
//
// Boxes are in each drawing's own units, measured from its named layers in Chromium.

import { POSTERS } from '../catalogue.js'

// ── Shared context ──────────────────────────────────────────────────────────────────────────────

const LOGOS_LINK = {
  label: 'BC Ferries’ marks',
  note: 'Logos · BC Ferries: the Toll Authority wordmark, the dogwood flags and the wave',
  to: { view: 'gallery', logos: 'bc-ferries' }
}
const TOLL_AUTHORITY_LINK = {
  label: 'British Columbia Toll Highways and Bridges Authority',
  note: 'Government · 1962: the authority that ran the ferries until 1964',
  to: { view: 'government', year: 1962, node: 'bc-toll-highways-and-bridges-authority' }
}
const FERRY_AUTHORITY_LINK = {
  label: 'British Columbia Ferry Authority',
  note: 'Government · 1970: the ferries’ own authority, from 1 April 1964',
  to: { view: 'government', year: 1970, node: 'bc-ferry-authority' }
}
const poster = (id, part, note) => ({
  label: POSTERS[id].title,
  note,
  to: { view: 'posters', poster: id, part }
})

const box = (id) => POSTERS[id].view

// ── GO B.C. FERRIES ─────────────────────────────────────────────────────────────────────────────

export const GO_BC_FERRIES = {
  id: 'go-bc-ferries',
  spotlight: { keep: ['border-and-field'] },
  regions: ['routes', 'mountains', 'ferry', 'gull', 'title', 'subtitle', 'flag'],
  parts: {
    overview: {
      label: 'Whole decal',
      box: box('go-bc-ferries'),
      pad: 0.05,
      panel: {
        eyebrow: 'BC Ferries · car decal',
        heading: 'GO B.C. FERRIES',
        lede: 'A rounded cushion of a sticker: teal sea and green mountains, a gull flying low over a ferry, the dogwood flag at the foot, and the system’s routes running round the cream rim.',
        blocks: [
          'A window sticker for a car that had made the crossing. It sells the service the way a resort sticker sells a place: the routes are destinations, and the ferry is half hidden by the gull.',
          { facts: [
            ['Issued by', 'British Columbia Toll Authority Ferry Systems, from the subtitle'],
            ['Date', 'not established; the wording places it in 1960–64'],
            ['Rebuilt from', 'one supplied picture of the sticker, 1354 × 1161 pixels'],
            ['Drawing', '145 paths, 23 rectangles, 15 circles and 2 ellipses; all lettering outlined']
          ] },
          { palette: [
            { name: 'Cream', value: '#FCE6A3' },
            { name: 'Teal', value: '#1DA4A9' },
            { name: 'Green', value: '#047634' },
            { name: 'Dark navy', value: '#031E24' },
            { name: 'Gold edge', value: '#EFB247' }
          ] },
          { note: 'The colours are flat approximations of the picture’s, not verified ink values. Its paper grain, tonal variation and fuzzy edge were left out, and the outline was regularised.' },
          { h: 'Also a decal' },
          { links: [poster('queen-of-sidney', 'overview', 'A ship’s own sticker, from the same fleet'), LOGOS_LINK] }
        ]
      }
    },
    routes: {
      label: 'Routes',
      hint: 'round the rim: the system’s crossings',
      box: { x: 47, y: 43, w: 1264, h: 1060 },
      pad: 0.03,
      layer: '#perimeter-text, #perimeter-dots',
      hit: 'shape',
      panel: {
        eyebrow: 'The rim',
        heading: 'Victoria – Vancouver – Nanaimo',
        em: 'and the Sunshine Coast and Gulf Islands',
        lede: 'The three cities across the top, joined by dashes, and the coast and the islands across the bottom, either side of the flagpole.',
        blocks: [
          'Between them they name the system’s whole reach: the two main crossings to Vancouver Island, and the smaller routes up the coast and among the islands. Black dots stand between the two halves at either side.',
          'The upper route is custom geometric lettering; the lower combines custom letters with saved font outlines. They were fitted to the picture letter by letter, not set in a recovered typeface.',
          { facts: [
            ['Upper', 'VICTORIA-VANCOUVER-NANAIMO'],
            ['Lower', 'SUNSHINE COAST / GULF ISLANDS'],
            ['Ink', '#070A09']
          ] }
        ]
      }
    },
    mountains: {
      label: 'Mountains',
      hint: 'green peaks with snow',
      box: { x: 125, y: 173, w: 1115, h: 479 },
      pad: 0.05,
      layer: '#mountains',
      hit: 'shape',
      panel: {
        eyebrow: 'The scene',
        heading: 'The Coast Mountains',
        em: 'in two flat colours',
        lede: 'A ridge of green peaks with cream snowcaps across the teal, the coast as the crossing sees it.',
        blocks: [
          'The ridges and snowcaps are simple authored paths in two colours, with no shading: the sticker was printed flat.'
        ]
      }
    },
    ferry: {
      label: 'Ferry',
      hint: 'decks, windows and portholes',
      box: { x: 157, y: 446, w: 1028, h: 239 },
      pad: 0.06,
      layer: '#ferry-illustration',
      hit: 'shape',
      panel: {
        eyebrow: 'The ship',
        heading: 'A ferry, side on',
        em: 'under the gull',
        lede: 'A long, low ship in cream and navy: funnel and mast, a superstructure of windows, the lower deck, and the hull with its portholes.',
        blocks: [
          'Its windows and nine visible portholes are separate shapes. The parts of the ship hidden under the gull are inferred, so the drawing still holds together if the gull is moved.',
          { facts: [
            ['Groups', 'funnel and mast, superstructure, lower deck, waterline and hull'],
            ['Portholes', 'nine visible']
          ] }
        ]
      }
    },
    gull: {
      label: 'Gull',
      hint: 'wings over the ship',
      box: { x: 232, y: 173, w: 734, h: 664 },
      pad: 0.05,
      layer: '#gull',
      hit: 'shape',
      panel: {
        eyebrow: 'The picture',
        heading: 'A gull',
        em: 'in front of everything',
        lede: 'One great cream gull sweeps down across the scene, its upper wing reaching the mountains and the lower one the title.',
        blocks: [
          'It covers the ship, as on the sticker. Its wings and feather tips were narrowed and its notches shortened during the comparison with the picture.'
        ]
      }
    },
    title: {
      label: 'Title',
      hint: '“GO B.C. FERRIES”',
      box: { x: 307, y: 698, w: 802, h: 115 },
      pad: 0.12,
      layer: '#go-bc-ferries',
      panel: {
        eyebrow: 'The title',
        heading: 'GO B.C. FERRIES',
        em: 'an invitation',
        lede: 'Heavy cream capitals across the sea below the ship: not the system’s name but an imperative, as a road sign would put it.',
        blocks: [
          'Custom geometric lettering, drawn and outlined. It is a visual reconstruction, not a recovered historical font.',
          { facts: [['Fill', '#FCE6A3'], ['Typeface', 'none: custom display letters']] }
        ]
      }
    },
    subtitle: {
      label: 'Subtitle',
      hint: 'the authority’s name',
      box: { x: 308, y: 820, w: 802, h: 31 },
      pad: 0.3,
      layer: '#subtitle',
      panel: {
        eyebrow: 'The signature',
        heading: 'British Columbia Toll Authority Ferry Systems',
        lede: 'The small black line under the title, and the only one that dates the decal.',
        blocks: [
          'From 1960 the ferries were run by the Toll Highways and Bridges Authority, under the name British Columbia Toll Authority Ferry System. On 1 April 1964 they passed to an authority of their own, the British Columbia Ferry Authority. A sticker that still names the Toll Authority belongs to the years before.',
          'The letters are saved outlines of DejaVu Sans Bold, each placed from the picture: a substitute, not the original face.',
          { h: 'The authority, and the one that followed' },
          { links: [TOLL_AUTHORITY_LINK, FERRY_AUTHORITY_LINK, LOGOS_LINK] }
        ]
      }
    },
    flag: {
      label: 'Dogwood flag',
      hint: 'on its pole, at the foot',
      box: { x: 533, y: 848, w: 291, h: 264 },
      pad: 0.12,
      layer: '#dogwood-flag',
      hit: 'shape',
      panel: {
        eyebrow: 'The flag',
        heading: 'The dogwood on green',
        em: 'the system’s house flag',
        lede: 'A green flag with a cream dogwood, the province’s flower, flying from a pole that splits the lower route in two.',
        blocks: [
          'The same flower on green is the fleet’s flag in the 1963 brochure, as the Logos view draws it. Here it is a five-bract flower with dark detail; its finer seams and marks were simplified.',
          { links: [LOGOS_LINK] }
        ]
      }
    }
  },
  order: ['overview', 'routes', 'mountains', 'ferry', 'gull', 'title', 'subtitle', 'flag']
}

// ── Queen of Sidney ─────────────────────────────────────────────────────────────────────────────

export const QUEEN_OF_SIDNEY = {
  id: 'queen-of-sidney',
  spotlight: { keep: ['sticker-and-field'] },
  regions: ['lettering', 'flag', 'flowers', 'helm', 'scene', 'ferry', 'ribbon'],
  parts: {
    overview: {
      label: 'Whole decal',
      box: box('queen-of-sidney'),
      pad: 0.04,
      panel: {
        eyebrow: 'BC Ferries · car decal',
        heading: 'Queen of Sidney',
        lede: 'An orange sticker with a white edge: a ship’s wheel framing the ferry at sea, a dogwood flower either side, the house flag above and the ship’s name on a ribbon below.',
        blocks: [
          'Where GO B.C. FERRIES sells the system, this one is a souvenir of one ship. The wheel makes the picture a view from the bridge; the ribbon names the vessel.',
          { facts: [
            ['Issued by', 'British Columbia Ferries, from the lettering'],
            ['Date', 'not established'],
            ['Rebuilt from', 'one supplied picture of the sticker, 1305 × 1206 pixels'],
            ['Drawing', '254 paths, 55 rectangles, ellipses and circles, 47 groups; all lettering outlined']
          ] },
          { palette: [
            { name: 'Orange', value: '#FF6404' },
            { name: 'Navy', value: '#081B22' },
            { name: 'Sky blue', value: '#4ACBFA' },
            { name: 'Green', value: '#12BA15' },
            { name: 'Warm white', value: '#FFFDF7' }
          ] },
          { note: 'The colours are clean approximations of the picture’s, not recovered ink specifications. Its paper grain, faded ink, wear and drop shadow were left out, and the wheel and the sticker’s edge were regularised.' },
          { h: 'Also a decal' },
          { links: [poster('go-bc-ferries', 'overview', 'The Toll Authority’s sticker for the whole system'), LOGOS_LINK] }
        ]
      }
    },
    lettering: {
      label: 'Lettering',
      hint: '“British Columbia Ferries”',
      box: { x: 116, y: 155, w: 949, h: 38 },
      pad: 0.3,
      layer: '#top-lettering',
      panel: {
        eyebrow: 'The signature',
        heading: 'British Columbia Ferries',
        em: 'either side of the flag',
        lede: 'The system’s name in plain capitals across the top, split by the flagpole.',
        blocks: [
          'It names British Columbia Ferries, not the Toll Authority. That points to a sticker of after 1 April 1964, when the ferries passed to an authority of their own, though the wording alone does not establish a date.',
          'The letters are outlined Nimbus Sans Regular, fitted one by one to the picture: a substitute, not a claim about the original face.',
          { h: 'The authority' },
          { links: [FERRY_AUTHORITY_LINK, TOLL_AUTHORITY_LINK] }
        ]
      }
    },
    flag: {
      label: 'House flag',
      hint: 'the dogwood on green',
      box: { x: 533, y: 88, w: 252, h: 209 },
      pad: 0.15,
      layer: '#flag-and-pole',
      hit: 'shape',
      panel: {
        eyebrow: 'The flag',
        heading: 'The dogwood flag',
        em: 'at the masthead',
        lede: 'A green flag with a small white dogwood, flying from a pole that rises out of the wheel.',
        blocks: [
          'The fleet’s house flag; the same flower on green is in the Logos view, from the 1963 brochure.',
          { links: [LOGOS_LINK] }
        ]
      }
    },
    flowers: {
      label: 'Dogwoods',
      hint: 'one either side of the wheel',
      box: { x: 126, y: 291, w: 1056, h: 188 },
      pad: 0.05,
      layer: '#dogwood-flowers',
      hit: 'shape',
      panel: {
        eyebrow: 'The flowers',
        heading: 'Two dogwoods',
        em: 'not a mirrored pair',
        lede: 'A white, outlined dogwood flower on each side of the wheel, with a gold centre.',
        blocks: [
          'They are drawn as two different flowers, as on the sticker, not one flower flipped. Their fine veins are simplified.'
        ]
      }
    },
    helm: {
      label: 'Ship’s wheel',
      hint: 'the ring and its handles',
      box: { x: 335, y: 224, w: 702, h: 753 },
      pad: 0.04,
      layer: '#helm, #helm-above-bow',
      hit: 'shape',
      panel: {
        eyebrow: 'The frame',
        heading: 'A ship’s wheel',
        em: 'framing the picture',
        lede: 'A navy ring with its spokes’ handles standing out all round, and the scene inside it.',
        blocks: [
          'The ring is concentric ellipses and each handle its own shape. Where the ring crosses the ship’s bow it is drawn again above it, in a layer of its own, to keep the sticker’s order of overlaps.'
        ]
      }
    },
    scene: {
      label: 'Coast and sea',
      hint: 'forest, birds and waves',
      box: { x: 375, y: 328, w: 564, h: 575 },
      pad: 0.05,
      layer: '#sky-forest-and-birds, #sea',
      hit: 'shape',
      panel: {
        eyebrow: 'The scene',
        heading: 'Through the wheel',
        em: 'forested shores and open water',
        lede: 'A pale sky with four birds, forested shores either side, and blue waves with white crests under the ship.',
        blocks: [
          'The forest edges were made more irregular, and a white crest that crosses the lower left of the wheel was kept, after comparison with the picture.'
        ]
      }
    },
    ferry: {
      label: 'Ferry',
      hint: 'the Queen of Sidney herself',
      box: { x: 290, y: 312, w: 644, h: 498 },
      pad: 0.05,
      layer: '#ferry',
      hit: 'shape',
      panel: {
        eyebrow: 'The ship',
        heading: 'Queen of Sidney',
        em: 'bow on',
        lede: 'The ship coming towards you out of the wheel: white hull with blue bow bands, green waterline, the bridge and saloon windows, the upper cabin, mast and an anchor hanging at the bow.',
        blocks: [
          'Its bridge, saloon windows, railings, mast fittings, aft deck and perforated bulwark are separately editable groups. The bow bands’ spacing and curve and the upper bridge windows were corrected against the picture.',
          { facts: [
            ['Groups', 'lower hull, upper cabin, bridge and passenger deck, mast and railings, aft deck, main hull, bow flagstaff']
          ] }
        ]
      }
    },
    ribbon: {
      label: 'Ribbon',
      hint: '“QUEEN OF SIDNEY”',
      box: { x: 182, y: 738, w: 943, h: 349 },
      pad: 0.05,
      layer: '#ribbon, #ribbon-lettering',
      hit: 'shape',
      panel: {
        eyebrow: 'The name',
        heading: 'QUEEN OF SIDNEY',
        em: 'on a curved ribbon',
        lede: 'A navy ribbon curving under the wheel with folded ends, the ship’s name across it in white capitals.',
        blocks: [
          'Each of the thirteen letters is built from explicit geometric outlines and placed and turned on its own along the curve. The Q’s angle and counter were corrected against the picture.',
          { facts: [['Letters', '13, each rotated to the ribbon'], ['Fill', '#FFFDF7, even-odd']] }
        ]
      }
    }
  },
  order: ['overview', 'lettering', 'flag', 'flowers', 'helm', 'scene', 'ferry', 'ribbon']
}

export const BC_FERRIES_POSTERS = {
  'go-bc-ferries': GO_BC_FERRIES,
  'queen-of-sidney': QUEEN_OF_SIDNEY
}
