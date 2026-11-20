// The cross-section of a printed pin-back button, as a lathe profile: pure numbers, no three.js, so
// it can be tested without a browser. printedButton.js turns it about the button's axis.
//
// Millimetres; the face looks along +z and the back is at z < 0. The profile runs from the centre
// of the face (r = 0) out over the face, a flat disc or a shallow spherical cap per `dome`, round
// the rolled edge (a shoulder, a short side and a curl under), and inward along the back as a lip
// that the tin back sits behind. The proportions below are illustrative: none is measured.

/** Proportions of the diameter, for a button of ordinary make. */
export const PROPORTIONS = {
  shoulder: 0.035, // the radius the face rolls over at its rim
  depth: 0.11, // from the face's rim to the back of the curl
  curl: 0.022, // the radius of the curl under, to the back
  lip: 0.035, // how far the curled edge reaches in over the back
  recess: 0.35 // mm the tin back sits in behind the lip
}

const arc = (centre, radius, from, to, steps) => Array.from({ length: steps + 1 }, (_, i) => {
  const angle = from + (to - from) * (i / steps)
  return { r: centre.r + radius * Math.sin(angle), z: centre.z + radius * Math.cos(angle) }
})

/**
 * @param {{ diameterMm: number, dome?: number, rings?: number }} options
 *   dome: the face's rise at its centre, as a fraction of the diameter (0 is flat).
 * @returns {{ points: Array<{ r: number, z: number, printed: boolean }>, radius: number,
 *   faceRadius: number, rise: number, shoulder: number, backZ: number, lipRadius: number,
 *   plateZ: number, plateRadius: number }}
 *   `printed` marks the points seen from the front, which take the artwork straight on; the rest
 *   (the side, the curl and the lip) take the face's background colour.
 */
export function buttonProfile ({ diameterMm, dome = 0, rings = 40 }) {
  if (!(diameterMm > 0)) throw new RangeError('diameterMm must be positive')
  if (!(dome >= 0 && dome <= 0.15)) throw new RangeError('dome must be between 0 and 0.15')
  const radius = diameterMm / 2
  const shoulder = PROPORTIONS.shoulder * diameterMm
  const curl = PROPORTIONS.curl * diameterMm
  const rise = dome * diameterMm
  const backZ = -PROPORTIONS.depth * diameterMm

  // The face meets the shoulder tangentially: a cap of sphere radius S through (0, rise) and
  // (faceRadius, 0) leaves its rim at angle α from the vertical, and the shoulder turns from α to
  // a vertical side. The shoulder's own width depends on α, so settle faceRadius in a few steps.
  let faceRadius = radius - shoulder
  let alpha = 0
  let sphere = Infinity
  for (let i = 0; i < 8 && rise > 0; i++) {
    sphere = (faceRadius ** 2 + rise ** 2) / (2 * rise)
    alpha = Math.asin(Math.min(1, faceRadius / sphere))
    faceRadius = radius - shoulder * (1 - Math.sin(alpha))
  }
  if (rise > 0) {
    sphere = (faceRadius ** 2 + rise ** 2) / (2 * rise)
    alpha = Math.asin(Math.min(1, faceRadius / sphere))
  }

  const points = []
  for (let i = 0; i <= rings; i++) {
    const r = faceRadius * (i / rings)
    const z = rise > 0 ? rise - sphere + Math.sqrt(sphere ** 2 - r ** 2) : 0
    points.push({ r, z, printed: true })
  }
  // The shoulder, from the face's rim to the vertical.
  const rim = { r: faceRadius, z: 0 }
  const centre = { r: rim.r - shoulder * Math.sin(alpha), z: rim.z - shoulder * Math.cos(alpha) }
  for (const point of arc(centre, shoulder, alpha, Math.PI / 2, 16).slice(1)) points.push({ ...point, printed: true })
  // The side, straight down to the curl.
  const sideTop = points[points.length - 1].z
  const sideBottom = backZ + curl
  for (let i = 1; i <= 3; i++) points.push({ r: radius, z: sideTop + (sideBottom - sideTop) * (i / 3), printed: false })
  // The curl under, to the back, and the lip inward along it.
  for (const point of arc({ r: radius - curl, z: backZ + curl }, curl, Math.PI / 2, Math.PI, 10).slice(1)) points.push({ ...point, printed: false })
  const lipRadius = radius - curl - PROPORTIONS.lip * diameterMm
  for (let i = 1; i <= 3; i++) points.push({ r: radius - curl - (radius - curl - lipRadius) * (i / 3), z: backZ, printed: false })

  return {
    points,
    radius,
    faceRadius,
    rise,
    shoulder,
    backZ,
    lipRadius,
    // The tin back: recessed a little behind the lip, and reaching under it so no gap shows.
    plateZ: backZ + PROPORTIONS.recess,
    plateRadius: lipRadius + 0.5 * (radius - curl - lipRadius)
  }
}

/**
 * Normals in the profile's plane, as (nr, nz): the tangent turned a quarter, so the face's normal
 * points out of the face (+z) and the lip's out of the back (−z).
 */
export function profileNormals (points) {
  return points.map((_, i) => {
    const a = points[Math.max(0, i - 1)]
    const b = points[Math.min(points.length - 1, i + 1)]
    const tr = b.r - a.r
    const tz = b.z - a.z
    const length = Math.hypot(tr, tz) || 1
    return { nr: -tz / length, nz: tr / length }
  })
}

/**
 * Where a profile point lands on an oval button, for the 3D view's ovals: the round lathe body
 * stretched across by `aspect`, but not by plain scaling, which would widen the rolled edge at the
 * oval's ends. Its outer edge is the ellipse with half-axes `radius × aspect` and `radius`; within
 * `band` of that edge (the shoulder, side, curl, lip and the back's rim) a point sits its own
 * distance in from the edge along the edge's normal, so the rim keeps one width all round; deeper
 * in, the face is that inner outline scaled down to the centre, with the two eased into each other
 * over `blend` so the dome meets the rim without a crease. With `aspect` 1 it is the round body.
 *
 * @param {{ radius: number, aspect: number, band?: number, blend?: number }} options
 * @returns {(r: number, t: number) => [number, number]} a profile radius and the ellipse's angle
 *   parameter to (x, y), in millimetres.
 */
export function ovalPlacer ({ radius, aspect, band = 0.2 * radius, blend = 0.3 * radius }) {
  if (!(radius > 0)) throw new RangeError('radius must be positive')
  if (!(aspect >= 1 && aspect <= 2)) throw new RangeError('aspect must be between 1 and 2')
  const a = radius * aspect
  const b = radius
  // An inward offset of the ellipse folds over itself past its tightest radius of curvature, b²/a.
  const reach = Math.min(band + blend, 0.9 * (b * b) / a)
  const easeTo = Math.max(reach - band, 1e-6)
  return (r, t) => {
    const cos = Math.cos(t)
    const sin = Math.sin(t)
    const nx = b * cos
    const ny = a * sin
    const length = Math.hypot(nx, ny)
    const edge = [a * cos, b * sin]
    const normal = [nx / length, ny / length]
    const inset = radius - r
    const offset = (u) => [edge[0] - u * normal[0], edge[1] - u * normal[1]]
    if (inset <= band) return offset(inset)
    const inner = offset(band)
    const scale = r / (radius - band)
    const scaled = [inner[0] * scale, inner[1] * scale]
    if (inset >= band + easeTo) return scaled
    const s = (inset - band) / easeTo
    const w = 1 - s * s * (3 - 2 * s)
    const near = offset(inset)
    return [w * near[0] + (1 - w) * scaled[0], w * near[1] + (1 - w) * scaled[1]]
  }
}
