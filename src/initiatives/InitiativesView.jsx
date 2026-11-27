import { useEffect, useLayoutEffect, useState } from 'react'
import { Breadcrumbs } from '../site/Breadcrumbs.jsx'
import { INITIATIVES, initiativeAncestors, initiativeById, initiativeParts, loadInitiative } from './initiatives.js'
import { InitiativeDetail } from './InitiativeDetail.jsx'
import { initiativePlaceUrl, readInitiativePlace } from './initiativePlace.js'
import { indexGroups, searchInitiatives } from './initiativeModel.js'
import { InitiativeParts, coverFile, coverUrl } from './InitiativeParts.jsx'
import { writeHistory } from '../site/browserHistory.js'
import { SiteLink } from '../site/navigation.jsx'
import { documentTitle, setDocumentMeta } from '../site/documentMeta.js'
import { useCatalogueIndex } from '../site/useCatalogueIndex.js'
import { useSiteTheme } from '../site/useTheme.js'
import './initiatives.css'

const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
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
  const ancestors = initiative ? initiativeAncestors(initiative.id) : []

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
    <Breadcrumbs label="Initiatives" steps={[
      { label: 'All initiatives', href: '?view=initiatives', onClick: back },
      ...ancestors.map((program) => ({ label: program.title, to: { view: 'initiatives', initiative: program.id } })),
      { label: initiative?.title ?? 'Unknown initiative' }
    ]} />
    {!initiative ? <div className="initiatives__empty"><h2>Initiative not found</h2><p>This initiative is not in the catalogue. Browse the available initiatives using the link above.</p></div>
      : error ? <div className="initiatives__empty" role="alert"><h2>The initiative could not load</h2><p>Please try again.</p><button type="button" onClick={() => setAttempt((value) => value + 1)}>Try again</button></div>
        : detail?.id === initiative.id ? <InitiativeDetail key={detail.id} initiative={detail} entry={initiative} parent={ancestors.at(-1)} parts={initiativeParts(initiative.id)} place={place} onChange={changeSection} />
          : <p className="initiatives__loading" role="status">Loading {initiative.title}…</p>}
  </main>

  const results = searchInitiatives(query, INITIATIVES)
  const groups = indexGroups(results, INITIATIVES)
  const programs = groups.filter((group) => group.parts.length)
  const singles = groups.filter((group) => !group.parts.length)
  const card = ({ program, matched }) => <a key={program.id} className="initiatives__card" data-context={matched ? undefined : true}
    href={`?view=initiatives&initiative=${encodeURIComponent(program.id)}`} onClick={(event) => open(event, program.id)} ref={(element) => { cards.current[program.id] = element }}>
    <div className="initiatives__card-copy">
      <p className="initiatives__eyebrow">{program.subtitle}</p><h3>{program.title}</h3><p>{program.summary}</p>
      {program.tags?.length > 0 && <ul className="initiatives__tags" aria-label="Available material">{program.tags.map((tag) => <li key={tag}>{tag}</li>)}</ul>}
      <span className="initiatives__explore">Explore initiative <Forward /></span>
    </div>
    {program.cover && <figure className="initiatives__cover">
      <span className="initiatives__art" data-themed={coverFile(program.cover, theme) !== program.cover.file ? true : undefined} data-dark={program.cover.darkBackground ? true : undefined}>
        <img src={coverUrl(coverFile(program.cover, theme))} alt={program.cover.alt} />
      </span>
      <figcaption>{program.cover.caption}</figcaption>
    </figure>}
  </a>
  return <main className="initiatives">
    <div className="initiatives__toolbar">
      <div><h3>Explore initiatives</h3><p aria-live="polite">{results.length} {results.length === 1 ? 'initiative' : 'initiatives'}{query.trim() ? ' matching your search' : ' in the collection'}</p></div>
      <label className="initiatives__search"><span className="initiatives__sr-only">Search initiatives</span><input type="search" placeholder="Search initiatives or programs" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
    </div>
    {programs.map((group) => <article key={group.program.id} className="initiatives__program" aria-label={group.program.title}>
      {card(group)}
      <InitiativeParts program={group.program} parts={group.parts} theme={theme} onOpen={open} linkRef={(id) => (element) => { cards.current[id] = element }} />
    </article>)}
    {singles.length > 0 && <div className="initiatives__grid" data-single={singles.length === 1 && !programs.length}>{singles.map(card)}</div>}
    {!results.length && <div className="initiatives__empty"><h3>No matching initiatives</h3><p>Try a program, campaign or organization name.</p><button type="button" onClick={() => setQuery('')}>Show all initiatives</button></div>}
    <aside className="initiatives__about"><h3>One initiative, a connected history.</h3><p>Websites, campaign artwork and publications belong together. Each collection keeps the original material alongside its dates, sources and related organizations. A program’s campaigns, events and sub-programs are listed beneath it and keep pages of their own.</p></aside>
  </main>
}
