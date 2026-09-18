// Copying a link that reproduces the current lockup.

import { useEffect, useRef, useState } from 'react'
import { buildShareUrl } from './shareLink.js'

export const ShareLink = ({ state }) => {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState({ message: '', tone: 'info' })
  const [busy, setBusy] = useState(false)
  const alive = useRef(true)

  useEffect(() => {
    alive.current = true
    return () => { alive.current = false }
  }, [])

  // Any change to the lockup invalidates a link already on screen, so it is cleared rather than
  // left there looking current.
  useEffect(() => {
    setUrl('')
    setStatus({ message: '', tone: 'info' })
  }, [state])

  const share = async () => {
    setBusy(true)

    try {
      const next = await buildShareUrl(state)
      if (!alive.current) return
      setUrl(next)

      // Clipboard access needs a secure context and can be refused outright; when it is, the URL
      // is shown instead so the link is never simply lost.
      try {
        await navigator.clipboard.writeText(next)
        if (alive.current) setStatus({ message: 'Link copied to the clipboard.', tone: 'info' })
      } catch {
        if (alive.current) setStatus({ message: 'Copy this link:', tone: 'info' })
      }
    } catch (error) {
      console.error(error)
      if (alive.current) setStatus({ message: 'Could not build a link.', tone: 'error' })
    } finally {
      if (alive.current) setBusy(false)
    }
  }

  return (
    <section className="panel">
      <h2>Share</h2>
      <p className="panel__hint">
        A link carrying this exact lockup — every setting travels in the URL, so there is nothing to
        upload and nothing to keep.
      </p>

      <button type="button" className="button" onClick={share} disabled={busy}>
        {busy ? 'Building…' : 'Copy link'}
      </button>

      {url && (
        <input
          className="share__url"
          type="text"
          value={url}
          readOnly
          aria-label="Shareable link"
          onFocus={(event) => event.target.select()}
        />
      )}

      <p className="export__status" data-tone={status.tone} role="status" aria-live="polite">
        {status.message}
      </p>
    </section>
  )
}
