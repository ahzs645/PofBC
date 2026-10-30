// The salaries across every employer, before anything is searched: the employers, the highest-paid
// people, and every position title, each as cards in pages or as one table to sort and filter.
// All of them follow the period range and sector chosen above them.
//
// People are each period's highest-paid named records (people/top.json.gzip, written by the build):
// the full name index is hundreds of files, loaded a surname at a time by the search instead.

import { useEffect, useMemo, useState } from 'react'
import { displayName } from './people.js'
import { keyedTitles } from './positions.js'
import { expenseLabel, reportingYearLabel } from './coverage.js'
import { formatMoney as money } from './money.js'
import { rangeLabel, YearStrip } from './parts.jsx'
import { count, loadJson, Paged, RecordRow, RoleIcon, seenYears } from './common.jsx'
import { DataTable } from './DataTable.jsx'
import { TitleCard } from './TitlePage.jsx'

const within = (range) => (at) => !range || (at >= range[0] && at <= range[1])

/** An employer as a card: its name, its records in the periods chosen, and the years it has any. */
export const EmployerCard = ({ entry, years, range, onOpen }) => {
  const inRange = within(range)
  const latest = entry.counts.reduce((best, value, at) => (value && inRange(at) ? at : best), -1)
  const records = range ? entry.counts.reduce((sum, value, at) => sum + (inRange(at) ? value : 0), 0) : entry.counts[latest] ?? 0
  return (
    <button type="button" className="salaries__card" onClick={() => onOpen(entry.slug)}>
      <span className="salaries__lead"><RoleIcon /></span>
      <span className="salaries__text">
        <span className="salaries__name">{entry.names.at(-1)}</span>
        <span className="salaries__line">{count(records, 'record', 'records')} in {range ? rangeLabel(years, range) : years[latest]}</span>
        <YearStrip years={years} seen={seenYears(entry)} coverage={entry.coverage} />
      </span>
    </button>
  )
}

const PREVIEW = 4

/**
 * Every employer, by sector, as cards: with every sector shown, each lists its largest few and a way
 * to the rest; with one chosen, all of its employers, in pages. As a table, one row an employer.
 */
export const EmployerBrowse = ({ employers, years, sector, range, layout, onOpen, onSector }) => {
  const inRange = within(range)
  const visible = employers.filter((entry) => (sector === 'all' || entry.sector === sector) && entry.counts.some((value, at) => value && inRange(at)))
  const rows = useMemo(() => visible.map((entry) => {
    const periods = entry.counts.map((value, at) => (value && inRange(at) ? at : null)).filter((at) => at !== null)
    return { entry, name: entry.names.at(-1), sector: entry.sector, records: periods.reduce((sum, at) => sum + entry.counts[at], 0), periods: periods.length, latest: years[periods.at(-1)] }
  }), [visible, range]) // eslint-disable-line react-hooks/exhaustive-deps
  const columns = useMemo(() => [
    { id: 'name', header: 'Employer', accessorKey: 'name', cell: ({ row }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onOpen(row.original.entry.slug)}>{row.original.name}</button> },
    { id: 'sector', header: 'Sector', accessorKey: 'sector' },
    { id: 'records', header: 'Records', accessorKey: 'records', meta: { kind: 'number' }, cell: ({ getValue }) => getValue().toLocaleString('en-CA') },
    { id: 'periods', header: 'Periods', accessorKey: 'periods', meta: { kind: 'number', filter: false } },
    { id: 'latest', header: 'Latest', accessorKey: 'latest', cell: ({ getValue }) => reportingYearLabel(getValue() ?? '') }
  ], [onOpen])

  if (layout === 'table') {
    return <DataTable data={rows} columns={columns} sorting={[{ id: 'records', desc: true }]} label="Employers" />
  }
  const bySector = new Map()
  for (const entry of visible) {
    if (!bySector.has(entry.sector)) bySector.set(entry.sector, [])
    bySector.get(entry.sector).push(entry)
  }
  const largest = (a, b) => Math.max(...b.counts) - Math.max(...a.counts)
  if (!visible.length) return <p className="salaries__hint">No employers have imported records in these periods and sector. Choose other periods or clear the filters above.</p>
  if (sector !== 'all') {
    return (
      <Paged list={[...visible].sort(largest)} size={24} reset={`${sector}|${range}`}>
        {(page) => <div className="salaries__grid">{page.map((entry) => <EmployerCard key={entry.slug} entry={entry} years={years} range={range} onOpen={onOpen} />)}</div>}
      </Paged>
    )
  }
  return [...bySector].sort(([a], [b]) => a.localeCompare(b)).map(([name, list]) => (
    <div key={name} className="salaries__sector">
      <h3 className="salaries__sector-title">{name} <span className="salaries__meta">{list.length}</span></h3>
      <div className="salaries__grid">
        {[...list].sort(largest).slice(0, PREVIEW).map((entry) => <EmployerCard key={entry.slug} entry={entry} years={years} range={range} onOpen={onOpen} />)}
      </div>
      {list.length > PREVIEW && <button type="button" className="salaries__more" onClick={() => onSector(name)}>All {list.length} {name.toLowerCase()} →</button>}
    </div>
  ))
}

/** The highest-paid named records across every employer, in the periods and sector chosen. */
export const PeopleBrowse = ({ index, sector, range, layout, onPerson, onEmployer }) => {
  const [top, setTop] = useState(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => { loadJson('salaries/people/top.json.gzip').then(setTop, () => setFailed(true)) }, [])
  const inRange = within(range)
  const rows = useMemo(() => (top ? top.rows.filter((row) => inRange(row[5]) && (sector === 'all' || index.employers[row[4]][1] === sector)).sort((a, b) => b[2] - a[2]) : []), [top, sector, range]) // eslint-disable-line react-hooks/exhaustive-deps
  const columns = useMemo(() => [
    { id: 'name', header: 'Name', accessorFn: (row) => displayName(row[0], index.sources?.[row[6]]?.nameDisclosure), cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(row.original[0])}>{getValue()}</button> },
    { id: 'position', header: 'Position', accessorFn: (row) => row[1] ?? '' },
    { id: 'employer', header: 'Employer', accessorFn: (row) => index.employers[row[4]][0], cell: ({ row, getValue }) => <button type="button" className="salaries__link" onClick={() => onEmployer(index.employers[row.original[4]][3])}>{getValue()}</button> },
    { id: 'period', header: 'Period', accessorFn: (row) => index.years[row[5]] },
    { id: 'pay', header: 'Pay', accessorFn: (row) => row[2], meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'expenses', header: 'Expenses', accessorFn: (row) => row[3], meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) }
  ], [index, onPerson, onEmployer])

  if (failed) return <p className="salaries__hint" role="alert">The highest-paid records could not be loaded.</p>
  if (!top) return <p className="salaries__hint" role="status">Loading the highest-paid records…</p>
  const note = <p className="salaries__hint salaries__hint--small">The {top.perPeriod.toLocaleString('en-CA')} highest-paid named records in each period, across every employer. Search a name to find anyone else.</p>
  if (layout === 'table') return <>{note}<DataTable data={rows} columns={columns} sorting={[{ id: 'pay', desc: true }]} label="Highest-paid records" /></>
  return (
    <>
      {note}
      <Paged list={rows} size={50} reset={`${sector}|${range}`}>
        {(page) => (
          <ol className="salaries-rows">
            {page.map((row) => (
              <RecordRow
                key={`${row[0]}|${row[4]}|${row[5]}|${row[2]}`}
                rank={rows.indexOf(row) + 1}
                name={row[0]}
                position={[row[1], index.employers[row[4]][0], index.years[row[5]]].filter(Boolean).join(' · ')}
                pay={row[2]}
                expenses={row[3]}
                expenseText={expenseLabel(row[6], index.sources)}
                sourceId={row[6]}
                sources={index.sources}
                pdfPage={row[7]}
                nameDisclosure={index.sources?.[row[6]]?.nameDisclosure}
                onPerson={onPerson}
              />
            ))}
          </ol>
        )}
      </Paged>
    </>
  )
}

/** Every position title across employers, with its average in the last period it was disclosed. */
export const PositionBrowse = ({ titlesIndex, years, range, layout, onTitle }) => {
  const titles = useMemo(() => (titlesIndex ? keyedTitles(titlesIndex) : []), [titlesIndex])
  const visible = useMemo(() => titles.filter((title) => !range || (title.first <= range[1] && title.last >= range[0]))
    .sort((a, b) => b.employers - a.employers || b.rows - a.rows), [titles, range])
  const columns = useMemo(() => [
    { id: 'title', header: 'Position', accessorKey: 'label', cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onTitle(row.original.key)}>{getValue()}</button> },
    { id: 'employers', header: 'Employers', accessorKey: 'employers', meta: { kind: 'number', filter: false } },
    { id: 'rows', header: 'Records', accessorKey: 'rows', meta: { kind: 'number', filter: false }, cell: ({ getValue }) => getValue().toLocaleString('en-CA') },
    { id: 'periods', header: 'Periods', accessorFn: (title) => (title.first === title.last ? years[title.first] : `${years[title.first]}–${years[title.last]}`) },
    { id: 'mean', header: 'Latest average', accessorKey: 'mean', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) }
  ], [years, onTitle])

  if (!titlesIndex) return <p className="salaries__hint" role="status">Loading the positions…</p>
  const note = <p className="salaries__hint salaries__hint--small">Each title gathers its spellings across employers; the average is for the last period it was disclosed.</p>
  if (layout === 'table') return <>{note}<DataTable data={visible} columns={columns} sorting={[{ id: 'employers', desc: true }]} label="Positions across employers" /></>
  return (
    <>
      {note}
      <Paged list={visible} size={24} reset={String(range)}>
        {(page) => <div className="salaries__grid">{page.map((title) => <TitleCard key={title.key} title={title} years={years} onOpen={onTitle} />)}</div>}
      </Paged>
    </>
  )
}
