// Small pieces the salary views share with the government panel's salary card: which years a name or
// an employer has records in, a year picker that shows how many each holds, and a person's pay by
// year. Each is styled in site.css (.salaries-strip, .salaries-picker, .salaries-chart) with the
// government view's colours where it sits inside that view.

import { formatMoney } from './money.js'
import { yearAvailability } from './coverage.js'

/** "2012/13–2023/24", or one label when the range is a single year. */
export const yearSpan = (labels) => (labels.length > 1 ? `${labels[0]}–${labels.at(-1)}` : labels[0] ?? '')

/** Short year label for tight spaces: "2023/24" → "23/24". */
export const shortYear = (label) => label.slice(2)

/**
 * One mark per collection year, filled where there are records: the shape of a history at a glance,
 * in the room of a line of text. `seen` is a list of year indexes.
 */
export const YearStrip = ({ years, seen, children }) => {
  const set = new Set(seen)
  const labels = years.filter((_, at) => set.has(at))
  return (
    <span className="salaries-strip">
      <span className="salaries-strip__marks" role="img" aria-label={`Records in ${labels.length} of ${years.length} years${labels.length ? `, ${yearSpan(labels)}` : ''}`}>
        {years.map((label, at) => <span key={label} data-seen={set.has(at) || undefined} title={label} />)}
      </span>
      <span className="salaries-strip__text">{children ?? `${labels.length} ${labels.length === 1 ? 'year' : 'years'}${labels.length ? ` · ${yearSpan(labels)}` : ''}`}</span>
    </span>
  )
}

/**
 * The years as a row of bars, each as tall as its record count and each a button that picks it. A
 * year without records is a dashed stub: still a button, since choosing it explains the gap.
 */
export const YearPicker = ({ years, counts, coverage = [], value, onChange, label = 'Disclosure year' }) => {
  const most = Math.max(1, ...counts)
  return (
    <div className="salaries-picker-wrap">
      <label className="salaries-picker-select">
        <span>{label}</span>
        <select value={value} onChange={(event) => onChange(Number(event.target.value))}>
          {years.map((year, at) => <option key={year} value={at}>{year} · {yearAvailability(coverage[at], counts[at] ?? 0)}</option>)}
        </select>
      </label>
    <div className="salaries-picker" role="group" aria-label={label}>
      {years.map((year, at) => {
        const count = counts[at] ?? 0
        return (
          <button
            key={year}
            type="button"
            aria-pressed={at === value}
            data-empty={!count || undefined}
            data-status={coverage[at]?.status}
            aria-label={`${year}: ${yearAvailability(coverage[at], count)}`}
            title={`${year}: ${yearAvailability(coverage[at], count)}`}
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
 */
export const PayChart = ({ years, points, multiple = false }) => {
  const indexes = points.map((point) => point.year)
  if (!indexes.length) return null
  const first = Math.min(...indexes)
  const last = Math.max(...indexes)
  const most = Math.max(...points.map((point) => point.pay))
  const span = years.slice(first, last + 1).map((label, offset) => ({ label, point: points.find((point) => point.year === first + offset) }))
  return (
    <figure className="salaries-chart" aria-label={`Disclosed pay by year, ${years[first]} to ${years[last]}; the figures are in the table below`}>
      <div className="salaries-chart__bars" aria-hidden="true">
        {span.map(({ label, point }) => (
          <div key={label} className="salaries-chart__column" data-empty={!point || undefined} title={point ? `${label}: ${formatMoney(point.pay)}` : `${label}: no record`}>
            <span className="salaries-chart__value">{point ? compactMoney(point.pay) : ''}</span>
            <span className="salaries-chart__bar" style={{ height: point ? `${Math.max(4, (point.pay / most) * 100)}%` : undefined }} />
            <span className="salaries-chart__label">{shortYear(label)}</span>
          </div>
        ))}
      </div>
      {multiple && <figcaption className="salaries__hint salaries__hint--small">For years with several records, each bar shows the highest single record. All records are listed below.</figcaption>}
    </figure>
  )
}

/** "$123k", for labels over bars. */
export const compactMoney = (value) => (value >= 1e6 ? `$${(value / 1e6).toFixed(1)}M` : value >= 1e3 ? `$${Math.round(value / 1e3)}k` : formatMoney(value))
