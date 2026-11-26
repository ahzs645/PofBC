import { useEffect, useLayoutEffect, useState } from 'react'
import { INITIATIVES, initiativeById, loadInitiative } from './initiatives.js'
import { InitiativeDetail } from './InitiativeDetail.jsx'
import { initiativePlaceUrl, readInitiativePlace } from './initiativePlace.js'
import { searchInitiatives } from './initiativeModel.js'
import { writeHistory } from '../site/browserHistory.js'
import { SiteLink } from '../site/navigation.jsx'
import { documentTitle, setDocumentMeta } from '../site/documentMeta.js'
import { useCatalogueIndex } from '../site/useCatalogueIndex.js'
import { useSiteTheme } from '../site/useTheme.js'
import { COLLECTED_DISPLAY } from '../gallery/collectedDisplay.js'
import './initiatives.css'

const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
const coverUrl = (file) => `${import.meta.env.BASE_URL}${file.replace(/^\//, '')}`
const Forward = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M3 10h13m-5-5 5 5-5 5" stroke="currentColor" strokeWidth="1.4" /></svg>
const INDEX_DESCRIPTION = 'Explore British Columbia’s public programs, campaigns and services through their websites, identities, publications and source records.'

export const InitiativesView = () => {
  const [place, setPlace] = useState(() => readInitiativePlace())
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const { name: theme } = useSiteTheme()
  const { cards, query, setQuery, openCard, closeCard } = useCatalogueIndex('initiatives')
  const initiative = initiativeById(place.initiative)
  const parent = initiativeById(initiative?.parentId)

  useLayoutEffect(() => {
    const saved = globalThis.history?.state?.catalogueIndex
    if (!place.initiative && saved?.view === 'initiatives') cards.current[saved.card]?.focus()
  }, [place.initiative, cards])

  useEffect(() => {
    const restore = () => setPlace(readInitiativePlace())
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [])

  useEffect(() => {
    let cancelled = false
    setDetail(null)
    setError(false)
    if (initiative) loadInitiative(initiative.id).then((value) => {
      if (!cancelled) setDetail(value)
    }).catch(() => { if (!cancelled) setError(true) })
    return () => { cancelled = true }
  }, [initiative, attempt])

  useEffect(() => {
    setDocumentMeta({
      title: documentTitle(initiative?.title, 'Initiatives'),
      description: initiative?.summary ?? INDEX_DESCRIPTION
    })
  }, [initiative])

  const open = (event, id) => {
    if (!plainClick(event)) return
    event.preventDefault()
    openCard(initiativePlaceUrl(location.href, { initiative: id }), id)
    setPlace(readInitiativePlace())
    globalThis.scrollTo?.({ top: 0 })
  }

  const back = (event) => {
    if (!plainClick(event)) return
    event.preventDefault()
    closeCard(place.initiative, () => {
      writeHistory(initiativePlaceUrl(location.href))
      setPlace(readInitiativePlace())
      globalThis.scrollTo?.({ top: 0 })
    })
  }

  const changeSection = (section, record = null, page = null) => {
    writeHistory(initiativePlaceUrl(location.href, { initiative: initiative.id, section, record, page }), { replace: true })
    setPlace(readInitiativePlace())
  }

  if (place.initiative) return <main className="initiatives">
    <nav className="initiatives__breadcrumbs" aria-label="Initiative breadcrumb">
      <a href="?view=initiatives" onClick={back}>All initiatives</a><span aria-hidden="true">/</span>
      {parent && <><SiteLink to={{ view: 'initiatives', initiative: parent.id }}>{parent.title}</SiteLink><span aria-hidden="true">/</span></>}
      <span aria-current="page">{initiative?.title ?? 'Unknown initiative'}</span>
    </nav>
    {!initiative ? <div className="initiatives__empty"><h2>Initiative not found</h2><p>This initiative is not in the catalogue. Browse the available initiatives using the link above.</p></div>
      : error ? <div className="initiatives__empty" role="alert"><h2>The initiative could not load</h2><p>Please try again.</p><button type="button" onClick={() => setAttempt((value) => value + 1)}>Try again</button></div>
        : detail?.id === initiative.id ? <InitiativeDetail key={detail.id} initiative={detail} subInitiatives={INITIATIVES.filter((entry) => entry.parentId === detail.id)} place={place} onChange={changeSection} />
          : <p className="initiatives__loading" role="status">Loading {initiative.title}…</p>}
  </main>

  const results = searchInitiatives(query, INITIATIVES)
  return <main className="initiatives">
    <div className="initiatives__toolbar">
      <div><h3>Explore initiatives</h3><p aria-live="polite">{results.length} {results.length === 1 ? 'initiative' : 'initiatives'}{query.trim() ? ' matching your search' : ' in the collection'}</p></div>
      <label className="initiatives__search"><span className="initiatives__sr-only">Search initiatives</span><input type="search" placeholder="Search initiatives or programs" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
    </div>
    <div className="initiatives__grid" data-single={results.length === 1}>
      {results.map((entry) => <a key={entry.id} className="initiatives__card" href={`?view=initiatives&initiative=${encodeURIComponent(entry.id)}`} onClick={(event) => open(event, entry.id)} ref={(element) => { cards.current[entry.id] = element }}>
        <div className="initiatives__card-copy">
          <p className="initiatives__eyebrow">{entry.subtitle}</p><h3>{entry.title}</h3><p>{entry.summary}</p>
          {entry.tags?.length > 0 && <ul className="initiatives__tags" aria-label="Available material">{entry.tags.map((tag) => <li key={tag}>{tag}</li>)}</ul>}
          <span className="initiatives__explore">Explore initiative <Forward /></span>
        </div>
        {entry.cover && <figure className="initiatives__cover" data-themed={entry.cover.displayId ? true : undefined}>
          <img src={coverUrl(COLLECTED_DISPLAY[entry.cover.displayId]?.[theme]?.file ?? entry.cover.file)} alt={entry.cover.alt} />
          <figcaption>{entry.cover.caption}</figcaption>
        </figure>}
      </a>)}
    </div>
    {!results.length && <div className="initiatives__empty"><h3>No matching initiatives</h3><p>Try a program, campaign or organization name.</p><button type="button" onClick={() => setQuery('')}>Show all initiatives</button></div>}
    <aside className="initiatives__about"><h3>One initiative, a connected history.</h3><p>Websites, campaign artwork and publications belong together. Each collection keeps the original material alongside its dates, sources and related organizations.</p></aside>
  </main>
}
