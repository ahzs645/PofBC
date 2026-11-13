// The stage a patch is inspected on: one or more panes that zoom and pan together, so a detail in
// the source stays beside the same detail in the drawing and in the simulation.
//
// Zoom with the buttons, Ctrl/⌘ + wheel, a pinch or a double click; drag to pan once zoomed. A plain
// wheel or a one-finger swipe still scrolls the page while the stage is at fit.

import { useCallback, useEffect, useRef, useState } from 'react'
import { FIT, MAX_ZOOM, MIN_ZOOM, clampPan, zoomTo } from './patchView.js'

/**
 * @param {object} props
 * @param {Array<{key: string, label: string, node: import('react').ReactNode}>} props.panes
 * @param {string} props.resetKey   Changing it returns the stage to fit (a new patch or mode).
 * @param {import('react').ReactNode} [props.toolbar]  Shown at the left of the stage's bar.
 */
export const PatchStage = ({ panes, resetKey, toolbar }) => {
  const [view, setView] = useState(FIT)
  const [expanded, setExpanded] = useState(false)
  const frame = useRef(null)
  const pointers = useRef(new Map())
  const gesture = useRef(null)

  useEffect(() => { setView(FIT) }, [resetKey])

  // One pane's box: every pane is the same size, so the first stands for all.
  const paneBox = () => frame.current?.querySelector('.patch-stage__pane')?.getBoundingClientRect() ?? null
  const fromCentre = (event) => {
    const box = event.currentTarget.getBoundingClientRect()
    return { x: event.clientX - box.left - box.width / 2, y: event.clientY - box.top - box.height / 2, box }
  }
  const zoomBy = useCallback((factor, point) => {
    const box = paneBox()
    if (!box) return
    setView((current) => zoomTo(current, current.k * factor, point?.x ?? 0, point?.y ?? 0, box.width, box.height))
  }, [])

  // React's wheel listener is passive, and stopping the page from zooming needs preventDefault.
  useEffect(() => {
    const element = frame.current
    if (!element) return undefined
    const onWheel = (event) => {
      if (!event.ctrlKey && !event.metaKey) return
      const pane = event.target.closest?.('.patch-stage__pane')
      if (!pane) return
      event.preventDefault()
      const box = pane.getBoundingClientRect()
      const point = { x: event.clientX - box.left - box.width / 2, y: event.clientY - box.top - box.height / 2 }
      setView((current) => zoomTo(current, current.k * Math.exp(-event.deltaY * 0.01), point.x, point.y, box.width, box.height))
    }
    element.addEventListener('wheel', onWheel, { passive: false })
    return () => element.removeEventListener('wheel', onWheel)
  }, [])

  useEffect(() => {
    if (!expanded) return undefined
    const onKey = (event) => { if (event.key === 'Escape') { event.stopImmediatePropagation(); setExpanded(false) } }
    // Capture, so Escape closes the enlarged stage before the viewer's own handler leaves the patch.
    globalThis.addEventListener('keydown', onKey, true)
    const { overflow } = document.body.style
    document.body.style.overflow = 'hidden'
    return () => { globalThis.removeEventListener('keydown', onKey, true); document.body.style.overflow = overflow }
  }, [expanded])

  const onPointerDown = (event) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return
    const { x, y, box } = fromCentre(event)
    pointers.current.set(event.pointerId, { x, y })
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()]
      gesture.current = { kind: 'pinch', distance: Math.hypot(a.x - b.x, a.y - b.y) || 1, view, box }
    } else if (view.k > MIN_ZOOM) {
      gesture.current = { kind: 'pan', x, y, view, box }
    } else {
      return
    }
    event.currentTarget.setPointerCapture?.(event.pointerId)
  }
  const onPointerMove = (event) => {
    if (!pointers.current.has(event.pointerId) || !gesture.current) return
    const { x, y } = fromCentre(event)
    pointers.current.set(event.pointerId, { x, y })
    const start = gesture.current
    if (start.kind === 'pinch' && pointers.current.size >= 2) {
      const [a, b] = [...pointers.current.values()]
      const k = start.view.k * (Math.hypot(a.x - b.x, a.y - b.y) / start.distance)
      setView(zoomTo(start.view, k, (a.x + b.x) / 2, (a.y + b.y) / 2, start.box.width, start.box.height))
    } else if (start.kind === 'pan') {
      setView(clampPan({ k: start.view.k, x: start.view.x + x - start.x, y: start.view.y + y - start.y }, start.box.width, start.box.height))
    }
  }
  const onPointerEnd = (event) => {
    pointers.current.delete(event.pointerId)
    gesture.current = null
  }
  const onDoubleClick = (event) => {
    const { x, y, box } = fromCentre(event)
    setView((current) => (current.k > MIN_ZOOM ? { ...FIT } : zoomTo(current, 2.5, x, y, box.width, box.height)))
  }

  const zoomed = view.k > MIN_ZOOM
  const transform = `translate(${view.x}px, ${view.y}px) scale(${view.k})`

  return (
    <div ref={frame} className={expanded ? 'patch-stage patch-stage--expanded' : 'patch-stage'}>
      <div className="patch-stage__bar">
        <div className="patch-stage__tools">{toolbar}</div>
        <div className="patch-stage__zoom" role="group" aria-label="Zoom">
          <button type="button" className="button" onClick={() => zoomBy(1 / 1.5)} disabled={!zoomed} aria-label="Zoom out" title="Zoom out">−</button>
          <button type="button" className="button patch-stage__level" onClick={() => setView(FIT)} disabled={!zoomed} title="Fit to the stage">
            {zoomed ? `${Math.round(view.k * 100)}%` : 'Fit'}
          </button>
          <button type="button" className="button" onClick={() => zoomBy(1.5)} disabled={view.k >= MAX_ZOOM} aria-label="Zoom in" title="Zoom in">+</button>
          <button type="button" className="button" onClick={() => setExpanded((on) => !on)} aria-pressed={expanded} title={expanded ? 'Back to the page (Esc)' : 'Fill the window'}>
            {expanded ? 'Close' : 'Enlarge'}
          </button>
        </div>
      </div>
      <div className={`patch-stage__panes patch-stage__panes--${panes.length}`}>
        {panes.map((pane) => (
          <figure
            key={pane.key}
            className={zoomed ? 'patch-stage__pane patch-stage__pane--zoomed' : 'patch-stage__pane'}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerEnd}
            onPointerCancel={onPointerEnd}
            onDoubleClick={onDoubleClick}
          >
            {panes.length > 1 && <figcaption>{pane.label}</figcaption>}
            <div className="patch-stage__content" style={{ transform }}>{pane.node}</div>
          </figure>
        ))}
      </div>
    </div>
  )
}
