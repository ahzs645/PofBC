import { useEffect, useState } from 'react'
import { count, loadJson } from './common.jsx'
import { CURRENT_WINDOW_DAYS, currentSince, employerRanking, isCurrent, MIN_EMPLOYER_RECORDS } from './employerStats.js'
import { formatSummaryMoney as formatMoney } from './money.js'
import { SiteLink } from '../site/navigation.jsx'
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
    {ready && older > 0 && <p className="salaries__meta employer-insights__older">{count(older, 'organization', 'organizations')} not ranked: latest disclosure over {Math.round(CURRENT_WINDOW_DAYS / 365 * 12)} months older than the newest.</p>}
    <p className="salaries__meta employer-insights__definitions">
      Figures describe the disclosed records, not salary rates.{' '}
      <SiteLink to={{ view: 'salaries', browse: 'about' }} className="salaries__link">How they are worked out</SiteLink>
    </p>
  </section>
  )
}
