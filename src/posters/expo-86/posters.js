// The Expo 86 poster of Robert Davidson’s artwork: its parts, where each sits in the drawing, and
// what the panel says about it. Data only — the drawing is attached in ./index.js — as for the
// Forest Service posters (see ../forest-service/posters.js for the shape of a part and a panel).
//
// Unlisted: the poster is not on the shelf (its series says `unlisted`), but its address opens it:
// ?view=posters&poster=expo-86-davidson. Boxes are in the drawing's own units, measured from its
// named groups in Chromium.

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
        heading: 'Expo 86 — Robert Davidson',
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
          { links: [EXPO_LOGOS_LINK, EXPO_CORPORATION_LINK] }
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
          { figure: 'review', alt: 'Two versions side by side — the restored reference artwork and the reconstructed poster — and below them an enlarged strip of the poster’s foot with the logo, signature and event text', caption: 'The restored reference artwork beside the reconstructed poster, and the foot enlarged. The reference’s cream border is the restoration’s, not a measured margin.' }
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
          'Rebuilt by hand as 25 rounded strokes from a photograph taken through glass. The name and the year are clear; small crossings — after the R, and between the letters of Davidson — are smoothed where reflection hides them.',
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
        lede: 'The fair’s stacked mark — EXPO over the three interlocking rings of 86 — printed in the poster’s black, with a small TM.',
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

export const EXPO_86_POSTERS = { 'expo-86-davidson': { ...EXPO_86_DAVIDSON, parts: withStories('expo-86-davidson', EXPO_86_DAVIDSON.parts) } }
