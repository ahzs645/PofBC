// Small pieces the salary views share with the government panel's salary card: which years a name or
// an employer has records in, a year picker that shows how many each holds, and a person's pay by
// year. Each is styled in site.css (.salaries-strip, .salaries-picker, .salaries-chart) with the
// government view's colours where it sits inside that view.

import { useEffect, useRef, useState } from 'react'
import { formatMoney } from './money.js'
import { labelPlan } from './labelPlan.js'
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

/** An element's width, kept current as it changes: [ref, width], width 0 until it is measured. */
const useWidth = () => {
  const ref = useRef(null)
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const node = ref.current
    if (!node || typeof ResizeObserver === 'undefined') return undefined
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    observer.observe(node)
    return () => observer.disconnect()
  }, [])
  return [ref, width]
}

/**
 * The years as a row of bars, each as tall as its record count and each a button that picks it. A
 * year without records is a dashed stub: still a button, since choosing it explains the gap. Given
 * `values` (a figure a year, such as median pay), the bars are as tall as those instead, `describe`
 * writing each in full, so the one chart both shows the figure and picks the year.
 */
export const YearPicker = ({ years, counts, values, describe = formatMoney, valueName = 'median', coverage = [], value, onChange, label = 'Disclosure period', chooseLabel = label }) => {
  const heights = values ?? counts
  const most = Math.max(1, ...heights.map((height) => height ?? 0))
  const visible = new Set([...relevantYearIndexes(years, coverage, counts), value])
  const shown = years.map((_, at) => at).filter((at) => visible.has(at))
  const [ref, width] = useWidth()
  const plan = labelPlan(shown.length, width, shown.indexOf(value), 2)
  return (
    <div className="salaries-picker-wrap">
      {/* Too narrow for a bar a period (a phone, the government panel): the period chooser instead. */}
      <div className="salaries-picker-select">
        <span>{chooseLabel}</span>
        <PeriodRange
          single
          years={years}
          counts={counts}
          value={[value, value]}
          onChange={(range) => onChange(range[0])}
          only={[...visible]}
          describe={(at) => yearAvailability(coverage[at], counts[at] ?? 0)}
        />
      </div>
    <div ref={ref} className="salaries-picker" role="group" aria-label={label}>
      {shown.map((at, place) => {
        const year = years[at]
        const count = counts[at] ?? 0
        const height = values ? (count ? values[at] ?? 0 : 0) : count
        const said = `${reportingYearLabel(year)}: ${yearAvailability(coverage[at], count)}${values && count && values[at] != null ? `, ${valueName} ${describe(values[at])}` : ''}`
        return (
          <button
            key={year}
            type="button"
            aria-pressed={at === value}
            data-empty={!count || undefined}
            data-status={coverage[at]?.status}
            aria-label={said}
            title={said}
            onClick={() => onChange(at)}
          >
            <span className="salaries-picker__bar"><span style={{ height: height ? `${Math.max(8, (height / most) * 100)}%` : undefined }} /></span>
            <span className="salaries-picker__label" data-hidden={!plan[place].shown || undefined} data-edge={plan[place].edge}>{shortYear(year)}</span>
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
 * `label` says what the pay is: a person's disclosed pay, or a position's average. `format` writes a
 * value over its bar and `describe` one in full; both are money unless given (a count of records).
 */
export const PayChart = ({ years, points, label = 'Disclosed pay by year', multiple = false, format = compactMoney, describe = formatMoney }) => {
  const indexes = points.map((point) => point.year)
  if (!indexes.length) return null
  const first = Math.min(...indexes)
  const last = Math.max(...indexes)
  const most = Math.max(1, ...points.map((point) => Math.abs(point.pay)))
  const span = samePeriodKinds(years, indexes).filter((at) => at >= first && at <= last).map((at) => ({ label: years[at], point: points.find((point) => point.year === at) }))
  const [ref, width] = useWidth()
  const plan = labelPlan(span.length, width, -1, 4)
  // A value over its bar only where a column has room for "$208k" without meeting the next one's.
  const values = !width || width / span.length >= 34
  return (
    <figure className="salaries-chart" aria-label={`${label}, ${years[first]} to ${years[last]}; the figures are in the list below`}>
      <div ref={ref} className="salaries-chart__bars" aria-hidden="true">
        {span.map(({ label, point }, place) => (
          <div key={label} className="salaries-chart__column" data-empty={!point || undefined} title={point ? `${label}: ${describe(point.pay)}` : `${label}: no record`}>
            <span className="salaries-chart__value">{point && values ? format(point.pay) : ''}</span>
            <span className="salaries-chart__bar" data-negative={point?.pay < 0 || undefined} style={{ height: point ? `${Math.max(4, (Math.abs(point.pay) / most) * 100)}%` : undefined }} />
            <span className="salaries-chart__label" data-hidden={!plan[place].shown || undefined} data-edge={plan[place].edge}>{shortYear(label)}</span>
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
 * The periods to search, as a button that opens a panel of them: fiscal years and calendar years
 * apart, each a chip with a bar as long as its share of the records. A tap picks a period; a second
 * tap, the other end of a range, previewed as the pointer moves. Quick picks cover the usual cases.
 * It closes on Done, Escape or a tap outside; on a phone it is a sheet at the foot of the screen.
 * `single` chooses one period and closes on it; `only` limits the periods offered; `describe` says
 * what each holds, in place of its record count.
 */
export const PeriodRange = ({ years, counts, value, onChange, single = false, only, describe, inline = false }) => {
  const [open, setOpen] = useState(false)
  const [anchor, setAnchor] = useState(null)
  const [hover, setHover] = useState(null)
  const root = useRef(null)
  // A containing filter sheet can clear the range while the first end is being chosen.
  useEffect(() => { if (!value) { setAnchor(null); setHover(null) } }, [value])
  useEffect(() => {
    if (!open || inline) return undefined
    const away = (event) => { if (!root.current?.contains(event.target)) setOpen(false) }
    const key = (event) => { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('pointerdown', away)
    document.addEventListener('keydown', key)
    return () => { document.removeEventListener('pointerdown', away); document.removeEventListener('keydown', key) }
  }, [open, inline])
  const most = Math.max(1, ...counts)
  const calendar = (label) => /^\d{4}$/.test(label)
  const offered = only ? new Set(only) : null
  const indexes = years.map((_, at) => at).filter((at) => !offered || offered.has(at))
  const groups = [
    { kind: 'fiscal', title: 'Fiscal years', note: 'April to March', indexes: indexes.filter((at) => !calendar(years[at])) },
    { kind: 'calendar', title: 'Calendar years', note: 'January to December', indexes: indexes.filter((at) => calendar(years[at])) }
  ].filter((group) => group.indexes.length)
  const says = (at) => `${reportingYearLabel(years[at])}: ${describe ? describe(at) : `${(counts[at] ?? 0).toLocaleString('en-CA')} records`}`
  // While a range is being chosen, the pointer's period is its other end.
  const shown = !single && anchor !== null && hover !== null ? [Math.min(anchor, hover), Math.max(anchor, hover)] : value
  const inside = (at) => Boolean(shown) && at >= shown[0] && at <= shown[1]
  const edge = (at) => Boolean(shown) && (at === shown[0] || at === shown[1])
  const pick = (at) => {
    if (single) { onChange([at, at]); setOpen(false) } else if (anchor === null) { setAnchor(at); onChange([at, at]) } else { onChange([Math.min(anchor, at), Math.max(anchor, at)]); setAnchor(null) }
  }
  const quick = (range) => { onChange(range); setAnchor(null) }
  const fiscal = groups.find((group) => group.kind === 'fiscal')?.indexes ?? []
  const lastFive = fiscal.length >= 5 ? [fiscal.at(-5), years.length - 1] : null
  return (
    <div className={`salaries-range${single ? ' salaries-range--single' : ''}${inline ? ' salaries-range--inline' : ''}`} ref={root}>
      {!inline && <button type="button" className="salaries-range__trigger" aria-haspopup="dialog" aria-expanded={open} onClick={() => { setOpen((now) => !now); setAnchor(null) }}>
        <span className="salaries-range__label">{rangeLabel(years, value)}</span>
        <svg width="10" height="10" viewBox="0 0 18 10" aria-hidden="true" style={{ transform: open ? 'rotate(180deg)' : undefined }}><path d="M1.64 0.74 0.74 1.64 8.55 9.45 9 9.88 9.45 9.45 17.26 1.64 16.36 0.74 9 8.1 1.64 0.74Z" fill="currentColor" /></svg>
      </button>}
      {(inline || open) && (
        <div className="salaries-range__panel" role={inline ? 'group' : 'dialog'} aria-label="Reporting periods">
          <div className="salaries-range__head">
            <p className="salaries-range__chosen" aria-live="polite">{rangeLabel(years, shown)}</p>
            <p className="salaries-range__hint">{single ? 'Tap a period.' : anchor === null ? 'Tap a period, or the first of a range.' : `Now the last period, from ${years[anchor]}.`}</p>
          </div>
          {!single && <div className="salaries-range__quick" role="group" aria-label="Quick picks">
            <button type="button" aria-pressed={!value} onClick={() => quick(null)}>Every period</button>
            {lastFive && <button type="button" aria-pressed={value?.[0] === lastFive[0] && value?.[1] === lastFive[1]} onClick={() => quick(lastFive)}>Last five years</button>}
            <button type="button" aria-pressed={value?.[0] === years.length - 1 && value?.[1] === years.length - 1} onClick={() => quick([years.length - 1, years.length - 1])}>Latest</button>
          </div>}
          {groups.map((group) => (
            <section key={group.kind} className="salaries-range__group" aria-label={group.title}>
              <h3 className="salaries-range__group-title">{group.title} <span>{group.note}</span></h3>
              <div className="salaries-range__chips" onPointerLeave={() => setHover(null)}>
                {group.indexes.map((at) => (
                  <button
                    key={years[at]}
                    type="button"
                    className="salaries-range__chip"
                    aria-pressed={inside(at)}
                    data-edge={edge(at) || undefined}
                    data-empty={!counts[at] || undefined}
                    aria-label={says(at)}
                    title={says(at)}
                    onPointerEnter={() => setHover(at)}
                    onFocus={() => setHover(at)}
                    onClick={() => pick(at)}
                  >
                    <span className="salaries-range__year">{years[at]}</span>
                    <span className="salaries-range__bar" aria-hidden="true"><span style={{ width: counts[at] ? `${Math.max(6, (counts[at] / most) * 100)}%` : 0 }} /></span>
                  </button>
                ))}
              </div>
            </section>
          ))}
          {!inline && <div className="salaries-range__actions">
            <button type="button" className="salaries__more" onClick={() => setOpen(false)}>Done</button>
          </div>}
        </div>
      )}
    </div>
  )
}
