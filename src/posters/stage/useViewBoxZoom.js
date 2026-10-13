import { useEffect, useRef } from 'react'
import { useReducedMotion } from 'motion/react'
import { fit, tween } from './zoom.js'

const setViewBox = (svg, v) => svg.setAttribute('viewBox', `${v.x} ${v.y} ${v.w} ${v.h}`)

/**
 * Keeps an SVG's viewBox framed on `box` (with `pad`, a fraction of its size), animating between
 * targets and refitting on resize.
 *
 * `inset` is the part of the stage covered by floating UI ({ right, bottom } in px): the box is
 * fitted into what is left and the viewBox then widened to cover the whole stage, so the subject
 * stays centred in the uncovered area.
 */
export const useViewBoxZoom = (svg, stageRef, { box, pad = 0.05, inset = { right: 0, bottom: 0 }, duration = 1000, initial }) => {
  const vb = useRef(initial ?? { x: 0, y: 0, w: 1, h: 1 })
  const reduced = useReducedMotion()
  const key = `${box.x},${box.y},${box.w},${box.h},${pad}`

  const target = () => {
    const rect = stageRef.current.getBoundingClientRect()
    const free = { width: Math.max(rect.width - inset.right, 200), height: Math.max(rect.height - inset.bottom, 200) }
    const v = fit(box, pad, free)
    const unitsPerPx = v.w / free.width
    return { x: v.x, y: v.y, w: v.w + inset.right * unitsPerPx, h: v.h + inset.bottom * unitsPerPx }
  }

  useEffect(() => {
    if (!svg) return
    return tween(vb.current, target(), {
      duration: reduced ? 0 : duration,
      onUpdate: (v) => { vb.current = v; setViewBox(svg, v) }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [svg, key, inset.right, inset.bottom, reduced, duration])

  useEffect(() => {
    if (!svg) return
    const observer = new ResizeObserver(() => { vb.current = target(); setViewBox(svg, vb.current) })
    observer.observe(stageRef.current)
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [svg, key, inset.right, inset.bottom])

  return vb
}
