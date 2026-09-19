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

/** The BC identity palette, as the colour-accessibility guidance states it for screen. */
export const BCID = {
  blue: '#234075',
  gold: '#e3a82b',
  blueTint: '#7b8cac',
  goldTint: '#eecb80',
  white: '#ffffff',
  black: '#000000'
}

/**
 * The four official colourways.
 *
 * Each maps a shape's role to the colour it takes. `null` removes the fill entirely, which is how
 * the solid versions let the background show through the sun's rays — painting those white instead
 * would put a white halo around the mark on anything but a white page.
 *
 * The mountains and the wordmark are the same blue in the artwork and part company here: reverse
 * lightens the mountains but turns the wordmark white. That is the reason the extraction labels
 * every shape rather than relying on its fill.
 */
export const CURRENT_VARIANTS = {
  colour: {
    label: 'Colour',
    description: 'The mark as drawn. For white and very light backgrounds.',
    fills: {
      sun: BCID.gold,
      mountains: BCID.blue,
      knockout: BCID.white,
      wordmark: BCID.blue,
      divider: BCID.gold,
      name: BCID.blue
    }
  },
  reverse: {
    label: 'Reverse',
    description: 'For BC Blue and black. The mountains lighten and the type goes white.',
    fills: {
      sun: BCID.gold,
      mountains: BCID.blueTint,
      knockout: BCID.white,
      wordmark: BCID.white,
      divider: BCID.gold,
      name: BCID.white
    }
  },
  black: {
    label: 'Solid black',
    description: 'One colour. For BC Gold, the 60% tints, and white.',
    fills: {
      sun: BCID.black,
      mountains: BCID.black,
      knockout: null,
      wordmark: BCID.black,
      divider: BCID.black,
      name: BCID.black
    }
  },
  white: {
    label: 'Solid white',
    description: 'One colour. For BC Blue and black.',
    fills: {
      sun: BCID.white,
      mountains: BCID.white,
      knockout: null,
      wordmark: BCID.white,
      divider: BCID.white,
      name: BCID.white
    }
  }
}

export const CURRENT_VARIANT_ORDER = ['colour', 'reverse', 'black', 'white']

/**
 * The backgrounds the Province's guidance actually sanctions the mark on, light to dark.
 *
 * Offered instead of the crest era's palette, whose forest green is not a BC identity colour at
 * all — and which, left in place when the era changed, put blue type on green.
 */
export const BCID_PALETTE = [
  { name: 'white', value: BCID.white },
  { name: 'gold 60%', value: BCID.goldTint },
  { name: 'gold', value: BCID.gold },
  { name: 'blue 60%', value: BCID.blueTint },
  { name: 'blue', value: BCID.blue },
  { name: 'black', value: BCID.black }
]

export const LANGUAGES = { en: 'English', fr: 'Français' }
export const LANGUAGE_ORDER = ['en', 'fr']

// Which colourway the guidance pairs with each background, so the app can start somewhere sensible
// rather than making the person cross-reference a table.
const RECOMMENDED = [
  { match: (background) => background === TRANSPARENT, variant: 'colour' },
  { match: (background) => background === BCID.blue || background === BCID.black, variant: 'reverse' },
  { match: (background) => background === BCID.gold || background === BCID.blueTint || background === BCID.goldTint, variant: 'black' }
]

/** The colourway the Province pairs with a given background, or null where it says nothing. */
export const recommendedVariant = (background) => {
  const resolved = resolveColor(background, TRANSPARENT).toLowerCase()
  return RECOMMENDED.find((rule) => rule.match(resolved))?.variant ?? null
}

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
