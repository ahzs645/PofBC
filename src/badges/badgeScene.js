// The stage a metal badge is shown on: one WebGL canvas, an environment to reflect, orbit controls,
// named camera positions, the shared curvature, and PNG and GLB exports. Lighting, camera and the
// tight clip range follow the curved badge trial's viewer (src/main.ts).

import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js'
import { PreparedBadgeCurvature } from './curvature.js'

/** Camera directions, scaled to the badge's size when used. */
const VIEWS = {
  front: [0, 0, 1],
  oblique: [0.43, 0.15, 0.92],
  top: [0, 1, 0.08],
  side: [1, 0.04, 0],
  back: [-0.35, 0.12, -0.93]
}
export const VIEW_NAMES = Object.keys(VIEWS)

export class BadgeScene {
  /** @param {HTMLCanvasElement} canvas */
  constructor (canvas) {
    this.canvas = canvas
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true })
    this.renderer.setPixelRatio(Math.min(globalThis.devicePixelRatio || 1, 2))
    this.renderer.outputColorSpace = THREE.SRGBColorSpace
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.15
    this.renderer.setClearColor(0x000000, 0)
    // Struck relief reads by its shadows: on a silver badge a raised letter is the field's own colour.
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFShadowMap

    this.scene = new THREE.Scene()
    const room = new RoomEnvironment()
    const pmrem = new THREE.PMREMGenerator(this.renderer)
    this.environment = pmrem.fromScene(room, 0.04).texture
    room.dispose()
    pmrem.dispose()
    this.scene.environment = this.environment
    // Less fill from the room than the trial's 1.1, so the key light's shadows are not washed out.
    this.scene.environmentIntensity = 0.85
    // From the upper left and lower than the trial's key, so a letter's shoulder catches the light
    // on one side and drops a short shadow on the other, as in the reference photographs.
    const key = new THREE.DirectionalLight('#fff0d8', 3.4)
    key.position.set(-45, 50, 50)
    key.castShadow = true
    key.shadow.mapSize.set(2048, 2048)
    key.shadow.bias = -0.0004
    key.shadow.normalBias = 0.02
    this.scene.add(key.target)
    const fill = new THREE.DirectionalLight('#b7d6ee', 1.7)
    fill.position.set(55, 20, 20)
    const rim = new THREE.DirectionalLight('#ffe2b1', 1.3)
    rim.position.set(-30, -30, 10)
    this.lights = [key, fill, rim]
    this.scene.add(key, fill, rim)

    this.camera = new THREE.PerspectiveCamera(40, 1, 1, 400)
    this.controls = new OrbitControls(this.camera, canvas)
    this.controls.enablePan = false
    this.controls.enableDamping = false
    this.controls.addEventListener('change', () => this.render())
    this.model = null
    this.modelTextures = []
    this.curvature = null
    this.reach = 65
    this.viewName = 'oblique'
  }

  /**
   * Show a built badge (medalBadge.js). The scene owns it from here and disposes of it.
   * Leather takes softer light: lit for polished metal, a diffuse surface washes out.
   */
  setModel (group, { metal = 'gold' } = {}) {
    this.clearModel()
    const soft = metal === 'leather'
    this.renderer.toneMappingExposure = soft ? 0.72 : 1.15
    this.lights.forEach((light, i) => { light.intensity = [3.4, 1.7, 1.3][i] * (soft ? 0.55 : 1) })
    this.model = group
    this.scene.add(group)
    // Keep long triangles short enough to bend smoothly; finer for a small badge.
    const box = new THREE.Box3().setFromObject(group)
    const size = box.getSize(new THREE.Vector3())
    this.reach = Math.max(size.x, size.y)
    group.traverse((o) => {
      if (!o.isMesh) return
      o.castShadow = true
      o.receiveShadow = true
      if (o.userData.fieldMap) {
        this.texture(o.material, o.userData.fieldMap)
        // The pixels now live in the texture; left here, a GLB export would write them out as JSON.
        delete o.userData.fieldMap
      }
    })
    // The key light's shadow covers the badge and no more, so its texels stay finer than the relief.
    const shadow = this.lights[0].shadow.camera
    const half = this.reach * 0.75
    Object.assign(shadow, { left: -half, right: half, top: half, bottom: -half, near: 1, far: this.reach * 4 })
    this.lights[0].position.setLength(this.reach * 1.6)
    shadow.updateProjectionMatrix()
    this.curvature = new PreparedBadgeCurvature(group, { maxEdgeLength: Math.max(0.8, this.reach / 36), maxVertices: 2_400_000 })
    this.controls.minDistance = this.reach * 0.9
    this.controls.maxDistance = this.reach * 3.6
    this.setView(this.viewName)
  }

  /** Give a field its struck texture: the normal map stipple.js made for this badge's field. */
  texture (material, field) {
    const map = new THREE.DataTexture(field.data, field.width, field.height, THREE.RGBAFormat)
    map.wrapS = THREE.ClampToEdgeWrapping
    map.wrapT = THREE.ClampToEdgeWrapping
    map.colorSpace = THREE.NoColorSpace
    map.magFilter = THREE.LinearFilter
    map.minFilter = THREE.LinearMipmapLinearFilter
    map.generateMipmaps = true
    map.anisotropy = this.renderer.capabilities.getMaxAnisotropy()
    map.needsUpdate = true
    this.modelTextures.push(map)
    material.normalMap = map
    // The bumps' crowns catch the light: a little smoother than a plain satin field.
    material.roughness = field.roughness
    if (field.tone) material.color.multiplyScalar(field.tone)
    material.needsUpdate = true
  }

  clearModel () {
    if (!this.model) return
    this.curvature?.dispose()
    this.curvature = null
    this.scene.remove(this.model)
    this.model.traverse((o) => { if (o.isMesh) { o.geometry.dispose(); o.material.dispose() } })
    this.modelTextures.forEach((map) => map.dispose())
    this.modelTextures = []
    this.model = null
  }

  /** The largest rise the current model allows for a mode, in mm. */
  maxRise (mode) {
    return this.curvature ? this.curvature.maxRise(mode) : 0
  }

  /** @param {'flat'|'cylinder'|'dome'} mode @param {number} rise in mm */
  bend (mode, rise) {
    if (!this.curvature) return null
    const safe = mode === 'flat' ? 0 : Math.min(rise, this.maxRise(mode))
    const result = this.curvature.apply({ mode, rise: safe, neutralZ: 0 })
    this.render()
    return result
  }

  setView (name) {
    this.viewName = VIEWS[name] ? name : 'oblique'
    const [x, y, z] = VIEWS[this.viewName]
    const distance = this.reach * 1.75
    this.camera.position.set(x, y, z).normalize().multiplyScalar(distance)
    this.camera.up.set(0, 1, 0)
    if (this.viewName === 'top') this.camera.up.set(0, 0, -1)
    this.controls.target.set(0, 0, -0.8)
    this.controls.update()
    this.render()
  }

  resize (width, height) {
    if (!width || !height) return
    this.renderer.setSize(width, height, false)
    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.render()
  }

  render () {
    // A clip range local to the badge keeps the depth precision its thin layers need.
    const distance = this.camera.position.distanceTo(this.controls.target)
    this.camera.near = Math.max(1, distance - this.reach)
    this.camera.far = distance + this.reach
    this.camera.updateProjectionMatrix()
    this.renderer.render(this.scene, this.camera)
  }

  /** Rotate the camera about the badge by small steps, for the keyboard. */
  orbit (dTheta, dPhi) {
    const offset = this.camera.position.clone().sub(this.controls.target)
    const s = new THREE.Spherical().setFromVector3(offset)
    s.theta += dTheta
    s.phi = Math.max(0.05, Math.min(Math.PI - 0.05, s.phi + dPhi))
    this.camera.position.copy(new THREE.Vector3().setFromSpherical(s).add(this.controls.target))
    this.controls.update()
    this.render()
  }

  /** @returns {Promise<Blob>} */
  png () {
    this.render()
    return new Promise((resolve, reject) => this.canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error('No image'))), 'image/png'))
  }

  /** The model as it is bent now, in metres, with what it is and is not recorded in its extras. */
  async glb (extras = {}) {
    if (!this.model) throw new Error('No badge to export')
    const wrapper = new THREE.Group()
    wrapper.add(this.model.clone(true))
    wrapper.scale.setScalar(0.001)
    wrapper.userData = extras
    const buffer = await new GLTFExporter().parseAsync(wrapper, { binary: true, onlyVisible: true })
    return new Blob([buffer], { type: 'model/gltf-binary' })
  }

  dispose () {
    this.clearModel()
    this.controls.dispose()
    this.environment.dispose()
    this.renderer.dispose()
  }
}
