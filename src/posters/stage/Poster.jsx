// A zoomable SVG stage with hidden hotspots.
//
// Generic on purpose: it knows nothing about this poster. Give it any SVG document, a list of
// regions in that document's units, and which one is current, and it frames the current region,
// spotlights whichever the pointer is over, and labels it with a chip that follows the cursor.
// Layer-specific effects (glyph reveals, logo swaps, dimming) are hooks the caller runs on the
// <svg> element handed back through `onReady`.

import { useEffect, useRef } from 'react'
import { AnimatePresence, motion, useMotionValue } from 'motion/react'
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
  const chipX = useMotionValue('16px')
  const chipY = useMotionValue('18px')

  const svg = useInlineSvg(hostRef, svgRaw, { prepare })
  useReadyOnce(svg, onReady)
  const hover = useHotspots(svg, regions, { onSelect, active: current, spotlight })
  useViewBoxZoom(svg, stageRef, { box: frame.box, pad: frame.pad, inset, initial: frame.initial })
  const tilt = useTilt(overview)

  const region = regions.find((r) => r.id === hover)

  const onPointerMove = (e) => {
    const rect = stageRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    // The chip sits below and right of the pointer, unless that would run it under the dock along
    // the foot or a panel down the side: then above, or to the left.
    chipX.set(x + CHIP.w > rect.width - inset.right ? `calc(${x - 12}px - 100%)` : `${x + 16}px`)
    chipY.set(y + CHIP.h > rect.height - inset.bottom ? `calc(${y - 12}px - 100%)` : `${y + 18}px`)
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
          <Chip key={region.id} x={chipX} y={chipY} title={region.label} hint={region.hint} />
        )}
      </AnimatePresence>
      {children}
    </div>
  )
}

// The room the chip needs beside the pointer: its offset, its widest (posters.css) and a two-line hint.
const CHIP = { w: 16 + 240 + 12, h: 18 + 72 + 12 }

// Calls onReady once per mounted <svg>, without making callers memoise their callback.
const useReadyOnce = (svg, onReady) => {
  const ref = useRef(onReady)
  ref.current = onReady
  useEffect(() => { if (svg) ref.current?.(svg) }, [svg])
}
