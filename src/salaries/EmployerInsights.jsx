import { useEffect, useState } from 'react'
import { count, loadJson } from './common.jsx'
import { employerRanking, MIN_EMPLOYER_RECORDS } from './employerStats.js'
import { formatMoney } from './money.js'
import './employerInsights.css'

export const employerRate = (value) => value == null ? '—' : new Intl.NumberFormat('en-CA', {
  style: 'percent', maximumFractionDigits: 1, signDisplay: 'exceptZero'
}).format(value)

export const useEmployerStatistics = (years) => {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let live = true
    setFailed(false)
    loadJson(`salaries/employer-stats.json.gzip${attempt ? `?retry=${attempt}` : ''}`).then((result) => {
      if (!live) return
      if (!result || result.schemaVersion !== 1 || !result.employers || JSON.stringify(result.years) !== JSON.stringify(years)) {
        setFailed(true)
        return
      }
      setData(result.employers)
    }, () => { if (live) setFailed(true) })
    return () => { live = false }
  }, [attempt, years])
  return { data, failed, retry: () => setAttempt((value) => value + 1) }
}

export const EMPLOYER_ORDERS = [
  { value: 'sector', label: 'By sector' },
  { value: 'count', label: 'Most employee records' },
  { value: 'median', label: 'Highest median pay' },
  { value: 'mean', label: 'Highest average pay' },
  { value: 'growth', label: 'Fastest disclosure growth' },
  { value: 'total', label: 'Largest disclosed payroll' }
]

const highlights = [
  { metric: 'median', label: 'Highest median pay', format: formatMoney },
  { metric: 'mean', label: 'Highest average pay', format: formatMoney },
  { metric: 'growth', label: 'Fastest disclosure growth', format: employerRate },
  { metric: 'total', label: 'Largest disclosed payroll', format: (value) => new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD', notation: 'compact', maximumFractionDigits: 2 }).format(value) }
]

export const EmployerInsights = ({ rows, years, ready, failed, onRetry, onOpen, onOrder }) => (
  <section className="employer-insights" aria-labelledby="employer-insights-heading">
    <h3 id="employer-insights-heading" className="salaries__title">Across organizations</h3>
    <p className="salaries__meta">Latest official employee disclosure in the selected periods and sector.</p>
    {failed
      ? <p className="salaries__hint" role="alert">Organization statistics could not be loaded. <button type="button" className="salaries__link" onClick={onRetry}>Retry statistics</button></p>
      : !ready
        ? <p className="salaries__hint" role="status">Loading organization statistics…</p>
        : <div className="employer-insights__grid">
          {highlights.map(({ metric, label, format }) => {
            const winner = employerRanking(rows, metric)[0]
            const positive = metric !== 'growth' || winner?.stats.growth > 0
            return (
              <div key={metric} className="employer-insights__tile">
                <button type="button" className="salaries__link employer-insights__label" onClick={() => onOrder(metric)}>{label} <span aria-hidden="true">→</span></button>
                {winner && positive
                  ? <>
                    <strong className="employer-insights__value" title={metric === 'total' ? formatMoney(winner.stats.total) : undefined}>{format(winner.stats[metric])}</strong>
                    <button type="button" className="salaries__link employer-insights__name" onClick={() => onOpen(winner.entry.slug, years[winner.stats.year])}>{winner.name}</button>
                    <span className="salaries__line">{metric === 'growth' ? `${years[winner.stats.from]} → ${years[winner.stats.year]} · ${winner.stats.previousCount.toLocaleString('en-CA')} → ${winner.stats.count.toLocaleString('en-CA')} records` : `${years[winner.stats.year]} · ${count(winner.stats.count, 'employee record', 'employee records')}`}</span>
                    <span className="salaries__line">Reporting threshold {formatMoney(winner.stats.threshold, 'not specified')}</span>
                  </>
                  : <p className="salaries__meta">{metric === 'growth' ? 'No comparable increase in this selection.' : 'No eligible employee disclosures in this selection.'}</p>}
              </div>
            )
          })}
        </div>}
    <details className="employer-insights__definitions">
      <summary>What these statistics cover</summary>
      <p>Amounts are CAD remuneration in official annual employee schedules. Council, board, executive-only, compiled and incomplete schedules are excluded. Median, average and payroll describe the disclosed records, including any part-year payments; they are not annual salary rates or the organization’s complete payroll.</p>
      <p>Disclosure growth counts published employee records, not total employees or new hires. It compares consecutive annual periods only when the recorded scope, threshold and boundary rule match, with unique disclosed names and at least {MIN_EMPLOYER_RECORDS} records in each. Pay increases can move more employees above a reporting threshold.</p>
      <p>Rankings require at least {MIN_EMPLOYER_RECORDS} records. Latest periods and reporting thresholds can differ across organizations. Filter to the same period and sector for a closer comparison; open an employer to inspect its source reports.</p>
    </details>
  </section>
)
