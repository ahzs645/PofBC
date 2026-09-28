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
 * @returns {{svg: string, view: {x: number, y: number, width: number, height: number}}}
 */
export const renderSuppliedSvg = ({ id, background = TRANSPARENT, clearSpace = 0, width, title } = {}) => {
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
    mark.body +
    '</svg>'

  return { svg, view }
}

/** Whether a mark is drawn only in white, so needs a dark ground to be seen at all. */
export const isReversed = (id) => CROWN_MARKS[id].inks.every((ink) => ink === '#ffffff' || ink === '#fff')
