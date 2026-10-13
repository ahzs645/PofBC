import { useCallback, useEffect, useState } from 'react'

/**
 * Hands-free stepping through `order`: while playing, `onAdvance` is called with the next id every
 * `seconds`. The caller stops it on any manual navigation by calling `stop`.
 */
export const useTour = ({ order, current, onAdvance, seconds = 12 }) => {
  const [playing, setPlaying] = useState(false)

  useEffect(() => {
    if (!playing) return
    const timer = setTimeout(() => {
      const i = order.indexOf(current)
      onAdvance(order[(i + 1) % order.length])
    }, seconds * 1000)
    return () => clearTimeout(timer)
  }, [playing, current, order, onAdvance, seconds])

  const toggle = useCallback(() => setPlaying((p) => !p), [])
  const stop = useCallback(() => setPlaying(false), [])
  return { playing, toggle, stop, seconds }
}
