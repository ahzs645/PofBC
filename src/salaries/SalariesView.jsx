// Search the remuneration records imported here, with explicit employer/year coverage and sources.
//
// Disclosures differ in reporting period, threshold and scope. A search loads one
// slice of the index — the surnames that start with the same two letters (scripts/build-salaries.mjs)
// — and groups its rows into the people they appear to be. Opening one lines their years up. An
// employer's page loads that employer's rows and sets out the positions in it: how many held each,
// what they were paid, and who.
//
// A name in two years' disclosures is not proof of one person. Multiple rows may be different people,
// multiple payments to one person, or source duplicates; none of these is inferred from a name alone.

import { useEffect, useMemo, useState } from 'react'
import { displayName, matchesNameQuery, nameMatch, personKey, positionKey, readName, surnameShard } from './people.js'
import { coverageAt, expenseLabel, filterEmployers, missingYearMessage, rowCoverage } from './coverage.js'
import { DisclosureEvidence, SourceLink } from './DisclosureEvidence.jsx'
import { formatMoney as money, medianMoney as median } from './money.js'

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

/** A position: a briefcase, in the same layered style. */
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
  const [shown, setShown] = useState(30)

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

  const sectors = useMemo(() => (index ? [...new Set(index.employers.map(([, sectorName]) => sectorName))].filter(Boolean).sort() : []), [index])

  // The rows that answer the search, then grouped into the people they appear to be.
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

  // Filters narrow the search results, not the history of a name opened from one of those results.
  const chosen = useMemo(() => {
    if (!person || rows.shard !== shard) return null
    const list = rows.list.filter((row) => personKey(row[0]) === person)
    return list.length ? describeNameGroup(person, list) : null
  }, [person, rows, shard])
  const openEmployer = (slug) => { setEmployer(slug); setPerson(null); globalThis.scrollTo?.({ top: 0 }) }
  const openPerson = (name) => { setEmployer(null); setQuery(name); setPerson(personKey(name)); globalThis.scrollTo?.({ top: 0 }) }

  if (failed) return <p className="gallery__intro">The requested salary records could not be loaded. <button type="button" onClick={() => { setFailed(false); setLoadVersion((value) => value + 1) }}>Retry</button></p>
  if (!index || !employersIndex) return <p className="gallery__intro" role="status">Loading the salary index…</p>

  const employerOf = (row) => index.employers[row[4]]
  const yearLabel = (row) => index.years[row[5]]
  const total = Object.values(index.shards).reduce((a, b) => a + b, 0)

  if (employer) {
    const canonical = employersIndex.aliases?.[employer] ?? employer
    const entry = employersIndex.employers.find((each) => each.slug === canonical)
    if (entry) return <EmployerPage key={entry.slug} entry={entry} years={employersIndex.years} sources={employersIndex.sources ?? index.sources} initialYear={year} onBack={() => setEmployer(null)} onPerson={openPerson} onOpenGovernment={onOpenGovernment} />
  }

  return (
    <div className="salaries">
      <section className="salaries__intro">
        <h2 className="salaries__heading">Public-sector salaries</h2>
        <p>
          Search {total.toLocaleString('en-CA')} named remuneration records from {employersIndex.employers.length} British Columbia public employers,
          spanning {index.years[0]}–{index.years.at(-1)}. Coverage varies by employer and reporting period; some records
          cover executives only. Search a surname to compare disclosed names across years, or open an employer to see
          its records, reported positions and sources.
        </p>
      </section>

      <div className="salaries__search">
        <input
          type="search"
          value={query}
          placeholder="Surname, then a given name if you like — “Smith, J”"
          aria-label="Search a name"
          onChange={(event) => { setQuery(event.target.value); setPerson(null); setShown(30) }}
        />
        <select value={year} onChange={(event) => setYear(event.target.value)} aria-label="Year">
          <option value="all">Every year</option>
          {index.years.map((label, at) => <option key={label} value={String(at)}>{label}</option>)}
        </select>
        <select value={sector} onChange={(event) => setSector(event.target.value)} aria-label="Sector">
          <option value="all">Every sector</option>
          {sectors.map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
      </div>

      {chosen && (
        <section className="salaries__person" aria-labelledby="salaries-person">
          <button type="button" className="salaries__back" onClick={() => setPerson(null)}>← All “{query.trim()}” results</button>
          <h2 id="salaries-person" className="salaries__heading">{displayName(chosen.name, index.sources?.[chosen.latest[6]]?.nameDisclosure)}</h2>
          <p className="salaries__note">
            Disclosed as “{chosen.name}” in {chosen.years.length} of {index.years.length} years.
            {' A matching name does not verify that records concern the same person.'}
            {chosen.shared ? ' Multiple records share this name in a year; they can represent different people, multiple payments or source duplicates.' : ''}
          </p>
          <PersonTimeline chosen={chosen} all={rows.list} index={index} onEmployer={openEmployer} onOpenGovernment={onOpenGovernment} />
        </section>
      )}

      {wanted && !chosen && (
        <section aria-labelledby="salaries-results">
          <div className="salaries__head">
            <h2 id="salaries-results" className="salaries__title">People</h2>
            <p className="salaries__meta">{rows.shard === shard ? count(people.length, 'name', 'names') : 'Loading…'}</p>
          </div>
          <div className="salaries__grid">
            {people.slice(0, shown).map((each) => (
              <button key={each.key} type="button" className="salaries__card" onClick={() => setPerson(each.key)}>
                <span className="salaries__lead"><Person /></span>
                <span className="salaries__text">
                  <span className="salaries__name">{displayName(each.name, index.sources?.[each.latest[6]]?.nameDisclosure)}</span>
                  <span className="salaries__line">{[each.latest[1], employerOf(each.latest)[0]].filter(Boolean).join(' · ')}</span>
                  <span className="salaries__years">
                    {index.years.map((label, at) => (
                      <span key={label} data-seen={each.years.includes(at) || undefined}>{label}</span>
                    ))}
                  </span>
                </span>
                <span className="salaries__aside">{money(each.latest[2])}<span className="salaries__line">{yearLabel(each.latest)}</span></span>
              </button>
            ))}
          </div>
          {people.length > shown && (
            <button type="button" className="salaries__more" onClick={() => setShown((value) => value + 60)}>
              Show {Math.min(60, people.length - shown)} more
            </button>
          )}
        </section>
      )}

      {!wanted && <EmployerList employers={employersIndex.employers} years={employersIndex.years} sector={sector} year={year} onOpen={openEmployer} />}

      <p className="salaries__source">
        These are the disclosures imported into this collection. Pay is the period’s reported remuneration or
        compensation, not a salary rate. Reporting thresholds, calendar years, fiscal years and executive-only
        disclosures differ. Missing records do not establish whether someone was employed or paid.
      </p>
    </div>
  )
}

/** Every employer, by sector, each a way to its positions. */
const EmployerList = ({ employers, years, sector, year, onOpen }) => {
  const selectedYear = (entry) => year !== 'all' ? Number(year) : entry.counts.reduce((best, value, at) => (value ? at : best), 0)
  const visible = filterEmployers(employers, sector, year)
  const bySector = new Map()
  for (const entry of visible) {
    if (!bySector.has(entry.sector)) bySector.set(entry.sector, [])
    bySector.get(entry.sector).push(entry)
  }
  return (
    <section aria-labelledby="salaries-employers">
      <div className="salaries__head">
        <h2 id="salaries-employers" className="salaries__title">Employers</h2>
        <p className="salaries__meta">{count(visible.length, 'employer', 'employers')}{year !== 'all' ? ` with imported records for ${years[Number(year)]}` : ''}</p>
      </div>
      {[...bySector].sort(([a], [b]) => a.localeCompare(b)).map(([name, list]) => (
        <details key={name} className="salaries__sector" open={sector !== 'all' || undefined}>
          <summary>{name} <span className="salaries__meta">{list.length}</span></summary>
          <div className="salaries__grid">
            {[...list].sort((a, b) => Math.max(...b.counts) - Math.max(...a.counts)).map((entry) => (
              <button key={entry.slug} type="button" className="salaries__card" onClick={() => onOpen(entry.slug)}>
                <span className="salaries__lead"><Role /></span>
                <span className="salaries__text">
                  <span className="salaries__name">{entry.names.at(-1)}</span>
                  <span className="salaries__years">
                    {years.map((label, at) => <span key={label} data-seen={entry.counts[at] > 0 || undefined}>{label}</span>)}
                  </span>
                </span>
                <span className="salaries__aside">{entry.counts[selectedYear(entry)].toLocaleString('en-CA')}<span className="salaries__line">records · {years[selectedYear(entry)]}</span></span>
              </button>
            ))}
          </div>
        </details>
      ))}
    </section>
  )
}

/**
 * An employer's positions in a year: each with how many held it and their pay, most held first, and
 * opened, who held it. Spellings of one position (capitals, stops, spacing) are counted as one.
 */
const EmployerPage = ({ entry, years, sources, initialYear, onBack, onPerson, onOpenGovernment }) => {
  const seen = years.map((_, at) => at).filter((at) => entry.counts[at] > 0)
  const [chosenYear, setYear] = useState(initialYear !== 'all' ? Number(initialYear) : null)
  const [rows, setRows] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [filter, setFilter] = useState('')
  const [open, setOpen] = useState(null)
  const [shown, setShown] = useState(40)

  useEffect(() => {
    let live = true
    setFailed(false)
    setRows(null)
    loadJson(`salaries/employers/${entry.slug}.json.gzip`).then((list) => live && setRows(list), () => live && setFailed(true))
    return () => { live = false }
  }, [entry.slug, loadVersion])

  // How much of each year's disclosure names positions: some employers give them one year and not the
  // next. The page opens on the latest available year, regardless of whether positions are supplied.
  const named = useMemo(() => years.map((_, at) => {
    const list = rows ? rows.filter((row) => row[4] === at) : []
    return list.length ? list.filter((row) => row[1]).length / list.length : 0
  }), [rows, years])
  const year = chosenYear ?? seen.at(-1) ?? 0
  const coverage = coverageAt({ ...entry, years }, year)

  const positions = useMemo(() => {
    if (!rows) return []
    const groups = new Map()
    for (const row of rows) {
      if (row[4] !== year) continue
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
  }, [rows, year])

  const words = filter.trim().toLowerCase().split(/\s+/).filter(Boolean)
  const matching = positions.filter((position) => words.every((word) => (position.label ?? 'position not given').toLowerCase().includes(word)))
  const people = rows ? rows.filter((row) => row[4] === year) : []
  const pay = people.map((row) => row[2])

  return (
    <div className="salaries">
      <section className="salaries__person" aria-labelledby="salaries-employer">
        <button type="button" className="salaries__back" onClick={onBack}>← Salaries</button>
        <h2 id="salaries-employer" className="salaries__heading">{entry.names.at(-1)}</h2>
        <p className="salaries__note">
          {entry.sector}
          {entry.names.length > 1 ? ` · also filed as ${entry.names.slice(0, -1).map((name) => `“${name}”`).join(', ')}` : ''}
          {entry.body && onOpenGovernment && (
            <> · <button type="button" className="salaries__link" onClick={() => onOpenGovernment(entry.body, Number(years[year].slice(0, 4)))}>in the government graph</button></>
          )}
        </p>
        {entry.repeated?.length > 0 && (
          <p className="salaries__note">
            Compiled records for {entry.repeated.join(', ')} were excluded after extensive repetition of names and pay
            from an earlier collection. Sources and any verified replacements are listed for each year below.
          </p>
        )}
        <div className="salaries__years-switch" role="group" aria-label="Disclosure year">
          {years.map((label, at) => (
            <button key={label} type="button" aria-pressed={at === year} title={!entry.counts[at] ? 'No usable records imported; select to see coverage information' : rows && named[at] < 0.5 ? 'Most records do not include a position' : undefined} onClick={() => { setYear(at); setOpen(null); setFilter(''); setShown(40) }}>
              {label}{!entry.counts[at] ? ' —' : rows && named[at] < 0.5 ? ' ·' : ''}
            </button>
          ))}
        </div>
        <DisclosureEvidence coverage={coverage} sources={sources} />
        {!entry.counts[year] && <p className="salaries__note">{coverage.status === 'excluded' ? 'These records were excluded following a data-quality check.' : 'No records have been imported for this employer and period.'} This does not mean the employer had no staff or made no payments.</p>}
        {rows && entry.counts[year] > 0 && (
          <dl className="salaries__tiles">
            <div><dt>Records</dt><dd>{people.length.toLocaleString('en-CA')}</dd></div>
            <div><dt>Reported positions</dt><dd>{positions.filter((position) => position.label).length.toLocaleString('en-CA')}</dd></div>
            <div><dt>Median</dt><dd>{pay.length ? money(median(pay)) : '—'}</dd></div>
            <div><dt>Highest</dt><dd>{pay.length ? money(Math.max(...pay)) : '—'}</dd></div>
          </dl>
        )}
      </section>

      {failed && <p className="salaries__hint" role="alert">The employer’s records could not be loaded. <button type="button" onClick={() => setLoadVersion((value) => value + 1)}>Retry</button></p>}
      {!rows && !failed && <p className="salaries__hint" role="status">Loading its records…</p>}
      {rows && entry.counts[year] > 0 && named[year] < 0.5 && (
        <section aria-labelledby="salaries-people">
          <p className="salaries__note">
            Most imported records for {years[year]} do not include a position. Position availability can differ
            from the original disclosure and from other years in this collection.
          </p>
          <div className="salaries__head">
            <h2 id="salaries-people" className="salaries__title">Highest paid</h2>
            <p className="salaries__meta">{count(people.length, 'record', 'records')} · {years[year]}</p>
          </div>
          <ul className="salaries__holders salaries__holders--page">
            {[...people].sort((a, b) => b[2] - a[2]).slice(0, shown).map((row, at) => (
              <li key={at}>
                {row[0]
                  ? <button type="button" className="salaries__link" onClick={() => onPerson(row[0])}>{displayName(row[0], sources?.[row[5]]?.nameDisclosure)}</button>
                  : <span className="salaries__line">Name not given</span>}
                <span>{money(row[2])} <SourceLink sourceId={row[5]} sources={sources} /></span>
              </li>
            ))}
          </ul>
          {people.length > shown && (
            <button type="button" className="salaries__more" onClick={() => setShown((value) => value + 80)}>
              Show {Math.min(80, people.length - shown)} more
            </button>
          )}
        </section>
      )}
      {rows && entry.counts[year] > 0 && named[year] >= 0.5 && (
        <section aria-labelledby="salaries-positions">
          <div className="salaries__search salaries__search--one">
            <input type="search" value={filter} placeholder="Find a position" aria-label="Find a position" onChange={(event) => { setFilter(event.target.value); setShown(40) }} />
          </div>
          <div className="salaries__head">
            <h2 id="salaries-positions" className="salaries__title">Positions</h2>
            <p className="salaries__meta">{count(matching.length, 'position', 'positions')} · {years[year]}</p>
          </div>
          <div className="salaries__grid">
            {matching.slice(0, shown).map((position) => (
              <div key={position.key} className="salaries__position" data-open={open === position.key || undefined}>
                <button type="button" className="salaries__card" aria-expanded={open === position.key} onClick={() => setOpen((current) => (current === position.key ? null : position.key))}>
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
                  <ul className="salaries__holders">
                    {position.rows.map((row, at) => (
                      <li key={at}>
                        {row[0]
                          ? <button type="button" className="salaries__link" onClick={() => onPerson(row[0])}>{displayName(row[0], sources?.[row[5]]?.nameDisclosure)}</button>
                          : <span className="salaries__line">Name not given</span>}
                        <span>{money(row[2])} <SourceLink sourceId={row[5]} sources={sources} /></span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
          {matching.length > shown && (
            <button type="button" className="salaries__more" onClick={() => setShown((value) => value + 80)}>
              Show {Math.min(80, matching.length - shown)} more
            </button>
          )}
        </section>
      )}
    </div>
  )
}

/**
 * A disclosed name's years, with compatible abbreviated names clearly marked as possible matches.
 * These are search results, not a verified employment history. The card leads with the position, since the name
 * is the page's; a row's own spelling of the name is shown only where it differs.
 */
const PersonTimeline = ({ chosen, all, index, onEmployer, onOpenGovernment }) => {
  const near = all.filter((row) => !chosen.rows.includes(row))
    .map((row) => ({ row, link: nameMatch(row[0], chosen.name) }))
    .filter(({ link }) => link === 'initial' || link === 'partial')
  const employerKey = (row) => index.employers[row[4]][3]
  const associatedEmployers = [...new Set(chosen.rows.map(employerKey))]
  const entries = [
    ...chosen.rows.map((row) => ({ row, link: 'name' })),
    ...near
  ].sort((a, b) => a.row[5] - b.row[5] || b.row[2] - a.row[2])
  const byYear = index.years.map((label, at) => ({ label, yearIndex: at, entries: entries.filter(({ row }) => row[5] === at) }))
  return (
    <ol className="salaries__timeline">
      {byYear.map(({ label, yearIndex, entries: list }) => {
        return (
          <li key={label} className="salaries__year">
            <p className="salaries__year-label">{label}</p>
            {list.length === 0 && <p className="salaries__line">{missingYearMessage(index.coverage, associatedEmployers, yearIndex)}</p>}
            <div className="salaries__grid">
              {list.map(({ row, link }, at) => {
                const [employerName, sectorName, body, slug] = index.employers[row[4]]
                const why = link === 'initial'
                  ? 'Possible match: surname and compatible initials only; identity unverified'
                  : link === 'partial' ? 'Possible match: compatible but incomplete given names; identity unverified'
                    : chosen.rows.some((other) => other !== row && other[5] !== row[5] && employerKey(other) === employerKey(row)) ? 'Same disclosed name and employer; identity unverified' : 'Same disclosed name; identity unverified'
                return (
                  <div key={at} className="salaries__card salaries__card--still" data-weak={link !== 'name' || undefined}>
                    <span className="salaries__lead"><Role /></span>
                    <div className="salaries__text">
                      <span className="salaries__name" data-missing={!row[1] || undefined}>{row[1] ?? 'Position not given'}</span>
                      <span className="salaries__line">
                        <button type="button" className="salaries__link" onClick={() => onEmployer(slug)}>{employerName}</button>
                        {sectorName ? ` · ${sectorName}` : ''}
                        {body && onOpenGovernment && (
                          <> · <button type="button" className="salaries__link" onClick={() => onOpenGovernment(body, Number(label.slice(0, 4)))}>graph</button></>
                        )}
                      </span>
                      {row[0] !== chosen.name && <span className="salaries__line">As “{row[0]}”</span>}
                      <span className="salaries__why">{why}</span>
                      <DisclosureEvidence coverage={rowCoverage(index.coverage?.[slug]?.[yearIndex], row[6], index.sources)} sources={index.sources} />
                    </div>
                    <span className="salaries__aside">
                      {money(row[2])}
                      {row[3] ? <span className="salaries__line">{expenseLabel(row[6], index.sources)} {money(row[3])}</span> : null}
                    </span>
                  </div>
                )
              })}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
