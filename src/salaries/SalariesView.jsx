// Search the remuneration records imported here, with explicit employer/year coverage and sources.
//
// Disclosures differ in reporting period, threshold and scope. A search finds employers by name and
// people by surname: it loads one slice of the index — the surnames that start with the same two
// letters (scripts/build-salaries.mjs) — and groups its rows into the names they appear under.
// Opening a name sets its years out as a chart and a table. An employer's page loads that employer's
// rows and sets out the year chosen: by position where the disclosure names positions, and by person.
//
// A name in two years' disclosures is not proof of one person. Multiple rows may be different people,
// multiple payments to one person, or source duplicates; none of these is inferred from a name alone.

import { useEffect, useMemo, useState } from 'react'
import { displayName, matchesNameQuery, nameMatch, personKey, positionKey, readName, surnameShard } from './people.js'
import { coverageAt, expenseLabel, GAP_LABELS, gapReason, gapRuns, missingYearMessage } from './coverage.js'
import { DisclosureSummary, SourceLink } from './DisclosureEvidence.jsx'
import { formatMoney as money, medianMoney as median } from './money.js'
import { PayChart, YearPicker, YearStrip, yearSpan } from './parts.jsx'

const BASE = import.meta.env?.BASE_URL ?? '/'
const loaded = new Map()

const count = (value, one, many) => `${value.toLocaleString('en-CA')} ${value === 1 ? one : many}`

/** A gzipped file, decompressed here; or plain JSON, if the server already undid the gzip. */
const loadJson = (path) => {
  if (!loaded.has(path)) {
    loaded.set(path, fetch(`${BASE}${path}`).then(async (response) => {
      if (!response.ok) throw new Error(`${response.status}`)
      const bytes = new Uint8Array(await response.arrayBuffer())
      if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
        const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))
        return JSON.parse(await new Response(stream).text())
      }
      return JSON.parse(new TextDecoder().decode(bytes))
    }).catch((error) => { loaded.delete(path); throw error }))
  }
  return loaded.get(path)
}

// Where the search is lives in the address bar — the name typed, the person or employer open — so a
// link opens there, and a person in a body's salary panel opens their years here.
const PLACE = ['q', 'person', 'employer']

const readPlace = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  return Object.fromEntries(PLACE.map((key) => [key, params.get(key) ?? (key === 'q' ? '' : null)]))
}

const writePlace = (place) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  for (const key of PLACE) {
    if (place[key]) url.searchParams.set(key, place[key])
    else url.searchParams.delete(key)
  }
  globalThis.history.replaceState(null, '', url)
}

const Person = () => (
  <svg className="salaries__icon" viewBox="0 0 21 22" aria-hidden="true">
    <rect x="4.25" y="8" width="12.5" height="10" rx="2.6" fill="var(--surface)" />
    <rect x="4.25" y="8" width="12.5" height="10" rx="2.6" fill="var(--salaries-ink)" fillOpacity="0.5" />
    <rect x="4.25" y="8" width="12.5" height="10" rx="2.6" fill="none" stroke="var(--salaries-ink)" />
    <circle cx="10.5" cy="8" r="3.75" fill="var(--surface)" />
    <circle cx="10.5" cy="8" r="3.75" fill="var(--salaries-ink)" fillOpacity="0.5" />
    <circle cx="10.5" cy="8" r="3.75" fill="none" stroke="var(--salaries-ink)" />
  </svg>
)

/** A position or an employer: a briefcase, in the same layered style. */
const Role = () => (
  <svg className="salaries__icon" viewBox="0 0 21 22" aria-hidden="true">
    {[{ fill: 'var(--surface)' }, { fill: 'var(--salaries-ink)', fillOpacity: 0.5 }, { fill: 'none', stroke: 'var(--salaries-ink)' }].map((layer, at) => (
      <g key={at}>
        <rect x="3.5" y="7.5" width="14" height="10" rx="2.4" {...layer} />
        <path d="M8 7.5V5.6a1.3 1.3 0 0 1 1.3-1.3h2.4A1.3 1.3 0 0 1 13 5.6v1.9" fill="none" stroke={layer.stroke ?? 'none'} />
      </g>
    ))}
  </svg>
)

const describeNameGroup = (key, list) => {
  const latest = list.reduce((best, row) => (row[5] > best[5] || (row[5] === best[5] && row[2] > best[2]) ? row : best))
  const years = [...new Set(list.map((row) => row[5]))].sort((a, b) => a - b)
  const shared = years.some((each) => list.filter((row) => row[5] === each).length > 1)
  return { key, name: latest[0], latest, years, rows: list, shared }
}

const seenYears = (entry) => entry.counts.map((value, at) => (value > 0 ? at : null)).filter((at) => at !== null)
const latestYear = (entry) => entry.counts.reduce((best, value, at) => (value ? at : best), 0)
const wordsOf = (text) => text.trim().toLowerCase().split(/\s+/).filter(Boolean)

/** An employer as a card: its name, the years it has records in, and its latest count. */
const EmployerCard = ({ entry, years, year, onOpen }) => {
  const at = year !== 'all' ? Number(year) : latestYear(entry)
  return (
    <button type="button" className="salaries__card" onClick={() => onOpen(entry.slug)}>
      <span className="salaries__lead"><Role /></span>
      <span className="salaries__text">
        <span className="salaries__name">{entry.names.at(-1)}</span>
        <span className="salaries__line">{count(entry.counts[at], 'record', 'records')} in {years[at]}</span>
        <YearStrip years={years} seen={seenYears(entry)} />
      </span>
    </button>
  )
}

/**
 * @param {object} props
 * @param {(node: string, year?: number) => void} [props.onOpenGovernment]  To a body in the diagram.
 */
export const SalariesView = ({ onOpenGovernment }) => {
  const [index, setIndex] = useState(null)
  const [employersIndex, setEmployersIndex] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const initial = readPlace()
  const [query, setQuery] = useState(initial.q)
  const [person, setPerson] = useState(initial.person)
  const [employer, setEmployer] = useState(initial.employer)
  const [year, setYear] = useState('all')
  const [sector, setSector] = useState('all')
  const [rows, setRows] = useState({ shard: null, list: [] })
  const [shown, setShown] = useState(24)
  const [employersShown, setEmployersShown] = useState(6)

  useEffect(() => {
    loadJson('salaries/people/index.json').then(setIndex, () => setFailed(true))
    loadJson('salaries/employers/index.json').then(setEmployersIndex, () => setFailed(true))
  }, [loadVersion])

  // What was typed, read as a name: a surname, and perhaps the start of a given name after a comma
  // or a space ("smith, j", "smith john").
  const wanted = useMemo(() => {
    const text = query.trim()
    if (!text) return null
    const [surname, ...given] = text.includes(',') ? text.split(',') : text.split(/\s+/)
    const typedName = `${surname},${given.join(' ')}`
    const name = readName(typedName)
    return name.surname.length >= 2 ? { ...name, typedName } : null
  }, [query])
  const shard = wanted ? surnameShard(`${wanted.surname},`) : null

  useEffect(() => {
    if (!shard || !index) return undefined
    if (!index.shards[shard]) { setRows({ shard, list: [] }); return undefined }
    let live = true
    loadJson(`salaries/people/${shard}.json.gzip`).then((list) => live && setRows({ shard, list }), () => live && setFailed(true))
    return () => { live = false }
  }, [shard, index, loadVersion])

  useEffect(() => { writePlace({ q: query.trim(), person, employer }) }, [query, person, employer])

  // The rows that answer the search, then grouped into the names they appear under.
  const people = useMemo(() => {
    if (!wanted || rows.shard !== shard || !index) return []
    const matching = rows.list.filter((row) => {
      if (!matchesNameQuery(row[0], wanted.typedName, index.sources?.[row[6]]?.nameDisclosure)) return false
      if (year !== 'all' && String(row[5]) !== year) return false
      if (sector !== 'all' && index.employers[row[4]][1] !== sector) return false
      return true
    })
    const groups = new Map()
    for (const row of matching) {
      const key = personKey(row[0])
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key).push(row)
    }
    return [...groups.entries()].map(([key, list]) => describeNameGroup(key, list))
      .sort((a, b) => b.years.length - a.years.length || b.latest[2] - a.latest[2])
  }, [rows, shard, wanted, year, sector, index])

  // Employers whose name, or a name they filed under, has every word typed.
  const employerMatches = useMemo(() => {
    const words = wordsOf(query)
    if (!words.length || !employersIndex) return []
    return employersIndex.employers.filter((entry) => {
      if (sector !== 'all' && entry.sector !== sector) return false
      if (year !== 'all' && !entry.counts[Number(year)]) return false
      const text = entry.names.join(' ').toLowerCase()
      return words.every((word) => text.includes(word))
    }).sort((a, b) => Math.max(...b.counts) - Math.max(...a.counts))
  }, [query, employersIndex, sector, year])

  // Filters narrow the search results, not the history of a name opened from one of those results.
  const chosen = useMemo(() => {
    if (!person || rows.shard !== shard) return null
    const list = rows.list.filter((row) => personKey(row[0]) === person)
    return list.length ? describeNameGroup(person, list) : null
  }, [person, rows, shard])
  const openEmployer = (slug) => { setEmployer(slug); setPerson(null); globalThis.scrollTo?.({ top: 0 }) }
  const openPerson = (name) => { setEmployer(null); setQuery(name); setPerson(personKey(name)); globalThis.scrollTo?.({ top: 0 }) }
  const search = (text) => { setQuery(text); setPerson(null); setShown(24); setEmployersShown(6) }

  if (failed) return <p className="gallery__intro">The requested salary records could not be loaded. <button type="button" onClick={() => { setFailed(false); setLoadVersion((value) => value + 1) }}>Retry</button></p>
  if (!index || !employersIndex) return <p className="gallery__intro" role="status">Loading the salary index…</p>

  const total = Object.values(index.shards).reduce((a, b) => a + b, 0)
  const sectors = [...new Set(employersIndex.employers.map((entry) => entry.sector))].filter(Boolean).sort()

  if (employer) {
    // An employer by its slug, an old slug, or the government body it is (the panel links by body).
    const canonical = employersIndex.aliases?.[employer] ?? employer
    const entry = employersIndex.employers.find((each) => each.slug === canonical) ?? employersIndex.employers.find((each) => each.body === canonical)
    if (entry) return <EmployerPage key={entry.slug} entry={entry} years={employersIndex.years} sources={employersIndex.sources ?? index.sources} initialYear={year} onBack={() => setEmployer(null)} onPerson={openPerson} onOpenGovernment={onOpenGovernment} />
  }

  if (chosen) {
    return (
      <div className="salaries">
        <PersonPage chosen={chosen} all={rows.list} index={index} query={query.trim()} onBack={() => setPerson(null)} onEmployer={openEmployer} onOpenGovernment={onOpenGovernment} />
      </div>
    )
  }

  return (
    <div className="salaries">
      <section className="salaries__intro">
        <h2 className="salaries__heading">Public-sector salaries</h2>
        <p>
          {total.toLocaleString('en-CA')} disclosed pay records from {employersIndex.employers.length} British Columbia public
          employers, {index.years[0]} to {index.years.at(-1)}. Search for a person or an employer.
        </p>
      </section>

      <div className="salaries__search">
        <input
          type="search"
          value={query}
          placeholder="A name or an employer, like “Smith, J” or “Transit”"
          aria-label="Search a name or an employer"
          onChange={(event) => search(event.target.value)}
        />
        <select value={year} onChange={(event) => setYear(event.target.value)} aria-label="Year">
          <option value="all">Every year</option>
          {index.years.map((label, at) => <option key={label} value={String(at)}>{label}</option>)}
        </select>
      </div>

      <div className="salaries__chips" role="group" aria-label="Sector">
        <button type="button" aria-pressed={sector === 'all'} onClick={() => setSector('all')}>All sectors</button>
        {sectors.map((name) => (
          <button key={name} type="button" aria-pressed={sector === name} onClick={() => setSector(sector === name ? 'all' : name)}>
            {name} <span>{employersIndex.employers.filter((entry) => entry.sector === name).length}</span>
          </button>
        ))}
      </div>

      {query.trim() && (
        <>
          {employerMatches.length > 0 && (
            <section aria-labelledby="salaries-employer-results">
              <div className="salaries__head">
                <h2 id="salaries-employer-results" className="salaries__title">Employers</h2>
                <p className="salaries__meta">{count(employerMatches.length, 'employer', 'employers')}</p>
              </div>
              <div className="salaries__grid">
                {employerMatches.slice(0, employersShown).map((entry) => <EmployerCard key={entry.slug} entry={entry} years={employersIndex.years} year={year} onOpen={openEmployer} />)}
              </div>
              {employerMatches.length > employersShown && (
                <button type="button" className="salaries__more" onClick={() => setEmployersShown(Infinity)}>Show all {employerMatches.length}</button>
              )}
            </section>
          )}
          {wanted && !(rows.shard === shard && people.length === 0 && employerMatches.length > 0) && (
            <section aria-labelledby="salaries-results">
              <div className="salaries__head">
                <h2 id="salaries-results" className="salaries__title">People</h2>
                <p className="salaries__meta">{rows.shard === shard ? count(people.length, 'name', 'names') : 'Loading…'}</p>
              </div>
              {rows.shard === shard && people.length === 0 && (
                <p className="salaries__hint">No disclosed name matches “{query.trim()}”{year !== 'all' || sector !== 'all' ? ' with these filters' : ''}. Try the surname alone.</p>
              )}
              <div className="salaries__grid">
                {people.slice(0, shown).map((each) => (
                  <button key={each.key} type="button" className="salaries__card" onClick={() => setPerson(each.key)}>
                    <span className="salaries__lead"><Person /></span>
                    <span className="salaries__text">
                      <span className="salaries__name">{displayName(each.name, index.sources?.[each.latest[6]]?.nameDisclosure)}</span>
                      <span className="salaries__line">{[each.latest[1], index.employers[each.latest[4]][0]].filter(Boolean).join(' · ')}</span>
                      <YearStrip years={index.years} seen={each.years} />
                    </span>
                    <span className="salaries__aside">{money(each.latest[2])}<span className="salaries__line">{index.years[each.latest[5]]}</span></span>
                  </button>
                ))}
              </div>
              {people.length > shown && (
                <button type="button" className="salaries__more" onClick={() => setShown((value) => value + 48)}>
                  Show {Math.min(48, people.length - shown)} more
                </button>
              )}
            </section>
          )}
          {!wanted && !employerMatches.length && <p className="salaries__hint">Type at least two letters of a surname, or part of an employer’s name.</p>}
        </>
      )}

      {!query.trim() && <EmployerList employers={employersIndex.employers} years={employersIndex.years} sector={sector} year={year} onOpen={openEmployer} onSector={setSector} />}

      <p className="salaries__source">
        These are the disclosures imported into this collection. Pay is the period’s reported remuneration or
        compensation, not a salary rate. Reporting thresholds, calendar years, fiscal years and executive-only
        disclosures differ. Missing records do not establish whether someone was employed or paid.
      </p>
    </div>
  )
}

/**
 * Every employer, by sector. With every sector shown, each lists its largest few and a way to the
 * rest; with one chosen, all of its employers.
 */
const PREVIEW = 4
const EmployerList = ({ employers, years, sector, year, onOpen, onSector }) => {
  const visible = employers.filter((entry) => (sector === 'all' || entry.sector === sector) && (year === 'all' || entry.counts[Number(year)] > 0))
  const bySector = new Map()
  for (const entry of visible) {
    if (!bySector.has(entry.sector)) bySector.set(entry.sector, [])
    bySector.get(entry.sector).push(entry)
  }
  return (
    <section aria-labelledby="salaries-employers" className="salaries__employers">
      <div className="salaries__head">
        <h2 id="salaries-employers" className="salaries__title">Employers</h2>
        <p className="salaries__meta">{count(visible.length, 'employer', 'employers')}{year !== 'all' ? ` with records for ${years[Number(year)]}` : ''}</p>
      </div>
      {[...bySector].sort(([a], [b]) => a.localeCompare(b)).map(([name, list]) => {
        const sorted = [...list].sort((a, b) => Math.max(...b.counts) - Math.max(...a.counts))
        const preview = sector === 'all' ? sorted.slice(0, PREVIEW) : sorted
        return (
          <div key={name} className="salaries__sector">
            {sector === 'all' && <h3 className="salaries__sector-title">{name} <span className="salaries__meta">{list.length}</span></h3>}
            <div className="salaries__grid">
              {preview.map((entry) => <EmployerCard key={entry.slug} entry={entry} years={years} year={year} onOpen={onOpen} />)}
            </div>
            {preview.length < sorted.length && (
              <button type="button" className="salaries__more" onClick={() => { onSector(name); globalThis.scrollTo?.({ top: 0 }) }}>All {sorted.length} {name.toLowerCase()} →</button>
            )}
          </div>
        )
      })}
    </section>
  )
}

/** A record as a row: who or what on the left, the pay on the right, and its source under the pay. */
const RecordRow = ({ rank, name, position, pay, expenses, expenseText, sourceId, sources, onPerson, nameDisclosure }) => (
  <li className="salaries-row">
    {rank != null && <span className="salaries-row__rank">{rank}</span>}
    <span className="salaries-row__who">
      {name !== undefined && (name
        ? <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(name)}>{displayName(name, nameDisclosure)}</button>
        : <span className="salaries-row__name salaries__line">Name not given</span>)}
      {position && <span className="salaries__line">{position}</span>}
    </span>
    <span className="salaries-row__pay">
      {money(pay)}
      {(expenses || sourceId) && (
        <span className="salaries__line">
          {expenses ? `${expenseText} ${money(expenses)}` : ''}
          {expenses && sourceId ? ' · ' : ''}
          {sourceId && <SourceLink sourceId={sourceId} sources={sources} />}
        </span>
      )}
    </span>
  </li>
)

/**
 * An employer's year: its records by position, where the disclosure names positions, or by person.
 * Spellings of one position (capitals, stops, spacing) are counted as one.
 */
const EmployerPage = ({ entry, years, sources, initialYear, onBack, onPerson, onOpenGovernment }) => {
  const seen = seenYears(entry)
  const [chosenYear, setYear] = useState(initialYear !== 'all' ? Number(initialYear) : null)
  const [rows, setRows] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [filter, setFilter] = useState('')
  const [mode, setMode] = useState('positions')
  const [open, setOpen] = useState(null)
  const [openShown, setOpenShown] = useState(50)
  const [shown, setShown] = useState(40)

  useEffect(() => {
    let live = true
    setFailed(false)
    setRows(null)
    loadJson(`salaries/employers/${entry.slug}.json.gzip`).then((list) => live && setRows(list), () => live && setFailed(true))
    return () => { live = false }
  }, [entry.slug, loadVersion])

  const year = chosenYear ?? seen.at(-1) ?? 0
  const coverage = coverageAt({ ...entry, years }, year)
  const people = useMemo(() => (rows ? rows.filter((row) => row[4] === year) : []), [rows, year])
  // Whether the year's disclosure names positions: some employers give them one year and not the next.
  const withPositions = people.length > 0 && people.filter((row) => row[1]).length / people.length >= 0.5
  const view = withPositions ? mode : 'people'
  // A source shown once for the year is not repeated on every row.
  const oneSource = new Set(people.map((row) => row[5])).size <= 1

  const positions = useMemo(() => {
    const groups = new Map()
    for (const row of people) {
      const key = positionKey(row[1]) || '—'
      if (!groups.has(key)) groups.set(key, { key, spellings: new Map(), rows: [] })
      const group = groups.get(key)
      group.rows.push(row)
      if (row[1]) group.spellings.set(row[1], (group.spellings.get(row[1]) ?? 0) + 1)
    }
    return [...groups.values()].map((group) => {
      const pay = group.rows.map((row) => row[2])
      const label = [...group.spellings].sort((a, b) => b[1] - a[1])[0]?.[0] ?? null
      return { ...group, label, median: median(pay), low: Math.min(...pay), high: Math.max(...pay) }
    }).sort((a, b) => (a.label === null) - (b.label === null) || b.rows.length - a.rows.length || b.median - a.median)
  }, [people])

  const words = wordsOf(filter)
  const has = (text) => words.every((word) => String(text ?? '').toLowerCase().includes(word))
  const matchingPositions = positions.filter((position) => has(position.label ?? 'position not given'))
  const ranked = useMemo(() => [...people].sort((a, b) => b[2] - a[2]), [people])
  const matchingPeople = ranked.filter((row) => has(`${row[0] ?? ''} ${row[1] ?? ''}`))
  const pay = people.map((row) => row[2])
  const positionCount = positions.filter((position) => position.label).length
  const pick = (at) => { setYear(at); setOpen(null); setShown(40) }

  return (
    <div className="salaries">
      <section className="salaries__person" aria-labelledby="salaries-employer">
        <button type="button" className="salaries__back" onClick={onBack}>← Salaries</button>
        <h2 id="salaries-employer" className="salaries__heading">{entry.names.at(-1)}</h2>
        <p className="salaries__note">
          {entry.sector}
          {entry.names.length > 1 ? ` · also filed as ${entry.names.slice(0, -1).map((name) => `“${name}”`).join(', ')}` : ''}
          {entry.body && onOpenGovernment && (
            <> · <button type="button" className="salaries__link" onClick={() => onOpenGovernment(entry.body, Number(years[year].slice(0, 4)))}>See it in Government</button></>
          )}
        </p>
        <YearPicker years={years} counts={entry.counts} value={year} onChange={pick} />
        <h3 className="salaries__year-title">{years[year]}</h3>
        <DisclosureSummary
          coverage={coverage}
          sources={sources}
          more={entry.repeated?.length > 0 && <p>Compiled records for {entry.repeated.join(', ')} were excluded after extensive repetition of names and pay from an earlier collection.</p>}
        />
        {!entry.counts[year] && <p className="salaries__hint">{coverage.status === 'excluded' ? 'These records were excluded after a data-quality check.' : 'No records have been imported for this employer in this year.'} That does not mean it had no staff or made no payments.</p>}
        {rows && entry.counts[year] > 0 && (
          <dl className={`salaries__tiles${positionCount ? '' : ' salaries__tiles--three'}`}>
            <div><dt>Records</dt><dd>{people.length.toLocaleString('en-CA')}</dd></div>
            <div><dt>Median</dt><dd>{pay.length ? money(median(pay)) : '—'}</dd></div>
            <div><dt>Highest</dt><dd>{pay.length ? money(Math.max(...pay)) : '—'}</dd></div>
            {positionCount > 0 && <div><dt>Positions</dt><dd>{positionCount.toLocaleString('en-CA')}</dd></div>}
          </dl>
        )}
      </section>

      {failed && <p className="salaries__hint" role="alert">The employer’s records could not be loaded. <button type="button" onClick={() => setLoadVersion((value) => value + 1)}>Retry</button></p>}
      {!rows && !failed && <p className="salaries__hint" role="status">Loading its records…</p>}
      {rows && people.length > 0 && (
        <section aria-labelledby="salaries-records">
          <div className="salaries__search salaries__search--one">
            <input type="search" value={filter} placeholder={withPositions ? 'Find a name or a position' : 'Find a name'} aria-label="Find a name or a position" onChange={(event) => { setFilter(event.target.value); setShown(40) }} />
          </div>
          <div className="salaries__head">
            <h2 id="salaries-records" className="salaries__title">
              {withPositions
                ? (
                  <span className="salaries__toggle" role="group" aria-label="Show records">
                    <button type="button" aria-pressed={view === 'positions'} onClick={() => { setMode('positions'); setShown(40) }}>By position</button>
                    <button type="button" aria-pressed={view === 'people'} onClick={() => { setMode('people'); setShown(40) }}>Highest paid</button>
                  </span>
                )
                : 'Highest paid'}
            </h2>
            <p className="salaries__meta">
              {view === 'positions' ? count(matchingPositions.length, 'position', 'positions') : count(matchingPeople.length, 'record', 'records')} · {years[year]}
            </p>
          </div>
          {!withPositions && <p className="salaries__hint salaries__hint--small">This year’s records do not name positions.</p>}
          {words.length > 0 && (view === 'positions' ? matchingPositions : matchingPeople).length === 0 && (
            <p className="salaries__hint">Nothing in {years[year]} matches “{filter.trim()}”.</p>
          )}

          {view === 'people' && (
            <ol className="salaries-rows">
              {matchingPeople.slice(0, shown).map((row) => (
                <RecordRow
                  key={`${row[0]}-${row[2]}-${ranked.indexOf(row)}`}
                  rank={ranked.indexOf(row) + 1}
                  name={row[0]}
                  position={row[1]}
                  pay={row[2]}
                  expenses={row[3]}
                  expenseText={expenseLabel(row[5], sources)}
                  sourceId={oneSource ? null : row[5]}
                  sources={sources}
                  nameDisclosure={sources?.[row[5]]?.nameDisclosure}
                  onPerson={onPerson}
                />
              ))}
            </ol>
          )}

          {view === 'positions' && (
            <div className="salaries__grid">
              {matchingPositions.slice(0, shown).map((position) => (
                <div key={position.key} className="salaries__position" data-open={open === position.key || undefined}>
                  <button type="button" className="salaries__card" aria-expanded={open === position.key} onClick={() => { setOpen((current) => (current === position.key ? null : position.key)); setOpenShown(50) }}>
                    <span className="salaries__lead"><Role /></span>
                    <span className="salaries__text">
                      <span className="salaries__name" data-missing={!position.label || undefined}>{position.label ?? 'Position not given'}</span>
                      <span className="salaries__line">
                        {count(position.rows.length, 'record', 'records')}
                        {position.rows.length > 1 ? ` · ${money(position.low)}–${money(position.high)}` : ''}
                      </span>
                    </span>
                    <span className="salaries__aside">{money(position.median)}<span className="salaries__line">{position.rows.length > 1 ? 'median' : 'paid'}</span></span>
                  </button>
                  {open === position.key && (
                    <ol className="salaries-rows salaries-rows--inner">
                      {[...position.rows].sort((a, b) => b[2] - a[2]).slice(0, openShown).map((row, at) => (
                        <RecordRow
                          key={at}
                          name={row[0]}
                          pay={row[2]}
                          expenses={row[3]}
                          expenseText={expenseLabel(row[5], sources)}
                          sourceId={oneSource ? null : row[5]}
                          sources={sources}
                          nameDisclosure={sources?.[row[5]]?.nameDisclosure}
                          onPerson={onPerson}
                        />
                      ))}
                    </ol>
                  )}
                  {open === position.key && position.rows.length > openShown && (
                    <button type="button" className="salaries__more salaries__more--inner" onClick={() => setOpenShown(Infinity)}>Show all {position.rows.length.toLocaleString('en-CA')}</button>
                  )}
                </div>
              ))}
            </div>
          )}

          {(view === 'positions' ? matchingPositions : matchingPeople).length > shown && (
            <button type="button" className="salaries__more" onClick={() => setShown((value) => value + 80)}>
              Show {Math.min(80, (view === 'positions' ? matchingPositions : matchingPeople).length - shown)} more
            </button>
          )}
        </section>
      )}
    </div>
  )
}

/**
 * A disclosed name's years: its pay as a chart, then year by year as a table, with the years it is
 * absent from folded into runs that give the reason. Names that only may be the same — a surname with
 * compatible initials — are kept apart, below. None of this is a verified employment history.
 */
const PersonPage = ({ chosen, all, index, query, onBack, onEmployer, onOpenGovernment }) => {
  const employerOf = (row) => index.employers[row[4]]
  const slugOf = (row) => employerOf(row)[3]
  const associated = [...new Set(chosen.rows.map(slugOf))]
  const employers = [...new Map(chosen.rows.map((row) => {
    const [name, , body, slug] = employerOf(row)
    return [slug, { name, body, slug }]
  })).values()]
  const near = all.filter((row) => !chosen.rows.includes(row))
    .map((row) => ({ row, link: nameMatch(row[0], chosen.name) }))
    .filter(({ link }) => link === 'initial' || link === 'partial')
    .map(({ row }) => row)
  const yearLabels = chosen.years.map((at) => index.years[at])
  // The chart plots a year's highest record: where a name has more than one in a year, the table
  // shows them all.
  const points = chosen.years.map((at) => ({ year: at, pay: Math.max(...chosen.rows.filter((row) => row[5] === at).map((row) => row[2])) }))
  const missing = index.years.map((_, at) => at).filter((at) => !chosen.years.includes(at))
  const runs = gapRuns(missing, (at) => gapReason(index.coverage, associated, at))
  const lines = [
    ...chosen.years.map((at) => ({ at, rows: chosen.rows.filter((row) => row[5] === at).sort((a, b) => b[2] - a[2]) })),
    ...runs.map((run) => ({ at: run.from, run }))
  ].sort((a, b) => b.at - a.at)

  const recordLine = (row, as) => {
    const [employerName, , , slug] = employerOf(row)
    return (
      <div className="salaries-record" key={`${row[5]}-${row[2]}-${row[4]}-${as ?? ''}`}>
        <span className="salaries-record__what">
          {row[1] && <span className="salaries__name">{row[1]}</span>}
          {/* The employer, unless it is the one employer the header names. */}
          {(employers.length > 1 || !employers.some((each) => each.slug === slug)) && (
            <span className={row[1] ? 'salaries__line' : 'salaries__name'}>
              <button type="button" className="salaries__link" onClick={() => onEmployer(slug)}>{employerName}</button>
            </span>
          )}
          {as && <span className="salaries__line">As “{as}”</span>}
        </span>
        <span className="salaries-row__pay">
          {money(row[2])}
          <span className="salaries__line">
            {row[3] ? `${expenseLabel(row[6], index.sources)} ${money(row[3])} · ` : ''}
            <SourceLink sourceId={row[6]} sources={index.sources} />
          </span>
        </span>
      </div>
    )
  }

  return (
    <section className="salaries__person" aria-labelledby="salaries-person">
      <button type="button" className="salaries__back" onClick={onBack}>← All “{query}” results</button>
      <h2 id="salaries-person" className="salaries__heading">{displayName(chosen.name, index.sources?.[chosen.latest[6]]?.nameDisclosure)}</h2>
      <p className="salaries__note">
        {employers.map((employer, at) => (
          <span key={employer.slug}>
            {at > 0 ? ', ' : ''}
            <button type="button" className="salaries__link" onClick={() => onEmployer(employer.slug)}>{employer.name}</button>
            {employer.body && onOpenGovernment && <> (<button type="button" className="salaries__link" onClick={() => onOpenGovernment(employer.body, Number(index.years[chosen.latest[5]].slice(0, 4)))}>in Government</button>)</>}
          </span>
        ))}
        {' '}· {yearLabels.length} {yearLabels.length === 1 ? 'year' : 'years'}, {yearSpan(yearLabels)} · disclosed as “{chosen.name}”
      </p>
      <p className="salaries__hint salaries__hint--small">
        Records are grouped by the disclosed name only, so they may not all concern one person.
        {chosen.shared ? ' Some years have more than one record under this name: different people, separate payments or source duplicates.' : ''}
      </p>

      <dl className="salaries__tiles salaries__tiles--three">
        <div><dt>Latest</dt><dd>{money(chosen.latest[2])}</dd><dd className="salaries__line">{index.years[chosen.latest[5]]}</dd></div>
        <div><dt>Highest</dt><dd>{money(Math.max(...points.map((point) => point.pay)))}</dd><dd className="salaries__line">{index.years[points.reduce((best, point) => (point.pay > best.pay ? point : best)).year]}</dd></div>
        <div><dt>Years</dt><dd>{yearLabels.length}</dd><dd className="salaries__line">of {index.years.length} in the collection</dd></div>
      </dl>

      {points.length > 1 && <PayChart years={index.years} points={points} />}

      <h3 className="salaries__title salaries__title--spaced">Year by year</h3>
      <ol className="salaries-years">
        {lines.map((line) => line.run
          ? (
            <li key={`gap-${line.run.from}`} className="salaries-years__gap">
              <span className="salaries-years__label">{line.run.from === line.run.to ? index.years[line.run.from] : `${index.years[line.run.from]} – ${index.years[line.run.to]}`}</span>
              <span className="salaries__line">{GAP_LABELS[line.run.reason]}</span>
            </li>
          )
          : (
            <li key={line.at} className="salaries-years__year">
              <span className="salaries-years__label">{index.years[line.at]}</span>
              <span className="salaries-years__records">{line.rows.map((row) => recordLine(row))}</span>
            </li>
          ))}
      </ol>

      {near.length > 0 && (
        <>
          <h3 className="salaries__title salaries__title--spaced">Possible matches</h3>
          <p className="salaries__hint salaries__hint--small">The same surname with compatible initials or given names. These may be the same person or someone else.</p>
          <ol className="salaries-years salaries-years--weak">
            {[...new Set(near.map((row) => row[5]))].sort((a, b) => b - a).map((at) => (
              <li key={at} className="salaries-years__year">
                <span className="salaries-years__label">{index.years[at]}</span>
                <span className="salaries-years__records">{near.filter((row) => row[5] === at).sort((a, b) => b[2] - a[2]).map((row) => recordLine(row, row[0]))}</span>
              </li>
            ))}
          </ol>
        </>
      )}

      <details className="salaries-disclosure__more">
        <summary>About missing years</summary>
        <p>{missingYearMessage(index.coverage, associated, missing.find((at) => gapReason(index.coverage, associated, at) === 'not-found') ?? missing[0] ?? 0)}</p>
        <p>Pay is the reported remuneration for the period, not a salary rate. Thresholds, reporting periods and the scope of each disclosure differ; each record links to the document it comes from.</p>
      </details>
    </section>
  )
}
