// Search the remuneration records imported here, with explicit employer/year coverage and sources.
//
// Disclosures differ in reporting period, threshold and scope. A search finds employers by name,
// position titles across employers, and people by name. A name typed without a comma can be read more
// than one way ("john smith" or "smith john"), so it is read the likeliest way first, surname first,
// and only where nobody is disclosed under that reading is the next one tried; the page says which
// reading it shows and offers the others that also find someone. Within a reading, names that answer
// in full come first, then names that only begin as typed, then initials that may be the person meant.
//
// Each search loads one slice of the people index — the surnames that start with the same two letters
// (scripts/build-salaries.mjs) — a slice for each reading. Opening a name sets its years out as a chart
// and a table (PersonPage.jsx); an employer, its positions, people and every year (EmployerPage.jsx);
// a title, the employers that disclosed it (TitlePage.jsx).
//
// A name in two years' disclosures is not proof of one person. Multiple rows may be different people,
// multiple payments to one person, or source duplicates; none of these is inferred from a name alone.

import { useEffect, useMemo, useRef, useState } from 'react'
import { displayName, nameQueryTier, nameReadings, personKey, surnameShard } from './people.js'
import { keyedTitles, titleMatcher } from './positions.js'
import { filterEmployers } from './coverage.js'
import { formatMoney as money } from './money.js'
import { YearStrip } from './parts.jsx'
import { salaryYearIndex } from './viewState.js'
import { count, latestYear, loadJson, More, PersonIcon, readPlace, RoleIcon, seenYears, toTop, wordsOf, writePlace } from './common.jsx'
import { EmployerPage } from './EmployerPage.jsx'
import { PersonPage } from './PersonPage.jsx'
import { TitleCard, TitlePage } from './TitlePage.jsx'

const describeNameGroup = (key, list) => {
  const latest = list.reduce((best, row) => (row[5] > best[5] || (row[5] === best[5] && row[2] > best[2]) ? row : best))
  const years = [...new Set(list.map((row) => row[5]))].sort((a, b) => a - b)
  const shared = years.some((each) => list.filter((row) => row[5] === each).length > 1)
  return { key, name: latest[0], latest, years, rows: list, shared }
}

const shardOf = (reading) => surnameShard(`${reading.surname},`)
const shardOfKey = (key) => key.split('|')[0].slice(0, 2).padEnd(2, '_')
/** A reading as it is written in the disclosures: "smith john" read surname first is "Smith, John". */
const asDisclosed = (reading) => [reading.surname, reading.given].filter(Boolean).join(', ')
  .replace(/(^|[\s,-])(\p{L})/gu, (_, before, letter) => `${before}${letter.toUpperCase()}`)

/** An employer as a card: its name, the years it has records in, and its latest count. */
const EmployerCard = ({ entry, years, year, onOpen }) => {
  const at = year !== 'all' ? Number(year) : latestYear(entry)
  return (
    <button type="button" className="salaries__card" onClick={() => onOpen(entry.slug)}>
      <span className="salaries__lead"><RoleIcon /></span>
      <span className="salaries__text">
        <span className="salaries__name">{entry.names.at(-1)}</span>
        <span className="salaries__line">{count(entry.counts[at], 'record', 'records')} in {years[at]}</span>
        <YearStrip years={years} seen={seenYears(entry)} />
      </span>
    </button>
  )
}

/** A name found by the search, as a card. */
const PersonCard = ({ each, index, onOpen }) => (
  <button type="button" className="salaries__card" onClick={() => onOpen(each.key)}>
    <span className="salaries__lead"><PersonIcon /></span>
    <span className="salaries__text">
      <span className="salaries__name">{displayName(each.name, index.sources?.[each.latest[6]]?.nameDisclosure)}</span>
      <span className="salaries__line">{[each.latest[1], index.employers[each.latest[4]][0]].filter(Boolean).join(' · ')}</span>
      <YearStrip years={index.years} seen={each.years} />
    </span>
    <span className="salaries__aside">{money(each.latest[2])}<span className="salaries__line">{index.years[each.latest[5]]}</span></span>
  </button>
)

/**
 * @param {object} props
 * @param {(node: string, year?: number) => void} [props.onOpenGovernment]  To a body in the diagram.
 */
export const SalariesView = ({ onOpenGovernment }) => {
  const [index, setIndex] = useState(null)
  const [employersIndex, setEmployersIndex] = useState(null)
  const [titlesIndex, setTitlesIndex] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [place, setPlace] = useState(readPlace)
  // The pages opened on the way here, newest last, each with the name its back button gives it.
  const [trail, setTrail] = useState([])
  const heading = useRef(null)
  const [shards, setShards] = useState({})
  const [reading, setReading] = useState(null)
  const [shown, setShown] = useState(24)
  const [employersShown, setEmployersShown] = useState(6)
  const [titlesShown, setTitlesShown] = useState(9)
  const query = place.q
  const sector = place.sector
  const setSector = (value) => setPlace((current) => ({ ...current, sector: value }))

  useEffect(() => {
    loadJson('salaries/people/index.json').then(setIndex, () => setFailed(true))
    loadJson('salaries/employers/index.json').then(setEmployersIndex, () => setFailed(true))
  }, [loadVersion])

  // The year filter is kept as a label, so a shared link survives older years being added.
  const filterYear = salaryYearIndex(place.year, index?.years ?? [])
  const setFilterYear = (value) => setPlace((current) => ({ ...current, year: value === 'all' ? 'all' : index.years[Number(value)] }))

  // The ways what was typed can be read as a name, and the index slices they need.
  const readings = useMemo(() => nameReadings(query), [query])
  const needed = useMemo(() => [...new Set([...readings.map(shardOf), ...(place.person ? [shardOfKey(place.person)] : [])])], [readings, place.person])

  useEffect(() => {
    if (!index) return undefined
    let live = true
    for (const shard of needed) {
      if (shards[shard]) continue
      if (!index.shards[shard]) { setShards((current) => ({ ...current, [shard]: [] })); continue }
      // A slice that fails leaves the employer and position results standing, with its own retry.
      loadJson(`salaries/people/${shard}.json.gzip`).then((list) => live && setShards((current) => ({ ...current, [shard]: list })), () => live && setShards((current) => ({ ...current, [shard]: 'failed' })))
    }
    return () => { live = false }
  }, [needed, index, loadVersion]) // eslint-disable-line react-hooks/exhaustive-deps

  // Position titles are searched once three letters are typed; their index is loaded then.
  const titleQuery = query.trim().replace(/[^A-Za-z0-9 ]/g, '').length >= 3 ? query.trim() : ''
  useEffect(() => {
    if (!titleQuery && !place.title) return
    loadJson('salaries/positions/index.json.gzip').then(setTitlesIndex, () => {})
  }, [titleQuery, place.title])

  useEffect(() => { writePlace(place) }, [place])

  // Each reading's names, in the order they answer it; then the reading shown — the first that finds
  // anyone in full, or failing that by initials alone, unless another has been chosen.
  const found = useMemo(() => {
    if (!index) return []
    return readings.map((each) => {
      const list = shards[shardOf(each)]
      if (!list) return { reading: each, loading: true, groups: [] }
      if (list === 'failed') return { reading: each, loading: false, failed: true, groups: [], full: 0 }
      const groups = new Map()
      for (const row of list) {
        const tier = nameQueryTier(row[0], each.typed, index.sources?.[row[6]]?.nameDisclosure)
        if (tier === null) continue
        if (filterYear !== 'all' && String(row[5]) !== filterYear) continue
        if (sector !== 'all' && index.employers[row[4]][1] !== sector) continue
        const key = personKey(row[0])
        if (!groups.has(key)) groups.set(key, { tier, rows: [] })
        const group = groups.get(key)
        group.tier = Math.min(group.tier, tier)
        group.rows.push(row)
      }
      const described = [...groups].map(([key, group]) => ({ ...describeNameGroup(key, group.rows), tier: group.tier }))
        .sort((a, b) => a.tier - b.tier || b.years.length - a.years.length || b.latest[2] - a.latest[2])
      return { reading: each, loading: false, groups: described, full: described.filter((group) => group.tier < 2).length }
    })
  }, [readings, shards, filterYear, sector, index])
  const nameSearchFailed = found.some((each) => each.failed)
  const retryNames = () => { setShards((current) => Object.fromEntries(Object.entries(current).filter(([, list]) => list !== 'failed'))); setLoadVersion((value) => value + 1) }
  const settled = found.findIndex((each) => each.loading)
  const automatic = (() => {
    const done = settled < 0 ? found : found.slice(0, settled)
    const full = done.findIndex((each) => each.full > 0)
    if (full >= 0) return full
    if (settled >= 0) return null
    const any = found.findIndex((each) => each.groups.length > 0)
    return any >= 0 ? any : 0
  })()
  const shownReading = reading !== null && found[reading] ? reading : automatic
  const result = shownReading !== null ? found[shownReading] : null
  const people = result?.groups ?? []
  const fullPeople = people.filter((each) => each.tier < 2)
  const initialsOnly = people.filter((each) => each.tier === 2)
  const otherReadings = found.map((each, at) => ({ ...each, at })).filter((each) => each.at !== shownReading && each.groups.length > 0)

  // Employers whose name, or a name they filed under, has every word typed.
  const employerMatches = useMemo(() => {
    const words = wordsOf(query)
    if (!words.length || !employersIndex) return []
    return employersIndex.employers.filter((entry) => {
      if (sector !== 'all' && entry.sector !== sector) return false
      if (filterYear !== 'all' && !entry.counts[Number(filterYear)]) return false
      const text = entry.names.join(' ').toLowerCase()
      return words.every((word) => text.includes(word))
    }).sort((a, b) => Math.max(...b.counts) - Math.max(...a.counts))
  }, [query, employersIndex, sector, filterYear])

  // Titles answering what was typed: the same title first, then every title beginning with it or
  // holding its words, the most widely used first — so "nurse" finds Nurse, then the nursing titles
  // most employers use, ahead of rare ones that merely start with the word.
  const titleMatches = useMemo(() => {
    if (!titleQuery || !titlesIndex) return []
    const match = titleMatcher(titleQuery)
    return keyedTitles(titlesIndex).map((title) => ({ title, tier: match(title.key) })).filter(({ tier }) => tier !== null)
      .sort((a, b) => (a.tier > 0) - (b.tier > 0) || b.title.employers - a.title.employers || b.title.rows - a.title.rows)
      .map(({ title }) => title)
  }, [titleQuery, titlesIndex])

  if (failed) return <p className="gallery__intro">The requested salary records could not be loaded. <button type="button" onClick={() => { setFailed(false); setLoadVersion((value) => value + 1) }}>Retry</button></p>
  if (!index || !employersIndex) return <p className="gallery__intro" role="status">Loading the salary index…</p>

  const years = index.years
  const yearAt = place.employerYear ? years.indexOf(place.employerYear) : -1
  const pageYear = yearAt >= 0 ? yearAt : null
  const rootLabel = query.trim() ? `All “${query.trim()}” results` : 'Salaries'

  // Going somewhere remembers where from, under the name of the page being left.
  const go = (next) => {
    setTrail((current) => [...current, { place, label: place.person || place.employer || place.title ? heading.current : rootLabel }])
    setPlace({ ...place, person: null, employer: null, role: null, title: null, show: null, ...next })
    toTop()
  }
  const goBack = () => {
    const previous = trail.at(-1)
    setTrail((current) => current.slice(0, -1))
    setPlace(previous ? previous.place : { ...place, person: null, employer: null, role: null, title: null, show: null })
    toTop()
  }
  const backLabel = trail.at(-1)?.label ?? rootLabel
  const back = <button type="button" className="salaries__back" onClick={goBack}>← {backLabel}</button>
  const remember = (label) => { heading.current = label }
  const setYear = (at) => setPlace((current) => ({ ...current, employerYear: years[at] }))
  const yearFromFilter = filterYear !== 'all' ? years[Number(filterYear)] : place.employerYear

  const openEmployer = (slug) => go({ employer: slug, employerYear: yearFromFilter })
  const openPerson = (name) => go({ q: name, person: personKey(name) })
  const openPersonKey = (key) => go({ person: key })
  const openTitle = (key) => go({ title: key, employerYear: yearFromFilter })
  const openRole = (slug, key, at) => go({ employer: slug, role: key, employerYear: at !== undefined && at !== null && at >= 0 ? years[at] : place.employerYear })
  const search = (text) => {
    setPlace((current) => ({ ...current, q: text, person: null }))
    setReading(null); setShown(24); setEmployersShown(6); setTitlesShown(9)
  }

  if (place.employer) {
    // An employer by its slug, an old slug, or the government body it is (the panel links by body).
    const canonical = employersIndex.aliases?.[place.employer] ?? place.employer
    const entry = employersIndex.employers.find((each) => each.slug === canonical) ?? employersIndex.employers.find((each) => each.body === canonical)
    if (entry) {
      return (
        <EmployerPage
          key={`${entry.slug}|${place.role ?? ''}`}
          entry={entry}
          years={employersIndex.years}
          sources={employersIndex.sources ?? index.sources}
          year={pageYear}
          show={place.show}
          role={place.role}
          back={back}
          onYear={setYear}
          onShow={(show) => setPlace((current) => ({ ...current, show }))}
          onRole={(key) => openRole(entry.slug, key, pageYear)}
          onTitle={openTitle}
          onPerson={openPerson}
          onOpenGovernment={onOpenGovernment}
          remember={remember}
        />
      )
    }
  }

  if (place.title) {
    return (
      <TitlePage
        key={place.title}
        titleKey={place.title}
        employers={employersIndex.employers}
        years={years}
        sector={sector}
        year={pageYear}
        back={back}
        onYear={setYear}
        onSector={setSector}
        onEmployerRole={openRole}
        onTitle={openTitle}
        remember={remember}
      />
    )
  }

  // Filters narrow the search results, not the history of a name opened from one of those results.
  const personRows = place.person ? shards[shardOfKey(place.person)] : null
  const chosen = personRows ? (() => {
    const list = personRows.filter((row) => personKey(row[0]) === place.person)
    return list.length ? describeNameGroup(place.person, list) : null
  })() : null
  if (place.person && !personRows) return <p className="gallery__intro" role="status">Loading the name…</p>
  if (chosen) {
    return (
      <div className="salaries">
        <PersonPage chosen={chosen} all={personRows} index={index} back={back} onEmployer={openEmployer} onRole={openRole} onOpenGovernment={onOpenGovernment} remember={remember} />
      </div>
    )
  }

  // Every record, named or not: the people index holds only the named ones.
  const total = employersIndex.employers.reduce((sum, entry) => sum + entry.counts.reduce((a, b) => a + b, 0), 0)
  const sectors = [...new Set(employersIndex.employers.map((entry) => entry.sector))].filter(Boolean).sort()
  const typed = query.trim()
  const peopleSettled = result && !result.loading
  const filtered = filterYear !== 'all' || sector !== 'all'

  return (
    <div className="salaries">
      <section className="salaries__intro">
        <h2 className="salaries__heading">Public-sector salaries</h2>
        <p>
          {total.toLocaleString('en-CA')} disclosed pay records from {employersIndex.employers.length} British Columbia public
          employers, {years[0]} to {years.at(-1)}. Search for a person, an employer or a position.
        </p>
      </section>

      <div className="salaries__search">
        <input
          type="search"
          value={query}
          placeholder="A name, an employer or a position, like “Smith, J”, “Transit” or “Nurse”"
          aria-label="Search a name, an employer or a position"
          aria-describedby="salaries-name-help"
          onChange={(event) => search(event.target.value)}
        />
        <select value={filterYear} onChange={(event) => setFilterYear(event.target.value)} aria-label="Year">
          <option value="all">Every year</option>
          {years.map((label, at) => <option key={label} value={String(at)}>{label}</option>)}
        </select>
      </div>

      <p id="salaries-name-help" className="salaries__hint salaries__hint--small">
        A name is read surname first, then the other way round. A comma fixes where given names begin, as in “Van der Meer, J”.
      </p>
      {filtered && (
        <p className="salaries__hint">
          {filterYear !== 'all' ? years[Number(filterYear)] : 'Every year'} · {sector === 'all' ? 'All sectors' : sector}{' '}
          <button type="button" className="salaries__link" onClick={() => setPlace((current) => ({ ...current, year: 'all', sector: 'all' }))}>Clear filters</button>
        </p>
      )}

      <div className="salaries__chips" role="group" aria-label="Sector">
        <button type="button" aria-pressed={sector === 'all'} onClick={() => setSector('all')}>All sectors</button>
        {sectors.map((name) => (
          <button key={name} type="button" aria-pressed={sector === name} onClick={() => setSector(sector === name ? 'all' : name)}>
            {name} <span>{employersIndex.employers.filter((entry) => entry.sector === name).length}</span>
          </button>
        ))}
      </div>

      {typed && (
        <>
          {employerMatches.length > 0 && (
            <section aria-labelledby="salaries-employer-results">
              <div className="salaries__head">
                <h2 id="salaries-employer-results" className="salaries__title">Employers</h2>
                <p className="salaries__meta">{count(employerMatches.length, 'employer', 'employers')}</p>
              </div>
              <div className="salaries__grid">
                {employerMatches.slice(0, employersShown).map((entry) => <EmployerCard key={entry.slug} entry={entry} years={employersIndex.years} year={filterYear} onOpen={openEmployer} />)}
              </div>
              {employerMatches.length > employersShown && (
                <button type="button" className="salaries__more" onClick={() => setEmployersShown(Infinity)}>Show all {employerMatches.length}</button>
              )}
            </section>
          )}

          {readings.length > 0 && !(peopleSettled && !nameSearchFailed && !people.length && (employerMatches.length > 0 || titleMatches.length > 0)) && (
            <section aria-labelledby="salaries-results">
              <div className="salaries__head">
                <h2 id="salaries-results" className="salaries__title">People</h2>
                <p className="salaries__meta" role="status">{nameSearchFailed && !people.length ? 'Search unavailable' : peopleSettled ? count(fullPeople.length, 'name', 'names') : 'Loading…'}</p>
              </div>
              {nameSearchFailed && (
                <p className="salaries__hint" role="alert">Some name records could not be loaded. Employer and position results are still available. <button type="button" onClick={retryNames}>Retry name search</button></p>
              )}
              {peopleSettled && readings.length > 1 && (
                <p className="salaries__hint salaries__hint--small">
                  {shownReading !== 0 && reading === null
                    ? <>Nobody is disclosed in full as “{asDisclosed(readings[0])}”, so this is read as “{asDisclosed(result.reading)}”.</>
                    : <>Read as “{asDisclosed(result.reading)}”, surname first.</>}
                  {otherReadings.map((each) => (
                    <span key={each.at}>
                      {' '}<button type="button" className="salaries__link" onClick={() => { setReading(each.at); setShown(24) }}>
                        “{asDisclosed(each.reading)}” finds {each.full ? count(each.full, 'name', 'names') : `${count(each.groups.length, 'name', 'names')} by initials`}
                      </button>.
                    </span>
                  ))}
                </p>
              )}
              {peopleSettled && !nameSearchFailed && people.length === 0 && !(titleQuery && !titlesIndex) && (
                <p className="salaries__hint">No disclosed name matches “{typed}”{filtered ? ' with these filters' : ''}. Try the surname alone.</p>
              )}
              {peopleSettled && fullPeople.length === 0 && initialsOnly.length > 0 && (
                <p className="salaries__hint">No disclosed name matches “{typed}” in full.</p>
              )}
              <div className="salaries__grid">
                {fullPeople.slice(0, shown).map((each) => <PersonCard key={each.key} each={each} index={index} onOpen={openPersonKey} />)}
              </div>
              <More shown={shown} total={fullPeople.length} step={48} onMore={() => setShown((value) => value + 48)} />
              {initialsOnly.length > 0 && (
                <>
                  <h3 className="salaries__title salaries__title--spaced">Initials only</h3>
                  <p className="salaries__hint salaries__hint--small">Disclosed with initials that agree with “{result.reading.given}”. Each may be the person you mean, or someone else.</p>
                  <div className="salaries__grid salaries__grid--spaced">
                    {initialsOnly.slice(0, 12).map((each) => <PersonCard key={each.key} each={each} index={index} onOpen={openPersonKey} />)}
                  </div>
                  {initialsOnly.length > 12 && <p className="salaries__hint salaries__hint--small">And {initialsOnly.length - 12} more; type an initial after the surname to narrow them.</p>}
                </>
              )}
            </section>
          )}

          {titleMatches.length > 0 && (
            <section aria-labelledby="salaries-title-results">
              <div className="salaries__head">
                <h2 id="salaries-title-results" className="salaries__title">Positions</h2>
                <p className="salaries__meta">{count(titleMatches.length, 'title', 'titles')} across employers</p>
              </div>
              <div className="salaries__grid">
                {titleMatches.slice(0, titlesShown).map((title) => <TitleCard key={title.key} title={title} years={years} onOpen={openTitle} />)}
              </div>
              <More shown={titlesShown} total={titleMatches.length} step={24} onMore={() => setTitlesShown((value) => value + 24)} />
            </section>
          )}

          {!readings.length && !employerMatches.length && !titleMatches.length && <p className="salaries__hint">Type at least two letters of a surname, or part of an employer’s name or a position.</p>}
        </>
      )}

      {!typed && <EmployerList employers={employersIndex.employers} years={employersIndex.years} sector={sector} year={filterYear} onOpen={openEmployer} onSector={setSector} />}

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
  const visible = filterEmployers(employers, sector, year)
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
      {visible.length === 0 && <p className="salaries__hint">No employers have imported records with these filters. Choose another year or clear the filters above.</p>}
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
              <button type="button" className="salaries__more" onClick={() => { onSector(name); toTop() }}>All {sorted.length} {name.toLowerCase()} →</button>
            )}
          </div>
        )
      })}
    </section>
  )
}
