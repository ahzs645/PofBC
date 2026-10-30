// An employer's records, set out three ways: its positions for a year, each with how many records it
// has and what they paid on average, and each opening onto its own page; its people for a year,
// highest paid first; or everyone under a name across every year, as a table.
//
// A position is a title however the employer spelled it (positions.js): "Teacher", "TEACHERS" and
// "Teacher · Elementary" are one, and its page lists the spellings it gathers.

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { displayName, personKey } from './people.js'
import { meanMoney, titleKey, titleLabel } from './positions.js'
import { coverageAt, expenseLabel } from './coverage.js'
import { DisclosureSummary } from './DisclosureEvidence.jsx'
import { formatMoney as money, medianMoney as median } from './money.js'
import { PayChart, YearPicker, shortYear } from './parts.jsx'
import { count, loadJson, More, RecordRow, RoleIcon, seenYears, wordsOf } from './common.jsx'

const SHOWS = ['positions', 'people', 'everyone']

/** Rows grouped into titles: each with its commonest spelling, its spellings and what it paid. */
const groupTitles = (rows) => {
  const groups = new Map()
  for (const row of rows) {
    const key = row[1] ? titleKey(row[1]) : ''
    if (!groups.has(key)) groups.set(key, { key, spellings: new Map(), rows: [] })
    const group = groups.get(key)
    group.rows.push(row)
    if (row[1]) group.spellings.set(row[1], (group.spellings.get(row[1]) ?? 0) + 1)
  }
  return [...groups.values()].map((group) => {
    const pay = group.rows.map((row) => row[2])
    const spellings = [...group.spellings].sort((a, b) => b[1] - a[1])
    return { ...group, label: group.key ? titleLabel(spellings[0]?.[0]) : null, spellings, mean: meanMoney(pay), median: median(pay), low: Math.min(...pay), high: Math.max(...pay) }
  })
}

const POSITION_ORDER = {
  records: (a, b) => b.rows.length - a.rows.length || b.mean - a.mean,
  average: (a, b) => b.mean - a.mean || b.rows.length - a.rows.length,
  name: (a, b) => a.label.localeCompare(b.label)
}

/**
 * @param {object} props
 * @param {string|null} props.show   'positions', 'people' or 'everyone'; null for the default.
 * @param {string|null} props.role   A title key: that position's page.
 */
export const EmployerPage = ({ entry, years, sources, year: wantedYear, show, role, back, onYear, onShow, onRole, onTitle, onPerson, onOpenGovernment, remember }) => {
  const seen = seenYears(entry)
  const [rows, setRows] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [filter, setFilter] = useState('')
  const [order, setOrder] = useState('records')
  const [tableOrder, setTableOrder] = useState('pay')
  const [shown, setShown] = useState(40)

  useEffect(() => {
    let live = true
    setFailed(false)
    setRows(null)
    loadJson(`salaries/employers/${entry.slug}.json.gzip`).then((list) => live && setRows(list), () => live && setFailed(true))
    return () => { live = false }
  }, [entry.slug, loadVersion])

  const year = wantedYear ?? seen.at(-1) ?? 0
  const name = entry.names.at(-1)
  remember?.(name)
  const coverage = coverageAt({ ...entry, years }, year)
  const people = useMemo(() => (rows ? rows.filter((row) => row[4] === year) : []), [rows, year])
  // Whether the year's disclosure names positions: some employers give them one year and not the next.
  const withPositions = people.length > 0 && people.filter((row) => row[1]).length / people.length >= 0.5
  const view = SHOWS.includes(show) ? (show === 'positions' && !withPositions ? 'people' : show) : (withPositions ? 'positions' : 'people')
  // A source shown once for the year is not repeated on every row.
  const oneSource = new Set(people.map((row) => row[5])).size <= 1
  const positions = useMemo(() => groupTitles(people), [people])

  const words = wordsOf(filter)
  const has = (text) => words.every((word) => String(text ?? '').toLowerCase().includes(word))
  const named = positions.filter((position) => position.label)
  const matchingPositions = named.filter((position) => has(position.label)).sort(POSITION_ORDER[order])
  const unpositioned = positions.find((position) => !position.label)
  const ranked = useMemo(() => [...people].sort((a, b) => b[2] - a[2]), [people])
  const matchingPeople = ranked.filter((row) => has(`${row[0] ?? ''} ${row[1] ?? ''}`))
  const pay = people.map((row) => row[2])

  // Everyone under a name across the years: one row a name, one column a year with records.
  const everyone = useMemo(() => {
    if (view !== 'everyone' || !rows) return []
    const groups = new Map()
    for (const row of rows) {
      if (!row[0]) continue
      const key = personKey(row[0])
      if (!groups.has(key)) groups.set(key, { key, name: row[0], latest: row, pay: new Map(), records: new Map() })
      const group = groups.get(key)
      if (row[4] > group.latest[4]) { group.latest = row; group.name = row[0] }
      group.pay.set(row[4], Math.max(group.pay.get(row[4]) ?? 0, row[2]))
      group.records.set(row[4], (group.records.get(row[4]) ?? 0) + 1)
    }
    return [...groups.values()]
  }, [rows, view])
  const tableSort = {
    pay: (a, b) => (b.pay.get(year) ?? -1) - (a.pay.get(year) ?? -1) || b.latest[2] - a.latest[2],
    years: (a, b) => b.pay.size - a.pay.size || b.latest[2] - a.latest[2],
    name: (a, b) => a.key.localeCompare(b.key)
  }[tableOrder]
  const matchingEveryone = useMemo(
    () => everyone.filter((group) => has(`${group.name} ${group.latest[1] ?? ''}`)).sort(tableSort),
    [everyone, filter, tableOrder, year]
  )
  const unnamed = rows ? rows.filter((row) => !row[0]).length : 0

  const pick = (at) => { onYear(at); setShown(40) }
  const switchTo = (next) => { onShow(next); setShown(40) }

  if (role) {
    return (
      <RolePage
        entry={entry} years={years} sources={sources} rows={rows} failed={failed} roleKey={role} wantedYear={wantedYear} back={back}
        onRetry={() => setLoadVersion((value) => value + 1)} onYear={pick} onTitle={onTitle} onPerson={onPerson} remember={remember}
      />
    )
  }

  const list = { positions: matchingPositions, people: matchingPeople, everyone: matchingEveryone }[view]

  return (
    <div className="salaries">
      <section className="salaries__person" aria-labelledby="salaries-employer">
        {back}
        <h2 id="salaries-employer" className="salaries__heading">{name}</h2>
        <p className="salaries__note">
          {entry.sector}
          {entry.names.length > 1 ? ` · also filed as ${entry.names.slice(0, -1).map((each) => `“${each}”`).join(', ')}` : ''}
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
          <dl className="salaries__tiles">
            <div><dt>Records</dt><dd>{people.length.toLocaleString('en-CA')}</dd></div>
            <div><dt>Average</dt><dd>{pay.length ? money(meanMoney(pay)) : '—'}</dd></div>
            <div><dt>Median</dt><dd>{pay.length ? money(median(pay)) : '—'}</dd></div>
            <div><dt>{named.length ? 'Positions' : 'Highest'}</dt><dd>{named.length ? named.length.toLocaleString('en-CA') : money(Math.max(...pay))}</dd></div>
          </dl>
        )}
      </section>

      {failed && <p className="salaries__hint" role="alert">The employer’s records could not be loaded. <button type="button" onClick={() => setLoadVersion((value) => value + 1)}>Retry</button></p>}
      {!rows && !failed && <p className="salaries__hint" role="status">Loading its records…</p>}
      {rows && rows.length > 0 && (
        <section aria-labelledby="salaries-records" className="salaries__records">
          <Segmented
            ariaLabel="Show records"
            value={view}
            onChange={switchTo}
            options={[
              { value: 'positions', label: 'Positions', disabled: !withPositions, title: withPositions ? 'Each position this year, with its average pay' : 'This year’s records do not name positions' },
              { value: 'people', label: 'People', title: 'This year’s records, highest paid first' },
              { value: 'everyone', label: 'All years', title: 'Everyone under a name, with their pay in every year' }
            ]}
          />
          <div className="salaries__search salaries__search--one">
            <input type="search" value={filter} placeholder={view === 'positions' ? 'Find a position' : 'Find a name or a position'} aria-label="Find a name or a position" onChange={(event) => { setFilter(event.target.value); setShown(40) }} />
          </div>
          <div className="salaries__head">
            <h2 id="salaries-records" className="salaries__title">
              {{ positions: `Positions in ${years[year]}`, people: `Highest paid in ${years[year]}`, everyone: 'Everyone, every year' }[view]}
            </h2>
            <p className="salaries__meta">
              {view === 'positions' && count(matchingPositions.length, 'position', 'positions')}
              {view === 'people' && count(matchingPeople.length, 'record', 'records')}
              {view === 'everyone' && count(matchingEveryone.length, 'name', 'names')}
            </p>
          </div>
          {view === 'positions' && (
            <Segmented compact ariaLabel="Order positions" value={order} onChange={setOrder} options={[{ value: 'records', label: 'Most records' }, { value: 'average', label: 'Highest average' }, { value: 'name', label: 'A–Z' }]} />
          )}
          {view === 'everyone' && (
            <Segmented compact ariaLabel="Order names" value={tableOrder} onChange={setTableOrder} options={[{ value: 'pay', label: `${years[year]} pay` }, { value: 'years', label: 'Most years' }, { value: 'name', label: 'A–Z' }]} />
          )}
          {view === 'people' && !withPositions && people.length > 0 && <p className="salaries__hint salaries__hint--small">This year’s records do not name positions.</p>}
          {view !== 'everyone' && !people.length && <p className="salaries__hint">No records in {years[year]}. Choose a year with records above, or see all years.</p>}
          {words.length > 0 && list.length === 0 && <p className="salaries__hint">Nothing {view === 'everyone' ? '' : `in ${years[year]} `}matches “{filter.trim()}”.</p>}

          {view === 'positions' && (
            <div className="salaries__grid">
              {matchingPositions.slice(0, shown).map((position) => (
                <button key={position.key} type="button" className="salaries__card" onClick={() => onRole(position.key)}>
                  <span className="salaries__lead"><RoleIcon /></span>
                  <span className="salaries__text">
                    <span className="salaries__name">{position.label}</span>
                    <span className="salaries__line">
                      {count(position.rows.length, 'record', 'records')}
                      {position.rows.length > 1 ? ` · ${money(position.low)}–${money(position.high)}` : ''}
                    </span>
                    {position.rows.length > 1 && <span className="salaries__line">Median {money(position.median)}</span>}
                  </span>
                  <span className="salaries__aside">{money(position.mean)}<span className="salaries__line">{position.rows.length > 1 ? 'average' : 'paid'}</span></span>
                </button>
              ))}
            </div>
          )}
          {view === 'positions' && unpositioned && !words.length && (
            <p className="salaries__hint salaries__hint--small">
              {count(unpositioned.rows.length, 'record does', 'records do')} not name a position (average {money(unpositioned.mean)}); they are under People.
            </p>
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

          {view === 'everyone' && (
            <>
              <EveryoneTable groups={matchingEveryone.slice(0, shown)} years={years} columns={seen} chosen={year} sources={sources} onPerson={onPerson} onYear={(at) => { pick(at); setTableOrder('pay') }} />
              <p className="salaries__hint salaries__hint--small">
                The highest record is shown where a name has more than one in a year (marked +). Names are grouped as disclosed, so a row may
                not be one person{unnamed ? `; ${count(unnamed, 'record without a name is', 'records without a name are')} left out` : ''}.
              </p>
            </>
          )}

          <More shown={shown} total={list.length} step={view === 'everyone' ? 100 : 80} onMore={() => setShown((value) => value + (view === 'everyone' ? 100 : 80))} />
        </section>
      )}
    </div>
  )
}

/**
 * Names down the side, years across, pay in each. The name column stays put while the years scroll
 * sideways; on a phone the table scrolls inside its own box rather than widening the page, starting
 * scrolled to the year chosen.
 */
const EveryoneTable = ({ groups, years, columns, chosen, sources, onPerson, onYear }) => {
  const box = useRef(null)
  useLayoutEffect(() => {
    const element = box.current
    const column = element?.querySelector('thead th[data-chosen]')
    if (!column) return
    const left = column.offsetLeft - element.querySelector('thead th').offsetWidth
    const right = column.offsetLeft + column.offsetWidth - element.clientWidth
    if (element.scrollLeft > left) element.scrollLeft = left
    else if (element.scrollLeft < right) element.scrollLeft = right
  }, [chosen])
  return (
    <div ref={box} className="salaries-table" role="region" aria-label="Pay by name and year" tabIndex={0}>
      <table>
        <thead>
          <tr>
            <th scope="col">Name</th>
            {columns.map((at) => (
              <th key={at} scope="col" data-chosen={at === chosen || undefined}>
                <button type="button" className="salaries__link" onClick={() => onYear(at)} title={`Sort by ${years[at]} pay`} aria-label={`${years[at]}: sort by its pay`}>{shortYear(years[at])}</button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {groups.map((group) => (
            <tr key={group.key}>
              <th scope="row">
                <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(group.name)}>{displayName(group.name, sources?.[group.latest[5]]?.nameDisclosure)}</button>
                {group.latest[1] && <span className="salaries__line">{group.latest[1]}</span>}
              </th>
              {columns.map((at) => {
                const value = group.pay.get(at)
                const extra = (group.records.get(at) ?? 0) - 1
                return (
                  <td key={at} data-chosen={at === chosen || undefined} title={extra > 0 ? `${extra + 1} records in ${years[at]}; the highest is shown` : undefined}>
                    {value === undefined ? <span className="salaries__line" aria-label="No record">·</span> : money(value)}
                    {extra > 0 && <sup>+{extra}</sup>}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/**
 * One position at one employer: its average by year as a chart and a list, and the people in the
 * year chosen. The same title at other employers is a link away.
 */
const RolePage = ({ entry, years, sources, rows, failed, roleKey, wantedYear, back, onRetry, onYear, onTitle, onPerson, remember }) => {
  const matching = useMemo(() => (rows ? rows.filter((row) => row[1] && titleKey(row[1]) === roleKey) : []), [rows, roleKey])
  const [shown, setShown] = useState(50)
  const byYear = useMemo(() => years.map((_, at) => matching.filter((row) => row[4] === at)), [matching, years])
  const [group] = useMemo(() => groupTitles(matching), [matching])
  const label = group?.label ?? roleKey
  remember?.(`${label} · ${entry.names.at(-1)}`)
  const counts = byYear.map((list) => list.length)
  const year = wantedYear ?? counts.findLastIndex((value) => value > 0)
  const stats = byYear.map((list) => (list.length ? { mean: meanMoney(list.map((row) => row[2])), median: median(list.map((row) => row[2])), low: Math.min(...list.map((row) => row[2])), high: Math.max(...list.map((row) => row[2])) } : null))
  const points = stats.map((stat, at) => (stat ? { year: at, pay: stat.mean } : null)).filter(Boolean)
  const chosen = byYear[year] ?? []
  const ranked = [...chosen].sort((a, b) => b[2] - a[2])
  const oneSource = new Set(chosen.map((row) => row[5])).size <= 1

  return (
    <div className="salaries">
      <section className="salaries__person" aria-labelledby="salaries-role">
        {back}
        <h2 id="salaries-role" className="salaries__heading">{label}</h2>
        <p className="salaries__note">
          {entry.names.at(-1)}
          {group && ` · ${count(points.length, 'year', 'years')} with records`}
          {' · '}<button type="button" className="salaries__link" onClick={() => onTitle(roleKey)}>This title at every employer</button>
        </p>
        {group?.spellings.length > 1 && (
          <p className="salaries__hint salaries__hint--small">Written as {group.spellings.slice(0, 6).map(([text]) => `“${text}”`).join(', ')}{group.spellings.length > 6 ? ` and ${group.spellings.length - 6} more ways` : ''}.</p>
        )}
        {failed && <p className="salaries__hint" role="alert">The employer’s records could not be loaded. <button type="button" onClick={onRetry}>Retry</button></p>}
        {!rows && !failed && <p className="salaries__hint" role="status">Loading its records…</p>}
        {rows && !group && <p className="salaries__hint">No records under this position at {entry.names.at(-1)}.</p>}
        {group && (
          <>
            <YearPicker years={years} counts={counts} value={year} onChange={onYear} label="Year of this position’s records" />
            <h3 className="salaries__year-title">{years[year]}</h3>
            {stats[year]
              ? (
                <dl className="salaries__tiles">
                  <div><dt>Records</dt><dd>{chosen.length.toLocaleString('en-CA')}</dd></div>
                  <div><dt>Average</dt><dd>{money(stats[year].mean)}</dd></div>
                  <div><dt>Median</dt><dd>{money(stats[year].median)}</dd></div>
                  <div><dt>Range</dt><dd className="salaries__range">{chosen.length > 1 ? `${money(stats[year].low)}–${money(stats[year].high)}` : money(stats[year].low)}</dd></div>
                </dl>
              )
              : <p className="salaries__hint">No records under this position in {years[year]}; the bars above show the years with them.</p>}
            {points.length > 1 && <PayChart years={years} points={points} label="Average pay by year" />}
          </>
        )}
      </section>

      {group && (
        <section aria-labelledby="salaries-role-years" className="salaries__person">
          <h3 id="salaries-role-years" className="salaries__title">Year by year</h3>
          <ol className="salaries-years">
            {stats.map((stat, at) => ({ stat, at })).filter(({ stat }) => stat).reverse().map(({ stat, at }) => (
              <li key={at} className="salaries-years__year">
                <span className="salaries-years__label">
                  <button type="button" className="salaries__link" aria-pressed={at === year} onClick={() => onYear(at)}>{years[at]}</button>
                </span>
                <span className="salaries-record">
                  <span className="salaries-record__what">
                    <span className="salaries__name">{count(counts[at], 'record', 'records')}</span>
                    <span className="salaries__line">{counts[at] > 1 ? `Median ${money(stat.median)} · ${money(stat.low)}–${money(stat.high)}` : 'One record'}</span>
                  </span>
                  <span className="salaries-row__pay">{money(stat.mean)}<span className="salaries__line">{counts[at] > 1 ? 'average' : 'paid'}</span></span>
                </span>
              </li>
            ))}
          </ol>
        </section>
      )}

      {chosen.length > 0 && (
        <section aria-labelledby="salaries-role-people">
          <div className="salaries__head">
            <h3 id="salaries-role-people" className="salaries__title">People in {years[year]}</h3>
            <p className="salaries__meta">{count(chosen.length, 'record', 'records')}</p>
          </div>
          <ol className="salaries-rows">
            {ranked.slice(0, shown).map((row, at) => (
              <RecordRow
                key={`${row[0]}-${row[2]}-${at}`}
                rank={at + 1}
                name={row[0]}
                position={group.spellings.length > 1 ? row[1] : null}
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
          <More shown={shown} total={ranked.length} step={100} onMore={() => setShown((value) => value + 100)} />
        </section>
      )}
    </div>
  )
}
