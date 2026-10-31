import { useCallback, useMemo, useState } from 'react'
import StoryFrame from './StoryFrame.jsx'
import { BoundaryMap } from './BoundaryMap.jsx'
import { useBoundaryData } from './useBoundaryData.js'
import {
  AREAS, CATALOGUE, CHAPTERS, DEFAULT_AREA_ID, PUBLIC_SOURCES, SOURCE_REPORT,
  CONSOLIDATION_SOURCE, areaById, areasIn, assetUrl, candidateCodes,
  comparisonFor, evidenceLabel, filterAreas, mapById, readHealthPlace,
} from './healthStoryData.js'
import { SiteLink } from '../site/navigation.jsx'
import './healthStory.css'

const asset = (path) => assetUrl(path, import.meta.env.BASE_URL)
const groupLabels = { boards: 'Regional boards', councils: 'Community councils', societies: 'Service societies' }
const formatCodes = (codes) => codes.length ? codes.join(', ') : 'None proposed'

function SourceLink({ href, children }) {
  return <a href={href} target="_blank" rel="noreferrer">{children}<span aria-hidden="true"> ↗</span></a>
}

function ArchiveMap({ map, area }) {
  const [zoom, setZoom] = useState(1)
  const selected = area?.mapId === map.id ? area : null
  return <figure className="health-archive">
    <div className="health-media-heading"><div><span className="health-kicker">Original published map</span><h3>{map.title}</h3></div><span className="health-date">{map.dateLabel}</span></div>
    {selected && <p className="health-archive-selection"><b>{selected.number}</b><span>{selected.sourceLabel}<small>Number in the original legend</small></span></p>}
    <div className="health-archive-viewport" tabIndex={0} aria-label={`${map.title}, scroll to inspect the enlarged map`}>
      <img src={asset(map.asset)} alt={`${map.title}. ${map.dateLabel}. Geographic areas are numbered; the complete legend is in the image and the area index below.`} draggable={false} style={{ width: `${zoom * 100}%`, height: `${zoom * 100}%` }} />
    </div>
    <figcaption className="health-archive-caption">
      <div className="health-map-zoom" aria-label="Original map zoom">
        <button type="button" aria-label="Enlarge original map" disabled={zoom >= 3} onClick={() => setZoom((value) => Math.min(3, value + .5))}>+</button>
        <button type="button" aria-label="Reduce original map" disabled={zoom <= 1} onClick={() => setZoom((value) => Math.max(1, value - .5))}>−</button>
        <button type="button" onClick={() => setZoom(1)}>Fit page</button>
      </div>
      <SourceLink href={map.sourceUrl}>Original source{map.printedPage ? ` · page ${map.printedPage}` : ''}</SourceLink>
      <span className="health-map-credit">{map.credit}</span>
    </figcaption>
  </figure>
}

function AreaPicker({ mapId, selected, onSelect, id }) {
  return <label className="health-field" htmlFor={id}><span>Find an area on this map</span>
    <select id={id} value={selected?.mapId === mapId ? selected.id : ''} onChange={(event) => { if (event.target.value) onSelect(event.target.value) }}>
      <option value="">Choose an area…</option>
      {areasIn(mapId).map((area) => <option key={area.id} value={area.id}>{area.number}. {area.sourceLabel}</option>)}
    </select>
  </label>
}

function AreaEvidence({ area, match, onCompare, compact = false }) {
  if (!area) return null
  return <section className={`health-area-evidence${compact ? ' is-compact' : ''}`} aria-label={`Evidence for ${area.sourceLabel}`}>
    <p className="health-kicker">{groupLabels[area.mapId]} · map area {area.number}</p>
    <h3>{area.sourceLabel}</h3><p className="health-muted">{area.name}</p>
    {!area.identityConfirmed && <p className="health-notice">This source labels a Nisga’a health authority. Its relationship to the separately recorded statutory council remains unresolved.</p>}
    {match && <><span className="health-evidence-badge">{evidenceLabel(match)}</span><p>{match.explanation}</p></>}
    {area.legalDefinition && <p className="health-small"><SourceLink href={area.legalDefinition.sourcePageUrl}>Written boundary · PDF pages {area.legalDefinition.pdfPageStart}–{area.legalDefinition.pdfPageEnd}</SourceLink></p>}
    <div className="health-actions">
      {onCompare && <button type="button" className="health-button" onClick={() => onCompare(area.id)}>Compare existing boundaries</button>}
      {area.bodyId && <SiteLink to={{ view: 'government', node: area.bodyId, year: 1997 }} className="health-text-link">Organization history →</SiteLink>}
      <SourceLink href={area.sourceUrl}>Source map</SourceLink>
    </div>
    {!compact && <details className="health-details"><summary>Names and evidence notes</summary><ul>{area.notes.map((note, index) => <li key={index}>{note}</li>)}</ul></details>}
  </section>
}

function BoundaryLoading({ data }) {
  return <div className="health-loading" role="status"><p>{data.phase === 'error' ? data.error : 'Loading the boundary comparison…'}</p>
    {data.phase === 'error' && <button type="button" className="health-button" onClick={data.retry}>Retry boundary data</button>}
    <p className="health-small">The original maps remain available in the earlier chapters and downloads.</p>
  </div>
}

function ComparisonMedia({ data, area, layer, setLayer, onFeatureSelect }) {
  const [view, setView] = useState('boundaries')
  const match = comparisonFor(data.comparison, area.id)
  const selectedCodes = useMemo(() => candidateCodes(match, layer), [match, layer])
  return <div className="health-comparison-media">
    <div className="health-media-tabs" role="group" aria-label="Comparison display">
      {[['boundaries', 'Existing boundaries'], ['archive', 'Original map'], ['both', 'Side by side']].map(([id, label]) => <button type="button" key={id} aria-pressed={view === id} onClick={() => setView(id)}>{label}</button>)}
    </div>
    <div className={`health-comparison-panes${view === 'both' ? ' is-split' : ''}`}>
      {view !== 'archive' && <section className="health-current-pane" aria-label="Existing PGMaps boundary comparison">
        <div className="health-media-heading"><div><span className="health-kicker">PGMaps comparison layer</span><h3>{area.sourceLabel}</h3></div>
          <select aria-label="Existing boundary layer" value={layer} onChange={(event) => setLayer(event.target.value)}><option value="lha">Local health areas</option><option value="hsda">Service delivery areas</option><option value="ha">Health authorities</option></select>
        </div>
        {data.phase !== 'ready' ? <BoundaryLoading data={data} /> : <BoundaryMap collections={data.collections} layer={layer} selectedCodes={selectedCodes} selectedName={area.sourceLabel} onFeatureSelect={onFeatureSelect} />}
        <p className="health-map-credit">Modern PGMaps geography. A highlighted candidate does not establish the historical legal boundary.</p>
      </section>}
      {view !== 'boundaries' && <ArchiveMap key={area.mapId} map={mapById(area.mapId)} area={area} />}
    </div>
  </div>
}

function CurrentAuthorityMap({ data }) {
  const [chosen, setChosen] = useState(null)
  const codes = useMemo(() => new Set(chosen ? [String(chosen.properties.code)] : []), [chosen])
  return <section className="health-current-pane">
    <div className="health-media-heading"><div><span className="health-kicker">Present-day context</span><h3>Five geographic health authorities</h3></div><span className="health-date">Current PGMaps layer</span></div>
    {data.phase !== 'ready' ? <BoundaryLoading data={data} /> : <BoundaryMap collections={data.collections} layer="ha" selectedCodes={codes} selectedName={chosen?.properties.name} onFeatureSelect={setChosen} contextOnly />}
    <p className="health-map-credit">This modern map provides context. It is not asserted to show the boundaries on 12 December 2001; later transfers also changed the geography.</p>
  </section>
}

export function HealthStoryView() {
  const [initial] = useState(() => readHealthPlace(globalThis.location?.search))
  const [chapter, setChapter] = useState(initial.chapter)
  const [requestedChapter, setRequestedChapter] = useState(initial.chapter)
  const [navigationRequestKey, setNavigationRequestKey] = useState(0)
  const [selectedId, setSelectedId] = useState(initial.area)
  const [layer, setLayer] = useState('lha')
  const [query, setQuery] = useState('')
  const [group, setGroup] = useState('all')
  const [copied, setCopied] = useState(false)
  const [copyFailed, setCopyFailed] = useState(false)
  const [clickedFeature, setClickedFeature] = useState(null)
  const [loadComparison, setLoadComparison] = useState(['compare-boundaries', 'consolidation'].includes(initial.chapter))
  const data = useBoundaryData(loadComparison)
  const selected = areaById(selectedId) ?? areaById(DEFAULT_AREA_ID)
  const match = comparisonFor(data.comparison, selected.id)
  const filteredAreas = useMemo(() => filterAreas(query, group), [query, group])

  const writePlace = useCallback((nextChapter, nextArea) => {
    if (!globalThis.history?.replaceState) return
    const url = new URL(globalThis.location.href)
    url.searchParams.set('view', 'health-map')
    url.searchParams.set('chapter', nextChapter)
    url.searchParams.set('area', nextArea)
    globalThis.history.replaceState(null, '', url)
    setCopied(false)
    setCopyFailed(false)
  }, [])
  const chooseArea = useCallback((id) => {
    if (!areaById(id)) return
    setSelectedId(id)
    setClickedFeature(null)
    writePlace(chapter, id)
  }, [chapter, writePlace])
  const compareArea = useCallback((id) => {
    chooseArea(id)
    setLoadComparison(true)
    setRequestedChapter('compare-boundaries')
    setNavigationRequestKey((value) => value + 1)
    setChapter('compare-boundaries')
    writePlace('compare-boundaries', id)
    document.getElementById('health-story-frame')?.scrollIntoView({ block: 'start', behavior: globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
  }, [chooseArea, writePlace])
  const onChapterChange = useCallback((id) => {
    setChapter(id)
    if (id === 'compare-boundaries' || id === 'consolidation') setLoadComparison(true)
    writePlace(id, selectedId)
  }, [selectedId, writePlace])
  const onFeatureSelect = useCallback((feature, featureLayer) => setClickedFeature({ code: String(feature.properties.code), name: feature.properties.name, layer: featureLayer }), [])
  const copyLink = async () => {
    try { await navigator.clipboard.writeText(globalThis.location.href); setCopied(true); setCopyFailed(false) }
    catch { setCopied(false); setCopyFailed(true) }
  }
  const matchSources = (match?.sourceIds ?? []).map((id) => data.comparison?.sources?.find((source) => source.id === id)).filter(Boolean)
  const relatedToClick = clickedFeature ? AREAS.filter((area) => candidateCodes(comparisonFor(data.comparison, area.id), clickedFeature.layer).has(clickedFeature.code)) : []
  const selectedFor = (mapId) => selected.mapId === mapId ? selected : areasIn(mapId)[0]
  const chapterTitle = (number, title, date) => <><p className="health-chapter-date">Chapter {number} · {date}</p><h2>{title}</h2></>
  const choose = (mapId) => <AreaPicker mapId={mapId} selected={selected} onSelect={chooseArea} id={`choose-${mapId}`} />
  const evidence = (mapId) => <AreaEvidence area={selectedFor(mapId)} match={comparisonFor(data.comparison, selectedFor(mapId).id)} onCompare={compareArea} compact />

  const slides = [
    { ...CHAPTERS[0], imageUrl: asset(mapById('regions-2000').asset), content: <>
      {chapterTitle('01', 'A different health map', '1995–2000')}
      <p className="health-lead">Before the five geographic authorities, British Columbia had a much more local health system.</p>
      <p>A 1995 order designated twenty regional boards. The statistical map published in April 2001 preserves twenty analytical health regions, including separate Vancouver, Richmond, Burnaby and Simon Fraser areas.</p>
      <p className="health-notice">Statistical regions generally coincided with boards, but were not a complete statement of their legal territories. Keep the two kinds of evidence together.</p>
      <div className="health-story-facts"><span><b>20</b> earlier boards</span><span><b>1997</b> reorganization</span><span><b>2001</b> consolidation</span></div>
      <p><SourceLink href="https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0597_1995#page=2">1995 designation and boundary schedule</SourceLink></p>
      <details className="health-details"><summary>Written boundaries for the twenty boards</summary><ul className="health-source-list">{CATALOGUE.earlierBoards.map((row) => <li key={row.name}><SourceLink href={row.link}>{row.name}</SourceLink><small>PDF pages {row.pdf_pages.join('–')}</small></li>)}</ul></details>
    </>, media: <ArchiveMap key="regions-2000" map={mapById('regions-2000')} /> },
    { ...CHAPTERS[1], imageUrl: asset(mapById('boards').asset), content: <>
      {chapterTitle('02', 'Eleven regional boards', '1997 restructuring')}
      <p className="health-lead">The regional boards covered these eleven areas. The rest of the province had a different arrangement.</p>
      <p>The original Ministry map gives each board a number. Choose one to connect its geographic area with the organization’s history and its written boundary definition.</p>
      {choose('boards')}{evidence('boards')}
      <p className="health-small"><SourceLink href={`${SOURCE_REPORT}#page=28`}>Original map · exhibit 3</SourceLink></p>
    </>, media: <ArchiveMap key="boards" map={mapById('boards')} area={selectedFor('boards')} /> },
    { ...CHAPTERS[2], imageUrl: asset(mapById('councils').asset), content: <>
      {chapterTitle('03', 'Care closer to home', 'Community councils')}
      <p className="health-lead">Local councils served communities outside the regional-board areas.</p>
      <p>This map contains 34 numbered entries. Thirty-three have a confirmed institutional name match here; the separately labelled Nisga’a area retains its unresolved identity note.</p>
      {choose('councils')}{evidence('councils')}
      <p className="health-small"><SourceLink href={`${SOURCE_REPORT}#page=29`}>Original map · exhibit 4</SourceLink></p>
    </>, media: <ArchiveMap key="councils" map={mapById('councils')} area={selectedFor('councils')} /> },
    { ...CHAPTERS[3], imageUrl: asset(mapById('societies').asset), content: <>
      {chapterTitle('04', 'Shared community services', 'Seven service societies')}
      <p className="health-lead">The societies linked multiple local council areas through community health services.</p>
      <p>Their geography overlaps the council areas they served. Showing them as a separate layer preserves that relationship.</p>
      {choose('societies')}{evidence('societies')}
      <p className="health-small">The map’s “Central Kootenay” label is retained as the earlier name of Kootenay Boundary. North West’s source map explicitly excludes the Nisga’a health authority.</p>
    </>, media: <ArchiveMap key="societies" map={mapById('societies')} area={selectedFor('societies')} /> },
    { ...CHAPTERS[4], content: <>
      {chapterTitle('05', 'What changed in 2001', '12 December 2001')}
      <p className="health-lead">Five geographic health authorities brought together the preceding boards and councils.</p>
      <p>The original consolidation regulation names the constituent organizations. Society services passed to the new authorities through a different process; the societies were not all statutory amalgamations.</p>
      <p>Later transfers also matter. Bella Coola and Central Coast moved to Vancouver Coastal in 2002. Today’s boundaries cannot simply be assigned to every predecessor.</p>
      <p className="health-notice">The map here is the existing modern PGMaps layer, shown for orientation. It is not a verified December 2001 snapshot.</p>
      <div className="health-actions"><SourceLink href={CONSOLIDATION_SOURCE}>Original consolidation regulation</SourceLink><SiteLink to={{ view: 'government', year: 2001, node: 'northern-health' }}>Explore the 2001 government →</SiteLink></div>
    </>, media: <CurrentAuthorityMap data={data} /> },
    { ...CHAPTERS[5], content: <>
      {chapterTitle('06', 'Which boundaries still align?', 'Compare existing geography')}
      <p className="health-lead">Use the PGMaps layers to investigate a historical area.</p>
      <label className="health-field" htmlFor="compare-area"><span>Historical area</span><select id="compare-area" value={selected.id} onChange={(event) => chooseArea(event.target.value)}>{Object.entries(groupLabels).map(([mapId, label]) => <optgroup key={mapId} label={label}>{areasIn(mapId).map((area) => <option key={area.id} value={area.id}>{area.number}. {area.sourceLabel}</option>)}</optgroup>)}</select></label>
      <AreaEvidence area={selected} match={match} compact />
      {data.phase === 'ready' && <><dl className="health-match-facts"><div><dt>Candidate local health areas</dt><dd>{formatCodes([...candidateCodes(match, 'lha')])}</dd></div><div><dt>Candidate delivery areas</dt><dd>{formatCodes([...candidateCodes(match, 'hsda')])}</dd></div></dl>
        {matchSources.length > 0 && <details className="health-details"><summary>Why this comparison was proposed</summary><ul>{matchSources.map((source) => <li key={source.id}><SourceLink href={source.url}>{source.title}</SourceLink>{source.note && <p>{source.note}</p>}</li>)}</ul></details>}
      </>}
      <p className="health-notice">A shared name, a documented code correspondence and matching polygons answer different questions. The original legal boundaries remain the standard for historical territorial claims.</p>
      {clickedFeature && <section className="health-clicked-area"><h3>{clickedFeature.name} · {clickedFeature.code}</h3><p>Historical areas with this modern candidate:</p>{relatedToClick.length ? <div className="health-chip-list">{relatedToClick.map((area) => <button type="button" key={area.id} onClick={() => chooseArea(area.id)}>{area.sourceLabel}</button>)}</div> : <p>No historical relationship is proposed in this catalogue.</p>}</section>}
    </>, media: <ComparisonMedia data={data} area={selected} layer={layer} setLayer={setLayer} onFeatureSelect={onFeatureSelect} /> },
  ]

  return <main className="health-story">
    <header className="health-story-heading"><div><p className="health-kicker">Historical atlas · British Columbia</p><h1>How the health map changed</h1><p>Explore the boards, councils and societies before the 2001 consolidation, and compare their areas with the boundaries already in PGMaps.</p></div>
      <div className="health-heading-actions"><button type="button" className="health-button health-button--quiet" onClick={copyLink}>{copied ? 'Link copied' : 'Copy this chapter’s link'}</button>{copyFailed && <span className="health-small" role="status">Copy the current address from your browser to share this chapter.</span>}<a className="health-text-link" href={asset('maps/BC-health-area-maps-1997-98.pdf')} download>Download original map pages ↓</a></div>
    </header>
    <p className="health-intro-note"><strong>Historical sources, dated comparisons.</strong> Original maps retain their published labels. Modern polygons are comparison candidates until a historical boundary is verified.</p>
    <div id="health-story-frame"><StoryFrame id="health-geography" title="The changing health map" slides={slides} initialChapterId={initial.chapter} requestedChapterId={requestedChapter} navigationRequestKey={navigationRequestKey} onChapterChange={onChapterChange} /></div>
    <section className="health-area-index" aria-labelledby="health-area-index-title">
      <div className="health-section-heading"><div><p className="health-kicker">Explore every source area</p><h2 id="health-area-index-title">Find a board, council or society</h2></div><span className="health-count">{filteredAreas.length} of {AREAS.length}</span></div>
      <div className="health-index-filters"><label className="health-field" htmlFor="health-area-search"><span>Search historical areas</span><input id="health-area-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Northern Interior, Cariboo, North Shore…" /></label><label className="health-field" htmlFor="health-area-type"><span>Type</span><select id="health-area-type" value={group} onChange={(event) => setGroup(event.target.value)}><option value="all">All source areas</option>{Object.entries(groupLabels).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label></div>
      <div className="health-area-grid">{filteredAreas.map((area) => <article key={area.id} className="health-index-card"><p className="health-kicker">{groupLabels[area.mapId]} · {area.number}</p><h3>{area.sourceLabel}</h3><p>{area.identityConfirmed ? 'Matched to the organization record' : 'Institutional identity unresolved'}</p><div className="health-actions"><button type="button" onClick={() => compareArea(area.id)}>Compare area →</button>{area.bodyId && <SiteLink to={{ view: 'government', node: area.bodyId, year: 1997 }}>History</SiteLink>}<SourceLink href={area.sourceUrl}>Map</SourceLink></div></article>)}</div>
      {!filteredAreas.length && <p className="health-empty" role="status">No source areas match that search. <button type="button" onClick={() => { setQuery(''); setGroup('all') }}>Clear the filters</button></p>}
    </section>
    <section className="health-source-section" aria-labelledby="health-source-title">
      <div className="health-section-heading"><div><p className="health-kicker">Evidence and reuse</p><h2 id="health-source-title">Sources behind the story</h2></div><a href={asset('catalogue.json')} download>Download the area index ↓</a></div>
      <ul className="health-source-grid">{PUBLIC_SOURCES.map((source) => <li key={source.id}><SourceLink href={source.url}>{source.title}</SourceLink><p>{source.detail}</p></li>)}</ul>
      <details className="health-details"><summary>Boundary comparison method and limits</summary><p>The source-map index matches historical institutional names. Existing PGMaps polygons are shown as modern candidates, with the proposed code combinations and source evidence retained for each area. A statistical-region correspondence is not proof of a legal board boundary.</p><p>The original maps are vector page artwork, without geographic coordinates. No exact overlap percentage between those page graphics and modern polygons is claimed. Where present, geometry audit statistics compare PGMaps with the current provincial datasets only.</p><p>Later renamings, the separate Nisga’a source label, the two South Cariboo lineages, and the 2002 coastal transfers are retained as explicit evidence notes.</p>{data.phase === 'ready' && <a href={asset('boundary-comparison.json')} download>Download comparison evidence and candidate codes ↓</a>}</details>
      <p className="health-small health-muted">Story presentation uses the same <SourceLink href="https://github.com/ahzs645/geo-toolkit">geo-toolkit</SourceLink> components as <SourceLink href="https://github.com/ahzs645/PGMaps">PGMaps</SourceLink>. Source artwork and data retain their original attribution.</p>
    </section>
  </main>
}
