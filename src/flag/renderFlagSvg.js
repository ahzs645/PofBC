// The flag identity as a complete SVG.
//
// Framework-free, like every other renderer here: plain string building over a table of numbers,
// so the preview, the exporter and a Node script all produce the same drawing.

import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'
import { flagLockupMarkup, layoutFlagLockup } from './flagLayout.js'

/** The BC cap height the lockup is laid out at. Everything else is proportional to it. */
export const FLAG_CAP = 100

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value) => Math.round(value * 1000) / 1000

/**
 * @param {object} options
 * @param {string} options.ministry      The wording beneath the letters.
 * @param {string} [options.letterColor] The BC letters. Also the flag, when it is set in one ink.
 * @param {string} [options.textColor]   The wording. Falls back to the letters' colour.
 * @param {string} [options.flagColour]  'colour' for the flag's own three, 'ink' for one.
 * @param {string} [options.background]
 * @param {number} [options.clearSpaceFactor]  Margin as a fraction of the lockup's own width.
 * @param {number} [options.pixelWidth]
 * @param {string} [options.title]
 * @param {object} [options.glyphs]      Outline table; draws the type as paths instead of text.
 * @param {string} [options.fontCss]     Embedded @font-face, for a self-contained file.
 */
export const renderFlagSvg = ({
  ministry = '',
  letterColor = '#000000',
  textColor,
  flagColour = 'colour',
  background = TRANSPARENT,
  clearSpaceFactor = 0,
  pixelWidth,
  title,
  glyphs,
  fontCss
} = {}) => {
  const layout = layoutFlagLockup({ ministry, cap: FLAG_CAP })
  const ink = resolveColor(letterColor)
  const type = resolveColor(textColor ?? letterColor)

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
    flagLockupMarkup({
      layout,
      letterColor: ink,
      textColor: type,
      // One ink means the flag is painted in the letters' colour rather than its own three.
      flagInk: flagColour === 'ink' ? ink : undefined,
      glyphs
    }) +
    '</svg>'

  return { svg, box, layout }
}

/** The lockup's size in layout units, before any clear space. */
export const flagSize = (ministry) => {
  const { box } = layoutFlagLockup({ ministry, cap: FLAG_CAP })
  return { width: box.width, height: box.height }
}
