import { useEffect, useRef } from 'react'

const PAINTS = ['fill', 'stroke']

/**
 * Recolours a drawing on the stage: every fill or stroke attribute equal to a `from` colour is set
 * to its `to`. `swaps` is [[from, to], …]; pass null to put the drawing's own colours back. The
 * change is made on the live <svg>, so an export of the stage carries it.
 */
export const useColourSwap = (svg, swaps) => {
  // Each repainted attribute's own colour, so that any swap starts from the drawing as it was.
  const original = useRef(new Map())

  useEffect(() => {
    if (!svg) return
    for (const [el, paints] of original.current) for (const [name, value] of Object.entries(paints)) el.setAttribute(name, value)
    original.current = new Map()
    if (!swaps?.length) return
    const to = new Map(swaps.map(([from, into]) => [from.toLowerCase(), into]))
    for (const el of svg.querySelectorAll('[fill], [stroke]')) {
      for (const name of PAINTS) {
        const value = el.getAttribute(name)
        const into = value && to.get(value.toLowerCase())
        if (!into) continue
        original.current.set(el, { ...original.current.get(el), [name]: value })
        el.setAttribute(name, into)
      }
    }
  }, [svg, swaps])
}
