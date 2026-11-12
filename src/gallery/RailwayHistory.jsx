import { useEffect, useRef } from 'react'
import { assetUrl } from './collectedCollections.js'

const SECTION_IDS = ['railway-history', 'railway-connections', 'railway-evidence']
const EVIDENCE_LABELS = {
  proposal: 'Proposed design · not adopted',
  'decorative-context': 'Decorative illustration · not an adopted logo'
}

const revealSection = (section) => {
  const details = section.closest('details.gallery__railway-more')
  if (details) details.open = true
  section.focus({ preventScroll: true })
  section.scrollIntoView({ block: 'start' })
}

/** Section changes edit this gallery page's URL, without adding a route-history entry. */
const followSectionLink = (event) => {
  // Keep the real href usable for copy link, new tab/window, and other modified clicks.
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
  if (event.currentTarget.target && event.currentTarget.target !== '_self') return
  const id = event.currentTarget.hash.slice(1)
  if (!SECTION_IDS.includes(id) || !globalThis.history?.replaceState) return
  const section = document.getElementById(id)
  if (!section) return
  event.preventDefault()
  const url = new URL(globalThis.location.href)
  url.hash = id
  globalThis.history.replaceState(globalThis.history.state, '', url)
  revealSection(section)
}

/** Dates remain the source's wording, including approximate dates and periods. */
const Sources = ({ sources }) => sources?.length > 0 && (
  <p className="gallery__sources">
    <span>Sources:</span>{' '}
    {sources.map((source, index) => (
      <span key={`${source.url}-${index}`}>
        {index > 0 && '; '}
        <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
        {source.locator && <span className="gallery__sources-locator">, {source.locator}</span>}
      </span>
    ))}
  </p>
)

/** Make the history beneath the logo groups easy to find, especially on a phone. */
export const RailwayHistoryLinks = ({ history }) => history && (
  <nav className="gallery__railway-links" aria-label="Railway collection sections">
    <a href="#railway-history" onClick={followSectionLink}>Railway history</a>
    {history.connections?.length > 0 && <a href="#railway-connections" onClick={followSectionLink}>Company connections</a>}
    {history.evidence?.length > 0 && <a href="#railway-evidence" onClick={followSectionLink}>Supporting images</a>}
  </nav>
)

const HistoryContent = ({ history, containerRef }) => (
  <div className="gallery__railway-content" ref={containerRef}>
    <section id="railway-history" className="gallery__railway-section" aria-labelledby="railway-history-heading" tabIndex={-1}>
      <h2 id="railway-history-heading">{history.title}</h2>
      {history.overview && <p className="gallery__railway-overview">{history.overview}</p>}
      <ol className="gallery__railway-events">
        {history.events.map((event) => (
          <li key={event.id}>
            <div className="gallery__railway-event-date">
              <span>{event.date}</span>
              <span className="gallery__railway-kind">{event.kind.replace(/[_-]/g, ' ')}</span>
            </div>
            <div>
              <h3>{event.title}</h3>
              <p>{event.description}</p>
              <Sources sources={event.sources} />
            </div>
          </li>
        ))}
      </ol>
    </section>

    {history.connections?.length > 0 && (
      <section id="railway-connections" className="gallery__railway-section" aria-labelledby="railway-connections-heading" tabIndex={-1}>
        <h2 id="railway-connections-heading">Company connections</h2>
        <ul className="gallery__railway-connections">
          {history.connections.map((connection) => (
            <li key={connection.id}>
              <p className="gallery__railway-connection-route">
                <strong>{connection.from}</strong>
                <span aria-hidden="true">→</span>
                <strong>{connection.to}</strong>
              </p>
              <p className="gallery__railway-connection-type">
                <span>{connection.relationship}</span>
                {connection.date && <span>{connection.date}</span>}
              </p>
              <p>{connection.description}</p>
              <Sources sources={connection.sources} />
            </li>
          ))}
        </ul>
      </section>
    )}

    {history.evidence?.length > 0 && (
      <section id="railway-evidence" className="gallery__railway-section" aria-labelledby="railway-evidence-heading" tabIndex={-1}>
        <h2 id="railway-evidence-heading">Supporting images</h2>
        <div className="gallery__railway-evidence">
          {history.evidence.map((item) => (
            <figure key={item.id}>
              <a className="gallery__railway-image" href={assetUrl(item.file)} target="_blank" rel="noreferrer" aria-label={`Open ${item.label}`}>
                <img src={assetUrl(item.file)} alt={item.label} loading="lazy" />
              </a>
              <figcaption>
                <span className="gallery__railway-kind">{EVIDENCE_LABELS[item.role] ?? 'Historical context'}</span>
                <h3>{item.label}</h3>
                <p>{item.caption}</p>
                <p className="gallery__sources">
                  <a href={item.sourceUrl} target="_blank" rel="noreferrer" aria-label={`View source for ${item.label}`}>View source publication</a>
                  {item.sourceLocator && <span className="gallery__sources-locator"> · {item.sourceLocator}</span>}
                </p>
                <a className="gallery__railway-download" href={assetUrl(item.file)} download aria-label={`Download ${item.label}`}>Download image</a>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>
    )}
  </div>
)

/** The same evidence stays available from a deep link directly to an individual railway mark. */
export const RailwayHistory = ({ history, compact = false }) => {
  const container = useRef(null)
  useEffect(() => {
    if (!history) return
    // The gallery loads lazily, after the browser's initial fragment lookup. Resolve its own
    // section links once mounted and on hash changes, opening the mark page's details if needed.
    const revealFragment = () => {
      const id = globalThis.location?.hash.slice(1)
      if (!SECTION_IDS.includes(id)) return
      const target = container.current?.querySelector(`#${id}`)
      if (!target) return
      revealSection(target)
    }
    revealFragment()
    globalThis.addEventListener?.('hashchange', revealFragment)
    return () => globalThis.removeEventListener?.('hashchange', revealFragment)
  }, [history, compact])

  if (!history) return null
  if (compact) return (
    <details className="gallery__railway-more" ref={container}>
      <summary>Railway history, connections and supporting images</summary>
      <HistoryContent history={history} />
    </details>
  )
  return <HistoryContent history={history} containerRef={container} />
}
