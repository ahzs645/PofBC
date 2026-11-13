import { useEffect } from 'react'

const NS = 'http://www.w3.org/2000/svg'

/** The id of the layer the reference is drawn in; exports leave it out (see export/exportSvg.js). */
export const REFERENCE_LAYER = 'pv-reference'

/**
 * Lays a reference picture of the original over the drawing, in the drawing's own units, so the
 * two share one frame however the stage is zoomed. `reference` is { src, box } (where the picture
 * sits in the drawing); `mode` is 'reconstruction' (no picture), 'original' (the picture alone, on
 * white) or 'overlay' (the picture at `opacity` over the drawing).
 */
export const useReferenceOverlay = (svg, reference, mode, opacity = 0.5) => {
  useEffect(() => {
    if (!svg || !reference || mode === 'reconstruction') return undefined
    const { x, y, w, h } = reference.box
    const layer = document.createElementNS(NS, 'g')
    layer.setAttribute('id', REFERENCE_LAYER)
    layer.setAttribute('pointer-events', 'none')
    if (mode === 'original') {
      const ground = document.createElementNS(NS, 'rect')
      for (const [name, value] of Object.entries({ x, y, width: w, height: h, fill: '#ffffff' })) ground.setAttribute(name, value)
      layer.append(ground)
    }
    const picture = document.createElementNS(NS, 'image')
    for (const [name, value] of Object.entries({ x, y, width: w, height: h, href: reference.src, preserveAspectRatio: 'none' })) picture.setAttribute(name, value)
    picture.setAttribute('opacity', mode === 'overlay' ? String(opacity) : '1')
    layer.append(picture)
    // Under the hotspots, so the parts can still be found through it.
    svg.insertBefore(layer, svg.querySelector('#hotspots'))
    return () => layer.remove()
  }, [svg, reference, mode, opacity])
}
