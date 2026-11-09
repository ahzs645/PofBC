import { useMemo, useEffect, useState } from 'react'
import { CompanionShell, Chips } from './CompanionShell.jsx'
import { DataTable } from './DataTable.jsx'
import { count, Paged, PersonIcon, RoleIcon } from './common.jsx'
import { councilCsv, councilMeasure, councilMoney, councilNotes, councilRows, councilSourceMap, councilSourceUrl, councilYearCoverage, describeCouncilYears, filterCouncilRows, loadCouncilPay } from './councilPay.js'
import './councilPay.css'

const BASE = import.meta.env?.BASE_URL ?? '/'
const humanize = (value) => value.replace(/([a-z])([A-Z])/g, '$1 $2').replaceAll('-', ' ').replace(/^./, (letter) => letter.toUpperCase())

const SourceLink = ({ source, page }) => {
  const href = councilSourceUrl(source?.url)
  const original = councilSourceUrl(source?.originalUrl)
  return <>{href ? <a href={href} target="_blank" rel="noreferrer">{source.title}{page ? ` · PDF p. ${page}` : ''}</a> : <span>{source?.title ?? 'Source unavailable'}</span>}{original && <> · <a href={original} target="_blank" rel="noreferrer">Original article</a></>}</>
}

const SupportingSources = ({ source }) => (source?.supportingSources ?? []).map((support) => <p key={support.url}><SourceLink source={support} />{support.locator ? ` · ${support.locator}` : ''}</p>)

const RecordDetails = ({ row, source }) => {
  const notes = councilNotes(row.notes)
  const sourceNotes = councilNotes(source?.notes)
  const components = Object.entries(row.components ?? {})
  const precision = row.sourcePrecision ?? row.amountPrecisionCad
  return <div className="council-pay__evidence">
    <p><SourceLink source={source} page={row.pdfPage} /></p>
    <p className="council-pay__muted">{humanize(source?.kind ?? 'Source')}</p>
    {row.sourceRowLabel && <p>{row.sourceRowLabel}</p>}
    {!row.sourceRowLabel && row.tableLabel && <p>Source table: {row.tableLabel}</p>}
    {Number.isFinite(precision) && precision >= 1 && <p className="council-pay__muted">Reported precision: {councilMoney(precision, row.currency)}.</p>}
    {row.sourceLocator && <p>{row.sourceLocator}</p>}
    {source?.locator && source.locator !== row.sourceLocator && <p className="council-pay__muted">{source.locator}</p>}
    {row.effectiveFrom && <p>Effective from {row.effectiveFrom}{row.effectiveTo ? ` to ${row.effectiveTo}` : ''}.</p>}
    {!row.effectiveFrom && row.effectiveTo && <p>Effective through {row.effectiveTo}.</p>}
    {row.effectiveDateNote && <p>{row.effectiveDateNote}</p>}
    {row.sourceEffectiveFrom && <p>Published rate interval: {row.sourceEffectiveFrom}{row.sourceEffectiveTo ? ` to ${row.sourceEffectiveTo}` : ''}. The annual row retains this source interval.</p>}
    {row.scheduleVersion && <p>Schedule edition: {humanize(row.scheduleVersion)}.</p>}
    {notes.length > 0 && <ul>{notes.map((note, at) => <li key={at}>{note}</li>)}</ul>}
    {(components.length > 0 || sourceNotes.length > 0) && <details>
      <summary>{components.length ? 'Payment components and source notes' : 'Source notes'}</summary>
      {components.length > 0 && <dl className="council-pay__components">{components.map(([name, value]) => <div key={name}><dt>{humanize(name)}</dt><dd>{typeof value === 'number' || value == null ? councilMoney(value, row.currency) : String(value)}</dd></div>)}</dl>}
      {sourceNotes.length > 0 && <ul>{sourceNotes.map((note, at) => <li key={at}>{note}</li>)}</ul>}
      <SupportingSources source={source} />
    </details>}
  </div>
}

const Filter = ({ label, value, onChange, children }) => <label className="council-pay__filter"><span>{label}</span><select value={value} onChange={(event) => onChange(event.target.value)}>{children}</select></label>

/** One office figure or named payment as a card, like an employer or a person elsewhere; its source opens below. */
const CouncilCard = ({ row, tab, source, onEmployer }) => {
  const payment = tab === 'payments'
  return (
    <article className="salaries__card salaries__card--static council-pay__card">
      <span className="salaries__lead">{payment ? <PersonIcon /> : <RoleIcon />}</span>
      <span className="salaries__text">
        <span className="salaries__name">{payment ? row.name : row.municipality}</span>
        <span className="salaries__line">{payment ? row.role : `${row.role} · ${councilMeasure(row.measure)}`}</span>
        <span className="salaries__line">
          {payment && <>{row.employerSlug && onEmployer ? <button type="button" className="salaries__link" onClick={() => onEmployer(row.employerSlug)}>{row.municipality}</button> : row.municipality} · </>}
          {row.year}
        </span>
        <details className="council-pay__card-source">
          <summary>Source</summary>
          <RecordDetails row={row} source={source} />
        </details>
      </span>
      <span className="salaries__aside">
        {councilMoney(payment ? row.remuneration : row.amount, row.currency)}
        <span className="salaries__line">{payment ? (Number.isFinite(row.expenses) ? `Expenses ${councilMoney(row.expenses, row.currency)}` : 'Expenses not stated') : Number.isFinite(row.annualSupplement) ? `+ ${councilMoney(row.annualSupplement, row.currency)} supplement` : 'office figure'}</span>
      </span>
    </article>
  )
}

export default function CouncilPayView({ place, setPlace, onBrowse, onEmployer }) {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const tab = place.councilTab === 'payments' ? 'payments' : 'rates'
  const municipality = place.councilMunicipality || 'all'
  const year = place.councilYear || 'all'
  const role = place.councilRole || 'all'
  const query = place.q ?? ''
  const layout = place.layout === 'table' ? 'table' : 'cards'

  useEffect(() => {
    const controller = new AbortController()
    setFailed(false)
    loadCouncilPay({ signal: controller.signal }).then((value) => { if (!controller.signal.aborted) setData(value) }, () => { if (!controller.signal.aborted) setFailed(true) })
    return () => controller.abort()
  }, [attempt])

  const sources = useMemo(() => data ? councilSourceMap(data) : new Map(), [data])
  const rows = useMemo(() => data ? councilRows(data, tab) : [], [data, tab])
  const filtered = useMemo(() => filterCouncilRows(rows, { query, municipality, year, role }, sources), [rows, query, municipality, year, role, sources])
  const coverageRows = useMemo(() => filterCouncilRows(rows, { municipality, role }), [rows, municipality, role])
  const observed = useMemo(() => councilYearCoverage(coverageRows), [coverageRows])
  const series = useMemo(() => (data?.coverage?.timeSeries ?? []).filter((entry) => entry.municipality === municipality && (role === 'all' || entry.role === role) && (tab === 'payments' ? entry.measure === 'actual-remuneration' : entry.measure !== 'actual-remuneration')), [data, municipality, role, tab])
  const municipalities = useMemo(() => [...new Set([...(data?.coverage?.municipalities ?? []).map((entry) => entry.municipality), ...rows.map((row) => row.municipality)])].sort((a, b) => a.localeCompare(b, 'en-CA')), [data, rows])
  const years = useMemo(() => [...new Set(rows.map((row) => String(row.year)))].sort((a, b) => b - a), [rows])
  // Roles as chips, each with how many rows it has under the other filters.
  const roleCounts = useMemo(() => {
    const counts = new Map()
    for (const row of filterCouncilRows(rows, { query, municipality, year }, sources)) counts.set(row.role, (counts.get(row.role) ?? 0) + 1)
    return [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  }, [rows, query, municipality, year, sources])
  const update = (key, value) => setPlace((current) => ({ ...current, [key]: value }))
  const clear = () => setPlace((current) => ({ ...current, q: '', councilMunicipality: 'all', councilYear: 'all', councilRole: 'all' }))
  const download = () => {
    const url = URL.createObjectURL(new Blob(['﻿', councilCsv(filtered, tab, sources)], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `bc-council-${tab}-filtered.csv`
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  const payment = tab === 'payments'
  const columns = useMemo(() => [
    { id: 'municipality', header: 'Municipality', accessorKey: 'municipality' },
    { id: 'year', header: 'Year', accessorFn: (row) => row.year, meta: { kind: 'number' } },
    ...(payment ? [{ id: 'name', header: 'Official', accessorKey: 'name' }] : []),
    { id: 'role', header: 'Role', accessorKey: 'role' },
    ...(payment
      ? [
        { id: 'remuneration', header: 'Remuneration', accessorFn: (row) => row.remuneration ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ row }) => councilMoney(row.original.remuneration, row.original.currency) },
        { id: 'expenses', header: 'Expenses', accessorFn: (row) => row.expenses ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ row }) => councilMoney(row.original.expenses, row.original.currency) }
      ]
      : [
        { id: 'measure', header: 'Type of figure', accessorFn: (row) => councilMeasure(row.measure) },
        { id: 'amount', header: 'Amount', accessorFn: (row) => row.amount ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ row }) => councilMoney(row.original.amount, row.original.currency) }
      ]),
    { id: 'source', header: 'Source', accessorFn: (row) => sources.get(row.sourceId)?.title ?? '', cell: ({ row }) => <SourceLink source={sources.get(row.original.sourceId)} page={row.original.pdfPage} /> }
  ], [payment, sources])

  // The tiles describe the whole dataset, whichever record type is chosen.
  const allRows = data ? [...data.observations, ...data.payments] : []
  const allYears = allRows.map((row) => Number(row.year)).filter(Number.isFinite)
  const allMunicipalities = new Set(allRows.map((row) => row.municipality))
  const tiles = data ? [
    { label: 'Office figures', value: data.observations.length.toLocaleString('en-CA'), note: 'rates and reported pay' },
    { label: 'Named payments', value: data.payments.length.toLocaleString('en-CA'), note: 'to council members' },
    { label: 'Municipalities', value: allMunicipalities.size.toLocaleString('en-CA'), note: `${data.sources.length} sources` },
    { label: 'Years', value: allYears.length ? `${Math.min(...allYears)}–${Math.max(...allYears)}` : '—', note: `reviewed ${data.asOf}` }
  ] : []

  return (
    <CompanionShell
      browse="council" onBrowse={onBrowse}
      layout={layout} onLayout={(next) => update('layout', next)}
      query={query} onSearch={(value) => update('q', value)}
      searchLabel="Search council pay" searchHelp="Search a municipality, an official’s name or a source, such as “Saanich”, “Vancouver” or “CBC”."
      placeholder={payment ? 'Municipality, name or source' : 'Municipality or source'}
      heading="Council pay"
      intro={<p>Published mayor and councillor pay: office figures from surveys and salary schedules, and payments to named officials, each with its source. Amounts are in Canadian dollars as reported. Coverage is partial; an unlisted year or municipality means no record has been added here.</p>}
      tiles={tiles}
    >
      {failed ? <p className="salaries__hint" role="alert">Council pay could not be loaded. <button type="button" className="salaries__link" onClick={() => setAttempt((value) => value + 1)}>Retry</button></p> : !data ? <p className="salaries__hint" role="status">Loading council sources…</p> : <div className="council-pay">
        <Chips label="Record type" value={tab} onChange={(value) => update('councilTab', value)} options={[
          { value: 'rates', label: 'Office rates & reported pay', count: data.observations.length },
          { value: 'payments', label: 'Named payments', count: data.payments.length }
        ]} />
        <Chips label="Role" all="All roles" value={role} onChange={(value) => update('councilRole', value)} options={roleCounts.map(([name, total]) => ({ value: name, label: name, count: total }))} />
        <p className="salaries__meta council-pay__definition">{payment
          ? 'Amounts paid to named officials in the source year. Remuneration and expenses remain separate. Partial terms and extra duties can affect the amount; a payment does not establish a full-year salary.'
          : 'Figures attached to an office. A published survey figure and an annual base rate can use different definitions. Multiple sources for the same office and year remain visible; these figures are not assigned to a person.'}</p>
        <div className="council-pay__filters">
          <Filter label="Municipality" value={municipality} onChange={(value) => update('councilMunicipality', value)}><option value="all">All municipalities</option>{!municipalities.includes(municipality) && municipality !== 'all' && <option value={municipality}>{municipality}</option>}{municipalities.map((value) => <option key={value} value={value}>{value}</option>)}</Filter>
          <Filter label="Year" value={year} onChange={(value) => update('councilYear', value)}><option value="all">All source years</option>{!years.includes(year) && year !== 'all' && <option value={year}>{year} (no records)</option>}{years.map((value) => <option key={value} value={value}>{value}</option>)}</Filter>
          <div className="council-pay__actions"><button type="button" onClick={clear}>Clear filters</button><button type="button" disabled={!filtered.length} onClick={download}>Download these rows (CSV)</button></div>
        </div>
        <div className="council-pay__coverage" aria-label="Available years">
          <p><strong>{municipality === 'all' ? 'Years represented' : `${municipality}: years represented`}{role !== 'all' ? ` · ${role}` : ''}:</strong> {observed.years.length ? describeCouncilYears(observed.years) : 'No records added.'}</p>
          {observed.missing.length > 0 && <p>Gaps between those years: {describeCouncilYears(observed.missing)}.</p>}
          {series.length > 0 && <details><summary>Coverage by office and type of figure</summary><ul>{series.map((entry) => <li key={`${entry.role}-${entry.measure}`}><strong>{entry.role} · {councilMeasure(entry.measure)}:</strong> {entry.ranges}{entry.missingYears.length > 0 ? ` · Gaps: ${describeCouncilYears(entry.missingYears)}.` : ''}</li>)}</ul></details>}
          <p className="council-pay__muted">A represented year can contain only some offices or officials. Other years are unknown; missing amounts are never treated as zero.</p>
        </div>
        <div className="salaries__head">
          <h3 className="salaries__title">{payment ? 'Named payments' : 'Office figures'}</h3>
          <p className="salaries__meta" role="status">{count(filtered.length, payment ? 'payment' : 'figure', payment ? 'payments' : 'figures')} · newest first</p>
        </div>
        {!filtered.length
          ? <p className="salaries__hint">No source records match these filters. This does not indicate unpaid service. Try another year or municipality, or clear the filters.</p>
          : layout === 'table'
            ? <DataTable key={tab} data={filtered} columns={columns} sorting={[{ id: 'year', desc: true }]} label={payment ? 'Named council payments' : 'Council office figures'} rowHeight={52} />
            : <Paged list={filtered} size={24} reset={`${tab}|${query}|${municipality}|${year}|${role}`}>
              {(page) => <div className="salaries__grid">{page.map((row) => <CouncilCard key={row.id} row={row} tab={tab} source={sources.get(row.sourceId)} onEmployer={onEmployer} />)}</div>}
            </Paged>}
        <details className="council-pay__source-inventory">
          <summary>Historical coverage, held records and all sources</summary>
          <ul>{councilNotes(data.coverage?.notes).map((note, at) => <li key={at}>{note}</li>)}</ul>
          {(data.coverage?.held ?? []).map((held, at) => <p key={at}><strong>{held.municipality ? `${held.municipality} · ` : ''}{held.year}: held for verification.</strong> {held.reason} {councilSourceUrl(held.evidenceUrl) && <a href={councilSourceUrl(held.evidenceUrl)} target="_blank" rel="noreferrer">Read the correction evidence</a>}</p>)}
          <h3>Sources</h3>
          <ul>{data.sources.map((source) => <li key={source.id}><SourceLink source={source} /> <span className="council-pay__muted">({humanize(source.kind ?? 'Source')})</span>{councilNotes(source.notes).map((note, at) => <p key={at}>{note}</p>)}</li>)}</ul>
          <p><a href={`${BASE}salaries/council-pay.csv`} download>Download the complete council dataset (CSV)</a> · <a href={`${BASE}salaries/council-pay.json`} download>JSON with sources and coverage</a></p>
        </details>
      </div>}
    </CompanionShell>
  )
}
