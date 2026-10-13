import { useEffect } from 'react'

/**
 * Dims every element matching `selector` for which `keep(el)` is false. Pass `keep` as null to
 * clear the dimming.
 */
export const useLayerDim = (svg, selector, keep, { dim = 0.22 } = {}) => {
  useEffect(() => {
    if (!svg) return
    for (const el of svg.querySelectorAll(selector)) el.style.opacity = keep && !keep(el) ? String(dim) : ''
  }, [svg, selector, keep, dim])
}
