import { useEffect, useRef } from 'react'
import { useReducedMotion } from 'motion/react'
import { easeInOutQuint, easeOutQuint, fit, tween } from './zoom.js'

const setViewBox = (svg, v) => svg.setAttribute('viewBox', `${v.x} ${v.y} ${v.w} ${v.h}`)

/**
 * Keeps an SVG's viewBox framed on `box` (with `pad`, a fraction of its size), animating between
 * targets and refitting on resize.
 *
 * `inset` is the part of the stage covered by floating UI ({ right, bottom } in px): the box is
 * fitted into what is left and the viewBox then widened to cover the whole stage, so the subject
 * stays centred in the uncovered area.
 *
 * A new target while a zoom is still running picks up from where that one is, already moving, so
 * stepping quickly through targets reads as one continuous glide rather than a run of restarts.
 */
export const useViewBoxZoom = (svg, stageRef, { box, pad = 0.05, inset = { right: 0, bottom: 0 }, duration = 1000, initial }) => {
  const vb = useRef(initial ?? { x: 0, y: 0, w: 1, h: 1 })
  const stop = useRef(null)
  const running = useRef(false)
  const reduced = useReducedMotion()
  const key = `${box.x},${box.y},${box.w},${box.h},${pad}`

  const target = () => {
    const rect = stageRef.current.getBoundingClientRect()
    const free = { width: Math.max(rect.width - inset.right, 200), height: Math.max(rect.height - inset.bottom, 200) }
    const v = fit(box, pad, free)
    const unitsPerPx = v.w / free.width
    return { x: v.x, y: v.y, w: v.w + inset.right * unitsPerPx, h: v.h + inset.bottom * unitsPerPx }
  }
  // The resize observer outlives renders, so it reads the latest target through a ref.
  const latest = useRef(target)
  latest.current = target

  useEffect(() => {
    if (!svg) return
    const moving = running.current
    stop.current?.()
    running.current = true
    stop.current = tween(vb.current, target(), {
      duration: reduced ? 0 : duration,
      ease: moving ? easeOutQuint : easeInOutQuint,
      onUpdate: (v) => { vb.current = v; setViewBox(svg, v) },
      onComplete: () => { running.current = false }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [svg, key, inset.right, inset.bottom, reduced, duration])

  useEffect(() => () => stop.current?.(), [])

  // Only a real change of the stage's size refits, and it snaps: the observer's first call on
  // observe() is skipped, or it would jump to the target for a frame under a running zoom.
  useEffect(() => {
    if (!svg) return
    let observed = false
    const observer = new ResizeObserver(() => {
      if (!observed) { observed = true; return }
      stop.current?.()
      running.current = false
      vb.current = latest.current()
      setViewBox(svg, vb.current)
    })
    observer.observe(stageRef.current)
    return () => observer.disconnect()
  }, [svg, stageRef])

  return vb
}
