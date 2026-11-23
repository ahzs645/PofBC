// PackCAD's viewer in a frame, and a hook to talk to it.
//
// Only messages from this frame's own window are read, and commands go to it alone. Commands sent
// before the viewer has said it is ready would be lost, so `send` drops them; the view disables
// its controls until then instead.

import { forwardRef, useCallback, useEffect, useRef, useState } from 'react'
import { viewerEvent } from './packcadFrame.js'

/**
 * @returns {{ frame: React.RefObject<HTMLIFrameElement>, ready: object|null, state: object|null,
 *   error: string|null, send: (command: object) => void }}
 */
export const usePackcadViewer = (src) => {
  const frame = useRef(null)
  const [ready, setReady] = useState(null)
  const [state, setState] = useState(null)
  const [error, setError] = useState(null)

  // A new address is a new project: forget what the last one said.
  useEffect(() => { setReady(null); setState(null); setError(null) }, [src])

  useEffect(() => {
    const listen = (event) => {
      if (!frame.current || event.source !== frame.current.contentWindow) return
      const message = viewerEvent(event.data)
      if (message?.type === 'packcad:ready') setReady(message)
      if (message?.type === 'packcad:state') setState(message)
      if (message?.type === 'packcad:error') setError(message.message)
    }
    globalThis.addEventListener('message', listen)
    return () => globalThis.removeEventListener('message', listen)
  }, [])

  const send = useCallback((command) => {
    frame.current?.contentWindow?.postMessage(command, '*')
  }, [])

  return { frame, ready, state, error, send }
}

export const PackcadFrame = forwardRef(({ src, title, className, loading = false }, ref) => (
  <iframe
    ref={ref}
    key={src}
    src={src}
    title={title}
    className={className}
    data-loading={loading || undefined}
    // The viewer fetches its project from this site and renders with WebGL; it needs nothing else.
    sandbox="allow-scripts allow-same-origin"
    allow="fullscreen"
  />
))
PackcadFrame.displayName = 'PackcadFrame'
