import { useLayoutEffect, useState } from 'react'

/**
 * Puts an SVG document (as a string) into `hostRef` and returns the live <svg> element, sized to
 * its container. `prepare` may rewrite the string first, e.g. to point image references at the
 * app's base path.
 */
export const useInlineSvg = (hostRef, raw, { prepare } = {}) => {
  const [svg, setSvg] = useState(null)

  useLayoutEffect(() => {
    const host = hostRef.current
    host.innerHTML = prepare ? prepare(raw) : raw
    const el = host.querySelector('svg')
    el.removeAttribute('width')
    el.removeAttribute('height')
    el.setAttribute('preserveAspectRatio', 'xMidYMid meet')
    setSvg(el)
    return () => {
      host.innerHTML = ''
      setSvg(null)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [raw])

  return svg
}
