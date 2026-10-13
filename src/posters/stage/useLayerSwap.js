import { useEffect, useRef } from 'react'
import { animate, useReducedMotion } from 'motion/react'

/**
 * Replaces the contents of one group in an SVG with another SVG document, fitted into `slot`
 * ({ x, y, w, h } in the host's units). Pass null to restore the original contents.
 */
export const useLayerSwap = (svg, selector, replacement, slot, { align = 'xMaxYMax meet' } = {}) => {
  const original = useRef(null)
  const reduced = useReducedMotion()

  useEffect(() => {
    if (!svg) return
    const layer = svg.querySelector(selector)
    if (!layer) return
    if (original.current == null) original.current = layer.innerHTML
    if (!replacement) {
      layer.innerHTML = original.current
      return
    }
    const doc = new DOMParser().parseFromString(replacement, 'image/svg+xml')
    const el = document.importNode(doc.documentElement, true)
    el.setAttribute('x', slot.x)
    el.setAttribute('y', slot.y)
    el.setAttribute('width', slot.w)
    el.setAttribute('height', slot.h)
    el.setAttribute('preserveAspectRatio', align)
    layer.replaceChildren(el)
    if (!reduced) animate(el, { opacity: [0, 1] }, { duration: 0.35 })
  }, [svg, selector, replacement, slot, align, reduced])
}
