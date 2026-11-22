// The spotlight, as a walk over a drawing: every drawn element that neither is nor holds a lit
// layer is dimmed, and the ones that hold one are walked into, so nothing inside a lit layer is
// touched. Shared by the stage (useHotspots.js), which dims the live drawing, and by the pins' 3D
// view (src/pins/PinModel.jsx), which prints a dimmed copy on the button's face.

export const NOT_DRAWN = new Set(['defs', 'title', 'desc', 'style', 'metadata', 'clipPath', 'mask', 'linearGradient', 'radialGradient', 'pattern', 'symbol'])

/**
 * Calls `dim(element)` for each element to dim under `root`. `lit` is the lit layer's elements;
 * `keep` holds ids never dimmed (the paper, say), at any depth.
 */
export const spotlightWalk = (root, lit, keep, dim) => {
  const walk = (parent) => {
    for (const child of parent.children) {
      if (NOT_DRAWN.has(child.tagName) || child.id === 'hotspots' || keep.has(child.id)) continue
      if (lit.includes(child)) continue
      if (lit.some((el) => child.contains(el))) { walk(child); continue }
      dim(child)
    }
  }
  walk(root)
}

/**
 * A copy of a drawing's markup with one layer spotlit, as the stage shows it while that part is
 * open: the rest at `spotlight.dim` (0.32 unless it says otherwise). Unchanged if the layer finds
 * nothing.
 */
export const spotlitMarkup = (svgText, layer, spotlight = {}) => {
  const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml')
  const root = doc.documentElement
  const lit = layer ? [...root.querySelectorAll(layer)] : []
  if (!lit.length) return svgText
  const opacity = String(spotlight.dim ?? 0.32)
  spotlightWalk(root, lit, new Set(spotlight.keep ?? []), (el) => el.setAttribute('opacity', opacity))
  return new XMLSerializer().serializeToString(doc)
}
