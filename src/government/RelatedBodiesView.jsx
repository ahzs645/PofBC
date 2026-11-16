import { useMemo, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { ViewSwitcher } from '../site/ViewSwitcher.jsx'
import { SunGlyph, ThemeIcon } from '../site/icons.jsx'
import { LogoCard } from './LogoCard.jsx'
import { RELATED_BODIES_AS_OF, RELATED_BODY_KINDS, relatedBodyById, relatedBodyPlace, searchRelatedBodies } from './relatedBodies.js'
import './relatedBodies.css'

/** Current regional and independent organizations, connected without assigning them to a ministry. */
export const RelatedBodiesView = ({ selectedId, onChangeView, themeName, onToggleTheme }) => {
  const [query, setQuery] = useState('')
  const bodies = useMemo(() => searchRelatedBodies(query), [query])
  const selected = relatedBodyById(selectedId)
  return (
    <div className="gov gov-related" data-theme={themeName}>
      <nav className="gov-card gov-breadcrumb" aria-label="Breadcrumb">
        <SunGlyph fill={themeName === 'dark' ? '#fcba19' : '#e8a412'} />
        <strong className="gov-breadcrumb__site">Province of BC</strong>
        <span className="gov-muted" aria-hidden="true">/</span>
        <ViewSwitcher view="government" onChange={onChangeView} className="gov-breadcrumb__views" />
        <span className="gov-muted">/ Related bodies</span>
        <button className="gov-button gov-button--icon" type="button" onClick={onToggleTheme} aria-label={`Switch to ${themeName === 'dark' ? 'light' : 'dark'} mode`}>
          <ThemeIcon name={themeName} />
        </button>
      </nav>

      <header className="gov-card gov-related__intro">
        <p className="gov-eyebrow">Current catalogue · checked {RELATED_BODIES_AS_OF}</p>
        <h1 className="gov-title">Related public bodies</h1>
        <p className="gov-description">Regional authorities, operating companies, public institutions and independent organizations connected to the identity collection. Each record describes its own role and governance.</p>
        <p className="gov-links"><SiteLink to={{ view: 'government' }}>Open the provincial government timeline →</SiteLink></p>
      </header>

      <section className="gov-card gov-related__directory" aria-label="Related public bodies directory">
        <label htmlFor="related-body-search" className="gov-card__heading">Find an organization</label>
        <input id="related-body-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="TransLink, Metro Vancouver, UNBC…" />
        <p className="gov-muted" role="status">{bodies.length} {bodies.length === 1 ? 'organization' : 'organizations'}</p>
        <ul className="gov-related__list">
          {bodies.map((body) => (
            <li key={body.id}>
              <SiteLink to={relatedBodyPlace(body.id)} aria-current={body.id === selectedId ? 'page' : undefined}>
                <strong>{body.shortName ?? body.name}</strong>
                <span>{RELATED_BODY_KINDS[body.kind]}</span>
              </SiteLink>
            </li>
          ))}
        </ul>
        {!bodies.length && <p className="gov-muted">No matching organization in this catalogue.</p>}
      </section>

      <div className="gov-related__detail" aria-live="polite">
        {selected ? <>
          <section className="gov-card" aria-labelledby="related-body-title">
            <p className="gov-eyebrow">{RELATED_BODY_KINDS[selected.kind]} · current record</p>
            <h2 className="gov-title" id="related-body-title">{selected.name}</h2>
            {selected.shortName !== selected.name && <p className="gov-muted">{selected.shortName}</p>}
            <p className="gov-description">{selected.description}</p>
            {selected.historyNote && <p className="gov-muted">{selected.historyNote}</p>}
            <p className="gov-links"><a href={selected.officialUrl} target="_blank" rel="noreferrer">Official website →</a></p>
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
        </> : <section className="gov-card">
          <h2 className="gov-title">Choose an organization</h2>
          <p className="gov-description">Open a record to see its identity collection, institutional relationships and any salary disclosures already held here.</p>
          <p className="gov-muted">These current records have their own classifications. They are not placed within the provincial executive or treated as historical government snapshots.</p>
        </section>}
      </div>
    </div>
  )
}
