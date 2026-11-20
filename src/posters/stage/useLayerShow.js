import { useEffect } from 'react'

/**
 * Shows one option's layers and hides the others'. `options` is [{ id, show }], `show` a selector
 * of the layers only that option has (a sign's changeable strip, say, one face per option); an
 * option without one shows nothing of its own. The change is made on the live <svg>, so an export
 * of the stage carries it.
 */
export const useLayerShow = (svg, options, current) => {
  useEffect(() => {
    if (!svg || !options) return
    for (const { id, show } of options) {
      if (!show) continue
      for (const el of svg.querySelectorAll(show)) {
        if (id === current) el.removeAttribute('display')
        else el.setAttribute('display', 'none')
      }
    }
  }, [svg, options, current])
}
