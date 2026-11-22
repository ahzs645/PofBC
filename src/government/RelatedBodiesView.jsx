import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { ViewSwitcher } from '../site/ViewSwitcher.jsx'
import { SunGlyph, ThemeIcon } from '../site/icons.jsx'
import { LogoCard } from './LogoCard.jsx'
import {
  RELATED_BODIES, RELATED_BODIES_AS_OF, RELATED_BODY_KINDS, groupRelatedBodies, relatedBodyById, relatedBodyPlace, searchRelatedBodies
} from './relatedBodies.js'
import './relatedBodies.css'

const LIST_PLACE = { view: 'government', mode: 'related' }
// What gives way, in order, when the breadcrumb is too narrow for the page's own name.
const FOLD_STEPS = ['list', 'view', 'sun', 'site']

const Chevron = () => (
  <svg className="gov-related__chevron" width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
    <path d="M5.5 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

/**
 * Current regional and independent organizations, connected without assigning them to a ministry.
 *
 * Laid out as the government view is: on a wide screen the breadcrumb and the directory share the
 * left column, and the chosen record (or, with none, what the catalogue is) fills the right. On a
 * phone the record comes first, then the directory, whole, with no box of its own to scroll.
 */
export const RelatedBodiesView = ({ selectedId, onChangeView, themeName, onToggleTheme }) => {
  const [query, setQuery] = useState('')
  const bodies = useMemo(() => searchRelatedBodies(query), [query])
  const groups = useMemo(() => groupRelatedBodies(bodies), [bodies])
  const selected = relatedBodyById(selectedId)
  const top = useRef(null)

  // The breadcrumb reads from the left as far as there is room, and the page it names must stay
  // readable. While its name would be cut, the trail folds one step at a time: the list's crumb to
  // "…", then the view's name (one "…" then stands for both; the record's "All related bodies" link
  // is the way back), then the sun, and last the site's name takes the ellipsis instead — but only
  // if that makes the page's name whole; a name too long for any room keeps the site's name beside
  // it. Measured, since names run from "UBC" to "Coast Mountain Bus Company".
  const crumbs = useRef(null)
  const [fold, setFold] = useState(0)
  const [settled, setSettled] = useState(false)
  const steps = selected ? FOLD_STEPS : FOLD_STEPS.slice(1)
  const refold = () => { setFold(0); setSettled(false) }
  useLayoutEffect(refold, [selectedId])
  useLayoutEffect(() => {
    const nav = crumbs.current
    const page = nav?.querySelector('.gov-breadcrumb__page')
    if (settled || !page) return
    // It fits when the page's name is whole and nothing is pushed out of the card.
    if (page.scrollWidth <= page.clientWidth + 1 && nav.scrollWidth <= nav.clientWidth + 1) setSettled(true)
    else if (fold < steps.length) setFold(fold + 1)
    else { setFold(steps.length - 1); setSettled(true) }
  }, [fold, settled, steps.length, selectedId])
  useEffect(() => {
    const nav = crumbs.current
    if (!nav || typeof ResizeObserver === 'undefined') return undefined
    let width = nav.clientWidth
    const observer = new ResizeObserver(() => {
      if (nav.clientWidth === width) return
      width = nav.clientWidth
      refold()
    })
    observer.observe(nav)
    return () => observer.disconnect()
  }, [])
  const folded = steps.slice(0, fold)
  const foldList = folded.includes('list')
  const foldView = folded.includes('view')
  const showList = Boolean(selected) && !(foldList && foldView)

  // Choosing a body from far down the list on a phone would leave its record above, out of sight.
  const first = useRef(true)
  useEffect(() => {
    if (first.current) { first.current = false; return }
    if (top.current && top.current.getBoundingClientRect().top < 0) top.current.scrollIntoView({ block: 'start' })
  }, [selectedId])

  return (
    <div className="gov gov-related" data-theme={themeName} data-selected={selected ? '' : undefined} ref={top}>
      <nav className="gov-card gov-breadcrumb" aria-label="Breadcrumb" ref={crumbs} data-fold={folded.join(' ') || undefined}>
        <SunGlyph fill={themeName === 'dark' ? '#fcba19' : '#e8a412'} />
        <strong className="gov-breadcrumb__site">Province of BC</strong>
        <span className="gov-muted" aria-hidden="true">/</span>
        <ViewSwitcher view="government" onChange={onChangeView} className="gov-breadcrumb__views" compact={foldView} />
        <span className="gov-muted" aria-hidden="true">/</span>
        {selected ? <>
          {showList && <>
          <SiteLink className="gov-breadcrumb__parent" to={LIST_PLACE} aria-label={foldList ? 'Related bodies' : undefined} title="All related bodies">
            {foldList ? '…' : 'Related bodies'}
          </SiteLink>
          <span className="gov-muted" aria-hidden="true">/</span>
          </>}
          <span className="gov-breadcrumb__page" aria-current="page" title={selected.name}>{selected.shortName ?? selected.name}</span>
        </> : <span className="gov-breadcrumb__page" aria-current="page">Related bodies</span>}
        <span className="gov-breadcrumb__tools">
          <button className="gov-button gov-button--icon" type="button" onClick={onToggleTheme} aria-label={`Switch to ${themeName === 'dark' ? 'light' : 'dark'} mode`}>
            <ThemeIcon name={themeName} />
          </button>
        </span>
      </nav>

      <main className="gov-related__main" aria-live="polite">
        {selected ? <>
          <section className="gov-card gov-related__record" aria-labelledby="related-body-title">
            <SiteLink className="gov-related__back" to={LIST_PLACE}>← All related bodies</SiteLink>
            <p className="gov-eyebrow">{RELATED_BODY_KINDS[selected.kind]} · current record</p>
            <h1 className="gov-title" id="related-body-title">{selected.name}</h1>
            {selected.shortName !== selected.name && <p className="gov-muted">{selected.shortName}</p>}
            <p className="gov-description">{selected.description}</p>
            {selected.historyNote && <p className="gov-muted">{selected.historyNote}</p>}
            {selected.schoolDistrict && <p className="gov-links"><SiteLink to={{ view: 'school-districts', district: selected.schoolDistrict }}>District history, predecessor connections and logos →</SiteLink></p>}
            <p className="gov-links"><a href={selected.officialUrl} target="_blank" rel="noreferrer">Official website ↗</a></p>
          </section>

          <LogoCard node={selected} theme={themeName} />

          {selected.relationships.length > 0 && <section className="gov-card" aria-labelledby="related-connections">
            <h2 className="gov-card__heading" id="related-connections">Connections</h2>
            <ul className="gov-related__connections">
              {selected.relationships.map((connection) => <li key={connection.id}>
                {relatedBodyById(connection.id)
                  ? <SiteLink to={relatedBodyPlace(connection.id)}>{connection.label}</SiteLink>
                  : <SiteLink to={{ view: 'government', node: connection.id, year: connection.year, mode: connection.mode }}>{connection.label}</SiteLink>}
                <span className="gov-muted">{connection.description}</span>
              </li>)}
            </ul>
          </section>}

          {selected.salaryEmployers.length > 0 && <section className="gov-card" aria-labelledby="related-salaries">
            <h2 className="gov-card__heading" id="related-salaries">Salary disclosures</h2>
            <p className="gov-muted">Open the existing employer records with their reporting periods and original sources.</p>
            <ul className="gov-related__connections">
              {selected.salaryEmployers.map((entry) => <li key={entry.slug}>
                <SiteLink to={{ view: 'salaries', employer: entry.slug }}>{entry.label} →</SiteLink>
              </li>)}
            </ul>
            {selected.salaryNote && <p className="gov-muted">{selected.salaryNote}</p>}
          </section>}

          <section className="gov-card" aria-labelledby="related-sources">
            <h2 className="gov-card__heading" id="related-sources">Sources</h2>
            <p className="gov-muted">Organization descriptions checked {selected.checked}. The provincial timeline does not yet reconstruct the history of these bodies.</p>
            <ul className="gov-related__sources">
              {selected.sources.map((item) => <li key={item.url}><a href={item.url} target="_blank" rel="noreferrer">{item.title}</a></li>)}
            </ul>
          </section>
        </> : <header className="gov-card gov-related__intro">
          <p className="gov-eyebrow">Current catalogue · checked {RELATED_BODIES_AS_OF}</p>
          <h1 className="gov-title">Related public bodies</h1>
          <p className="gov-description">Regional authorities, operating companies, public institutions and independent organizations connected to the identity collection. Each record describes its own role and governance.</p>
          <p className="gov-links"><SiteLink to={{ view: 'government' }}>Open the provincial government timeline →</SiteLink></p>
        </header>}
      </main>

      <section className="gov-card gov-related__directory" aria-labelledby="related-directory-title">
        <div className="gov-related__directory-head">
          <h2 className="gov-card__heading" id="related-directory-title">{selected ? 'All related bodies' : 'Find an organization'}</h2>
          <span className="gov-muted gov-related__count" role="status">
            {query ? `${bodies.length} of ${RELATED_BODIES.length}` : RELATED_BODIES.length}
          </span>
        </div>
        <input
          className="gov-related__search"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="TransLink, Metro Vancouver, UNBC…"
          aria-label="Find an organization"
          autoComplete="off"
        />
        <div className="gov-related__groups">
          {groups.map((group) => (
            <section key={group.id} className="gov-related__group" aria-labelledby={`related-group-${group.id}`}>
              <h3 className="gov-related__group-title" id={`related-group-${group.id}`}>{group.label}</h3>
              <ul className="gov-related__list">
                {group.bodies.map((body) => (
                  <li key={body.id}>
                    <SiteLink className="gov-related__item" to={relatedBodyPlace(body.id)} aria-current={body.id === selectedId ? 'page' : undefined}>
                      <span className="gov-related__name">
                        <strong>{body.shortName ?? body.name}</strong>
                        <span>{RELATED_BODY_KINDS[body.kind]}</span>
                      </span>
                      <Chevron />
                    </SiteLink>
                  </li>
                ))}
              </ul>
            </section>
          ))}
          {!bodies.length && <p className="gov-muted gov-related__empty">No organization in this catalogue matches “{query.trim()}”.</p>}
        </div>
      </section>
    </div>
  )
}
