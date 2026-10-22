// The salary search: every public-sector employee whose pay was disclosed, by name, and the same
// name followed from one year's disclosure to the next.
//
// The disclosures are each employer's list of everyone it paid over $75,000 (and every elected
// official), in 2017/18, 2020/21 and 2023/24, as compiled in the pssdb files. A search loads one
// slice of the index — the surnames that start with the same two letters (scripts/build-salaries.mjs)
// — and groups its rows into the people they appear to be. Opening one lines their years up.
//
// A name in two years' disclosures is not proof of one person. Each year beside a person says what
// joins it to the others: the same full name at the same employer, the same name elsewhere, or only
// an initial that agrees. Two people with one name in one year are shown as that, not merged.

import { useEffect, useMemo, useState } from 'react'
import { nameMatch, personKey, readName, surnameShard } from './people.js'

const BASE = import.meta.env?.BASE_URL ?? '/'
const loaded = new Map()

const money = (value) => (value === null || value === undefined ? '—' : `$${Math.round(value).toLocaleString('en-CA')}`)

/** A gzipped slice, decompressed here; or plain JSON, if the server already undid the gzip. */
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
    }))
  }
  return loaded.get(path)
}

const readPlace = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  return { query: params.get('q') ?? '', person: params.get('person') ?? null }
}

const writePlace = (query, person) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  for (const [key, value] of [['q', query], ['person', person]]) {
    if (value) url.searchParams.set(key, value)
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

/**
 * @param {object} props
 * @param {(node: string, year?: number) => void} [props.onOpenGovernment]  To a body in the diagram.
 */
export const SalariesView = ({ onOpenGovernment }) => {
  const [index, setIndex] = useState(null)
  const [failed, setFailed] = useState(false)
  const initial = readPlace()
  const [query, setQuery] = useState(initial.query)
  const [person, setPerson] = useState(initial.person)
  const [year, setYear] = useState('all')
  const [sector, setSector] = useState('all')
  const [rows, setRows] = useState({ shard: null, list: [] })
  const [shown, setShown] = useState(30)

  useEffect(() => { loadJson('salaries/people/index.json').then(setIndex, () => setFailed(true)) }, [])

  // What was typed, read as a name: a surname, and perhaps the start of a given name after a comma
  // or a space ("smith, j", "smith john").
  const wanted = useMemo(() => {
    const text = query.trim()
    if (!text) return null
    const [surname, ...given] = text.includes(',') ? text.split(',') : text.split(/\s+/)
    const name = readName(`${surname},${given.join(' ')}`)
    return name.surname.length >= 2 ? { ...name, typedGiven: given.join(' ').trim().toLowerCase().replace(/[^a-z]/g, '') } : null
  }, [query])
  const shard = wanted ? surnameShard(`${wanted.surname},`) : null

  useEffect(() => {
    if (!shard || !index) return undefined
    if (!index.shards[shard]) { setRows({ shard, list: [] }); return undefined }
    let live = true
    loadJson(`salaries/people/${shard}.json.gzip`).then((list) => live && setRows({ shard, list }), () => live && setFailed(true))
    return () => { live = false }
  }, [shard, index])

  useEffect(() => { writePlace(query.trim(), person) }, [query, person])

  const sectors = useMemo(() => (index ? [...new Set(index.employers.map(([, sectorName]) => sectorName))].filter(Boolean).sort() : []), [index])

  // The rows that answer the search, then grouped into the people they appear to be.
  const people = useMemo(() => {
    if (!wanted || rows.shard !== shard || !index) return []
    const matching = rows.list.filter((row) => {
      const name = readName(row[0])
      if (!name.surname.startsWith(wanted.surname)) return false
      if (wanted.typedGiven && !name.given.startsWith(wanted.typedGiven)) return false
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
    return [...groups.entries()].map(([key, list]) => {
      const latest = list.reduce((best, row) => (row[5] > best[5] || (row[5] === best[5] && row[2] > best[2]) ? row : best))
      const years = [...new Set(list.map((row) => row[5]))].sort()
      // More than one row in a year: more than one person shares the name.
      const shared = years.some((each) => list.filter((row) => row[5] === each).length > 1)
      return { key, name: latest[0], latest, years, rows: list, shared }
    }).sort((a, b) => b.years.length - a.years.length || b.latest[2] - a.latest[2])
  }, [rows, shard, wanted, year, sector, index])

  const chosen = person ? people.find((each) => each.key === person) ?? null : null

  if (failed) return <p className="gallery__intro">The salary index could not be loaded.</p>
  if (!index) return <p className="gallery__intro" role="status">Loading the salary index…</p>

  const employer = (row) => index.employers[row[4]]
  const yearLabel = (row) => index.years[row[5]]

  return (
    <div className="salaries">
      <section className="salaries__intro">
        <h2 className="salaries__heading">Public-sector salaries</h2>
        <p>
          Everyone a British Columbia public employer disclosed paying over $75,000, and every elected official,
          in {index.years.join(', ')}: {Object.values(index.shards).reduce((a, b) => a + b, 0).toLocaleString('en-CA')} rows
          from {index.employers.length} employers — the Province’s public service, Crown corporations, health authorities,
          cities, school districts, universities and police. Search a surname, then open a person to follow the name
          from year to year.
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

      {!wanted && <p className="salaries__hint">Type at least two letters of a surname.</p>}

      {chosen && (
        <section className="salaries__person" aria-labelledby="salaries-person">
          <button type="button" className="salaries__back" onClick={() => setPerson(null)}>← All {query.trim()} results</button>
          <h2 id="salaries-person" className="salaries__heading">{chosen.name}</h2>
          <p className="salaries__note">
            The name in {chosen.years.length} of {index.years.length} disclosures.
            {chosen.shared ? ' More than one person has this name in a year, so these rows are not all one person.' : ''}
          </p>
          <PersonTimeline chosen={chosen} all={rows.list} index={index} onOpenGovernment={onOpenGovernment} />
        </section>
      )}

      {wanted && !chosen && (
        <section aria-labelledby="salaries-results">
          <div className="salaries__head">
            <h2 id="salaries-results" className="salaries__title">People</h2>
            <p className="salaries__meta">{rows.shard === shard ? `${people.length.toLocaleString('en-CA')} names` : 'Loading…'}</p>
          </div>
          <div className="salaries__grid">
            {people.slice(0, shown).map((each) => (
              <button key={each.key} type="button" className="salaries__card" onClick={() => setPerson(each.key)}>
                <span className="salaries__lead"><Person /></span>
                <span className="salaries__text">
                  <span className="salaries__name">{each.name}</span>
                  <span className="salaries__line">{[each.latest[1], employer(each.latest)[0]].filter(Boolean).join(' · ')}</span>
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
            <button type="button" className="salaries__more" onClick={() => setShown((count) => count + 60)}>
              Show {Math.min(60, people.length - shown)} more
            </button>
          )}
        </section>
      )}

      <p className="salaries__source">
        Disclosed by each employer under the Financial Information Act and the Public Sector Employers Act; compiled
        in the pssdb public-sector salary files. Pay is the year’s remuneration, not a salary rate, and some employers
        report a calendar year. A name in two years is not proof of one person.
      </p>
    </div>
  )
}

/**
 * A person's years: every row with their name, and, after it, rows elsewhere in the slice whose name
 * agrees only by initial — each said for what it is. Pay is compared with the year before.
 */
const PersonTimeline = ({ chosen, all, index, onOpenGovernment }) => {
  const near = all.filter((row) => !chosen.rows.includes(row) && nameMatch(row[0], chosen.name) === 'initial')
  // One employer is spelled differently from year to year, so it is compared by its atlas body where it has one.
  const employerKey = (row) => index.employers[row[4]][2] ?? index.employers[row[4]][0].toLowerCase().replace(/[^a-z]/g, '')
  const entries = [
    ...chosen.rows.map((row) => ({ row, link: 'name' })),
    ...near.map((row) => ({ row, link: 'initial' }))
  ].sort((a, b) => a.row[5] - b.row[5] || b.row[2] - a.row[2])
  const byYear = index.years.map((label, at) => ({ label, entries: entries.filter(({ row }) => row[5] === at) }))
  let previous = null
  return (
    <ol className="salaries__timeline">
      {byYear.map(({ label, entries: list }) => {
        const named = list.filter(({ link }) => link === 'name')
        const change = named.length === 1 && previous ? (named[0].row[2] - previous) / previous : null
        if (named.length === 1) previous = named[0].row[2]
        return (
          <li key={label} className="salaries__year">
            <p className="salaries__year-label">{label}</p>
            {list.length === 0 && <p className="salaries__line">Not in this year’s disclosures.</p>}
            <div className="salaries__grid">
              {list.map(({ row, link }, at) => {
                const [employerName, sectorName, body] = index.employers[row[4]]
                const why = link === 'initial'
                  ? 'Same surname and initial only'
                  : chosen.rows.some((other) => other !== row && other[5] !== row[5] && employerKey(other) === employerKey(row)) ? 'Same name, same employer' : 'Same name'
                return (
                  <div key={at} className="salaries__card salaries__card--still" data-weak={link === 'initial' || undefined}>
                    <span className="salaries__lead"><Person /></span>
                    <span className="salaries__text">
                      <span className="salaries__name">{row[0]}</span>
                      <span className="salaries__line">{row[1] ?? 'Position not given'}</span>
                      <span className="salaries__line">
                        {body && onOpenGovernment
                          ? <button type="button" className="salaries__link" onClick={() => onOpenGovernment(body, Number(label.slice(0, 4)))}>{employerName}</button>
                          : employerName}
                        {sectorName ? ` · ${sectorName}` : ''}
                      </span>
                      <span className="salaries__why">{why}</span>
                    </span>
                    <span className="salaries__aside">
                      {money(row[2])}
                      {link === 'name' && change !== null && named.length === 1 && (
                        <span className="salaries__line" data-up={change >= 0 || undefined}>{change >= 0 ? '+' : '−'}{Math.abs(change * 100).toFixed(1)}%</span>
                      )}
                      {row[3] ? <span className="salaries__line">Expenses {money(row[3])}</span> : null}
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
