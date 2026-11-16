import { useState } from 'react'
import {
  COVERAGE_FAMILIES, COVERAGE_STATES, IDENTITY_COVERAGE, coverageSummary, familyById,
  filterIdentityCoverage, identitySubjectById, subjectsForCollection
} from './identityCoverage.js'
import { galleryPlaceUrl, readCoverageFilters } from './galleryPlace.js'
import { writeHistory } from '../site/browserHistory.js'
import { tileArt } from './tileArt.js'
import { entriesOf } from './collections.js'
import { IDENTITY_KIND_LABELS, IDENTITY_RELATION_LABELS } from './identitySubjects.js'
import './identityCoverage.css'

const Status = ({ subject }) => (
  <span className="identity-status" data-held={subject.hasArtwork || undefined} title={COVERAGE_STATES[subject.state].description}>
    {subject.stateLabel}
  </span>
)

const SubjectButton = ({ subject, onOpen }) => (
  <button type="button" className="identity-subject-link" onClick={() => onOpen(subject.id)}>
    <span>{subject.label}</span><Status subject={subject} /><span aria-hidden="true">→</span>
  </button>
)

export const IdentitySearchResults = ({ subjects, onOpen }) => subjects.length > 0 && (
  <section className="gallery__shelf" aria-labelledby="search-identities">
    <h2 id="search-identities" className="gallery__shelf-title">{subjects.length} identity {subjects.length === 1 ? 'subject' : 'subjects'}</h2>
    <p className="gallery__note">Organizations, services and historical names, including those whose artwork is still sought.</p>
    <div className="identity-subject-links">
      {subjects.map((subject) => <SubjectButton key={subject.id} subject={subject} onOpen={onOpen} />)}
    </div>
  </section>
)

export const IdentityCoverageOverview = ({ onOpenRegister, onOpenSubject }) => {
  const summary = coverageSummary()
  const featured = ['translink', 'metro-vancouver', 'liquor-distribution-branch', 'creative-bc'].map(identitySubjectById).filter(Boolean)
  return (
    // One line above the shelves: the marks are what the page is for, so the register is a way in
    // from it, not a banner over it.
    <section className="identity-overview" aria-labelledby="identity-overview-heading">
      <h2 id="identity-overview-heading" className="identity-overview__title">Collection register</h2>
      <p className="identity-overview__counts" title="Regional transit, public agencies, service brands and institutions, alongside the Crown and health collections: their relationships, sources and remaining gaps.">
        <strong>{summary.subjects}</strong> subjects · <strong>{summary.held}</strong> with artwork · <strong>{summary.sources}</strong> leads
      </p>
      <div className="identity-featured">
        {featured.map((subject) => <button type="button" key={subject.id} onClick={() => onOpenSubject(subject.id)}>{subject.label} <span aria-hidden="true">↗</span></button>)}
      </div>
      <button type="button" className="identity-primary" onClick={() => onOpenRegister()}>Browse the register <span aria-hidden="true">→</span></button>
    </section>
  )
}

export const IdentityCoverageBrowser = ({ onHome, onOpenSubject }) => {
  const [filters, setFilters] = useState(() => {
    const initial = readCoverageFilters()
    return {
      query: initial.query,
      family: COVERAGE_FAMILIES.some((family) => family.id === initial.family) ? initial.family : '',
      state: ['held', 'missing', ...Object.keys(COVERAGE_STATES)].includes(initial.state) ? initial.state : '',
      scope: ['core', 'institution'].includes(initial.scope) ? initial.scope : ''
    }
  })
  const update = (patch) => {
    const next = { ...filters, ...patch }
    setFilters(next)
    if (globalThis.location) writeHistory(galleryPlaceUrl(globalThis.location.href, { coverage: true, filters: next }), { replace: true })
  }
  const subjects = filterIdentityCoverage(IDENTITY_COVERAGE, filters)
  const summary = coverageSummary(subjects)
  const family = familyById(filters.family)
  const groups = COVERAGE_FAMILIES.map((group) => ({ ...group, subjects: subjects.filter((subject) => subject.family === group.id) })).filter((group) => group.subjects.length)
  return (
    <div className="identity-register">
      <nav className="gallery__crumbs" aria-label="Gallery"><button type="button" className="gallery__back" onClick={onHome}>← All logos</button><span aria-hidden="true">/</span><span aria-current="page">Collection register</span></nav>
      <header className="identity-register__head">
        <p className="identity-eyebrow">Coverage and acquisition</p>
        <h2>Collection register</h2>
        <p>Each subject has its own evidence. A parent’s logo does not fill its services’ gaps, and a collected file does not establish a complete history.</p>
      </header>
      <div className="identity-filters" role="search" aria-label="Filter identity subjects">
        <label className="identity-filters__query">Name or alias<input type="search" value={filters.query} placeholder="TransLink, GVTA, SeaBus…" onChange={(event) => update({ query: event.target.value })} /></label>
        <label>Family<select value={filters.family} onChange={(event) => update({ family: event.target.value })}><option value="">All families</option>{COVERAGE_FAMILIES.map((group) => <option key={group.id} value={group.id}>{group.label}</option>)}</select></label>
        <label>Evidence<select value={filters.state} onChange={(event) => update({ state: event.target.value })}><option value="">All evidence states</option><option value="held">With artwork</option><option value="missing">Without artwork</option>{Object.entries(COVERAGE_STATES).map(([id, state]) => <option key={id} value={id}>{state.label}</option>)}</select></label>
        <label>Scope<select value={filters.scope} onChange={(event) => update({ scope: event.target.value })}><option value="">All registered subjects</option><option value="core">Public bodies and services</option><option value="institution">Wider institutions</option></select></label>
      </div>
      <div className="identity-register__result-heading">
        <p role="status">{summary.subjects} subjects · {summary.held} with artwork · {summary.sources} source leads</p>
        {Object.values(filters).some(Boolean) && <button type="button" className="gallery__back" onClick={() => update({ query: '', family: '', state: '', scope: '' })}>Clear filters</button>}
      </div>
      {(family?.note || family?.description) && <p className="gallery__note">{family.note || family.description}</p>}
      {!subjects.length && <p className="identity-empty">No subjects match these filters. Try another name or clear the filters.</p>}
      {groups.map((group) => (
        <section className="identity-family" key={group.id} aria-labelledby={`identity-family-${group.id}`}>
          <h3 id={`identity-family-${group.id}`}>{group.label}<span>{group.subjects.length} subjects</span></h3>
          <div className="identity-subject-links">
            {group.subjects.map((subject) => <SubjectButton key={subject.id} subject={subject} onOpen={onOpenSubject} />)}
          </div>
        </section>
      ))}
      <details className="identity-method"><summary>What the register measures</summary>
        <p>This is a researched collection scope, not a census of every BC institution. It retains the earlier Crown corporation and health-authority queue and adds explicit agencies, regional bodies, officers and service identities. Named wider institutions can be filtered separately.</p>
        <p>Evidence states describe the files actually held. They do not imply permission to reuse a mark, an adoption date, or complete coverage of every historical era. Those questions remain attached to each specimen and its sources.</p>
        <dl>{Object.entries(COVERAGE_STATES).map(([id, state]) => <div key={id}><dt>{state.label}</dt><dd>{state.description}</dd></div>)}</dl>
      </details>
    </div>
  )
}

export const IdentitySubjectDetail = ({ subject, theme, onOpenRegister, onOpenSubject, onChooseCollection, onOpenGovernment }) => {
  const family = familyById(subject.family)
  const related = (subject.relations ?? []).map((relation) => ({ ...relation, target: identitySubjectById(relation.subject) })).filter((relation) => relation.target)
  const familySubjects = IDENTITY_COVERAGE.filter((item) => item.family === subject.family && item.id !== subject.id)
  const heldEntries = subject.entries.map((entry) => ({ entry, collection: subject.collections.find((collection) => entriesOf(collection).some((item) => item.id === entry.id)) }))
  return (
    <article className="identity-detail">
      <nav className="gallery__crumbs" aria-label="Gallery"><button type="button" className="gallery__back" onClick={() => onOpenRegister()}>← Collection register</button><span aria-hidden="true">/</span><span aria-current="page">{subject.label}</span></nav>
      <header className="identity-detail__head">
        <p className="identity-eyebrow">{family?.label ?? 'Identity subject'} · {IDENTITY_KIND_LABELS[subject.kind] ?? subject.kind.replace(/-/g, ' ')}</p>
        <h2>{subject.label}</h2>
        {subject.name !== subject.label && <p className="identity-detail__name">{subject.name}</p>}
        <Status subject={subject} />
        <p>{subject.note}</p>
        {subject.aliases?.length > 0 && <p className="identity-aliases"><strong>Also indexed:</strong> {subject.aliases.join(' · ')}</p>}
        {subject.graphNode && onOpenGovernment && <button type="button" className="gallery__graph-link" onClick={() => onOpenGovernment(subject.graphNode, subject.graphYear)}>Organization and salary links <span aria-hidden="true">→</span></button>}
      </header>
      <div className="identity-detail__columns">
        <div>
          <section className="identity-detail__section" aria-labelledby="identity-artwork">
            <h3 id="identity-artwork">Artwork held</h3>
            {heldEntries.length ? <div className="identity-artworks">{heldEntries.map(({ entry, collection }) => (
              <button key={entry.id} type="button" className="identity-artwork" onClick={() => onChooseCollection(collection.id, null, entry.id)}>
                <span className="identity-artwork__image" dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }} />
                <span className="identity-artwork__label">{entry.label}</span><span className="gallery__note">{entry.years}</span>
              </button>
            ))}</div> : <div className="identity-empty"><strong>No accepted artwork yet.</strong><p>{COVERAGE_STATES[subject.state].description}</p></div>}
          </section>
          {subject.nextAction && <section className="identity-next" aria-labelledby="identity-next-heading"><p className="identity-eyebrow">Research still open</p><h3 id="identity-next-heading">Next collection work</h3><p>{subject.nextAction}</p></section>}
          {subject.sources?.length > 0 && <section className="identity-detail__section" aria-labelledby="identity-sources"><h3 id="identity-sources">Primary sources and acquisition routes</h3><ul className="identity-sources">{subject.sources.map((source, index) => <li key={`${source.url}-${index}`}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.title} <span aria-hidden="true">↗</span></a>{source.note && <p>{source.note}</p>}</li>)}</ul></section>}
        </div>
        <aside>
          {related.length > 0 && <section className="identity-detail__section" aria-labelledby="identity-relationships"><h3 id="identity-relationships">Relationships</h3><ul className="identity-relations">{related.map((relation, index) => <li key={`${relation.subject}-${index}`}><span>{relation.label ?? IDENTITY_RELATION_LABELS[relation.type] ?? relation.type.replace(/-/g, ' ')}</span><button type="button" onClick={() => onOpenSubject(relation.subject)}>{relation.target.label} →</button></li>)}</ul></section>}
          {familySubjects.length > 0 && <section className="identity-detail__section" aria-labelledby="identity-family"><h3 id="identity-family">In this family</h3><div className="identity-subject-links">{familySubjects.slice(0, 12).map((item) => <SubjectButton key={item.id} subject={item} onOpen={onOpenSubject} />)}</div>{familySubjects.length > 12 && <button type="button" className="gallery__graph-link" onClick={() => onOpenRegister({ family: subject.family })}>Browse all {familySubjects.length + 1} subjects →</button>}</section>}
        </aside>
      </div>
    </article>
  )
}

/** The same register remains reachable after opening a collection or a single-file mark page. */
export const IdentityCollectionLinks = ({ collectionId, onOpenSubject, onOpenGovernment }) => {
  const subjects = subjectsForCollection(collectionId).filter((subject) => !subject.legacy)
  return subjects.length > 0 && <section className="identity-collection-links" aria-label="Identity context">{subjects.map((subject) => <div key={subject.id}>
    <button type="button" className="gallery__graph-link" onClick={() => onOpenSubject(subject.id)}>{subject.label}: family, sources and collection gaps →</button>
    {subject.graphNode && onOpenGovernment && <button type="button" className="gallery__graph-link" onClick={() => onOpenGovernment(subject.graphNode, subject.graphYear)}>Organization and salary links →</button>}
  </div>)}</section>
}
