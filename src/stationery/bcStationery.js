// The 1977 General Use stationery of the B.C. Visual Identity Program, as brandkit templates.
//
// Every measurement is from the Reproduction Manual's specification sheets (page R08, "General
// Use stationery"; the letterhead and calling card are explained on R03), which give each piece
// as a grid of columns in millimetres and its type in points:
//
//   Letterhead   8½ × 11 in    9 | 18 symbol | 9 | 55 | 55 | 70 mm; 9 mm to the type's hang line,
//                              a 20 mm band, then the rule. Province of British Columbia in 10 pt
//                              Helvetica Medium, the ministry in 10 pt Regular (4.25 mm leading),
//                              a split ministry name in 6 pt caps, the address column in 8 pt
//                              (3.25 mm leading). Symbol 19 mm, crest and ring.
//   Envelope     No. 10        8 | 15 symbol | 8 | 34 | 34 mm; 8 mm, a 16 mm band; 9 pt type on
//                              4 mm leading; the return address in 8 pt under the rule. Symbol 16
//                              mm. Symbol and type both in Pantone 462 (brown).
//   Calling card 3½ × 2 in     4 | 12 symbol | 4 | 30 | 39 mm; 6 mm to the hang line. 9 pt above
//                              the rule; below it, the name in 7 pt Medium, title and component in
//                              7 pt Italic, the address in 7 pt on 3 mm leading. Symbol 12.5 mm.
//
// A hang line is the top of the capitals, so each first baseline sits a cap height below it.
// Helvetica Medium is set in the bold the site carries; Italic is the regular, slanted.

import { PROVINCIAL_MARK } from '../assets/markup.js'
import { getFaceMetrics } from '../logo/fontMetrics.js'
import { LOGO_FONT_FAMILY } from '../logo/renderLogoSvg.js'

const PT = 25.4 / 72
const CAP = getFaceMetrics('regular').capHeight / 1000
/** The baseline of type of `points` whose capitals hang from `hang` mm. */
const hung = (hang, points) => Math.round((hang + CAP * points * PT) * 100) / 100

const PROVINCE = [{ id: 'province-1', text: 'Province of', locked: true }, { id: 'province-2', text: 'British Columbia', locked: true }]

/** Pantone 462 C as Pantone publishes it for screens: a conversion, not a match to the ink. */
export const PANTONE_462 = '#5C462B'

const letterhead = {
  id: 'letterhead-general', label: 'Letterhead', group: 'General Use',
  title: 'Province of British Columbia / General Use letterhead / Format A',
  description: 'Letterhead, General Use (Format A): the 1977 B.C. Visual Identity Program specification, rebuilt. Type in Helvetica, symbol in Pantone 462.',
  width: 215.9, height: 279.4, unit: 'mm', physical: ['8.5in', '11in'], raster: 1700,
  elements: [
    { type: 'background', fill: 'paper' },
    { type: 'symbol', id: 'symbol', x: 8.5, y: 9, height: 19, colour: 'symbol' },
    { type: 'lines', x: 36, y: hung(9, 10), leading: 4.25, size: '10pt', font: 'medium', colour: 'type', lines: PROVINCE },
    { type: 'paragraph', id: 'ministry', x: 91, y: hung(9, 10), width: 52, size: '10pt', leading: 4.25, maxLines: 3, font: 'regular', colour: 'type' },
    { type: 'text', id: 'ministry-split', x: 91, y: hung(9, 10) + 3 * 4.25, size: '6pt', caps: true, font: 'regular', colour: 'type' },
    {
      type: 'lines', x: 146, y: hung(9, 8), leading: 3.25, size: '8pt', font: 'regular', colour: 'type',
      lines: [{ id: 'component' }, { id: 'address' }, { compose: '{city}, British Columbia' }, { id: 'postal-code' }, { compose: 'Telephone: {telephone}' }]
    },
    { type: 'line', id: 'rule', x1: 36, y1: 29, x2: 206.9, y2: 29, stroke: 'type', strokeWidth: '0.5pt' }
  ]
}

const envelope = {
  id: 'envelope-no10', label: 'Envelope, No. 10', group: 'General Use',
  title: 'Province of British Columbia / General Use envelope / No. 10',
  description: 'No. 10 envelope, General Use: the 1977 B.C. Visual Identity Program specification, rebuilt. Symbol and type in Pantone 462.',
  width: 241.3, height: 104.78, unit: 'mm', physical: ['9.5in', '4.125in'], raster: 1900,
  elements: [
    { type: 'background', fill: 'paper' },
    { type: 'symbol', id: 'symbol', x: 7.5, y: 8, height: 16, colour: 'symbol' },
    { type: 'lines', x: 31, y: hung(8, 9), leading: 4, size: '9pt', font: 'medium', colour: 'symbol', lines: PROVINCE },
    { type: 'paragraph', id: 'ministry', x: 65, y: hung(8, 9), width: 32, size: '9pt', leading: 4, maxLines: 3, font: 'regular', colour: 'symbol' },
    { type: 'text', id: 'ministry-split', x: 65, y: hung(8, 9) + 3 * 4, size: '6pt', caps: true, font: 'regular', colour: 'symbol' },
    { type: 'paragraph', id: 'component', x: 99, y: hung(8, 9), width: 34, size: '9pt', leading: 4, maxLines: 3, font: 'regular', colour: 'symbol' },
    { type: 'line', id: 'rule', x1: 31, y1: 24, x2: 133, y2: 24, stroke: 'symbol', strokeWidth: '0.5pt' },
    { type: 'text', id: 'return-address', compose: '{address}, {city}, British Columbia, {postal-code}', x: 31, y: 27.6, size: '8pt', font: 'regular', colour: 'symbol' }
  ]
}

const callingCard = {
  id: 'calling-card', label: 'Calling card', group: 'General Use',
  title: 'Province of British Columbia / General Use calling card',
  description: 'Calling card, General Use: the 1977 B.C. Visual Identity Program specification, rebuilt. Symbol in Pantone 462, type in black.',
  width: 88.9, height: 50.8, unit: 'mm', physical: ['3.5in', '2in'], raster: 1400, print: { trim: [88.9, 50.8], bleed: 0, unit: 'mm' },
  elements: [
    { type: 'background', fill: 'paper' },
    { type: 'symbol', id: 'symbol', x: 3.75, y: 6, height: 12.5, colour: 'symbol' },
    { type: 'lines', x: 20, y: hung(6, 9), leading: 3.8, size: '9pt', font: 'medium', colour: 'type', lines: PROVINCE },
    { type: 'paragraph', id: 'ministry', x: 50, y: hung(6, 9), width: 35, size: '9pt', leading: 3.8, maxLines: 3, font: 'regular', colour: 'type' },
    { type: 'text', id: 'ministry-split', x: 50, y: 18.3, size: '6pt', caps: true, font: 'regular', colour: 'type' },
    { type: 'line', id: 'rule', x1: 20, y1: 19.5, x2: 85, y2: 19.5, stroke: 'type', strokeWidth: '0.5pt' },
    { type: 'text', id: 'name', x: 20, y: 23.2, size: '7pt', font: 'medium', colour: 'type' },
    { type: 'text', id: 'title', x: 20, y: 26.2, size: '7pt', font: 'italic', colour: 'type' },
    { type: 'paragraph', id: 'component', x: 20, y: 29.2, width: 28, size: '7pt', leading: 3, maxLines: 2, font: 'italic', colour: 'type' },
    { type: 'text', id: 'phone-line', compose: '{telephone}', x: 20, y: 38.2, size: '7pt', font: 'regular', colour: 'type' },
    {
      type: 'lines', x: 50, y: 23.2, leading: 3, size: '7pt', font: 'regular', colour: 'type',
      lines: [{ id: 'address' }, { compose: '{city}' }, { text: 'British Columbia', locked: true }, { id: 'postal-code' }]
    }
  ]
}

/**
 * The stationery as a brandkit brand: the Province's symbol, its two inks, its type, and the
 * three General Use pieces. `fields` names what can be filled in, with the specification's own
 * placeholders as defaults.
 */
export const createStationeryBrand = ({ symbolColour = PANTONE_462 } = {}) => ({
  schema: 'brandkit/1',
  id: 'bc-1977-stationery',
  name: 'Province of British Columbia',
  version: '1977-general-use',
  colours: { brown: symbolColour, black: '#000000', white: '#FFFFFF' },
  roles: { symbol: 'brown', type: 'black', paper: 'white', ink: 'black', muted: 'black', reverse: 'white' },
  fonts: {
    medium: { family: 'HelveticaPofBC', stack: LOGO_FONT_FAMILY, weight: 700, label: 'Helvetica Medium' },
    regular: { family: 'HelveticaPofBC', stack: LOGO_FONT_FAMILY, weight: 400, label: 'Helvetica Regular' },
    italic: { family: 'HelveticaPofBC', stack: LOGO_FONT_FAMILY, weight: 400, style: 'italic', label: 'Helvetica Italic' }
  },
  symbol: { name: 'provincial-symbol', viewBox: [0, 0, PROVINCIAL_MARK.viewBox.width, PROVINCIAL_MARK.viewBox.height], markup: PROVINCIAL_MARK.inner },
  copy: { motifLabel: 'Provincial symbol, crest and ring' },
  fields: {
    ministry: { label: 'Ministry', placeholder: 'Ministry of\nAbcdefghijk\nLmnopqrstuvw', multiline: true },
    'ministry-split': { label: 'Split ministry name or branch', placeholder: 'Split ministry name' },
    name: { label: 'Name', placeholder: 'Name' },
    title: { label: 'Title', placeholder: 'Title' },
    component: { label: 'Organizational component', placeholder: 'Organizational Component', multiline: true },
    address: { label: 'Address', placeholder: 'Address' },
    city: { label: 'City', placeholder: 'City' },
    'postal-code': { label: 'Postal code', placeholder: 'Postal Code' },
    telephone: { label: 'Telephone', placeholder: '(604) 000-0000' }
  },
  templates: [callingCard, letterhead, envelope]
})

/** "Ministry of Forests" → "Ministry of\nForests": the specification sets "Ministry of" alone. */
export const ministryLines = (name) => {
  const match = /^(Ministry of(?: the)?)\s+(.+)$/i.exec(String(name).trim())
  return match ? `${match[1]}\n${match[2]}` : String(name).trim()
}
