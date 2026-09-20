// How the flag is coloured.
//
// The identity's own standards page — "B.C. Flag Symbol · Colour Usage · Vertical and Horizontal"
// — names three inks and a rule for the fourth:
//
//     Pantone Blue    072C
//     Pantone Red     032C
//     Pantone Yellow  109C
//     Use White when applicable
//
// and adds: "When printed or painted on coloured background White shall be used as fourth colour."
//
// The artwork this project was given is drawn in a later recolouring — a navy, a darker red and a
// gold — so both are offered, keyed by the colour each shape carries in the source file.

import { FLAG_PALETTE } from '../assets/flagMark.js'
import { TRANSPARENT, isLightColor, resolveColor } from '../logo/logoColors.js'

const [SOURCE_BLUE, SOURCE_RED, SOURCE_YELLOW] = FLAG_PALETTE

export const FLAG_PALETTES = {
  official: {
    label: 'Official',
    description: 'Pantone Blue 072C, Red 032C and Yellow 109C, as the standards page specifies.',
    // sRGB for the three Pantone inks. Screen approximations of spot colours, which is the best
    // any screen can do with them.
    fills: {
      [SOURCE_BLUE]: '#10069f',
      [SOURCE_RED]: '#ef3340',
      [SOURCE_YELLOW]: '#ffd100'
    }
  },
  modern: {
    label: 'Modern',
    description: 'The navy, red and gold the artwork was supplied in.',
    fills: {
      [SOURCE_BLUE]: SOURCE_BLUE,
      [SOURCE_RED]: SOURCE_RED,
      [SOURCE_YELLOW]: SOURCE_YELLOW
    }
  },
  ink: {
    label: 'One ink',
    description: 'The whole flag in the same colour as the letters.',
    // Resolved against the lockup's own ink at render time; see flagLockupMarkup.
    fills: null
  }
}

export const FLAG_PALETTE_ORDER = ['official', 'modern', 'ink']

/**
 * The grounds and inks the standards page sanctions.
 *
 * Its own examples are the symbol on white and on a yellow panel, and it names white as the
 * fourth colour — so these are the three inks, white, and black for the one-colour documents.
 */
export const FLAG_SWATCHES = [
  { name: 'white', value: '#ffffff' },
  { name: 'yellow 109C', value: '#ffd100' },
  { name: 'red 032C', value: '#ef3340' },
  { name: 'blue 072C', value: '#10069f' },
  { name: 'black', value: '#000000' }
]

export const FLAG_PALETTE_LABELS = Object.fromEntries(
  Object.entries(FLAG_PALETTES).map(([id, entry]) => [id, entry.label])
)

export const FLAG_PALETTE_HINTS = Object.fromEntries(
  Object.entries(FLAG_PALETTES).map(([id, entry]) => [id, entry.description])
)

/**
 * The palette a background calls for, or null where it says nothing.
 *
 * The flag's white is not painted — it is the page between the bands, and the Union Jack's
 * diagonals besides. Put the full-colour flag on anything but white and the background shows
 * through all of it. The documents solve this the same way: on a coloured ground the whole lockup
 * is set in one ink.
 */
export const recommendedPalette = (background) => {
  const resolved = resolveColor(background, TRANSPARENT).toLowerCase()
  if (resolved === TRANSPARENT) return null
  return isLightColor(resolved) ? null : 'ink'
}

/** The colour a source shape takes under a palette. `ink` overrides every shape. */
export const paletteFill = (palette, sourceFill, ink) => {
  const chosen = FLAG_PALETTES[palette] ?? FLAG_PALETTES.official
  if (!chosen.fills) return ink
  return chosen.fills[sourceFill] ?? sourceFill
}
