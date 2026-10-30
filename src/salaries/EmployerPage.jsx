// An employer's records, set out three ways: its positions for a year, each with how many records it
// has and what they paid on average, and each opening onto its own page; its people for a year,
// highest paid first; or everyone under a name across every year, as a table.
//
// A position is a title however the employer spelled it (positions.js): "Teacher", "TEACHERS" and
// "Teacher · Elementary" are one, and its page lists the spellings it gathers.

import { useEffect, useMemo, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { displayName, personKey } from './people.js'
import { meanMoney, titleKey, titleLabel } from './positions.js'
import { categoryCoverage, coverageAt, expenseLabel, reportingYearLabel, scopeLabel } from './coverage.js'
import { DisclosureSummary } from './DisclosureEvidence.jsx'
import { formatMoney as money, medianMoney as median } from './money.js'
import { PayChart, YearPicker, shortYear } from './parts.jsx'
import { count, LAYOUTS, loadJson, Paged, RecordRow, RoleIcon, seenYears, wordsOf } from './common.jsx'
import { DataTable } from './DataTable.jsx'
import { SourceLink } from './DisclosureEvidence.jsx'
import { filterPositionGroups, matchesRecordQuery } from './viewState.js'

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
export const EmployerPage = ({ entry, years, sources, year: wantedYear, show, role, layout = 'cards', back, onYear, onShow, onLayout, onRole, onTitle, onPerson, onOpenGovernment, remember }) => {
  const seen = seenYears(entry)
  const [rows, setRows] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [filter, setFilter] = useState('')
  const [order, setOrder] = useState('records')
  const [category, setCategory] = useState(null)

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
  // A period can combine disclosure categories (Prince George's employees and its mayor and council):
  // employees are shown by default, and each category can be chosen on its own.
  const wholeCoverage = coverageAt({ ...entry, years }, year)
  const periodRows = useMemo(() => (rows ? rows.filter((row) => row[4] === year) : []), [rows, year])
  const categories = [...new Set(periodRows.map((row) => sources?.[row[5]]?.scope ?? 'compiled-unverified'))]
  const defaultCategory = categories.includes('elected-officials') && categories.includes('employee-remuneration') ? 'employee-remuneration' : 'all'
  const chosenCategory = category && (category === 'all' || categories.includes(category)) ? category : defaultCategory
  const people = useMemo(() => periodRows.filter((row) => chosenCategory === 'all' || sources?.[row[5]]?.scope === chosenCategory), [periodRows, chosenCategory, sources])
  const coverage = categoryCoverage(wholeCoverage, chosenCategory, sources, people)
  // Whether the year's disclosure names positions: some employers give them one year and not the next.
  const withPositions = people.length > 0 && people.filter((row) => row[1]).length / people.length >= 0.5
  const view = SHOWS.includes(show) ? (show === 'positions' && !withPositions ? 'people' : show) : (withPositions ? 'positions' : 'people')
  // A source shown once for the year is not repeated on every row.
  const oneSource = new Set(people.map((row) => row[5])).size <= 1
  const positions = useMemo(() => groupTitles(people), [people])

  const words = wordsOf(filter)
  const named = positions.filter((position) => position.label)
  // A search in positions finds a position by its title or by the people in it: "Jane Smith" finds
  // her position, with one of its records matching.
  const matchingPositions = filterPositionGroups(named, filter).sort(POSITION_ORDER[order])
  const unpositioned = positions.find((position) => !position.label)
  const ranked = useMemo(() => [...people].sort((a, b) => b[2] - a[2]), [people])
  const matchingPeople = ranked.filter((row) => matchesRecordQuery(row, filter))
  const positionedRecords = people.filter((row) => row[1]).length
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
  const matchingEveryone = useMemo(() => everyone.filter((group) => matchesRecordQuery([group.name, group.latest[1]], filter)), [everyone, filter])
  const unnamed = rows ? rows.filter((row) => !row[0]).length : 0

  // The same records as tables: each column sorts from its header and filters under it.
  const positionColumns = useMemo(() => [
    { id: 'label', header: 'Position', accessorKey: 'label', cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onRole(row.original.key)}>{getValue()}</button> },
    { id: 'records', header: 'Records', accessorFn: (position) => position.totalRows, meta: { kind: 'number' } },
    { id: 'mean', header: 'Average', accessorKey: 'mean', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'median', header: 'Median', accessorKey: 'median', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'low', header: 'Lowest', accessorKey: 'low', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'high', header: 'Highest', accessorKey: 'high', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) }
  ], [onRole])
  const peopleColumns = useMemo(() => [
    { id: 'name', header: 'Name', accessorFn: (row) => (row[0] ? displayName(row[0], sources?.[row[5]]?.nameDisclosure) : 'Name not given'), cell: ({ row, getValue }) => (row.original[0] ? <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(row.original[0])}>{getValue()}</button> : <span className="salaries__line">{getValue()}</span>) },
    { id: 'position', header: 'Position', accessorFn: (row) => row[1] ?? '' },
    { id: 'pay', header: 'Pay', accessorFn: (row) => row[2], meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'expenses', header: expenseLabel(people[0]?.[5], sources), accessorFn: (row) => row[3], meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'source', header: 'Source', accessorFn: (row) => row[6] ?? '', meta: { filter: false }, cell: ({ row }) => <SourceLink sourceId={row.original[5]} sources={sources} pdfPage={row.original[6]} /> }
  ], [sources, onPerson, people])
  const everyoneColumns = useMemo(() => [
    { id: 'name', header: 'Name', accessorFn: (group) => displayName(group.name, sources?.[group.latest[5]]?.nameDisclosure), cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(row.original.name)}>{getValue()}</button> },
    { id: 'position', header: 'Latest position', accessorFn: (group) => group.latest[1] ?? '' },
    ...seen.map((at) => ({
      id: `y${at}`, header: shortYear(years[at]), accessorFn: (group) => group.pay.get(at), meta: { kind: 'money' }, sortUndefined: 'last',
      cell: ({ row, getValue }) => {
        const extra = (row.original.records.get(at) ?? 0) - 1
        return getValue() == null ? <span className="salaries__line" aria-label="No record">·</span> : <span title={extra > 0 ? `${extra + 1} records in ${years[at]}; the highest is shown` : undefined}>{money(getValue())}{extra > 0 && <sup>+{extra}</sup>}</span>
      }
    }))
  ], [seen.join(','), years, sources, onPerson]) // eslint-disable-line react-hooks/exhaustive-deps

  const pick = (at) => { onYear(at); setCategory(null) }
  const switchTo = (next) => onShow(next)

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
        <YearPicker years={years} counts={entry.counts} coverage={entry.coverage} value={year} onChange={pick} />
        <h3 className="salaries__year-title">{reportingYearLabel(years[year])}</h3>
        {categories.length > 1 && (
          <label className="salaries__note salaries__category">
            Disclosure category{' '}
            <select value={chosenCategory} onChange={(event) => setCategory(event.target.value)}>
              <option value="all">All disclosed categories</option>
              {categories.map((scope) => <option key={scope} value={scope}>{scopeLabel(scope)}</option>)}
            </select>
          </label>
        )}
        <DisclosureSummary coverage={coverage} sources={sources} />
        {!entry.counts[year] && <p className="salaries__hint">{coverage.status === 'aggregate-only' ? 'The verified report publishes aggregate payroll without named employee records.' : coverage.status === 'excluded' ? 'These records are held for review because source checks have not passed.' : coverage.status === 'source-found' ? 'A report has been located, but its employee records have not yet passed extraction and validation.' : 'No records have been imported for this employer in this year.'} That does not mean it had no staff or made no payments.</p>}
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
            <input type="search" value={filter} placeholder={view === 'positions' ? 'Find a position' : 'Find a name or a position'} aria-label="Find a name or a position" onChange={(event) => setFilter(event.target.value)} />
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
          {view !== 'everyone' && (
            <div className="salaries__browse-bar">
              {view === 'positions' && layout === 'cards'
                ? <Segmented compact ariaLabel="Order positions" value={order} onChange={setOrder} options={[{ value: 'records', label: 'Most records' }, { value: 'average', label: 'Highest average' }, { value: 'name', label: 'A–Z' }]} />
                : <span />}
              <Segmented compact ariaLabel="Layout" value={layout} onChange={onLayout} options={LAYOUTS} />
            </div>
          )}
          {view === 'people' && !withPositions && people.length > 0 && (
            <p className="salaries__hint salaries__hint--small">
              {positionedRecords ? `${positionedRecords.toLocaleString('en-CA')} of this year’s ${people.length.toLocaleString('en-CA')} records name positions; they are shown where supplied.` : 'This year’s records do not name positions.'}
            </p>
          )}
          {view !== 'everyone' && !people.length && <p className="salaries__hint">No records in {years[year]}. Choose a year with records above, or see all years.</p>}
          {words.length > 0 && list.length === 0 && <p className="salaries__hint">Nothing {view === 'everyone' ? '' : `in ${years[year]} `}matches “{filter.trim()}”.</p>}

          {view === 'positions' && layout === 'table' && <DataTable data={matchingPositions} columns={positionColumns} sorting={[{ id: 'records', desc: true }]} label={`Positions in ${years[year]}`} />}
          {view === 'positions' && layout === 'cards' && (
            <Paged list={matchingPositions} size={24} reset={`${year}|${filter}|${order}|${chosenCategory}`}>
              {(page) => (
                <div className="salaries__grid">
                  {page.map((position) => (
                    <button key={position.key} type="button" className="salaries__card" onClick={() => onRole(position.key)}>
                      <span className="salaries__lead"><RoleIcon /></span>
                      <span className="salaries__text">
                        <span className="salaries__name">{position.label}</span>
                        <span className="salaries__line">
                          {count(position.rows.length, 'record', 'records')}
                          {position.rows.length < position.totalRows ? ` of ${position.totalRows.toLocaleString('en-CA')} match` : ''}
                          {position.totalRows > 1 ? ` · ${money(position.low)}–${money(position.high)}` : ''}
                        </span>
                        {position.totalRows > 1 && <span className="salaries__line">Median {money(position.median)}</span>}
                      </span>
                      <span className="salaries__aside">{money(position.mean)}<span className="salaries__line">{position.totalRows > 1 ? 'average' : 'paid'}</span></span>
                    </button>
                  ))}
                </div>
              )}
            </Paged>
          )}
          {view === 'positions' && unpositioned && !words.length && (
            <p className="salaries__hint salaries__hint--small">
              {count(unpositioned.rows.length, 'record does', 'records do')} not name a position (average {money(unpositioned.mean)}); they are under People.
            </p>
          )}

          {view === 'people' && layout === 'table' && <DataTable data={matchingPeople} columns={peopleColumns} sorting={[{ id: 'pay', desc: true }]} label={`Records in ${years[year]}`} />}
          {view === 'people' && layout === 'cards' && (
            <Paged list={matchingPeople} size={50} reset={`${year}|${filter}|${chosenCategory}`}>
              {(page) => (
                <ol className="salaries-rows">
                  {page.map((row) => (
                    <RecordRow
                      key={`${row[0]}-${row[2]}-${ranked.indexOf(row)}`}
                      rank={ranked.indexOf(row) + 1}
                      name={row[0]}
                      position={row[1]}
                      pay={row[2]}
                      expenses={row[3]}
                      expenseText={expenseLabel(row[5], sources)}
                      sourceId={oneSource && !row[6] ? null : row[5]}
                      sources={sources}
                      pdfPage={row[6]}
                      nameDisclosure={sources?.[row[5]]?.nameDisclosure}
                      onPerson={onPerson}
                    />
                  ))}
                </ol>
              )}
            </Paged>
          )}

          {view === 'everyone' && (
            <>
              <DataTable key={year} data={matchingEveryone} columns={everyoneColumns} sorting={[{ id: `y${year}`, desc: true }]} label="Pay by name and period" />
              <p className="salaries__hint salaries__hint--small">
                The highest record is shown where a name has more than one in a year (marked +). Names are grouped as disclosed, so a row may
                not be one person{unnamed ? `; ${count(unnamed, 'record without a name is', 'records without a name are')} left out` : ''}.
              </p>
            </>
          )}

        </section>
      )}
    </div>
  )
}

/**
 * One position at one employer: its average by year as a chart and a list, and the people in the
 * year chosen. The same title at other employers is a link away.
 */
const RolePage = ({ entry, years, sources, rows, failed, roleKey, wantedYear, back, onRetry, onYear, onTitle, onPerson, remember }) => {
  const matching = useMemo(() => (rows ? rows.filter((row) => row[1] && titleKey(row[1]) === roleKey) : []), [rows, roleKey])
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
            <h3 className="salaries__year-title">{reportingYearLabel(years[year])}</h3>
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
          <Paged list={ranked} size={50} reset={year}>
            {(page) => (
              <ol className="salaries-rows">
                {page.map((row) => (
                  <RecordRow
                    key={`${row[0]}-${row[2]}-${ranked.indexOf(row)}`}
                    rank={ranked.indexOf(row) + 1}
                    name={row[0]}
                    position={group.spellings.length > 1 ? row[1] : null}
                    pay={row[2]}
                    expenses={row[3]}
                    expenseText={expenseLabel(row[5], sources)}
                    sourceId={oneSource && !row[6] ? null : row[5]}
                    sources={sources}
                    pdfPage={row[6]}
                    nameDisclosure={sources?.[row[5]]?.nameDisclosure}
                    onPerson={onPerson}
                  />
                ))}
              </ol>
            )}
          </Paged>
        </section>
      )}
    </div>
  )
}
