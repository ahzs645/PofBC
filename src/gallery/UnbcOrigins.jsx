import { useEffect, useRef, useState } from 'react'
import { assetUrl } from './collectedCollections.js'
import { IUS_ASSETS, IUS_COLLECTION_ID, IUS_HIGHLIGHTS, IUS_ID, UNBC_ID } from './iusCollectionData.js'
import { UNBC_HISTORY } from './unbcHistoryData.js'
import './unbcOrigins.css'

const SECTIONS = ['unbc-origins', 'unbc-origins-campaign', 'unbc-origins-timeline', 'unbc-origins-sources']
export const hasUnbcOrigins = (id) => [UNBC_ID, IUS_ID].includes(id)
const storyHref = `?view=gallery&subject=${UNBC_ID}#unbc-origins`
const kitUrl = (path) => assetUrl(`unbc-origins/${path}`)
const plainClick = (event) => !event.defaultPrevented && event.button === 0 &&
  !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey

const reveal = (target) => {
  target.focus({ preventScroll: true })
  target.scrollIntoView({ block: 'start' })
}

// Keep native hrefs for copying and modified clicks. Same-page links replace only the fragment.
const followSection = (event) => {
  if (!plainClick(event)) return
  const target = document.getElementById(event.currentTarget.hash.slice(1))
  if (!target || !globalThis.history?.replaceState) return
  event.preventDefault()
  const url = new URL(globalThis.location.href)
  url.hash = target.id
  globalThis.history.replaceState(globalThis.history.state, '', url)
  reveal(target)
}

const Sources = ({ sources }) => <p className="unbc-origins__citations">
  {sources.map((source, index) => <span key={source.id ?? source.url}>
    {index > 0 && ' · '}
    <a href={source.url} target="_blank" rel="noreferrer" title={source.locator}>{source.title}</a>
  </span>)}
</p>

/** A short, shareable route from the UNBC logo and every IUS artwork to the same origin story. */
export const UnbcOriginsLink = ({ local = false, className = 'identity-action', children }) => (
  <a className={className} href={local ? '#unbc-origins' : storyHref} onClick={local ? followSection : undefined}>
    {children ?? 'How UNBC was formed'} <span aria-hidden="true">→</span>
  </a>
)

/** One line from a UNBC or IUS page to the origin story, which is to have a page of its own. */
export const UnbcOriginsTeaser = ({ owner }) => !hasUnbcOrigins(owner) ? null : (
  <p className="unbc-origins-teaser">
    <UnbcOriginsLink className="gallery__graph-link" />
  </p>
)

/**
 * Whether the address asks for the origin story. Until it has a page of its own, a subject page
 * shows it only when its link is followed, rather than under every UNBC and IUS record.
 */
export const useUnbcOriginsRequested = () => {
  const read = () => SECTIONS.includes(globalThis.location?.hash.slice(1) ?? '')
  const [requested, setRequested] = useState(read)
  useEffect(() => {
    const onHash = () => setRequested(read())
    globalThis.addEventListener?.('hashchange', onHash)
    return () => globalThis.removeEventListener?.('hashchange', onHash)
  }, [])
  return requested
}

const Artifact = ({ asset }) => (
  <figure className="unbc-origins__artifact">
    <a className="unbc-origins__artifact-image" href={kitUrl(asset.svg)} target="_blank" rel="noreferrer" aria-label={`Enlarge ${asset.label}`}>
      <img src={kitUrl(asset.svg)} alt={asset.label} width={asset.width} height={asset.height} loading="lazy" />
    </a>
    <figcaption>
      <span className="unbc-origins__status">{asset.status}</span>
      <h4>{asset.label}</h4>
      <p>{asset.note}</p>
      <div className="unbc-origins__asset-links">
        <a href={kitUrl(asset.svg)} download aria-label={`Download ${asset.label} as SVG`}>SVG</a>
        <a href={kitUrl(asset.pdf)} download aria-label={`Download ${asset.label} as PDF`}>PDF</a>
      </div>
    </figcaption>
  </figure>
)

export const UnbcOrigins = ({ contextId = UNBC_ID, onOpenSubject, onChooseCollection }) => {
  const container = useRef(null)
  useEffect(() => {
    // The gallery is lazy-loaded, so a fragment must be resolved after its sections exist.
    const revealFragment = () => {
      const id = globalThis.location?.hash.slice(1)
      if (!SECTIONS.includes(id)) return
      const target = container.current?.querySelector(`#${id}`)
      if (target) reveal(target)
    }
    revealFragment()
    globalThis.addEventListener?.('hashchange', revealFragment)
    return () => globalThis.removeEventListener?.('hashchange', revealFragment)
  }, [contextId])

  const openSubject = (event, id) => {
    if (!onOpenSubject || !plainClick(event)) return
    event.preventDefault()
    onOpenSubject(id)
  }
  const openCollection = (event) => {
    if (!onChooseCollection || !plainClick(event)) return
    event.preventDefault()
    onChooseCollection(IUS_COLLECTION_ID)
  }

  return (
    <div className="unbc-origins" ref={container}>
      <section id="unbc-origins" className="unbc-origins__hero" aria-labelledby="unbc-origins-heading" tabIndex={-1}>
        <div>
          <p className="unbc-origins__eyebrow">UNBC origins / A public campaign</p>
          <h2 id="unbc-origins-heading">{UNBC_HISTORY.title}</h2>
          <p className="unbc-origins__subtitle">{UNBC_HISTORY.subtitle}</p>
          <p className="unbc-origins__lead">{UNBC_HISTORY.lead}</p>
          <nav className="unbc-origins__navigation" aria-label="UNBC origins sections">
            <a href="#unbc-origins-campaign" onClick={followSection}>Campaign artwork</a>
            <a href="#unbc-origins-timeline" onClick={followSection}>1987–1994 timeline</a>
            <a href="#unbc-origins-sources" onClick={followSection}>Sources</a>
          </nav>
        </div>
        <figure className="unbc-origins__hero-art">
          <img src={kitUrl('svg/ius-print-colour.svg')} alt="Interior University Society, with three projecting orange bars" width="1008" height="596" />
          <figcaption>Interior University Society · reconstructed print identity</figcaption>
        </figure>
      </section>

      <div className="unbc-origins__narrative">
        {UNBC_HISTORY.paragraphs.map((paragraph) => <section key={paragraph.id}>
          <h3>{paragraph.heading}</h3>
          <p>{paragraph.text}</p>
          <Sources sources={paragraph.sources} />
        </section>)}
      </div>

      <section className="unbc-origins__connections" aria-labelledby="unbc-origins-connections-heading">
        <div className="unbc-origins__section-head">
          <h3 id="unbc-origins-connections-heading">Connected by a campaign</h3>
          <div className="unbc-origins__record-links">
            <a href={`?view=gallery&subject=${IUS_ID}`} onClick={(event) => openSubject(event, IUS_ID)}>IUS record</a>
            <a href={`?view=gallery&subject=${UNBC_ID}`} onClick={(event) => openSubject(event, UNBC_ID)}>UNBC record</a>
          </div>
        </div>
        <ul>
          {UNBC_HISTORY.connections.map((connection) => <li key={connection.id}>
            <p className="unbc-origins__connection-type">{connection.relationship}</p>
            <h4>{connection.from} <span aria-hidden="true">→</span> {connection.to}</h4>
            <p>{connection.description}</p>
            <Sources sources={connection.sources} />
          </li>)}
        </ul>
      </section>

      <section id="unbc-origins-campaign" aria-labelledby="unbc-origins-campaign-heading" tabIndex={-1}>
        <div className="unbc-origins__section-head">
          <div>
            <p className="unbc-origins__eyebrow">The campaign in print and objects</p>
            <h3 id="unbc-origins-campaign-heading">Making a future university visible</h3>
          </div>
          <a className="button" href={kitUrl('ius-vector-brand-kit-v1.2.zip')} download>Download vector kit</a>
        </div>
        <p className="unbc-origins__artwork-note">These modern reconstructions come from the supplied version 1.2 kit. The captions distinguish reconstructed objects, re-typeset documents and interpretive artwork. Original fonts, exact colours and physical dimensions remain unconfirmed.</p>
        <div className="unbc-origins__artifacts">{IUS_HIGHLIGHTS.map((asset) => <Artifact key={asset.id} asset={asset} />)}</div>
        <div className="unbc-origins__download-note">
          <p><strong>All {IUS_ASSETS.length} designs.</strong> The download includes SVG, PDF and EPS artwork, palettes, authoring sources and reconstruction notes. The Northern U button retains the corrected capital N from version 1.2.</p>
          <div className="unbc-origins__asset-links">
            <a href={`?view=gallery&logos=${IUS_COLLECTION_ID}`} onClick={openCollection}>Browse all {IUS_ASSETS.length} designs →</a>
            <a href={kitUrl('README.md')} target="_blank" rel="noreferrer">Reconstruction notes</a>
            <a href={kitUrl('FONT_NOTES.md')} target="_blank" rel="noreferrer">Font review notes</a>
          </div>
        </div>
      </section>

      <section id="unbc-origins-timeline" className="unbc-origins__timeline" aria-labelledby="unbc-origins-timeline-heading" tabIndex={-1}>
        <p className="unbc-origins__eyebrow">From organising to opening</p>
        <h3 id="unbc-origins-timeline-heading">How UNBC came into being</h3>
        <ol>
          {UNBC_HISTORY.events.map((event) => <li key={event.id}>
            <p className="unbc-origins__event-date">{event.date}</p>
            <div><h4>{event.title}</h4><p>{event.description}</p><Sources sources={event.sources} /></div>
          </li>)}
        </ol>
      </section>

      <section id="unbc-origins-sources" className="unbc-origins__sources" aria-labelledby="unbc-origins-sources-heading" tabIndex={-1}>
        <h3 id="unbc-origins-sources-heading">Sources and further reading</h3>
        <ul>{UNBC_HISTORY.sources.map((source) => <li key={source.id}>
          <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
          <p>{source.locator}</p>
        </li>)}</ul>
        <p>The artwork dates follow the objects: the invitation bears 8 June 1988. Archive accession 1992.2 identifies a collection; it does not date the design of the logo. Historical campaign wording and original designs retain their respective ownership.</p>
      </section>
    </div>
  )
}
