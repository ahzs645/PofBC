// The flag identity as a complete SVG.
//
// Framework-free, like every other renderer here: plain string building over a table of numbers,
// so the preview, the exporter and a Node script all produce the same drawing.

import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'
import { flagLockupMarkup, flagMarkup, layoutFlagLockup } from './flagLayout.js'
import { badgeLines, frameMarkup, layoutBadge } from './parksBadge.js'
import { outlineTextMarkup } from '../logo/textOutline.js'
import { LOGO_FONT_FAMILY } from '../logo/renderLogoSvg.js'

/** The BC cap height the lockup is laid out at. Everything else is proportional to it. */
export const FLAG_CAP = 100

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const round = (value) => Math.round(value * 1000) / 1000

/**
 * @param {object} options
 * @param {string} options.ministry      The ministry. Newlines break lines.
 * @param {string} [options.symbol]      'horizontal' | 'vertical' | 'flag'
 * @param {string} [options.placement]   'below' | 'beside'
 * @param {boolean} [options.province]   Set "Province of British Columbia" above the ministry.
 * @param {string} [options.extra]       A third line.
 * @param {string} [options.letterColor] The BC letters. Also the flag, when it is set in one ink.
 * @param {string} [options.textColor]   The wording. Falls back to the letters' colour.
 * @param {string} [options.flagPalette]  'official', 'modern' or 'ink'.
 * @param {string} [options.background]
 * @param {number} [options.clearSpaceFactor]  Margin as a fraction of the lockup's own width.
 * @param {number} [options.pixelWidth]
 * @param {string} [options.title]
 * @param {object} [options.glyphs]      Outline table; draws the type as paths instead of text.
 * @param {string} [options.fontCss]     Embedded @font-face, for a self-contained file.
 */
export const renderFlagSvg = ({
  ministry = '',
  symbol = 'horizontal',
  placement = 'below',
  province = false,
  extra = '',
  bold = false,
  letterColor = '#000000',
  textColor,
  flagPalette = 'official',
  background = TRANSPARENT,
  clearSpaceFactor = 0,
  pixelWidth,
  title,
  glyphs,
  fontCss
} = {}) => {
  // The badge is its own composition — a frame, and two words set alike inside it — so it does not
  // go through the lockup layout at all. The ministry field supplies the second word.
  const badge = symbol === 'badge'
    ? layoutBadge({ second: String(ministry).replace(/\s+/g, ' ').trim() || 'Parks', cap: FLAG_CAP })
    : null
  const layout = badge ?? layoutFlagLockup({ ministry, symbol, placement, province, extra, bold, cap: FLAG_CAP })
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
    (badge
      ? frameMarkup(badge, ink) +
        flagMarkup(badge.flag, flagPalette, ink) +
        (glyphs
          ? outlineTextMarkup(badgeLines(badge), glyphs, type)
          : badgeLines(badge).map((line) =>
            `<text data-role="name" x="${round(line.x)}" y="${round(line.y)}" fill="${escapeXml(type)}"` +
            ` font-family="${escapeXml(LOGO_FONT_FAMILY)}" font-size="${round(line.style.fontSize)}"` +
            ' font-weight="700">' + escapeXml(line.text) + '</text>').join(''))
      : flagLockupMarkup({ layout, letterColor: ink, textColor: type, flagPalette, glyphs })) +
    '</svg>'

  return { svg, box, layout }
}

/** The lockup's size in layout units, before any clear space. */
export const flagSize = (options = {}) => {
  // The badge has its own layout, and an export asks for the box before anything is drawn — so
  // this has to branch the same way the renderer does or a badge exports at the wrong size.
  const { box } = options.symbol === 'badge'
    ? layoutBadge({ second: String(options.ministry ?? '').replace(/\s+/g, ' ').trim() || 'Parks', cap: FLAG_CAP })
    : layoutFlagLockup({ ...options, cap: FLAG_CAP })
  return { width: box.width, height: box.height }
}
