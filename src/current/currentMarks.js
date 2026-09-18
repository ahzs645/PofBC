// The Province's current ministry marks.
//
// Unlike the historical lockups, nothing here is drawn from parts: these are the official files,
// extracted from the published PDF and served whole. The guidelines are explicit that the marks
// must be used exactly as provided, so the only thing this module does to them is apply one of the
// Province's own four colourways and put them on a background.
//
// The artwork lives in public/current-marks/ and is fetched on demand — 23 ministries in two
// languages is a couple of megabytes, and a visit uses one of them.

import { TRANSPARENT, resolveColor } from '../logo/logoColors.js'

const BASE = `${import.meta.env?.BASE_URL ?? '/'}current-marks/`

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

// ── Loading ──────────────────────────────────────────────────────────────────────────────────────

let cataloguePromise
const markCache = new Map()

/** The list of ministries, with the size of each mark. Fetched once. */
export const loadCatalogue = () => {
  cataloguePromise ??= fetch(`${BASE}index.json`)
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return response.json()
    })
    .catch((error) => {
      cataloguePromise = undefined
      throw new Error(`Could not load the current ministry marks. ${error.message}`)
    })

  return cataloguePromise
}

/** One ministry's mark, as the SVG source. Cached, since switching back and forth is cheap. */
export const loadMark = (code, language) => {
  const key = `${code}-${language}`.toLowerCase()

  if (!markCache.has(key)) {
    markCache.set(
      key,
      fetch(`${BASE}${key}.svg`)
        .then((response) => {
          if (!response.ok) throw new Error(`HTTP ${response.status}`)
          return response.text()
        })
        .catch((error) => {
          markCache.delete(key)
          throw new Error(`Could not load the ${code} mark. ${error.message}`)
        })
    )
  }

  return markCache.get(key)
}

// ── Rendering ────────────────────────────────────────────────────────────────────────────────────

const VIEWBOX = /viewBox="([\d.\s-]+)"/
const ROLED_ELEMENT = /<(path|rect)([^>]*?)data-role="(\w+)"([^>]*?)\/>/g
const FILL = /\sfill="[^"]*"/

/** Applies a colourway to the official artwork, leaving the geometry untouched. */
export const recolour = (source, variant) => {
  const { fills } = CURRENT_VARIANTS[variant] ?? CURRENT_VARIANTS.colour

  return source.replace(ROLED_ELEMENT, (element, tag, before, role, after) => {
    if (!(role in fills)) return element

    const colour = fills[role]
    // A role with no colour is dropped rather than painted, so the background shows through.
    if (colour === null) return ''

    // The role is re-emitted, not consumed: it has to survive so a colourway can be applied again
    // over the top, and so a file served from here still carries its labels.
    const attributes = `${before}${after}`.replace(FILL, '').trimEnd()
    return `<${tag} data-role="${role}"${attributes} fill="${colour}"/>`
  })
}

/** The artwork's own dimensions, in PDF points. */
export const markSize = (source) => {
  const [, box] = VIEWBOX.exec(source) ?? []
  const [, , width, height] = (box ?? '0 0 0 0').split(/\s+/).map(Number)
  return { width, height }
}

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

/**
 * A ministry mark as a complete SVG, in the requested colourway.
 *
 * @param {object} options
 * @param {string} options.source        The fetched artwork.
 * @param {string} [options.variant]     One of CURRENT_VARIANT_ORDER.
 * @param {string} [options.background]  'none' for transparent, or any colour.
 * @param {number} [options.padding]     Clear space, in the artwork's own units.
 * @param {number} [options.pixelWidth]  Sets width/height attributes at this pixel width.
 * @param {string} [options.title]       Accessible name.
 */
export const renderCurrentSvg = ({
  source,
  variant = 'colour',
  background = TRANSPARENT,
  padding = 0,
  pixelWidth,
  title
}) => {
  const { width, height } = markSize(source)
  const inner = recolour(source, variant)
    // Take the artwork's own contents; the wrapper is rebuilt with the margin and background.
    .replace(/^[\s\S]*?<svg[^>]*>/, '')
    .replace(/<\/svg>\s*$/, '')
    .replace(/<title>[\s\S]*?<\/title>/, '')

  const box = {
    x: -padding,
    y: -padding,
    width: width + padding * 2,
    height: height + padding * 2
  }

  const dimensions = pixelWidth
    ? ` width="${pixelWidth}" height="${Math.round(pixelWidth * box.height / box.width)}"`
    : ''

  const fill = resolveColor(background, TRANSPARENT)
  const backdrop = fill && fill !== TRANSPARENT
    ? `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" fill="${escapeXml(fill)}"/>`
    : ''

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box.x} ${box.y} ${box.width} ${box.height}"${dimensions}>` +
    (title ? `<title>${escapeXml(title)}</title>` : '') +
    backdrop +
    inner +
    '</svg>'
}
