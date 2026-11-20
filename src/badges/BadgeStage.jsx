// The 3D stage shared by the badges (BadgeViewer.jsx) and the pins (src/pins/PinModel.jsx): a
// BadgeScene on a canvas that fills its pane, a toolbar slot, the camera presets, keyboard orbit
// and a one-line hint. The caller builds the model and hands it to the scene through `onReady`.

import { useEffect, useId, useRef, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { BadgeScene } from './badgeScene.js'
import './badges.css'

export const CAMERAS = [
  { value: 'front', label: 'Front' },
  { value: 'oblique', label: 'Oblique' },
  { value: 'top', label: 'Top', title: 'Looking down on the curve' },
  { value: 'side', label: 'Side' },
  { value: 'back', label: 'Back', title: 'The reverse: generated, without fittings or marks' }
]

export const webglAvailable = () => {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}

/**
 * The 3D stage: a canvas that fills its pane, the mode switch and the camera presets above it.
 * `cameras` narrows the presets (a pin has no use for Top); `unavailable` words the message for a
 * browser without WebGL.
 */
export function BadgeStage ({ sceneRef, toolbar, status, onReady, label, camera, onCamera, cameras = CAMERAS, unavailable = 'This browser can’t show 3D (WebGL is off or unavailable). The vector is a tab away.' }) {
  const canvas = useRef(null)
  const pane = useRef(null)
  const hintId = useId()
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (!webglAvailable()) { setFailed(true); return undefined }
    let scene
    try {
      scene = new BadgeScene(canvas.current)
    } catch (error) {
      console.error(error)
      setFailed(true)
      return undefined
    }
    sceneRef.current = scene
    const observer = new ResizeObserver(([entry]) => scene.resize(entry.contentRect.width, entry.contentRect.height))
    observer.observe(pane.current)
    onReady(scene)
    return () => { observer.disconnect(); onReady(null); scene.dispose(); if (sceneRef.current === scene) sceneRef.current = null }
  }, [])

  const onKeyDown = (event) => {
    const scene = sceneRef.current
    if (!scene) return
    const step = 0.1
    if (event.key === 'r' || event.key === 'R') { scene.setView('oblique'); onCamera('oblique'); return }
    const moves = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }
    if (!moves[event.key]) return
    event.preventDefault()
    event.stopPropagation()
    scene.orbit(...moves[event.key])
  }

  return (
    <div className="patch-stage badge-stage">
      <div className="patch-stage__bar">
        <div className="patch-stage__tools">{toolbar}</div>
        <div className="badge-stage__cameras">
          <Segmented ariaLabel="Camera" options={cameras} value={camera} onChange={(value) => { sceneRef.current?.setView(value); onCamera(value) }} compact />
        </div>
      </div>
      <div ref={pane} className="badge-stage__pane">
        {failed
          ? <p className="patch__status" role="alert">{unavailable}</p>
          : <canvas ref={canvas} tabIndex={0} role="img" aria-label={label} aria-describedby={hintId} onKeyDown={onKeyDown} />}
        {!failed && status && <p className="patch__status badge-stage__status" role="status">{status}</p>}
      </div>
      {!failed && <p id={hintId} className="badge-stage__hint">Drag to rotate · Pinch or scroll to zoom · Arrow keys to turn · R to reset the view</p>}
    </div>
  )
}
