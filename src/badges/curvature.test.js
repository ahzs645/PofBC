// The curvature checks from the curved badge trial (tools/test-curvature.ts), ported to node:test.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Vector3 } from 'three'
import { PreparedBadgeCurvature, curveDirection, curvePoint, radiusForRise } from './curvature.js'

const near = (a, b, tolerance = 1e-8) => assert.ok(Math.abs(a - b) <= tolerance, `${a} != ${b}`)

test('the requested rise is the neutral surface’s sag at the unbent half-width', () => {
  for (const rise of [0.001, 1, 4, 8]) {
    const r = radiusForRise(65, rise)
    near(-curvePoint({ x: 32.5, y: 0, z: 0 }, 'cylinder', r).z, rise, 1e-9)
    near(-curvePoint({ x: 32.5, y: 0, z: 0 }, 'dome', r).z, rise, 1e-9)
  }
  near(radiusForRise(65, 4), 131.35911627806416, 1e-6)
})

test('body thickness and relief height are kept along the surface normal', () => {
  for (const mode of ['cylinder', 'dome']) {
    for (const [x, y] of [[0, 0], [16, 9], [31, -28]]) {
      const r = radiusForRise(65, 8)
      const a = curvePoint({ x, y, z: -1.8 }, mode, r)
      const b = curvePoint({ x, y, z: 0 }, mode, r)
      const c = curvePoint({ x, y, z: 0.65 }, mode, r)
      near(Math.hypot(b.x - a.x, b.y - a.y, b.z - a.z), 1.8)
      near(Math.hypot(c.x - b.x, c.y - b.y, c.z - b.z), 0.65)
    }
  }
})

test('analytic normals stay perpendicular to the curved surfaces', () => {
  const eps = 1e-5
  for (const mode of ['cylinder', 'dome']) {
    for (const p of [{ x: 0, y: 0, z: 0 }, { x: 24, y: -16, z: 1.5 }]) {
      const r = radiusForRise(65, 6)
      const n = curveDirection(p, { x: 0, y: 0, z: 1 }, mode, r)
      const centre = curvePoint(p, mode, r)
      for (const d of [{ x: eps, y: 0 }, { x: 0, y: eps }]) {
        const other = curvePoint({ ...p, x: p.x + d.x, y: p.y + d.y }, mode, r)
        near((n.x * (other.x - centre.x) + n.y * (other.y - centre.y) + n.z * (other.z - centre.z)) / eps, 0, 1e-6)
      }
    }
  }
})

test('subdivision keeps materials, UVs, unit normals and nested transforms, and flat is exact', () => {
  const root = new Group()
  const child = new Group()
  root.add(child)
  child.scale.set(1.2, 0.9, 1)
  child.rotation.z = 0.11
  child.position.set(3, -2, 0)
  const box = new Mesh(new BoxGeometry(50, 60, 1.8), [0, 1, 2, 3, 4, 5].map(() => new MeshStandardMaterial()))
  child.add(box)
  const prepared = new PreparedBadgeCurvature(root, { maxEdgeLength: 2 })
  const before = new Float32Array(box.geometry.getAttribute('position').array)
  const uv = new Float32Array(box.geometry.getAttribute('uv').array)
  const groups = JSON.stringify(box.geometry.groups)
  assert.equal(new Set(box.geometry.groups.map((g) => g.materialIndex)).size, 6)
  prepared.apply({ mode: 'dome', rise: 4 })
  const normals = box.geometry.getAttribute('normal')
  for (let i = 0; i < normals.count; i++) near(new Vector3().fromBufferAttribute(normals, i).length(), 1, 1e-6)
  assert.equal(JSON.stringify(box.geometry.groups), groups)
  assert.deepEqual(new Float32Array(box.geometry.getAttribute('uv').array), uv)
  prepared.apply({ mode: 'cylinder', rise: 8 })
  prepared.apply({ mode: 'flat', rise: 0 })
  assert.deepEqual(new Float32Array(box.geometry.getAttribute('position').array), before)
  prepared.apply({ mode: 'dome', rise: 4 })
  const firstBent = new Float32Array(box.geometry.getAttribute('position').array)
  prepared.apply({ mode: 'dome', rise: 4 })
  assert.deepEqual(new Float32Array(box.geometry.getAttribute('position').array), firstBent)
})

test('an impossible bend or an exhausted budget leaves the geometry untouched', () => {
  const root = new Group()
  const mesh = new Mesh(new BoxGeometry(50, 60, 2))
  root.add(mesh)
  const original = mesh.geometry
  assert.throws(() => new PreparedBadgeCurvature(root, { maxEdgeLength: 0.01, maxVertices: 30 }))
  assert.equal(mesh.geometry, original)
  const prepared = new PreparedBadgeCurvature(root, { maxEdgeLength: 4 })
  const positions = new Float32Array(mesh.geometry.getAttribute('position').array)
  assert.throws(() => prepared.apply({ mode: 'dome', rise: 20 }))
  assert.deepEqual(new Float32Array(mesh.geometry.getAttribute('position').array), positions)
  assert.ok(prepared.maxRise('cylinder') < 2 * 25 / Math.PI)
  prepared.dispose()
  assert.equal(mesh.geometry, original)
})
