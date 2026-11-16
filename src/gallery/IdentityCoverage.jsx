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
import { Select } from '../site/ui/Select.jsx'
import { holdScroll } from '../site/holdScroll.js'

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
          <button type="button" className="gallery__back" onClick={(event) => {
            // The regions give way to the one region's municipalities: their heading takes the
            // button's place on screen, so the narrowed list starts under the finger.
            holdScroll(event.currentTarget, { find: () => document.getElementById('identity-family-municipalities') })
            onRegion(region)
          }}>Only this region</button>
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
        <label>Family<Select keepPlace value={filters.family} onChange={(value) => update({ family: value })}><option value="">All families</option>{COVERAGE_FAMILIES.map((group) => <option key={group.id} value={group.id}>{group.label}</option>)}</Select></label>
        <label>Evidence<Select keepPlace value={filters.state} onChange={(value) => update({ state: value })}><option value="">All evidence states</option><option value="held">With artwork</option><option value="missing">Without artwork</option>{Object.entries(COVERAGE_STATES).map(([id, state]) => <option key={id} value={id}>{state.label}</option>)}</Select></label>
        <label>Region<Select keepPlace value={filters.region} onChange={(value) => update({ region: value })}><option value="">All regions</option>{MUNICIPAL_REGIONS.map((region) => <option key={region} value={region}>{region}</option>)}</Select></label>
        <label>Scope<Select keepPlace value={filters.scope} onChange={(value) => update({ scope: value })}><option value="">All registered subjects</option><option value="core">Public bodies and services</option><option value="institution">Wider institutions</option></Select></label>
      </div>
      <div className="identity-register__result-heading">
        <p role="status">{summary.subjects} subjects · {summary.held} with artwork · {summary.sources} source leads</p>
        {Object.values(filters).some(Boolean) && <button type="button" className="gallery__back" onClick={(event) => { holdScroll(event.currentTarget.parentElement); update({ query: '', family: '', state: '', scope: '', region: '' }) }}>Clear filters</button>}
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

/** A subject as a small link: its name, with a dot that is filled when artwork is held. */
const SubjectChip = ({ subject, onOpen, label = subject.label }) => (
  <SubjectLink id={subject.id} onOpen={onOpen} className="identity-chip">
    <span className="identity-chip__dot" data-held={subject.hasArtwork || undefined} title={subject.stateLabel} aria-hidden="true" />
    {label}<span className="visually-hidden"> ({subject.stateLabel})</span>
  </SubjectLink>
)

/**
 * Every relation of a subject as labelled groups: its own ("Part of TransLink") and those recorded
 * on others that point to it ("Includes BCRTC"), each label once.
 */
const connectionGroups = (subject) => {
  const { outgoing, incoming } = relationsOf(subject)
  const groups = new Map()
  const add = (label, relation) => groups.set(label, [...(groups.get(label) ?? []), relation])
  for (const relation of outgoing) add(relation.label ?? IDENTITY_RELATION_LABELS[relation.type] ?? relation.type.replace(/-/g, ' '), relation)
  for (const relation of incoming) add(INVERSE_RELATION_LABELS[relation.type] ?? relation.type.replace(/-/g, ' '), relation)
  return [...groups].map(([label, relations]) => ({ label, relations }))
}

const External = ({ href, children, className }) => <a className={className} href={href} target="_blank" rel="noopener noreferrer">{children} <span aria-hidden="true">↗</span></a>

/** A municipality's facts, its arms registrations and the site's records about it, compactly. */
const MunicipalRecords = ({ subject }) => {
  const { municipal } = subject
  return (
    <section className="identity-card" aria-labelledby="identity-municipal">
      <h3 id="identity-municipal">Municipal records</h3>
      <dl className="identity-facts">
        <div><dt>Type</dt><dd>{municipal.classification}</dd></div>
        <div><dt>Regional district</dt><dd>{municipal.regionalDistrict ?? 'None'}</dd></div>
        <div><dt>{municipal.inProvincialLayer ? 'Provincial ID' : 'Registry ID'}</dt><dd><code>{municipal.provincialId}</code></dd></div>
        {municipal.historicalNames.length > 0 && <div><dt>Earlier name</dt><dd>{municipal.historicalNames.join(', ')}</dd></div>}
      </dl>
      <h4>Arms</h4>
      {municipal.heraldry.length
        ? <ul className="identity-grants">{municipal.heraldry.map((grant) => (
          <li key={grant.registerUrl}>
            <span className="identity-grants__year">{grant.date.slice(0, 4)}</span>
            <External href={grant.registerUrl}>{grant.letters.replace(/^Grant of /, '').replace(/^Registration of /, 'Registered: ')}</External>
            {grant.relation === 'predecessor' && <span className="identity-tag" title="Granted to a predecessor; not the current municipality’s arms">{grant.recipient}</span>}
          </li>
        ))}</ul>
        : <p className="identity-muted">None in the Canadian Heraldic Register.</p>}
    </section>
  )
}

export const IdentitySubjectDetail = ({ subject, theme, onOpenRegister, onOpenSubject, onChooseCollection, onOpenGovernment }) => {
  const family = familyById(subject.family)
  const groups = connectionGroups(subject)
  const connected = new Set(groups.flatMap((group) => group.relations.map((relation) => relation.subject)))
  // A municipality's neighbours are the others in its regional district, not the first of 162.
  // Anything already listed as a connection is not listed again.
  const familySubjects = IDENTITY_COVERAGE.filter((item) => item.family === subject.family && item.id !== subject.id &&
    !connected.has(item.id) && (!subject.municipal || regionOf(item) === regionOf(subject)))
  const familyTitle = subject.municipal ? `Also in ${regionOf(subject).replace(/^No separate regional district$/, 'this group')}` : `More in ${family?.label ?? 'this family'}`
  const heldEntries = subject.entries.map((entry) => ({ entry, collection: subject.collections.find((collection) => entriesOf(collection).some((item) => item.id === entry.id)) }))
  const { municipal } = subject
  const kind = IDENTITY_KIND_LABELS[subject.kind] ?? subject.kind.replace(/-/g, ' ')
  const SHOWN = 16
  return (
    <article className="identity-detail">
      <nav className="gallery__crumbs" aria-label="Gallery"><button type="button" className="gallery__back" onClick={() => onOpenRegister()}>← Collection register</button><span aria-hidden="true">/</span><span aria-current="page">{subject.label}</span></nav>

      <header className="identity-hero">
        <p className="identity-eyebrow">{family?.label ?? 'Identity subject'} · {kind}</p>
        <h2>{subject.label}</h2>
        {(subject.name !== subject.label || subject.aliases?.length > 0) && (
          <p className="identity-hero__names">
            {subject.name !== subject.label && <span>{subject.name}</span>}
            {subject.aliases?.filter((alias) => alias !== subject.name).length > 0 && <span className="identity-muted">Also {subject.aliases.filter((alias) => alias !== subject.name).join(' · ')}</span>}
          </p>
        )}
        <p className="identity-hero__note">{subject.note}</p>
        <div className="identity-actions">
          <Status subject={subject} />
          {subject.graphNode && onOpenGovernment && <button type="button" className="identity-action" onClick={() => onOpenGovernment(subject.graphNode, subject.graphYear)}>Organization and salaries <span aria-hidden="true">→</span></button>}
          {municipal?.councilMunicipality && <SiteLink className="identity-action" to={{ view: 'salaries', browse: 'council', 'council-municipality': municipal.councilMunicipality }}>Council pay <span aria-hidden="true">→</span></SiteLink>}
          {municipal && subject.salaryEmployers.map((slug) => <SiteLink key={slug} className="identity-action" to={{ view: 'salaries', employer: slug }}>Staff salaries <span aria-hidden="true">→</span></SiteLink>)}
          {municipal?.website && <External className="identity-action" href={municipal.website}>{municipal.website.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')}</External>}
        </div>
      </header>

      <div className="identity-layout">
        <div className="identity-layout__main">
          <section aria-labelledby="identity-artwork">
            <h3 id="identity-artwork" className="identity-heading">Artwork <span>{heldEntries.length || ''}</span></h3>
            {heldEntries.length
              ? <div className="identity-artworks">{heldEntries.map(({ entry, collection }) => (
                <button key={entry.id} type="button" className="identity-artwork" onClick={() => onChooseCollection(collection.id, null, entry.id)}>
                  <span className="identity-artwork__image" dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }} />
                  <span className="identity-artwork__label">{entry.label}</span><span className="identity-muted">{entry.years}</span>
                </button>
              ))}</div>
              : <div className="identity-empty"><strong>Still wanted.</strong> {subject.nextAction}</div>}
          </section>

          {(subject.sources?.length > 0 || (heldEntries.length > 0 && subject.nextAction)) && (
            <details className="identity-research">
              <summary>Research notes<span>{[heldEntries.length > 0 && subject.nextAction ? 'next step' : null, subject.sources?.length ? `${subject.sources.length} ${subject.sources.length === 1 ? 'source' : 'sources'}` : null].filter(Boolean).join(' · ')}</span></summary>
              {heldEntries.length > 0 && subject.nextAction && <p className="identity-research__next"><strong>Next:</strong> {subject.nextAction}</p>}
              <ul className="identity-sources">{subject.sources.map((source, index) => (
                <li key={`${source.url ?? source.title}-${index}`}>
                  {source.url ? <External href={source.url}>{source.title}</External> : <span>{source.title}</span>}
                  {(source.note || source.citation) && <p>{source.note ?? source.citation}</p>}
                </li>
              ))}</ul>
            </details>
          )}
        </div>

        <aside className="identity-layout__side">
          {municipal && <MunicipalRecords subject={subject} />}
          {groups.length > 0 && (
            <section className="identity-card" aria-labelledby="identity-relationships">
              <h3 id="identity-relationships">Connections</h3>
              {groups.map(({ label, relations }) => (
                <div key={label} className="identity-chip-group">
                  <h4>{label}</h4>
                  <div className="identity-chips">{relations.map((relation) => <SubjectChip key={relation.subject} subject={relation.target} onOpen={onOpenSubject} />)}</div>
                </div>
              ))}
            </section>
          )}
          {familySubjects.length > 0 && (
            <section className="identity-card" aria-labelledby="identity-family">
              <h3 id="identity-family">{familyTitle}</h3>
              <div className="identity-chips">{familySubjects.slice(0, SHOWN).map((item) => <SubjectChip key={item.id} subject={item} onOpen={onOpenSubject} />)}</div>
              {familySubjects.length > SHOWN && <button type="button" className="identity-more" onClick={() => onOpenRegister({ family: subject.family, ...(municipal ? { region: regionOf(subject) } : {}) })}>All {IDENTITY_COVERAGE.filter((item) => item.family === subject.family && (!municipal || regionOf(item) === regionOf(subject))).length} in the register →</button>}
            </section>
          )}
          {(groups.length > 0 || familySubjects.length > 0) && <p className="identity-legend"><span className="identity-chip__dot" data-held aria-hidden="true" /> artwork held <span className="identity-chip__dot" aria-hidden="true" /> still wanted</p>}
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
