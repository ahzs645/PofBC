import { useEffect } from 'react'
import { animate, stagger, useReducedMotion } from 'motion/react'

/** While `active`, the elements matching `selector` fade in one after another. */
export const useGlyphReveal = (svg, selector, active, { each = 0.045, startDelay = 0.45, duration = 0.55 } = {}) => {
  const reduced = useReducedMotion()
  useEffect(() => {
    if (!svg || !active || !selector || reduced) return
    const items = [...svg.querySelectorAll(selector)]
    const clear = () => items.forEach((el) => { el.style.opacity = '' })
    const controls = animate(items, { opacity: [0, 1] }, { delay: stagger(each, { startDelay }), duration, ease: 'easeOut' })
    controls.then(clear)
    return () => { controls.stop(); clear() }
  }, [svg, selector, active, each, startDelay, duration, reduced])
}
