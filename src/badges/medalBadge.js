// A library badge's drawing, built as a solid metal (or leather) badge with the Medal Forge
// geometry core (./vendor/medal-forge, MIT): every piece of the drawing extruded and bevelled to its
// own relief over a body that is the outline of the whole badge.
//
// Adapted from the curved badge trial's medal-adapter.ts (14 November 2026), which worked on one
// prepared shield. Here any atlas badge goes in as it is joined from the library:
//
//   1. Illustrative shadows (data-intentional-shadow), text, images and scripts are left out.
//   2. Each painted region becomes a piece in absolute coordinates: fills as SVGLoader resolves them
//      (fill rule and transforms applied), and strokes expanded into solid rings with Clipper,
//      because Medal Forge extrudes filled regions only.
//   3. The body is the union of every piece's outline, outer contours only.
//   4. badgeParts.js decides each piece's part, relief and finish from the drawing's own markings
//      and paint.
//
// As in the trial, the engine's artificial per-path z steps are replaced by a small, ordered offset,
// and the winding its y flip reverses is put back so faces point outward.

import * as THREE from 'three'
import { SVGLoader } from 'three/examples/jsm/loaders/SVGLoader.js'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import ClipperLib from 'clipper-lib'
import { buildMedalGroup } from './vendor/medal-forge/model-builder'
import { DEFAULT_SETTINGS } from './vendor/medal-forge/defaults'
import { EMBOSSED_COMPONENT, METALS, NOMINAL_SIZE_MM, PARTS, RAISED, bodyFor, bossFor, metalOf, partFor } from './badgeParts.js'
import { FIELD_TEXTURES, fieldTexture } from './stipple.js'

export const MEDAL_FORGE = {
  repository: 'https://github.com/CatsJuice/medal-forge',
  commit: 'a6da89fc2a9416a0651a6db113e8a2a741e6a2ae',
  license: 'MIT'
}

const SCALE = 10000 // Clipper works in integers
const SVG_NS = 'http://www.w3.org/2000/svg'
const IDENTITY = [1, 0, 0, 1, 0, 0]
/** The engine raises path i by min(i × 0.004, 0.064) mm; this undoes it. */
const ENGINE_LAYER_STEP = 0.004
const ENGINE_LAYER_CAP = 0.064
/** Pieces smaller than this share of the badge, or with outlines this busy (a whole coat of arms in
 *  one path), get no bevel. */
const TINY_SHARE = 0.0015
const BUSY_POINTS = 3000
const points = (piece) => piece.rings.reduce((sum, ring) => sum + ring.length, 0)
/** Pieces later in the drawing sit this much higher in total, so overlaps keep the drawing's order. */
const ORDER_SPREAD = 0.03

const multiply = (a, b) => [
  a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1],
  a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
  a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]
]

function transformMatrix (value) {
  let result = IDENTITY
  for (const part of (value || '').matchAll(/(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)/g)) {
    const v = (part[2].match(/[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?/g) || []).map(Number)
    let m = IDENTITY
    if (part[1] === 'matrix' && v.length === 6) m = v
    if (part[1] === 'translate') m = [1, 0, 0, 1, v[0] || 0, v[1] || 0]
    if (part[1] === 'scale') m = [v[0], 0, 0, v[1] ?? v[0], 0, 0]
    if (part[1] === 'rotate') {
      const angle = ((v[0] || 0) * Math.PI) / 180
      m = [Math.cos(angle), Math.sin(angle), -Math.sin(angle), Math.cos(angle), 0, 0]
      if (v.length === 3) m = multiply(multiply([1, 0, 0, 1, v[1], v[2]], m), [1, 0, 0, 1, -v[1], -v[2]])
    }
    if (part[1] === 'skewX') m = [1, 0, Math.tan((v[0] * Math.PI) / 180), 1, 0, 0]
    if (part[1] === 'skewY') m = [1, Math.tan((v[0] * Math.PI) / 180), 0, 1, 0, 0]
    result = multiply(result, m)
  }
  return result
}

/** How much the element's transforms scale a stroke width (the area-preserving mean). */
function strokeScale (node) {
  const chain = []
  for (let p = node; p && p.getAttribute; p = p.parentElement) chain.unshift(p)
  const m = chain.reduce((acc, e) => multiply(acc, transformMatrix(e.getAttribute('transform'))), IDENTITY)
  return Math.sqrt(Math.abs(m[0] * m[3] - m[1] * m[2]))
}

function inherited (node, name) {
  for (let p = node; p && p.getAttribute; p = p.parentElement) {
    const v = p.getAttribute(name)
    if (v !== null) return v
  }
  return null
}

/** Points per curve segment. Fine heraldry is thousands of short curves; 12 is smooth at badge size. */
const CURVE_DIVISIONS = 12
/**
 * Detail finer than this share of the drawing's longer side is dropped: about 0.065 mm on a 65 mm
 * badge, far below what the model shows. Without it the provincial arms on the ranger badges (one
 * path of some 1,500 subpaths) sample to a quarter of a million points.
 */
const DETAIL_SHARE = 0.001

/** The drawing's simplification tolerance, in its own units, from its viewBox (or size). */
function toleranceFor (root) {
  const box = (root.getAttribute('viewBox') ?? '').trim().split(/[\s,]+/).map(Number)
  const width = box.length === 4 ? box[2] : parseFloat(root.getAttribute('width'))
  const height = box.length === 4 ? box[3] : parseFloat(root.getAttribute('height'))
  const longer = Math.max(width || 0, height || 0)
  return longer > 0 ? longer * DETAIL_SHARE : 0.02
}

/**
 * A ring without points closer than the tolerance to the last one kept, or null if too little of it
 * is left. Spacing only: Clipper's CleanPolygon also drops "near-collinear" points, and repeated
 * along a smooth curve that collapses an O into a triangle.
 */
function simplify (ring, tolerance) {
  const min = tolerance * SCALE
  const kept = [ring[0]]
  for (const p of ring.slice(1)) {
    const last = kept.at(-1)
    if (Math.hypot(p.X - last.X, p.Y - last.Y) >= min) kept.push(p)
  }
  if (kept.length > 3 && Math.hypot(kept[0].X - kept.at(-1).X, kept[0].Y - kept.at(-1).Y) < min) kept.pop()
  if (kept.length < 3) return null
  return Math.abs(ClipperLib.Clipper.Area(kept)) > (2 * min) ** 2 ? kept : null
}

const toClipper = (points) => points.map((p) => ({ X: Math.round(p.x * SCALE), Y: Math.round(p.y * SCALE) }))
const ringD = (ring) => ring.map((v, i) => `${i ? 'L' : 'M'}${+(v.X / SCALE).toFixed(4)} ${+(v.Y / SCALE).toFixed(4)}`).join('') + 'Z'

/** Clipper's boolean operations, with the nonzero rule SVG fills default to. */
function clip (type, subject, clipRings = []) {
  const clipper = new ClipperLib.Clipper()
  clipper.AddPaths(subject, ClipperLib.PolyType.ptSubject, true)
  if (clipRings.length) clipper.AddPaths(clipRings, ClipperLib.PolyType.ptClip, true)
  const out = []
  clipper.Execute(type, out, ClipperLib.PolyFillType.pftNonZero, ClipperLib.PolyFillType.pftNonZero)
  return out
}

/**
 * A filled path's region as non-overlapping rings in absolute coordinates. SVGLoader resolves the
 * fill rule into shapes with holes, but those shapes may overlap one another: the atlas builds a
 * letter such as E from overlapping rectangles. Each shape loses its holes, then all are joined.
 */
function fillRings (path, tolerance) {
  const solids = []
  for (const shape of SVGLoader.createShapes(path)) {
    const { shape: outer, holes } = shape.extractPoints(CURVE_DIVISIONS)
    const ring = simplify(toClipper(outer), tolerance)
    if (!ring) continue
    const hollow = holes.map((hole) => simplify(toClipper(hole), tolerance)).filter(Boolean)
    solids.push(...(hollow.length ? clip(ClipperLib.ClipType.ctDifference, [ring], hollow) : [ring]))
  }
  return solids.length ? clip(ClipperLib.ClipType.ctUnion, solids) : []
}

/** A stroked path's outline, as the rings of the solid band it paints. */
function strokeRings (path, style, tolerance) {
  const delta = (Number(style.strokeWidth) * strokeScale(path.userData.node) * SCALE) / 2
  const offset = new ClipperLib.ClipperOffset(2, Math.max(0.015, tolerance / 2) * SCALE)
  for (const subpath of path.subPaths) {
    let points = subpath.getPoints(CURVE_DIVISIONS)
    if (points.length < 2) continue
    const closed = Boolean(subpath.autoClose) || points[0].distanceTo(points.at(-1)) < 1e-5
    if (closed && points[0].distanceTo(points.at(-1)) < 1e-5) points = points.slice(0, -1)
    const join = style.strokeLineJoin === 'miter' ? ClipperLib.JoinType.jtMiter : style.strokeLineJoin === 'bevel' ? ClipperLib.JoinType.jtSquare : ClipperLib.JoinType.jtRound
    const end = closed
      ? ClipperLib.EndType.etClosedLine
      : style.strokeLineCap === 'round' ? ClipperLib.EndType.etOpenRound : style.strokeLineCap === 'square' ? ClipperLib.EndType.etOpenSquare : ClipperLib.EndType.etOpenButt
    // Thin the line before offsetting it: offsetting is what costs, point by point.
    const thinned = [points[0]]
    for (const point of points.slice(1, -1)) if (point.distanceTo(thinned.at(-1)) >= tolerance) thinned.push(point)
    thinned.push(points.at(-1))
    if (thinned.length < 2) continue
    offset.AddPath(toClipper(thinned), join, end)
  }
  const out = []
  offset.Execute(out, delta)
  // Drop near-collinear slivers far below a displayed pixel; they only make unstable bevels.
  return out.map((ring) => simplify(ring, Math.max(0.02, tolerance))).filter(Boolean)
}

/** The longer side of a set of rings' bounds, in drawing units. */
function longerSide (rings) {
  let minX = Infinity; let minY = Infinity; let maxX = -Infinity; let maxY = -Infinity
  for (const ring of rings) for (const p of ring) { minX = Math.min(minX, p.X); maxX = Math.max(maxX, p.X); minY = Math.min(minY, p.Y); maxY = Math.max(maxY, p.Y) }
  return Math.max(maxX - minX, maxY - minY) / SCALE
}

/**
 * A raised piece's outline inset by its bevel, so the bevel's slope rises from the drawn edge to a
 * narrower top, as a struck letter's shoulder does. A stroke too thin for the full shoulder gets a
 * smaller one: the top must keep at least half the piece's area.
 */
function shoulder (rings, bevelMm, perMm) {
  const before = Math.abs(rings.reduce((sum, ring) => sum + ClipperLib.Clipper.Area(ring), 0))
  for (const share of [1, 0.6, 0.35]) {
    const bevel = bevelMm * share
    const offset = new ClipperLib.ClipperOffset(2, 0.25 * SCALE * perMm * 0.01)
    offset.AddPaths(rings, ClipperLib.JoinType.jtRound, ClipperLib.EndType.etClosedPolygon)
    const inset = []
    offset.Execute(inset, -bevel * perMm * SCALE)
    const after = Math.abs(inset.reduce((sum, ring) => sum + ClipperLib.Clipper.Area(ring), 0))
    if (inset.length && after >= 0.5 * before) return { rings: inset, bevel }
  }
  return { bevel: Math.min(bevelMm, 0.02) }
}

/** The struck emblem (see EMBOSSED_COMPONENT) an element belongs to, or null. */
function emblemOf (node) {
  for (let p = node; p && p.getAttribute; p = p.parentElement) {
    if (EMBOSSED_COMPONENT.test(p.getAttribute('data-component') ?? '')) return p
  }
  return null
}

/** How far the parts of an emblem are joined across, to make one mass of its line work, in mm. */
const EMBLEM_JOIN_MM = 0.5

/**
 * Give each struck emblem the raised mass the photographs show: its outline, with the small gaps
 * between its parts closed (grown, then shrunk, by EMBLEM_JOIN_MM) and everything inside filled,
 * raised as a boss. The emblem's own pieces then stand on the boss, not on the field.
 */
function withBosses (pieces, metal, perMm) {
  const groups = new Map()
  for (const piece of pieces) if (piece.emblem) groups.set(piece.emblem, [...(groups.get(piece.emblem) ?? []), piece])
  if (!groups.size) return pieces
  const out = []
  const done = new Set()
  for (const piece of pieces) {
    const members = piece.emblem ? groups.get(piece.emblem) : null
    if (members && !done.has(piece.emblem)) {
      done.add(piece.emblem)
      const join = EMBLEM_JOIN_MM * perMm * SCALE
      const grow = (rings, delta) => {
        // The boss's outline is soft anyway: a coarse arc tolerance keeps the busy arms quick.
        const offset = new ClipperLib.ClipperOffset(2, 0.05 * perMm * SCALE)
        offset.AddPaths(rings, ClipperLib.JoinType.jtRound, ClipperLib.EndType.etClosedPolygon)
        const result = []
        offset.Execute(result, delta)
        return result
      }
      const merged = clip(ClipperLib.ClipType.ctUnion, members.flatMap((m) => m.rings))
      const solid = grow(grow(merged, join), -join).filter((ring) => ClipperLib.Clipper.Orientation(ring))
      if (solid.length) {
        const boss = { kind: 'fill', paint: null, rings: solid, caption: null, border: false, emblem: null, share: 0, ...bossFor(metal) }
        const shaped = { ...boss, ...shoulder(boss.rings, boss.bevel, perMm) }
        out.push(shaped)
        const top = shaped.thickness + shaped.bevel
        for (const member of members) {
          member.base = top
          // Inside an emblem the drawing's order decides what is on top: its dark outlines are drawn
          // over its light fills, so they must not sink under them as lighter-over-darker would.
          if (RAISED.has(member.part)) member.thickness = PARTS[member.part].thickness
          // An "engraved" emblem is drawn as plates of the metal with its detail cut out of them:
          // those plates are its polished high points, standing over the darker boss.
          if (member.part === 'plate') {
            Object.assign(member, { part: 'emblem', thickness: PARTS.emblem.thickness, color: METALS[metal].plate, metalness: metal === 'leather' ? 0 : 1, roughness: METALS[metal].polish })
          }
        }
      }
    }
    out.push(piece)
  }
  return out
}

const visible = (paint, opacity) => paint && paint !== 'none' && Number(opacity ?? 1) > 0

/**
 * The drawing as pieces, plus the body.
 * @param {string} svgText  A joined library drawing.
 * @param {{ medium?: string }} [options]
 */
export function badgePieces (svgText, { medium = '', sizeMm = NOMINAL_SIZE_MM } = {}) {
  const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml')
  if (doc.querySelector('parsererror')) throw new Error('The badge drawing is not valid SVG.')
  const root = doc.documentElement
  const shadows = root.querySelectorAll('[data-intentional-shadow="true"]').length
  root.querySelectorAll('[data-intentional-shadow="true"], text, image, script, foreignObject, metadata').forEach((e) => e.remove())
  const parsed = new SVGLoader().parse(new XMLSerializer().serializeToString(doc))
  const tolerance = toleranceFor(root)

  const raw = []
  for (const path of parsed.paths) {
    const style = path.userData?.style ?? {}
    const node = path.userData?.node
    if (style.visibility === 'hidden' || style.display === 'none' || Number(style.opacity ?? 1) <= 0) continue
    const context = { caption: inherited(node, 'data-caption'), border: inherited(node, 'data-role') === 'border', emblem: emblemOf(node) }
    if (visible(style.fill, style.fillOpacity)) {
      const rings = fillRings(path, tolerance)
      if (rings.length) raw.push({ kind: 'fill', paint: style.fill, rings, ...context })
    }
    if (visible(style.stroke, style.strokeOpacity) && Number(style.strokeWidth) > 0) {
      const rings = strokeRings(path, style, tolerance)
      if (rings.length) raw.push({ kind: 'stroke', paint: style.stroke, rings, ...context })
    }
  }
  if (!raw.length) throw new Error('The badge drawing has no filled or stroked shapes.')

  const area = (rings) => Math.abs(rings.reduce((sum, ring) => sum + ClipperLib.Clipper.Area(ring), 0)) / SCALE / SCALE
  const metal = metalOf({ medium, paints: raw.map((piece) => ({ paint: piece.paint, area: area(piece.rings) })) })

  // The body: everything's outline together, solid (outer contours only).
  const union = clip(ClipperLib.ClipType.ctUnion, raw.flatMap((piece) => piece.rings))
  const smallest = (0.002 * area(union)) * SCALE * SCALE
  const outline = union.filter((ring) => ClipperLib.Clipper.Orientation(ring) && Math.abs(ClipperLib.Clipper.Area(ring)) > smallest)

  const outlineArea = area(outline)
  const perMm = longerSide(outline) / sizeMm
  const pieces = raw.map((piece) => {
    const share = area(piece.rings) / outlineArea
    const look = partFor({ ...piece, metal, share })
    // Fine heraldry is hundreds of tiny pieces; a bevel on each would multiply the model several
    // times over for nothing visible, so they stand square.
    if (share < TINY_SHARE || points(piece) > BUSY_POINTS) return { ...piece, share, ...look, bevel: 0 }
    if (!RAISED.has(look.part)) return { ...piece, share, ...look }
    return { ...piece, share, ...look, ...shoulder(piece.rings, look.bevel, perMm) }
  })
  return { metal, shadows, perMm, body: { rings: outline, ...bodyFor(metal) }, pieces: withBosses(pieces, metal, perMm) }
}

/** The pieces as one flat SVG of plain paths, body first, in the order the engine will index them. */
function piecesSvg ({ body, pieces }) {
  const all = [body, ...pieces]
  const paths = all.map((piece) =>
    `<path d="${piece.rings.map(ringD).join('')}" fill="${piece.color}"/>`)
  return { all, svg: `<svg xmlns="${SVG_NS}">${paths.join('')}</svg>` }
}

function reverseWinding (geometry) {
  if (geometry.index) {
    const index = geometry.index
    for (let i = 0; i < index.count; i += 3) {
      const b = index.getX(i + 1)
      index.setX(i + 1, index.getX(i + 2))
      index.setX(i + 2, b)
    }
    index.needsUpdate = true
  } else {
    for (const attr of Object.values(geometry.attributes)) {
      const data = attr.array
      for (let i = 0; i < attr.count; i += 3) {
        for (let j = 0; j < attr.itemSize; j++) {
          const a = (i + 1) * attr.itemSize + j
          const b = (i + 2) * attr.itemSize + j
          const t = data[a]
          data[a] = data[b]
          data[b] = t
        }
      }
      attr.needsUpdate = true
    }
  }
  geometry.computeVertexNormals()
}

/** Bounds of Clipper rings, in drawing units. */
function boundsOf (rings) {
  let minX = Infinity; let minY = Infinity; let maxX = -Infinity; let maxY = -Infinity
  for (const ring of rings) for (const p of ring) { minX = Math.min(minX, p.X); maxX = Math.max(maxX, p.X); minY = Math.min(minY, p.Y); maxY = Math.max(maxY, p.Y) }
  return { minX: minX / SCALE, minY: minY / SCALE, maxX: maxX / SCALE, maxY: maxY / SCALE }
}

/**
 * The field's texture (stipple.js) and how the model's coordinates map onto it. The engine places
 * a drawing point (X, Y) at ((X − cx) / perMm, −(Y − cy) / perMm) mm, about the centre of the
 * badge's outline; the texture's frame runs from the field's lower left, y up.
 */
function texturedField ({ body, pieces, perMm }, name) {
  const grounds = pieces.filter((p) => p.part === 'ground')
  if (!grounds.length) return null
  const fieldRings = grounds.flatMap((p) => p.rings)
  const raisedRings = pieces.filter((p) => p.part !== 'ground').flatMap((p) => p.rings)
  const f = boundsOf(fieldRings)
  const o = boundsOf(body.rings)
  const cx = (o.minX + o.maxX) / 2
  const cy = (o.minY + o.maxY) / 2
  const toFrame = (rings) => rings.map((ring) => ring.map((p) => [(p.X / SCALE - f.minX) / perMm, (f.maxY - p.Y / SCALE) / perMm]))
  const widthMm = (f.maxX - f.minX) / perMm
  const heightMm = (f.maxY - f.minY) / perMm
  const map = fieldTexture(name, { width: widthMm, height: heightMm, field: toFrame(fieldRings), raised: toFrame(raisedRings) })
  return { map, widthMm, heightMm, offsetX: (cx - f.minX) / perMm, offsetY: (f.maxY - cy) / perMm }
}

/**
 * Build a badge.
 * @param {string} svgText  A joined library drawing.
 * @param {{ medium?: string, sizeMm?: number, family?: string }} [options]
 *   sizeMm: its longer side (illustrative). family: the library's family, which says whether its
 *   field is textured (stipple.js).
 * A textured field gets its own normal map (stipple.js), made for this badge's field and relief, and
 * UVs spanning the field's box.
 * @returns {{ group: THREE.Group, metal: string, sizeMm: {width: number, height: number, depth: number}, stats: object }}
 */
export function buildBadge (svgText, { medium = '', sizeMm = NOMINAL_SIZE_MM, family = '' } = {}) {
  const fieldTexture = FIELD_TEXTURES[family] ?? null
  const started = performance.now()
  const prepared = badgePieces(svgText, { medium, sizeMm })
  const { all, svg } = piecesSvg(prepared)
  const count = all.length
  const shapeSettings = {}
  all.forEach((piece, index) => {
    const engineOffset = Math.min(index * ENGINE_LAYER_STEP, ENGINE_LAYER_CAP)
    const order = piece.part === 'body' ? 0 : (ORDER_SPREAD * index) / count
    // A bevel adds its own depth on both faces: a piece spans zOffset − bevel to zOffset +
    // thickness + bevel. The body's face is z = 0; every other piece's back bevel is sunk into it.
    shapeSettings[String(index)] = {
      thickness: piece.thickness,
      zOffset: (piece.part === 'body' ? -piece.thickness - piece.bevel : (piece.base ?? 0) + order) - engineOffset,
      bevel: piece.bevel,
      material: 'brushedGold',
      color: piece.color,
      curveSegments: 24,
      bevelSegments: piece.part === 'body' ? 3 : 1,
      depthSteps: 1
    }
  })
  const engine = buildMedalGroup(svg, {
    ...DEFAULT_SETTINGS,
    modelSize: sizeMm,
    dome: { enabled: false, depth: 0, radius: 1, segments: 32 },
    quality: { bevelSegments: 2, curvePrecision: 6, curveSegments: 24 },
    shapeSettings
  })
  if (engine.userData.isEmptyPlaceholder) throw new Error('Medal Forge could not build this badge.')

  // One mesh per part and colour: a few draw calls instead of hundreds.
  engine.updateMatrixWorld(true)
  const byLook = new Map()
  engine.traverse((mesh) => {
    if (!mesh.isMesh) return
    const piece = all[mesh.userData.pathIndex]
    if (!piece) return
    reverseWinding(mesh.geometry)
    const texture = piece.part === 'ground' ? fieldTexture : null
    const key = `${piece.part}|${piece.color}|${piece.metalness}|${piece.roughness}|${texture}`
    if (!byLook.has(key)) byLook.set(key, { piece, texture, geometries: [] })
    const geometry = mesh.geometry.index ? mesh.geometry.toNonIndexed() : mesh.geometry.clone()
    geometry.applyMatrix4(mesh.matrixWorld)
    for (const name of Object.keys(geometry.attributes)) if (name !== 'position' && name !== 'normal') geometry.deleteAttribute(name)
    byLook.get(key).geometries.push(geometry)
  })
  const group = new THREE.Group()
  group.name = 'badge'
  let triangles = 0
  const field = fieldTexture ? texturedField(prepared, fieldTexture) : null
  for (const { piece, texture, geometries } of byLook.values()) {
    const geometry = mergeGeometries(geometries, false)
    geometries.forEach((g) => g.dispose())
    if (!geometry) continue
    if (texture && field) {
      const position = geometry.getAttribute('position')
      const uv = new Float32Array(position.count * 2)
      for (let i = 0; i < position.count; i++) {
        uv[2 * i] = (position.getX(i) + field.offsetX) / field.widthMm
        uv[2 * i + 1] = (position.getY(i) + field.offsetY) / field.heightMm
      }
      geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2))
    }
    const material = new THREE.MeshStandardMaterial({ color: piece.color, metalness: piece.metalness, roughness: piece.roughness })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.name = `${piece.part} ${piece.color}`
    mesh.userData.part = piece.part
    if (texture && field) mesh.userData.fieldMap = field.map
    triangles += geometry.getAttribute('position').count / 3
    group.add(mesh)
  }
  engine.traverse((o) => { if (o.isMesh) { o.geometry.dispose(); o.material.dispose() } })

  // Centre the face on the origin; z = 0 stays the body's face, the plane the curvature bends.
  const box = new THREE.Box3().setFromObject(group)
  const centre = box.getCenter(new THREE.Vector3())
  for (const mesh of group.children) mesh.geometry.translate(-centre.x, -centre.y, 0)
  const size = box.getSize(new THREE.Vector3())
  const parts = {}
  for (const piece of prepared.pieces) parts[piece.part] = (parts[piece.part] ?? 0) + 1
  return {
    group,
    metal: prepared.metal,
    sizeMm: { width: size.x, height: size.y, depth: size.z },
    stats: { pieces: prepared.pieces.length, parts, shadowsLeftOut: prepared.shadows, meshes: group.children.length, triangles, buildMs: Math.round(performance.now() - started) }
  }
}
