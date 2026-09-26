// A mark's colours for the page it is shown on.
//
// The gallery's marks were published on grounds of their own — WelcomeBC on a blue panel, WorkBC on
// navy, StrongerBC and BC Stats on white — so laid side by side as published they read as a stack
// of pictures cut from different sources. Shown on the gallery itself, every mark sits on the one
// ground the page has, in the version the BC identity sanctions for it: its colour version on a
// light page, its reversal on a dark one.
//
// What makes each mark its own is kept: the gold "BC", StrongerBC's grey divider, BC Timber Sales'
// green, the maple leaf. Only what the page's ground decides changes — whether the name and the
// mountains are BC blue or white — and nothing is taken from the published colours that the
// reversal does not change. The exact published version is still one choice away, as the first
// starting point every mark opens with.

const BC_BLUE = '#004b8d'
/** The mountains of the Province's reversed marks: lighter, so they still read against a dark ground. */
const REVERSED_MOUNTAINS = '#4a6ea7'
const WHITE = '#ffffff'

const rgb = (hex) => {
  const value = String(hex ?? '').replace('#', '')
  if (!/^[0-9a-f]{6}$/i.test(value)) return null
  return [0, 2, 4].map((offset) => parseInt(value.slice(offset, offset + 2), 16) / 255)
}

/** Relative luminance, as WCAG defines it. */
export const luminance = (hex) => {
  const channels = rgb(hex)
  if (!channels) return null
  const [r, g, b] = channels.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/** Hue in degrees and saturation, 0–1. */
const hueAndSaturation = (hex) => {
  const [r, g, b] = rgb(hex)
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const saturation = max === 0 ? 0 : (max - min) / max
  if (max === min) return { hue: 0, saturation }
  const d = max - min
  const hue = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4
  return { hue: (hue * 60 + 360) % 360, saturation }
}

const lighten = (hex, amount) => `#${rgb(hex).map((c) => Math.round((c + (1 - c) * amount) * 255).toString(16).padStart(2, '0')).join('')}`

/** Parts that are the mark's own colour whatever the ground: the sun and its light, and the leaf. */
const FIXED = new Set(['sun', 'rays', 'core', 'light', 'leaf'])

/**
 * The colours a published mark takes on a page of `theme`, with no ground of its own.
 *
 * @param {Record<string, string>} printed  The mark's published colours, by part, with its background.
 * @param {'light'|'dark'} theme
 */
export const pageColoursFor = (printed, theme) => {
  const ground = printed.background
  const groundLuminance = luminance(ground)
  // Published on a dark or mid-toned panel — the reversal — as against on white.
  const reversed = groundLuminance !== null && groundLuminance < 0.5
  const colours = { ...printed, background: 'none' }

  for (const [role, colour] of Object.entries(printed)) {
    if (role === 'background' || FIXED.has(role) || luminance(colour) === null) continue
    if (theme === 'light' && reversed) {
      // A reversed mark on a light page takes the colour version: white type and the lighter
      // mountains go back to BC blue.
      if (role === 'mountains' || luminance(colour) > 0.8) colours[role] = BC_BLUE
    }
    // On a dark page the mountains are always the reversal's lighter blue, even on a mark published
    // on a mid-toned panel like Canada's Pacific Gateway red, where they were left dark.
    if (theme === 'dark' && role === 'mountains' && luminance(colour) < luminance(REVERSED_MOUNTAINS)) {
      colours[role] = REVERSED_MOUNTAINS
      continue
    }
    if (theme === 'dark' && !reversed) {
      // A mark published on white, on a dark page, takes the reversal: the mountains lighten, and
      // dark type goes white — unless it is a colour of the mark's own, like BC Timber Sales'
      // green, which lightens instead of being lost.
      if (role === 'mountains') colours[role] = REVERSED_MOUNTAINS
      else if (luminance(colour) < 0.2) {
        const { hue, saturation } = hueAndSaturation(colour)
        const own = saturation > 0.45 && !(hue >= 190 && hue <= 250)
        colours[role] = own ? lighten(colour, 0.35) : WHITE
      }
    }
  }
  return colours
}
