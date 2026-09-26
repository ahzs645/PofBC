// BC Hydro's 1990 and current marks: drawn from their artwork, in the colours each may take.
//
// Unlike the 1961 signature, which is rebuilt from a manual's rules, these are lifted whole from the
// supplied files (src/assets/hydroMarks.js, by scripts/extract_hydro_marks.py) and only coloured
// here. The 1990 mark is history, so any part can take any colour. The current logo is not: BC
// Hydro's guidelines give it exactly three colourways, a version without its tagline for signage,
// and a symbol with and without a white border — and forbid reconstructing, recolouring or
// rearranging it. So it is offered in those, and in nothing else.

import { HYDRO_MARKS } from '../assets/hydroMarks.js'
import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'

/**
 * The current palette, as the guidelines give it for screens ("BinHex"). The logo's artwork in the
 * PDF is a print conversion and a shade off these; the guidelines name these as the digital values.
 */
export const HYDRO_PALETTE = {
  granite: '#3e3935',
  grass: '#50b848',
  sea: '#10a3c8',
  ice: '#ffffff',
  spruce: '#004f6c',
  hemlock: '#046a38',
  arbutus: '#fa4616',
  tide: '#9adbe8',
  sunset: '#e8927c',
  sand: '#cbc4bc',
  stone: '#9c948d',
  moss: '#bcd19b',
  quartz: '#fcd299'
}

export const HYDRO_PALETTE_SWATCHES = [
  { name: 'Ice', value: HYDRO_PALETTE.ice },
  { name: 'Tide', value: HYDRO_PALETTE.tide },
  { name: 'Sand', value: HYDRO_PALETTE.sand },
  { name: 'Grass', value: HYDRO_PALETTE.grass },
  { name: 'Sea', value: HYDRO_PALETTE.sea },
  { name: 'Spruce', value: HYDRO_PALETTE.spruce },
  { name: 'Hemlock', value: HYDRO_PALETTE.hemlock },
  { name: 'Granite', value: HYDRO_PALETTE.granite },
  { name: 'black', value: '#000000' }
]

const { granite, grass, sea, ice } = HYDRO_PALETTE
const allIn = (ink, roles) => Object.fromEntries(roles.map((role) => [role, ink]))
const LOGO = ['upper', 'lower', 'wordmark', 'tagline']

/**
 * The current logo's variations, in the guidelines' own words. Each is a drawing and its colours;
 * the background is the one the guidelines put it on, and is the only thing left to choose.
 */
export const CURRENT_VARIANTS = {
  colour: {
    label: 'Colour',
    mark: 'bc-hydro-2016',
    colours: { upper: grass, lower: sea, wordmark: granite, tagline: granite },
    background: ice,
    hint: 'For use against a white background in colour applications (including four-colour process, spot colour and onscreen).'
  },
  black: {
    label: 'Black',
    mark: 'bc-hydro-2016',
    colours: allIn('#000000', LOGO),
    background: ice,
    hint: 'For use against a white background in limited-colour applications.'
  },
  reverse: {
    label: 'Reverse',
    mark: 'bc-hydro-2016',
    colours: allIn(ice, LOGO),
    background: granite,
    hint: 'For use against colourful, dark or busy backgrounds in both full- and limited-colour applications.'
  },
  signage: {
    label: 'Without tagline',
    mark: 'bc-hydro-2016',
    colours: { upper: grass, lower: sea, wordmark: granite },
    omit: ['tagline'],
    background: ice,
    hint: 'Only for signage and permanent installations — never use it anywhere else.'
  },
  symbol: {
    label: 'Symbol',
    mark: 'bc-hydro-2016-symbol',
    colours: { upper: grass, lower: sea },
    background: ice,
    hint: 'Where space is limited or legibility is a concern: permanent signage, power boxes or uniforms. Its Grass and Sea are part of it, always.'
  },
  'symbol-border': {
    label: 'Symbol with border',
    mark: 'bc-hydro-2016-symbol-border',
    colours: { border: ice, upper: grass, lower: sea },
    background: granite,
    hint: 'On a coloured or patterned background, so the symbol stays clear and visible.'
  }
}
export const CURRENT_VARIANT_ORDER = Object.keys(CURRENT_VARIANTS)

/** The 1990 mark's parts, as the controls name them. */
export const MARK_1990_PARTS = [
  { label: 'BC', role: 'bc' },
  { label: 'hydro', role: 'hydro' },
  { label: 'Symbol, upper half', role: 'upper' },
  { label: 'Symbol, lower half', role: 'lower' }
]

/** Starting colours for the 1990 mark: as supplied, then one ink each way. */
export const MARK_1990_PRESETS = [
  { id: 'supplied', label: 'As supplied', colours: { ...HYDRO_MARKS['bc-hydro-1990'].printed, background: ice } },
  { id: 'mono', label: 'One ink', colours: { ...allIn('#000000', ['bc', 'hydro', 'upper', 'lower']), background: ice } },
  { id: 'reverse', label: 'Reversed', colours: { ...allIn(ice, ['bc', 'hydro', 'upper', 'lower']), background: '#000000' } }
]

const round = (value) => Math.round(value * 1000) / 1000

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

/** How wide a mark's symbol is — the guidelines' unit of clear space. */
export const symbolWidth = (id) => {
  const halves = HYDRO_MARKS[id].shapes.filter(({ role }) => role === 'upper' || role === 'lower' || role === 'border')
  return Math.max(...halves.map(({ box }) => box[2])) - Math.min(...halves.map(({ box }) => box[0]))
}

/**
 * A mark as SVG.
 *
 * @param {object} options
 * @param {string} options.id                     A key of HYDRO_MARKS.
 * @param {object} [options.colours]              Part → colour; anything missing is as supplied.
 * @param {string[]} [options.omit]               Parts to leave out — the tagline, for signage.
 * @param {string} [options.background]           A colour, or transparent.
 * @param {'symbol'|'none'|number} [options.clearSpace]  One symbol's width all round, none, or
 *   that many symbol widths — previews use a fraction, so a coloured ground does not end at the ink.
 * @param {number} [options.width]                Pixel width written on the root.
 * @param {string} [options.title]
 * @returns {{svg: string, view: {x: number, y: number, width: number, height: number}}}
 */
export const renderHydroMarkSvg = ({ id, colours = {}, omit = [], background = TRANSPARENT, clearSpace = 'symbol', width, title } = {}) => {
  const mark = HYDRO_MARKS[id]
  if (!mark) throw new Error(`no BC Hydro mark called ${id}`)
  const shapes = mark.shapes.filter(({ role }) => !omit.includes(role))

  const left = Math.min(...shapes.map(({ box }) => box[0]))
  const top = Math.min(...shapes.map(({ box }) => box[1]))
  const right = Math.max(...shapes.map(({ box }) => box[2]))
  const bottom = Math.max(...shapes.map(({ box }) => box[3]))
  const pad = symbolWidth(id) * (clearSpace === 'symbol' ? 1 : typeof clearSpace === 'number' ? clearSpace : 0)
  const view = { x: left - pad, y: top - pad, width: right - left + 2 * pad, height: bottom - top + 2 * pad }
  const pixels = width ?? Math.round(view.width * 4)
  const ground = resolveColor(background, TRANSPARENT)

  const parts = shapes.map(({ role, d, evenOdd }) => {
    const fill = resolveColor(colours[role] ?? mark.printed[role], TRANSPARENT)
    if (!fill || fill === TRANSPARENT) return ''
    return `<path data-role="${role}" d="${d}" fill="${escapeXml(fill)}"${evenOdd ? ' fill-rule="evenodd"' : ''}/>`
  })

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${pixels}" height="${Math.max(1, Math.round(pixels * view.height / view.width))}" ` +
    `viewBox="${[view.x, view.y, view.width, view.height].map(round).join(' ')}" role="img"><title>${escapeXml(title ?? 'BC Hydro')}</title>` +
    (ground && ground !== TRANSPARENT
      ? `<rect x="${round(view.x)}" y="${round(view.y)}" width="${round(view.width)}" height="${round(view.height)}" fill="${escapeXml(ground)}"/>`
      : '') +
    parts.join('') +
    '</svg>'

  return { svg, view }
}

/** The current logo in one of its variations, on a background of your choosing. */
export const renderCurrentHydroSvg = ({ variant = 'colour', background, clearSpace, width } = {}) => {
  const spec = CURRENT_VARIANTS[variant] ?? CURRENT_VARIANTS.colour
  return renderHydroMarkSvg({
    id: spec.mark,
    colours: spec.colours,
    omit: spec.omit,
    background: background ?? spec.background,
    clearSpace,
    width,
    title: `BC Hydro logo — ${spec.label.toLowerCase()}`
  })
}
