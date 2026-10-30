// Small pieces the salary views share with the government panel's salary card: which years a name or
// an employer has records in, a year picker that shows how many each holds, and a person's pay by
// year. Each is styled in site.css (.salaries-strip, .salaries-picker, .salaries-chart) with the
// government view's colours where it sits inside that view.

import { formatMoney } from './money.js'
import { yearAvailability, shortYearLabel, reportingYearLabel, relevantYearIndexes, samePeriodKinds } from './coverage.js'

/** "2012/13–2023/24", or one label when the range is a single year. */
export const yearSpan = (labels) => (labels.length > 1 ? `${labels[0]}–${labels.at(-1)}` : labels[0] ?? '')

/** Short year label for tight spaces: "2023/24" → "23/24". */
export const shortYear = shortYearLabel

/**
 * One mark per collection year, filled where there are records: the shape of a history at a glance,
 * in the room of a line of text. `seen` is a list of year indexes.
 */
export const YearStrip = ({ years, seen, coverage = [], children }) => {
  const set = new Set(seen)
  const labels = years.filter((_, at) => set.has(at))
  const eligible = new Set(coverage.length ? relevantYearIndexes(years, coverage, years.map((_, at) => set.has(at) ? 1 : 0)) : samePeriodKinds(years, seen))
  return (
    <span className="salaries-strip">
      <span className="salaries-strip__marks" role="img" aria-label={`Records in ${labels.length} of ${eligible.size} reporting periods${labels.length ? `, ${yearSpan(labels)}` : ''}`}>
        {years.map((label, at) => eligible.has(at) ? <span key={label} data-seen={set.has(at) || undefined} title={reportingYearLabel(label)} /> : null)}
      </span>
      <span className="salaries-strip__text">{children ?? `${labels.length} ${labels.length === 1 ? 'period' : 'periods'}${labels.length ? ` · ${yearSpan(labels)}` : ''}`}</span>
    </span>
  )
}

/**
 * The years as a row of bars, each as tall as its record count and each a button that picks it. A
 * year without records is a dashed stub: still a button, since choosing it explains the gap.
 */
export const YearPicker = ({ years, counts, coverage = [], value, onChange, label = 'Disclosure period' }) => {
  const most = Math.max(1, ...counts)
  const visible = new Set([...relevantYearIndexes(years, coverage, counts), value])
  return (
    <div className="salaries-picker-wrap">
      <label className="salaries-picker-select">
        <span>{label}</span>
        <select value={value} onChange={(event) => onChange(Number(event.target.value))}>
          {years.map((year, at) => visible.has(at) ? <option key={year} value={at}>{reportingYearLabel(year)} · {yearAvailability(coverage[at], counts[at] ?? 0)}</option> : null)}
        </select>
      </label>
    <div className="salaries-picker" role="group" aria-label={label}>
      {years.map((year, at) => {
        if (!visible.has(at)) return null
        const count = counts[at] ?? 0
        return (
          <button
            key={year}
            type="button"
            aria-pressed={at === value}
            data-empty={!count || undefined}
            data-status={coverage[at]?.status}
            aria-label={`${reportingYearLabel(year)}: ${yearAvailability(coverage[at], count)}`}
            title={`${reportingYearLabel(year)}: ${yearAvailability(coverage[at], count)}`}
            onClick={() => onChange(at)}
          >
            <span className="salaries-picker__bar"><span style={{ height: count ? `${Math.max(8, (count / most) * 100)}%` : undefined }} /></span>
            <span className="salaries-picker__label">{shortYear(year)}</span>
          </button>
        )
      })}
    </div>
    </div>
  )
}

/**
 * Pay by year as bars, from the first year with a record to the last; a year between with none is
 * left empty rather than drawn as zero. The table under it carries the same figures for reading.
 * `label` says what the pay is: a person's disclosed pay, or a position's average.
 */
export const PayChart = ({ years, points, label = 'Disclosed pay by year', multiple = false }) => {
  const indexes = points.map((point) => point.year)
  if (!indexes.length) return null
  const first = Math.min(...indexes)
  const last = Math.max(...indexes)
  const most = Math.max(1, ...points.map((point) => Math.abs(point.pay)))
  const span = samePeriodKinds(years, indexes).filter((at) => at >= first && at <= last).map((at) => ({ label: years[at], point: points.find((point) => point.year === at) }))
  return (
    <figure className="salaries-chart" aria-label={`${label}, ${years[first]} to ${years[last]}; the figures are in the list below`}>
      <div className="salaries-chart__bars" aria-hidden="true">
        {span.map(({ label, point }) => (
          <div key={label} className="salaries-chart__column" data-empty={!point || undefined} title={point ? `${label}: ${formatMoney(point.pay)}` : `${label}: no record`}>
            <span className="salaries-chart__value">{point ? compactMoney(point.pay) : ''}</span>
            <span className="salaries-chart__bar" data-negative={point?.pay < 0 || undefined} style={{ height: point ? `${Math.max(4, (Math.abs(point.pay) / most) * 100)}%` : undefined }} />
            <span className="salaries-chart__label">{shortYear(label)}</span>
          </div>
        ))}
      </div>
      {multiple && <figcaption className="salaries__hint salaries__hint--small">For years with several records, each bar shows the highest single record. All records are listed below.</figcaption>}
      {points.some((point) => point.pay < 0) && <figcaption className="salaries__hint salaries__hint--small">Negative amounts are preserved as reported. Bar height shows the amount's magnitude; labels retain its sign.</figcaption>}
    </figure>
  )
}

/** "$123k", for labels over bars. */
export const compactMoney = (value) => (value >= 1e6 ? `$${(value / 1e6).toFixed(1)}M` : value >= 1e3 ? `$${Math.round(value / 1e3)}k` : formatMoney(value))
