import { useEffect, useMemo, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { councilCsv, councilMeasure, councilMoney, councilNotes, councilRows, councilSourceMap, councilSourceUrl, councilYearCoverage, describeCouncilYears, filterCouncilRows, loadCouncilPay } from './councilPay.js'
import './councilPay.css'

const BASE = import.meta.env?.BASE_URL ?? '/'
const BROWSE = [{ value: 'employers', label: 'Employers' }, { value: 'people', label: 'People' }, { value: 'positions', label: 'Positions' }, { value: 'council', label: 'Council pay' }]
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
  return <div className="council-pay__evidence">
    <p><SourceLink source={source} page={row.pdfPage} /></p>
    <p className="council-pay__muted">{humanize(source?.kind ?? 'Source')}</p>
    {row.sourceLocator && <p>{row.sourceLocator}</p>}
    {source?.locator && source.locator !== row.sourceLocator && <p className="council-pay__muted">{source.locator}</p>}
    {row.effectiveFrom && <p>Effective from {row.effectiveFrom}{row.effectiveTo ? ` to ${row.effectiveTo}` : ''}.</p>}
    {!row.effectiveFrom && row.effectiveTo && <p>Effective through {row.effectiveTo}.</p>}
    {row.effectiveDateNote && <p>{row.effectiveDateNote}</p>}
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

export default function CouncilPayView({ place, setPlace, onBrowse }) {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const [page, setPage] = useState(0)
  const tab = place.councilTab === 'payments' ? 'payments' : 'rates'
  const municipality = place.councilMunicipality || 'all'
  const year = place.councilYear || 'all'
  const role = place.councilRole || 'all'
  const query = place.q ?? ''

  useEffect(() => {
    const controller = new AbortController()
    setFailed(false)
    loadCouncilPay({ signal: controller.signal }).then((value) => { if (!controller.signal.aborted) setData(value) }, () => { if (!controller.signal.aborted) setFailed(true) })
    return () => controller.abort()
  }, [attempt])
  useEffect(() => setPage(0), [tab, municipality, year, role, query])

  const sources = useMemo(() => data ? councilSourceMap(data) : new Map(), [data])
  const rows = useMemo(() => data ? councilRows(data, tab) : [], [data, tab])
  const filtered = useMemo(() => filterCouncilRows(rows, { query, municipality, year, role }, sources), [rows, query, municipality, year, role, sources])
  const coverageRows = useMemo(() => filterCouncilRows(rows, { municipality, role }), [rows, municipality, role])
  const observed = useMemo(() => councilYearCoverage(coverageRows), [coverageRows])
  const municipalities = useMemo(() => [...new Set([...(data?.coverage?.municipalities ?? []).map((entry) => entry.municipality), ...rows.map((row) => row.municipality)])].sort((a, b) => a.localeCompare(b, 'en-CA')), [data, rows])
  const years = useMemo(() => [...new Set(rows.map((row) => String(row.year)))].sort((a, b) => b - a), [rows])
  const roles = useMemo(() => [...new Set(rows.map((row) => row.role))].sort(), [rows])
  const update = (key, value) => setPlace((current) => ({ ...current, [key]: value }))
  const clear = () => setPlace((current) => ({ ...current, q: '', councilMunicipality: 'all', councilYear: 'all', councilRole: 'all' }))
  const download = () => {
    const url = URL.createObjectURL(new Blob(['\uFEFF', councilCsv(filtered, tab, sources)], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `bc-council-${tab}-filtered.csv`
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  const pageCount = Math.ceil(filtered.length / 25)
  const currentPage = Math.min(page, Math.max(0, pageCount - 1))
  const shown = filtered.slice(currentPage * 25, (currentPage + 1) * 25)

  return <div className="salaries council-pay">
    <nav aria-label="Salary browsing"><Segmented ariaLabel="Browse" value="council" onChange={onBrowse} options={BROWSE} /></nav>
    <header className="council-pay__header">
      <p className="council-pay__eyebrow">Municipal government · British Columbia</p>
      <h2 className="salaries__heading">Council pay, through the years</h2>
      <p>Explore published mayor and councillor pay figures, annual salary schedules, and payments to named officials. Each observation retains its source and reporting definition.</p>
      <p className="council-pay__muted">Amounts are in Canadian dollars as reported. Coverage is partial; an unlisted year or municipality means no record has been added here.</p>
    </header>
    {failed ? <p role="alert">Council pay could not be loaded. <button type="button" onClick={() => setAttempt((value) => value + 1)}>Retry</button></p> : !data ? <p role="status">Loading council sources…</p> : <>
      <dl className="council-pay__stats">
        <div><dt>Office observations</dt><dd>{data.observations.length.toLocaleString('en-CA')}</dd></div>
        <div><dt>Named payments</dt><dd>{data.payments.length.toLocaleString('en-CA')}</dd></div>
        <div><dt>Sources</dt><dd>{data.sources.length}</dd></div>
        <div><dt>Reviewed</dt><dd className="council-pay__date">{data.asOf}</dd></div>
      </dl>
      <Segmented ariaLabel="Council record type" value={tab} onChange={(value) => update('councilTab', value)} options={[{ value: 'rates', label: 'Office rates & reported pay' }, { value: 'payments', label: 'Named payments' }]} />
      <p className="council-pay__definition">{tab === 'payments'
        ? 'Amounts paid to named officials in the source year. Remuneration and expenses remain separate. Partial terms and extra duties can affect the amount; a payment does not establish a full-year salary.'
        : 'Figures attached to an office. A published survey figure and an annual base rate can use different definitions. Multiple sources for the same office and year remain visible; these figures are not assigned to a person.'}</p>
      <div className="council-pay__filters">
        <label className="council-pay__filter council-pay__search"><span>Search {tab === 'payments' ? 'municipality, name or source' : 'municipality or source'}</span><input type="search" value={query} onChange={(event) => update('q', event.target.value)} placeholder={tab === 'payments' ? 'Vancouver, name, source…' : 'Saanich, Vancouver, CBC…'} /></label>
        <Filter label="Municipality" value={municipality} onChange={(value) => update('councilMunicipality', value)}><option value="all">All municipalities</option>{!municipalities.includes(municipality) && municipality !== 'all' && <option value={municipality}>{municipality}</option>}{municipalities.map((value) => <option key={value} value={value}>{value}</option>)}</Filter>
        <Filter label="Year" value={year} onChange={(value) => update('councilYear', value)}><option value="all">All source years</option>{!years.includes(year) && year !== 'all' && <option value={year}>{year} (no records)</option>}{years.map((value) => <option key={value} value={value}>{value}</option>)}</Filter>
        <Filter label="Role" value={role} onChange={(value) => update('councilRole', value)}><option value="all">All roles</option>{!roles.includes(role) && role !== 'all' && <option value={role}>{role}</option>}{roles.map((value) => <option key={value} value={value}>{value}</option>)}</Filter>
      </div>
      <div className="council-pay__coverage" aria-label="Available years">
        <p><strong>{municipality === 'all' ? 'Years represented in this tab' : `${municipality}: years represented`}{role !== 'all' ? ` · ${role}` : ''}:</strong> {observed.years.length ? describeCouncilYears(observed.years) : 'No records added.'}</p>
        {observed.missing.length > 0 && <p>Gaps between those years: {describeCouncilYears(observed.missing)}.</p>}
        <p className="council-pay__muted">A represented year can contain only some offices or officials. Other years are unknown; missing amounts are never treated as zero.</p>
      </div>
      <div className="council-pay__results-bar"><p role="status">{filtered.length.toLocaleString('en-CA')} {tab === 'payments' ? 'named payments' : 'office observations'} match</p><div><button type="button" onClick={clear}>Clear filters</button><button type="button" disabled={!filtered.length} onClick={download}>Download these rows (CSV)</button></div></div>
      {!filtered.length ? <p className="council-pay__empty">No source records match these filters. This does not indicate unpaid service. Try another year or municipality, or clear the filters.</p> : <div className="council-pay__table-wrap">
        <table className="council-pay__table">
          <caption>{tab === 'payments' ? 'Named council payments' : 'Council office observations'} · CAD · newest source years first</caption>
          <thead><tr><th scope="col">Municipality / year</th><th scope="col">{tab === 'payments' ? 'Official / role' : 'Office / measure'}</th><th scope="col">{tab === 'payments' ? 'Remuneration / expenses' : 'Reported amount'}</th><th scope="col">Source and qualifications</th></tr></thead>
          <tbody>{shown.map((row) => <tr key={row.id}>
            <th scope="row"><strong>{row.municipality}</strong><span className="council-pay__year">{row.year}</span></th>
            <td>{tab === 'payments' ? <><strong>{row.name}</strong><span className="council-pay__muted council-pay__block">{row.role}</span></> : <><strong>{row.role}</strong><span className="council-pay__muted council-pay__block">{councilMeasure(row.measure)}</span></>}</td>
            <td className="council-pay__amount">{tab === 'payments' ? <><span className="council-pay__amount-label">Remuneration</span><strong>{councilMoney(row.remuneration, row.currency)}</strong><span className="council-pay__amount-label">Expenses</span><span>{councilMoney(row.expenses, row.currency)}</span>{row.expenses == null && Number.isFinite(row.knownExpenses) && <span className="council-pay__muted council-pay__block">Known expense components: {councilMoney(row.knownExpenses, row.currency)}; total incomplete.</span>}</> : <><strong>{councilMoney(row.amount, row.currency)}</strong>{Number.isFinite(row.annualSupplement) && <><span className="council-pay__amount-label">Annual supplement (separate)</span><span>{councilMoney(row.annualSupplement, row.currency)}</span></>}</>}</td>
            <td><RecordDetails row={row} source={sources.get(row.sourceId)} /></td>
          </tr>)}</tbody>
        </table>
      </div>}
      {pageCount > 1 && <nav className="council-pay__pagination" aria-label="Council records pages"><button type="button" disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>Previous</button><span>Page {currentPage + 1} of {pageCount}</span><button type="button" disabled={currentPage + 1 >= pageCount} onClick={() => setPage(currentPage + 1)}>Next</button></nav>}
      <details className="council-pay__source-inventory">
        <summary>Historical coverage, held records and all sources</summary>
        <ul>{councilNotes(data.coverage?.notes).map((note, at) => <li key={at}>{note}</li>)}</ul>
        {(data.coverage?.held ?? []).map((held, at) => <p key={at}><strong>{held.municipality ? `${held.municipality} · ` : ''}{held.year}: held for verification.</strong> {held.reason} {councilSourceUrl(held.evidenceUrl) && <a href={councilSourceUrl(held.evidenceUrl)} target="_blank" rel="noreferrer">Read the correction evidence</a>}</p>)}
        <h3>Sources</h3>
        <ul>{data.sources.map((source) => <li key={source.id}><SourceLink source={source} /> <span className="council-pay__muted">({humanize(source.kind ?? 'Source')})</span>{councilNotes(source.notes).map((note, at) => <p key={at}>{note}</p>)}</li>)}</ul>
        <p><a href={`${BASE}salaries/council-pay.csv`} download>Download the complete council dataset (CSV)</a> · <a href={`${BASE}salaries/council-pay.json`} download>JSON with sources and coverage</a></p>
      </details>
    </>}
  </div>
}
