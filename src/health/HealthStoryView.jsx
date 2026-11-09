import { useCallback, useMemo, useState } from 'react'
import { HealthAtlasMap } from './HealthAtlasMap.jsx'
import { useHealthGeography } from './useHealthGeography.js'
import {
  AREAS, BOUNDARIES, CONSOLIDATION_SOURCE, FRAMEWORKS, OVERLAY_MAP, SOURCE_REPORT, STATCAN_MAP,
  areaById, areasIn, assetUrl, filterAreas, formatDate, frameworkById, readHealthPlace, relatedAreas,
} from './healthStoryData.js'
import { SiteLink } from '../site/navigation.jsx'
import './healthStory.css'

const asset = (path) => assetUrl(path, import.meta.env.BASE_URL)
const km = (metres) => (metres / 1000).toLocaleString('en-CA', { maximumFractionDigits: 1, minimumFractionDigits: 1 })
const PANEL_LABELS = {
  boards: 'Regional boards, main map', 'boards-inset-mainland': 'Regional boards, Lower Mainland inset',
  'boards-inset-island': 'Regional boards, south Vancouver Island inset', councils: 'Community councils',
  societies: 'Service societies', 'regions-2000': 'Statistical regions, main map', 'regions-2000-inset': 'Statistical regions, southwest inset',
}

function External({ href, children, className }) {
  return <a className={className} href={href} target="_blank" rel="noreferrer">{children}<span aria-hidden="true"> ↗</span></a>
}

// The area in another framework that shares the most local health areas.
function counterpartIn(area, framework) {
  const candidates = areasIn(framework)
  if (!area) return candidates[0]
  let best = null
  let bestShared = 0
  for (const candidate of candidates) {
    const shared = candidate.lhaCodes.filter((code) => area.lhaCodes.includes(code)).length
    if (shared > bestShared) { best = candidate; bestShared = shared }
  }
  return best ?? candidates[0]
}

function fitLabel(area) {
  if (area.framework === 'authorities-2001') return 'Rebuilt from the organizations that amalgamated into it'
  const overlap = Math.round(area.drawingOverlap * 100)
  return `${overlap}% overlap with the printed map`
}

function AreaDetails({ area, onSelect }) {
  if (!area) return <aside className="hm-details hm-details--empty"><p>Select an area on the map or in the list to see the organization and its boundary.</p></aside>
  const framework = frameworkById(area.framework)
  const org = area.organization
  const groups = relatedAreas(area)
  const historyYear = area.framework === 'authorities-2001' ? 2002 : 1998
  return <aside className="hm-details" aria-labelledby="hm-details-title">
    <p className="hm-kicker">{framework.kind}{area.legendNumber ? ` · map no. ${area.legendNumber}` : ''}</p>
    <h3 id="hm-details-title">{area.name}</h3>
    {org && org.officialName !== area.name && <p className="hm-official">{org.officialName}</p>}
    {!org && area.framework === 'councils' && <p className="hm-official">Shown on the 1997/98 council map, but not designated under the Health Authorities Act. It is not linked to an organization record.</p>}
    {org && <dl className="hm-facts">
      {(org.established || org.ended) && <div><dt>{org.ended ? 'Active' : 'Established'}</dt><dd>{formatDate(org.established) ?? 'Unknown'}{org.ended ? ` – ${formatDate(org.ended)}` : ''}</dd></div>}
      {org.formerNames?.length > 0 && <div><dt>Earlier names</dt><dd>{org.formerNames.join(' · ')}</dd></div>}
    </dl>}
    {!org && area.framework === 'regions-2000' && <p className="hm-official">A reporting region used by Statistics Canada, not an organization.</p>}
    <div className="hm-boundary">
      <p className="hm-kicker">Boundary</p>
      <p><b>{area.areaKm2.toLocaleString('en-CA')} km²</b> · made of {area.lhaCodes.length} local health area{area.lhaCodes.length === 1 ? '' : 's'}</p>
      <ul className="hm-lha-list">{area.lhaNames.map((name, index) => <li key={area.lhaCodes[index]}>{name}</li>)}</ul>
      <p className={`hm-fit hm-fit--${area.confidence}`}>{area.framework !== 'authorities-2001' && <span>{area.confidence === 'high' ? 'Close fit' : 'Approximate fit'}</span>}{fitLabel(area)}</p>
      {area.note && <p className="hm-note">{area.note}</p>}
    </div>
    {groups.map((group) => <div className="hm-related" key={group.label}>
      <p className="hm-kicker">{group.label}</p>
      <div className="hm-chips">{group.areas.map((related) => <button type="button" key={related.id} onClick={() => onSelect(related.id)}>{related.name}</button>)}</div>
    </div>)}
    <div className="hm-links">
      {org && <SiteLink to={{ view: 'government', node: org.bodyId, year: historyYear }}>Organization history →</SiteLink>}
      <External href={framework.source.url}>Printed source</External>
    </div>
  </aside>
}

function AccuracyTable() {
  const rows = BOUNDARIES.panels
  return <div className="hm-table-wrap"><table className="hm-table">
    <caption>Typical distance between a printed boundary and the modern line it was matched to, measured on parts of each map held out of the fit.</caption>
    <thead><tr><th scope="col">Map panel</th><th scope="col">Typical error</th><th scope="col">Nine in ten within</th><th scope="col">Earlier 3-point fit</th></tr></thead>
    <tbody>{rows.map((row) => <tr key={row.id}>
      <th scope="row">{PANEL_LABELS[row.id] ?? row.id}</th>
      <td>{km(row.heldOut.medianMetres)} km</td>
      <td>{km(row.heldOut.p90Metres)} km</td>
      <td>{row.seedAffineBaseline ? `${km(row.seedAffineBaseline.medianMetres)} km` : '—'}</td>
    </tr>)}</tbody>
  </table></div>
}

export function HealthStoryView() {
  const [initial] = useState(() => readHealthPlace(globalThis.location?.search))
  const [framework, setFramework] = useState(initial.framework)
  const [selectedId, setSelectedId] = useState(initial.area)
  const [overlayOn, setOverlayOn] = useState(false)
  const [opacity, setOpacity] = useState(.8)
  const [query, setQuery] = useState('')
  const [chosenFilter, setFilter] = useState(null)
  const overlayMap = OVERLAY_MAP[framework]
  const geo = useHealthGeography(framework, overlayOn && overlayMap ? overlayMap : null)
  const selected = areaById(selectedId)
  const current = frameworkById(framework)
  // The list follows the map on screen until the reader picks a filter.
  const filter = chosenFilter ?? (query ? 'all' : framework)
  const results = useMemo(() => filterAreas(query, filter), [query, filter])

  const writePlace = useCallback((nextFramework, nextArea) => {
    if (!globalThis.history?.replaceState) return
    const url = new URL(globalThis.location.href)
    url.searchParams.set('view', 'health-map')
    url.searchParams.set('layer', nextFramework)
    if (nextArea) url.searchParams.set('area', nextArea)
    else url.searchParams.delete('area')
    url.searchParams.delete('chapter')
    globalThis.history.replaceState(null, '', url)
  }, [])
  const select = useCallback((id) => {
    const area = areaById(id)
    if (!area) return
    setFramework(area.framework)
    setSelectedId(area.id)
    writePlace(area.framework, area.id)
  }, [writePlace])
  const chooseFramework = (id) => {
    const next = counterpartIn(selected, id)
    setFramework(id)
    setSelectedId(next?.id ?? null)
    writePlace(id, next?.id)
  }
  const showInAtlas = (id) => {
    select(id)
    document.getElementById('hm-atlas')?.scrollIntoView({ block: 'start', behavior: globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
  }

  return <main className="health-story hm">
    <header className="hm-header">
      <p className="hm-kicker">Historical atlas · British Columbia</p>
      <h1>How BC’s health map changed</h1>
      <p className="hm-lede">Before five health authorities took over in December 2001, BC’s health services were run by regional boards, community councils and service societies. These maps put each of those organizations back on the map, with its dates, its earlier names and what it became.</p>
    </header>

    <section id="hm-atlas" className="hm-atlas" aria-labelledby="hm-atlas-title">
      <h2 id="hm-atlas-title" className="hm-visually-hidden">Map of historical health organizations</h2>
      <div className="hm-tabs" role="tablist" aria-label="Choose a historical map">
        {FRAMEWORKS.map((entry) => <button type="button" role="tab" key={entry.id} aria-selected={entry.id === framework} onClick={() => chooseFramework(entry.id)}>
          <span>{entry.year}</span>{entry.label}
        </button>)}
      </div>
      <div className="hm-intro"><h3>{current.title}</h3><p>{current.blurb}</p></div>
      <div className="hm-grid">
        <div className="hm-map-column">
          {geo.phase === 'error' ? <div className="hm-loading" role="alert"><p>{geo.error}</p><button type="button" className="hm-button" onClick={geo.retry}>Try again</button></div>
            : !geo.regions ? <div className="hm-loading" role="status"><p>Loading the map…</p></div>
              : <HealthAtlasMap base={geo.base} regions={geo.regions} overlay={overlayOn ? geo.overlay : null} overlayOpacity={opacity}
                selectedId={selectedId} onSelect={select} frameworkLabel={current.title} />}
          <div className="hm-map-options">
            {overlayMap ? <>
              <label className="hm-toggle"><input type="checkbox" checked={overlayOn} onChange={(event) => setOverlayOn(event.target.checked)} /> Show the original printed map, georectified</label>
              {overlayOn && <label className="hm-range">Opacity <input type="range" min=".2" max="1" step=".05" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} aria-label="Original map opacity" /></label>}
              {overlayOn && geo.phase === 'updating' && <span className="hm-small" role="status">Loading the original map…</span>}
            </> : <span className="hm-small">This layer is rebuilt from its predecessor organizations, so it has no printed map.</span>}
          </div>
        </div>
        <AreaDetails area={selected?.framework === framework ? selected : null} onSelect={select} />
      </div>
    </section>

    <section className="hm-directory" aria-labelledby="hm-directory-title">
      <div className="hm-section-heading"><div><p className="hm-kicker">Every organization</p><h2 id="hm-directory-title">Find a board, council, society or region</h2></div><span className="hm-count">{results.length} of {AREAS.length}</span></div>
      <div className="hm-filters">
        <label className="hm-field"><span>Search names and places</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Cariboo, Nelson, Richmond…" /></label>
        <label className="hm-field"><span>Map</span><select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="all">All maps</option>{FRAMEWORKS.map((entry) => <option key={entry.id} value={entry.id}>{entry.year} · {entry.label}</option>)}</select></label>
      </div>
      {FRAMEWORKS.filter((entry) => results.some((area) => area.framework === entry.id)).map((entry) => <div className="hm-group" key={entry.id}>
        <h3>{entry.year} · {entry.label}</h3>
        <ul className="hm-cards">{results.filter((area) => area.framework === entry.id).map((area) => <li key={area.id}>
          <button type="button" className={area.id === selectedId ? 'is-selected' : undefined} onClick={() => showInAtlas(area.id)}>
            <i className={`hm-swatch hm-c${area.colour ?? 0}`} aria-hidden="true" />
            <span className="hm-card-name">{area.legendNumber ? <b>{area.legendNumber}</b> : null}{area.name}</span>
            <span className="hm-card-meta">{area.organization?.ended ? `${area.organization.established?.slice(0, 4) ?? '?'}–${area.organization.ended.slice(0, 4)}` : area.framework === 'regions-2000' ? 'Statistical region' : area.organization ? `Since ${area.organization.established?.slice(0, 4)}` : 'No organization record'}</span>
          </button>
        </li>)}</ul>
      </div>)}
      {!results.length && <p className="hm-small" role="status">Nothing matches that search. <button type="button" className="hm-link-button" onClick={() => { setQuery(''); setFilter('all') }}>Clear the search</button></p>}
    </section>

    <section className="hm-method" aria-labelledby="hm-method-title">
      <div className="hm-section-heading"><div><p className="hm-kicker">Method</p><h2 id="hm-method-title">How these boundaries were made</h2></div></div>
      <ol className="hm-steps">
        <li><b>Georectify the printed maps.</b> The three 1997/98 Ministry maps (published by the Auditor General in March 1998) and the Statistics Canada map were fitted onto modern BC geography. Thousands of points along each printed boundary were matched to the coast, the provincial border and modern local health area (LHA) edges, and each map panel, including the enlarged insets, was warped to fit.</li>
        <li><b>Snap each printed region to local health areas.</b> Health regions were built from LHAs, so every LHA that falls at least half inside a printed region is assigned to it. Two exceptions, where a legal boundary description settles a detail the printed map is too small to show, are noted on those areas.</li>
        <li><b>Check the result.</b> Nothing forced these to agree, yet the 11 boards and 34 councils cover all 89 LHAs exactly once, the 20 statistical regions do too, and each society is exactly the councils it served.</li>
      </ol>
      <AccuracyTable />
      <p className="hm-small">Boundaries use today’s LHA lines. Where a 1997 edge did not follow one, the true line can differ locally. The statistical layer also corrects an earlier mix-up: New Westminster belongs to Simon Fraser (region 08) and Burnaby is region 17.</p>
      <div className="hm-downloads">
        <a className="hm-button hm-button--quiet" href={asset('historical-boundaries.geojson')} download>Download all boundaries (GeoJSON) ↓</a>
        <a href={asset('georectification.json')} download>Fit and LHA-share report ↓</a>
        <a href={asset('maps/BC-health-area-maps-1997-98.pdf')} download>Original 1997/98 map pages ↓</a>
      </div>
    </section>

    <section className="hm-sources" aria-labelledby="hm-sources-title">
      <h2 id="hm-sources-title">Sources</h2>
      <ul>
        <li><External href={`${SOURCE_REPORT}#page=28`}>BC Auditor General, <i>A Review of Governance and Accountability in the Regionalization of Health Services</i>, 1997/98 Report 3, Exhibits 3–5</External> — maps credited to the Ministry of Health and Ministry Responsible for Seniors, March 1998.</li>
        <li><External href={STATCAN_MAP}>Statistics Canada, <i>Health Indicators</i>, April 2001, BC health regions map</External> — reproduced and distributed on an “as is” basis with the permission of Statistics Canada.</li>
        <li><External href={CONSOLIDATION_SOURCE}>B.C. Reg. 293/2001, Regional Health Boards Regulation</External> — names the organizations amalgamated into each authority.</li>
        <li><External href="https://catalogue.data.gov.bc.ca/dataset/local-health-area-boundaries">BC Ministry of Health local health area boundaries</External> via <External href="https://github.com/ahzs645/PGMaps">PGMaps</External> — Open Government Licence – British Columbia.</li>
      </ul>
    </section>
  </main>
}

export default HealthStoryView
