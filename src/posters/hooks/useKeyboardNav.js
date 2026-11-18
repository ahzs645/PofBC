import { useEffect } from 'react'

/**
 * Arrow keys step through `order`, digits jump to an index, and `keys` adds any other single-key bindings. Nothing fires
 * while typing in a field or while `enabled` is false.
 */
export const useKeyboardNav = ({ order, current, onSelect, keys = {}, enabled = true }) => {
  useEffect(() => {
    if (!enabled) return
    const onKey = (e) => {
      if (e.defaultPrevented || e.target.matches?.('input, textarea, select, [contenteditable]')) return
      if (e.metaKey || e.ctrlKey || e.altKey) return
      const i = order.indexOf(current)
      if (e.key === 'ArrowRight') onSelect(order[(i + 1) % order.length])
      else if (e.key === 'ArrowLeft') onSelect(order[(i - 1 + order.length) % order.length])
      else if (/^[1-9]$/.test(e.key) && Number(e.key) < order.length) onSelect(order[Number(e.key)])
      else if (keys[e.key.toLowerCase()]) keys[e.key.toLowerCase()](e)
    }
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  }, [order, current, onSelect, keys, enabled])
}
