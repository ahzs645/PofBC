// A pin as the object: its construction recipe (construction.js) built in 3D on the badges' stage
// (src/badges/BadgeStage.jsx), with its own drawing printed on the face. Loaded only when a pin's
// 3D view is opened, so the shelf does not carry three.js.

import { useEffect, useRef, useState } from 'react'
import { BadgeStage } from '../badges/BadgeStage.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { buildPrintedButton, faceCanvas, faceTexture } from './printedButton.js'
import { FACE_SHAPES, diameterWords, faceShapeFor } from './construction.js'
import './pinModel.css'

const CAMERAS = [
  { value: 'front', label: 'Front' },
  { value: 'oblique', label: 'Oblique' },
  { value: 'side', label: 'Side' },
  { value: 'back', label: 'Back', title: 'The back: a generic tin back and safety pin' }
]
// A recipe can word its own note (construction.js); this is the usual one.
const NOTE = 'Illustrative: diameter, dome and the back are not known from the photograph; the face is printed artwork.'

const escape = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
/** The drawing and its ground colour with a variation's colour swaps applied. */
const swapped = (text, swap) => (swap ?? []).reduce((out, [from, to]) => out.replace(new RegExp(escape(from), 'gi'), to), text)

const download = (blob, name) => {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = name
  link.click()
  setTimeout(() => URL.revokeObjectURL(link.href), 1000)
}

export default function PinModel ({ meta, module, swap, variation }) {
  const recipe = module.construction
  const note = recipe.note ?? NOTE
  const sceneRef = useRef(null)
  const [scene, setScene] = useState(null)
  const [camera, setCamera] = useState('oblique')
  const cameraRef = useRef(camera)
  cameraRef.current = camera
  const [shape, setShape] = useState(() => faceShapeFor(recipe.dome).value)
  const dome = FACE_SHAPES.find((entry) => entry.value === shape).dome
  const domeRef = useRef(dome)
  domeRef.current = dome
  const [built, setBuilt] = useState(null)
  const [phase, setPhase] = useState('building')
  const [exporting, setExporting] = useState(null)
  const [exportError, setExportError] = useState(null)
  const swapKey = JSON.stringify(swap ?? [])

  // Print the face, build the button and put it on the stage; again when the face's colours change.
  useEffect(() => {
    if (!scene) return undefined
    let gone = false
    let map = null
    setPhase('building')
    setBuilt(null)
    const background = swapped(recipe.face.background, swap)
    faceCanvas(swapped(module.svgRaw, swap), background)
      .then((canvas) => {
        if (gone) return
        map = faceTexture(canvas, { anisotropy: scene.renderer.capabilities.getMaxAnisotropy() })
        const button = buildPrintedButton(recipe, { map, dome: domeRef.current })
        scene.fitWidth = true
        scene.setModel(button.group, { metal: 'printed', bendable: false })
        scene.setView(cameraRef.current)
        setBuilt({ button, scene, dome: domeRef.current })
        setPhase('ready')
      })
      .catch((error) => { console.error(error); if (!gone) setPhase('failed') })
    return () => { gone = true; map?.dispose() }
  }, [scene, module.svgRaw, recipe, swapKey]) // eslint-disable-line react-hooks/exhaustive-deps

  // A new face shape reshapes the shell in place, so the view stays where it was turned to.
  useEffect(() => {
    if (!built || built.dome === dome || built.scene !== scene) return
    built.button.setDome(dome)
    built.dome = dome
    scene.render()
  }, [built, dome, scene])

  const ready = phase === 'ready' && Boolean(built)
  const shapeLabel = FACE_SHAPES.find((entry) => entry.value === shape).label
  const stem = `${meta.id}-${shapeLabel.toLowerCase().replace(/\s+/g, '-')}${variation && variation !== module.variations?.options[0]?.id ? `-${variation}` : ''}`

  const exportModel = async (format) => {
    if (!ready || exporting) return
    setExporting(format)
    setExportError(null)
    try {
      const blob = format === 'png' ? await scene.png() : await scene.glb({
        pin: meta.id,
        title: meta.title,
        construction: { ...recipe, dome },
        faceVariation: variation,
        physicalMeasurements: false,
        limitations: note
      })
      download(blob, `${stem}.${format}`)
    } catch (error) {
      console.error(error)
      setExportError(`The ${format.toUpperCase()} export could not be created.`)
    } finally {
      setExporting(null)
    }
  }

  const status = phase === 'building' ? 'Printing the face…' : phase === 'failed' ? 'The 3D view could not be built.' : null
  const faceControl = (
    <Segmented label="Face" options={FACE_SHAPES} value={shape} onChange={setShape} compact />
  )

  return (
    <div className="pin-model">
      <BadgeStage
        sceneRef={sceneRef}
        toolbar={faceControl}
        status={status}
        onReady={setScene}
        label={`${meta.title}, 3D model of the button`}
        camera={camera}
        onCamera={setCamera}
        cameras={CAMERAS}
        unavailable="This browser can’t show 3D (WebGL is off or unavailable). The drawing is a switch away."
      />
      <div className="pin-model__foot">
        <p className="pin-model__note" title={`Built at ${diameterWords(recipe)}; ${recipe.evidence.join(' ')}`}>{note}</p>
        <div className="pin-model__exports">
          <button type="button" className="pv-ghost" disabled={!ready || Boolean(exporting)} onClick={() => exportModel('png')} title="The view as it is now">{exporting === 'png' ? 'PNG…' : 'Export PNG'}</button>
          <button type="button" className="pv-ghost" disabled={!ready || Boolean(exporting)} onClick={() => exportModel('glb')} title="The model, in metres, with its recipe">{exporting === 'glb' ? 'GLB…' : 'Export GLB'}</button>
        </div>
      </div>
      {exportError && <p className="pin-model__error" role="alert">{exportError}</p>}
    </div>
  )
}
