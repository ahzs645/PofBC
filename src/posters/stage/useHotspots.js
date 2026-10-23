import { useEffect, useRef, useState } from 'react'

const SVG_NS = 'http://www.w3.org/2000/svg'
const NOT_DRAWN = new Set(['defs', 'title', 'desc', 'style', 'metadata', 'clipPath', 'mask', 'linearGradient', 'radialGradient', 'pattern', 'symbol'])

/** The transform from an element's parent to the root <svg>, read from the transform attributes. */
const parentMatrix = (svg, element) => {
  let matrix = svg.createSVGMatrix()
  for (let node = element.parentNode; node && node !== svg; node = node.parentNode) {
    const own = node.transform?.baseVal?.consolidate()
    if (own) matrix = own.matrix.multiply(matrix)
  }
  return matrix
}

/**
 * Invisible clickable regions drawn into an SVG in its own units.
 *
 * `regions` is [{ id, box: {x, y, w, h}, label, layer, hit }]. Each becomes a focusable target
 * with class "pv-hs" inside a <g id="hotspots">. By default the target is the box, slightly
 * enlarged. With `hit: 'shape'` the targets are the drawn shapes of the region's `layer` (a
 * selector of elements with ids), cloned with <use> and made transparent, so a region can be found
 * by the ink itself — a badge's lettering and the cigarette crossing it, say, whose boxes overlap.
 * Returns the id under the pointer.
 *
 * With `spotlight`, the open region — or, while the pointer is over one, the region under it — dims
 * everything in the drawing except that region's `layer` (any selector, any depth) and any ids in
 * `spotlight.keep`. Following the open part as well as the pointer keeps it isolated through the
 * story and after a click, once the zoom has moved the drawing out from under the pointer.
 */
export const useHotspots = (svg, regions, { onSelect, active, margin = 0.08, spotlight } = {}) => {
  const [hover, setHover] = useState(null)
  const dimmed = useRef(new Set())

  useEffect(() => {
    if (!svg) return
    const group = document.createElementNS(SVG_NS, 'g')
    group.setAttribute('id', 'hotspots')
    const target = (element, { id, label }) => {
      element.setAttribute('class', 'pv-hs')
      element.setAttribute('tabindex', '0')
      element.setAttribute('role', 'button')
      element.setAttribute('aria-label', label ? `Open the ${label.toLowerCase()}` : id)
      element.dataset.region = id
      return element
    }
    for (const region of regions) {
      const shapes = region.hit === 'shape' && region.layer ? [...svg.querySelectorAll(region.layer)].filter((el) => el.id) : []
      if (shapes.length) {
        // One focusable wrapper per region, holding a clone of each of its shapes.
        const wrapper = target(document.createElementNS(SVG_NS, 'g'), region)
        wrapper.setAttribute('class', 'pv-hs pv-hs-shape')
        for (const shape of shapes) {
          const placed = document.createElementNS(SVG_NS, 'g')
          const m = parentMatrix(svg, shape)
          placed.setAttribute('transform', `matrix(${m.a} ${m.b} ${m.c} ${m.d} ${m.e} ${m.f})`)
          const use = document.createElementNS(SVG_NS, 'use')
          use.setAttribute('href', `#${shape.id}`)
          placed.appendChild(use)
          wrapper.appendChild(placed)
        }
        group.appendChild(wrapper)
        continue
      }
      for (const box of region.boxes ?? [region.box]) {
        const m = Math.min(box.w, box.h) * margin
        const r = target(document.createElementNS(SVG_NS, 'rect'), region)
        r.setAttribute('x', box.x - m)
        r.setAttribute('y', box.y - m)
        r.setAttribute('width', box.w + 2 * m)
        r.setAttribute('height', box.h + 2 * m)
        r.setAttribute('rx', 10)
        group.appendChild(r)
      }
    }
    svg.appendChild(group)

    const regionOf = (e) => e.target.closest?.('.pv-hs')?.dataset.region
    const onClick = (e) => { const id = regionOf(e); if (!id) return; e.stopPropagation(); onSelect?.(id) }
    const onKey = (e) => {
      const id = regionOf(e)
      if (!id || (e.key !== 'Enter' && e.key !== ' ')) return
      e.preventDefault()
      onSelect?.(id)
    }
    const onOver = (e) => { const id = regionOf(e); if (id) setHover(id) }
    const onOut = (e) => { if (regionOf(e)) setHover(null) }
    const onFocusIn = (e) => { const id = regionOf(e); if (id) setHover(id) }
    const onFocusOut = () => setHover(null)
    group.addEventListener('click', onClick)
    group.addEventListener('keydown', onKey)
    group.addEventListener('pointerover', onOver)
    group.addEventListener('pointerout', onOut)
    group.addEventListener('focusin', onFocusIn)
    group.addEventListener('focusout', onFocusOut)
    return () => {
      group.remove()
      setHover(null)
    }
  }, [svg, regions, onSelect, margin])

  useEffect(() => {
    if (!svg) return
    for (const r of svg.querySelectorAll('.pv-hs')) r.classList.toggle('pv-active', r.dataset.region === active)
  }, [svg, active])

  useEffect(() => { setHover(null) }, [active])

  // The spotlight: walk down from the root, dimming every drawn element that neither holds nor is a
  // lit layer, and descending into the ones that hold one. Nothing inside a lit layer is touched.
  useEffect(() => {
    if (!svg || !spotlight) return
    for (const el of dimmed.current) el.style.opacity = ''
    dimmed.current.clear()
    const region = regions.find((r) => r.id === (hover ?? active))
    if (!region?.layer) return
    const lit = [...svg.querySelectorAll(region.layer)]
    if (!lit.length) return
    const keep = new Set(spotlight.keep ?? [])
    const walk = (parent) => {
      for (const child of parent.children) {
        if (NOT_DRAWN.has(child.tagName) || child.id === 'hotspots' || keep.has(child.id)) continue
        if (lit.includes(child)) continue
        if (lit.some((el) => child.contains(el))) { walk(child); continue }
        child.style.transition = 'opacity 320ms ease'
        child.style.opacity = String(spotlight.dim ?? 0.32)
        dimmed.current.add(child)
      }
    }
    walk(svg)
  }, [svg, hover, active, regions, spotlight])

  return hover
}
