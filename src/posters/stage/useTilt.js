import { useEffect } from 'react'
import { useMotionValue, useReducedMotion, useSpring } from 'motion/react'

/** A little parallax: springs for rotateX/rotateY that follow the pointer while `enabled`. */
export const useTilt = (enabled, { degrees = 3 } = {}) => {
  const reduced = useReducedMotion()
  const rx = useSpring(useMotionValue(0), { stiffness: 120, damping: 20 })
  const ry = useSpring(useMotionValue(0), { stiffness: 120, damping: 20 })

  const move = (e, rect) => {
    if (!enabled || reduced || e.pointerType === 'touch') return
    const nx = (e.clientX - rect.left) / rect.width - 0.5
    const ny = (e.clientY - rect.top) / rect.height - 0.5
    rx.set(-ny * degrees)
    ry.set(nx * degrees)
  }
  const reset = () => { rx.set(0); ry.set(0) }
  useEffect(() => { if (!enabled) reset() }, [enabled]) // eslint-disable-line react-hooks/exhaustive-deps

  return { rx, ry, move, reset }
}
