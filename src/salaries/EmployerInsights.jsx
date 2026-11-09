import { useEffect, useState } from 'react'
import { count, loadJson } from './common.jsx'
import { CURRENT_WINDOW_DAYS, currentSince, employerRanking, isCurrent, MIN_EMPLOYER_RECORDS, MIN_RANKED_STAYERS, MIN_STAYERS } from './employerStats.js'
import { formatSummaryMoney as formatMoney } from './money.js'
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
  { value: 'raise', label: 'Highest typical raise' },
  { value: 'growth', label: 'Most added to the list' }
]

const highlights = [
  { metric: 'median', label: 'Highest median pay', format: formatMoney },
  { metric: 'mean', label: 'Highest average pay', format: formatMoney },
  { metric: 'raise', label: 'Highest typical raise', format: employerRate }
]

const detail = (metric, stats, years) => {
  if (metric === 'growth') return `${years[stats.from]} → ${years[stats.year]} · ${stats.previousCount.toLocaleString('en-CA')} → ${stats.count.toLocaleString('en-CA')} records`
  if (metric === 'raise') return `${years[stats.raiseFrom]} → ${years[stats.year]} · ${count(stats.stayers, 'name on both lists', 'names on both lists')}`
  return `${years[stats.year]} · ${count(stats.count, 'employee record', 'employee records')}`
}

export const EmployerInsights = ({ rows, years, ready, failed, onRetry, onOpen, onOrder }) => {
  const since = currentSince(rows)
  const older = rows.filter(({ stats }) => stats && stats.count >= MIN_EMPLOYER_RECORDS && !isCurrent(stats, since)).length
  return (
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
            const positive = !['growth', 'raise'].includes(metric) || winner?.stats[metric] > 0
            return (
              <div key={metric} className="employer-insights__tile">
                <button type="button" className="salaries__link employer-insights__label" onClick={() => onOrder(metric)}>{label} <span aria-hidden="true">→</span></button>
                {winner && positive
                  ? <>
                    <strong className="employer-insights__value">{format(winner.stats[metric])}</strong>
                    <button type="button" className="salaries__link employer-insights__name" onClick={() => onOpen(winner.entry.slug, years[winner.stats.year])}>{winner.name}</button>
                    <span className="salaries__line">{detail(metric, winner.stats, years)}</span>
                    {winner.stats.threshold !== 75000 && <span className="salaries__line">Reporting threshold {formatMoney(winner.stats.threshold, 'not specified')}</span>}
                  </>
                  : <p className="salaries__meta">{metric === 'raise' ? 'No comparable raises in this selection.' : 'No eligible employee disclosures in this selection.'}</p>}
              </div>
            )
          })}
        </div>}
    {ready && older > 0 && <p className="salaries__meta employer-insights__older">{count(older, 'organization is', 'organizations are')} not ranked because {older === 1 ? 'its' : 'their'} latest disclosure in this selection is more than {Math.round(CURRENT_WINDOW_DAYS / 365 * 12)} months older than the newest. Choose a period range to compare older years.</p>}
    <details className="employer-insights__definitions">
      <summary>What these statistics cover</summary>
      <p>Amounts are CAD remuneration in official annual employee schedules, which list employees paid more than $75,000 unless a card says otherwise. Council, board, executive-only, compiled and incomplete schedules are excluded. Median and average describe the disclosed records, including any part-year payments; they are not annual salary rates. These organization-level figures combine different roles.</p>
      <p>Typical raise is the median change in pay for names on both of two consecutive annual lists with the same threshold and period rules, at least {MIN_STAYERS} of them ({MIN_RANKED_STAYERS} to be ranked). A promotion, a part year or retroactive pay from a settled contract shows as a raise or a cut; a shared name is not proof of one person.</p>
      <p>The $75,000 Financial Information Act threshold has not changed since 2002 and is not indexed to inflation, so as pay rises more employees cross it each year. That is why “Most added to the list” counts published records, not employees or new hires, and why an employer’s median can fall while nearly everyone on its list got a raise.</p>
      <p>Rankings require at least {MIN_EMPLOYER_RECORDS} records, and leave out organizations whose latest disclosure is much older than the rest. Reporting thresholds can differ across organizations. Filter to the same period and sector for a closer comparison; open an employer to inspect its source reports.</p>
    </details>
  </section>
  )
}
