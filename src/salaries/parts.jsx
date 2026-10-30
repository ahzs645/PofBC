// Small pieces the salary views share with the government panel's salary card: which years a name or
// an employer has records in, a year picker that shows how many each holds, and a person's pay by
// year. Each is styled in site.css (.salaries-strip, .salaries-picker, .salaries-chart) with the
// government view's colours where it sits inside that view.

import { useEffect, useRef, useState } from 'react'
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

/** "2018/19 – 2023/24", one period's own label, or every period. */
export const rangeLabel = (years, range) => (!range ? 'Every period'
  : range[0] === range[1] ? reportingYearLabel(years[range[0]]) : `${years[range[0]]} – ${years[range[1]]}`)

/**
 * The periods to search, as a button that opens the bar picker the employer pages use: a tap picks a
 * period, a second tap the other end of a range. It closes on Done, Escape or a tap outside.
 */
export const PeriodRange = ({ years, counts, value, onChange }) => {
  const [open, setOpen] = useState(false)
  const [anchor, setAnchor] = useState(null)
  const root = useRef(null)
  useEffect(() => {
    if (!open) return undefined
    const away = (event) => { if (!root.current?.contains(event.target)) setOpen(false) }
    const key = (event) => { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('pointerdown', away)
    document.addEventListener('keydown', key)
    return () => { document.removeEventListener('pointerdown', away); document.removeEventListener('keydown', key) }
  }, [open])
  const most = Math.max(1, ...counts)
  const pick = (at) => {
    if (anchor === null) { setAnchor(at); onChange([at, at]) } else { onChange([Math.min(anchor, at), Math.max(anchor, at)]); setAnchor(null) }
  }
  const inside = (at) => Boolean(value) && at >= value[0] && at <= value[1]
  return (
    <div className="salaries-range" ref={root}>
      <button type="button" className="salaries-range__trigger" aria-haspopup="dialog" aria-expanded={open} onClick={() => { setOpen((now) => !now); setAnchor(null) }}>
        <span className="salaries-range__label">{rangeLabel(years, value)}</span>
        <svg width="10" height="10" viewBox="0 0 18 10" aria-hidden="true" style={{ transform: open ? 'rotate(180deg)' : undefined }}><path d="M1.64 0.74 0.74 1.64 8.55 9.45 9 9.88 9.45 9.45 17.26 1.64 16.36 0.74 9 8.1 1.64 0.74Z" fill="currentColor" /></svg>
      </button>
      {open && (
        <div className="salaries-range__panel" role="dialog" aria-label="Reporting periods">
          <p className="salaries-range__hint">{anchor === null ? 'Choose a period, or the first of a range.' : `Now the last period of the range from ${years[anchor]}.`}</p>
          <div className="salaries-picker" role="group" aria-label="Periods">
            {years.map((year, at) => (
              <button
                key={year}
                type="button"
                aria-pressed={inside(at)}
                data-edge={(value && (at === value[0] || at === value[1])) || undefined}
                data-empty={!counts[at] || undefined}
                aria-label={`${reportingYearLabel(year)}: ${(counts[at] ?? 0).toLocaleString('en-CA')} records`}
                title={`${reportingYearLabel(year)}: ${(counts[at] ?? 0).toLocaleString('en-CA')} records`}
                onClick={() => pick(at)}
              >
                <span className="salaries-picker__bar"><span style={{ height: counts[at] ? `${Math.max(8, (counts[at] / most) * 100)}%` : undefined }} /></span>
                <span className="salaries-picker__label">{shortYear(year)}</span>
              </button>
            ))}
          </div>
          <div className="salaries-range__actions">
            <button type="button" className="salaries__link" onClick={() => { onChange(null); setAnchor(null) }}>Every period</button>
            <button type="button" className="salaries__link" onClick={() => { onChange([years.length - 1, years.length - 1]); setAnchor(null) }}>Latest only</button>
            <button type="button" className="salaries__more" onClick={() => setOpen(false)}>Done</button>
          </div>
        </div>
      )}
    </div>
  )
}
