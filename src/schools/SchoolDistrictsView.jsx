import { useEffect, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { writeHistory } from '../site/browserHistory.js'
import { documentTitle, setDocumentMeta } from '../site/documentMeta.js'
import { CURRENT_DISTRICTS, SCHOOL_DIRECTORY_SOURCE, SCHOOL_DISTRICTS_AS_OF, DISTRICT_COUNTS, districtById, districtPlace, searchDistricts, connectionsOf, districtHistory, districtSources, formatHistoryDate, establishmentLabel } from './districts.js'
import './schools.css'

const assetUrl = (file) => `${import.meta.env.BASE_URL}${file.replace(/^\//, '')}`
const External = ({ children, ...props }) => <a {...props} target="_blank" rel="noreferrer">{children}<span aria-hidden="true"> ↗</span></a>
const readPlace = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  return { district: params.get('district') ?? '', query: params.get('school-query') ?? '', scope: ['all', 'historical'].includes(params.get('school-scope')) ? params.get('school-scope') : 'current' }
}
const preserved = (place) => ({ ...(place.query ? { 'school-query': place.query } : {}), ...(place.scope !== 'current' ? { 'school-scope': place.scope } : {}) })
const sourceLink = (event) => event.sourceUrl && <External href={event.sourceUrl}>{event.sourceTitle ?? 'Source'}{event.locator ? ` · ${event.locator}` : ''}</External>
const Logo = ({ district, className = '' }) => {
  const asset = district.assets.find((item) => !item.variantOf) ?? district.assets[0]
  return <div className={`schools__logo ${className}`} data-dark={asset?.darkBackground || asset?.displayBackground || undefined}>
    {asset ? <img src={assetUrl(asset.previewFile ?? asset.file)} alt={`${district.name} logo`} loading="lazy" /> : <span className="schools__number" aria-label="Logo not yet collected">SD<span>{district.number}</span></span>}
  </div>
}

const DistrictCard = ({ district, place }) => <SiteLink className="schools__card" to={districtPlace(district, preserved(place))}>
  <Logo district={district} />
  <div className="schools__card-copy">
    <span className="schools__eyebrow">SD {district.number} · {district.current ? 'Current district' : 'Historical district'}</span>
    <h3>{district.name}</h3>
    <p>{district.established?.date ? `${establishmentLabel(district)} ${formatHistoryDate(district.established.date)}` : 'Establishment date under review'}</p>
    <span className="schools__card-footer">{district.assets.length ? `${district.assets.length} logo ${district.assets.length === 1 ? 'file' : 'files'}` : 'Logo research'}<span aria-hidden="true">Explore →</span></span>
  </div>
</SiteLink>

const Connection = ({ link, place }) => <li>
  <SiteLink className="schools__connection" to={districtPlace(link.district, preserved(place))}>
    <span className="schools__eyebrow">SD {link.district.number}</span>
    <strong>{link.district.name}</strong>
    <span>{formatHistoryDate(link.date)} <span aria-hidden="true">→</span></span>
  </SiteLink>
  <div className="schools__connection-source"><External href={link.sourceUrl}>Connection source{link.locator ? ` · ${link.locator}` : ''}</External></div>
</li>

const DistrictConnections = ({ district, place }) => {
  const { predecessors, successors } = connectionsOf(district.id)
  return <section className="schools__section" id="district-connections" aria-labelledby="district-connections-title">
    <div className="schools__section-heading"><div><p className="schools__eyebrow">Follow the organizations</p><h3 id="district-connections-title">Connected history</h3></div><span className="schools__muted">Select a district to follow its story</span></div>
    {predecessors.length || successors.length ? <div className="schools__lineage">
      <div className="schools__lineage-column"><h4>Predecessors</h4>{predecessors.length ? <ul>{predecessors.map((link) => <Connection key={link.from} link={link} place={place} />)}</ul> : <p className="schools__muted">Earlier districts have not yet been established by the collected sources.</p>}</div>
      <div className="schools__lineage-focus"><span className="schools__lineage-arrow" aria-hidden="true">↓</span><Logo district={district} /><p className="schools__eyebrow">Selected district</p><h4>{district.title}</h4><p>{district.established?.date ? formatHistoryDate(district.established.date) : 'Establishment date under review'}</p><span className="schools__lineage-arrow" aria-hidden="true">↓</span></div>
      <div className="schools__lineage-column"><h4>Successors</h4>{successors.length ? <ul>{successors.map((link) => <Connection key={link.to} link={link} place={place} />)}</ul> : <p className="schools__muted">{district.current ? 'This district is in the current provincial directory.' : 'A later successor has not yet been established by the collected sources.'}</p>}</div>
    </div> : <p className="schools__empty">No predecessor or successor relationship is established by the sources collected for this district so far. Its formation and later changes are recorded below.</p>}
    <p className="schools__caption">These links record district succession. Each predecessor retains its own dates and identity.</p>
  </section>
}

const AmalgamationOverview = ({ place }) => {
  const rows = CURRENT_DISTRICTS.map((district) => ({ district, links: connectionsOf(district.id).predecessors })).filter((row) => row.links.length)
  return <details className="schools__amalgamations">
    <summary>Explore {rows.length} documented amalgamations <span>{DISTRICT_COUNTS.connections} predecessor connections</span></summary>
    <p>Follow an earlier district into its successor. The date belongs to the effective amalgamation; each link opens that district’s own history.</p>
    <ul>{rows.map(({ district, links }) => <li key={district.id}>
      <div className="schools__merger-predecessors">{links.map((link) => <SiteLink key={link.from} to={districtPlace(link.district, preserved(place))}>{link.district.title}</SiteLink>)}</div>
      <span className="schools__merger-arrow" aria-hidden="true">→</span>
      <div className="schools__merger-successor"><SiteLink to={districtPlace(district, preserved(place))}>{district.title}</SiteLink><span>{formatHistoryDate(links[0].date)} · <External href={links[0].sourceUrl}>{links[0].sourceTitle ?? 'Source'}</External></span></div>
    </li>)}</ul>
  </details>
}

const DistrictTimeline = ({ district }) => {
  const events = districtHistory(district)
  return <section className="schools__section" id="district-history" aria-labelledby="district-history-title">
    <div className="schools__section-heading"><div><p className="schools__eyebrow">Dates and evidence</p><h3 id="district-history-title">District history</h3></div></div>
    {events.length ? <ol className="schools__timeline">{events.map((event, i) => <li key={`${event.type}-${event.date}-${i}`}>
      <div className="schools__timeline-date"><time dateTime={event.precision === 'report-period' ? undefined : event.date}>{formatHistoryDate(event.date)}</time><span>{event.precision === 'year' ? 'Year recorded' : event.precision === 'month' ? 'Month recorded' : event.precision === 'report-period' ? 'Report period' : event.evidenceType?.includes('financial-statement') ? 'District-reported date' : ''}</span></div>
      <div className="schools__timeline-event"><h4>{event.title}</h4>{event.detail && <p>{event.detail}</p>}{event.notes && <p className="schools__muted">{Array.isArray(event.notes) ? event.notes.join(' ') : event.notes}</p>}<div className="schools__source">{sourceLink(event)}</div></div>
    </li>)}</ol> : <p className="schools__empty">The district is documented, but an establishment date has not yet been verified. The source links below provide the research starting points.</p>}
    {district.notes.length > 0 && <details className="schools__notes"><summary>Research notes and remaining questions</summary><ul>{district.notes.map((note, i) => <li key={i}>{note}</li>)}</ul></details>}
  </section>
}

const DistrictLogos = ({ district }) => <section className="schools__section" id="district-logos" aria-labelledby="district-logos-title">
  <div className="schools__section-heading"><div><p className="schools__eyebrow">Original published artwork</p><h3 id="district-logos-title">Logos and identity</h3></div>{district.assets.length > 0 && <SiteLink to={{ view: 'gallery', logos: `collected-${district.id}` }}>Open in Logos →</SiteLink>}</div>
  {district.assets.length ? <div className="schools__artworks">{district.assets.map((asset) => <figure key={asset.id} className="schools__artwork">
    <div className="schools__artwork-image" data-dark={asset.darkBackground || asset.displayBackground || undefined}><img src={assetUrl(asset.previewFile ?? asset.file)} alt={asset.label} loading="lazy" /></div>
    <figcaption><div className="schools__artwork-meta"><strong>{asset.label}</strong><span className="schools__badge">{asset.isVector ? 'Source vector' : 'Published image'} · {asset.format.toUpperCase()}</span></div>
      <p>{asset.notes}</p>
      {asset.adoptionDate && <p>{asset.adoptionDatePrecision === 'announcement' ? 'Announced' : 'Introduced'} {formatHistoryDate(asset.adoptionDate)}{asset.adoptionSource && <> · <External href={asset.adoptionSource}>Announcement</External></>}</p>}
      {asset.sourceDate && <p className="schools__muted">Source date: {asset.sourceDate}</p>}
      {asset.sourcePeriod && <p className="schools__muted">Documented in the {asset.sourcePeriod} report.</p>}
      {asset.rightsReview && <p className="schools__muted">{asset.rightsReview.note} <External href={asset.rightsReview.sourceUrl}>Source terms</External></p>}
      <div className="schools__artwork-links"><a href={assetUrl(asset.file)} download>Download {asset.format.toUpperCase()}</a><External href={asset.sourcePage ?? asset.sourceUrl}>{asset.sourceKind === 'district-recruitment-profile' ? 'District employer profile' : 'Official source'}</External></div>
    </figcaption>
  </figure>)}</div> : <p className="schools__empty">{district.logoNotes || 'An original logo or seal has not yet been collected for this district.'}</p>}
  <p className="schools__caption">Artwork is preserved from its published source. A website capture dates the observation; an introduction date is shown only where a source identifies it.</p>
</section>

const DistrictDetail = ({ district, place }) => <article className="schools__detail">
  <SiteLink className="schools__back" to={districtPlace(null, preserved(place))}>← All school districts</SiteLink>
  <header className="schools__detail-head"><div><p className="schools__eyebrow">British Columbia · {district.current ? 'Current public school district' : 'Historical school district'}</p><h2>{district.name}</h2><p className="schools__detail-subtitle">School District No. {district.number}</p>{district.legalName && <p className="schools__muted">{district.legalName}</p>}
    <div className="schools__detail-facts"><div><span>{establishmentLabel(district)}</span><strong>{formatHistoryDate(district.established?.date)}</strong></div>{district.ended?.date && <div><span>Abolished</span><strong>{formatHistoryDate(district.ended.date)}</strong></div>}<div><span>Identity collection</span><strong>{district.assets.length ? `${district.assets.length} original ${district.assets.length === 1 ? 'file' : 'files'}` : 'Research in progress'}</strong></div></div>
    {district.established?.disputed && <p className="schools__date-note">Sources give different dates. See the dated claims and evidence in the history below.</p>}
    {district.established?.kind === 'institutional-origin' && <p className="schools__date-note">This records an institutional origin; the formation of the modern numbered district is a separate research question.</p>}
    <div className="schools__actions">{district.officialUrl && <External href={district.officialUrl}>Official website</External>}{district.employerSlug && <SiteLink to={{ view: 'salaries', employer: district.employerSlug }}>Salary disclosures →</SiteLink>}{district.current && <SiteLink to={{ view: 'government', mode: 'related', node: district.id }}>Governance and organization →</SiteLink>}</div>
  </div><Logo district={district} className="schools__hero-logo" /></header>
  <nav className="schools__section-nav" aria-label="District sections"><a href="#district-connections">Connections</a><a href="#district-history">History</a><a href="#district-logos">Logos</a><a href="#district-sources">Sources</a></nav>
  <DistrictConnections district={district} place={place} /><DistrictTimeline district={district} /><DistrictLogos district={district} />
  <section className="schools__section" id="district-sources" aria-labelledby="district-sources-title"><div className="schools__section-heading"><div><p className="schools__eyebrow">Follow the evidence</p><h3 id="district-sources-title">Sources</h3></div></div><ol className="schools__sources">{districtSources(district).map((source, i) => <li key={`${source.url}-${i}`}><External href={source.url}>{source.title}</External>{source.locator && <span>{source.locator}</span>}{source.note && <p>{source.note}</p>}</li>)}</ol></section>
</article>

export const SchoolDistrictsView = () => {
  const [place, setPlace] = useState(readPlace)
  const selected = districtById(place.district)
  useEffect(() => {
    const restore = () => setPlace(readPlace())
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [])
  useEffect(() => setDocumentMeta({ title: documentTitle(selected ? `${selected.title} · School districts` : 'School districts'), description: 'Explore B.C. school districts through their formation, predecessor connections, original logos and public salary disclosures.' }), [selected])
  const changeFilters = (patch) => {
    const next = { ...place, ...patch }; setPlace(next)
    const url = new URL(globalThis.location.href); url.search = new URLSearchParams(districtPlace(null, preserved(next))).toString(); url.hash = ''
    writeHistory(url, { replace: true })
  }
  if (place.district && !selected) return <main className="schools"><div className="schools__empty"><h2>District not found</h2><p>This address does not identify a district in the collection.</p><SiteLink to={districtPlace()}>Browse all districts →</SiteLink></div></main>
  if (selected) return <main className="schools"><DistrictDetail district={selected} place={place} /></main>
  const results = searchDistricts(place)
  return <main className="schools">
    <header className="schools__intro"><div><p className="schools__eyebrow">Public education · British Columbia</p><h2>School districts,<br />connected through time.</h2><p>Explore the districts behind B.C.’s public schools: when they formed, the organizations they came from, and the identities they used.</p></div><div className="schools__stats"><div><strong>{DISTRICT_COUNTS.current}</strong><span>current districts</span></div><div><strong>{DISTRICT_COUNTS.historical}</strong><span>documented predecessors</span></div><div><strong>{DISTRICT_COUNTS.withLogos}</strong><span>districts with logos</span></div><div><strong>{DISTRICT_COUNTS.dated}</strong><span>dated origins and formations</span></div></div></header>
    <AmalgamationOverview place={place} />
    <div className="schools__toolbar"><label className="schools__search"><span>Find a district</span><input type="search" value={place.query} onChange={(event) => changeFilters({ query: event.target.value })} placeholder="Name, district number or earlier name" /></label><label className="schools__scope"><span>Show</span><select value={place.scope} onChange={(event) => changeFilters({ scope: event.target.value })}><option value="current">Current districts</option><option value="historical">Historical districts</option><option value="all">All districts</option></select></label><p role="status">{results.length} {results.length === 1 ? 'district' : 'districts'}</p></div>
    <div className="schools__grid">{results.map((district) => <DistrictCard key={district.id} district={district} place={place} />)}</div>
    {!results.length && <div className="schools__empty"><h3>No matching districts</h3><p>Try an earlier name or district number, or include historical districts.</p><button type="button" onClick={() => changeFilters({ query: '', scope: 'all' })}>Show all districts</button></div>}
    <footer className="schools__about"><div><h3>A district’s history, with its sources.</h3><p>Formation, amalgamation, name changes and logo introductions retain their own dates and evidence. Unresolved dates and missing historical artwork remain visible.</p><p className="schools__muted">Current directory checked {formatHistoryDate(SCHOOL_DISTRICTS_AS_OF)}. All {CURRENT_DISTRICTS.length} current districts link to existing salary disclosures.</p></div><div className="schools__about-links"><External href={SCHOOL_DIRECTORY_SOURCE}>Provincial district directory</External><a href={assetUrl('education/school-districts/catalogue.json')} download>Download the sourced catalogue</a><SiteLink to={{ view: 'gallery', coverage: '1', 'identity-family': 'school-districts' }}>School district identity register →</SiteLink></div></footer>
  </main>
}
