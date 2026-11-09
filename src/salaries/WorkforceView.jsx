// The B.C. Public Service as aggregates, set out like the other salary sections: the FOI release's
// average headcount and salary by year, and the BC Stats Workforce Profiles tables, each as cards or
// as one sortable table. Nothing here is a list of people.

import { useEffect, useId, useMemo, useState } from 'react'
import { CompanionShell, Chips } from './CompanionShell.jsx'
import { DataTable } from './DataTable.jsx'
import { count } from './common.jsx'
import { formatWorkforceNumber, formatWorkforceSalary, loadWorkforce, normalizeWorkforcePopulation, selectWorkforceRows, workforceAssetUrl } from './workforce.js'
import { loadProfiles, numericColumns, profileAssetUrl, profileNumber, profileParts, PROFILE_KINDS, withMinistryNames } from './workforceProfiles.js'
import { CPI_LATEST, inDollarsOf } from './inflation.js'
import { formatRate } from './growth.js'
import './workforce.css'

function MeasureChart({ rows, measure, label, format }) {
  const id = useId()
  const width = 520
  const height = 224
  const left = 62
  const right = 14
  const top = 34
  const bottom = 42
  const plotHeight = height - top - bottom
  const unit = measure === 'averageHeadCount' ? 5000 : 10000
  const maximum = Math.ceil(Math.max(...rows.map((row) => row[measure])) / unit) * unit
  const step = (width - left - right) / rows.length
  return (
    <figure className="workforce__chart">
      <figcaption>{label}</figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby={`${id}-title`}>
        <title id={`${id}-title`}>{label} by year label; exact values are in the table view</title>
        {[0, maximum / 2, maximum].map((value) => {
          const y = top + plotHeight * (1 - value / maximum)
          return <g key={value} className="workforce__chart-grid"><line x1={left} y1={y} x2={width - right} y2={y} /><text x={left - 8} y={y + 4} textAnchor="end">{format(value)}</text></g>
        })}
        {rows.map((row, index) => {
          const x = left + step * index + step / 2
          const barHeight = plotHeight * row[measure] / maximum
          return (
            <g key={row.yearLabel}>
              <rect className={`workforce__bar workforce__bar--${measure === 'averageHeadCount' ? 'averageHeadCount' : 'averageSalary'}`} x={x - step * 0.29} y={top + plotHeight - barHeight} width={step * 0.58} height={barHeight} rx="2" />
              <text className="workforce__chart-value" x={x} y={top + plotHeight - barHeight - 7} textAnchor="middle">{format(row[measure])}</text>
              <text className="workforce__chart-year" x={x} y={height - bottom + 20} textAnchor="middle">{row.yearLabel}</text>
            </g>
          )
        })}
      </svg>
    </figure>
  )
}

const salaryIn = (row) => Math.round(inDollarsOf(row.averageSalary, row.yearLabel))

/** The FOI release's two series for one population, as charts or as a table. */
function HeadcountSalary({ data, populationId, layout }) {
  const population = data.populations.find((item) => item.id === populationId)
  const rows = selectWorkforceRows(data, populationId).map((row) => ({ ...row, realSalary: salaryIn(row) }))
  const columns = useMemo(() => [
    { id: 'year', header: 'Year label', accessorKey: 'yearLabel' },
    { id: 'headcount', header: 'Average HeadCount', accessorKey: 'averageHeadCount', meta: { kind: 'number' }, cell: ({ getValue }) => formatWorkforceNumber(getValue()) },
    { id: 'salary', header: 'Average Salary', accessorKey: 'averageSalary', meta: { kind: 'money' }, cell: ({ getValue }) => formatWorkforceSalary(getValue()) },
    { id: 'real', header: `In ${CPI_LATEST} dollars`, accessorKey: 'realSalary', meta: { kind: 'money' }, cell: ({ getValue }) => formatWorkforceSalary(getValue()) }
  ], [])
  return (
    <section aria-labelledby="workforce-foi">
      <div className="salaries__head">
        <h3 id="workforce-foi" className="salaries__title">{population.label}</h3>
        <p className="salaries__meta"><a href={`${data.source.url}#page=${population.sourcePage}`} target="_blank" rel="noreferrer">FOI {data.source.id}, PDF p. {population.sourcePage}</a> · <a href={workforceAssetUrl('csv')} download="bc-public-service-workforce.csv">CSV</a> · <a href={workforceAssetUrl('json')} download="bc-public-service-workforce.json">JSON</a></p>
      </div>
      {layout === 'table'
        ? <DataTable data={rows} columns={columns} sorting={[{ id: 'year', desc: true }]} label={`${population.label}: average headcount and salary`} />
        : <div className="workforce__charts">
          <MeasureChart rows={rows} measure="averageHeadCount" label="Average HeadCount" format={formatWorkforceNumber} />
          <MeasureChart rows={rows} measure="averageSalary" label="Average Salary, as published" format={formatWorkforceSalary} />
          <MeasureChart rows={rows} measure="realSalary" label={`Average Salary in ${CPI_LATEST} dollars (B.C. CPI)`} format={formatWorkforceSalary} />
        </div>}
      <details className="salaries__about">
        <summary className="salaries__title">How to read these figures</summary>
        <ul className="salaries__hint salaries__hint--small workforce__notes">
          <li>“Average HeadCount” and “Average Salary” are the release’s own labels; it does not explain how they were calculated, or when each year starts and ends. Year labels are as printed, and 2024 may not be a complete year.</li>
          <li>{populationId === 'victoria' ? 'Victoria-office employees are also counted in the all-employees figures; do not add the two populations.' : 'The population is the B.C. Public Service only, not the wider public sector.'} Page 1 of the release has the all-employees table and page 3 the Victoria-office table.</li>
          <li>These aggregates are separate from the named payment records, which only list people above the $75,000 threshold, and cannot be compared directly with an average of them. Dollars adjusted to {CPI_LATEST} use the B.C. consumer price index.</li>
        </ul>
      </details>
    </section>
  )
}

/** Employee counts by ministry as bars, largest first: the one profile table that reads as a chart. */
const MinistryBars = ({ table }) => {
  const at = { key: table.columns.indexOf('Ministry_Key'), name: table.columns.indexOf('Ministry'), type: table.columns.indexOf('Employee_Type'), value: table.columns.indexOf('Employee_Count') }
  const bars = table.rows.filter((row) => row[at.type] === 'ALL' && row[at.key] !== 'BCPS')
    .map((row) => ({ key: row[at.key], name: row[at.name] || row[at.key], value: profileNumber(row[at.value]) }))
    .filter((bar) => bar.value !== null).sort((a, b) => b.value - a.value)
  const widest = Math.max(1, ...bars.map((bar) => bar.value))
  const total = table.rows.find((row) => row[at.key] === 'BCPS' && row[at.type] === 'ALL')
  return (
    <div>
      {total && <p className="salaries__meta">B.C. Public Service in total: {formatWorkforceNumber(profileNumber(total[at.value]))} employees, all types.</p>}
      <ol className="salaries-bands workforce__ministries">
        {bars.map((bar) => (
          <li key={bar.key}>
            <span className="salaries-bands__label" title={bar.key}>{bar.name}</span>
            <span className="salaries-bands__bar"><span style={{ width: `${(bar.value / widest) * 100}%` }} /></span>
            <span className="salaries-bands__count">{formatWorkforceNumber(bar.value)}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

/** One profile table: its rows as a sortable table, with ministry names beside their keys. */
function Profiles({ data, edition, kind, query, layout, onEdition, onKind }) {
  const editions = [...new Set(data.tables.map((table) => profileParts(table.name).edition))].sort().reverse()
  const kinds = data.tables.filter((table) => profileParts(table.name).edition === edition).map((table) => profileParts(table.name).kind)
  const chosenKind = kinds.includes(kind) ? kind : kinds[0]
  const raw = data.tables.find((table) => table.name === `WP${edition}_${chosenKind}`)
  const table = useMemo(() => withMinistryNames(raw, data.tables), [raw, data.tables])
  const numeric = useMemo(() => numericColumns(table), [table])
  const words = query.trim().toLocaleLowerCase('en-CA').split(/\s+/).filter(Boolean)
  const rows = useMemo(() => table.rows.filter((row) => words.every((word) => row.some((cell) => cell.toLocaleLowerCase('en-CA').includes(word)))), [table, query]) // eslint-disable-line react-hooks/exhaustive-deps
  const columns = useMemo(() => table.columns.map((column, at) => ({
    id: `${at}`,
    header: column.replaceAll('_', ' '),
    accessorFn: (row) => (numeric[at] ? profileNumber(row[at]) ?? undefined : row[at]),
    sortUndefined: 'last',
    meta: numeric[at] ? { kind: 'number' } : undefined,
    cell: ({ row }) => row.original[at] === '' ? '—' : row.original[at]
  })), [table, numeric])
  return (
    <section aria-labelledby="workforce-profiles">
      <Chips label="Profile edition" value={edition} onChange={onEdition} options={editions.map((value) => ({ value, label: value }))} />
      <Chips label="Profile table" value={chosenKind} onChange={onKind} options={kinds.map((value) => ({ value, label: PROFILE_KINDS[value] ?? value.replaceAll('_', ' '), count: data.tables.find((each) => each.name === `WP${edition}_${value}`).rowCount }))} />
      <div className="salaries__head">
        <h3 id="workforce-profiles" className="salaries__title">{PROFILE_KINDS[chosenKind] ?? chosenKind}, {edition}</h3>
        <p className="salaries__meta">{count(rows.length, 'row', 'rows')}{words.length ? ` matching “${query.trim()}”` : ''} · <a href={raw.url} target="_blank" rel="noreferrer">BC Stats CSV</a> · <a href={profileAssetUrl()} download="bc-workforce-profiles.json">every table (JSON)</a></p>
      </div>
      {layout === 'cards' && chosenKind === 'EmpCounts' && !words.length
        ? <MinistryBars table={table} />
        : <DataTable key={table.name} data={rows} columns={columns} label={`${table.name} source rows`} />}
      <details className="salaries__about">
        <summary className="salaries__title">How to read these tables</summary>
        <ul className="salaries__hint salaries__hint--small workforce__notes">
          <li>Aggregate statistics from BC Stats corporate surveys, not a list of people. Cells keep their published text: “S” (suppressed), “NA” and blanks are not zero.</li>
          <li>Tables use different units and denominators, and groups overlap, so rows should not be added together. Comparison columns can refer to earlier years than the edition.</li>
          <li>Ministry names come from each edition’s own ministry key, since keys change between editions. <a href={data.catalogueUrl} target="_blank" rel="noreferrer">BC Stats catalogue and methods</a> · {data.license}.</li>
        </ul>
      </details>
    </section>
  )
}

export default function WorkforceView({ place, setPlace, onBrowse }) {
  const [data, setData] = useState(null)
  const [profiles, setProfiles] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const [edition, setEdition] = useState('2024')
  const [kind, setKind] = useState('EmpCounts')
  useEffect(() => {
    const controller = new AbortController()
    setFailed(false)
    Promise.all([loadWorkforce({ signal: controller.signal }), loadProfiles({ signal: controller.signal })]).then(
      ([workforce, archive]) => { if (!controller.signal.aborted) { setData(workforce); setProfiles(archive) } },
      () => { if (!controller.signal.aborted) setFailed(true) }
    )
    return () => controller.abort()
  }, [attempt])
  const section = place.show === 'profiles' ? 'profiles' : 'foi'
  const populationId = normalizeWorkforcePopulation(place?.workforcePopulation)
  const layout = place.layout === 'table' ? 'table' : 'cards'
  const update = (key, value) => setPlace((current) => ({ ...current, [key]: value }))

  const series = data ? selectWorkforceRows(data, 'all') : []
  const first = series[0]
  const last = series.at(-1)
  const realChange = first && last ? salaryIn(last) / salaryIn(first) - 1 : null
  const tiles = data && profiles ? [
    { label: 'Average headcount', value: formatWorkforceNumber(last.averageHeadCount), note: `${last.yearLabel}, B.C. Public Service` },
    { label: 'Average salary', value: formatWorkforceSalary(last.averageSalary), note: `${last.yearLabel}, as published` },
    { label: 'After inflation', value: formatRate(realChange, ''), note: `average salary, ${first.yearLabel}–${last.yearLabel}` },
    { label: 'Profile tables', value: profiles.tables.length, note: `${profiles.totalSourceRows.toLocaleString('en-CA')} rows, ${[...new Set(profiles.tables.map((table) => profileParts(table.name).edition))].length} editions` }
  ] : []

  return (
    <CompanionShell
      browse="workforce" onBrowse={onBrowse}
      layout={layout} onLayout={(next) => update('layout', next)}
      query={place.q ?? ''} onSearch={section === 'profiles' ? (value) => update('q', value) : null}
      searchLabel="Search the profile tables" placeholder="Ministry, group or any value"
      searchHelp="Find rows in the chosen Workforce Profiles table that contain every word typed, such as a ministry, a group or an occupation."
      heading="B.C. Public Service workforce"
      intro={<p>Aggregate figures for the B.C. Public Service as a whole: average headcount and salary from an official freedom-of-information release, and BC Stats’ Workforce Profiles. They count everyone, not just the people named in the payment records.</p>}
      tiles={tiles}
    >
      {failed
        ? <p className="salaries__hint" role="alert">Workforce statistics could not be loaded. <button type="button" className="salaries__link" onClick={() => setAttempt((value) => value + 1)}>Retry</button></p>
        : !data || !profiles ? <p className="salaries__hint" role="status">Loading workforce statistics…</p>
          : <div className="workforce">
            <Chips label="Section" value={section} onChange={(value) => update('show', value === 'profiles' ? 'profiles' : null)} options={[
              { value: 'foi', label: 'Headcount & salary', count: data.observations.length / data.populations.length },
              { value: 'profiles', label: 'Workforce Profiles', count: profiles.tables.length }
            ]} />
            {section === 'foi'
              ? <>
                <Chips label="Population" value={populationId} onChange={(value) => update('workforcePopulation', value)} options={data.populations.map((item) => ({ value: item.id, label: item.label }))} />
                <HeadcountSalary data={data} populationId={populationId} layout={layout} />
              </>
              : <Profiles data={profiles} edition={edition} kind={kind} query={place.q ?? ''} layout={layout} onEdition={setEdition} onKind={setKind} />}
          </div>}
    </CompanionShell>
  )
}
