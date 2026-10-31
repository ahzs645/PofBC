// Drawing ICBC's and BCLC's marks, exactly as supplied.
//
// These are Crown corporations' marks, from research packages that say of every file whether it is
// a supplied vector, a declared recolour or a reconstruction (src/assets/crownMarks.js). Nothing
// here changes a mark: it is placed on a ground, with clear space around it, and that is all. A
// colour a body did not use would be a new variant of its mark, and the packages already mark the
// line between what was supplied and what was derived; recolouring here would blur it.

import { CROWN_MARKS } from '../assets/crownMarks.js'
import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value) => Math.round(value * 1000) / 1000

/**
 * A supplied mark as SVG.
 *
 * @param {object} options
 * @param {string} options.id                 The mark, a key of CROWN_MARKS.
 * @param {string} [options.background]       A ground behind it; none by default.
 * @param {number} [options.clearSpace]       Margin as a fraction of the mark's shorter side.
 * @param {number} [options.width]            Pixel width to declare, for a download; none for a page.
 * @param {string} [options.title]            A title to carry, for a download.
 * @param {Record<string, string>} [options.inks]  Inks to draw in another colour, for a dark page
 *   (see darkPageInks); a value of 'surface' takes the page's own card colour.
 * @returns {{svg: string, view: {x: number, y: number, width: number, height: number}}}
 */
export const renderSuppliedSvg = ({ id, background = TRANSPARENT, clearSpace = 0, width, title, inks } = {}) => {
  const mark = CROWN_MARKS[id]
  if (!mark) throw new Error(`no supplied mark called ${id}`)
  const [x, y, w, h] = mark.viewBox
  const pad = clearSpace * Math.min(w, h)
  const view = { x: x - pad, y: y - pad, width: w + 2 * pad, height: h + 2 * pad }
  const ground = resolveColor(background, TRANSPARENT)
  const size = width ? ` width="${width}" height="${Math.max(1, Math.round(width * view.height / view.width))}"` : ''

  const svg = `<svg xmlns="http://www.w3.org/2000/svg"${size} viewBox="${[view.x, view.y, view.width, view.height].map(round).join(' ')}">` +
    (title ? `<title>${escapeXml(title)}</title>` : '') +
    (ground && ground !== TRANSPARENT
      ? `<rect x="${round(view.x)}" y="${round(view.y)}" width="${round(view.width)}" height="${round(view.height)}" fill="${escapeXml(ground)}"/>`
      : '') +
    (inks ? reink(mark.body, inks) : mark.body) +
    '</svg>'

  return { svg, view }
}

/** Whether a mark is drawn only in white, so needs a dark ground to be seen at all. */
export const isReversed = (id) => CROWN_MARKS[id].inks.every((ink) => ink === '#ffffff' || ink === '#fff')

// A page's dark form of a supplied mark. The marks are drawn as supplied wherever they are opened;
// only the gallery's cards, on a dark page, show them as their reversal would: an ink too dark to be
// seen there (black, near-black, the navies) is drawn white, and every colour of the mark's own,
// such as BCLC's dots or ICBC's blue, is kept. A mark whose white parts sit on its dark ones names
// those in `swap`, and they take the card's colour, so the reversal keeps them apart.
const DARK = 0.08

const luminance = (hex) => {
  const value = String(hex).replace('#', '')
  const full = value.length === 3 ? value.replace(/./g, '$&$&') : value
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/**
 * The inks a supplied mark changes on a dark page, or null when it needs none.
 * @param {string} id
 * @param {{ swap?: string[] }} [options]  White inks that sit on the mark's dark ones.
 */
export const darkPageInks = (id, { swap = [] } = {}) => {
  const map = {}
  for (const ink of CROWN_MARKS[id].inks) if (luminance(ink) < DARK) map[ink.toLowerCase()] = '#ffffff'
  for (const ink of swap) map[ink.toLowerCase()] = 'surface'
  return Object.keys(map).length ? map : null
}

const reink = (body, inks) => body.replace(/(fill|stroke)="(#[0-9a-f]{3,6})"/gi, (match, attr, colour) => {
  const to = inks[colour.toLowerCase()]
  if (!to) return match
  return to === 'surface' ? `style="${attr}:var(--surface)"` : `${attr}="${to}"`
})
