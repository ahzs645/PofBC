// A printed pin-back button as a three.js model, from a construction recipe (construction.js):
// the face shell turned from buttonProfile.js with the pin's drawing printed on it, a tin back
// recessed behind the rolled edge, and a generic safety pin across the back. Millimetres, face
// towards +z, as BadgeScene expects; its GLB export carries the printed face as a PNG texture.

import * as THREE from 'three'
import { buttonProfile, profileNormals } from './buttonProfile.js'

export const FACE_TEXTURE_SIZE = 2048
const SEGMENTS = 192

/**
 * The drawing rasterised square, for the face: its ground colour first, so the corners and the
 * edge outside the drawn circle are the face's colour too.
 * @returns {Promise<HTMLCanvasElement>}
 */
export async function faceCanvas (svgText, background, size = FACE_TEXTURE_SIZE) {
  const doc = new DOMParser().parseFromString(svgText, 'image/svg+xml')
  const root = doc.documentElement
  if (root.nodeName !== 'svg') throw new Error('The face is not an SVG drawing')
  // Drawn at the canvas's own size, so the browser rasterises the vector there, not a 1000 px copy.
  root.setAttribute('width', String(size))
  root.setAttribute('height', String(size))
  const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(doc)], { type: 'image/svg+xml' }))
  try {
    const image = new Image()
    image.src = url
    await image.decode()
    const canvas = document.createElement('canvas')
    canvas.width = size
    canvas.height = size
    const context = canvas.getContext('2d')
    context.fillStyle = background
    context.fillRect(0, 0, size, size)
    context.drawImage(image, 0, 0, size, size)
    return canvas
  } finally {
    URL.revokeObjectURL(url)
  }
}

/** The printed face's texture, from faceCanvas. */
export function faceTexture (canvas, { anisotropy = 8 } = {}) {
  const map = new THREE.CanvasTexture(canvas)
  map.colorSpace = THREE.SRGBColorSpace
  map.anisotropy = anisotropy
  map.name = 'printed face'
  return map
}

/**
 * A profile turned about the z axis. `uvAt(point, cos, sin)` gives each vertex's texture
 * coordinate; the normals come from the profile, so the seam and the centre stay smooth.
 */
function revolve (points, uvAt) {
  const normals = profileNormals(points)
  const ring = SEGMENTS + 1
  const position = new Float32Array(points.length * ring * 3)
  const normal = new Float32Array(points.length * ring * 3)
  const uv = new Float32Array(points.length * ring * 2)
  points.forEach((point, i) => {
    for (let j = 0; j < ring; j++) {
      const angle = (j / SEGMENTS) * Math.PI * 2
      const cos = Math.cos(angle)
      const sin = Math.sin(angle)
      const k = i * ring + j
      position.set([point.r * cos, point.r * sin, point.z], k * 3)
      normal.set([normals[i].nr * cos, normals[i].nr * sin, normals[i].nz], k * 3)
      uv.set(uvAt ? uvAt(point, cos, sin) : [j / SEGMENTS, i / (points.length - 1)], k * 2)
    }
  })
  const index = []
  for (let i = 0; i < points.length - 1; i++) {
    for (let j = 0; j < SEGMENTS; j++) {
      const a = i * ring + j
      const b = (i + 1) * ring + j
      // Two triangles a quad, wound to face along the profile's normal.
      index.push(a, b, b + 1, a, b + 1, a + 1)
    }
  }
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(position, 3))
  geometry.setAttribute('normal', new THREE.BufferAttribute(normal, 3))
  geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2))
  geometry.setIndex(index)
  return geometry
}

/**
 * The face shell. Its texture is projected straight on from the front: a point's (x, y) is where it
 * is in the drawing, so the lettering is undistorted on a flat face and follows a dome without
 * stretching. The side, the curl and the lip sit just inside the drawn circle's rim, the ground.
 */
function shellGeometry (profile) {
  const { radius } = profile
  const edge = 0.995 * radius
  return revolve(profile.points, (point, cos, sin) => {
    const r = point.printed ? Math.min(point.r, radius) : edge
    return [0.5 + (r * cos) / (2 * radius), 0.5 + (r * sin) / (2 * radius)]
  })
}

/** The tin back, from its rim (turned up, hidden behind the lip) in to the centre. */
function backGeometry ({ plateZ, plateRadius }) {
  const points = [{ r: plateRadius, z: plateZ + 0.9 }]
  for (let i = 1; i <= 6; i++) {
    const angle = (i / 6) * (Math.PI / 2)
    points.push({ r: plateRadius - 0.6 + 0.6 * Math.cos(angle), z: plateZ + 0.9 * (1 - Math.sin(angle)) })
  }
  // A shallow stamped ring, the one feature of a plain back, then flat to the centre.
  const ring = plateRadius * 0.62
  for (let i = 0; i <= 8; i++) {
    const t = i / 8
    points.push({ r: ring + 0.9 - 1.8 * t, z: plateZ - 0.12 * Math.sin(Math.PI * t) })
  }
  points.push({ r: ring * 0.5, z: plateZ }, { r: 0, z: plateZ })
  return revolve(points, null)
}

const helix = ({ x, zAxis, radius, pitch, turns, steps = 28 }) => Array.from({ length: Math.round(turns * steps) + 1 }, (_, i) => {
  const angle = (i / steps) * Math.PI * 2
  return new THREE.Vector3(x - (pitch * angle) / (Math.PI * 2), radius * Math.sin(angle), zAxis + radius * Math.cos(angle))
})

const line = (from, to, step = 0.6) => {
  const count = Math.max(1, Math.ceil(from.distanceTo(to) / step))
  return Array.from({ length: count }, (_, i) => from.clone().lerp(to, (i + 1) / count))
}

/**
 * A generic safety pin across the back: a wire bar lying on the tin, a coil at one end, the arm
 * back across to a hooked catch at the other, with its point just past it.
 */
function safetyPin ({ plateZ, lipRadius }, steel) {
  const wire = 0.45
  const coil = 1.25
  const pitch = 1.05
  const half = 0.72 * lipRadius
  const zBar = plateZ - wire
  const zAxis = zBar - coil
  const zTop = zAxis - coil
  const xCatch = half - 0.3
  const xCoil = -half + 3.7

  const start = new THREE.Vector3(xCatch + 0.6, 0, zBar)
  const coilPoints = helix({ x: xCoil, zAxis, radius: coil, pitch, turns: 3.5 })
  const coilEnd = coilPoints[coilPoints.length - 1]
  // The arm clears the coil's turns, then runs down to rest in the catch.
  const lift = new THREE.Vector3(coilEnd.x + 0.9, 0, zTop - 2 * wire - 0.05)
  const clear = new THREE.Vector3(xCoil + 1.2, 0, zTop - 2 * wire - 0.05)
  const rest = new THREE.Vector3(half + 0.6, 0, zTop + 0.15)
  const path = [start, ...line(start, new THREE.Vector3(xCoil, 0, zBar)).slice(0, -1), ...coilPoints, lift, ...line(lift, clear), ...line(clear, rest)]
  const curve = new THREE.CatmullRomCurve3(path, false, 'centripetal')
  const group = new THREE.Group()
  group.name = 'safety pin'
  const add = (geometry, name) => {
    const mesh = new THREE.Mesh(geometry, steel)
    mesh.name = name
    group.add(mesh)
    return mesh
  }
  add(new THREE.TubeGeometry(curve, path.length * 3, wire, 12, false), 'pin wire')
  add(new THREE.SphereGeometry(wire, 16, 12), 'pin wire end').position.copy(start)
  const point = add(new THREE.ConeGeometry(wire, 1.8, 16), 'pin point')
  const along = rest.clone().sub(clear).normalize()
  point.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), along)
  point.position.copy(rest).addScaledVector(along, 0.9)

  // The catch: a hook rising from the tin round the far side of the arm, open towards the coil.
  const zArm = rest.z - (rest.z - clear.z) * (0.9 / rest.distanceTo(clear))
  const hookRadius = wire + 0.55
  const hook = [new THREE.Vector3(xCatch, -hookRadius, plateZ + 0.2), new THREE.Vector3(xCatch, -hookRadius, zArm - 0.3)]
  for (let i = 0; i <= 14; i++) {
    const angle = Math.PI + (i / 14) * (Math.PI + 0.7)
    hook.push(new THREE.Vector3(xCatch, hookRadius * Math.cos(angle), zArm + hookRadius * Math.sin(angle)))
  }
  add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(hook, false, 'centripetal'), 48, 0.5, 12, false), 'catch')
  add(new THREE.SphereGeometry(0.5, 12, 10), 'catch end').position.copy(hook[hook.length - 1])
  return group
}

/**
 * @param {object} recipe  A pin's construction (construction.js).
 * @param {{ map: THREE.Texture, dome?: number }} options  The printed face, and a dome to use in
 *   place of the recipe's.
 * @returns {{ group: THREE.Group, setDome: (dome: number) => void }}
 */
export function buildPrintedButton (recipe, { map, dome = recipe.dome }) {
  let profile = buttonProfile({ diameterMm: recipe.diameterMm, dome })
  const face = new THREE.MeshStandardMaterial({ name: 'printed face', map, roughness: 0.7, metalness: 0 })
  const tin = new THREE.MeshStandardMaterial({ name: 'tin back', color: '#cfd2d5', metalness: 1, roughness: 0.4 })
  const steel = new THREE.MeshStandardMaterial({ name: 'steel', color: '#c4c8cc', metalness: 1, roughness: 0.35 })

  const group = new THREE.Group()
  group.name = 'printed button'
  const shell = new THREE.Mesh(shellGeometry(profile), face)
  shell.name = 'face shell'
  const back = new THREE.Mesh(backGeometry(profile), tin)
  back.name = 'tin back'
  group.add(shell, back, safetyPin(profile, steel))

  return {
    group,
    /** Reshape the face (the back and the pin stay where they are). */
    setDome (next) {
      profile = buttonProfile({ diameterMm: recipe.diameterMm, dome: next })
      const before = shell.geometry
      shell.geometry = shellGeometry(profile)
      before.dispose()
    }
  }
}
