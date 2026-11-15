// Bend a whole badge model: body, reverse, sidewalls and every relief layer, by one mapping.
//
// Ported from the PofBC curved badge trial (14 November 2026, src/curvature.ts) without changing
// its mathematics. Geometry is in the badge's own units (millimetres here).
//
// For a cylinder, flat horizontal position is treated as arc length; the radius is solved from the
// requested centre-to-edge rise and the unbent span. Depth becomes a radial offset, so thickness and
// relief keep their size along the curved surface's normal. Normals use the inverse-transpose of
// the deformation's Jacobian and tangents the Jacobian itself, so lighting follows the new surface.
// The dome is the radial counterpart. Long triangles are subdivided first, or their interiors would
// stay straight chords while their corners bend. Going back to flat restores the prepared flat
// coordinates exactly; bends never accumulate.

import { Box3, BufferAttribute, BufferGeometry, Matrix3, Vector3 } from 'three'

/** @typedef {'flat' | 'cylinder' | 'dome'} CurvatureMode */
/**
 * @typedef {object} BendOptions
 * @property {CurvatureMode} mode
 * @property {number} rise       Neutral-surface centre-to-edge rise, measured at half the span.
 * @property {number} [span]     The unbent horizontal arc width. Defaults to the prepared model's width.
 * @property {number} [centerX]
 * @property {number} [centerY]
 * @property {number} [neutralZ] The plane that is bent; thickness and relief are offset along its normal.
 */

export const CURVATURE_MODES = ['flat', 'cylinder', 'dome']

/** Solve R(1 − cos(a/R)) = rise for a = span/2, with arc rather than chord width. */
export function radiusForRise (span, rise) {
  if (!(span > 0) || !Number.isFinite(span)) throw new RangeError('span must be finite and positive')
  if (!(rise >= 0) || !Number.isFinite(rise)) throw new RangeError('rise must be finite and nonnegative')
  if (rise === 0) return Infinity
  const a = span / 2
  if (rise >= (2 * a) / Math.PI) throw new RangeError('rise would bend the reference edge through 90 degrees')
  let low = 0
  let high = Math.PI / 2
  const ratio = rise / a
  for (let i = 0; i < 60; i++) {
    const theta = (low + high) / 2
    // 2sin²(θ/2) avoids cancellation at very small curvature.
    const predicted = (2 * Math.sin(theta / 2) ** 2) / theta
    if (predicted < ratio) low = theta
    else high = theta
  }
  return a / ((low + high) / 2)
}

/** The analytic neutral-surface mapping; z is a signed physical offset along the normal. */
export function curvePoint (p, mode, radius) {
  if (mode === 'flat' || !Number.isFinite(radius)) return { ...p }
  if (mode === 'cylinder') {
    const t = p.x / radius
    return {
      x: (radius + p.z) * Math.sin(t),
      y: p.y,
      z: p.z * Math.cos(t) - 2 * radius * Math.sin(t / 2) ** 2
    }
  }
  const rho = Math.hypot(p.x, p.y)
  if (rho < 1e-12) return { x: 0, y: 0, z: p.z }
  const t = rho / radius
  const factor = ((radius + p.z) * Math.sin(t)) / rho
  return {
    x: p.x * factor,
    y: p.y * factor,
    z: p.z * Math.cos(t) - 2 * radius * Math.sin(t / 2) ** 2
  }
}

/** The inverse-transpose Jacobian for normals; the direct Jacobian for tangent vectors. */
export function curveDirection (p, v, mode, radius, normal = true) {
  if (mode === 'flat' || !Number.isFinite(radius)) return { ...v }
  const a = 1 + p.z / radius
  if (!(a > 0)) throw new RangeError('normal offset crosses the curvature center')
  if (mode === 'cylinder') {
    const t = p.x / radius
    const c = Math.cos(t)
    const s = Math.sin(t)
    const vx = normal ? v.x / a : v.x * a
    return { x: vx * c + v.z * s, y: v.y, z: -vx * s + v.z * c }
  }
  const rho = Math.hypot(p.x, p.y)
  if (rho < 1e-12) return { x: normal ? v.x / a : v.x * a, y: normal ? v.y / a : v.y * a, z: v.z }
  const ex = p.x / rho
  const ey = p.y / rho
  const t = rho / radius
  const c = Math.cos(t)
  const s = Math.sin(t)
  const b = (a * s) / t
  const vr = (v.x * ex + v.y * ey) * (normal ? 1 / a : a)
  const vt = (-v.x * ey + v.y * ex) * (normal ? 1 / b : b)
  return {
    x: vr * c * ex - vt * ey + v.z * s * ex,
    y: vr * c * ey + vt * ex + v.z * s * ey,
    z: -vr * s + v.z * c
  }
}

/** Split only long XY edges. Every original material group and UV seam survives. */
function subdivide (sourceGeometry, toRoot, maxEdge, budget) {
  const source = sourceGeometry.index ? sourceGeometry.toNonIndexed() : sourceGeometry.clone()
  if (!source.getAttribute('normal')) source.computeVertexNormals()
  const names = Object.keys(source.attributes)
  if (names.some((n) => /^(skinIndex|skinWeight)$/.test(n))) throw new Error('Skinned badge meshes are unsupported')
  const specs = names.map((name) => ({ name, attribute: source.getAttribute(name), offset: 0, out: [] }))
  let stride = 0
  for (const s of specs) {
    s.offset = stride
    stride += s.attribute.itemSize
    if (s.attribute.itemSize > 4) throw new Error(`Unsupported attribute size for ${s.name}`)
  }
  const po = specs.find((s) => s.name === 'position').offset
  const tmp = new Vector3()
  const read = (i) => {
    const v = new Array(stride + 2)
    for (const s of specs) {
      const attr = s.attribute
      const vals = [attr.getX(i), attr.getY(i), attr.getZ(i), attr.getW(i)]
      for (let c = 0; c < attr.itemSize; c++) v[s.offset + c] = vals[c]
    }
    tmp.set(v[po], v[po + 1], v[po + 2]).applyMatrix4(toRoot)
    v[stride] = tmp.x
    v[stride + 1] = tmp.y
    return v
  }
  let count = 0
  const groups = []
  let materialIndex = 0
  const push = (a, b, c) => {
    if (count + 3 > budget) throw new RangeError(`Curvature subdivision exceeded the ${budget}-vertex remaining budget`)
    for (const v of [a, b, c]) {
      for (const s of specs) for (let k = 0; k < s.attribute.itemSize; k++) s.out.push(v[s.offset + k])
    }
    const last = groups.at(-1)
    if (last && last.materialIndex === materialIndex) last.count += 3
    else groups.push({ start: count, count: 3, materialIndex })
    count += 3
  }
  const distance2 = (a, b) => (a[stride] - b[stride]) ** 2 + (a[stride + 1] - b[stride + 1]) ** 2
  const midpoint = (a, b) => a.map((x, i) => (x + b[i]) / 2)
  const limit2 = maxEdge * maxEdge
  const split = (a, b, c, depth) => {
    const ab = distance2(a, b)
    const bc = distance2(b, c)
    const ca = distance2(c, a)
    if (Math.max(ab, bc, ca) <= limit2) return push(a, b, c)
    if (depth >= 24) throw new Error('Curvature subdivision depth limit reached')
    if (ab >= bc && ab >= ca) {
      const m = midpoint(a, b)
      split(a, m, c, depth + 1); split(m, b, c, depth + 1)
    } else if (bc >= ca) {
      const m = midpoint(b, c)
      split(a, b, m, depth + 1); split(a, m, c, depth + 1)
    } else {
      const m = midpoint(c, a)
      split(a, b, m, depth + 1); split(m, b, c, depth + 1)
    }
  }
  let groupIndex = 0
  for (let i = 0; i < source.getAttribute('position').count; i += 3) {
    while (groupIndex < source.groups.length && i >= source.groups[groupIndex].start + source.groups[groupIndex].count) groupIndex++
    const sg = source.groups[groupIndex]
    materialIndex = sg && i >= sg.start ? sg.materialIndex ?? 0 : 0
    split(read(i), read(i + 1), read(i + 2), 0)
  }
  const output = new BufferGeometry()
  output.name = sourceGeometry.name
  for (const s of specs) output.setAttribute(s.name, new BufferAttribute(new Float32Array(s.out), s.attribute.itemSize))
  // Normalize interpolated normals but do not merge sharp edges or UV seams.
  output.normalizeNormals()
  for (const g of groups) output.addGroup(g.start, g.count, g.materialIndex)
  output.userData = { ...sourceGeometry.userData }
  source.dispose()
  return output
}

/** A model made ready to bend: subdivided once, its flat coordinates kept for every later bend. */
export class PreparedBadgeCurvature {
  /**
   * @param {import('three').Object3D} root
   * @param {{ maxEdgeLength?: number, maxVertices?: number }} [options]
   *   maxEdgeLength: the longest triangle edge allowed in the unbent XY plane.
   *   maxVertices: a safety ceiling; preparation stops without changing the model.
   */
  constructor (root, options = {}) {
    this.root = root
    this.states = []
    this.flatBounds = new Box3()
    const maxEdge = options.maxEdgeLength ?? 1.8
    const maxVertices = options.maxVertices ?? 1_200_000
    if (!(maxEdge > 0) || !Number.isFinite(maxEdge)) throw new RangeError('maxEdgeLength must be positive')
    root.updateWorldMatrix(true, true)
    const rootInverse = root.matrixWorld.clone().invert()
    let count = 0
    const point = new Vector3()
    try {
      root.traverse((mesh) => {
        if (!mesh.isMesh || !mesh.geometry?.getAttribute('position')) return
        const toRoot = rootInverse.clone().multiply(mesh.matrixWorld)
        const normalToRoot = new Matrix3().getNormalMatrix(toRoot)
        const vectorToRoot = new Matrix3().setFromMatrix4(toRoot)
        const toLocal = toRoot.clone().invert()
        const geometry = subdivide(mesh.geometry, toRoot, maxEdge, maxVertices - count)
        const position = geometry.getAttribute('position')
        const normal = geometry.getAttribute('normal')
        const tangent = geometry.getAttribute('tangent')
        const rootPositions = new Float64Array(position.count * 3)
        const rootNormals = new Float64Array(position.count * 3)
        const rootTangents = tangent ? new Float64Array(position.count * 3) : undefined
        for (let i = 0; i < position.count; i++) {
          point.fromBufferAttribute(position, i).applyMatrix4(toRoot)
          this.flatBounds.expandByPoint(point)
          point.toArray(rootPositions, i * 3)
          point.fromBufferAttribute(normal, i).applyNormalMatrix(normalToRoot).toArray(rootNormals, i * 3)
          if (tangent) point.fromBufferAttribute(tangent, i).applyMatrix3(vectorToRoot).normalize().toArray(rootTangents, i * 3)
        }
        this.states.push({
          mesh,
          originalGeometry: mesh.geometry,
          geometry,
          flatLocalPositions: new Float32Array(position.array),
          flatLocalNormals: new Float32Array(normal.array),
          flatLocalTangents: tangent ? new Float32Array(tangent.array) : undefined,
          rootPositions,
          rootNormals,
          rootTangents,
          toLocal,
          normalToLocal: new Matrix3().getNormalMatrix(toLocal),
          vectorToLocal: new Matrix3().setFromMatrix4(toLocal)
        })
        count += position.count
      })
    } catch (error) {
      this.states.forEach((s) => s.geometry.dispose())
      throw error
    }
    if (!this.states.length) throw new Error('No badge mesh geometry found')
    this.vertices = count
    this.defaultSpan = this.flatBounds.max.x - this.flatBounds.min.x
    this.defaultCenter = this.flatBounds.getCenter(new Vector3())
    for (const state of this.states) state.mesh.geometry = state.geometry
  }

  /**
   * A safe rise for this model's default span/centre and neutralZ = 0. Rise is always measured at
   * the unbent half-width, including for a dome. Its radius must also keep the farthest corner
   * below a 90° turn and the back of the badge outside the curvature centre.
   */
  maxRise (mode) {
    if (!CURVATURE_MODES.includes(mode)) throw new Error('Unknown curvature mode')
    if (mode === 'flat') return 0
    const w = this.flatBounds.max.x - this.flatBounds.min.x
    const h = this.flatBounds.max.y - this.flatBounds.min.y
    const halfWidth = w / 2
    if (!(halfWidth > 0)) return 0
    // The dome's reach is the half-diagonal; the cylinder's the half-width.
    const reach = mode === 'dome' ? Math.hypot(w, h) / 2 : w / 2
    const minRadius = Math.max((2 * reach) / Math.PI, -this.flatBounds.min.z)
    // Convert the limiting radius back to the same half-width rise radiusForRise() accepts.
    // Using the diagonal itself as a rise overstates the limit on narrow, tall badges.
    const limit = 2 * minRadius * Math.sin(halfWidth / (2 * minRadius)) ** 2
    return limit * 0.95
  }

  /** @param {BendOptions} options */
  apply (options) {
    if (!CURVATURE_MODES.includes(options.mode)) throw new Error('Unknown curvature mode')
    const mode = options.rise === 0 ? 'flat' : options.mode
    const span = options.span ?? this.defaultSpan
    const radius = mode === 'flat' ? Infinity : radiusForRise(span, options.rise)
    const cx = options.centerX ?? this.defaultCenter.x
    const cy = options.centerY ?? this.defaultCenter.y
    const neutralZ = options.neutralZ ?? 0
    // Check the whole domain before changing any vertex.
    if (mode !== 'flat') {
      for (const state of this.states) {
        const p = state.rootPositions
        for (let i = 0; i < p.length; i += 3) {
          const distance = mode === 'cylinder' ? Math.abs(p[i] - cx) : Math.hypot(p[i] - cx, p[i + 1] - cy)
          if (distance / radius >= Math.PI / 2) throw new RangeError('Curvature would turn a badge extremity through 90 degrees')
          if (p[i + 2] - neutralZ <= -radius) throw new RangeError('Badge thickness crosses the curvature center')
        }
      }
    }
    const point = new Vector3()
    const direction = new Vector3()
    for (const state of this.states) {
      const pos = state.geometry.getAttribute('position')
      const norm = state.geometry.getAttribute('normal')
      const tangent = state.geometry.getAttribute('tangent')
      if (mode === 'flat') {
        pos.array.set(state.flatLocalPositions)
        norm.array.set(state.flatLocalNormals)
        if (tangent) tangent.array.set(state.flatLocalTangents)
      } else {
        for (let i = 0; i < pos.count; i++) {
          const k = i * 3
          const p = { x: state.rootPositions[k] - cx, y: state.rootPositions[k + 1] - cy, z: state.rootPositions[k + 2] - neutralZ }
          const curved = curvePoint(p, mode, radius)
          point.set(curved.x + cx, curved.y + cy, curved.z + neutralZ).applyMatrix4(state.toLocal)
          pos.setXYZ(i, point.x, point.y, point.z)
          const n = curveDirection(p, { x: state.rootNormals[k], y: state.rootNormals[k + 1], z: state.rootNormals[k + 2] }, mode, radius)
          direction.set(n.x, n.y, n.z).applyNormalMatrix(state.normalToLocal)
          norm.setXYZ(i, direction.x, direction.y, direction.z)
          if (tangent && state.rootTangents) {
            const t = curveDirection(p, { x: state.rootTangents[k], y: state.rootTangents[k + 1], z: state.rootTangents[k + 2] }, mode, radius, false)
            direction.set(t.x, t.y, t.z).applyMatrix3(state.vectorToLocal).normalize()
            tangent.setXYZ(i, direction.x, direction.y, direction.z)
          }
        }
      }
      pos.needsUpdate = true
      norm.needsUpdate = true
      if (tangent) tangent.needsUpdate = true
      state.geometry.computeBoundingBox()
      state.geometry.computeBoundingSphere()
    }
    return {
      mode,
      rise: mode === 'flat' ? 0 : options.rise,
      radius: Number.isFinite(radius) ? radius : null,
      span,
      vertices: this.vertices,
      triangles: this.vertices / 3,
      meshes: this.states.length
    }
  }

  /** Restore the untouched original geometry and free the prepared copies. */
  dispose () {
    for (const state of this.states) {
      state.mesh.geometry = state.originalGeometry
      state.geometry.dispose()
    }
  }
}
