// The government diagram: the Province's structure as a radial graph, with a timeline back to
// Confederation.
//
// Laid out after the org-graph convention it is modelled on — a detail panel on the left, the
// diagram filling the right, search and theme over it, the legend beneath — and styled in its warm
// stone, with the branch colours taken from the BC identity instead.
//
// The year and the chosen body live in the address bar, so a view of the 1986 cabinet with the
// Ministry of Forests and Lands open is a link that can be sent.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { MINISTRY_EPISODES, standsIn } from './episodes.js'
import { ChangesCard, EntityCard, OverviewCard } from './GovernmentPanel.jsx'
import { GovernmentGraph } from './GovernmentGraph.jsx'
import { GovernmentList } from './GovernmentList.jsx'
import { CompareView, CoverageCard } from './AtlasCards.jsx'
import { EVENT_SOURCES } from './events.js'
import { Legend } from './Legend.jsx'
import { ViewSwitcher } from '../site/ViewSwitcher.jsx'
import { SunGlyph, ThemeIcon } from '../site/icons.jsx'
import { useSiteTheme } from '../site/useTheme.js'
import { layoutGovernment } from './layout.js'
import { FIRST_YEAR, governmentIn, PRESENT_YEAR } from './snapshot.js'
import { TimelineBar } from './TimelineBar.jsx'
import { THEMES } from './theme.js'
import { CURRENT_AS_OF, CURRENT_SOURCES } from './currentData.js'
import { HISTORICAL_BODIES, HISTORY_SOURCES, MINISTERS } from './historyData.js'
import { TIMELINE_SOURCES } from './timelineData.js'
import './government.css'

const validYear = (value) => Number.isInteger(value) && value >= FIRST_YEAR && value <= PRESENT_YEAR

const readParams = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const year = Number(params.get('year'))
  const compare = Number(params.get('compare'))
  const mode = params.get('mode')
  return {
    year: validYear(year) ? year : PRESENT_YEAR,
    node: params.get('node'),
    mode: ['graph', 'list', 'compare'].includes(mode) ? mode : 'graph',
    compare: validYear(compare) ? compare : null,
    undated: params.get('undated') === '1'
  }
}

/**
 * Everything that decides what is on screen goes in the address bar — the year, the body, the view,
 * the year compared against, and whether undated bodies are drawn — so a copied link restores it.
 */
const writeParams = ({ year, node, mode, compare, undated }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'government')
  const set = (key, value) => (value === null || value === undefined || value === false ? url.searchParams.delete(key) : url.searchParams.set(key, String(value)))
  set('year', year === PRESENT_YEAR ? null : year)
  set('node', node)
  set('mode', mode === 'graph' ? null : mode)
  set('compare', mode === 'compare' ? compare : null)
  set('undated', undated ? 1 : null)
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

/**
 * Search over everything the timeline holds, not just the year on screen: a ministry that ran
 * from 1986 to 1988 is found, and choosing it moves the timeline there.
 */
const SEARCH_INDEX = (() => {
  const today = governmentIn(PRESENT_YEAR).nodes
    .filter((node) => node.kind !== 'ministry')
    .map((node) => ({ id: node.id, name: node.name, alias: node.shortName, year: PRESENT_YEAR, detail: node.head?.person }))
  const episodes = MINISTRY_EPISODES.map((episode) => ({
    id: episode.id,
    name: episode.name,
    year: episode.to === null ? PRESENT_YEAR : episode.to === episode.from ? episode.from : episode.to - 1,
    detail: episode.to ? `${episode.from}–${episode.to}` : `${episode.from}–`
  }))
  // Former bodies, and every minister by name, so "Vander Zalm" or "BC Rail" finds its year.
  const bodies = HISTORICAL_BODIES.filter((body) => !body.current && body.ended).map((body) => ({
    id: body.id,
    name: body.name,
    alias: body.shortName,
    year: Number(String(body.established).slice(0, 4)),
    detail: `${String(body.established).slice(0, 4)}–${String(body.ended).slice(0, 4)}`,
    body
  }))
  const ministers = Object.entries(MINISTERS).flatMap(([episodeId, rows]) => rows.map(([person, from, to, title]) => {
    const episode = MINISTRY_EPISODES.find((entry) => entry.id === episodeId)
    const start = Math.max(Number(String(from).slice(0, 4)), episode?.from ?? 0)
    return { id: episodeId, name: person, alias: title, year: start, detail: `${title}, ${String(from).slice(0, 4)}–${to ? String(to).slice(0, 4) : ''}`, minister: true }
  }))
  // A term that spans a renaming — the 1976 departments becoming ministries — is one entry, not two.
  const seen = new Set()
  const people = ministers.filter((entry) => {
    const key = `${entry.name}|${entry.detail}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
  return [...today, ...episodes, ...bodies, ...people]
})()

const normal = (text) => String(text ?? '').toLowerCase().normalize('NFD').replace(/[^a-z0-9 ]+/g, ' ')

const search = (query) => {
  const words = normal(query).split(/\s+/).filter(Boolean)
  if (!words.length) return []
  return SEARCH_INDEX
    .filter((entry) => {
      // A minister is found by name, not by portfolio, or "forests" would list every minister of it.
      const haystack = normal(entry.minister ? entry.name : `${entry.name} ${entry.alias ?? ''} ${entry.detail ?? ''}`)
      return words.every((word) => haystack.includes(word))
    })
    // Bodies first, then people; the most recent first within each.
    .sort((a, b) => Number(Boolean(a.minister)) - Number(Boolean(b.minister)) || b.year - a.year)
    .slice(0, 10)
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
        placeholder="Search every ministry since 1871, or a Crown corporation…"
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={(event) => { if (event.key === 'Enter' && results[0]) choose(results[0]) }}
        aria-label="Search the government"
      />
      {query && (
        <ul className="gov-search__results">
          {results.length === 0 && <li className="gov-muted">Nothing by that name. Try “Forests”, “Hydro” or “Ombudsperson”.</li>}
          {results.map((result) => (
            <li key={result.id}>
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
  const initial = useMemo(readParams, [])
  const [year, setYear] = useState(initial.year)
  const [selectedId, setSelectedId] = useState(initial.node)
  const [hidden, setHidden] = useState(() => new Set())
  const [hiddenRelations, setHiddenRelations] = useState(() => new Set())
  const [mode, setMode] = useState(initial.mode)
  const [compareYear, setCompareYear] = useState(initial.compare ?? Math.max(FIRST_YEAR, initial.year - 25))
  const [includeUndated, setIncludeUndated] = useState(initial.undated)
  const [playing, setPlaying] = useState(false)
  // The site's one theme: the toggle here and the one in the generator's masthead are the same.
  const { name: themeName, toggle } = useSiteTheme()
  const theme = THEMES[themeName]
  const narrow = useNarrow()
  const panel = useRef(null)

  const government = useMemo(() => governmentIn(year, { includeUndated }), [year, includeUndated])
  const selected = government.nodes.find((node) => node.id === selectedId) ?? null

  useEffect(() => {
    writeParams({ year, node: selected ? selectedId : null, mode, compare: compareYear, undated: includeUndated })
  }, [year, selectedId, selected, mode, compareYear, includeUndated])

  // On a phone the panel is below the diagram, so choosing a body brings its panel into view.
  const chooseFromGraph = (id) => {
    setSelectedId(id)
    if (narrow && id) requestAnimationFrame(() => panel.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
  }

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

  /** Moves the timeline to a year the episode stood in, and chooses it. */
  const jump = useCallback((episode, end) => {
    const target = end === 'end' && episode.to !== null
      ? (episode.to === episode.from ? episode.from : episode.to - 1)
      : episode.from
    setPlaying(false)
    setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, target)))
    setSelectedId(episode.id)
  }, [])

  /** Moves the timeline to a year a body stood — its first, or its last — and chooses it. */
  const jumpBody = useCallback((body, end) => {
    const first = Number(String(body.established ?? PRESENT_YEAR).slice(0, 4))
    const last = body.ended ? Math.max(first, Number(String(body.ended).slice(0, 4)) - 1) : PRESENT_YEAR
    setPlaying(false)
    setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, end === 'end' ? last : first)))
    setSelectedId(body.id)
  }, [])

  const pick = (result) => {
    if (result.minister) {
      setPlaying(false)
      setYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, result.year)))
      setSelectedId(result.id)
      return
    }
    if (result.body) return jumpBody(result.body, result.body.ended ? 'end' : 'start')
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

  return (
    <div className="gov" data-theme={themeName}>
      <nav className="gov-card gov-breadcrumb" aria-label="Breadcrumb">
        <SunGlyph fill={theme.people} />
        <strong className="gov-breadcrumb__site">Province of BC</strong>
        <span className="gov-muted" aria-hidden="true">/</span>
        <ViewSwitcher view="government" onChange={onChangeView} className="gov-breadcrumb__views" />
        <span className="gov-muted" aria-hidden="true">/</span>
        <button type="button" className="gov-breadcrumb__year" onClick={() => setSelectedId(null)} title="Back to the overview">{year}</button>
        {selected?.branch && <span className="gov-muted">/ {selected.branch[0].toUpperCase() + selected.branch.slice(1)}</span>}
      </nav>
      <div className="gov__stage">
        <div className="gov__overlay gov__overlay--top">
          <Search onPick={pick} />
          <div className="gov__tools">
            <button type="button" className="gov-button gov-button--icon" onClick={toggle} aria-label={`Switch to ${themeName === 'dark' ? 'light' : 'dark'} mode`}>
              <ThemeIcon name={themeName} />
            </button>
            <span className="gov-button-group">
              <button type="button" className="gov-button gov-button--icon" disabled={!selected} onClick={() => step(-1)} aria-label="Previous of this kind"><ChevronIcon direction={-1} /></button>
              <button type="button" className="gov-button gov-button--icon" disabled={!selected} onClick={() => step(1)} aria-label="Next of this kind"><ChevronIcon direction={1} /></button>
            </span>
          </div>
        </div>

        <div className="gov__graph" data-mode={mode}>
          {mode === 'graph'
            ? <GovernmentGraph government={government} selectedId={selected ? selectedId : null} onSelect={chooseFromGraph} hiddenKinds={hidden} hiddenRelations={hiddenRelations} theme={theme} compact={narrow} />
            : mode === 'list'
              ? <GovernmentList government={government} selectedId={selected ? selectedId : null} onSelect={chooseFromGraph} hiddenKinds={hidden} />
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
            />
            <div className="gov-segmented" role="group" aria-label="Show as">
              <button type="button" aria-pressed={mode === 'graph'} onClick={() => setMode('graph')}>Graph</button>
              <button type="button" aria-pressed={mode === 'list'} onClick={() => setMode('list')}>List</button>
              <button type="button" aria-pressed={mode === 'compare'} onClick={() => setMode('compare')}>Compare</button>
            </div>
          </div>
        </div>

        <TimelineBar year={year} onYear={changeYear} playing={playing} onPlay={play} />
      </div>
      <div className="gov__panel" ref={panel}>

        {selected
          ? <EntityCard node={selected} government={government} theme={themeName} onJumpBody={jumpBody} onSelect={setSelectedId} onJump={jump} onOpenInGenerator={onOpenInGenerator} />
          : <OverviewCard government={government} onSelect={setSelectedId} />}
        <ChangesCard year={year} onSelect={setSelectedId} onJump={jump} />

        <details className="gov-card gov-sources">
          <summary>Sources and caveats</summary>
          <p className="gov-muted">
            Ministries and their lineage from the BC Archives’ ministry history diagram (to December
            2024), corrected where it leaves ends open and extended since. Ministers from the
            Legislative Library’s Executive Council Appointments 1871–1986 and its cabinet lists since;
            former Crown corporations and agencies, and past Speakers, officers and chief justices, from
            BC Archives, the Library, Orders in Council and Wikipedia. Which ministry answered for a body
            is shown where a source states it, and otherwise inferred and marked so. Present-day officials as
            checked on {CURRENT_AS_OF} against the Province’s and each body’s own pages. Staff are
            2025/26 full-time equivalents from the Public Accounts. The dates of the four identities are
            estimates, most of all the crest’s. Typed events — origins, name and logo changes,
            appointments, the 2026 election’s schedule — come from the BC government atlas research
            package of 25 September 2026 and the research that followed it ({EVENT_SOURCES.length} sources).
            A date is shown only as precisely as its source gives it; an unknown start is not treated as
            proof a body did not exist.
          </p>
          <CoverageCard />
          <ul>
            {[...TIMELINE_SOURCES, ...CURRENT_SOURCES].map((source) => (
              <li key={source.id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></li>
            ))}
          </ul>
          <details className="gov-sources__more">
            <summary>{HISTORY_SOURCES.length} sources behind the history</summary>
            <ul>
              {HISTORY_SOURCES.map((url) => (
                <li key={url}><a href={url} target="_blank" rel="noreferrer">{url.replace(/^https?:\/\/(www\.)?/, '')}</a></li>
              ))}
            </ul>
          </details>
        </details>
      </div>

    </div>
  )
}
