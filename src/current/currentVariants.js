// The current identity's colours, colourways and languages: what the generator's state, its share
// links and its agent tools need to know about the era without drawing it.
//
// Kept apart from currentMarks.js, which draws the marks and so brings the Province's artwork and
// the alphabet its wording is set in. Those are a quarter of a megabyte that every page would
// otherwise load to learn four colour names; the drawing is fetched when a current mark is first
// shown or exported. currentMarks.js re-exports everything here, so it can still be the one import.

import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'

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
