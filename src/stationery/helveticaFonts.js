// The site's Helvetica as a brandkit font provider, for the stationery.
//
// brandkit's template engine measures and outlines type through a provider (see
// vendor/brandkit/src/fonts/provider.js). This one is built from what the lockups already use: the
// committed advance widths (src/logo/fontMetrics.js), so wrapping is right before anything loads,
// and the outlines generated from the licensed face (src/export/fontOutlines.js), so images and
// PDFs set the type as paths. Without the outlines, `has()` is false and the engine keeps the text
// live in the embedded face instead.

import { FALLBACK_WIDTH, getFaceMetrics } from '../logo/fontMetrics.js'
import { getGlyphOutlines } from '../export/fontOutlines.js'

// The roles the stationery templates set type in, and the face and slant each uses. The 1977
// specification calls for Helvetica Medium; the bold face is the nearest the site carries.
export const STATIONERY_FACES = {
  medium: { face: 'bold', slant: 0 },
  regular: { face: 'regular', slant: 0 },
  italic: { face: 'regular', slant: 12 }
}

const SHEAR = (degrees) => Math.tan(degrees * Math.PI / 180)

/** Moves an absolute path (fontkit's toSVG: M L Q C Z) by a scale, a shear and an offset. */
const place = (d, scale, dx, dy, shear) => {
  const numbers = (text) => text.trim().split(/[\s,]+|(?=-)/).filter(Boolean).map(Number)
  return d.replace(/([MLHVQCZ])([^MLHVQCZ]*)/gi, (match, command, body) => {
    const values = numbers(body)
    if (command === 'Z' || command === 'z') return 'Z'
    if (command === 'H') return `H${(values[0] * scale + dx).toFixed(3)}`
    if (command === 'V') return `V${(values[0] * scale + dy).toFixed(3)}`
    const out = []
    for (let index = 0; index + 1 < values.length; index += 2) {
      const y = values[index + 1] * scale + dy
      const x = values[index] * scale + dx + (dy - y) * shear
      out.push(`${x.toFixed(3)} ${y.toFixed(3)}`)
    }
    return `${command}${out.join(' ')}`
  })
}

/**
 * @param {object|null} outlines  The generated outline table ({ regular, bold }), or null.
 */
export const createHelveticaProvider = (outlines) => {
  const metricsOf = (key) => getFaceMetrics(STATIONERY_FACES[key]?.face === 'bold' ? 'bold' : 'regular')
  const width = (text, key, size, tracking = 0) => {
    if (!STATIONERY_FACES[key]) return 0
    const { widths } = metricsOf(key)
    const characters = [...String(text)]
    const advance = characters.reduce((sum, character) => sum + (widths.get(character.codePointAt(0)) ?? FALLBACK_WIDTH), 0)
    return advance / 1000 * size + Math.max(0, characters.length - 1) * size * tracking
  }
  const has = (key) => Boolean(STATIONERY_FACES[key] && outlines?.[STATIONERY_FACES[key].face]?.glyphs)
  const path = (text, key, size, x, y, tracking = 0, anchor = 'start') => {
    if (!has(key)) return ''
    const { face: faceKey, slant } = STATIONERY_FACES[key]
    const { unitsPerEm, glyphs } = outlines[faceKey]
    const { widths } = metricsOf(key)
    const scale = size / unitsPerEm
    let pen = x - (anchor === 'end' ? width(text, key, size, tracking) : anchor === 'middle' ? width(text, key, size, tracking) / 2 : 0)
    let d = ''
    for (const character of [...String(text)]) {
      const point = character.codePointAt(0)
      if (glyphs[point]) d += place(glyphs[point], scale, pen, y, SHEAR(slant))
      pen += (widths.get(point) ?? FALLBACK_WIDTH) / 1000 * size + size * tracking
    }
    return d
  }
  return { has, width, path }
}

/** The provider with outlines, once they load; with metrics only, if they cannot. */
export const loadHelveticaProvider = async () => createHelveticaProvider(await getGlyphOutlines())
