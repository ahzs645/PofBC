// Embeds the brand typeface directly into exported artwork.
//
// A standalone SVG — saved to disk, or loaded into an <img> to be rasterised — cannot see the host
// page's @font-face rules. Without this the type silently falls back to a system sans and the
// export stops matching the preview the person just approved.
//
// Both faces are needed: the province wordmark is bold and the ministry line is not.

export const BRAND_FONT_FAMILY = 'HelveticaPofBC'

// `new URL(..., import.meta.url)` is standard ESM that Vite also rewrites at build time, so this
// resolves in a bundled app and in a plain module script alike. The specifiers must stay literal
// for that rewriting to happen — do not refactor them into a variable.
const FACE_URLS = {
  400: new URL('../fonts/generated/regular.ttf', import.meta.url).href,
  700: new URL('../fonts/generated/bold.ttf', import.meta.url).href
}

const toBase64 = (buffer) => {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  // Chunked to stay under the argument-count limit of String.fromCharCode on a large font.
  const chunkSize = 0x8000
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize))
  }
  return btoa(binary)
}

let cachedFaces = null

/**
 * Fetches both faces and returns them as base64, keyed by weight. Cached after the first call —
 * exports are usually run several times in a row, and the faces are ~50 KB each.
 *
 * Resolves to null if the fonts cannot be fetched, so an export still succeeds with a fallback
 * face rather than failing outright.
 */
export const getEmbeddedFaces = async () => {
  if (cachedFaces !== null) return cachedFaces

  try {
    const entries = await Promise.all(
      Object.entries(FACE_URLS).map(async ([weight, url]) => {
        const response = await fetch(url)
        if (!response.ok) throw new Error(`HTTP ${response.status} fetching ${url}`)
        return [weight, toBase64(await response.arrayBuffer())]
      })
    )

    cachedFaces = Object.fromEntries(entries)
  } catch (error) {
    console.error('Could not embed the brand font; the export will use a fallback face.', error)
    cachedFaces = null
    return null
  }

  return cachedFaces
}

/** @font-face rules with both faces inlined, ready to drop into an SVG <style>. */
export const getEmbeddedFontCss = async () => {
  const faces = await getEmbeddedFaces()
  if (!faces) return ''

  return Object.entries(faces).map(([weight, base64]) => (
    `@font-face{font-family:'${BRAND_FONT_FAMILY}';` +
    `src:url(data:font/truetype;base64,${base64}) format('truetype');` +
    `font-weight:${weight};font-style:normal;}`
  )).join('')
}
