// What a body took in and spent, as the Province's Public Accounts publish it, in the panel's card
// style. Built like the Salaries card: the index (financeIndex.js) says which bodies have anything;
// a body's records (public/finance/<id>.json) are fetched when its panel opens. They are, each from
// its own source and cited to its page:
//
//   * a ministry's or office's votes, estimates against actual (MoneyParts.jsx, BudgetActual);
//   * revenue by source and expense from the body's own statement of operations (Breakdown);
//   * cash paid to it by ministries, from the Government Transfers schedule (FromMinistries);
//   * the Adjusted Net Income table, in $ millions as printed, and the list of its statements.
//
// Nothing is restated, adjusted for inflation or added across bodies. Each body's figures are its own
// gross figures; money passing between government bodies is counted by each, which is why they must
// not be summed.

import { useEffect, useMemo, useState } from 'react'
import { FINANCE_INDEX, FINANCE_SOURCES } from './financeIndex.js'
import { SourceList } from '../site/SourceList.jsx'
import { Breakdown, BudgetActual, FromMinistries } from './MoneyParts.jsx'
import './money.css'

const fetched = new Map()
const load = (id) => {
  const url = `${import.meta.env?.BASE_URL ?? '/'}finance/${id}.json`
  if (!fetched.has(url)) fetched.set(url, fetch(url)
    .then((response) => (response.ok ? response.json() : Promise.reject(new Error(response.status))))
    .catch((error) => { fetched.delete(url); throw error }))
  return fetched.get(url)
}

/** A figure as the table prints it: brackets for a negative, a blank cell left blank. */
const printed = (value) => (value === null || value === undefined ? '' : value < 0 ? `(${Math.abs(value).toLocaleString('en-CA')})` : value.toLocaleString('en-CA'))
const pageUrl = (source) => `${source.url}#page=${source.pdfPage}`
const fyLabel = (year) => `${year.slice(0, 4)}/${year.slice(5)}`
const STATEMENTS_SHOWN = 6

/** Bodies the table reports only inside a sector total. */
const SECTOR_KINDS = {
  'health-authority': 'health authorities',
  'public-university': 'universities',
  'public-institute': 'colleges and institutes',
  'school-district': 'school districts',
  'francophone-school-district': 'school districts',
  'affiliated-health-society': 'hospital societies'
}

/** Revenue and expense year by year, as paired bars: a picture of the table below, which holds the figures. */
const Bars = ({ rows }) => {
  const years = [...rows].reverse()
  const max = Math.max(1, ...years.flatMap((row) => [Math.abs(row.figures.revenue ?? 0), Math.abs(row.figures.expense ?? 0)]))
  const step = 10
  const height = 56
  const bar = (value) => (Math.abs(value ?? 0) / max) * height
  return (
    <svg className="gov-money__bars" viewBox={`0 0 ${years.length * step} ${height}`} preserveAspectRatio="none" aria-hidden="true">
      {years.map((row, at) => (
        <g key={`${row.year}-${row.basis}`}>
          <rect className="gov-money__bar gov-money__bar--revenue" x={at * step + 1} width="3.6" y={height - bar(row.figures.revenue)} height={bar(row.figures.revenue)} />
          <rect className="gov-money__bar gov-money__bar--expense" x={at * step + 5} width="3.6" y={height - bar(row.figures.expense)} height={bar(row.figures.expense)} />
        </g>
      ))}
    </svg>
  )
}

/** Which heading the fifth column had, year by year, for this body's rows. */
const fifthHeadings = (rows) => {
  const runs = []
  for (const row of [...rows].reverse()) {
    const label = row.headings[4]
    if (runs.at(-1)?.label === label) runs.at(-1).to = row.year
    else runs.push({ label, from: row.year, to: row.year })
  }
  return runs
}

export const Money = ({ node, year }) => {
  const entry = FINANCE_INDEX[node.id]
  const [state, setState] = useState({ status: 'idle' })
  const [version, setVersion] = useState(0)
  const [allStatements, setAllStatements] = useState(false)

  useEffect(() => { setAllStatements(false) }, [node.id])
  useEffect(() => {
    if (!entry) return undefined
    let live = true
    setState({ status: 'loading' })
    load(node.id).then((data) => live && setState({ status: 'ready', data }), () => live && setState({ status: 'failed' }))
    return () => { live = false }
  }, [node.id, entry, version])

  const rows = state.data?.table ?? []
  const statements = state.data?.statements ?? []
  const breakdowns = state.data?.breakdowns ?? []
  const transfers = state.data?.transfers ?? []
  const estimates = state.data?.estimates ?? []
  const statementProvince = useMemo(() => Object.fromEntries(breakdowns.map((record) => [record.year, record.revenue.filter((line) => line.category === 'province').reduce((sum, line) => sum + line.amount, 0)])), [breakdowns])
  const showFifth = rows.some((row) => row.figures.fifth !== null)
  const runs = useMemo(() => fifthHeadings(rows), [rows])
  const notes = useMemo(() => {
    const byText = new Map()
    for (const row of rows) for (const note of row.notes ?? []) {
      if (!byText.has(note.text)) byText.set(note.text, [])
      byText.get(note.text).push(fyLabel(row.year))
    }
    return [...byText.entries()]
  }, [rows])

  if (!entry) return null
  const heading = `money-${node.id}`
  const latestName = rows[0]?.name
  const twice = new Set(rows.filter((row, at) => rows.findIndex((other) => other.year === row.year) !== at).map((row) => row.year))
  const sector = SECTOR_KINDS[node.kind]
  const shownStatements = allStatements ? statements : statements.slice(0, STATEMENTS_SHOWN)
  const onScreen = (row) => Number(row.year.slice(0, 4)) + 1 === Number(year)

  return (
    <section className="gov-card gov-money" aria-labelledby={heading}>
      <h2 id={heading} className="gov-card__heading">Money</h2>
      {state.status === 'loading' && <p className="gov-muted" role="status">Loading the Public Accounts records…</p>}
      {state.status === 'failed' && <p className="gov-muted" role="alert">The Public Accounts records could not be loaded. <button type="button" onClick={() => setVersion((value) => value + 1)}>Retry</button></p>}
      {state.status === 'ready' && <>
        {estimates.length > 0 && <BudgetActual records={estimates} calendarYear={year} />}
        {breakdowns.length > 0 && <Breakdown records={breakdowns} calendarYear={year} />}
        {transfers.length > 0 && <FromMinistries records={transfers} calendarYear={year} statementProvince={statementProvince} />}
        {rows.length > 0 && <h3 className="gov-card__subheading gov-money__table-heading">Adjusted Net Income table</h3>}
        {rows.length > 0 ? <>
          <p className="gov-money__about">
            As published in the Public Accounts’ table <em>Adjusted Net Income of Crown Corporations, Agencies and the SUCH Sector</em>:
            {' '}<strong>$ millions</strong>, fiscal years ending 31 March, unaudited, {rows.length === 1 ? 'one year' : `${rows.length} years`} from {fyLabel(rows.at(-1).year)} to {fyLabel(rows[0].year)}.
          </p>
          {rows.length > 1 && <figure className="gov-money__chart">
            <Bars rows={rows} />
            <figcaption className="gov-money__legend">
              <span><i className="gov-money__swatch gov-money__swatch--revenue" />Revenue</span>
              <span><i className="gov-money__swatch gov-money__swatch--expense" />Expense</span>
              <span className="gov-muted">{fyLabel(rows.at(-1).year)} → {fyLabel(rows[0].year)}</span>
            </figcaption>
          </figure>}
          <div className="gov-money__scroll" tabIndex={0} role="region" aria-label={`${node.name}: revenue, expense and net income by fiscal year, $ millions`}>
            <table className="gov-money__table">
              <thead>
                <tr>
                  <th scope="col">Fiscal year</th>
                  <th scope="col">Revenue</th>
                  <th scope="col">Expense</th>
                  <th scope="col">Net income</th>
                  {showFifth && <th scope="col">{runs.length === 1 ? runs[0].label : 'Col. 5*'}</th>}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={`${row.year}-${row.basis}`} className={onScreen(row) ? 'gov-money__current' : undefined}>
                    <th scope="row">
                      <a href={pageUrl(row.source)} target="_blank" rel="noreferrer" title={`Public Accounts ${fyLabel(row.year)}, Supplementary Information, PDF page ${row.source.pdfPage}${row.source.printedPage ? ` (printed page ${row.source.printedPage})` : ''}`}>{fyLabel(row.year)}</a>
                      {twice.has(row.year) && <span className="gov-money__tag">{row.basis}</span>}
                      {row.name !== latestName && <span className="gov-money__tag">as {row.name}</span>}
                    </th>
                    <td>{printed(row.figures.revenue)}</td>
                    <td>{printed(row.figures.expense)}</td>
                    <td>{printed(row.figures.netIncome)}</td>
                    {showFifth && <td>{printed(row.figures.fifth)}</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {showFifth && runs.length > 1 && <p className="gov-muted gov-money__note">* The fifth column is printed as {runs.map((run) => `“${run.label}” (${fyLabel(run.from)}${run.to !== run.from ? `–${fyLabel(run.to)}` : ''})`).join(', ')}.</p>}
          <p className="gov-muted gov-money__note">Each year links to its page in the Public Accounts. Blank cells are blank in the table. Expense is printed in brackets, as the table prints it. {rows[0].basis === 'self-supported' ? 'Self-supported Crown corporations are recorded on a modified equity basis; their net income, not their revenue, enters the Province’s accounts.' : ''}</p>
          {notes.length > 0 && <ul className="gov-money__notes">
            {notes.map(([text, years]) => <li key={text}><span className="gov-muted">{years.join(', ')}:</span> {text}</li>)}
          </ul>}
        </> : statements.length > 0 && <p className="gov-money__about">
          The Public Accounts’ <em>Adjusted Net Income</em> table has no row of its own for this body{sector ? `: it reports ${sector} only as a sector total, which is not divided among them here` : ''}. Its published financial statements are listed below.
        </p>}

        {(rows.length > 0 || breakdowns.length > 0 || transfers.length > 0) && <p className="gov-money__warning">These are this body’s own figures. Money passing between government bodies — a ministry’s grant, or one body paying another — is counted in each body’s figures, so they must not be added across bodies. The Province’s Summary Financial Statements remove those transfers; these figures do not.</p>}

        {statements.length > 0 && <div className="gov-money__statements">
          <h3 className="gov-card__subheading">Financial statements <span className="gov-muted">{statements.length}</span></h3>
          <p className="gov-muted gov-money__note">Audited statements the Province lists with each year’s Public Accounts. A statement’s own year end can differ from 31 March; the statement says which.</p>
          <ul className="gov-money__list">
            {shownStatements.map((statement, at) => (
              <li key={`${statement.year}-${statement.url}`}>
                <a href={statement.url} target="_blank" rel="noreferrer">{fyLabel(statement.year)}<span aria-hidden="true"> ↗</span></a>
                <span className="gov-muted">
                  {/* The published name on the newest statement and wherever it changes, not on every year. */}
                  {[statement.name !== node.name && (at === 0 || statement.name !== shownStatements[at - 1].name) ? statement.name : null, statement.basis === 'self-supported' ? 'self-supported' : null, statement.hosted === 'ministry page' ? 'ministry page' : null].filter(Boolean).join(' · ')}
                </span>
              </li>
            ))}
          </ul>
          {statements.length > STATEMENTS_SHOWN && <button type="button" className="gov-show-more" onClick={() => setAllStatements((value) => !value)}>
            {allStatements ? 'Show fewer' : `Show all ${statements.length}`}
          </button>}
        </div>}
        <div className="gov-money__sources">
          <h3 className="gov-card__subheading">Sources</h3>
          <SourceList sources={[
            ...(estimates.length ? [{ ...FINANCE_SOURCES.votes, locator: 'Each year’s CRF Supplementary Schedules PDF; every vote links to its page' }] : []),
            ...(breakdowns.length ? breakdowns.map((record) => ({ key: record.url, url: `${record.url}#page=${record.page.pdf}`, title: `${record.title || 'Statement of operations'}, ${fyLabel(record.year)}`, locator: `PDF page ${record.page.pdf}${record.page.printed ? `, printed page ${record.page.printed}` : ''}` })) : []),
            ...(transfers.length ? [{ ...FINANCE_SOURCES.transfers, locator: 'One CSV per fiscal year; payees matched to this body by name' }] : []),
            ...(rows.length ? [{ ...FINANCE_SOURCES.table, locator: 'Each year’s Supplementary Information PDF; every figure links to its page' }] : []),
            ...(statements.length ? [{ ...FINANCE_SOURCES.statements, locator: 'Financial statements of the government reporting entity, by sector' }] : []),
            ...(statements.some((statement) => statement.hosted === 'ministry page') ? [FINANCE_SOURCES.postSecondary] : [])
          ]} />
        </div>
      </>}
    </section>
  )
}
