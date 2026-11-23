// British Columbia's provincial political parties, by the marks they used.
//
// The roster follows the parties that governed, formed the Official Opposition or otherwise held
// seats, with their predecessors and labels. Each party opens on its designs, oldest first, then the
// organizational history — formations, registered names, mergers that were not mergers — and the gaps
// the research left open. The data is the filed package in research/parties (scripts/build-parties.mjs).

import { useEffect, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { writeHistory } from '../site/browserHistory.js'
import { documentTitle, setDocumentMeta } from '../site/documentMeta.js'
import {
  PARTIES, PARTY_COUNTS, PARTY_GROUPS, PARTY_SOURCES, PARTIES_AS_OF, assetClassLabel, eventLabel, formatPartyDate, isViewable,
  kindLabel, lineageOf, partyAsset, partyById, partyHistory, partyPlace, partySources, searchParties, statusLabel
} from './parties.js'
import './parties.css'

const assetUrl = (file) => `${import.meta.env.BASE_URL}${file.replace(/^\//, '')}`
const External = ({ children, ...props }) => <a {...props} target="_blank" rel="noreferrer">{children}<span aria-hidden="true"> ↗</span></a>
const SCOPES = ['artwork', 'gaps', 'all']
const readPlace = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const scope = params.get('party-scope')
  return { party: params.get('party') ?? '', query: params.get('party-query') ?? '', scope: SCOPES.includes(scope) ? scope : 'artwork' }
}
const preserved = (place) => ({ ...(place.query ? { 'party-query': place.query } : {}), ...(place.scope !== 'artwork' ? { 'party-scope': place.scope } : {}) })
/** An event's sources from the bibliography, plus any address it cites that the bibliography lacks. */
const eventSources = (event) => {
  const listed = event.sourceIds.map((id) => ({ id, ...PARTY_SOURCES[id] })).filter((source) => source.url)
  const urls = new Set(listed.map((source) => source.url))
  return [...listed, ...event.sourceUrls.filter((url) => !urls.has(url)).map((url) => ({ id: null, url, title: null }))]
}
/**
 * The date column keeps the source's own wording when it is short. A long one ("Official file
 * retrieved …; same design documented …") is shortened to its day or its years, and the full
 * wording is kept under the event.
 */
const shortDate = (event) => {
  if (event.dateLabel && event.dateLabel.length <= 30) return event.dateLabel
  if (!event.dateFrom) return event.dateLabel ?? 'Date unknown'
  if (!event.dateTo || event.dateTo === event.dateFrom) return formatPartyDate(event.dateFrom)
  const [from, to] = [event.dateFrom.slice(0, 4), event.dateTo.slice(0, 4)]
  return from === to ? from : `${from}–${to}`
}
const year = (date) => (date ? String(date).slice(0, 4) : '')
const kilobytes = (bytes) => (bytes >= 1e6 ? `${(bytes / 1e6).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1e3))} KB`)

const Preview = ({ asset, alt, className = '' }) => (
  <div className={`parties__preview ${className}`}>
    <img src={assetUrl(asset.preview)} alt={alt ?? asset.title} width={asset.previewSize[0]} height={asset.previewSize[1]} loading="lazy" />
  </div>
)

const Monogram = ({ party, className = '' }) => (
  <div className={`parties__preview parties__preview--empty ${className}`} aria-label="No artwork recovered">
    <span>{party.name.replace(/\(.*?\)|—.*$/g, '').split(/\s+/).filter((word) => /^[A-Z]/.test(word)).slice(0, 3).map((word) => word[0]).join('')}</span>
  </div>
)

const PartyCard = ({ party, place }) => (
  <SiteLink className="parties__card" to={partyPlace(party, preserved(place))}>
    {party.logo ? <Preview asset={party.logo} alt={`${party.name}: ${party.logo.title}`} /> : <Monogram party={party} />}
    <div className="parties__card-copy">
      <span className="parties__eyebrow">{statusLabel(party)}</span>
      <h3>{party.name}</h3>
      <p>{party.designs.length ? `${party.designs.length} ${party.designs.length === 1 ? 'design' : 'designs'}, ${year(party.designs[0].sortDate) || 'undated'}–${year(party.designs.at(-1).sortDate) || ''}` : party.summary}</p>
      <span className="parties__card-footer">{party.files ? `${party.files} logo ${party.files === 1 ? 'file' : 'files'}` : 'History and gaps'}<span aria-hidden="true">Explore →</span></span>
    </div>
  </SiteLink>
)

/** One lineage as a strip of its designs in order, each opening its party. */
const Lineage = ({ group, place }) => {
  const parties = new Map(group.parties.map((id) => [id, partyById(id)]))
  return (
    <section className="parties__lineage" aria-labelledby={`lineage-${group.id}`}>
      <div className="parties__lineage-head">
        <h3 id={`lineage-${group.id}`}>{group.title}</h3>
        <p>{group.intro}</p>
      </div>
      <ol className="parties__strip">
        {group.designs.map((design) => {
          const asset = partyAsset(design.representative)
          const party = parties.get(asset.party)
          return (
            <li key={design.id}>
              <SiteLink to={{ ...partyPlace(party, preserved(place)), 'party-design': design.id }} className="parties__strip-item">
                <Preview asset={asset} />
                <span className="parties__strip-date">{year(design.sortDate) || 'Undated'}</span>
                <span className="parties__strip-title">{group.parties.length > 1 ? `${party.name} · ` : ''}{kindLabel(asset)}</span>
              </SiteLink>
            </li>
          )
        })}
      </ol>
    </section>
  )
}

const VariantList = ({ design }) => (
  <ul className="parties__files">
    {design.assets.map((asset) => (
      <li key={asset.id}>
        {isViewable(asset) ? <Preview asset={asset} className="parties__file-thumb" /> : <div className="parties__file-thumb parties__file-thumb--eps" aria-hidden="true">{asset.format}</div>}
        <div>
          <strong>{asset.variant && asset.variant !== 'main' ? asset.variant.replace(/^./, (c) => c.toUpperCase()) : asset.title}</strong>
          <span className="parties__muted">{asset.format} · {kilobytes(asset.bytes)} · {assetClassLabel(asset)}</span>
          <span className="parties__file-links">
            <a href={assetUrl(asset.file)} download>Download {asset.format}</a>
            {asset.companions.map((file) => <a key={file} href={assetUrl(file)} download>Cropped PDF</a>)}
            {asset.source.url && <External href={asset.source.url}>{asset.source.id ? `${asset.source.id} · ` : ''}Source</External>}
          </span>
        </div>
      </li>
    ))}
  </ul>
)

const Design = ({ design, open }) => {
  const asset = design.representative
  return (
    <article className="parties__design" id={`design-${design.id}`} data-selected={open || undefined}>
      <Preview asset={asset} className="parties__design-image" />
      <div className="parties__design-copy">
        <p className="parties__eyebrow">{kindLabel(asset)} · {assetClassLabel(asset)}</p>
        <h4>{asset.title}</h4>
        <p className="parties__design-date"><strong>{asset.dateLabel}</strong> · confidence {asset.confidence}</p>
        {asset.dateBasis && <p className="parties__muted">{asset.dateBasis}</p>}
        {asset.notes && <p>{asset.notes}</p>}
        {asset.source.url && <p className="parties__source"><External href={asset.source.url}>{asset.source.title}</External>{asset.source.locator && <span> · {asset.source.locator}</span>}</p>}
        <details className="parties__variants" open={open || design.assets.length === 1 || undefined}>
          <summary>{design.assets.length === 1 ? 'The file' : `${design.assets.length} files: colourways and formats`}</summary>
          <VariantList design={design} />
          {asset.rights && <p className="parties__muted parties__rights">{asset.rights}</p>}
        </details>
      </div>
    </article>
  )
}

const PartyDetail = ({ party, place, design }) => {
  const lineage = lineageOf(party)
  const history = partyHistory(party)
  const sources = partySources(party)
  useEffect(() => {
    if (design) globalThis.document?.getElementById(`design-${design}`)?.scrollIntoView?.({ block: 'start' })
  }, [design])
  return (
    <article className="parties__detail">
      <SiteLink className="parties__back" to={partyPlace(null, preserved(place))}>← All parties</SiteLink>
      <header className="parties__detail-head">
        <div>
          <p className="parties__eyebrow">British Columbia · {statusLabel(party)}</p>
          <h2>{party.name}</h2>
          {party.aliases.length > 0 && <p className="parties__detail-subtitle">Also {party.aliases.join(' · ')}</p>}
          <p>{party.summary}</p>
          <div className="parties__facts">
            <div><span>Designs</span><strong>{party.designs.length || 'None recovered'}</strong></div>
            <div><span>Logo files</span><strong>{party.files || '—'}</strong></div>
            <div><span>Earliest dated use</span><strong>{party.earliestUse ? formatPartyDate(party.earliestUse) : party.earliestFile ? `File ${formatPartyDate(party.earliestFile)}` : 'Not established'}</strong></div>
            <div><span>Events recorded</span><strong>{history.length}</strong></div>
          </div>
        </div>
        {party.logo ? <Preview asset={party.logo} className="parties__hero" /> : <Monogram party={party} className="parties__hero" />}
      </header>
      {lineage && lineage.members.length > 1 && (
        <nav className="parties__related" aria-label="Same lineage">
          <span className="parties__eyebrow">{lineage.title}</span>
          {lineage.members.map((member) => member.id === party.id
            ? <strong key={member.id} aria-current="page">{member.name}</strong>
            : <SiteLink key={member.id} to={partyPlace(member, preserved(place))}>{member.name}</SiteLink>)}
        </nav>
      )}
      <nav className="parties__section-nav" aria-label="Party sections"><a href="#party-logos">Logos</a><a href="#party-history">History</a><a href="#party-gaps">Gaps</a><a href="#party-sources">Sources</a></nav>

      <section className="parties__section" id="party-logos" aria-labelledby="party-logos-title">
        <div className="parties__section-heading"><div><p className="parties__eyebrow">Oldest first</p><h3 id="party-logos-title">Logos and designs</h3></div></div>
        {party.designs.length
          ? <div className="parties__designs">{party.designs.map((entry) => <Design key={entry.id} design={entry} open={entry.id === design} />)}</div>
          : <p className="parties__empty">No artwork has been authenticated for this party. {party.gaps[0] ?? ''}</p>}
        <p className="parties__caption">A dated specimen proves use on that day, not adoption. A Commons upload, a file’s metadata or a year in its name dates the file, not the design. Colourways and formats of one arrangement are grouped as one design.</p>
      </section>

      <section className="parties__section" id="party-history" aria-labelledby="party-history-title">
        <div className="parties__section-heading"><div><p className="parties__eyebrow">Names, formations and observations</p><h3 id="party-history-title">History</h3></div></div>
        {history.length ? (
          <ol className="parties__timeline">
            {history.map((event) => (
              <li key={event.id} data-visual={event.visual || undefined}>
                <div className="parties__timeline-date"><span>{shortDate(event)}</span><span className="parties__chip">{eventLabel(event)}</span></div>
                <div className="parties__timeline-event">
                  <p>{event.description}</p>
                  {shortDate(event) !== event.dateLabel && event.dateLabel && <p className="parties__muted">Date: {event.dateLabel}</p>}
                  {event.qualification && <p className="parties__muted">{event.qualification}</p>}
                  {event.parties.length > 1 && (
                    <p className="parties__muted">Also concerns {event.parties.filter((id) => id !== party.id).map((id, i) => {
                      const other = partyById(id)
                      return <span key={id}>{i ? ', ' : ''}{other ? <SiteLink to={partyPlace(other, preserved(place))}>{other.name}</SiteLink> : id}</span>
                    })}</p>
                  )}
                  <p className="parties__source">{eventSources(event).map((source, i) => <span key={source.url}>{i ? ' · ' : ''}<External href={source.url}>{source.id ? `${source.id} · ` : ''}{source.title ?? 'Source'}</External></span>)}</p>
                </div>
              </li>
            ))}
          </ol>
        ) : <p className="parties__empty">No organizational events are recorded for this party yet.</p>}
      </section>

      <section className="parties__section" id="party-gaps" aria-labelledby="party-gaps-title">
        <div className="parties__section-heading"><div><p className="parties__eyebrow">What is still open</p><h3 id="party-gaps-title">Gaps</h3></div></div>
        {party.notes && <p>{party.notes}</p>}
        {party.datesNote && <p className="parties__muted">{party.datesNote}</p>}
        {party.gaps.length ? <ul className="parties__gaps">{party.gaps.map((gap) => <li key={gap}>{gap}</li>)}</ul> : <p className="parties__muted">No gaps are recorded.</p>}
        <p className="parties__caption">An absence here means no authenticated artwork was found, not that the party never used a logo.</p>
      </section>

      <section className="parties__section" id="party-sources" aria-labelledby="party-sources-title">
        <div className="parties__section-heading"><div><p className="parties__eyebrow">Follow the evidence</p><h3 id="party-sources-title">Sources</h3></div></div>
        <ol className="parties__sources">{sources.map((source) => <li key={`${source.id}-${source.url}`}>{source.id && <span className="parties__source-id">{source.id}</span>}<External href={source.url}>{source.title ?? source.url}</External></li>)}</ol>
      </section>
    </article>
  )
}

export const PartiesView = () => {
  const [place, setPlace] = useState(readPlace)
  const selected = partyById(place.party)
  const design = new URLSearchParams(globalThis.location?.search ?? '').get('party-design')
  useEffect(() => {
    const restore = () => setPlace(readPlace())
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [])
  useEffect(() => setDocumentMeta({
    title: documentTitle(selected ? `${selected.name} · Political parties` : 'Political parties'),
    description: 'British Columbia’s provincial political parties: their logos over time, name changes and formations, with sources and open gaps.'
  }), [selected])
  const changeFilters = (patch) => {
    const next = { ...place, ...patch }
    setPlace(next)
    const url = new URL(globalThis.location.href)
    url.search = new URLSearchParams(partyPlace(null, preserved(next))).toString()
    url.hash = ''
    writeHistory(url, { replace: true })
  }

  if (place.party && !selected) {
    return <main className="parties"><div className="parties__empty"><h2>Party not found</h2><p>This address does not identify a party in the collection.</p><SiteLink to={partyPlace()}>Browse all parties →</SiteLink></div></main>
  }
  if (selected) return <main className="parties"><PartyDetail party={selected} place={place} design={design} /></main>

  const results = searchParties(place)
  return (
    <main className="parties">
      <header className="parties__intro">
        <div>
          <p className="parties__eyebrow">Provincial politics · British Columbia</p>
          <h2>Political parties,<br />by the marks they used.</h2>
          <p>The parties that governed, formed the Official Opposition or held seats in the Legislature, from the pre-1903 alignments to today: their logos in the order they appear, and the formations and renamings behind them.</p>
        </div>
        <div className="parties__stats">
          <div><strong>{PARTY_COUNTS.parties}</strong><span>parties and labels recorded</span></div>
          <div><strong>{PARTY_COUNTS.withArtwork}</strong><span>with recovered artwork</span></div>
          <div><strong>{PARTY_COUNTS.designs}</strong><span>designs in {PARTY_COUNTS.files} files</span></div>
          <div><strong>{PARTY_COUNTS.sources}</strong><span>sources</span></div>
        </div>
      </header>

      <section className="parties__lineages" aria-label="Lineages">
        {PARTY_GROUPS.map((group) => <Lineage key={group.id} group={group} place={place} />)}
      </section>

      <div className="parties__toolbar">
        <label className="parties__search"><span>Find a party</span><input type="search" value={place.query} onChange={(event) => changeFilters({ query: event.target.value })} placeholder="Name or earlier name" /></label>
        <label className="parties__scope"><span>Show</span>
          <select value={place.scope} onChange={(event) => changeFilters({ scope: event.target.value })}>
            <option value="artwork">Parties with artwork</option>
            <option value="gaps">Parties without artwork</option>
            <option value="all">All parties and labels</option>
          </select>
        </label>
        <p role="status">{results.length} {results.length === 1 ? 'party' : 'parties'}</p>
      </div>
      <div className="parties__grid">{results.map((party) => <PartyCard key={party.id} party={party} place={place} />)}</div>
      {!results.length && <div className="parties__empty"><h3>No matching parties</h3><p>Try an earlier name, or include parties without artwork.</p><button type="button" onClick={() => changeFilters({ query: '', scope: 'all' })}>Show all parties</button></div>}

      <footer className="parties__about">
        <div>
          <h3>Dated use, file dates and events are kept apart.</h3>
          <p>A newspaper advertisement dates a mark’s use on one day; a Commons upload or a file’s metadata dates the file; a registered-name change is an organizational event. None is read as another. No missing logo has been traced, redrawn or generated.</p>
          <p className="parties__muted">Collected {formatPartyDate(PARTIES_AS_OF)}. Party marks belong to their parties; they are shown here for identification and research, without endorsement.</p>
        </div>
        <div className="parties__about-links">
          <a href={assetUrl('parties/catalogue.json')} download>Download the sourced catalogue</a>
          <SiteLink to={{ view: 'government' }}>Premiers and seats in Government →</SiteLink>
        </div>
      </footer>
    </main>
  )
}
