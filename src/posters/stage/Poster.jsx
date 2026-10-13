// A zoomable SVG stage with hidden hotspots.
//
// Generic on purpose: it knows nothing about this poster. Give it any SVG document, a list of
// regions in that document's units, and which one is current, and it frames the current region,
// spotlights whichever the pointer is over, and labels it with a chip that follows the cursor.
// Layer-specific effects (glyph reveals, logo swaps, dimming) are hooks the caller runs on the
// <svg> element handed back through `onReady`.

import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { useInlineSvg } from './useInlineSvg.js'
import { useHotspots } from './useHotspots.js'
import { useViewBoxZoom } from './useViewBoxZoom.js'
import { useTilt } from './useTilt.js'
import { Chip } from '../ui/Chip.jsx'

export function Poster({
  svgRaw,
  prepare,
  regions,
  current,
  frame,
  inset = { right: 0, bottom: 0 },
  overview = false,
  spotlight = { keep: ['background'] },
  className = '',
  onSelect,
  onReady,
  children
}) {
  const stageRef = useRef(null)
  const hostRef = useRef(null)
  const [cursor, setCursor] = useState({ x: 0, y: 0 })

  const svg = useInlineSvg(hostRef, svgRaw, { prepare })
  useReadyOnce(svg, onReady)
  const hover = useHotspots(svg, regions, { onSelect, active: current, spotlight })
  useViewBoxZoom(svg, stageRef, { box: frame.box, pad: frame.pad, inset, initial: frame.initial })
  const tilt = useTilt(overview)

  const region = regions.find((r) => r.id === hover)

  const onPointerMove = (e) => {
    const rect = stageRef.current.getBoundingClientRect()
    setCursor({ x: e.clientX - rect.left, y: e.clientY - rect.top })
    tilt.move(e, rect)
  }

  return (
    <div
      ref={stageRef}
      className={`pv-stage ${overview ? 'pv-overview' : ''} ${className}`}
      aria-label="Zoomable drawing"
      onClick={() => { if (!overview) onSelect?.(null) }}
      onPointerMove={onPointerMove}
      onPointerLeave={tilt.reset}
    >
      <motion.div ref={hostRef} className="pv-sheet" style={{ rotateX: tilt.rx, rotateY: tilt.ry }} />
      <AnimatePresence>
        {region && region.id !== current && (
          <Chip key={region.id} x={cursor.x} y={cursor.y} title={region.label} hint={region.hint} />
        )}
      </AnimatePresence>
      {children}
    </div>
  )
}

// Calls onReady once per mounted <svg>, without making callers memoise their callback.
const useReadyOnce = (svg, onReady) => {
  const ref = useRef(onReady)
  ref.current = onReady
  useEffect(() => { if (svg) ref.current?.(svg) }, [svg])
}
