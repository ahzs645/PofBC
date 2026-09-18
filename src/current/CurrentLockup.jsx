// Shows one of the Province's current ministry marks.
//
// Unlike the historical lockup, which is drawn from parts on every render, this fetches a finished
// file. That means it has states the other never has — loading, and failing to load — and they are
// shown rather than swallowed, because a blank frame with no explanation is the worst outcome.

import { useEffect, useState } from 'react'
import { loadCatalogue, loadMark, markSize, renderCurrentSvg } from './currentMarks.js'

/** The catalogue of ministries, loaded once. */
export const useCurrentCatalogue = () => {
  const [state, setState] = useState({ status: 'loading' })

  useEffect(() => {
    let cancelled = false

    loadCatalogue()
      .then((catalogue) => !cancelled && setState({ status: 'ready', catalogue }))
      .catch((error) => !cancelled && setState({ status: 'error', message: error.message }))

    return () => { cancelled = true }
  }, [])

  return state
}

/** One ministry's artwork, loaded when the ministry or language changes. */
export const useCurrentMark = (code, language) => {
  const [state, setState] = useState({ status: 'loading' })

  useEffect(() => {
    let cancelled = false
    setState({ status: 'loading' })

    loadMark(code, language)
      .then((source) => !cancelled && setState({ status: 'ready', source }))
      .catch((error) => !cancelled && setState({ status: 'error', message: error.message }))

    return () => { cancelled = true }
  }, [code, language])

  return state
}

/**
 * @param {object} props
 * @param {string} props.code        Ministry abbreviation, e.g. 'FOR'.
 * @param {string} props.language    'en' | 'fr'
 * @param {string} props.variant     One of the four official colourways.
 * @param {string} [props.background]
 * @param {number} [props.clearSpaceFactor]  Margin as a fraction of the mark's own width.
 * @param {string} [props.title]     Accessible name.
 */
export const CurrentLockup = ({ code, language, variant, background, clearSpaceFactor = 0, title, ...rest }) => {
  const mark = useCurrentMark(code, language)

  if (mark.status === 'loading') {
    return <p className="stage__message" role="status">Loading the official artwork…</p>
  }

  if (mark.status === 'error') {
    return <p className="stage__message" data-tone="error" role="status">{mark.message}</p>
  }

  const { width, height } = markSize(mark.source)
  const padding = clearSpaceFactor * width
  const svg = renderCurrentSvg({ source: mark.source, variant, background, padding, title })

  return (
    <div
      className="current-lockup"
      style={{ aspectRatio: `${width + padding * 2} / ${height + padding * 2}` }}
      role="img"
      aria-label={title}
      // The artwork is a static file this project generated and serves from its own origin; there
      // is no author-supplied content anywhere in it.
      dangerouslySetInnerHTML={{ __html: svg }}
      {...rest}
    />
  )
}
