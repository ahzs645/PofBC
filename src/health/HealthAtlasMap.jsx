import { useEffect, useMemo, useRef, useState } from 'react'
import { forSphericalDrawing, prepareMap, selectionViewBox } from './mapGeometry.js'

const WIDTH = 800
const HEIGHT = 720
const FULL = [0, 0, WIDTH, HEIGHT]

function clampBox([x, y, width]) {
  const w = Math.max(14, Math.min(WIDTH * 1.4, width))
  const h = w * HEIGHT / WIDTH
  return [x, y, w, h]
}

// Province map for one historical framework. Region shapes come from the
// boundary files; the optional overlay is the printed source map, georectified.
export function HealthAtlasMap({ base, regions, overlay, overlayOpacity = .75, selectedId, onSelect, frameworkLabel }) {
  const geometry = useMemo(() => prepareMap(base, WIDTH, HEIGHT), [base])
  const features = useMemo(() => (regions?.features ?? []).map(forSphericalDrawing), [regions])
  const paths = useMemo(() => features.map((feature) => {
    const d = geometry.path(feature)
    const [[x0, y0], [x1, y1]] = geometry.path.bounds(feature)
    const label = feature.properties.labelPoint ? geometry.projection(feature.properties.labelPoint) : geometry.path.centroid(feature)
    return { feature, d, size: Math.max(x1 - x0, y1 - y0), label }
  }), [features, geometry])
  const land = useMemo(() => geometry.features.map((feature) => geometry.path(feature)), [geometry])
  const overlayPaths = useMemo(() => (overlay?.features ?? []).map((feature) => ({
    kind: feature.properties.kind, fill: feature.properties.fill, d: geometry.path(forSphericalDrawing(feature)),
  })), [overlay, geometry])
  const selected = paths.find((entry) => entry.feature.properties.id === selectedId)
  const [viewBox, setViewBox] = useState(FULL)
  const [hovered, setHovered] = useState(null)
  const svg = useRef(null)
  const [pixels, setPixels] = useState({ width: WIDTH, height: HEIGHT })
  const drag = useRef(null)
  const moved = useRef(false)

  // Bring a newly selected small region into view; leave the view alone otherwise.
  useEffect(() => {
    if (!selected) return
    const scale = WIDTH / viewBox[2]
    const [[x0, y0], [x1, y1]] = geometry.path.bounds(selected.feature)
    const visible = x0 >= viewBox[0] && y0 >= viewBox[1] && x1 <= viewBox[0] + viewBox[2] && y1 <= viewBox[1] + viewBox[3]
    if (selected.size * scale < 40 || !visible) setViewBox(clampBox(selectionViewBox(geometry.path, [selected.feature], WIDTH, HEIGHT)))
  }, [selectedId, regions])

  // Track the rendered size so labels stay a constant on-screen size.
  useEffect(() => {
    const element = svg.current
    if (!element || typeof ResizeObserver === 'undefined') return undefined
    const observer = new ResizeObserver(([entry]) => setPixels({ width: entry.contentRect.width || WIDTH, height: entry.contentRect.height || HEIGHT }))
    observer.observe(element)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const element = svg.current
    if (!element) return undefined
    const onWheel = (event) => {
      event.preventDefault()
      const bounds = element.getBoundingClientRect()
      const factor = event.deltaY > 0 ? 1.18 : 1 / 1.18
      setViewBox(([x, y, width, height]) => {
        const scale = Math.min(bounds.width / width, bounds.height / height)
        const px = x + (event.clientX - bounds.left - (bounds.width - width * scale) / 2) / scale
        const py = y + (event.clientY - bounds.top - (bounds.height - height * scale) / 2) / scale
        const [, , w, h] = clampBox([0, 0, width * factor])
        return [px - (px - x) * (w / width), py - (py - y) * (h / height), w, h]
      })
    }
    element.addEventListener('wheel', onWheel, { passive: false })
    return () => element.removeEventListener('wheel', onWheel)
  }, [])

  const zoom = (factor) => setViewBox(([x, y, width, height]) => {
    const [, , w, h] = clampBox([0, 0, width * factor])
    return [x + (width - w) / 2, y + (height - h) / 2, w, h]
  })
  // Map units per screen pixel.
  const unit = 1 / Math.min(pixels.width / viewBox[2], pixels.height / viewBox[3])
  const showOverlay = overlayPaths.length > 0
  const name = (entry) => entry.feature.properties.name
  const readout = hovered ?? selected?.feature.properties.name ?? 'Select an area on the map'

  return <div className="hm-map">
    <div className="hm-map-tools" role="group" aria-label="Map zoom">
      <button type="button" onClick={() => zoom(1 / 1.6)} aria-label="Zoom in">+</button>
      <button type="button" onClick={() => zoom(1.6)} aria-label="Zoom out">−</button>
      <button type="button" onClick={() => setViewBox(FULL)}>Province</button>
      <button type="button" disabled={!selected} onClick={() => selected && setViewBox(clampBox(selectionViewBox(geometry.path, [selected.feature], WIDTH, HEIGHT)))}>Selected area</button>
    </div>
    <svg ref={svg} className={`hm-svg${showOverlay ? ' has-overlay' : ''}`} viewBox={viewBox.join(' ')} role="group"
      aria-label={`${frameworkLabel} map of British Columbia`}
      onPointerDown={(event) => { if (event.button === 0) { drag.current = { x: event.clientX, y: event.clientY, box: viewBox }; moved.current = false } }}
      onPointerMove={(event) => {
        if (!drag.current || !svg.current) return
        const dx = event.clientX - drag.current.x
        const dy = event.clientY - drag.current.y
        if (!moved.current && Math.abs(dx) + Math.abs(dy) < 5) return
        if (!moved.current) { moved.current = true; event.currentTarget.setPointerCapture?.(event.pointerId) }
        const bounds = svg.current.getBoundingClientRect()
        const [x, y, width, height] = drag.current.box
        const scale = Math.min(bounds.width / width, bounds.height / height)
        setViewBox([x - dx / scale, y - dy / scale, width, height])
      }}
      onPointerUp={() => { drag.current = null }} onPointerCancel={() => { drag.current = null }}>
      <rect className="hm-sea" x={-WIDTH} y={-HEIGHT} width={WIDTH * 3} height={HEIGHT * 3} />
      <g className="hm-land" aria-hidden="true">{land.map((d, index) => <path key={index} d={d} />)}</g>
      {showOverlay && <g className="hm-overlay" style={{ opacity: overlayOpacity }} aria-hidden="true">
        {overlayPaths.map((entry, index) => entry.kind === 'line'
          ? <path key={index} d={entry.d} className="hm-overlay-line" vectorEffect="non-scaling-stroke" />
          : <path key={index} d={entry.d} className={`hm-overlay-${entry.kind}`} style={entry.fill ? { fill: entry.fill } : undefined} />)}
      </g>}
      <g className="hm-regions">{paths.map((entry) => {
        const { id, colour } = entry.feature.properties
        const chosen = id === selectedId
        return <path key={id} d={entry.d} data-id={id} className={`hm-region hm-c${colour ?? 0}${chosen ? ' is-selected' : ''}`}
          vectorEffect="non-scaling-stroke" role="button" tabIndex={0} aria-pressed={chosen} aria-label={name(entry)}
          onMouseEnter={() => setHovered(name(entry))} onMouseLeave={() => setHovered(null)}
          onFocus={() => setHovered(name(entry))} onBlur={() => setHovered(null)}
          onClick={() => { if (!moved.current) onSelect(id) }}
          onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onSelect(id) } }} />
      })}</g>
      {selected && <path className="hm-selected-outline" d={selected.d} vectorEffect="non-scaling-stroke" aria-hidden="true" />}
      <g className="hm-labels" aria-hidden="true">{paths.map((entry) => {
        const { id, legendNumber } = entry.feature.properties
        const [x, y] = entry.label
        const screen = entry.size / unit
        if (!Number.isFinite(x + y) || (screen < 18 && id !== selectedId)) return null
        const text = legendNumber ?? entry.feature.properties.name
        return <text key={id} x={x} y={y} fontSize={(legendNumber ? 13 : 12) * unit} className={id === selectedId ? 'is-selected' : undefined}
          strokeWidth={3 * unit}>{text}</text>
      })}</g>
    </svg>
    <div className="hm-readout" aria-live="polite">{readout}</div>
    <span className="hm-north" aria-hidden="true">N ↑</span>
  </div>
}

export default HealthAtlasMap
