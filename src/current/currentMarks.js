// The Province's current ministry marks.
//
// The BC mark itself — the sun, the mountains and the wordmark — is the Province's own drawing,
// used exactly as published. The ministry wording beside it is set, in the same alphabet, to the
// measurements taken off that artwork; the official names ship with the line breaks the Province
// gave them, and match their published files to a hundredth of a point.
//
// The artwork used to be 46 finished files, one per ministry per language, each carrying its own
// copy of the mark and its name as outlines. It is now the mark once per language plus the
// alphabet those names were lettered with, so a name can be set rather than only chosen — and the
// whole era fits in the bundle instead of being fetched.

import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'
import { layoutLockup, lockupMarkup } from './currentLayout.js'
import { CURRENT_VARIANTS } from './currentVariants.js'

// The palette, the four colourways and the languages are in currentVariants.js, which the rest of
// the generator can read without loading the artwork.
export * from './currentVariants.js'

// ── Rendering ────────────────────────────────────────────────────────────────────────────────────

/**
 * A ministry mark as a complete SVG.
 *
 * The mark itself is the Province's own drawing, stored once; the wording is set from the same
 * alphabet that drawing was lettered with. Nothing is fetched — both live in the bundle — so this
 * is synchronous and works in Node, in the browser and in an exporter alike.
 *
 * @param {object} options
 * @param {string} options.text        The ministry name. A newline is a line break.
 * @param {string} [options.language]  'en' | 'fr' — picks the wordmark and its measurements.
 * @param {string} [options.variant]   One of CURRENT_VARIANT_ORDER.
 * @param {string} [options.background]
 * @param {number} [options.clearSpaceFactor]  Margin as a fraction of the mark's own width.
 * @param {number} [options.pixelWidth]        Sets width/height attributes at this pixel width.
 * @param {string} [options.title]     Accessible name.
 */
export const renderCurrentSvg = ({
  text,
  language = 'en',
  variant = 'colour',
  background = TRANSPARENT,
  clearSpaceFactor = 0,
  pixelWidth,
  title
}) => {
  const { fills } = CURRENT_VARIANTS[variant] ?? CURRENT_VARIANTS.colour
  const { markup, box } = lockupMarkup({ text, language, fills })

  const padding = clearSpaceFactor * box.width
  const frame = {
    x: box.x - padding,
    y: box.y - padding,
    width: box.width + padding * 2,
    height: box.height + padding * 2
  }

  const dimensions = pixelWidth
    ? ` width="${pixelWidth}" height="${Math.round(pixelWidth * frame.height / frame.width)}"`
    : ''

  const fill = resolveColor(background, TRANSPARENT)
  const backdrop = fill && fill !== TRANSPARENT
    ? `<rect x="${round(frame.x)}" y="${round(frame.y)}" width="${round(frame.width)}" height="${round(frame.height)}" fill="${escapeXml(fill)}"/>`
    : ''

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${round(frame.x)} ${round(frame.y)} ${round(frame.width)} ${round(frame.height)}"${dimensions}>` +
    (title ? `<title>${escapeXml(title)}</title>` : '') +
    backdrop +
    markup +
    '</svg>'
}

/** The lockup's size in points, before any clear space. */
export const markSize = ({ text, language = 'en' }) => {
  const { box } = layoutLockup({ text, language })
  return { width: box.width, height: box.height }
}

const round = (value) => Math.round(value * 1000) / 1000

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
