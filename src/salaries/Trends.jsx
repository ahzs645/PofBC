// An employer's records over the years: how many there were and what the middle of them was paid,
// who came onto and went off its list, the raises of names that stayed, its positions by how fast
// their pay grew, and the year chosen in pay bands. Rows are the employer file's: [name, position,
// pay, expenses, year index, source id, PDF page].

import { useMemo } from 'react'
import { personKey } from './people.js'
import { meanMoney, titleKey, titleLabel } from './positions.js'
import { annualRate, formatRate, listChanges, medianOf, payBands, seriesGrowth, stayerRaises, typicalRaise, yearNumber } from './growth.js'
import { compactMoney, PayChart } from './parts.jsx'
import { count } from './common.jsx'
import { DataTable } from './DataTable.jsx'
import { GrowthTip, rateColumn } from './Growth.jsx'
import { formatMoney as money, medianMoney } from './money.js'

/** Every measure the page shows, worked out once from the employer's rows. */
const analyse = (rows, years) => {
  const byYear = new Map()
  for (const row of rows) {
    if (!byYear.has(row[4])) byYear.set(row[4], [])
    byYear.get(row[4]).push(row)
  }
  const changes = listChanges(rows.map((row) => ({ name: row[0], year: row[4] })), years)
  // Raises of names kept on the list, whatever their title: a promotion is a raise too.
  const raises = stayerRaises(rows.map((row) => ({ name: row[0], group: '', pay: row[2], year: row[4] })), years)
  const raisesTo = new Map()
  for (const raise of raises) {
    if (!raisesTo.has(raise.to.year)) raisesTo.set(raise.to.year, [])
    raisesTo.get(raise.to.year).push(raise.rate)
  }
  const perYear = [...byYear].sort(([a], [b]) => yearNumber(years[a]) - yearNumber(years[b]) || a - b).map(([year, list]) => {
    const pay = list.map((row) => row[2])
    const change = changes.get(year)
    const yearRaises = raisesTo.get(year) ?? []
    return {
      year, label: years[year], records: list.length, median: medianMoney(pay), mean: meanMoney(pay),
      total: Math.round(pay.reduce((sum, value) => sum + value, 0)),
      joined: change?.joined, left: change?.left, raise: yearRaises.length ? medianOf(yearRaises) : null, raises: yearRaises.length
    }
  })

  // Positions, each as a series of its own.
  const titles = new Map()
  for (const row of rows) {
    if (!row[1]) continue
    const key = titleKey(row[1])
    if (!titles.has(key)) titles.set(key, { key, spellings: new Map(), rows: [] })
    const title = titles.get(key)
    title.rows.push(row)
    title.spellings.set(row[1], (title.spellings.get(row[1]) ?? 0) + 1)
  }
  const positions = [...titles.values()].map((title) => {
    const cells = new Map()
    for (const row of title.rows) {
      const cell = cells.get(row[4]) ?? { year: row[4], count: 0, sum: 0 }
      cell.count += 1
      cell.sum += row[2]
      cells.set(row[4], cell)
    }
    const series = [...cells.values()].map((cell) => ({ ...cell, mean: cell.sum / cell.count }))
    const latest = series.reduce((best, cell) => (yearNumber(years[cell.year]) > yearNumber(years[best.year]) ? cell : best))
    return {
      key: title.key,
      label: titleLabel([...title.spellings].sort((a, b) => b[1] - a[1])[0][0]),
      growth: seriesGrowth(series, years),
      raise: typicalRaise(stayerRaises(title.rows.map((row) => ({ name: row[0], group: '', pay: row[2], year: row[4] })), years)),
      latest
    }
  }).filter((position) => position.growth || position.raise)

  // An employer reports by fiscal or by calendar year; a few records of the other kind (a council's
  // fiscal year beside a city's calendar ones) are listed, but the measures follow the main kind.
  const calendar = (label) => /^\d{4}$/.test(label)
  const recordsOf = (kind) => perYear.filter((each) => calendar(each.label) === kind).reduce((sum, each) => sum + each.records, 0)
  const mainKind = recordsOf(true) > recordsOf(false)
  const main = perYear.filter((each) => calendar(each.label) === mainKind)
  const first = main[0]
  const last = main.at(-1)
  const span = first && last ? yearNumber(last.label) - yearNumber(first.label) : 0
  return { perYear, main, positions, raise: typicalRaise(raises), medianGrowth: span > 0 ? annualRate(first.median, last.median, span) : null, first, last }
}

export const Trends = ({ rows, years, year, onRole, onYear }) => {
  const analysis = useMemo(() => analyse(rows, years), [rows, years])
  const { perYear, main, positions, raise, medianGrowth, first, last } = analysis
  const chosen = perYear.find((each) => each.year === year) ?? last
  const bands = useMemo(() => payBands(rows.filter((row) => row[4] === chosen?.year).map((row) => row[2])), [rows, chosen?.year])
  const widest = Math.max(1, ...bands.map((band) => band.count))

  const yearColumns = useMemo(() => [
    { id: 'label', header: 'Period', accessorKey: 'label', sortingFn: (a, b) => a.original.year - b.original.year, cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onYear(row.original.year)}>{getValue()}</button> },
    { id: 'records', header: 'Records', accessorKey: 'records', meta: { kind: 'number' }, cell: ({ getValue }) => getValue().toLocaleString('en-CA') },
    { id: 'median', header: 'Median', accessorKey: 'median', meta: { kind: 'money' }, cell: ({ getValue }) => money(Math.round(getValue())) },
    { id: 'mean', header: 'Average', accessorKey: 'mean', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'total', header: 'Total disclosed', accessorKey: 'total', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'joined', header: 'New to the list', accessorKey: 'joined', sortUndefined: 'last', meta: { kind: 'number' }, cell: ({ getValue }) => getValue()?.toLocaleString('en-CA') ?? '—' },
    { id: 'left', header: 'Off the list', accessorKey: 'left', sortUndefined: 'last', meta: { kind: 'number' }, cell: ({ getValue }) => getValue()?.toLocaleString('en-CA') ?? '—' },
    rateColumn('raise', 'Typical raise', (row) => row.raise)
  ], [onYear])
  const positionColumns = useMemo(() => [
    { id: 'label', header: 'Position', accessorKey: 'label', cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onRole(row.original.key)}>{getValue()}</button> },
    rateColumn('growth', 'Average growth', (row) => row.growth?.rate),
    { id: 'span', header: 'Over', accessorFn: (row) => (row.growth ? `${years[row.growth.from.year]}–${years[row.growth.to.year]}` : ''), meta: { filter: false } },
    rateColumn('raise', 'Typical raise', (row) => row.raise?.rate),
    { id: 'raises', header: 'Raises', accessorFn: (row) => row.raise?.pairs ?? 0, meta: { kind: 'number' }, cell: ({ getValue }) => getValue().toLocaleString('en-CA') },
    { id: 'latest', header: 'Latest average', accessorFn: (row) => Math.round(row.latest.mean), meta: { kind: 'money' }, cell: ({ row, getValue }) => <span title={`${count(row.original.latest.count, 'record', 'records')} in ${years[row.original.latest.year]}`}>{money(getValue())}</span> }
  ], [years, onRole])

  if (!perYear.length) return null
  const latestChange = perYear.findLast((each) => each.joined !== undefined)
  return (
    <>
      <section className="salaries__person" aria-labelledby="salaries-trends">
        <h2 id="salaries-trends" className="salaries__title">Over the years <GrowthTip id="salaries-trends-help" /></h2>
        <dl className="salaries__tiles">
          <div><dt>Records</dt><dd>{first.records.toLocaleString('en-CA')} → {last.records.toLocaleString('en-CA')}</dd><dd className="salaries__line">{first.label}–{last.label}</dd></div>
          <div><dt>Median</dt><dd>{formatRate(medianGrowth, '')}</dd><dd className="salaries__line">{medianGrowth === null ? 'one period only' : `a year, ${compactMoney(first.median)} → ${compactMoney(last.median)}`}</dd></div>
          <div><dt>Typical raise</dt><dd>{formatRate(raise?.rate, '')}</dd><dd className="salaries__line">{raise ? `a year, from ${count(raise.pairs, 'raise', 'raises')}` : 'no name in two disclosures'}</dd></div>
          <div><dt>New to the list</dt><dd>{latestChange ? latestChange.joined.toLocaleString('en-CA') : '—'}</dd><dd className="salaries__line">{latestChange ? `in ${latestChange.label}; ${latestChange.left.toLocaleString('en-CA')} off it` : 'one period only'}</dd></div>
        </dl>
        {main.length > 1 && (
          <div className="salaries__charts">
            <div>
              <h3 className="salaries__chart-title">Median pay</h3>
              <PayChart years={years} points={main.map((each) => ({ year: each.year, pay: each.median }))} label="Median pay by year" />
            </div>
            <div>
              <h3 className="salaries__chart-title">Records</h3>
              <PayChart years={years} points={main.map((each) => ({ year: each.year, pay: each.records }))} label="Records by year" format={(value) => value.toLocaleString('en-CA')} describe={(value) => `${value.toLocaleString('en-CA')} records`} />
            </div>
          </div>
        )}
      </section>

      <section aria-labelledby="salaries-trends-years" className="salaries__records">
        <div className="salaries__head">
          <h2 id="salaries-trends-years" className="salaries__title">Year by year</h2>
          <p className="salaries__meta">{count(perYear.length, 'period', 'periods')}</p>
        </div>
        <DataTable data={perYear} columns={yearColumns} sorting={[{ id: 'label', desc: true }]} label="The employer's records by period" />
        <p className="salaries__hint salaries__hint--small">New and off the list compare each period with the one before it of the same kind; crossing the disclosure threshold counts as either.</p>
      </section>

      {positions.length > 0 && (
        <section aria-labelledby="salaries-trends-positions" className="salaries__records">
          <div className="salaries__head">
            <h2 id="salaries-trends-positions" className="salaries__title">Positions by how fast their pay grew</h2>
            <p className="salaries__meta">{count(positions.length, 'position', 'positions')}</p>
          </div>
          <DataTable data={positions} columns={positionColumns} sorting={[{ id: 'growth', desc: true }]} label="Positions by pay growth" />
        </section>
      )}

      {bands.length > 1 && (
        <section aria-labelledby="salaries-trends-bands" className="salaries__person">
          <h2 id="salaries-trends-bands" className="salaries__title">Pay bands in {chosen.label}</h2>
          <ol className="salaries-bands">
            {bands.map((band) => (
              <li key={band.from}>
                <span className="salaries-bands__label">{band.to === null ? `${compactMoney(band.from)}+` : `${compactMoney(band.from)}–${compactMoney(band.to)}`}</span>
                <span className="salaries-bands__bar"><span style={{ width: `${(band.count / widest) * 100}%` }} /></span>
                <span className="salaries-bands__count">{band.count.toLocaleString('en-CA')}</span>
              </li>
            ))}
          </ol>
        </section>
      )}
    </>
  )
}

/** The names under one position at one employer, with their pay in each year they held it. */
export const peopleOverTime = (rows, years) => {
  const groups = new Map()
  for (const row of rows) {
    if (!row[0]) continue
    const key = personKey(row[0])
    if (!groups.has(key)) groups.set(key, { key, name: row[0], latest: row, pay: new Map(), records: new Map() })
    const group = groups.get(key)
    if (yearNumber(years[row[4]]) > yearNumber(years[group.latest[4]])) { group.latest = row; group.name = row[0] }
    group.pay.set(row[4], Math.max(group.pay.get(row[4]) ?? 0, row[2]))
    group.records.set(row[4], (group.records.get(row[4]) ?? 0) + 1)
  }
  return [...groups.values()].map((group) => {
    const held = [...group.pay.keys()].sort((a, b) => yearNumber(years[a]) - yearNumber(years[b]))
    const from = held[0]
    const to = held.at(-1)
    const span = yearNumber(years[to]) - yearNumber(years[from])
    return { ...group, held, from, to, rate: span > 0 ? annualRate(group.pay.get(from), group.pay.get(to), span) : null }
  })
}
