import { useEffect, useMemo, useRef, useState } from 'react'
import { forSphericalDrawing, prepareMap } from './mapGeometry.js'

function fit(path, features) {
  const [[x0, y0], [x1, y1]] = path.bounds({ type: 'FeatureCollection', features })
  const width = Math.max(2, x1 - x0, (y1 - y0) * 800 / 650) * 1.22
  const height = width * 650 / 800
  return [(x0 + x1 - width) / 2, (y0 + y1 - height) / 2, width, height]
}
const places = [
  { name: 'Vancouver', point: [-123.12, 49.28] },
  { name: 'Richmond', point: [-123.13, 49.165] },
  { name: 'Bowen Island', point: [-123.3713, 49.37304] },
]

export function AlignmentMap({ collections, referenceLayer, referenceCodes, areaId, review }) {
  const map = useMemo(() => prepareMap(collections.ha), [collections.ha])
  const original = useMemo(() => forSphericalDrawing(collections.drawn.features.find((feature) => feature.properties.code === areaId)), [collections.drawn, areaId])
  const adjusted = useMemo(() => forSphericalDrawing(collections.adjusted.features.find((feature) => feature.properties.code === areaId)), [collections.adjusted, areaId])
  const references = useMemo(() => collections[referenceLayer].features.map(forSphericalDrawing), [collections, referenceLayer])
  const selected = useMemo(() => references.filter((feature) => referenceCodes.has(String(feature.properties.code))), [references, referenceCodes])
  const [viewBox, setViewBox] = useState(() => fit(map.path, [original, adjusted, ...selected]))
  const [referenceVisible, setReferenceVisible] = useState(true)
  const [originalVisible, setOriginalVisible] = useState(false)
  const [adjustedVisible, setAdjustedVisible] = useState(true)
  const [labels, setLabels] = useState(true)
  const [opacity, setOpacity] = useState(.3)
  const svg = useRef(null)
  const drag = useRef(null)
  const [viewport, setViewport] = useState({ width: 800, height: 650 })
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      if (width && height) setViewport({ width, height })
    })
    observer.observe(svg.current)
    return () => observer.disconnect()
  }, [])
  const labelSize = 11 / Math.min(viewport.width / viewBox[2], viewport.height / viewBox[3])
  const northKm = review.workingAlignment.northShiftMetres / 1000
  const visible = [...(originalVisible ? [original] : []), ...(adjustedVisible ? [adjusted] : []), ...(referenceVisible ? selected : [])]
  const zoom = (factor) => setViewBox(([x, y, width, height]) => {
    const next = Math.max(1, Math.min(1000, width * factor))
    return [x + (width - next) / 2, y + (height - next * 650 / 800) / 2, next, next * 650 / 800]
  })
  return <div className="health-boundary-map health-alignment-map">
    <div className="health-map-toolbar" aria-label="Alignment map controls"><div className="health-map-zoom">
      <button type="button" aria-label="Zoom in" onClick={() => zoom(.7)}>+</button>
      <button type="button" aria-label="Zoom out" onClick={() => zoom(1.4)}>−</button>
      <button type="button" disabled={!visible.length} onClick={() => setViewBox(fit(map.path, visible))}>Fit visible layers</button>
      <button type="button" onClick={() => setViewBox(fit(map.path, [original, adjusted, ...selected]))}>Reset alignment view</button>
    </div></div>
    <div className="health-map-canvas"><svg ref={svg} role="img" aria-label={`Vancouver/Richmond reference map and provisional trace, ${northKm} km north`} viewBox={viewBox.join(' ')}
      onPointerDown={(event) => {
        if (event.button !== 0) return
        drag.current = { x: event.clientX, y: event.clientY, box: [...viewBox] }
        event.currentTarget.setPointerCapture?.(event.pointerId)
      }} onPointerMove={(event) => {
        if (!drag.current || !svg.current) return
        const bounds = svg.current.getBoundingClientRect()
        const [x, y, width, height] = drag.current.box
        const scale = Math.min(bounds.width / width, bounds.height / height)
        setViewBox([x - (event.clientX - drag.current.x) / scale, y - (event.clientY - drag.current.y) / scale, width, height])
      }} onPointerUp={() => { drag.current = null }} onPointerCancel={() => { drag.current = null }}>
      <title>Current reference geography, original trace and adjusted historical trace</title>
      <g className="health-map-context" aria-hidden="true">{map.features.map((feature) => <path key={feature.properties.code} d={map.path(feature)} vectorEffect="non-scaling-stroke" />)}</g>
      {referenceVisible && <g data-testid="alignment-reference" className="health-alignment-reference">{references.map((feature) => <path key={feature.properties.code} d={map.path(feature)} className={referenceCodes.has(String(feature.properties.code)) ? 'is-candidate' : ''} style={{ fillOpacity: referenceCodes.has(String(feature.properties.code)) ? opacity : 0 }} vectorEffect="non-scaling-stroke"><title>{feature.properties.name}</title></path>)}</g>}
      {originalVisible && <path data-testid="alignment-original" className="health-alignment-original" d={map.path(original)} vectorEffect="non-scaling-stroke" />}
      {adjustedVisible && <path data-testid="alignment-adjusted" className="health-alignment-adjusted" d={map.path(adjusted)} style={{ fillOpacity: opacity }} vectorEffect="non-scaling-stroke" />}
      {labels && <g className="health-alignment-labels" aria-hidden="true">{places.map((place) => {
        const [x, y] = map.projection(place.point)
        const halfLabel = labelSize * place.name.length * .32
        if (x - halfLabel < viewBox[0] || x + halfLabel > viewBox[0] + viewBox[2] || y - labelSize < viewBox[1] || y > viewBox[1] + viewBox[3]) return null
        return <text key={place.name} x={x} y={y} fontSize={labelSize}>{place.name}</text>
      })}</g>}
    </svg><span className="health-map-north" aria-hidden="true">N ↑</span><div className="health-map-readout">Provisional local alignment · {northKm} km north</div></div>
    <div className="health-map-legend health-alignment-controls">
      <label><input type="checkbox" checked={referenceVisible} onChange={(event) => setReferenceVisible(event.target.checked)} /><i className="health-alignment-swatch is-reference" /> Current reference boundaries</label>
      <label><input type="checkbox" checked={originalVisible} onChange={(event) => setOriginalVisible(event.target.checked)} /><i className="health-alignment-swatch is-original" /> Original trace</label>
      <label><input type="checkbox" checked={adjustedVisible} onChange={(event) => setAdjustedVisible(event.target.checked)} /><i className="health-alignment-swatch is-adjusted" /> Adjusted trace (+{northKm} km north)</label>
      <label>Overlay opacity <input aria-label="Alignment overlay opacity" type="range" min=".1" max=".8" step=".1" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} /></label>
      <label><input type="checkbox" checked={labels} onChange={(event) => setLabels(event.target.checked)} /> Place labels</label>
    </div>
  </div>
}
