// Exercise the real SVG → relief → curvature → GLB path without a WebGL context.
// The DOM and FileReader below provide browser parsing/byte plumbing only; all geometry and the
// export method are the same modules used by BadgeViewer. This is not browser acceptance.
//
// npm install --prefix /tmp/badge-model-tools --ignore-scripts --no-package-lock jsdom@29.1.1 esbuild@0.27.0 @napi-rs/canvas@0.1.100
// BADGE_MODEL_TEST_MODULES=/tmp/badge-model-tools/node_modules node scripts/check-badge-models.mjs
// Add --output /absolute/directory to retain a report and S01-O01 GLBs (flat, curve, dome).
// --baseline <commit> captures the earlier model for comparison, without requiring the new profile.
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const appRequire = createRequire(join(root, 'package.json'))
const toolsRequire = createRequire(join(resolve(process.env.BADGE_MODEL_TEST_MODULES || join(root, 'node_modules')), '_badge-model-tools.cjs'))
const { build } = await import(pathToFileURL(toolsRequire.resolve('esbuild')).href)
const { JSDOM } = await import(pathToFileURL(toolsRequire.resolve('jsdom')).href)
const args = process.argv.slice(2)
const valueAfter = (flag) => {
  if (!args.includes(flag)) return null
  const value = args[args.indexOf(flag) + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}
const baseline = valueAfter('--baseline')
if (baseline && !/^[\da-f]{7,40}$/i.test(baseline)) throw new Error('--baseline must be a commit SHA')
const outputArg = valueAfter('--output')
const output = outputArg ? resolve(outputArg) : null
if (output) mkdirSync(output, { recursive: true })
const temporary = mkdtempSync(join(tmpdir(), 'pofbc-badge-model-'))
process.on('exit', () => rmSync(temporary, { recursive: true, force: true }))

const before = new Map()
if (baseline) {
  for (const file of ['src/badges/medalBadge.js', 'src/badges/badgeParts.js', 'src/badges/curvature.js', 'src/badges/badgeScene.js']) {
    before.set(join(root, file), execFileSync('git', ['show', `${baseline}:${file}`], { cwd: root, encoding: 'utf8' }))
  }
}
const bundle = join(temporary, 'badge-model.mjs')
await build({
  stdin: {
    contents: `export { badgePieces, buildBadge, MEDAL_FORGE } from './src/badges/medalBadge.js'; export { PreparedBadgeCurvature } from './src/badges/curvature.js'; export { BadgeScene } from './src/badges/badgeScene.js'; export * as THREE from 'three';`,
    resolveDir: root,
    sourcefile: 'badge-model-check-entry.js',
  },
  outfile: bundle,
  bundle: true,
  platform: 'node',
  format: 'esm',
  plugins: [
    { name: 'app-three', setup (builder) {
      builder.onResolve({ filter: /^three(?:\/.*)?$/ }, ({ path }) => ({
        path: path === 'three' ? appRequire.resolve('three').replace(/three\.cjs$/, 'three.module.js') : appRequire.resolve(path),
        external: true,
      }))
    } },
    { name: 'baseline-source', setup (builder) {
      builder.onLoad({ filter: /src\/badges\/(?:medalBadge|badgeParts|curvature|badgeScene)\.js$/ }, ({ path }) => before.has(path) ? { contents: before.get(path), loader: 'js' } : undefined)
    } },
  ],
  logLevel: 'warning',
})

const dom = new JSDOM('<!doctype html><html><body></body></html>')
for (const name of ['DOMParser', 'XMLSerializer', 'document', 'ImageData']) {
  if (dom.window[name]) Object.defineProperty(globalThis, name, { configurable: true, value: dom.window[name] })
}
// Real PNG encoding for generated normal maps during GLB export, without a WebGL context.
let canvasTools
try { canvasTools = toolsRequire('@napi-rs/canvas') } catch (error) {
  if (!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES) throw error
  const runtimeRequire = createRequire(join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, '_badge-canvas.cjs'))
  canvasTools = runtimeRequire('@napi-rs/canvas')
}
Object.defineProperty(globalThis, 'ImageData', { configurable: true, value: canvasTools.ImageData })
const createElement = document.createElement.bind(document)
document.createElement = (name, options) => {
  if (String(name).toLowerCase() !== 'canvas') return createElement(name, options)
  const canvas = canvasTools.createCanvas(1, 1)
  canvas.toBlob = (done, mimeType = 'image/png') => done(new Blob([canvas.toBuffer(mimeType)], { type: mimeType }))
  return canvas
}
// GLTFExporter reads real Node Blob bytes through this browser-compatible asynchronous interface.
class BlobReader {
  readAsArrayBuffer (blob) { this.read(blob, false) }
  readAsDataURL (blob) { this.read(blob, true) }
  async read (blob, dataUrl) {
    try {
      const bytes = await blob.arrayBuffer()
      this.result = dataUrl ? `data:${blob.type};base64,${Buffer.from(bytes).toString('base64')}` : bytes
      this.onloadend?.({ target: this })
    } catch (error) { this.error = error; this.onerror?.({ target: this }) }
  }
}
Object.defineProperty(globalThis, 'FileReader', { configurable: true, value: BlobReader })
const { badgePieces, buildBadge, MEDAL_FORGE, PreparedBadgeCurvature, BadgeScene, THREE } = await import(pathToFileURL(bundle).href)
const ClipperLib = appRequire('clipper-lib')
const library = join(root, 'vendor/patcher/library')
const manifest = JSON.parse(readFileSync(join(library, 'manifest.json'), 'utf8'))
const { joinSvg, unwrapBlock } = await import(pathToFileURL(join(root, 'vendor/patcher/src/library-join.js')).href)
const pathValues = {}
for (const name of readdirSync(join(library, 'shared')).filter((name) => name.startsWith('paths-') && name.endsWith('.json'))) Object.assign(pathValues, JSON.parse(readFileSync(join(library, 'shared', name), 'utf8')))
const store = { block: (id) => unwrapBlock(id, readFileSync(join(library, 'shared', `${id}.svg`), 'utf8')), path: (id) => pathValues[id] }

function geometrySummary (group) {
  const meshes = []
  let vertices = 0
  let zeroNormals = 0
  group.updateMatrixWorld(true)
  group.traverse((mesh) => {
    if (!mesh.isMesh) return
    const position = mesh.geometry.getAttribute('position')
    const normal = mesh.geometry.getAttribute('normal')
    assert.ok(position && normal && position.count === normal.count, 'Every mesh needs positions and normals')
    for (const attr of [position, normal]) for (const value of attr.array) assert.ok(Number.isFinite(value), `${mesh.name}: non-finite geometry`)
    let minZ = Infinity; let maxZ = -Infinity
    for (let i = 0; i < position.count; i++) {
      minZ = Math.min(minZ, position.getZ(i)); maxZ = Math.max(maxZ, position.getZ(i))
      if (Math.hypot(normal.getX(i), normal.getY(i), normal.getZ(i)) < 1e-8) zeroNormals++
    }
    vertices += position.count
    meshes.push({ name: mesh.name, part: mesh.userData.part, reliefRole: mesh.userData.reliefRole ?? null, vertices: position.count, minZ, maxZ, metalness: mesh.material.metalness, roughness: mesh.material.roughness })
  })
  const bounds = new THREE.Box3().setFromObject(group)
  const size = bounds.getSize(new THREE.Vector3())
  return { vertices, triangles: vertices / 3, zeroNormals, sizeMm: size.toArray(), meshes }
}

function assertWardenRelief (prepared, model, flat) {
  assert.equal(prepared.profile, 'junior-warden-tooled-v1')
  const required = ['outer-field', 'field', 'rim', 'letter-shoulder', 'letter-face', 'leaf-blade', 'leaf-veins']
  const byRole = new Map(flat.meshes.filter((mesh) => mesh.reliefRole).map((mesh) => [mesh.reliefRole, mesh]))
  assert.deepEqual([...byRole.keys()].sort(), required.toSorted(), 'The generated mesh retains every semantic relief layer')
  const blade = byRole.get('leaf-blade')
  const veins = byRole.get('leaf-veins')
  const shoulder = byRole.get('letter-shoulder')
  const face = byRole.get('letter-face')
  assert.ok(veins.maxZ - blade.maxZ > 0.12, 'Emitted veins stand above the leaf instead of being buried')
  assert.ok(veins.minZ < blade.maxZ && veins.minZ > blade.minZ, 'Veins overlap their supporting leaf without floating')
  assert.ok(face.maxZ - shoulder.maxZ > 0.1, 'Letter faces stand above their shoulders')
  assert.ok(face.minZ < shoulder.maxZ, 'Letter faces join their supporting shoulders')
  assert.ok(byRole.get('rim').maxZ - byRole.get('field').maxZ > 0.2, 'The rim stands above the field')
  const veinPiece = prepared.pieces.find((piece) => piece.reliefRole === 'leaf-veins')
  assert.equal(veinPiece.sourceIds.length, 19, 'All nineteen source vein paths contribute to the joined ribbon')
  const contours = Object.fromEntries(prepared.pieces.filter((piece) => ['rim', 'leaf-blade', 'leaf-veins', 'letter-face'].includes(piece.reliefRole)).map((piece) => [piece.reliefRole, {
    outer: piece.rings.filter((ring) => ClipperLib.Clipper.Orientation(ring)).length,
    holes: piece.rings.filter((ring) => !ClipperLib.Clipper.Orientation(ring)).length,
  }]))
  assert.deepEqual(contours.rim, { outer: 1, holes: 1 }, 'The rim keeps one connected outer contour and its open centre')
  assert.equal(contours['leaf-blade'].outer, 1, 'Leaf blade and stem stay connected')
  assert.equal(contours['leaf-veins'].outer, 1, 'The nineteen source vein paths form one connected ribbon')
  assert.ok(contours['letter-face'].holes > 0, 'Letter counters survive the face union')
  const meshFor = (role) => model.group.children.find((mesh) => mesh.userData.reliefRole === role)
  const ray = new THREE.Raycaster(new THREE.Vector3(0, 0, 5), new THREE.Vector3(0, 0, -1))
  assert.equal(ray.intersectObject(meshFor('rim')).length, 0, 'The actual rim mesh is a band, not a plate filling the middle')
  // Fixed points observed in the source photograph. The SVG uses a translation (-65,-125), then
  // the builder scales the source outline to nominal mm and centres it. These rays check actual
  // frontmost mesh surfaces, independently of the configured profile heights.
  const outline = prepared.outline.flat()
  const xs = outline.map((point) => point.X / 10000)
  const ys = outline.map((point) => point.Y / 10000)
  const cx = (Math.min(...xs) + Math.max(...xs)) / 2
  const cy = (Math.min(...ys) + Math.max(...ys)) / 2
  const points = [
    { label: 'midrib junction', source: [330, 452], role: 'leaf-veins', z: 0.54 },
    { label: 'left vein branch', source: [296, 428], role: 'leaf-veins', z: 0.54 },
    { label: 'JUNIOR O counter', source: [390, 247], role: 'field', z: 0.065 },
    { label: 'top rim band', source: [296, 145], role: 'rim', z: 0.31 },
  ]
  for (const point of points) {
    const x = (point.source[0] - 65 - cx) / prepared.perMm
    const y = -(point.source[1] - 125 - cy) / prepared.perMm
    ray.set(new THREE.Vector3(x, y, 5), new THREE.Vector3(0, 0, -1))
    const hits = ray.intersectObjects(model.group.children, false)
    assert.ok(hits.length, `${point.label}: the model has a visible surface`)
    assert.equal(hits[0].object.userData.reliefRole, point.role, `${point.label}: correct frontmost relief layer`)
    assert.ok(Math.abs(hits[0].point.z - point.z) < 1e-4, `${point.label}: emitted top height`)
  }
  return { veinClearanceMm: veins.maxZ - blade.maxZ, letteringClearanceMm: face.maxZ - shoulder.maxZ, contours, sourcePointChecks: points }
}

function assertGlb (buffer, id, expectedTriangles) {
  assert.equal(buffer.readUInt32LE(0), 0x46546c67, 'GLB magic')
  assert.equal(buffer.readUInt32LE(4), 2, 'GLB version')
  assert.equal(buffer.readUInt32LE(8), buffer.length, 'GLB byte length')
  assert.equal(buffer.readUInt32LE(16), 0x4e4f534a, 'First GLB chunk is JSON')
  const json = JSON.parse(buffer.subarray(20, 20 + buffer.readUInt32LE(12)).toString('utf8').trim())
  assert.equal(json.asset.version, '2.0')
  const wrapper = json.nodes.find((node) => node.extras?.badge === id)
  assert.ok(wrapper, 'Export retains badge provenance')
  assert.equal(wrapper.extras.physicalMeasurements, false, 'Nominal size must not become a measurement claim')
  const scale = wrapper.scale ?? [wrapper.matrix?.[0], wrapper.matrix?.[5], wrapper.matrix?.[10]]
  assert.deepEqual(scale, [0.001, 0.001, 0.001], 'Millimetre geometry is exported in metres')
  assert.ok(json.meshes.length > 0)
  const binaryHeader = 20 + buffer.readUInt32LE(12)
  assert.equal(buffer.readUInt32LE(binaryHeader + 4), 0x004e4942, 'Second GLB chunk is binary data')
  const binaryStart = binaryHeader + 8
  let triangles = 0
  let indexedPrimitives = 0
  for (const mesh of json.meshes) for (const primitive of mesh.primitives) {
    const position = json.accessors[primitive.attributes.POSITION]
    const normal = json.accessors[primitive.attributes.NORMAL]
    assert.equal(position.count, normal.count, 'Exported positions retain their normal seams')
    for (const accessor of [position, normal]) {
      assert.equal(accessor.type, 'VEC3')
      assert.equal(accessor.componentType, 5126)
      const view = json.bufferViews[accessor.bufferView]
      const start = binaryStart + (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0)
      const stride = view.byteStride ?? 12
      for (let vertex = 0; vertex < accessor.count; vertex++) {
        for (let axis = 0; axis < 3; axis++) assert.ok(Number.isFinite(buffer.readFloatLE(start + vertex * stride + axis * 4)), 'Export contains finite geometry')
      }
    }
    if (Number.isInteger(primitive.indices)) {
      indexedPrimitives++
      triangles += json.accessors[primitive.indices].count / 3
    } else triangles += position.count / 3
  }
  assert.equal(triangles, expectedTriangles, 'Index sharing preserves the complete triangle surface')
  if (!baseline) assert.ok(indexedPrimitives > 0, 'The current export shares matching vertices')
  return { bytes: buffer.length, meshes: json.meshes.length, indexedPrimitives, triangles, drawingSha256: wrapper.extras.drawingSha256, curvature: wrapper.extras.curvature }
}

const reports = []
for (const id of ['S01-O01', 'S51-O01']) {
  const org = manifest.orgs.find((org) => org.patches.some((patch) => patch.id === id))
  const patch = org?.patches.find((patch) => patch.id === id)
  assert.ok(patch, `${id} must exist in the current library`)
  const svg = joinSvg(readFileSync(join(library, patch.svg), 'utf8'), store)
  const digest = createHash('sha256').update(svg).digest('hex')
  assert.equal(digest, patch.sha256, 'Model input must match the current joined library SVG')
  const options = { medium: patch.medium, family: patch.family, sizeMm: 65 }
  const prepared = badgePieces(svg, options)
  const model = buildBadge(svg, options)
  const textureHost = { renderer: { capabilities: { getMaxAnisotropy: () => 1 } }, modelTextures: [] }
  model.group.traverse((mesh) => {
    if (mesh.isMesh && mesh.userData.fieldMap) {
      BadgeScene.prototype.texture.call(textureHost, mesh.material, mesh.userData.fieldMap)
      delete mesh.userData.fieldMap
    }
  })
  assert.equal(model.metal, id === 'S01-O01' ? 'leather' : 'gold')
  const flat = geometrySummary(model.group)
  assert.equal(flat.zeroNormals, 0, `${id}: flat mesh normals are defined`)
  // The engine sizes the source outline at 65 mm; bevels can extend it by a fraction of a millimetre.
  assert.ok(Math.abs(Math.max(flat.sizeMm[0], flat.sizeMm[1]) - 65) < 0.65, `${id}: nominal longest dimension remains within 1% of 65 mm; got ${flat.sizeMm.join(' × ')}`)
  if (id === 'S01-O01') assert.ok(flat.meshes.every((mesh) => mesh.metalness === 0), 'Leather has no metallic materials')
  else assert.ok(flat.meshes.some((mesh) => mesh.metalness > 0.8), 'The metal control badge retains metallic surfaces')
  const roles = prepared.pieces.map((piece) => ({ sourceIds: piece.sourceIds ?? [], role: piece.reliefRole ?? null, part: piece.part, thickness: piece.thickness, bevel: piece.bevel, base: piece.base ?? 0 }))
  const relief = id === 'S01-O01' && !baseline ? assertWardenRelief(prepared, model, flat) : null
  if (id === 'S01-O01' && !baseline) {
    assert.equal(badgePieces(svg, { ...options, family: 'other-family' }).profile, null, 'Other families keep the generic path')
    assert.equal(badgePieces(svg, { ...options, medium: 'Metal badge' }).profile, null, 'The leather profile is not inferred over a metal record')
    assert.equal(badgePieces(svg.replace('id="maple-leaf-blade-and-stem"', 'id="unrecognized-leaf"'), options).profile, null, 'Changed unrecognized artwork is not forced into the profile')
  }
  const report = { id, inputSha256: digest, medium: patch.medium, family: patch.family, profile: prepared.profile ?? null, metal: model.metal, stats: model.stats, flat, relief, pieces: roles, curves: [], exports: [] }
  const curvature = new PreparedBadgeCurvature(model.group, { maxEdgeLength: Math.max(0.8, 65 / 36), maxVertices: 2_400_000 })
  const original = curvature.states.map((state) => new Float32Array(state.geometry.getAttribute('position').array))
  for (const [mode, requestedRise] of [['flat', 0], ['cylinder', 4], ['dome', 4]]) {
    const applied = curvature.apply({ mode, rise: Math.min(requestedRise, curvature.maxRise(mode)), neutralZ: 0 })
    const summary = geometrySummary(model.group)
    assert.equal(summary.zeroNormals, 0, `${id}: ${mode} mesh normals are defined`)
    assert.equal(applied.mode, mode)
    assert.equal(applied.rise, requestedRise)
    report.curves.push({ ...applied, sizeMm: summary.sizeMm, zeroNormals: summary.zeroNormals })
    if (id === 'S01-O01') {
      const filename = `${id}-${mode}.glb`
      const liveBuffers = model.group.children.map((mesh) => ({ geometry: mesh.geometry, position: new Float32Array(mesh.geometry.getAttribute('position').array), normal: new Float32Array(mesh.geometry.getAttribute('normal').array) }))
      const blob = await BadgeScene.prototype.glb.call({ model: model.group }, {
        badge: id,
        label: patch.label,
        organization: org.name,
        material: 'Tooled leather (catalogue attribution, unverified)',
        nominalLongerSideMm: 65,
        physicalMeasurements: false,
        curvature: applied,
        drawingSha256: digest,
        engine: MEDAL_FORGE,
        limitations: 'Interpreted relief, size, finish and curvature; the reverse is generated, without fittings or marks. Not a 3D scan or a manufacturing master.',
      })
      const buffer = Buffer.from(await blob.arrayBuffer())
      model.group.children.forEach((mesh, index) => {
        assert.equal(mesh.geometry, liveBuffers[index].geometry, 'Export must not replace live model geometry')
        assert.deepEqual(mesh.geometry.getAttribute('position').array, liveBuffers[index].position, 'Export must not mutate live positions')
        assert.deepEqual(mesh.geometry.getAttribute('normal').array, liveBuffers[index].normal, 'Export must not mutate live normals')
      })
      const check = assertGlb(buffer, id, applied.triangles)
      if (output) writeFileSync(join(output, filename), buffer)
      report.exports.push({ filename, sha256: createHash('sha256').update(buffer).digest('hex'), ...check })
    }
  }
  curvature.apply({ mode: 'flat', rise: 0 })
  curvature.states.forEach((state, i) => assert.deepEqual(state.geometry.getAttribute('position').array, original[i], 'Returning to flat restores all prepared positions exactly'))
  curvature.dispose()
  model.group.traverse((mesh) => { if (mesh.isMesh) { mesh.geometry.dispose(); mesh.material.dispose() } })
  textureHost.modelTextures.forEach((texture) => texture.dispose())
  reports.push(report)
}
const sourceFiles = ['src/badges/medalBadge.js', 'src/badges/badgeParts.js', 'src/badges/curvature.js', 'src/badges/badgeScene.js'].map((name) => ({
  name,
  sha256: createHash('sha256').update(before.get(join(root, name)) ?? readFileSync(join(root, name))).digest('hex'),
}))
const result = { result: 'PASS', mode: baseline ? 'baseline comparison' : 'current model validation', baseline, browserAcceptance: false, engine: MEDAL_FORGE, sourceFiles, reports }
if (output) writeFileSync(join(output, 'model-validation.json'), JSON.stringify(result, null, 2) + '\n')
console.log(JSON.stringify({ ...result, reports: reports.map(({ pieces, flat, ...report }) => ({ ...report, flat: { ...flat, meshes: flat.meshes.length }, pieces: pieces.length })) }, null, 2))
dom.window.close()
