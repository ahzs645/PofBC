// Getting a lockup out of here, and back in again.
//
// Three routes, because they suit different callers. A share link is short and opaque, for sending
// to a person. A configuration is readable JSON in the app's documented vocabulary, for anything
// writing one by hand — which in practice means an agent that has read capabilities.json and wants
// to hand over a lockup rather than a list of instructions to re-enter.

import { useEffect, useRef, useState } from 'react'
import { buildConfigUrl, parseConfig, toConfig } from './configFormat.js'
import { buildShareUrl } from './shareLink.js'

const copy = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // Needs a secure context and can be refused outright; the caller shows the text instead.
    return false
  }
}

export const ShareLink = ({ state, update }) => {
  const [url, setUrl] = useState('')
  const [draft, setDraft] = useState('')
  const [status, setStatus] = useState({ message: '', tone: 'info' })
  const [busy, setBusy] = useState(false)
  const alive = useRef(true)

  useEffect(() => {
    alive.current = true
    return () => { alive.current = false }
  }, [])

  // Any change to the lockup invalidates what is on screen, so it is cleared rather than left
  // there looking current. The draft is only reset when it has not been edited away from the
  // lockup, so a half-pasted configuration is not destroyed by a stray click.
  useEffect(() => {
    setUrl('')
    setStatus({ message: '', tone: 'info' })
  }, [state])

  const configuration = JSON.stringify(toConfig(state), null, 2)

  const share = async () => {
    setBusy(true)
    try {
      const next = await buildShareUrl(state)
      if (!alive.current) return
      setUrl(next)
      setStatus(await copy(next)
        ? { message: 'Link copied to the clipboard.', tone: 'info' }
        : { message: 'Copy this link:', tone: 'info' })
    } catch (error) {
      console.error(error)
      if (alive.current) setStatus({ message: 'Could not build a link.', tone: 'error' })
    } finally {
      if (alive.current) setBusy(false)
    }
  }

  const copyConfiguration = async () => {
    setStatus(await copy(configuration)
      ? { message: 'Configuration copied.', tone: 'info' }
      : { message: 'Select the text below and copy it.', tone: 'info' })
  }

  const copyConfigurationLink = async () => {
    const link = buildConfigUrl(state)
    setUrl(link)
    setStatus(await copy(link)
      ? { message: 'Link copied — it opens the generator with these settings.', tone: 'info' }
      : { message: 'Copy this link:', tone: 'info' })
  }

  const apply = () => {
    const { patch, error } = parseConfig(draft)
    if (error) {
      setStatus({ message: error, tone: 'error' })
      return
    }

    update(patch)
    setDraft('')
    setStatus({ message: `Applied ${Object.keys(patch).length} setting(s).`, tone: 'info' })
  }

  return (
    <section className="panel">
      <h2>Share</h2>
      <p className="panel__hint">
        Everything travels in the URL — there is nothing to upload and nothing kept.
      </p>

      <div className="row" style={{ flexWrap: 'wrap' }}>
        <button type="button" className="button" onClick={share} disabled={busy}>
          {busy ? 'Building…' : 'Copy link'}
        </button>
        <button type="button" className="button" onClick={copyConfigurationLink}>
          Copy readable link
        </button>
      </div>

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

      <div className="field">
        <label className="field__label" htmlFor="configuration">Configuration</label>
        <p className="field__note" style={{ margin: '0 0 6px' }}>
          The current lockup as JSON. Paste one in and press Apply — the field names are the ones in{' '}
          <a href={`${import.meta.env.BASE_URL}capabilities.json`}>capabilities.json</a>.
        </p>
        <textarea
          id="configuration"
          className="configuration"
          rows={9}
          spellCheck="false"
          value={draft || configuration}
          onChange={(event) => setDraft(event.target.value)}
          onFocus={(event) => { if (!draft) event.target.select() }}
        />
        <div className="row" style={{ marginTop: 8 }}>
          <button type="button" className="button" onClick={apply} disabled={!draft}>Apply</button>
          <button type="button" className="button button--ghost" onClick={copyConfiguration}>Copy JSON</button>
          {draft && (
            <button type="button" className="button button--ghost" onClick={() => setDraft('')}>Discard</button>
          )}
        </div>
      </div>

      <p className="export__status" data-tone={status.tone} role="status" aria-live="polite">
        {status.message}
      </p>
    </section>
  )
}
