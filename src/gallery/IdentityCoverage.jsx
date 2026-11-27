import { useState } from 'react'
import {
  COVERAGE_FAMILIES, COVERAGE_STATES, IDENTITY_COVERAGE, INVERSE_RELATION_LABELS, coverageSummary, familyById,
  filterIdentityCoverage, identitySubjectById, regionOf, relationsOf, subjectsForCollection
} from './identityCoverage.js'
import { initiativesForBody } from '../initiatives/initiatives.js'
import { COMMISSION_DIRECTORIES, COMMISSION_FAMILY, commissionById } from './commissionHistory.js'
import { MUNICIPAL_AS_OF, MUNICIPAL_REGIONS } from './municipalSubjects.js'
import { regionalDistrictOf } from './regionalDistricts.js'
import { SiteLink } from '../site/navigation.jsx'
import { galleryPlaceUrl, readCoverageFilters } from './galleryPlace.js'
import { galleryCategoryRecords } from './gallerySearch.js'
import { writeHistory } from '../site/browserHistory.js'
import { tileArt } from './tileArt.js'
import { entriesOf } from './collections.js'
import { assetUrl } from './collectedCollections.js'
import { IDENTITY_KIND_LABELS, IDENTITY_RELATION_LABELS } from './identitySubjects.js'
import { EDITORIAL_LOGO_SPECIMENS } from './editorialLogoSpecimens.js'
import { CNC_BRAND_RESOURCES, CNC_CURRENT_MARKS, CNC_HISTORICAL_MARKS, CNC_SUBJECT, cncCover } from './cncIdentity.js'
import { POSTSECONDARY_ARTWORK_FORMAT, POSTSECONDARY_ARTWORK_SCOPE, summarizePostsecondaryArtwork } from './postsecondaryArtwork.js'
import './identityCoverage.css'
import { Select } from '../site/ui/Select.jsx'
import { holdScroll } from '../site/holdScroll.js'
import { UnbcOrigins, UnbcOriginsLink, hasUnbcOrigins, useUnbcOriginsRequested } from './UnbcOrigins.jsx'

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

const IdentitySubjectLinks = ({ subjects, onOpen }) => (
  <div className="identity-subject-links">
    {subjects.map((subject) => <SubjectButton key={subject.id} subject={subject} onOpen={onOpen} />)}
  </div>
)

export const CncIdentityCard = ({ subject, onOpen, theme }) => {
  const cover = cncCover(theme)
  return (
    <SubjectLink id={subject.id} onOpen={onOpen} className="gallery__collection">
      <span className="gallery__art gallery__art--cover identity-editorial-cover">
        <img src={assetUrl(cover.file)} width={cover.width} height={cover.height} alt="" loading="lazy" decoding="async" />
      </span>
      <span className="gallery__collection-text">
        <span className="gallery__collection-title">{subject.label}</span>
        <span className="gallery__note">Current brand and historical specimens</span>
      </span>
    </SubjectLink>
  )
}

export const IdentitySearchResults = ({ subjects, onOpen, theme }) => {
  if (!subjects.length) return null
  const cnc = subjects.find(({ id }) => id === CNC_SUBJECT)
  const otherSubjects = subjects.filter(({ id }) => id !== CNC_SUBJECT)
  return (
    <section className="gallery__shelf" aria-labelledby="search-identities">
      <h2 id="search-identities" className="gallery__shelf-title">{subjects.length} identity {subjects.length === 1 ? 'subject' : 'subjects'}</h2>
      {cnc && <div className="gallery__collections"><CncIdentityCard subject={cnc} onOpen={onOpen} theme={theme} /></div>}
      {otherSubjects.length > 0 && <IdentitySubjectLinks subjects={otherSubjects} onOpen={onOpen} />}
    </section>
  )
}

const CommissionRegisterLink = ({ onOpenRegister }) => (
  <a className="identity-action" href="?view=gallery&coverage=1&identity-family=commissions" onClick={(event) => {
    if (!plainClick(event)) return
    event.preventDefault()
    onOpenRegister({ family: COMMISSION_FAMILY.id })
  }}>Commissions</a>
)

export const IdentityCoverageOverview = ({ onOpenRegister }) => {
  const summary = coverageSummary()
  return (
    <div className="identity-overview">
      <p className="identity-overview__counts">
        <strong>{summary.subjects}</strong> subjects · <strong>{summary.held}</strong>{' '}
        <span className="identity-overview__wide">with artwork</span><span className="identity-overview__compact">held</span>
        {' · '}<strong>{summary.sources}</strong> leads
      </p>
      <button type="button" className="identity-primary" aria-label="Browse the register" onClick={() => onOpenRegister()}>
        <span>Browse<span className="identity-overview__wide"> the register</span></span><span aria-hidden="true">→</span>
      </button>
    </div>
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

const PostsecondaryCounts = ({ subjects }) => {
  const { held, vector, observedNonvector, shared, unverified } = summarizePostsecondaryArtwork(subjects)
  return (
    <p className="identity-artwork-coverage">
      <strong>{held} with artwork in the gallery</strong>
      {' · '}{vector} with verified native-vector sources
      {' · '}{observedNonvector} with observed nonvector artwork only
      {' · '}{unverified} without distinct verified logo artwork{shared ? ` (including ${shared} shared)` : ''}
    </p>
  )
}

export const IdentityCoverageBrowser = ({ onHome, onOpenSubject }) => {
  const [filters, setFilters] = useState(() => {
    const initial = readCoverageFilters()
    return {
      category: galleryCategoryRecords(initial.category) ? initial.category : '',
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
  const [filtersOpen, setFiltersOpen] = useState(false)
  const { category, ...recordFilters } = filters
  const section = galleryCategoryRecords(category)
  const title = section?.label ?? 'Collection register'
  const chosenFilters = ['family', 'state', 'region', 'scope'].filter((key) => recordFilters[key]).length
  const subjects = filterIdentityCoverage(section?.records ?? IDENTITY_COVERAGE, recordFilters)
  const summary = coverageSummary(subjects)
  const family = familyById(filters.family)
  const commissionsSelected = filters.family === COMMISSION_FAMILY.id || category === COMMISSION_FAMILY.id
  const visibleFamilies = family ? [family] : COVERAGE_FAMILIES
  const groups = visibleFamilies.map((group) => {
    const members = filterIdentityCoverage(subjects, { family: group.id })
    if (group.id === COMMISSION_FAMILY.id) {
      members.sort((a, b) => commissionById.get(a.id).name.localeCompare(commissionById.get(b.id).name, 'en-CA'))
    }
    return { ...group, subjects: members }
  }).filter((group) => group.subjects.length)
  return (
    <div className="identity-register">
      <nav className="gallery__crumbs" aria-label="Gallery"><button type="button" className="gallery__back" onClick={onHome}>← All logos</button><span aria-hidden="true">/</span><span aria-current="page">{title}</span></nav>
      <header className="identity-register__head">
        <p className="identity-eyebrow">{section ? 'Identity records' : 'Coverage and acquisition'}</p>
        <h2>{title}</h2>
      </header>
      {/* On a phone the four choices fold behind one button, so the list starts on the first screen. */}
      <div className="identity-filters" role="search" aria-label="Filter identity subjects" data-open={filtersOpen || undefined}>
        <label className="identity-filters__query">Name or alias<input type="search" value={filters.query} placeholder="TransLink, GVTA, SeaBus…" onChange={(event) => update({ query: event.target.value })} /></label>
        <button type="button" className="identity-filters__toggle" aria-expanded={filtersOpen} onClick={() => setFiltersOpen((open) => !open)}>
          Filters{chosenFilters ? ` (${chosenFilters})` : ''}
        </button>
        <label>Family<Select keepPlace value={filters.family} onChange={(value) => update({ family: value })}><option value="">All families</option>{COVERAGE_FAMILIES.map((group) => <option key={group.id} value={group.id}>{group.label}</option>)}</Select></label>
        <label>Evidence<Select keepPlace value={filters.state} onChange={(value) => update({ state: value })}><option value="">All evidence states</option><option value="held">With artwork</option><option value="missing">Without artwork</option>{Object.entries(COVERAGE_STATES).map(([id, state]) => <option key={id} value={id}>{state.label}</option>)}</Select></label>
        <label>Region<Select keepPlace value={filters.region} onChange={(value) => update({ region: value })}><option value="">All regions</option>{MUNICIPAL_REGIONS.map((region) => <option key={region} value={region}>{region}</option>)}</Select></label>
        <label>Scope<Select keepPlace value={filters.scope} onChange={(value) => update({ scope: value })}><option value="">All registered subjects</option><option value="core">Public bodies and services</option><option value="institution">Wider institutions</option></Select></label>
      </div>
      <div className="identity-register__result-heading">
        <p role="status">{summary.subjects} subjects · {summary.held} with artwork · {summary.sources} source leads</p>
        {Object.values(recordFilters).some(Boolean) && <button type="button" className="gallery__back" onClick={(event) => { holdScroll(event.currentTarget.parentElement); update({ query: '', family: '', state: '', scope: '', region: '' }) }}>Clear filters</button>}
      </div>
      {(family?.note || family?.description) && <p className="gallery__note">{family.note || family.description}{family.id === 'municipalities' && ` Registry as of ${MUNICIPAL_AS_OF}; filter by regional district with Region.`}</p>}
      {!subjects.length && <p className="identity-empty">No subjects match these filters. Try another name or clear the filters.</p>}
      {commissionsSelected && <details className="identity-research">
        <summary>Where to find other commissions</summary>
        <ul className="identity-sources">{COMMISSION_DIRECTORIES.map((entry) => <li key={entry.url}>
          <External href={entry.url}>{entry.title}</External><p>{entry.note}</p>
        </li>)}</ul>
      </details>}
      {groups.map((group) => (
        <section className="identity-family" key={group.id} aria-labelledby={`identity-family-${group.id}`}>
          <h3 id={`identity-family-${group.id}`}>{group.label}<span>{group.subjects.length} subjects</span></h3>
          {group.id === COMMISSION_FAMILY.id && !commissionsSelected && <button type="button" className="gallery__back" onClick={() => update({ family: COMMISSION_FAMILY.id })}>Browse commissions across all families →</button>}
          {group.id === 'postsecondary-history' && <PostsecondaryCounts subjects={group.subjects} />}
          {commissionsSelected ? (
            <ul className="identity-sources">{group.subjects.map((subject) => {
              const record = commissionById.get(subject.id)
              return <li key={subject.id}>
                <strong><SubjectLink id={subject.id} onOpen={onOpenSubject}>{record.name}</SubjectLink></strong>
                {' · '}{record.period}<p>{record.outcome}</p>
              </li>
            })}</ul>
          ) : group.id === 'municipalities' && !filters.region
            ? <MunicipalRegions subjects={group.subjects} onOpen={onOpenSubject} onRegion={(region) => update({ region })} />
            : <IdentitySubjectLinks subjects={group.subjects} onOpen={onOpenSubject} />}
        </section>
      ))}
      <details className="identity-method"><summary>What the register measures</summary>
        <p>Each subject has its own evidence. A parent’s logo does not fill its services’ gaps, and a collected file does not establish a complete history.</p>
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
export const RegionalDistrictMembers = ({ subject, onOpenSubject }) => {
  if (!subject?.regionalDistrict?.current) return null
  const members = IDENTITY_COVERAGE.filter(({ municipal }) => municipal?.regionalDistrict === subject.name)
  const municipalities = members.filter(({ municipal }) => municipal.inProvincialLayer)
  const otherMembers = members.filter(({ municipal }) => !municipal.inProvincialLayer)
  return (
    <section className="identity-card gallery__shelf" aria-labelledby="regional-district-members">
      <h3 id="regional-district-members">Member municipalities{municipalities.length > 0 && ` (${municipalities.length})`}</h3>
      {municipalities.length > 0
        ? <div className="identity-chips">{municipalities.map((member) => <SubjectChip key={member.id} subject={member} onOpen={onOpenSubject} />)}</div>
        : <p className="identity-muted">This regional district has no incorporated municipal members.</p>}
      {otherMembers.length > 0 && <>
        <h4>Self-government district with board representation</h4>
        <div className="identity-chips">{otherMembers.map((member) => <SubjectChip key={member.id} subject={member} onOpen={onOpenSubject} />)}</div>
      </>}
    </section>
  )
}

const MunicipalRecords = ({ subject, onOpenSubject }) => {
  const { municipal } = subject
  const district = regionalDistrictOf(municipal)
  return (
    <section className="identity-card" aria-labelledby="identity-municipal">
      <h3 id="identity-municipal">Municipal records</h3>
      <dl className="identity-facts">
        <div><dt>Type</dt><dd>{municipal.classification}</dd></div>
        <div><dt>Regional district</dt><dd>{district
          ? <SubjectLink id={district.id} onOpen={onOpenSubject}>{district.name}</SubjectLink>
          : municipal.regionalDistrict ?? 'None'}</dd></div>
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

const ArtworkSource = ({ item }) => {
  const action = item.format === 'native-vector' ? 'Open official vector source'
    : item.format === 'heraldic-register' ? 'Open heraldic register'
    : item.format === 'description-only' ? 'Open design reference' : 'Open artwork source'
  return <>
    <strong>{item.label}</strong>
    <p>{[POSTSECONDARY_ARTWORK_FORMAT[item.format], POSTSECONDARY_ARTWORK_SCOPE[item.scope], item.publisher, item.publicationDate, item.locator].filter(Boolean).join(' · ')}</p>
    <External href={item.url} className="identity-action">{action}<span className="visually-hidden">: {item.label}</span></External>
    {item.note && <p>{item.note}</p>}
    {item.rightsNote && <p>{item.rightsNote} {item.rightsUrl && <External href={item.rightsUrl}>See source terms</External>}</p>}
  </>
}

const PublicationSpecimens = ({ items }) => (
  <div className="identity-editorial-specimens__grid">{items.map((item) => (
    <figure key={item.id ?? item.file}>
      <img src={item.src ?? assetUrl(item.file)} width={item.width} height={item.height} loading="lazy" decoding="async" alt={item.alt} />
      <figcaption>
        {item.label && <strong>{item.label}</strong>}
        {item.caption && <p>{item.caption}</p>}
        {item.format && <p className="identity-muted">{item.format}</p>}
        <External href={item.url}>{item.credit}</External>
      </figcaption>
    </figure>
  ))}</div>
)

const EditorialLogoSpecimens = ({ subjectId }) => {
  const items = EDITORIAL_LOGO_SPECIMENS[subjectId]
  if (!items) return null
  return <div className="identity-editorial-specimens">
    <h5>Logo details from the publications</h5>
    <p className="identity-muted">Shown for historical comparison. PofBC is independent of the institutions; these publication excerpts are not reusable brand files.</p>
    <PublicationSpecimens items={items} />
  </div>
}

const CncIdentitySpecimens = () => (
  <div className="identity-editorial-specimens">
    <h5>Current identity</h5>
    <p>CNC unveiled its visual identity in March 2019. The full name appears in stacked and horizontal signatures. The enclosed initials still appear on the current website and the 2026–31 strategy.</p>
    <PublicationSpecimens items={CNC_CURRENT_MARKS} />
    <h5>Brand guidance and media artwork</h5>
    <ul className="identity-sources">{CNC_BRAND_RESOURCES.map(({ label, url }) => (
      <li key={url}><External href={url}>{label}</External></li>
    ))}</ul>
    <h5>Historical logos and other marks</h5>
    <p>The early covers pair the geometric CNC monogram with the full name. The 1978–79 cover also shows a shield and the description “College, Technical and Vocational Institute.” The date and status of the calendar shield remain unconfirmed.</p>
    <p>The bold calendar lettering appears in several editions around 2000. Later publications show an interlocking monogram, and the 2019 anniversary lockup pairs the new signature with a commemorative wordmark.</p>
    <PublicationSpecimens items={CNC_HISTORICAL_MARKS} />
    <p><SiteLink className="identity-action" to={{ view: 'arms', holder: CNC_SUBJECT }}>View the 1996 heraldic grant and artwork</SiteLink></p>
  </div>
)

const PostsecondaryArtworkReview = ({ review, subjectId, onOpenSubject }) => {
  const { specimens, shared, history } = review
  if (!specimens.length && !shared && !history.length) return null
  const sharedSubject = shared && IDENTITY_COVERAGE.find(({ id }) => id === shared.targetSubjectId)
  const byId = new Map(specimens.map((item) => [item.id, item]))
  const grouped = new Set(history.map((event) => event.specimenId))
  const otherSpecimens = specimens.filter((item) => !grouped.has(item.id))
  return (
    <section className="identity-card identity-artwork-review" aria-labelledby="identity-artwork-review">
      <h4 id="identity-artwork-review">{history.length ? 'Identity history and official sources' : 'Artwork sources and review'}</h4>
      {subjectId !== CNC_SUBJECT && <p className="identity-muted">The source links open the publishers’ original documents. Any excerpts shown here are separate from the gallery’s downloadable artwork holdings.</p>}
      {subjectId === CNC_SUBJECT ? <CncIdentitySpecimens /> : <EditorialLogoSpecimens subjectId={subjectId} />}
      {history.length > 0 && (
        <ol className="identity-sources identity-history" role="list">
          {history.map((event) => (
            <li key={event.specimenId ?? event.url}>
              <time dateTime={event.date} className="identity-history__date">{event.dateLabel}</time>
              {event.type === 'legal' ? <>
                <strong>{event.label}</strong>
                <p>{event.note}</p>
                <External href={event.url} className="identity-action">Open signed designation order</External>
              </> : <ArtworkSource item={byId.get(event.specimenId)} />}
            </li>
          ))}
        </ol>
      )}
      {shared && <div className="identity-artwork-review__shared">
        <strong>Shared branding{sharedSubject && <> with <SubjectLink id={sharedSubject.id} onOpen={onOpenSubject}>{sharedSubject.label}</SubjectLink></>}</strong>
        <p>{shared.note} <External href={shared.url}>{shared.label}</External></p>
      </div>}
      {otherSpecimens.length > 0 && <>
        {history.length > 0 && <h5>Other artwork leads</h5>}
        <ul className="identity-sources">
          {otherSpecimens.map((item) => <li key={item.id}><ArtworkSource item={item} /></li>)}
        </ul>
      </>}
    </section>
  )
}

export const IdentitySubjectDetail = ({ subject, theme, onOpenRegister, onOpenSubject, onChooseCollection, onOpenGovernment, children }) => {
  const commission = commissionById.get(subject.id)
  const relatedCommissionSubject = commission?.next && identitySubjectById(commission.next)
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
  const story = useUnbcOriginsRequested()
  return (
    <article className="identity-detail">
      <nav className="gallery__crumbs" aria-label="Gallery"><button type="button" className="gallery__back" onClick={() => onOpenRegister(subject.regionalDistrict ? { family: subject.family } : undefined)}>← {subject.regionalDistrict ? 'Regional districts register' : 'Collection register'}</button><span aria-hidden="true">/</span><span aria-current="page">{subject.label}</span></nav>

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
          {initiativesForBody(subject.id).map((entry) => <SiteLink key={entry.id} className="identity-action" to={{ view: 'initiatives', initiative: entry.id }}>{entry.title} initiative</SiteLink>)}
          {commission && <CommissionRegisterLink onOpenRegister={onOpenRegister} />}
          {hasUnbcOrigins(subject.id) && <UnbcOriginsLink local />}
          {subject.schoolDistrict && <SiteLink className="identity-action" to={{ view: 'school-districts', district: subject.schoolDistrict }}>Connected district history <span aria-hidden="true">→</span></SiteLink>}
          {subject.graphNode && onOpenGovernment && <button type="button" className="identity-action" onClick={() => onOpenGovernment(subject.graphNode, subject.graphYear)}>Organization and salaries <span aria-hidden="true">→</span></button>}
          {municipal?.councilMunicipality && <SiteLink className="identity-action" to={{ view: 'salaries', browse: 'council', 'council-municipality': municipal.councilMunicipality }}>Council pay <span aria-hidden="true">→</span></SiteLink>}
          {municipal && subject.salaryEmployers.map((slug) => <SiteLink key={slug} className="identity-action" to={{ view: 'salaries', employer: slug }}>Staff salaries <span aria-hidden="true">→</span></SiteLink>)}
          {municipal?.website && <External className="identity-action" href={municipal.website}>{municipal.website.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')}</External>}
        </div>
      </header>

      {children}
      <div className="identity-layout">
        <div className="identity-layout__main">
          {commission && <section className="identity-card" aria-labelledby="commission-history">
            <h3 id="commission-history">Commission history</h3>
            <strong>{commission.period}</strong>
            {subject.note !== commission.history && <p>{commission.history}</p>}
            <p>{commission.outcome}</p>
            {commission.later && <p>{commission.later}</p>}
            {relatedCommissionSubject && <SubjectLink id={relatedCommissionSubject.id} onOpen={onOpenSubject}>See {relatedCommissionSubject.name} →</SubjectLink>}
            <ul className="identity-sources">{commission.sources.map((source) => <li key={source.url}><External href={source.url}>{source.title}</External></li>)}</ul>
          </section>}
          <section aria-labelledby="identity-artwork">
            <h3 id="identity-artwork" className="identity-heading">Artwork <span>{heldEntries.length || ''}</span></h3>
            {heldEntries.length
              ? <div className="identity-artworks">{heldEntries.map(({ entry, collection }) => (
                <button key={entry.id} type="button" className="identity-artwork" onClick={() => onChooseCollection(collection.id, null, entry.id)}>
                  <span className="identity-artwork__image" dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }} />
                  <span className="identity-artwork__label">{entry.label}</span><span className="identity-muted">{entry.years}</span>
                </button>
              ))}</div>
              : subject.id !== CNC_SUBJECT && <div className="identity-empty"><strong>{subject.artworkReview ? 'No separately held artwork.' : 'Still wanted.'}</strong> {subject.nextAction}</div>}
            {subject.artworkReview && <PostsecondaryArtworkReview review={subject.artworkReview} subjectId={subject.id} onOpenSubject={onOpenSubject} />}
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
          {municipal && <MunicipalRecords subject={subject} onOpenSubject={onOpenSubject} />}
          <RegionalDistrictMembers subject={subject} onOpenSubject={onOpenSubject} />
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
      {hasUnbcOrigins(subject.id) && story && <UnbcOrigins contextId={subject.id} onOpenSubject={onOpenSubject} onChooseCollection={onChooseCollection} />}
    </article>
  )
}

/**
 * The same register remains reachable after opening a collection or a single-file mark page, for
 * every subject that owns its artwork, legacy Crown and health records included. On a mark's page
 * only the mark's own owner is listed; an organization link already shown on the page is not
 * repeated.
 */
export const IdentityCollectionLinks = ({ collectionId, entryId, graphShown, history, onOpenSubject, onOpenCollection, onOpenGovernment }) => {
  const all = subjectsForCollection(collectionId)
  const owners = entryId ? all.filter((subject) => subject.entries.some((entry) => entry.id === entryId)) : []
  const subjects = owners.length ? owners : all
  // A collection of many owners (the Province's one-offs) links each card to its organization, and
  // each mark's page to its owner; a row of every owner above the cards said all of that again.
  // A collection whose own organization link is already in its header needs no second way out.
  if (!subjects.length || subjects.length > 3) return false
  // A subject's defined ties (shareholder of, part of, operated by, and the reverse), as links to the
  // subjects they name, so a mark's page leads to the bodies it belongs with. A bare "related to" is
  // left to the register page, which explains it.
  const historicalTargets = new Set(history ? [...history.predecessors, ...history.successors].map(({ id }) => id) : [])
  const historyTypes = new Set(['successor-of', 'predecessor-of', 'renamed-from', 'renamed-to', 'amalgamated-into'])
  // A collection holding a line of names shows each name as an era, so a tie between two of its own
  // subjects (Capilano College renamed to Capilano University) would only lead back to this page.
  const own = new Set(all.map(({ id }) => id))
  const tiesOf = (subject) => connectionGroups(subject)
    .flatMap(({ label, relations }) => relations.filter((relation) => relation.type !== 'related-to').map((relation) => ({ label, relation })))
    .filter(({ relation }) => !own.has(relation.target.id))
    // A tie recorded from both sides reads the same from here; show it once.
    .filter(({ label, relation }, at, ties) => ties.findIndex((other) => other.label === label && other.relation.target.id === relation.target.id) === at)
    .filter(({ relation }) => !(historyTypes.has(relation.type) && historicalTargets.has(relation.target.id)))
    .slice(0, 4)
  const registerShown = !(graphShown && subjects.every((subject) => subject.graphNode === graphShown))
  const rows = subjects.map((subject) => ({ subject, ties: tiesOf(subject) })).filter(({ ties }) => registerShown || ties.length)
  if (!rows.length) return false
  return <section className="identity-collection-links" aria-label="Identity context">{rows.map(({ subject, ties }) => <div key={subject.id}>
    {registerShown && <SubjectLink id={subject.id} onOpen={onOpenSubject} className="gallery__graph-link">{subject.label} in the register →</SubjectLink>}
    {registerShown && subject.graphNode && subject.graphNode !== graphShown && onOpenGovernment && <button type="button" className="gallery__graph-link" onClick={() => onOpenGovernment(subject.graphNode, subject.graphYear)}>Organization and salary links →</button>}
    {ties.map(({ label, relation }) => relation.type === 'charitable-partner-of' && relation.target.collectionIds?.length === 1
      ? <a key={relation.target.id} className="gallery__graph-link" href={`?view=gallery&logos=${encodeURIComponent(relation.target.collectionIds[0])}`} onClick={(event) => {
          if (onOpenCollection && plainClick(event)) {
            event.preventDefault()
            onOpenCollection(relation.target.collectionIds[0])
          }
        }}>{label} {relation.target.label} →</a>
      : <SubjectLink key={`${relation.type}:${relation.target.id}`} id={relation.target.id} onOpen={onOpenSubject} className="gallery__graph-link">{label} {relation.target.label} →</SubjectLink>
    )}
  </div>)}</section>
}
