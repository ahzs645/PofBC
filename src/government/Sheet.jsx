// On a phone, the chosen body's panel as a sheet over the foot of the diagram, rather than a page
// below it: the diagram stays in view to choose the next body, and the sheet is pulled up to read.
//
// It rests half open, with the diagram above it, or pulled up to fill the screen. Its handle drags
// it between the two, and dragging it down from half open lets the body go.

import { useEffect, useRef, useState } from 'react'

// Below this share of its half-open height a released drag closes the sheet.
const CLOSE_BELOW = 0.6

export const Sheet = ({ label, title, tools, onClose, children }) => {
  const [full, setFull] = useState(false)
  const [drag, setDrag] = useState(null)
  // The bar names the body only once the panel's own heading has scrolled out from under it, so
  // the name is never on screen twice.
  const [named, setNamed] = useState(false)
  const sheet = useRef(null)
  const body = useRef(null)

  // A new body starts at the top of its panel.
  useEffect(() => { body.current?.scrollTo({ top: 0 }) }, [title])

  useEffect(() => {
    const heading = body.current?.querySelector('h1')
    if (!heading) return undefined
    const observer = new IntersectionObserver(([entry]) => setNamed(!entry.isIntersecting), { root: body.current })
    observer.observe(heading)
    return () => observer.disconnect()
  }, [title])

  useEffect(() => {
    const listen = (event) => { if (event.key === 'Escape') onClose() }
    globalThis.addEventListener('keydown', listen)
    return () => globalThis.removeEventListener('keydown', listen)
  }, [onClose])

  const start = (event) => {
    if (event.button !== 0 || event.target.closest('button:not(.gov-sheet__handle)')) return
    event.currentTarget.setPointerCapture(event.pointerId)
    setDrag({ y: event.clientY, height: sheet.current.getBoundingClientRect().height, now: null, moved: false })
  }
  const move = (event) => {
    if (!drag) return
    const delta = drag.y - event.clientY
    if (!drag.moved && Math.abs(delta) < 6) return
    setDrag({ ...drag, now: Math.max(80, drag.height + delta), moved: true })
  }
  const end = () => {
    if (!drag) return
    setDrag(null)
    // A tap, not a drag: the bar toggles between half open and full.
    if (!drag.moved) return setFull((value) => !value)
    const half = globalThis.innerHeight * 0.45
    if (drag.now < half * CLOSE_BELOW) onClose()
    else setFull(drag.now > (half + globalThis.innerHeight) / 2)
  }

  return (
    <section
      ref={sheet}
      className="gov-sheet"
      data-full={full || undefined}
      data-dragging={drag?.moved || undefined}
      style={drag?.moved ? { height: `${drag.now}px` } : undefined}
      role="dialog"
      aria-label={label}
    >
      <div className="gov-sheet__bar" onPointerDown={start} onPointerMove={move} onPointerUp={end} onPointerCancel={end}>
        <button
          type="button"
          className="gov-sheet__handle"
          aria-label={full ? 'Show the diagram' : 'Read in full'}
          aria-expanded={full}
          // The pointer is captured by the bar, which handles taps; this is for the keyboard.
          onClick={(event) => { if (event.detail === 0) setFull((value) => !value) }}
        />
        <div className="gov-sheet__head">
          <strong className="gov-sheet__title" data-shown={named || undefined} aria-hidden={!named || undefined}>{title}</strong>
          {tools}
          <button type="button" className="gov-button gov-button--icon" onClick={onClose} aria-label="Close">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M3.5 3.5l7 7M10.5 3.5l-7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>
      <div className="gov-sheet__body" ref={body}>{children}</div>
    </section>
  )
}
