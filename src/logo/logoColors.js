// Colour handling for the lockups.
//
// The generator lets the user set the mark colour and the background independently, which means it
// can produce combinations the brand guide would never ship. Rather than forbid them, this module
// gives the UI enough information — luminance, contrast ratio — to say when a pairing has become
// unreadable, and leaves the choice with the person making the logo.

/** The palette the source artwork and the wider provincial identity draw on. */
export const BRAND_COLORS = {
  white: '#ffffff',
  black: '#000000',
  // The green the supplied artwork is set in.
  green: '#006837',
  blue: '#234075',
  red: '#9f1d21',
  gold: '#e3a82b',
  // Keys are looked up lower-cased, so they have to be single lower-case words.
  silver: '#c0bfbf',
  grey: '#3e3e3e'
}

/** Named background choices, plus the transparent case the palette cannot express. */
export const TRANSPARENT = 'none'

/**
 * Resolves a colour name, hex string, or any CSS colour to something usable as a fill.
 * Unknown values pass through untouched so callers can use `rgb()`, `hsl()` or a var().
 */
export const resolveColor = (value, fallback = BRAND_COLORS.white) => {
  if (value == null || value === '') return fallback
  const key = String(value).toLowerCase()
  if (key === TRANSPARENT || key === 'transparent') return TRANSPARENT
  return BRAND_COLORS[key] || value
}

/** Parses #rgb / #rrggbb into `[r, g, b]` 0–255, or null for anything else. */
export const parseHex = (value) => {
  const match = /^#?([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(String(value).trim())
  if (!match) return null

  const hex = match[1].length === 3
    ? [...match[1]].map((character) => character + character).join('')
    : match[1]

  return [0, 2, 4].map((offset) => parseInt(hex.slice(offset, offset + 2), 16))
}

// WCAG relative luminance: channels are linearised before weighting, which is why this is not a
// simple average. Used for both the light/dark decision and the contrast ratio.
const relativeLuminance = (rgb) => {
  const [r, g, b] = rgb.map((channel) => {
    const value = channel / 255
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

// The luminance at which a background contrasts equally with black and with white. Solving
// 1.05 / (L + 0.05) = (L + 0.05) / 0.05 gives L = sqrt(0.0525) - 0.05 ≈ 0.1791. Above it, dark ink
// wins; below it, light ink does. Eyeballing a threshold here gets mid-tones like the brand gold
// wrong — it looks dark next to white, but black type on it is four times as legible as white.
const INK_CROSSOVER_LUMINANCE = Math.sqrt(0.0525) - 0.05

/** True when a colour is light enough that dark ink reads better on it. */
export const isLightColor = (value) => {
  const rgb = parseHex(resolveColor(value))
  return rgb ? relativeLuminance(rgb) > INK_CROSSOVER_LUMINANCE : false
}

/**
 * WCAG contrast ratio between two colours, 1–21, or null if either cannot be parsed.
 * A transparent background is judged against white, the likeliest surface a logo lands on.
 */
export const contrastRatio = (foreground, background) => {
  const resolvedBackground = resolveColor(background)
  const front = parseHex(resolveColor(foreground))
  const back = parseHex(resolvedBackground === TRANSPARENT ? BRAND_COLORS.white : resolvedBackground)
  if (!front || !back) return null

  const [lighter, darker] = [relativeLuminance(front), relativeLuminance(back)].sort((a, b) => b - a)
  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * How a mark/background pairing reads, for the UI to surface.
 * The thresholds are WCAG's for large text and graphical objects, which is what a logo is.
 */
export const describeContrast = (foreground, background) => {
  const ratio = contrastRatio(foreground, background)
  if (ratio == null) return { ratio: null, level: 'unknown', message: '' }

  const rounded = Math.round(ratio * 10) / 10
  // Worded without naming a part: the same function judges the mark and the type, and the caller
  // says which one it is reporting on.
  if (ratio < 1.5) return { ratio: rounded, level: 'fail', message: 'All but invisible here.' }
  if (ratio < 3) return { ratio: rounded, level: 'warn', message: 'Low contrast — hard to read at small sizes.' }
  return { ratio: rounded, level: 'pass', message: 'Good contrast.' }
}

/** The colour that reads best on a given background — used for the sensible-default pairings. */
export const preferredInkFor = (background) => (
  isLightColor(background) ? BRAND_COLORS.green : BRAND_COLORS.white
)
