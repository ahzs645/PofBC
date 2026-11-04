import { useEffect, useId, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { formatWorkforceNumber, formatWorkforceSalary, loadWorkforce, normalizeWorkforcePopulation, selectWorkforceRows, workforceAssetUrl } from './workforce.js'
import './workforce.css'

const BROWSE = [
  { value: 'employers', label: 'Employers' },
  { value: 'people', label: 'People' },
  { value: 'positions', label: 'Positions' },
  { value: 'council', label: 'Council pay' },
  { value: 'workforce', label: 'Workforce' },
]

function MeasureChart({ rows, measure, label, format }) {
  const id = useId()
  const width = 520
  const height = 224
  const left = 62
  const right = 14
  const top = 34
  const bottom = 42
  const plotHeight = height - top - bottom
  const maximum = Math.ceil(Math.max(...rows.map(row => row[measure])) / (measure === 'averageSalary' ? 10000 : 5000)) * (measure === 'averageSalary' ? 10000 : 5000)
  const step = (width - left - right) / rows.length
  return (
    <figure className="workforce__chart">
      <figcaption>{label}</figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby={`${id}-title ${id}-desc`}>
        <title id={`${id}-title`}>{label} by year label</title>
        <desc id={`${id}-desc`}>The vertical scale begins at zero. Exact values and source links are in the table below. Reporting periods and calculation methods are unverified.</desc>
        {[0, maximum / 2, maximum].map(value => {
          const y = top + plotHeight * (1 - value / maximum)
          return <g key={value} className="workforce__chart-grid"><line x1={left} y1={y} x2={width - right} y2={y} /><text x={left - 8} y={y + 4} textAnchor="end">{format(value)}</text></g>
        })}
        {rows.map((row, index) => {
          const x = left + step * index + step / 2
          const barHeight = plotHeight * row[measure] / maximum
          return (
            <g key={row.yearLabel}>
              <rect className={`workforce__bar workforce__bar--${measure}`} x={x - step * 0.29} y={top + plotHeight - barHeight} width={step * 0.58} height={barHeight} rx="2" />
              <text className="workforce__chart-value" x={x} y={top + plotHeight - barHeight - 7} textAnchor="middle">{format(row[measure])}</text>
              <text className="workforce__chart-year" x={x} y={height - bottom + 20} textAnchor="middle">{row.yearLabel}</text>
            </g>
          )
        })}
        <text className="workforce__chart-axis" x={(left + width - right) / 2} y={height - 3} textAnchor="middle">Year label</text>
      </svg>
    </figure>
  )
}

function WorkforceContent({ data, place, setPlace }) {
  const populationId = normalizeWorkforcePopulation(place?.workforcePopulation)
  const population = data.populations.find(item => item.id === populationId)
  const rows = selectWorkforceRows(data, populationId)
  const latest = rows.at(-1)
  const sourcePageUrl = `${data.source.url}#page=${population.sourcePage}`
  return (
    <>
      <div className="workforce__controls">
        <label className="workforce__population">
          <span>Population</span>
          <select value={populationId} onChange={event => setPlace(current => ({ ...current, workforcePopulation: event.target.value }))}>
            {data.populations.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
        </label>
        <div className="workforce__downloads" aria-label="Download complete workforce data">
          <a href={workforceAssetUrl('csv')} download="bc-public-service-workforce.csv">Download CSV</a>
          <a href={workforceAssetUrl('json')} download="bc-public-service-workforce.json">Download JSON</a>
        </div>
      </div>
      <p className="workforce__scope">{populationId === 'victoria' ? 'Employees whose office is located in Victoria are included in the all-employees figures. The two populations overlap and must not be added.' : 'The release describes this population as all BC Public Service employees. It does not cover the entire B.C. public sector.'} Downloads include both populations.</p>
      <section aria-labelledby="workforce-latest-heading">
        <h3 id="workforce-latest-heading" className="workforce__section-heading">Latest year label in this release: {latest.yearLabel}</h3>
        <dl className="workforce__stats">
          <div><dt>Average HeadCount</dt><dd>{formatWorkforceNumber(latest.averageHeadCount)}</dd></div>
          <div><dt>Average Salary</dt><dd>{formatWorkforceSalary(latest.averageSalary)}</dd></div>
        </dl>
      </section>
      <aside className="workforce__note" aria-label="How to read these figures">
        <strong>Read these as the release’s own measures.</strong> “Average HeadCount” and “Average Salary” retain the original labels. The release does not explain their calculation methods or the start and end of each reporting period. The salary figure cannot yet be compared directly with an average of annual payment records.
      </aside>
      <div className="workforce__charts">
        <MeasureChart rows={rows} measure="averageHeadCount" label="Average HeadCount" format={formatWorkforceNumber} />
        <MeasureChart rows={rows} measure="averageSalary" label="Average Salary" format={formatWorkforceSalary} />
      </div>
      <div className="workforce__table-wrap">
        <table className="workforce__table">
          <caption>{population.label} · <a href={sourcePageUrl} target="_blank" rel="noreferrer">Official table, PDF page {population.sourcePage}</a></caption>
          <thead><tr><th scope="col">Year label</th><th scope="col">Average HeadCount</th><th scope="col">Average Salary</th></tr></thead>
          <tbody>{rows.map(row => <tr key={row.yearLabel}><th scope="row">{row.yearLabel}</th><td>{formatWorkforceNumber(row.averageHeadCount)}</td><td>{formatWorkforceSalary(row.averageSalary)}</td></tr>)}</tbody>
        </table>
      </div>
      {populationId === 'victoria' && <p className="workforce__anomaly"><strong>2019 is reproduced as printed.</strong> The Victoria “Average HeadCount” of 21,405 appears on both pages 3 and 4. The release does not explain its increase or the decrease in 2020.</p>}
      <section className="workforce__provenance" aria-labelledby="workforce-source-heading">
        <h3 id="workforce-source-heading">Source and interpretation</h3>
        <p><a href={data.source.url} target="_blank" rel="noreferrer">Official response package {data.source.id}</a> · Government of British Columbia</p>
        <p className="workforce__source-label">Source population description: “{population.sourceLabel}”.</p>
        <ul>
          <li><a href={`${data.source.url}#page=1`} target="_blank" rel="noreferrer">Page 1</a> gives the all-employees table. <a href={`${data.source.url}#page=3`} target="_blank" rel="noreferrer">Page 3</a> gives the Victoria-office table. Pages 2 and 4 repeat those values alongside charts; each population and year appears here once.</li>
          <li>Year labels are preserved as printed. Calendar-year, fiscal-year and partial-year interpretations have not been established.</li>
          <li>“Average Salary” could represent annualized rates, actual earnings or another payroll measure. The released table does not settle that question. Dollar amounts are shown as printed; Canadian dollars are inferred from the B.C. government context.</li>
          <li>These are aggregate statistics. They are separate from PofBC’s named payment records and the government’s fiscal-year FTE series.</li>
          <li>A fixed disclosure threshold can bring more people into a published payment list as pay rises. The number of disclosed records alone does not establish workforce growth.</li>
        </ul>
      </section>
    </>
  )
}

export default function WorkforceView({ place, setPlace, onBrowse }) {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setFailed(false)
    loadWorkforce({ signal: controller.signal }).then(
      value => { if (!controller.signal.aborted) setData(value) },
      () => { if (!controller.signal.aborted) setFailed(true) },
    )
    return () => controller.abort()
  }, [attempt])
  return (
    <div className="salaries workforce">
      <nav aria-label="Salary browsing"><Segmented ariaLabel="Browse" value="workforce" onChange={onBrowse} options={BROWSE} /></nav>
      <header className="workforce__header">
        <p className="workforce__eyebrow">BC Public Service · Workforce statistics</p>
        <h2 className="salaries__heading">The workforce beyond the payment lists</h2>
        <p>Explore the “Average HeadCount” and “Average Salary” reported in an official B.C. freedom of information release, with year labels from 2017 to 2024.</p>
      </header>
      {failed ? <div className="workforce__error" role="alert"><p>Workforce statistics could not be loaded.</p><button type="button" onClick={() => setAttempt(value => value + 1)}>Try again</button></div> : !data ? <p role="status">Loading workforce statistics…</p> : <WorkforceContent data={data} place={place} setPlace={setPlace} />}
    </div>
  )
}
