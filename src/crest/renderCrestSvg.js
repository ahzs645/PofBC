// The crest identity as a complete SVG.
//
// Framework-free like every other renderer here: string building over a table of numbers, so the
// preview, the exporter and a Node script all produce the same drawing.

import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'
import { crestLockupMarkup, layoutCrestLockup } from './crestLayout.js'

/** The height the arms are laid out at. Everything else is proportional to it. */
export const CREST_SIZE = 100

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value) => Math.round(value * 1000) / 1000

/**
 * @param {object} options
 * @param {string} [options.arrangement]  'horizontal' | 'vertical'
 * @param {string} [options.placement]    'beside' | 'below'
 * @param {string} [options.ministry]     The ministry. Newlines break lines.
 * @param {string} [options.extra]        A further line — a branch, a division, a region.
 * @param {string} [options.align]        'centre' | 'left', for a stacked lockup's ministry.
 * @param {string} [options.ministrySize] A key of `MINISTRY_SIZES`.
 * @param {string} [options.extraStep]    'match' | 'smaller', for the trailing line.
 * @param {boolean} [options.bold]
 * @param {string} [options.markColor]    The arms and the wordmark.
 * @param {string} [options.textColor]    The ministry. Falls back to the mark's colour.
 * @param {string} [options.background]
 * @param {number} [options.clearSpaceFactor]
 * @param {number} [options.pixelWidth]
 * @param {string} [options.title]
 * @param {object} [options.glyphs]
 * @param {string} [options.fontCss]
 */
export const renderCrestSvg = ({
  arrangement = 'horizontal',
  placement = 'beside',
  ministry = '',
  extra = '',
  bold = false,
  align = 'centre',
  ministrySize,
  extraStep,
  markColor = '#000000',
  textColor,
  background = TRANSPARENT,
  clearSpaceFactor = 0,
  pixelWidth,
  title,
  glyphs,
  fontCss
} = {}) => {
  const layout = layoutCrestLockup({
    arrangement, placement, ministry, extra, bold, align, ministrySize, extraStep, size: CREST_SIZE
  })
  const ink = resolveColor(markColor)
  const type = resolveColor(textColor ?? markColor)

  const padding = clearSpaceFactor * layout.box.width
  const box = {
    x: layout.box.x - padding,
    y: layout.box.y - padding,
    width: layout.box.width + padding * 2,
    height: layout.box.height + padding * 2
  }

  const dimensions = pixelWidth
    ? ` width="${pixelWidth}" height="${Math.round(pixelWidth * box.height / box.width)}"`
    : ''

  const fill = resolveColor(background, TRANSPARENT)
  const backdrop = fill && fill !== TRANSPARENT
    ? `<rect x="${round(box.x)}" y="${round(box.y)}" width="${round(box.width)}" height="${round(box.height)}" fill="${escapeXml(fill)}"/>`
    : ''

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${round(box.x)} ${round(box.y)} ${round(box.width)} ${round(box.height)}"${dimensions}>` +
    (title ? `<title>${escapeXml(title)}</title>` : '') +
    (fontCss ? `<defs><style>${fontCss}</style></defs>` : '') +
    backdrop +
    crestLockupMarkup({ layout, markColor: ink, textColor: type, glyphs }) +
    '</svg>'

  return { svg, box, layout }
}

/** The lockup's size in layout units, before any clear space. */
export const crestSize = (options = {}) => {
  const { box } = layoutCrestLockup({ ...options, size: CREST_SIZE })
  return { width: box.width, height: box.height }
}
