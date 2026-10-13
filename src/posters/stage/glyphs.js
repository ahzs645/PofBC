// Lifts individual glyph paths out of an outlined-lettering SVG so they can be shown on their own.
//
// A lettering renderer that writes each letter as a path with data-character / data-glyph
// attributes and a transform of the form translate(tx ty) scale(s -s) is what this expects.
// getBBox() reports the path in its own (font) units, so the box is mapped through that
// transform into the drawing's units by hand.

const TRANSFORM = /translate\(([-\d.]+)\s+([-\d.]+)\)\s*scale\(([-\d.]+)\s+([-\d.]+)\)/

/**
 * @param {SVGSVGElement} svg     a mounted SVG
 * @param {string} selector       which paths to lift
 * @param {object} [options]
 * @param {boolean} [options.unique]  one card per glyph name
 * @param {object} [options.notes]    { glyphName: [letter, whereItAppears] }
 * @param {number} [options.margin]   breathing room around the glyph, in drawing units
 */
export const extractGlyphs = (svg, selector, { unique = false, notes = {}, margin = 6 } = {}) => {
  const seen = new Set()
  const out = []
  for (const path of svg.querySelectorAll(selector)) {
    const name = path.dataset.glyph
    if (unique && seen.has(name)) continue
    seen.add(name)
    const t = TRANSFORM.exec(path.getAttribute('transform') || '')
    if (!t) continue
    const b = path.getBBox()
    const [tx, ty, s] = [Number(t[1]), Number(t[2]), Number(t[3])]
    const x0 = tx + s * b.x
    const x1 = tx + s * (b.x + b.width)
    const y0 = ty - s * (b.y + b.height)
    const y1 = ty - s * b.y
    const [letter, where] = notes[name] || [path.dataset.character, '']
    out.push({
      key: `${name}-${out.length}`,
      name,
      letter,
      where,
      id: path.dataset.glyphId,
      viewBox: `${x0 - margin} ${y0 - margin} ${x1 - x0 + 2 * margin} ${y1 - y0 + 2 * margin}`,
      d: path.getAttribute('d'),
      transform: path.getAttribute('transform')
    })
  }
  return out
}
