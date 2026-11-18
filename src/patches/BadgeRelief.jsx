import { useEffect, useRef, useState } from 'react'
import { prepareRelief } from './badgeRelief.js'

const LIMIT = 42

export function BadgeRelief ({ drawing, patch, title }) {
  const host = useRef(null)
  const renderer = useRef(null)
  const drag = useRef(null)
  const currentAngle = useRef(0)
  const [angle, setAngle] = useState(0)
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    if (!drawing?.url) return
    let active = true
    const canvas = document.createElement('canvas')
    canvas.setAttribute('aria-hidden', 'true')
    const gl = canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: false, depth: false, antialias: true })
    if (!gl) { setStatus('unavailable'); return }
    const lost = () => { if (active) { renderer.current = null; setStatus('unavailable') } }
    canvas.addEventListener('webglcontextlost', lost)
    host.current.append(canvas)
    setStatus('loading')
    prepareRelief(gl, drawing, patch, () => active).then((draw) => {
      if (!active || !draw || gl.isContextLost()) return
      renderer.current = draw
      draw(currentAngle.current)
      setStatus('ready')
    }).catch(() => { if (active) setStatus('unavailable') })
    return () => {
      active = false
      renderer.current = null
      canvas.removeEventListener('webglcontextlost', lost)
      canvas.remove()
      gl.getExtension('WEBGL_lose_context')?.loseContext()
    }
  }, [drawing, patch])

  function turn (value) {
    const next = Math.max(-LIMIT, Math.min(LIMIT, Math.round(value)))
    currentAngle.current = next
    setAngle(next)
    renderer.current?.(next)
  }

  return (
    <figure className="patch__stage patch__stage--relief">
      <figcaption>3D relief</figcaption>
      <div
        ref={host} className="badge-relief__art" data-ready={status === 'ready'}
        role="img" aria-label={`${title}, front relief at ${angle} degrees`}
        onPointerDown={(event) => {
          if (status !== 'ready' || !event.isPrimary || event.button !== 0) return
          event.currentTarget.setPointerCapture(event.pointerId)
          drag.current = { x: event.clientX, angle }
        }}
        onPointerMove={(event) => {
          if (drag.current && event.isPrimary) turn(drag.current.angle + (event.clientX - drag.current.x) * .35)
        }}
        onLostPointerCapture={() => { drag.current = null }}
      >
        {status !== 'ready' && <img src={drawing?.url ?? patch.previewUrl} alt="" />}
      </div>
      {status === 'ready' ? (
        <label className="badge-relief__turn">
          Turn badge
          <input type="range" min={-LIMIT} max={LIMIT} value={angle} onChange={(event) => turn(Number(event.target.value))} aria-valuetext={`${angle} degrees`} />
          <output>{angle}°</output>
        </label>
      ) : <p className="patch__status" role="status">{status === 'unavailable' ? '3D is unavailable on this device. Showing the vector drawing.' : drawing?.failed ? 'Relief requires the vector drawing.' : 'Loading relief…'}</p>}
    </figure>
  )
}
