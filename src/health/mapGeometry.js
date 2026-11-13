// Longitude/latitude helpers for framing the health map. geo-toolkit (MapLibre) draws the GeoJSON
// itself, so this only measures it: the box around some areas, whether a box is in view, and
// whether an area is too small on screen to pick out.

function extend(box, [x, y]) {
  if (!Number.isFinite(x) || !Number.isFinite(y)) return box
  if (!box) return [[x, y], [x, y]]
  box[0][0] = Math.min(box[0][0], x); box[0][1] = Math.min(box[0][1], y)
  box[1][0] = Math.max(box[1][0], x); box[1][1] = Math.max(box[1][1], y)
  return box
}

function walk(coordinates, box) {
  if (typeof coordinates?.[0] === 'number') return extend(box, coordinates)
  for (const part of coordinates ?? []) box = walk(part, box)
  return box
}

/** [[west, south], [east, north]] around the features' geometry, or null when there is none. */
export function featureBounds(features) {
  let box = null
  for (const feature of features ?? []) box = walk(feature?.geometry?.coordinates, box)
  return box
}

/** A box grown by a share of its size, with a floor so a small area is not framed edge to edge. */
export function padBounds([[west, south], [east, north]], share = .12, floor = .08) {
  const dx = Math.max((east - west) * share, floor)
  const dy = Math.max((north - south) * share, floor)
  return [[west - dx, south - dy], [east + dx, north + dy]]
}

/** Whether `inner` lies wholly inside the map's visible bounds (a MapLibre LngLatBounds). */
export function isInside([[west, south], [east, north]], visible) {
  return west >= visible.getWest() && east <= visible.getEast() && south >= visible.getSouth() && north <= visible.getNorth()
}

/** Whether a box is under `pixels` across on screen at the map's current zoom. */
export function isSmall(box, map, pixels = 40) {
  if (!box || !map) return false
  const [[west, south], [east, north]] = box
  const a = map.project([west, south])
  const b = map.project([east, north])
  return Math.max(Math.abs(b.x - a.x), Math.abs(b.y - a.y)) < pixels
}
