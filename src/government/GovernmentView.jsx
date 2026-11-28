// The government diagram: the Province's structure as a radial graph, with a timeline back to
// Confederation.
//
// Laid out after the org-graph convention it is modelled on — a detail panel on the left, the
// diagram filling the right, search and theme over it, the legend beneath — and styled in its warm
// stone, with the branch colours taken from the BC identity instead.
//
// The year and the chosen body live in the address bar, so a view of the 1986 cabinet with the
// Ministry of Forests and Lands open is a link that can be sent.

import { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { MINISTRY_EPISODES, standsIn } from './episodes.js'
import { ChangesCard, EntityCard, OverviewCard, usePreloadSalaries } from './GovernmentPanel.jsx'
import { InstrumentCard } from './LegislationCards.jsx'
import { instrumentById } from './instruments.js'
import { GovernmentGraph } from './GovernmentGraph.jsx'
import { GovernmentList } from './GovernmentList.jsx'
import { CompareView } from './AtlasCards.jsx'
import { SourcesCard } from './SourcesCard.jsx'
import { Legend } from './Legend.jsx'
import { Sheet } from './Sheet.jsx'
import { ViewSwitcher } from '../site/ViewSwitcher.jsx'
import { holdScrollFrom } from '../site/holdScroll.js'
import { SiteLink, useNavigate } from '../site/navigation.jsx'
import { SunGlyph, ThemeIcon } from '../site/icons.jsx'
import { useSiteTheme } from '../site/useTheme.js'
import { layoutGovernment } from './layout.js'
import { FIRST_YEAR, governmentIn, lifeOf, lifespanOf, PRESENT_YEAR } from './snapshot.js'
import { TimelineBar } from './TimelineBar.jsx'
import { THEMES } from './theme.js'
import { RelatedBodiesView } from './RelatedBodiesView.jsx'
import { search } from './governmentSearch.js'
import { relatedBodyById, relatedBodyPlace } from './relatedBodies.js'
import { readGovernmentPlace } from './governmentPlace.js'
import './government.css'

// The Budget mode is its own page, loaded when it is opened.
const BudgetView = lazy(() => import('./BudgetView.jsx').then((module) => ({ default: module.BudgetView })))

const readParams = () => readGovernmentPlace(globalThis.location?.search ?? '')

/**
 * Everything that decides what is on screen goes in the address bar — the year, the body, the view,
 * the year compared against, and whether unconfirmed bodies are drawn — so a copied link restores it.
 */
const writeParams = ({ year, node, mode, compare, undated, local, instrument }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'government')
  const set = (key, value) => (value === null || value === undefined || value === false ? url.searchParams.delete(key) : url.searchParams.set(key, String(value)))
  set('year', mode === 'related' || year === PRESENT_YEAR ? null : year)
  set('node', node)
  set('mode', mode === 'graph' ? null : mode)
  set('compare', mode === 'compare' ? compare : null)
  set('undated', mode === 'related' || undated ? null : 0)
  set('local', mode !== 'related' && local ? 1 : null)
  set('instrument', mode === 'related' ? null : instrument)
  globalThis.history.replaceState(null, '', url)
}

const ChevronIcon = ({ direction }) => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
    <path d={direction < 0 ? 'M8.5 3 4.5 7l4 4' : 'M5.5 3l4 4-4 4'} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

/** Whether the page is laid out for a phone: the diagram above the panel, and drawn small. */
const useNarrow = () => {
  const media = globalThis.matchMedia?.('(max-width: 1023px)')
  const [narrow, setNarrow] = useState(() => Boolean(media?.matches))
  useEffect(() => {
    if (!media) return undefined
    const listen = (event) => setNarrow(event.matches)
    media.addEventListener('change', listen)
    return () => media.removeEventListener('change', listen)
  }, [media])
  return narrow
}

const Search = ({ onPick }) => {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const results = useMemo(() => search(query), [query])
  const box = useRef(null)
  const input = useRef(null)
  useEffect(() => { if (open) input.current?.focus() }, [open])

  const close = () => { setOpen(false); setQuery('') }
  const choose = (result) => { onPick(result); close() }
  // Up and down move through the results as well as Tab does; Escape goes back to the input.
  const step = (event) => {
    const items = [...(box.current?.querySelectorAll('.gov-search__results button') ?? [])]
    const index = items.indexOf(document.activeElement)
    if (event.key === 'ArrowDown') { event.preventDefault(); items[Math.min(items.length - 1, index + 1)]?.focus() }
    if (event.key === 'ArrowUp') { event.preventDefault(); (index <= 0 ? input.current : items[index - 1])?.focus() }
    if (event.key === 'Escape') { event.preventDefault(); close() }
  }

  if (!open) {
    return (
      <button type="button" className="gov-button gov-button--icon" onClick={() => setOpen(true)} aria-label="Search">
        <svg viewBox="0 0 20 20" width="17" height="17" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" strokeWidth="1.6" /><path d="M13 13l4.5 4.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" /></svg>
      </button>
    )
  }
  return (
    <div
      className="gov-search"
      ref={box}
      onKeyDown={step}
      // Closes when focus leaves the search altogether, not when it moves to one of the results.
      onBlur={(event) => { if (!box.current?.contains(event.relatedTarget)) close() }}
    >
      <input
        ref={input}
        type="search"
        value={query}
        placeholder="Search ministries, public bodies or TransLink…"
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={(event) => { if (event.key === 'Enter' && results[0]) choose(results[0]) }}
        aria-label="Search the government"
      />
      {query && (
        // A tap on a result must not take focus from the input first: iOS Safari does not focus a
        // tapped button, so the blur would close the results before the tap's click arrives.
        <ul className="gov-search__results" onMouseDown={(event) => event.preventDefault()}>
          {results.length === 0 && <li className="gov-muted">Nothing by that name. Try “Forests”, “Hydro” or “Ombudsperson”.</li>}
          {results.map((result) => (
            <li key={result.key}>
              <button type="button" onClick={() => choose(result)}>
                <span>{result.name}</span>
                <span className="gov-muted">{result.detail}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

/**
 * @param {object} props
 * @param {(patch: {era: string, name: string}) => void} props.onOpenInGenerator
 * @param {(view: string) => void} props.onChangeView
 */
export const GovernmentView = ({ onOpenInGenerator, onChangeView }) => {
  const navigate = useNavigate()
  usePreloadSalaries()
  const initial = useMemo(readParams, [])
  const [year, setYear] = useState(initial.year)
  const [selectedId, setSelectedId] = useState(initial.node)
  const [instrumentId, setInstrumentId] = useState(initial.instrument)
  const [hidden, setHidden] = useState(() => new Set())
  const [hiddenRelations, setHiddenRelations] = useState(() => new Set())
  const [mode, setMode] = useState(initial.mode)
  const [compareYear, setCompareYear] = useState(initial.compare ?? Math.max(FIRST_YEAR, initial.year - 25))
  const [includeUndated, setIncludeUndated] = useState(initial.undated)
  const [includeLocal, setIncludeLocal] = useState(initial.local)
  const [playing, setPlaying] = useState(false)
  // The site's one theme: the toggle here and the one in the generator's masthead are the same.
  const { name: themeName, toggle } = useSiteTheme()
  const theme = THEMES[themeName]
  const narrow = useNarrow()

  const government = useMemo(() => governmentIn(year, { includeUndated, includeLocal }), [year, includeUndated, includeLocal])
  const selected = mode === 'related' ? relatedBodyById(selectedId) : government.nodes.find((node) => node.id === selectedId) ?? null
  // The chosen body's whole life, kept while the years move through ones it did not exist in.
  const life = useMemo(() => lifeOf(selectedId), [selectedId])

  useEffect(() => {
    writeParams({ year, node: selected ? selectedId : null, mode, compare: compareYear, undated: includeUndated, local: includeLocal, instrument: instrumentId })
  }, [year, selectedId, selected, mode, compareYear, includeUndated, includeLocal, instrumentId])

  // On a phone the chosen body opens in a sheet over the foot of the diagram (Sheet.jsx), so the
  // diagram stays where it is to choose the next one.
  const sheeted = narrow && Boolean(selected)
  const close = useCallback(() => setSelectedId(null), [])

  // Playing runs the years forward, a little over two a second, and stops at today.
  useEffect(() => {
    if (!playing) return undefined
    const timer = setInterval(() => {
      setYear((current) => {
        if (current >= PRESENT_YEAR) { setPlaying(false); return current }
        return current + 1
      })
    }, 450)
    return () => clearInterval(timer)
  }, [playing])

  const play = () => {
    if (!playing && year >= PRESENT_YEAR) setYear(FIRST_YEAR)
    setPlaying((value) => !value)
  }

  const changeYear = useCallback((next) => { setPlaying(false); setYear(next) }, [])
  const showAs = (event, next) => {
    if (next !== mode) holdScrollFrom(event)
    setMode(next)
  }

  /** Moves the timeline to a year the episode stood in, and chooses it. */
  const jump = useCallback((episode, end) => {
    const target = end === 'end' && episode.to !== null
      ? (episode.to === episode.from ? episode.from : episode.to - 1)
      : episode.from
    setPlaying(false)
    setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, target)))
    setSelectedId(episode.id)
  }, [])

  /** Moves the timeline to `target` with `id` chosen, as the lineage chart's rows do. */
  const go = useCallback((target, id) => {
    setPlaying(false)
    setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, target)))
    setSelectedId(id)
  }, [])

  /** Moves the timeline to a year a body stood — its first, or its last — and chooses it. */
  const jumpBody = useCallback((body, end) => {
    // Its last year is the one before its end, the last a source shows it in if its end is
    // untraced, and today only if it continues.
    const life = lifespanOf(body)
    const first = Number(String(life.from ?? PRESENT_YEAR).slice(0, 4))
    const last = life.toKind === 'ended' ? Math.max(first, Number(String(life.to).slice(0, 4)) - 1)
      : life.toKind === 'open' ? PRESENT_YEAR : Number(String(life.lastSeen ?? life.from).slice(0, 4))
    setPlaying(false)
    setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, end === 'end' ? last : first)))
    setSelectedId(body.id)
  }, [])

  const pick = (result) => {
    if (result.related) {
      if (navigate) { navigate(relatedBodyPlace(result.id)); return }
      setPlaying(false)
      setYear(PRESENT_YEAR)
      setMode('related')
      setSelectedId(result.id)
      return
    }
    if (result.minister) {
      setPlaying(false)
      setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, result.year)))
      setSelectedId(result.id)
      return
    }
    // A local body is found whether or not its layer is on, and choosing it turns the layer on.
    if (result.local) setIncludeLocal(true)
    if (result.body) return jumpBody(result.body, lifespanOf(result.body).toKind === 'open' ? 'start' : 'end')
    const episode = MINISTRY_EPISODES.find((entry) => entry.id === result.id)
    if (episode && !standsIn(episode, year)) jump(episode, 'end')
    else {
      if (!episode) setYear(PRESENT_YEAR)
      setSelectedId(result.id)
    }
  }

  // Previous and next step through bodies of the same kind, in the order they sit round the disc.
  const positions = useMemo(() => layoutGovernment(government.nodes.filter((node) => node.branch)).positions, [government])
  const clockwise = (id) => (((positions[id]?.angle ?? 0) + Math.PI / 2) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2)
  const siblings = selected
    ? government.nodes.filter((node) => node.kind === selected.kind).sort((a, b) => clockwise(a.id) - clockwise(b.id))
    : []
  const step = (direction) => {
    if (!siblings.length) return
    const index = siblings.findIndex((node) => node.id === selectedId)
    setSelectedId(siblings[(index + direction + siblings.length) % siblings.length].id)
  }

  const present = useMemo(() => [...new Set(government.nodes.map((node) => node.kind))], [government])
  // A legend row can stand for several kinds; it hides them together, or shows them together.
  const toggleKinds = (kinds) => setHidden((current) => {
    const next = new Set(current)
    const hide = !kinds.every((kind) => next.has(kind))
    for (const kind of kinds) {
      if (hide) next.add(kind)
      else next.delete(kind)
    }
    return next
  })
  const toggleRelation = (relation) => setHiddenRelations((current) => {
    const next = new Set(current)
    if (next.has(relation)) next.delete(relation)
    else next.add(relation)
    return next
  })

  // On a phone the theme toggle ends the breadcrumb, as it ends every other view's; on a wide screen
  // it is with the diagram's tools.
  const themeButton = (
    <button type="button" className="gov-button gov-button--icon" onClick={toggle} aria-label={`Switch to ${themeName === 'dark' ? 'light' : 'dark'} mode`}>
      <ThemeIcon name={themeName} />
    </button>
  )

  // An instrument's page replaces the body's card (on a phone, its sheet); choosing a body from it closes it.
  const openInstrument = useCallback((id) => { setInstrumentId(id); setSelectedId(null) }, [])
  const goFromInstrument = useCallback((target, id) => { setInstrumentId(null); go(target, id) }, [go])
  const instrument = instrumentId ? instrumentById(instrumentId) : null
  // Choosing a body anywhere (the diagram, search, a link) closes an open instrument page.
  useEffect(() => { if (selectedId) setInstrumentId(null) }, [selectedId])

  const entityCard = selected && (
    <EntityCard node={selected} government={government} theme={themeName} onJumpBody={jumpBody} onGo={go} onSelect={setSelectedId} onJump={jump} onOpenInGenerator={onOpenInGenerator} onOpenInstrument={openInstrument} />
  )

  if (mode === 'budget') return <Suspense fallback={null}><BudgetView onChangeView={onChangeView} themeName={themeName} onToggleTheme={toggle} /></Suspense>

  if (mode === 'related') return <RelatedBodiesView
    selectedId={selectedId} onChangeView={onChangeView} themeName={themeName} onToggleTheme={toggle}
  />

  return (
    <div className="gov" data-theme={themeName} data-sheeted={sheeted || undefined}>
      <nav className="gov-card gov-breadcrumb" aria-label="Breadcrumb">
        <SunGlyph fill={theme.people} />
        <strong className="gov-breadcrumb__site">Province of BC</strong>
        <span className="gov-muted" aria-hidden="true">/</span>
        <ViewSwitcher view="government" onChange={onChangeView} className="gov-breadcrumb__views" />
        <span className="gov-muted gov-breadcrumb__year-slash" aria-hidden="true">/</span>
        <button type="button" className="gov-breadcrumb__year" onClick={() => setSelectedId(null)} title="Back to the overview">{year}</button>
        {selected?.branch && <span className="gov-muted gov-breadcrumb__branch">/ {selected.branch[0].toUpperCase() + selected.branch.slice(1)}</span>}
        {narrow && <span className="gov-breadcrumb__tools">{themeButton}</span>}
      </nav>
      <div className="gov__stage">
        <div className="gov__overlay gov__overlay--top">
          <Search onPick={pick} />
          <div className="gov__tools">
            <SiteLink className="gov-button gov__related-link" to={{ view: 'government', mode: 'budget' }}>Budget</SiteLink>
            <SiteLink className="gov-button gov__related-link" to={{ view: 'government', mode: 'related' }}>Related bodies</SiteLink>
            {!narrow && themeButton}
            {/* Narrow, a chosen body opens in the sheet, which carries these arrows itself. */}
            {!narrow && (
              <span className="gov-button-group">
                <button type="button" className="gov-button gov-button--icon" disabled={!selected} onClick={() => step(-1)} aria-label="Previous of this kind"><ChevronIcon direction={-1} /></button>
                <button type="button" className="gov-button gov-button--icon" disabled={!selected} onClick={() => step(1)} aria-label="Next of this kind"><ChevronIcon direction={1} /></button>
              </span>
            )}
          </div>
        </div>

        <div className="gov__graph" data-mode={mode}>
          {mode === 'graph'
            ? <GovernmentGraph government={government} selectedId={selected ? selectedId : null} onSelect={setSelectedId} hiddenKinds={hidden} hiddenRelations={hiddenRelations} theme={theme} compact={narrow} />
            : mode === 'list'
              ? <GovernmentList government={government} selectedId={selected ? selectedId : null} onSelect={setSelectedId} hiddenKinds={hidden} compact={narrow} />
              : (
                <CompareView
                  year={year}
                  other={compareYear}
                  onOther={setCompareYear}
                  onPick={(node, at) => { setPlaying(false); setYear(at); setSelectedId(node.id) }}
                />
                )}
          <div className="gov__overlay gov__overlay--bottom">
            <Legend
              hiddenKinds={hidden}
              hiddenRelations={hiddenRelations}
              onToggleKinds={toggleKinds}
              onToggleRelation={toggleRelation}
              onReset={() => { setHidden(new Set()); setHiddenRelations(new Set()) }}
              present={present}
              themeName={themeName}
              includeUndated={includeUndated}
              onToggleUndated={() => setIncludeUndated((value) => !value)}
              includeLocal={includeLocal}
              onToggleLocal={() => setIncludeLocal((value) => !value)}
            />
            {/* Under the diagram, the list or the comparison, each its own height: the switch stays
                under the finger as the one above it is replaced (holdScroll.js). */}
            <div className="segmented gov-segmented" role="group" aria-label="Show as">
              <button type="button" aria-pressed={mode === 'graph'} onClick={(event) => showAs(event, 'graph')}>Graph</button>
              <button type="button" aria-pressed={mode === 'list'} onClick={(event) => showAs(event, 'list')}>List</button>
              <button type="button" aria-pressed={mode === 'compare'} onClick={(event) => showAs(event, 'compare')}>Compare</button>
            </div>
          </div>
        </div>

        <TimelineBar year={year} onYear={changeYear} playing={playing} onPlay={play} life={life} />
      </div>
      <div className="gov__panel">

        {instrument && !selected
          ? <InstrumentCard instrument={instrument} onGo={goFromInstrument} onClose={() => setInstrumentId(null)} />
          : selected
            ? !sheeted && entityCard
            : <OverviewCard government={government} onSelect={setSelectedId} />}
        {!selected && <ChangesCard key={year} year={year} onSelect={setSelectedId} onJump={jump} />}

        <SourcesCard />
      </div>

      {sheeted && (
        <Sheet
          label="Chosen body"
          title={selected.name}
          onClose={close}
          tools={(
            <span className="gov-button-group">
              <button type="button" className="gov-button gov-button--icon" disabled={siblings.length < 2} onClick={() => step(-1)} aria-label="Previous of this kind"><ChevronIcon direction={-1} /></button>
              <button type="button" className="gov-button gov-button--icon" disabled={siblings.length < 2} onClick={() => step(1)} aria-label="Next of this kind"><ChevronIcon direction={1} /></button>
            </span>
          )}
        >
          {entityCard}
        </Sheet>
      )}
    </div>
  )
}
