// The Expo 86 posters: the art posters of Robert Davidson’s and Vittorio Fiorucci’s artwork, and the
// British Columbia Pavilion’s poster for its film, Our British Columbia. Their parts, where each sits
// in its drawing, and what the panel says about it. Data only — the drawings are attached in
// ./index.js — as for the Forest Service posters (see ../forest-service/posters.js for the shape of
// a part and a panel).
//
// Unlisted: the posters are not on the shelf (their series says `unlisted`), but their addresses
// open them (?view=posters&poster=expo-86-davidson), and they step among themselves. Boxes are in
// each drawing's own units, measured from its named groups in Chromium.

import { POSTERS } from '../catalogue.js'
import { withStories } from '../stories.js'

const EXPO_LOGOS_LINK = {
  label: 'Expo 86’s marks',
  note: 'Logos · Expo 86 Corporation: the stacked EXPO 86 this poster carries, and its other forms',
  to: { view: 'gallery', logos: 'collected-expo-86-corporation' }
}
const EXPO_CORPORATION_LINK = {
  label: 'Expo 86 Corporation',
  note: 'Government · 1986: the Crown corporation that ran the fair, and holds the poster’s copyright',
  to: { view: 'government', year: 1986, node: 'expo-86-corporation' }
}
const EXPO_FAIR_LINK = {
  label: 'Expo 86 Corporation',
  note: 'Government · 1986: the Crown corporation that ran the fair',
  to: { view: 'government', year: 1986, node: 'expo-86-corporation' }
}
const PAVILION_CORPORATION_LINK = {
  label: 'B.C. Pavilion Corporation',
  note: 'Government · 1986: the Crown corporation incorporated in 1984 under the pavilion’s name. The poster names the pavilion, not the corporation.',
  to: { view: 'government', year: 1986, node: 'bc-pavilion-corporation' }
}
// The sources the Fiorucci story's reading rests on. None of them explains this poster.
const SEKSIK = { label: 'Librairie Michael Seksik, Vittorio Fiorucci, “The 1986 World Exposition”, the dealer’s record of a matching copy', href: 'https://librairieseksik.fr/livre/1538' }
const BIE = { label: 'Bureau International des Expositions, Expo 1986 Vancouver: its theme and its plazas', href: 'https://www.bie-paris.org/site/en/1986-vancouver' }
const MCCORD = { label: 'McCord Stewart Museum, Montreal Through the Eyes of Vittorio, on his work in general', href: 'https://www.musee-mccord-stewart.ca/en/exhibitions/montreal-through-the-eyes-of-vittorio/' }

const poster = (id, note) => ({ label: POSTERS[id].title, note, to: { view: 'posters', poster: id } })
const box = (id) => POSTERS[id].view

export const EXPO_86_DAVIDSON = {
  id: 'expo-86-davidson',
  spotlight: { keep: ['poster-paper'] },
  regions: ['artwork', 'signature', 'logo', 'event', 'credit'],
  parts: {
    overview: {
      label: 'Whole poster',
      box: box('expo-86-davidson'),
      pad: 0.03,
      panel: {
        eyebrow: 'Expo 86 · official art poster',
        heading: 'Expo 86: Robert Davidson',
        lede: 'A mirrored formline composition in black, red and blue-grey on cream fills the sheet; along the foot, the stacked EXPO 86 mark, the artist’s signature and the fair’s name and dates in English and French.',
        blocks: [
          'An art poster for the 1986 World Exposition in Vancouver, with artwork by the Haida artist Robert Davidson, signed and dated 1985. The credit line names the Expo 86 Corporation as the copyright holder.',
          { facts: [
            ['Artist', 'Robert Davidson, from the printed credit and the signature'],
            ['Published by', 'The Expo 86 Corporation, © holder in the credit line'],
            ['Date', 'artwork signed 1985; the fair ran 2 May – 13 October 1986'],
            ['Rebuilt from', 'three photographs of a framed copy and a restored image of the artwork'],
            ['Drawing', '1200 × 1600 units for a 600 × 800 mm working sheet; all lettering outlined']
          ] },
          { palette: [
            { name: 'Cream paper', value: '#FBE5C1' },
            { name: 'Black', value: '#25282B' },
            { name: 'Red', value: '#C9231D' },
            { name: 'Blue-grey', value: '#88ACB3' }
          ] },
          { note: 'A vector reconstruction, not the printing artwork: the colours are flat values read from photographs, the sheet size is a working size rather than a measured one, and the type is a Helvetica-style substitute for a face not identified. Kept unlisted on the shelf; the artwork is Robert Davidson’s and remains under copyright.' },
          { links: [EXPO_LOGOS_LINK, EXPO_CORPORATION_LINK, poster('expo-86-fiorucci', 'Posters · another of the fair’s art posters, with the same mark and event text'), poster('our-british-columbia', 'Posters · the British Columbia Pavilion’s poster for its film')] }
        ]
      }
    },
    artwork: {
      label: 'Artwork',
      hint: 'the formline design, mirrored left and right',
      box: { x: 5, y: 12, w: 1189, h: 1335 },
      pad: 0.02,
      layer: '#poster-artwork',
      hit: 'shape',
      panel: {
        eyebrow: 'The artwork',
        heading: 'Black, red and blue-grey formline',
        lede: 'A composition built on a single vertical axis: heads with eyes and beaks at the top, side and foot, a central face under a cross-hatched brow, and two hands, each with an eye in its palm.',
        blocks: [
          'Davidson’s design is drawn in the northwest coast formline tradition: continuous black lines that swell and taper, with red secondary forms and blue-grey tertiary fields. Each half is the mirror of the other.',
          'The poster does not title or explain the image, and neither does this panel: what the figures represent is the artist’s to say, not something to infer from the drawing.',
          { facts: [
            ['Reconstruction', 'drawn by hand over a restored 1191 × 1320 image of the artwork, then checked region by region against it'],
            ['Placement', 'one uniform scale, 1.0339 in both directions, so the artwork keeps the restored image’s proportions'],
            ['Known differences', 'a few pixels of curve and edge at high enlargement; flat colour without the print’s texture; an exactly mirrored drawing where the original varies slightly side to side']
          ] },
          { figure: 'review', alt: 'Two versions side by side (the restored reference artwork and the reconstructed poster), and below them an enlarged strip of the poster’s foot with the logo, signature and event text', caption: 'The restored reference artwork beside the reconstructed poster, and the foot enlarged. The reference’s cream border is the restoration’s, not a measured margin.' }
        ]
      }
    },
    signature: {
      label: 'Signature',
      hint: 'Robert Davidson, 1985',
      box: { x: 935, y: 1358, w: 184, h: 31 },
      pad: 0.4,
      layer: '#poster-signature',
      panel: {
        eyebrow: 'Below the artwork, right',
        heading: 'Robert Davidson 1985',
        lede: 'The artist’s handwritten signature and the year, under the lower right of the design.',
        blocks: [
          'Rebuilt by hand as 25 rounded strokes from a photograph taken through glass. The name and the year are clear; small crossings (after the R, and between the letters of Davidson) are smoothed where reflection hides them.',
          { note: 'A drawn approximation for the reconstructed poster, not a copy of the autograph.' }
        ]
      }
    },
    logo: {
      label: 'Expo 86 logo',
      hint: 'the stacked EXPO and three-ring 86',
      box: { x: 80, y: 1408, w: 121, h: 170 },
      pad: 0.2,
      layer: '#poster-expo-logo',
      panel: {
        eyebrow: 'Lower left',
        heading: 'EXPO 86',
        lede: 'The fair’s stacked mark (EXPO over the three interlocking rings of 86) printed in the poster’s black, with a small TM.',
        blocks: [
          'The mark is the gallery’s vector of the Expo 86 symbol, recoloured from its blue and black to the poster’s single dark ink, every coordinate unchanged. That vector is itself a modern reconstruction, drawn for Wikimedia Commons from merchandise photographs. The TM is set separately; it is not part of the source drawing.',
          { links: [EXPO_LOGOS_LINK] }
        ]
      }
    },
    event: {
      label: 'Event',
      hint: 'the fair’s name and dates, in English and French',
      box: { x: 700, y: 1490, w: 481, h: 95 },
      pad: 0.15,
      layer: '#poster-bilingual-text',
      panel: {
        eyebrow: 'Lower right',
        heading: 'The 1986 World Exposition',
        lede: 'Two columns, English then French, each with the name in bold, the place in regular weight and the dates in bold.',
        blocks: [
          { facts: [
            ['English', 'The 1986 World Exposition · Vancouver · British Columbia, Canada · May 2-October 13, 1986'],
            ['French', 'Exposition internationale de 1986 · Vancouver · Colombie-Britannique, Canada · Du 2 mai au 13 octobre 1986']
          ] },
          'The wording, line breaks and the tight hyphen in “May 2-October 13” follow the photograph. The type is Nimbus Sans, a Helvetica-style stand-in, outlined.',
          { links: [EXPO_CORPORATION_LINK] }
        ]
      }
    },
    credit: {
      label: 'Credit',
      hint: 'artist, copyright and printer',
      box: { x: 80, y: 1589, w: 168, h: 8 },
      pad: 1.5,
      layer: '#poster-credit',
      panel: {
        eyebrow: 'Along the foot',
        heading: 'ARTIST: ROBERT DAVIDSON · © THE EXPO 86 CORPORATION · PRINTED IN CANADA',
        lede: 'The fine print under the logo: who made the image, who holds its copyright, and where it was printed.',
        blocks: [
          'Kept word for word, with its wide spaces between the three statements.',
          { links: [EXPO_CORPORATION_LINK] }
        ]
      }
    }
  },
  order: ['overview', 'artwork', 'signature', 'logo', 'event', 'credit']
}

const motif = (colour, windows, box, panel, storySources) => ({
  label: `${colour[0].toUpperCase()}${colour.slice(1)} shape`,
  hint: windows,
  box,
  pad: 0.03,
  layer: `#fio-${colour}-motif`,
  hit: 'shape',
  panel,
  ...(storySources ? { storySources } : {})
})

export const EXPO_86_FIORUCCI = {
  id: 'expo-86-fiorucci',
  spotlight: { keep: ['fio-paper'] },
  regions: ['red', 'blue', 'yellow', 'green', 'signature', 'logo', 'event'],
  parts: {
    overview: {
      label: 'Whole poster',
      box: box('expo-86-fiorucci'),
      pad: 0.03,
      storySources: [SEKSIK],
      panel: {
        eyebrow: 'Expo 86 · art poster',
        heading: 'Expo 86: Vittorio Fiorucci',
        lede: 'Four flat shapes, red, blue, yellow and green, cross a warm white sheet one under another, pointing left, right, left, right, each with a row of windows in a second colour. At the foot, the stacked EXPO 86 mark and the fair’s name and dates in English and French.',
        blocks: [
          'An art poster for the 1986 World Exposition in Vancouver, with artwork by the Montreal poster artist Vittorio Fiorucci, whose signature is at the lower left. The sheet carries no credit line; the dealer’s listing of a matching copy describes it as a screenprint published by The Expo 86 Corporation and printed in Canada.',
          { facts: [
            ['Artist', 'Vittorio Fiorucci, from the signature and the dealer’s listing'],
            ['Title', 'none printed; the dealer lists it as “The 1986 World Exposition”'],
            ['Published by', 'The Expo 86 Corporation, from the dealer’s listing; not printed on the sheet'],
            ['Date', 'undated; the fair ran 2 May – 13 October 1986'],
            ['Rebuilt from', 'one photograph of a framed copy, its corners squared by a perspective transform'],
            ['Drawing', '1100 × 1593.7 units for the listing’s 635 × 920 mm; all lettering outlined']
          ] },
          { palette: [
            { name: 'Paper', value: '#F7F5EF' },
            { name: 'Red', value: '#B70F18' },
            { name: 'Blue', value: '#24558F' },
            { name: 'Yellow', value: '#FFDA0A' },
            { name: 'Green', value: '#0C602E' },
            { name: 'Lemon', value: '#F6E579' },
            { name: 'Mint', value: '#62C5AF' },
            { name: 'Orange', value: '#EC5006' },
            { name: 'Pink', value: '#EC477D' },
            { name: 'Ink', value: '#171716' }
          ] },
          'Read as a picture, the four forms are both passenger aircraft and fish, and their windows and alternating directions a playful image of travel and exchange, in keeping with the fair’s theme of transportation and communication. That reading is this site’s: no statement from the artist about the poster has been found.',
          { note: 'A vector reconstruction, not the printing artwork: the colours are flat values estimated from an uncalibrated photograph, the page size is a dealer’s catalogue measurement rather than one of this print, and a little of the design may continue under the frame. Kept unlisted on the shelf; the artwork is Vittorio Fiorucci’s and remains under copyright.' },
          { links: [EXPO_LOGOS_LINK, EXPO_CORPORATION_LINK, poster('expo-86-davidson', 'Posters · another of the fair’s art posters, with the same mark and event text')] }
        ]
      }
    },
    red: motif('red', 'pointing left, four pale yellow windows', { x: 0, y: 2, w: 1100, h: 398 }, {
      eyebrow: 'The first shape',
      heading: 'Red, with four round windows',
      lede: 'The top shape points left: a sharp nose, two swept fins above and below, and a forked tail at the right edge. Four pale yellow rounds sit along its middle.',
      blocks: [
        'Each shape has a row of windows like a passenger plane’s, and a fish’s curved body, fins and forked tail. The story reads it as both at once; nothing from the artist confirms either.',
        { facts: [
          ['Drawing', 'one silhouette of 24 cubic curves, drawn by hand over the corrected photograph, not traced'],
          ['Windows', 'four rounded forms, each drawn on its own and none quite like another'],
          ['Fit', '98.53% overlap with the photographed shape, intersection over union']
        ] }
      ]
    }),
    blue: motif('blue', 'pointing right, six mint windows', { x: 5, y: 321, w: 1087, h: 474 }, {
      eyebrow: 'The second shape',
      heading: 'Blue, with six square windows',
      lede: 'The second shape turns the other way: its nose at the right edge, its tail fins reaching back to the left, and six mint quadrilaterals along its body.',
      blocks: [
        'The shapes alternate in direction down the sheet, and each overlaps the space of the next without touching it.',
        { facts: [
          ['Drawing', 'one silhouette of 22 cubic curves'],
          ['Windows', 'six quadrilaterals, slightly out of square, as in the print'],
          ['Fit', '98.81% overlap with the photographed shape']
        ] }
      ]
    }, [BIE]),
    yellow: motif('yellow', 'pointing left, seven orange windows', { x: 0, y: 762, w: 1100, h: 400 }, {
      eyebrow: 'The third shape',
      heading: 'Yellow, with seven square windows',
      lede: 'The third shape points left again, its tail sweeping down to the right edge, with seven orange quadrilaterals, the most windows of the four.',
      blocks: [
        { facts: [
          ['Drawing', 'one silhouette of 23 cubic curves'],
          ['Windows', 'seven quadrilaterals'],
          ['Fit', '98.87% overlap with the photographed shape']
        ] }
      ]
    }, [MCCORD]),
    green: motif('green', 'pointing right, four pink windows', { x: 0, y: 1083, w: 1100, h: 392 }, {
      eyebrow: 'The fourth shape',
      heading: 'Green, with four round windows',
      lede: 'The last shape points right, with a hooked fin above and a long tail below, and four pink rounds: the same four as the red shape at the top, in its complementary colours.',
      blocks: [
        { facts: [
          ['Drawing', 'one silhouette of 23 cubic curves'],
          ['Windows', 'four rounded forms'],
          ['Fit', '98.44% overlap with the photographed shape']
        ] },
        'No shape was mirrored or repeated to make another: each was drawn on its own.'
      ]
    }),
    signature: {
      label: 'Signature',
      hint: 'the artist’s, small, at the lower left',
      box: { x: 32, y: 1247, w: 93, h: 89 },
      pad: 0.2,
      layer: '#fio-signature',
      panel: {
        eyebrow: 'Lower left, over the green shape',
        heading: 'Vittorio',
        lede: 'The artist’s signature, written small in grey at an angle, in the space beside the green shape’s tail.',
        blocks: [
          'Rebuilt as five hand-drawn strokes from the supplied photograph, checked against a postcard of the same design.',
          { note: 'An approximate facsimile, not a copy of the autograph. The package also keeps an edition without it.' }
        ]
      }
    },
    logo: {
      label: 'Expo 86 logo',
      hint: 'the stacked EXPO and three-ring 86',
      box: { x: 36, y: 1413, w: 112, h: 155 },
      pad: 0.2,
      layer: '#fio-expo-mark',
      panel: {
        eyebrow: 'Lower left',
        heading: 'EXPO 86',
        lede: 'The fair’s stacked mark, EXPO over the three interlocking rings of 86, in black with a small TM.',
        blocks: [
          'The same vector as on the Davidson poster, its paths unchanged and placed to fit this printing. That vector is itself a modern reconstruction, drawn for Wikimedia Commons from merchandise photographs.',
          { links: [EXPO_LOGOS_LINK] }
        ]
      }
    },
    event: {
      label: 'Event',
      hint: 'the fair’s name and dates, in English and French',
      box: { x: 639, y: 1492, w: 430, h: 84 },
      pad: 0.15,
      layer: '#fio-footer',
      hit: 'letters',
      gap: 1.5,
      panel: {
        eyebrow: 'Lower right',
        heading: 'The 1986 World Exposition',
        lede: 'Two columns, English then French: the name in bold, the place in regular weight, the dates in bold.',
        blocks: [
          { facts: [
            ['English', 'The 1986 World Exposition · Vancouver · British Columbia, Canada · May 2-October 13, 1986'],
            ['French', 'Exposition internationale de 1986 · Vancouver · Colombie-Britannique, Canada · Du 2 mai au 13 octobre 1986']
          ] },
          'Word for word the Davidson poster’s event text, and drawn from it: the same outlined Nimbus Sans, a Helvetica-style stand-in, scaled a little across so each line meets this printing’s width.',
          { links: [EXPO_CORPORATION_LINK] }
        ]
      }
    }
  },
  order: ['overview', 'red', 'blue', 'yellow', 'green', 'signature', 'logo', 'event']
}

const obc = (ids) => ids.map((id) => `#obc-${id}`).join(', ')

export const OUR_BRITISH_COLUMBIA = {
  id: 'our-british-columbia',
  spotlight: { keep: ['obc-paper'] },
  regions: ['rays', 'sunburst', 'our', 'title', 'billing', 'fine-print', 'showmanship', 'bob-rogers-company', 'pavilion'],
  parts: {
    overview: {
      label: 'Whole poster',
      box: box('our-british-columbia'),
      pad: 0.03,
      panel: {
        eyebrow: 'Expo 86 · film poster',
        heading: 'Our British Columbia',
        lede: 'Bands of blue, white and red come down the sheet into a yellow sunburst, which carries the title: OUR in a quick pen hand over BRITISH COLUMBIA in large black capitals. Below, the film’s credits and fine print, two production emblems and the pavilion’s badge.',
        blocks: [
          'The poster for Our British Columbia, the film that THE BRITISH COLUMBIA PAVILION PRESENTS in its top credit line: the province’s pavilion at Expo 86, as its badge at the lower right says. The film was written and directed by Richard Jefferies and produced by Bob Rogers. The copyright line is International Media Distribution’s, dated 1986.',
          { facts: [
            ['Presented by', 'The British Columbia Pavilion, from the credit line'],
            ['Film', 'writer and director Richard Jefferies; producer Bob Rogers; music by David Spear'],
            ['Date', '1986, from the copyright line'],
            ['Printed by', 'Mitchell Press, in British Columbia, from the printer’s line'],
            ['Rebuilt from', 'one photograph of the poster, with two close-ups of the same copy for the emblems and badge'],
            ['Drawing', '1000 × 1450 units, a working proportion from the photograph; all lettering outlined']
          ] },
          { palette: [
            { name: 'Blue', value: '#143799' },
            { name: 'Red', value: '#E51D30' },
            { name: 'Yellow', value: '#FFC000' },
            { name: 'Lettering', value: '#24231B' }
          ] },
          { note: 'A vector reconstruction, not the printing artwork. The colours are clean values for an uncalibrated photograph, the sheet’s proportion and size are not known, and the billing is set in outlined open fonts standing in for a face not identified. No artist is credited on the sheet, and none is assigned here.' },
          { links: [PAVILION_CORPORATION_LINK, EXPO_FAIR_LINK, poster('expo-86-davidson', 'Posters · one of the fair’s art posters'), poster('expo-86-fiorucci', 'Posters · another of the fair’s art posters')] }
        ]
      }
    },
    rays: {
      label: 'Rays',
      hint: 'blue, white and red, down to the border',
      box: { x: 18, y: 0, w: 964, h: 1221 },
      pad: 0.02,
      layer: obc(['blue-left-field', 'blue-right-field', 'red-centre-field', 'red-left-ray', 'red-right-ray', 'red-lower-border']),
      hit: 'shape',
      panel: {
        eyebrow: 'The upper sheet',
        heading: 'Blue, white and red',
        lede: 'Two blue fields and a red one come straight down from the top edge with white between them; red rays slant in from the sides, and a red border closes round the foot of the sunburst.',
        blocks: [
          'Red, white, blue and gold are the provincial flag’s colours, laid out here as bands rather than as the flag. The poster does not say whether it means the echo.',
          { facts: [
            ['Drawing', 'a small set of straight-edged shapes, mirrored left and right, where the photographed sheet bent them'],
            ['Colours', 'blue #143799 and red #E51D30, clean values rather than measured inks']
          ] }
        ]
      }
    },
    sunburst: {
      label: 'Sunburst',
      hint: 'the yellow panel the title stands in',
      box: { x: 30, y: 544, w: 940, h: 661 },
      pad: 0.02,
      layer: '#obc-sunburst-panel',
      hit: 'shape',
      panel: {
        eyebrow: 'The middle of the sheet',
        heading: 'A yellow sunburst',
        lede: 'One yellow shape with a white edge: points rise into the bands above it, and its lower half widens into a panel across the sheet for the title.',
        blocks: [
          'Its points meet the bands above it, so the bands read as rays coming from behind the title.',
          { facts: [
            ['Drawing', 'one 27-point shape with a 7-unit white separator'],
            ['Check', '27 of its corners, measured on the photograph, sit a median 2.1 units from the drawing’s, at most 7.0, on a sheet 1000 units wide; that includes the paper’s curl, so it is no fidelity score']
          ] }
        ]
      }
    },
    our: {
      label: 'Our',
      hint: 'the handwritten word over the title',
      box: { x: 384, y: 762, w: 259, h: 110 },
      pad: 0.15,
      layer: '#obc-our-lettering',
      hit: 'letters',
      gap: 0.4,
      panel: {
        eyebrow: 'Over the title',
        heading: 'OUR',
        lede: 'The first word in a fast pen hand, its O, U and R run together, set against the formal capitals below it.',
        blocks: [
          'Rebuilt as five pen strokes, drawn as curves by hand, not traced.'
        ]
      }
    },
    title: {
      label: 'Title',
      hint: 'BRITISH COLUMBIA, in large capitals',
      box: { x: 108, y: 864, w: 789, h: 297 },
      pad: 0.04,
      layer: '#obc-british-columbia-lettering',
      hit: 'letters',
      panel: {
        eyebrow: 'The middle of the sunburst',
        heading: 'BRITISH COLUMBIA',
        lede: 'The province’s name in two lines of high-contrast serif capitals, the first B and the first C taller than the letters after them.',
        blocks: [
          'The letters touch and cross where the photograph shows them doing so: the R running into the I, the big C curling through the O, the I and A sharing a baseline stroke.',
          { facts: [
            ['Drawing', 'custom curve letterforms, drawn and refined twice against the photograph'],
            ['Typeface', 'not identified; the title is drawn, not set in a font']
          ] },
          'The same letterforms spell BRITISH COLUMBIA on the pavilion badge at the lower right.'
        ]
      }
    },
    billing: {
      label: 'Credits',
      hint: 'the film’s makers, in three lines',
      box: { x: 77, y: 1223, w: 854, h: 123 },
      pad: 0.04,
      layer: '#obc-billing',
      hit: 'letters',
      gap: 1,
      panel: {
        eyebrow: 'Under the sunburst',
        heading: 'THE BRITISH COLUMBIA PAVILION PRESENTS',
        lede: 'The billing block in tall condensed capitals, each name with its role in small type above it, and the names separated by dots.',
        blocks: [
          { facts: [
            ['Writer/director', 'Richard Jefferies'],
            ['Editor', 'Marshall Harvey'],
            ['Director of photography', 'Reed Smoot'],
            ['Cinematographer', 'Bruce Ingram'],
            ['Music', 'David Spear, with The New BC Philharmonic Orchestra'],
            ['Production supervisor', 'George Wiktor'],
            ['Post production supervisor', 'Rick Gordon'],
            ['Associate producer', 'Lynne Carrow'],
            ['Production manager', 'Karen Stewart'],
            ['Producer', 'Bob Rogers']
          ] },
          'Every name and role is readable in the photograph. The type is outlined Six Caps, an open font standing in for the original condensed face, which is not identified.'
        ]
      }
    },
    'fine-print': {
      label: 'Fine print',
      hint: 'dedication, thanks, distribution and printer',
      box: { x: 122, y: 1359, w: 774, h: 87 },
      pad: 0.06,
      layer: '#obc-fine-print',
      hit: 'letters',
      gap: 2,
      panel: {
        eyebrow: 'Along the foot',
        heading: 'For Lisa, Tyler and Jordy',
        lede: 'A dedication, then four lines of credits for the studios, thanks and distribution, the printer and the copyright.',
        blocks: [
          { facts: [
            ['Recording and post', 'Little Mountain Sound; Alpha Cine Service; W.F. White, Ltd.; Post Haste Video; all Vancouver'],
            ['Thanks', 'the Motion Picture Studio Production Technicians, I.A.T.S.E. 891, and George Chapman; Dianne Neufeld and the staff of the B.C. Film Production Office'],
            ['Distribution', 'Front Row Productions, Vancouver, for the sound track; International Media Distribution, Inc., Burbank, for the film, poster and sound track'],
            ['Printer', 'Mitchell Press, in British Columbia'],
            ['Copyright', '© 1986 International Media Distribution, Inc.']
          ] },
          { note: 'Some of these words are hidden by the holders in every photograph of the poster, and are restored so the lines read through: “Equipment by” and a repeated “Vancouver”, “with special thanks to”, “Office” after B.C. Film Production, “Sound Track distributed”, and the 02 of the ZIP code. “Jordy” is the best reading of a shadowed word. None of these is a verified transcription.' }
        ]
      }
    },
    showmanship: {
      label: 'Industrial Showmanship',
      hint: 'the winged camera emblem',
      box: { x: 37, y: 1312, w: 88, h: 54 },
      pad: 0.2,
      layer: '#obc-industrial-showmanship',
      panel: {
        eyebrow: 'Lower left',
        heading: 'INDUSTRIAL SHOWMANSHIP',
        lede: 'A blue line emblem: the arc of a gear over spread wings, a movie camera, globe and lightning at its centre, over the words in stencil capitals.',
        blocks: [
          'Rebuilt from a clearer close-up of the same copy. The gear, wings, camera, globe and tripod are drawn, and the lettering is outlined Stardos Stencil standing in for the original.',
          { note: 'An approximation of a small printed emblem, not a recovered master.' }
        ]
      }
    },
    'bob-rogers-company': {
      label: 'Bob Rogers & Company',
      hint: 'the producer’s company, with a filmstrip',
      box: { x: 42, y: 1382, w: 68, h: 49 },
      pad: 0.2,
      layer: '#obc-bob-rogers-company',
      panel: {
        eyebrow: 'Lower left',
        heading: 'Bob Rogers & Company, Inc.',
        lede: 'The producer’s company in heavy slab letters, stacked, with a strip of film running through the ampersand.',
        blocks: [
          'Bob Rogers is the film’s producer in the billing above. The lettering is outlined Alfa Slab One, a stand-in, and the filmstrip is drawn.',
          { note: 'An approximation of a small printed emblem, not a recovered master.' }
        ]
      }
    },
    pavilion: {
      label: 'Pavilion badge',
      hint: 'THE BRITISH COLUMBIA PAVILION, EXPO 86',
      box: { x: 911, y: 1331, w: 74, h: 113 },
      pad: 0.15,
      layer: '#obc-pavilion-badge',
      panel: {
        eyebrow: 'Lower right',
        heading: 'The British Columbia Pavilion, Expo 86',
        lede: 'The pavilion’s badge, framed in blue: a waving provincial flag on a yellow field, and under it THE BRITISH COLUMBIA PAVILION EXPO 86 in blue serif capitals.',
        blocks: [
          'The flag is this site’s own drawing of the provincial flag, its twelve paths unchanged and recoloured for the badge; the frame and captions are rebuilt, and BRITISH COLUMBIA uses the title’s letterforms.',
          'The badge is the pavilion’s mark, not the fair’s: the stacked EXPO 86 of the art posters does not appear on this sheet.',
          { links: [PAVILION_CORPORATION_LINK, EXPO_FAIR_LINK] }
        ]
      }
    }
  },
  order: ['overview', 'rays', 'sunburst', 'our', 'title', 'billing', 'fine-print', 'showmanship', 'bob-rogers-company', 'pavilion']
}

const withStoriesOf = (definition) => ({ ...definition, parts: withStories(definition.id, definition.parts) })

export const EXPO_86_POSTERS = {
  'expo-86-davidson': withStoriesOf(EXPO_86_DAVIDSON),
  'expo-86-fiorucci': withStoriesOf(EXPO_86_FIORUCCI),
  'our-british-columbia': withStoriesOf(OUR_BRITISH_COLUMBIA)
}
