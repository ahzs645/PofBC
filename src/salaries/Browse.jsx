// The salaries across every employer, before anything is searched: the employers, the highest-paid
// people, and every position title, each as cards in pages or as one table to sort and filter.
// All follow the period range; employers and people also follow the chosen sector.
//
// The People view groups each period's highest-paid records by name and employer (people/top.json.gzip):
// the full name index is hundreds of files, loaded a surname at a time by the search instead.

import { useEffect, useMemo, useState } from 'react'
import { displayName, groupHighestPaidRecords } from './people.js'
import { linkLookup } from './nameLinks.js'
import { keyedTitles, shortTitle } from './positions.js'
import { reportingYearLabel } from './coverage.js'
import { formatMoney as money, formatSummaryMoney as summary } from './money.js'
import { personAnnotation, personCurrency } from './recordAnnotations.js'
import { rangeLabel, YearStrip } from './parts.jsx'
import { count, loadJson, Paged, PersonIcon, RoleIcon, seenYears } from './common.jsx'
import { DataTable } from './DataTable.jsx'
import { TitleCard } from './TitlePage.jsx'
import { GrowthTip, rateColumn } from './Growth.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { employerRanking, employerSnapshot } from './employerStats.js'
import { EmployerInsights, EMPLOYER_ORDERS, employerRate, useEmployerStatistics } from './EmployerInsights.jsx'

const within = (range) => (at) => !range || (at >= range[0] && at <= range[1])

/** An employer as a card: its name, its records in the periods chosen, and the years it has any. */
export const EmployerCard = ({ entry, years, range, onOpen, stats }) => {
  const inRange = within(range)
  const latest = entry.counts.reduce((best, value, at) => (value && inRange(at) ? at : best), -1)
  const records = range ? entry.counts.reduce((sum, value, at) => sum + (inRange(at) ? value : 0), 0) : entry.counts[latest] ?? 0
  return (
    <button type="button" className="salaries__card" onClick={() => onOpen(entry.slug, stats ? years[stats.year] : undefined)}>
      <span className="salaries__lead"><RoleIcon /></span>
      <span className="salaries__text">
        <span className="salaries__name">{entry.names.at(-1)}</span>
        <span className="salaries__line">{count(records, 'record', 'records')} in {range ? rangeLabel(years, range) : years[latest]}</span>
        {stats && <span className="employer-card__stats">
          <span className="salaries__line"><b>Median {summary(stats.median)}</b> · Average {summary(stats.mean)}</span>
          {/* The period and count are on the line above unless the statistics come from another one. */}
          {stats.year !== latest && <span className="salaries__line">Statistics: {years[stats.year]} · {count(stats.count, 'employee record', 'employee records')}</span>}
          <span className="salaries__line">{Math.round(stats.above100k / stats.count * 100)}% paid $100,000+{stats.threshold !== STANDARD_THRESHOLD && ` · Threshold ${money(stats.threshold, 'not specified')}`}</span>
          {stats.raise !== null && <span className="salaries__line">Typical raise {employerRate(stats.raise)} · {years[stats.raiseFrom]} → {years[stats.year]}</span>}
        </span>}
        <YearStrip years={years} seen={seenYears(entry)} coverage={entry.coverage} />
      </span>
    </button>
  )
}

const PREVIEW = 4
/** The Financial Information Act's threshold: said once in the notes, and on a card only when it differs. */
export const STANDARD_THRESHOLD = 75000

/**
 * Every employer, by sector, as cards: with every sector shown, each lists its largest few and a way
 * to the rest; with one chosen, all of its employers, in pages. As a table, one row an employer.
 */
export const EmployerBrowse = ({ employers, years, sector, range, layout, onOpen, onSector }) => {
  const [order, setOrder] = useState('sector')
  const { data: statistics, failed, retry } = useEmployerStatistics(years)
  const inRange = within(range)
  const visible = employers.filter((entry) => (sector === 'all' || entry.sector === sector) && entry.counts.some((value, at) => value && inRange(at)))
  const rows = useMemo(() => visible.map((entry) => {
    const periods = entry.counts.map((value, at) => (value && inRange(at) ? at : null)).filter((at) => at !== null)
    return { entry, stats: employerSnapshot(statistics?.[entry.slug], range), name: entry.names.at(-1), sector: entry.sector, records: periods.reduce((sum, at) => sum + entry.counts[at], 0), periods: periods.length, latest: years[periods.at(-1)] }
  }), [visible, range, statistics, years]) // eslint-disable-line react-hooks/exhaustive-deps
  const columns = useMemo(() => [
    { id: 'name', header: 'Employer', accessorKey: 'name', cell: ({ row }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onOpen(row.original.entry.slug, row.original.stats ? years[row.original.stats.year] : undefined)}>{row.original.name}</button> },
    { id: 'sector', header: 'Sector', accessorKey: 'sector' },
    { id: 'records', header: 'Records', accessorKey: 'records', meta: { kind: 'number' }, cell: ({ getValue }) => getValue().toLocaleString('en-CA') },
    { id: 'periods', header: 'Periods', accessorKey: 'periods', meta: { kind: 'number', filter: false } },
    { id: 'latest', header: 'Latest record', accessorKey: 'latest', cell: ({ getValue }) => reportingYearLabel(getValue() ?? '') },
    { id: 'employee-period', header: 'Employee statistics period', accessorFn: ({ stats }) => stats ? years[stats.year] : undefined, sortUndefined: 'last' },
    { id: 'count', header: 'Employee records', accessorFn: ({ stats }) => stats?.count, sortUndefined: 'last', meta: { kind: 'number' }, cell: ({ getValue }) => getValue()?.toLocaleString('en-CA') ?? '—' },
    { id: 'threshold', header: 'Reporting threshold', accessorFn: ({ stats }) => stats?.threshold ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    ...[['median', 'Median pay'], ['mean', 'Average pay']].map(([id, header]) => ({ id, header, accessorFn: ({ stats }) => stats?.[id], sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ getValue }) => summary(getValue()) })),
    { id: 'above100k', header: 'Paid $100,000+', accessorFn: ({ stats }) => stats ? stats.above100k / stats.count : undefined, sortUndefined: 'last', meta: { kind: 'number', filter: false }, cell: ({ getValue }) => getValue() == null ? '—' : `${Math.round(getValue() * 100)}%` },
    { id: 'raise', header: 'Typical raise', accessorFn: ({ stats }) => stats?.raise ?? undefined, sortUndefined: 'last', meta: { kind: 'number', filter: false }, cell: ({ getValue }) => employerRate(getValue()) },
    { id: 'stayers', header: 'Names on both lists', accessorFn: ({ stats }) => stats?.stayers ?? undefined, sortUndefined: 'last', meta: { kind: 'number', filter: false }, cell: ({ getValue }) => getValue()?.toLocaleString('en-CA') ?? '—' },
    { id: 'growth', header: 'Change in records listed', accessorFn: ({ stats }) => stats?.growth ?? undefined, sortUndefined: 'last', meta: { kind: 'number', filter: false }, cell: ({ getValue }) => employerRate(getValue()) },
    { id: 'growth-period', header: 'Growth periods', accessorFn: ({ stats }) => stats?.from != null ? `${years[stats.from]} → ${years[stats.year]}` : '—' }
  ], [onOpen, years])

  const measured = order === 'sector' ? rows : employerRanking(rows, order)
  const header = <>
    <EmployerInsights rows={rows} years={years} ready={Boolean(statistics)} failed={failed} onRetry={retry} onOpen={onOpen} onOrder={setOrder} />
    <div className="employer-insights__order">
      <label>Order employers <select aria-label="Order employers" value={order} onChange={(event) => setOrder(event.target.value)}>{EMPLOYER_ORDERS.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}</select></label>
      {order !== 'sector' && <p className="salaries__meta" role="status">{count(measured.length, 'organization', 'organizations')} with eligible statistics</p>}
    </div>
  </>

  if (layout === 'table') {
    return <>{header}<DataTable key={order} data={measured} columns={columns} sorting={[{ id: order === 'sector' ? 'records' : order, desc: true }]} label="Employers" /></>
  }
  if (order !== 'sector') return <>{header}{measured.length
    ? <Paged list={measured} size={24} reset={`${sector}|${range}|${order}`}>
      {(page) => <div className="salaries__grid">{page.map(({ entry, stats }) => <EmployerCard key={entry.slug} entry={entry} stats={stats} years={years} range={range} onOpen={onOpen} />)}</div>}
    </Paged>
    : <p className="salaries__hint">{statistics ? 'No comparable employee statistics in this selection. Choose other periods or a different ranking.' : failed ? 'Choose By sector to browse while statistics are unavailable.' : 'Loading organization statistics…'}</p>}</>
  const statsBySlug = new Map(rows.map(({ entry, stats }) => [entry.slug, stats]))
  const bySector = new Map()
  for (const entry of visible) {
    if (!bySector.has(entry.sector)) bySector.set(entry.sector, [])
    bySector.get(entry.sector).push(entry)
  }
  const latestCount = (entry) => entry.counts.findLast((value, at) => value && inRange(at)) ?? 0
  const largest = (a, b) => latestCount(b) - latestCount(a)
  if (!visible.length) return <>{header}<p className="salaries__hint">No employers have imported records in these periods and sector. Choose other periods or clear the filters above.</p></>
  if (sector !== 'all') {
    return (
      <>{header}
      <Paged list={[...visible].sort(largest)} size={24} reset={`${sector}|${range}`}>
        {(page) => <div className="salaries__grid">{page.map((entry) => <EmployerCard key={entry.slug} entry={entry} stats={statsBySlug.get(entry.slug)} years={years} range={range} onOpen={onOpen} />)}</div>}
      </Paged>
      </>
    )
  }
  return <>{header}{[...bySector].sort(([a], [b]) => a.localeCompare(b)).map(([name, list]) => (
    <div key={name} className="salaries__sector">
      <h3 className="salaries__sector-title">{name} <span className="salaries__meta">{list.length}</span></h3>
      <div className="salaries__grid">
        {[...list].sort(largest).slice(0, PREVIEW).map((entry) => <EmployerCard key={entry.slug} entry={entry} stats={statsBySlug.get(entry.slug)} years={years} range={range} onOpen={onOpen} />)}
      </div>
      {list.length > PREVIEW && <button type="button" className="salaries__more" onClick={() => onSector(name)}>All {list.length} {name.toLowerCase()} →</button>}
    </div>
  ))}</>
}

/**
 * A disclosed name and employer, represented by its highest ranked payment. Opening it retains
 * every source record, including other periods and unverified compiled overlaps.
 */
const TopRecordCard = ({ group, rank, index, onPerson }) => {
  const { row, records, years } = group
  return (
    <button type="button" className="salaries__card" onClick={() => onPerson(group.name, index.employers[row[4]][3])}>
      <span className="salaries__lead"><PersonIcon /></span>
      <span className="salaries__text">
        <span className="salaries__name">{displayName(group.name, index.sources?.[row[6]]?.nameDisclosure)}</span>
        {row[1] && <span className="salaries__line">{shortTitle(row[1])}</span>}
        <span className="salaries__line">{index.employers[row[4]][0]}</span>
        {years.length > 1 && <span className="salaries__line">{records.length > years.length ? `${count(records.length, 'record', 'records')} in ${count(years.length, 'period', 'periods')}` : count(years.length, 'period', 'periods')}</span>}
        {group.aliases.length > 0 && <AliasLine aliases={group.aliases} records={records} sources={index.sources} />}
        {/* Another currency is a different measure, so it is listed here rather than beside the ranked CAD amount. */}
        {group.foreign?.map((foreign, at) => (
          <span className="salaries__line" key={at} title={personAnnotation(foreign, index)?.measure}>
            Also {money(foreign[2], '—', personCurrency(foreign, index))} in {index.years[foreign[5]]}, not ranked
          </span>
        ))}
      </span>
      <span className="salaries__aside">{money(row[2], '—', personCurrency(row, index))}<span className="salaries__line">{rank != null ? `No. ${rank} · ` : 'Unranked · '}{index.years[row[5]]}</span></span>
    </button>
  )
}

/** The other spellings a name's records were joined under, and how sure the join is (nameLinks.js). */
export const AliasLine = ({ aliases, records, sources }) => {
  const sure = aliases.every((alias) => alias.status === 'verified')
  return (
    <span className="salaries__line">
      Also disclosed as {aliases.map((alias) => displayName(alias.name, sources?.[records.find((row) => row[0].startsWith(alias.name))?.[6]]?.nameDisclosure)).join(', ')}
      {sure ? '' : ' (likely the same person)'}
    </span>
  )
}

/** Highest payments grouped by disclosed name and employer, in the chosen periods and sector. */
export const PeopleBrowse = ({ index, sector, range, layout, onPerson, onEmployer }) => {
  const [top, setTop] = useState(null)
  const [links, setLinks] = useState(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    loadJson('salaries/people/top.json.gzip').then(setTop, () => setFailed(true))
    // Without the link list the names are shown as disclosed, each spelling apart.
    loadJson('salaries/links/top.json.gzip').then(setLinks, () => setLinks({ links: [] }))
  }, [])
  const lookup = useMemo(() => linkLookup(links, index.employers), [links, index])
  const rows = useMemo(() => top && links ? groupHighestPaidRecords(top.rows, { employers: index.employers, sources: index.sources, sector, range, links: lookup }) : [], [top, links, lookup, index, sector, range])
  const foreign = useMemo(() => top && links ? groupHighestPaidRecords(top.unrankedRows ?? [], { employers: index.employers, sources: index.sources, sector, range, links: lookup }) : [], [top, links, lookup, index, sector, range])
  const foreignByKey = useMemo(() => new Map(foreign.map((group) => [group.key, group.records])), [foreign])
  const unranked = foreign.filter((group) => !rows.some((ranked) => ranked.key === group.key))
  const columns = useMemo(() => [
    { id: 'name', header: 'Name', accessorFn: ({ name, row }) => displayName(name, index.sources?.[row[6]]?.nameDisclosure), cell: ({ row: { original }, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(original.name, index.employers[original.row[4]][3])}>{getValue()}</button> },
    { id: 'position', header: 'Position', accessorFn: ({ row }) => row[1] ?? '' },
    { id: 'employer', header: 'Employer', accessorFn: ({ row }) => index.employers[row[4]][0], cell: ({ row: { original }, getValue }) => <button type="button" className="salaries__link" onClick={() => onEmployer(index.employers[original.row[4]][3])}>{getValue()}</button> },
    { id: 'period', header: 'Payment period', accessorFn: ({ row }) => index.years[row[5]] },
    { id: 'pay', header: 'Highest payment', accessorFn: ({ row }) => row[2], meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'expenses', header: 'Expenses', accessorFn: ({ row }) => row[3], meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'records', header: 'Ranked records', accessorFn: ({ records }) => records.length, meta: { kind: 'number', filter: false } },
    ...(foreign.length ? [{ id: 'other-currencies', header: 'Other currencies · unranked', accessorFn: (group) => (foreignByKey.get(group.key) ?? []).map((row) => `${money(row[2], '—', personCurrency(row, index))} · ${index.years[row[5]]}`).join('; ') }] : [])
  ], [index, onPerson, onEmployer, foreign, foreignByKey])

  if (failed) return <p className="salaries__hint" role="alert">The highest-paid records could not be loaded.</p>
  if (!top || !links) return <p className="salaries__hint" role="status">Loading the highest-paid records…</p>
  const note = <p className="salaries__hint salaries__hint--small">Each name’s highest CAD payment at an employer, from each period’s top {top.perPeriod.toLocaleString('en-CA')}. Other currencies are unranked. The same name may be different people.</p>
  const otherCurrencies = <>{unranked.length > 0 && <section aria-label="Other currencies"><h3 className="salaries__title">Other currencies · unranked</h3><div className="salaries__grid">{unranked.map((group) => <TopRecordCard key={group.key} group={group} index={index} onPerson={onPerson} />)}</div></section>}</>
  if (layout === 'table') return <>{note}<DataTable data={rows} columns={columns} sorting={[{ id: 'pay', desc: true }]} label="Highest CAD payments by name and employer" />{otherCurrencies}</>
  return (
    <>
      {note}
      <Paged list={rows} size={24} reset={`${sector}|${range}`}>
        {(page) => {
          const first = rows.indexOf(page[0])
          return (
            <div className="salaries__grid">
              {page.map((group, at) => <TopRecordCard key={group.key} group={{ ...group, foreign: foreignByKey.get(group.key) }} rank={first + at + 1} index={index} onPerson={onPerson} />)}
            </div>
          )
        }}
      </Paged>
      {unranked.length > 0 && <section aria-label="Other currencies"><h3 className="salaries__title">Other currencies · unranked</h3><div className="salaries__grid">{unranked.map((group) => <TopRecordCard key={group.key} group={group} index={index} onPerson={onPerson} />)}</div></section>}
    </>
  )
}

/** Titles ranked by how fast their pay moved need this much behind the measure (growth.js). */
const MEASURED = { growth: (title) => title.growth?.weight >= 10, raise: (title) => title.raise?.pairs >= 10 }
const TITLE_ORDERS = [
  { value: 'used', label: 'Most used' },
  { value: 'growth', label: 'Fastest growth' },
  { value: 'raise', label: 'Biggest raises' }
]

/**
 * Every position title across employers, with its average in the last period it was disclosed; or,
 * ordered by how fast its pay moved, only the titles with enough records to say.
 */
export const PositionBrowse = ({ titlesIndex, years, range, layout, onTitle }) => {
  const [order, setOrder] = useState('used')
  const titles = useMemo(() => (titlesIndex ? keyedTitles(titlesIndex) : []), [titlesIndex])
  const visible = useMemo(() => titles.filter((title) => (!range || (title.first <= range[1] && title.last >= range[0])) && (order === 'used' || MEASURED[order](title)))
    .sort(order === 'used' ? (a, b) => b.employers - a.employers || b.rows - a.rows : (a, b) => b[order].rate - a[order].rate), [titles, range, order])
  const columns = useMemo(() => [
    { id: 'title', header: 'Position', accessorKey: 'label', cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onTitle(row.original.key)}>{getValue()}</button> },
    { id: 'employers', header: 'Employers', accessorKey: 'employers', meta: { kind: 'number', filter: false } },
    { id: 'rows', header: 'Records', accessorKey: 'rows', meta: { kind: 'number', filter: false }, cell: ({ getValue }) => getValue().toLocaleString('en-CA') },
    { id: 'periods', header: 'Periods', accessorFn: (title) => (title.first === title.last ? years[title.first] : `${years[title.first]}–${years[title.last]}`) },
    { id: 'mean', header: 'Latest average', accessorKey: 'mean', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    rateColumn('growth', 'Average growth', (title) => title.growth?.rate),
    rateColumn('raise', 'Typical raise', (title) => title.raise?.rate),
    { id: 'raises', header: 'Raises', accessorFn: (title) => title.raise?.pairs ?? 0, meta: { kind: 'number' } }
  ], [years, onTitle])

  if (!titlesIndex) return <p className="salaries__hint" role="status">Loading the positions…</p>
  const note = (
    <div className="salaries__browse-bar salaries__browse-bar--position-order">
      <Segmented compact ariaLabel="Order positions" value={order} onChange={setOrder} options={TITLE_ORDERS} />
      <p className="salaries__hint salaries__hint--small salaries__order-note">
        {order === 'used'
          ? 'Grouped titles · latest CAD averages'
          : order === 'growth'
            ? 'Titles whose average could be followed over 10 or more records, fastest first.'
            : 'Titles with 10 or more raises of a name kept under them, largest first.'}
        {order !== 'used' && <GrowthTip id="salaries-positions-growth" />}
      </p>
    </div>
  )
  const sorting = [order === 'used' ? { id: 'employers', desc: true } : { id: order, desc: true }]
  if (layout === 'table') return <>{note}<DataTable key={order} data={visible} columns={columns} sorting={sorting} label="Positions across employers" /></>
  return (
    <>
      {note}
      <Paged list={visible} size={24} reset={`${range}|${order}`}>
        {(page) => <div className="salaries__grid">{page.map((title) => <TitleCard key={title.key} title={title} years={years} onOpen={onTitle} measure={order === 'used' ? null : order} />)}</div>}
      </Paged>
    </>
  )
}
