import { geoArea, geoConicConformal, geoPath } from 'd3-geo'

// D3 uses the opposite exterior-ring winding from RFC 7946 GeoJSON. Normalize
// a copy for projection so a BC polygon does not render as the rest of the globe.
export function forSphericalDrawing(feature) {
  const orientPolygon = (coordinates) => geoArea({ type: 'Polygon', coordinates }) > 2 * Math.PI
    ? coordinates.map((ring) => [...ring].reverse()) : coordinates
  const geometry = feature.geometry
  if (!geometry) return feature
  if (geometry.type === 'Polygon') return { ...feature, geometry: { ...geometry, coordinates: orientPolygon(geometry.coordinates) } }
  if (geometry.type === 'MultiPolygon') return { ...feature, geometry: { ...geometry, coordinates: geometry.coordinates.map(orientPolygon) } }
  return feature
}

export function prepareMap(collection, width = 800, height = 650) {
  const features = (collection?.features ?? []).filter((feature) => feature.geometry).map(forSphericalDrawing)
  if (!features.length) return { features: [], path: () => '', width, height }
  const projection = geoConicConformal().parallels([50, 58.5]).rotate([126, 0]).center([0, 54])
    .fitExtent([[24, 24], [width - 24, height - 24]], { type: 'FeatureCollection', features })
  return { features, projection, path: geoPath(projection).digits(2), width, height }
}

export function selectionViewBox(path, features, width = 800, height = 650) {
  if (!features.length) return [0, 0, width, height]
  const [[x0, y0], [x1, y1]] = path.bounds({ type: 'FeatureCollection', features })
  if (![x0, y0, x1, y1].every(Number.isFinite)) return [0, 0, width, height]
  const cx = (x0 + x1) / 2
  const cy = (y0 + y1) / 2
  const paddedWidth = Math.max(45, x1 - x0) * 1.22
  const paddedHeight = Math.max(45, y1 - y0) * 1.22
  const fittedWidth = Math.max(paddedWidth, paddedHeight * width / height)
  const fittedHeight = fittedWidth * height / width
  return [cx - fittedWidth / 2, cy - fittedHeight / 2, fittedWidth, fittedHeight]
}
