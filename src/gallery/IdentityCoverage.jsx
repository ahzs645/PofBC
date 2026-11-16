import { useState } from 'react'
import {
  COVERAGE_FAMILIES, COVERAGE_STATES, IDENTITY_COVERAGE, INVERSE_RELATION_LABELS, coverageSummary, familyById,
  filterIdentityCoverage, identitySubjectById, regionOf, relationsOf, subjectsForCollection
} from './identityCoverage.js'
import { MUNICIPAL_AS_OF, MUNICIPAL_REGIONS } from './municipalSubjects.js'
import { SiteLink } from '../site/navigation.jsx'
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

/**
 * A real link to a subject's page, so it can be copied or opened in another tab; a plain click
 * stays in the gallery and keeps its state.
 */
const subjectHref = (id) => globalThis.location
  ? `?${galleryPlaceUrl(globalThis.location.href, { subject: id }).searchParams}`
  : `?view=gallery&subject=${encodeURIComponent(id)}`
const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
export const SubjectLink = ({ id, onOpen, className, children }) => (
  <a className={className} href={subjectHref(id)} onClick={(event) => {
    if (!plainClick(event)) return
    event.preventDefault()
    onOpen(id)
  }}>{children}</a>
)

const SubjectButton = ({ subject, onOpen }) => (
  <SubjectLink id={subject.id} onOpen={onOpen} className="identity-subject-link">
    <span>{subject.label}</span><Status subject={subject} /><span aria-hidden="true">→</span>
  </SubjectLink>
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
    <section className="identity-overview" aria-labelledby="identity-overview-heading">
      <div>
        <p className="identity-eyebrow">The collection register</p>
        <h2 id="identity-overview-heading">Explore the families behind the marks</h2>
        <p>Regional transit, public agencies, service brands and institutions sit alongside the Crown and health collections. Follow their relationships, sources and remaining gaps.</p>
        <button type="button" className="identity-primary" onClick={() => onOpenRegister()}>Browse the register <span aria-hidden="true">→</span></button>
      </div>
      <div className="identity-overview__aside">
        <p className="identity-overview__counts"><strong>{summary.subjects}</strong> subjects tracked · <strong>{summary.held}</strong> with artwork<br />{summary.sources} source leads awaiting artwork</p>
        <div className="identity-featured">
          {featured.map((subject) => <button type="button" key={subject.id} onClick={() => onOpenSubject(subject.id)}>{subject.label} <span aria-hidden="true">↗</span></button>)}
        </div>
      </div>
    </section>
  )
}

const located = (subjects) => {
  const count = subjects.filter((subject) => subject.state === 'source-located').length
  return count ? ` · ${count} logo ${count === 1 ? 'source' : 'sources'} located` : ''
}

/** Municipalities by regional district, closed at first: 162 rows would bury every other family. */
const MunicipalRegions = ({ subjects, onOpen, onRegion }) => {
  const regions = MUNICIPAL_REGIONS.map((region) => ({ region, subjects: subjects.filter((subject) => regionOf(subject) === region) })).filter((each) => each.subjects.length)
  return (
    <div className="identity-regions">
      {regions.map(({ region, subjects: inRegion }) => (
        <details key={region} className="identity-region">
          <summary>{region}<span>{inRegion.length} {inRegion.length === 1 ? 'municipality' : 'municipalities'}{located(inRegion)}</span></summary>
          <div className="identity-subject-links">{inRegion.map((subject) => <SubjectButton key={subject.id} subject={subject} onOpen={onOpen} />)}</div>
          <button type="button" className="gallery__back" onClick={() => onRegion(region)}>Only this region</button>
        </details>
      ))}
    </div>
  )
}

export const IdentityCoverageBrowser = ({ onHome, onOpenSubject }) => {
  const [filters, setFilters] = useState(() => {
    const initial = readCoverageFilters()
    return {
      query: initial.query,
      family: COVERAGE_FAMILIES.some((family) => family.id === initial.family) ? initial.family : '',
      state: ['held', 'missing', ...Object.keys(COVERAGE_STATES)].includes(initial.state) ? initial.state : '',
      scope: ['core', 'institution'].includes(initial.scope) ? initial.scope : '',
      region: MUNICIPAL_REGIONS.includes(initial.region) ? initial.region : ''
    }
  })
  const update = (patch) => {
    const next = { ...filters, ...patch }
    // A region narrows the municipalities only; choosing it chooses that family.
    if (patch.region) next.family = 'municipalities'
    if (patch.family !== undefined && patch.family !== 'municipalities') next.region = ''
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
        <label>Region<select value={filters.region} onChange={(event) => update({ region: event.target.value })}><option value="">All regions</option>{MUNICIPAL_REGIONS.map((region) => <option key={region} value={region}>{region}</option>)}</select></label>
        <label>Scope<select value={filters.scope} onChange={(event) => update({ scope: event.target.value })}><option value="">All registered subjects</option><option value="core">Public bodies and services</option><option value="institution">Wider institutions</option></select></label>
      </div>
      <div className="identity-register__result-heading">
        <p role="status">{summary.subjects} subjects · {summary.held} with artwork · {summary.sources} source leads</p>
        {Object.values(filters).some(Boolean) && <button type="button" className="gallery__back" onClick={() => update({ query: '', family: '', state: '', scope: '', region: '' })}>Clear filters</button>}
      </div>
      {(family?.note || family?.description) && <p className="gallery__note">{family.note || family.description}{family.id === 'municipalities' && ` Registry as of ${MUNICIPAL_AS_OF}; filter by regional district with Region.`}</p>}
      {!subjects.length && <p className="identity-empty">No subjects match these filters. Try another name or clear the filters.</p>}
      {groups.map((group) => (
        <section className="identity-family" key={group.id} aria-labelledby={`identity-family-${group.id}`}>
          <h3 id={`identity-family-${group.id}`}>{group.label}<span>{group.subjects.length} subjects</span></h3>
          {group.id === 'municipalities' && !filters.region
            ? <MunicipalRegions subjects={group.subjects} onOpen={onOpenSubject} onRegion={(region) => update({ region })} />
            : <div className="identity-subject-links">
              {group.subjects.map((subject) => <SubjectButton key={subject.id} subject={subject} onOpen={onOpenSubject} />)}
            </div>}
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

/** Incoming relations grouped by type, in the order relationsOf sorted them. */
const byType = (relations) => [...relations.reduce((groups, relation) => groups.set(relation.type, [...(groups.get(relation.type) ?? []), relation]), new Map())]

const Grant = ({ grant }) => (
  <li>
    <a href={grant.registerUrl} target="_blank" rel="noopener noreferrer">{grant.letters}, {grant.date} <span aria-hidden="true">↗</span></a>
    <p>{grant.relation === 'predecessor' ? `Granted to ${grant.recipient}, a predecessor. These are not the current municipality’s arms.` : `Granted to ${grant.recipient}.`}</p>
  </li>
)

/** A municipality's place in the Province's records, and the site's existing records about it. */
const MunicipalRecords = ({ subject }) => {
  const { municipal } = subject
  const current = municipal.heraldry.filter((grant) => grant.relation === 'current')
  const predecessors = municipal.heraldry.filter((grant) => grant.relation === 'predecessor')
  return (
    <section className="identity-detail__section identity-municipal" aria-labelledby="identity-municipal">
      <h3 id="identity-municipal">Municipal records</h3>
      <dl className="identity-municipal__facts">
        <div><dt>Classification</dt><dd>{municipal.classification}</dd></div>
        <div><dt>Regional district</dt><dd>{municipal.regionalDistrict ?? 'No separate regional district'}</dd></div>
        <div><dt>{municipal.inProvincialLayer ? 'Provincial identifier' : 'Registry identifier'}</dt><dd><code>{municipal.provincialId}</code></dd></div>
        {municipal.historicalNames.length > 0 && <div><dt>Earlier names</dt><dd>{municipal.historicalNames.join(' · ')}</dd></div>}
        <div><dt>Official website</dt><dd><a href={municipal.website} target="_blank" rel="noopener noreferrer">{municipal.website.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')} <span aria-hidden="true">↗</span></a></dd></div>
      </dl>
      <ul className="identity-municipal__links">
        {municipal.councilMunicipality
          ? <li><SiteLink to={{ view: 'salaries', browse: 'council', 'council-municipality': municipal.councilMunicipality }}>Mayor and council pay <span aria-hidden="true">→</span></SiteLink></li>
          : <li className="identity-municipal__none">No council-pay records yet.</li>}
        {subject.salaryEmployers.length
          ? subject.salaryEmployers.map((slug) => <li key={slug}><SiteLink to={{ view: 'salaries', employer: slug }}>Published staff salaries <span aria-hidden="true">→</span></SiteLink></li>)
          : <li className="identity-municipal__none">No published staff salaries in the site’s records.</li>}
      </ul>
      <h4>Arms in the Canadian Heraldic Register</h4>
      {current.length || predecessors.length
        ? <ul className="identity-sources">{[...current, ...predecessors].map((grant) => <Grant key={grant.registerUrl} grant={grant} />)}</ul>
        : <p className="gallery__note">No registration found for this municipality. Arms, a flag or a seal are separate emblems from a corporate logo.</p>}
      {(current.length > 0 || predecessors.length > 0) && <p className="gallery__note">Arms are a separate emblem from the corporate logo. <SiteLink to={{ view: 'arms' }}>All municipal arms →</SiteLink></p>}
    </section>
  )
}

export const IdentitySubjectDetail = ({ subject, theme, onOpenRegister, onOpenSubject, onChooseCollection, onOpenGovernment }) => {
  const family = familyById(subject.family)
  const { outgoing: related, incoming } = relationsOf(subject)
  // A municipality's neighbours are the others in its regional district, not the first twelve of 162.
  const familySubjects = IDENTITY_COVERAGE.filter((item) => item.family === subject.family && item.id !== subject.id &&
    (!subject.municipal || regionOf(item) === regionOf(subject)))
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
          {subject.municipal && <MunicipalRecords subject={subject} />}
          {subject.sources?.length > 0 && <section className="identity-detail__section" aria-labelledby="identity-sources"><h3 id="identity-sources">Primary sources and acquisition routes</h3><ul className="identity-sources">{subject.sources.map((source, index) => <li key={`${source.url ?? source.title}-${index}`}>{source.url ? <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title} <span aria-hidden="true">↗</span></a> : <span>{source.title}</span>}{(source.note || source.citation) && <p>{source.note ?? source.citation}</p>}</li>)}</ul></section>}
        </div>
        <aside>
          {(related.length > 0 || incoming.length > 0) && <section className="identity-detail__section" aria-labelledby="identity-relationships"><h3 id="identity-relationships">Relationships</h3><ul className="identity-relations">
            {related.map((relation, index) => <li key={`out-${relation.subject}-${index}`}><span>{relation.label ?? IDENTITY_RELATION_LABELS[relation.type] ?? relation.type.replace(/-/g, ' ')}</span><SubjectLink id={relation.subject} onOpen={onOpenSubject}>{relation.target.label} →</SubjectLink></li>)}
            {byType(incoming).map(([type, group]) => <li key={`in-${type}`}><span>{INVERSE_RELATION_LABELS[type] ?? type.replace(/-/g, ' ')}</span>{group.map((relation) => <SubjectLink key={relation.subject} id={relation.subject} onOpen={onOpenSubject}>{relation.target.label} →</SubjectLink>)}</li>)}
          </ul></section>}
          {familySubjects.length > 0 && <section className="identity-detail__section" aria-labelledby="identity-family"><h3 id="identity-family">{subject.municipal ? `Also in ${regionOf(subject).replace(/^No separate regional district$/, 'this group')}` : 'In this family'}</h3><div className="identity-subject-links">{familySubjects.slice(0, 12).map((item) => <SubjectButton key={item.id} subject={item} onOpen={onOpenSubject} />)}</div>{familySubjects.length > 12 && <button type="button" className="gallery__graph-link" onClick={() => onOpenRegister({ family: subject.family, ...(subject.municipal ? { region: regionOf(subject) } : {}) })}>Browse all {familySubjects.length + 1} subjects →</button>}</section>}
        </aside>
      </div>
    </article>
  )
}

/**
 * The same register remains reachable after opening a collection or a single-file mark page, for
 * every subject that owns its artwork, legacy Crown and health records included. On a mark's page
 * only the mark's own owner is listed; an organization link already shown on the page is not
 * repeated.
 */
export const IdentityCollectionLinks = ({ collectionId, entryId, graphShown, onOpenSubject, onOpenGovernment }) => {
  const all = subjectsForCollection(collectionId)
  const owners = entryId ? all.filter((subject) => subject.entries.some((entry) => entry.id === entryId)) : []
  const subjects = owners.length ? owners : all
  if (!subjects.length) return false
  if (subjects.length > 3) {
    return <section className="identity-collection-links" aria-label="Identity context">
      <p className="gallery__note">The marks here belong to {subjects.length} register subjects:</p>
      <div>{subjects.map((subject) => <SubjectLink key={subject.id} id={subject.id} onOpen={onOpenSubject} className="gallery__graph-link">{subject.label} →</SubjectLink>)}</div>
    </section>
  }
  return <section className="identity-collection-links" aria-label="Identity context">{subjects.map((subject) => <div key={subject.id}>
    <SubjectLink id={subject.id} onOpen={onOpenSubject} className="gallery__graph-link">{subject.label}: family, sources and collection gaps →</SubjectLink>
    {subject.graphNode && subject.graphNode !== graphShown && onOpenGovernment && <button type="button" className="gallery__graph-link" onClick={() => onOpenGovernment(subject.graphNode, subject.graphYear)}>Organization and salary links →</button>}
  </div>)}</section>
}
