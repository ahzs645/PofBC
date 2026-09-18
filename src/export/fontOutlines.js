// Loads the glyph outlines used by exports that convert type to paths.
//
// Kept out of the main bundle: it is around 200 KB of path data, and most exports keep their text
// live and never touch it. The dynamic import is what makes it a separate chunk.

let cached

/**
 * The outline table, keyed 'regular' / 'bold'. Cached after the first call.
 * Resolves to null if it cannot be loaded, so the caller can fall back to live text rather than
 * failing the export outright.
 */
export const getGlyphOutlines = async () => {
  if (cached !== undefined) return cached

  try {
    const module = await import('../fonts/generated/outlines.js')
    cached = module.default
  } catch (error) {
    console.error('Could not load the glyph outlines; the export will keep its text live.', error)
    cached = null
  }

  return cached
}
