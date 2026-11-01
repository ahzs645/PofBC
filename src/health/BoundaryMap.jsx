import React, { useEffect, useMemo, useRef, useState } from 'react'
import { forSphericalDrawing, prepareMap, selectionViewBox } from './mapGeometry.js'

const WIDTH = 800
const HEIGHT = 650
const LAYER_LABELS = { lha: 'Local health areas', hsda: 'Health service delivery areas', ha: 'Health authorities', historical: 'Estimated historical statistical regions', estimates: 'Best available historical estimates', drawn: 'Source-drawn historical estimates', municipalities: 'Current municipalities', regionalDistricts: 'Current regional districts', schoolDistricts: 'Current school districts' }

export function BoundaryMap({ collections, layer = 'lha', selectedCodes = new Set(), selectedName, onFeatureSelect, showOverlay = true, contextOnly = false, sourceMapId, sourceAreaId }) {
  const rawCollection = collections[layer]
  const collection = useMemo(() => ['estimates', 'drawn'].includes(layer) && rawCollection
    ? { ...rawCollection, features: rawCollection.features.filter((feature) => feature.properties.mapId === sourceMapId) }
    : rawCollection, [rawCollection, layer, sourceMapId])
  const context = collections.ha ?? collection
  const geometry = useMemo(() => prepareMap(context, WIDTH, HEIGHT), [context])
  const features = useMemo(() => (collection?.features ?? []).map(forSphericalDrawing), [collection])
  const overlays = useMemo(() => (collections.hsda?.features ?? []).map(forSphericalDrawing), [collections.hsda])
  const selected = useMemo(() => features.filter((feature) => selectedCodes.has(String(feature.properties.code))), [features, selectedCodes])
  const [viewBox, setViewBox] = useState([0, 0, WIDTH, HEIGHT])
  const [overlay, setOverlay] = useState(showOverlay)
  const [hovered, setHovered] = useState(null)
  const [opacity, setOpacity] = useState(0.7)
  const [labels, setLabels] = useState(false)
  const [showSource, setShowSource] = useState(true)
  const estimated = ['estimates', 'drawn', 'historical'].includes(layer)
  const sourceLines = layer !== 'historical' && collections.registeredLines?.features.find((feature) => feature.properties.mapId === sourceMapId)
  const sourceArea = useMemo(() => {
    const feature = (collections.drawn ?? collections.registeredAreas)?.features.find((entry) => entry.properties.code === sourceAreaId)
    return feature ? forSphericalDrawing(feature) : null
  }, [collections.drawn, collections.registeredAreas, sourceAreaId])
  const drag = useRef(null)
  const dragged = useRef(false)
  const svg = useRef(null)
  useEffect(() => { setViewBox([0, 0, WIDTH, HEIGHT]); setHovered(null) }, [layer])
  const zoom = (factor) => setViewBox(([x, y, width, height]) => {
    const nextWidth = Math.max(18, Math.min(WIDTH * 1.5, width * factor))
    const nextHeight = nextWidth * HEIGHT / WIDTH
    return [x + (width - nextWidth) / 2, y + (height - nextHeight) / 2, nextWidth, nextHeight]
  })

  if (!features.length) return <p className="health-map-empty">No boundary geometry is available for this layer.</p>
  return (
    <div className="health-boundary-map">
      <div className="health-map-toolbar" aria-label="Map controls">
        <div className="health-map-zoom">
          <button type="button" onClick={() => zoom(0.65)} aria-label="Zoom in">+</button>
          <button type="button" onClick={() => zoom(1.5)} aria-label="Zoom out">−</button>
          <button type="button" onClick={() => setViewBox([0, 0, WIDTH, HEIGHT])}>Province</button>
          <button type="button" disabled={!selected.length} onClick={() => setViewBox(selectionViewBox(geometry.path, selected, WIDTH, HEIGHT))}>Fit selected area</button>
        </div>
        {layer === 'lha' && <label><input type="checkbox" checked={overlay} onChange={(event) => setOverlay(event.target.checked)} /> Delivery-area outlines</label>}
      </div>
      <div className="health-map-canvas">
        <svg ref={svg} viewBox={viewBox.join(' ')} role="group" aria-label={`${LAYER_LABELS[layer]}${estimated ? ', provisional geography' : ' comparison layer'}`} className={viewBox[2] < WIDTH ? 'is-zoomed' : ''}
          onPointerDown={(event) => {
            dragged.current = false
            if (viewBox[2] >= WIDTH || event.button !== 0) return
            drag.current = { x: event.clientX, y: event.clientY, box: [...viewBox] }
          }}
          onPointerMove={(event) => {
            if (!drag.current || !svg.current) return
            const bounds = svg.current.getBoundingClientRect()
            const dx = event.clientX - drag.current.x
            const dy = event.clientY - drag.current.y
            if (Math.abs(dx) + Math.abs(dy) > 5) { dragged.current = true; event.currentTarget.setPointerCapture?.(event.pointerId) }
            const [x, y, width, height] = drag.current.box
            const scale = Math.min(bounds.width / width, bounds.height / height)
            setViewBox([x - dx / scale, y - dy / scale, width, height])
          }}
          onPointerUp={() => { drag.current = null }} onPointerCancel={() => { drag.current = null }}>
          <title>{LAYER_LABELS[layer]}{estimated ? ' — provisional geography' : ' — modern comparison geography'}</title>
          <g className="health-map-context" aria-hidden="true">{geometry.features.map((feature, index) => <path key={index} d={geometry.path(feature)} />)}</g>
          <g>{features.map((feature) => {
            const code = String(feature.properties.code)
            const chosen = selectedCodes.has(code)
            const name = feature.properties.name
            return <path key={code} data-code={code} d={geometry.path(feature)} className={`health-map-region${chosen ? ' is-selected' : ''}`}
              style={chosen ? { fillOpacity: opacity } : undefined} role="button" tabIndex={0}
              aria-label={`${name}, ${LAYER_LABELS[layer]}, code ${code}${chosen ? contextOnly ? ', selected area' : estimated ? ', selected working estimate' : ', candidate for selected historical area' : ''}`}
              aria-pressed={contextOnly ? chosen : undefined} vectorEffect="non-scaling-stroke"
              onMouseEnter={() => setHovered(name)} onMouseLeave={() => setHovered(null)} onFocus={() => setHovered(name)} onBlur={() => setHovered(null)}
              onClick={() => { if (!dragged.current) onFeatureSelect?.(feature, layer) }}
              onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onFeatureSelect?.(feature, layer) } }}>
              <title>{name} · {code}</title>
            </path>
          })}</g>
          {layer === 'lha' && overlay && <g className="health-map-overlays" aria-hidden="true">{overlays.map((feature, index) => <path key={index} d={geometry.path(feature)} vectorEffect="non-scaling-stroke" />)}</g>}
          {sourceLines && showSource && <g className="health-map-source-lines" aria-hidden="true" data-testid="registered-source-overlay">
            <path d={geometry.path(sourceLines)} vectorEffect="non-scaling-stroke" />
            {sourceArea && <path className="health-map-source-selected" d={geometry.path(sourceArea)} vectorEffect="non-scaling-stroke" />}
          </g>}
          {labels && <g className="health-map-labels" aria-hidden="true">{features.filter((feature) => selectedCodes.has(String(feature.properties.code)) || layer === 'ha').map((feature) => {
            const [x, y] = geometry.path.centroid(feature)
            return Number.isFinite(x + y) ? <text key={feature.properties.code} x={x} y={y} fontSize={Math.max(4, 12 * viewBox[2] / WIDTH)}>{feature.properties.name}</text> : null
          })}</g>}
        </svg>
        <div className="health-map-readout" aria-live="polite">{hovered ?? (contextOnly ? selectedName || 'Select an area to see its name' : selected.length ? `${selected.length} ${estimated ? 'working estimate' : 'comparison area'}${selected.length === 1 ? '' : 's'} highlighted` : 'No complete candidate is proposed at this boundary level')}</div>
        <span className="health-map-north" aria-hidden="true">N ↑</span>
      </div>
      <div className="health-map-legend">
        <span><i className="health-legend-swatch" /> {contextOnly ? selectedName || 'Select an area' : `${estimated ? 'Working estimate' : 'Modern comparison'}${selectedName ? ` for ${selectedName}` : ''}`}</span>
        {sourceLines && <label className="health-source-toggle"><input type="checkbox" checked={showSource} onChange={(event) => setShowSource(event.target.checked)} /><i className="health-source-swatch" /> Registered 1997/98 drawing</label>}
        <label>Fill <input type="range" min="0.1" max="1" step="0.1" value={opacity} aria-label="Selected area fill opacity" onChange={(event) => setOpacity(Number(event.target.value))} /></label>
        <label><input type="checkbox" checked={labels} onChange={(event) => setLabels(event.target.checked)} /> Labels</label>
      </div>
    </div>
  )
}

export default BoundaryMap
