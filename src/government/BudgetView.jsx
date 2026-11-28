// The government view's Budget mode (?view=government&mode=budget&fy=2024-25): where the Province's
// money came from and where it went, year by year, from the consolidated Summary Financial
// Statements, with the bodies that sit under each function.
//
// The statements ship with the page (budgetData.js); a year's bodies are fetched when it is shown
// (public/budget/<year>.json). Both are built by scripts/build-budget.mjs.

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { ViewSwitcher } from '../site/ViewSwitcher.jsx'
import { Disclosure } from '../site/Disclosure.jsx'
import { SunGlyph, ThemeIcon } from '../site/icons.jsx'
import { BUDGET_CHECKED, BUDGET_SOURCES } from './budgetData.js'
import {
  BALANCE, BUDGET_YEARS, axisTicks, flowColumns, formatBillions, formatFigure, formatMillions, formatShare, layoutFlow,
  readBudgetYear, statementFor, trendSeries, wrap
} from './budgetLayout.js'
import { RELATED_BODIES, relatedBodyPlace } from './relatedBodies.js'
import './money.css'
import './budget.css'

// ── Data ─────────────────────────────────────────────────────────────────────────────────────────

const fetched = new Map()
const fetchBodies = (year) => {
  const url = `${import.meta.env?.BASE_URL ?? '/'}budget/${year}.json`
  if (!fetched.has(url)) {
    fetched.set(url, fetch(url)
      .then((response) => { if (!response.ok) throw new Error(`${response.status}`); return response.json() })
      .catch((error) => { fetched.delete(url); throw error }))
  }
  return fetched.get(url)
}

const useBodies = (year) => {
  const [state, setState] = useState({ year: null, data: null, error: false })
  useEffect(() => {
    let live = true
    fetchBodies(year).then(
      (data) => { if (live) setState({ year, data, error: false }) },
      () => { if (live) setState({ year, data: null, error: true }) }
    )
    return () => { live = false }
  }, [year])
  return state.year === year ? state : { year, data: null, error: false }
}

/** The width of an element, followed as it changes. */
const useWidth = () => {
  const ref = useRef(null)
  const [width, setWidth] = useState(0)
  useLayoutEffect(() => {
    const element = ref.current
    if (!element) return undefined
    setWidth(element.clientWidth)
    if (typeof ResizeObserver === 'undefined') return undefined
    const observer = new ResizeObserver(() => setWidth(element.clientWidth))
    observer.observe(element)
    return () => observer.disconnect()
  }, [])
  return [ref, width]
}

/** Whether the screen is phone-narrow, where the breadcrumb folds the view's name to "…". */
const usePhone = () => {
  const media = globalThis.matchMedia?.('(max-width: 479px)')
  const [phone, setPhone] = useState(() => Boolean(media?.matches))
  useEffect(() => {
    if (!media) return undefined
    const listen = (event) => setPhone(event.matches)
    media.addEventListener('change', listen)
    return () => media.removeEventListener('change', listen)
  }, [media])
  return phone
}

/** Keeps `fy` in the address bar beside the government view's own parameters. */
const writeYear = (year) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'government')
  url.searchParams.set('mode', 'budget')
  url.searchParams.set('fy', year)
  globalThis.history.replaceState(null, '', url)
}

const SCHOOL_DISTRICTS = RELATED_BODIES.filter((body) => body.kind === 'school-district' || body.kind === 'francophone-school-district')
  .sort((a, b) => a.name.localeCompare(b.name, 'en-CA', { numeric: true }))

/** Where a body's page is, from the build's link: a related body's record or the atlas in a year. */
const placeOf = (entry) => {
  if (!entry.id) return null
  if (entry.related) return relatedBodyPlace(entry.id)
  return { view: 'government', node: entry.id, year: entry.at, ...(entry.local ? { local: 1 } : {}) }
}

const BodyName = ({ entry }) => {
  const place = placeOf(entry)
  return place ? <SiteLink to={place}>{entry.name}</SiteLink> : <span>{entry.name}</span>
}

const Swatch = ({ line }) => <span className="gov-budget__swatch" data-key={line.key} aria-hidden="true" />

// ── The flow ─────────────────────────────────────────────────────────────────────────────────────

const FONT = 12
const LINE = 15

/** How many characters a label line holds beside a column. */
const labelChars = ({ width, inset, node, inside }) => Math.max(10, Math.floor((inside ? width / 2 - node - 18 : inset - 18) / (FONT * 0.55)))
const labelSize = (heading, chars) => (wrap(heading, chars).length + 1) * LINE + 4

const FlowLabels = ({ nodes, side, width, inset, node, inside, chars }) => {
  const gap = inside ? 6 : 12
  const anchorX = side === 'source'
    ? (inside ? inset + node + gap : inset - gap)
    : (inside ? width - inset - node - gap : width - inset + gap)
  const anchor = (side === 'source') === inside ? 'start' : 'end'
  return nodes.map((line) => {
    const lines = wrap(line.heading, chars)
    const size = (lines.length + 1) * LINE
    const first = line.y + line.size / 2 - size / 2 + LINE - 3
    return (
      <g key={line.key} className="gov-budget__label" data-key={line.key}>
        <text x={anchorX} y={first} textAnchor={anchor}>
          {lines.map((text, at) => <tspan key={at} x={anchorX} dy={at ? LINE : 0}>{text}</tspan>)}
          <tspan x={anchorX} dy={LINE} className="gov-budget__label-figure">{formatFigure(line.actual)}</tspan>
        </text>
      </g>
    )
  })
}

const BudgetFlow = ({ statement, onPick }) => {
  const [ref, width] = useWidth()
  const [active, setActive] = useState(null)
  const patternId = useId().replace(/:/g, '')
  const inside = width < 620
  const inset = inside ? 0 : Math.min(230, Math.round(width * 0.3))
  const chars = labelChars({ width, inset, node: 10, inside })
  // The total is drawn a set height; each bar's slot is at least its label's height, which sets the box's.
  const flow = useMemo(() => (width
    ? layoutFlow(statement, { width, hubHeight: inside ? 300 : 340, inset, gap: inside ? 8 : 6, slot: (line) => labelSize(line.heading, chars) })
    : null), [statement, width, inset, inside, chars])
  const height = flow?.height ?? 0
  useEffect(() => setActive(null), [statement])

  const readout = (() => {
    const line = flow && [...flow.sources, ...flow.uses].find((each) => `${each.side}:${each.key}` === active)
    if (!line) return 'Point at a band or a bar for its figure. Choose a function to see the bodies under it.'
    if (line.key === BALANCE) return `${line.heading}: ${formatMillions(line.actual)}.`
    const whole = line.side === 'source' ? flow.revenue : flow.expense
    return `${line.heading}: ${formatMillions(line.actual)}, ${formatShare(line.actual, whole)} of ${line.side === 'source' ? 'revenue' : 'expense'}.`
  })()

  const mark = (line) => ({
    'data-key': line.key,
    'data-side': line.side,
    'data-on': active === `${line.side}:${line.key}` ? '' : undefined,
    onPointerEnter: () => setActive(`${line.side}:${line.key}`),
    onPointerLeave: () => setActive(null)
  })

  return (
    <figure className="gov-budget__flow" ref={ref}>
      <p className="gov-budget__readout" aria-live="polite">{readout}</p>
      {flow && (
        <svg
          width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img"
          aria-label={`Revenue of ${formatMillions(flow.revenue)} from ${statement.revenue.lines.length} sources and expense of ${formatMillions(flow.expense)} across ${statement.expense.lines.length} functions, ${statement.year}. The figures are in the tables below.`}
          data-active={active ? '' : undefined}
          data-inside={inside ? '' : undefined}
        >
          <defs>
            <pattern id={patternId} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="6" height="6" className="gov-budget__hatch-ground" />
              <line x1="0" y1="0" x2="0" y2="6" className="gov-budget__hatch" />
            </pattern>
          </defs>
          {[...flow.sources, ...flow.uses].map((line) => (
            <path key={`${line.side}-${line.key}-band`} className="gov-budget__band" d={line.path} {...mark(line)}
              style={line.key === BALANCE ? { fill: `url(#${patternId})` } : undefined}>
              <title>{`${line.heading}: ${formatMillions(line.actual)}`}</title>
            </path>
          ))}
          <rect className="gov-budget__hub" x={flow.hub.x} y={flow.hub.y} width={flow.node} height={flow.hub.size} rx="2">
            <title>{`Revenue ${formatMillions(flow.revenue)}; expense ${formatMillions(flow.expense)}`}</title>
          </rect>
          {[...flow.sources, ...flow.uses].map((line) => {
            const pick = line.side === 'function' && line.key !== BALANCE
            return (
              <rect
                key={`${line.side}-${line.key}-node`} className="gov-budget__node" x={line.x} y={line.y} width={flow.node} height={Math.max(1, line.size)} rx="2"
                {...mark(line)}
                style={line.key === BALANCE ? { fill: `url(#${patternId})` } : undefined}
                tabIndex={pick ? 0 : undefined}
                role={pick ? 'button' : undefined}
                aria-label={pick ? `${line.heading}, ${formatMillions(line.actual)}: show the bodies under it` : undefined}
                onFocus={() => setActive(`${line.side}:${line.key}`)}
                onBlur={() => setActive(null)}
                onClick={pick ? () => onPick(line.key) : undefined}
                onKeyDown={pick ? (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onPick(line.key) } } : undefined}
              />
            )
          })}
          <g aria-hidden="true">
            <FlowLabels nodes={flow.sources} side="source" width={width} inset={inset} node={flow.node} inside={inside} chars={chars} />
            <FlowLabels nodes={flow.uses} side="function" width={width} inset={inset} node={flow.node} inside={inside} chars={chars} />
          </g>
        </svg>
      )}
      <figcaption className="gov-muted gov-budget__caption">
        Sources on the left, functions on the right, $ millions. They meet only in the total: the Province does not tie a source to a function.
      </figcaption>
    </figure>
  )
}

// ── The trend ────────────────────────────────────────────────────────────────────────────────────

const BudgetTrend = ({ year, onYear }) => {
  const [ref, width] = useWidth()
  const [hover, setHover] = useState(null)
  const series = useMemo(trendSeries, [])
  const height = 168
  const margin = { top: 12, right: 74, bottom: 26, left: 52 }
  const ticks = axisTicks(Math.max(...series.flatMap((point) => [point.revenue, point.expense])))
  const top = ticks.at(-1)
  const plotWidth = Math.max(10, width - margin.left - margin.right)
  const plotHeight = height - margin.top - margin.bottom
  const x = (at) => margin.left + (series.length === 1 ? 0 : (at / (series.length - 1)) * plotWidth)
  const y = (value) => margin.top + plotHeight - (value / top) * plotHeight
  const line = (key) => series.map((point, at) => `${at ? 'L' : 'M'}${x(at).toFixed(1)},${y(point[key]).toFixed(1)}`).join('')
  const chosen = series.findIndex((point) => point.year === year)
  const shown = series[hover ?? chosen]
  const nearest = (event) => {
    const box = event.currentTarget.getBoundingClientRect()
    const at = Math.round(((event.clientX - box.left - margin.left) / plotWidth) * (series.length - 1))
    return Math.min(series.length - 1, Math.max(0, at))
  }
  // Year labels counted back from the latest, so it is always labelled and none collide.
  const labelEvery = width < 520 ? 8 : width < 820 ? 4 : 2
  const ends = { revenue: y(series.at(-1).revenue), expense: y(series.at(-1).expense) }
  const apart = Math.abs(ends.revenue - ends.expense) < 14 ? (ends.revenue < ends.expense ? [-7, 7] : [7, -7]) : [0, 0]

  return (
    <figure className="gov-budget__trend" ref={ref}>
      <p className="gov-budget__readout" aria-live="polite">
        {shown.year}: revenue {formatBillions(shown.revenue)}, expense {formatBillions(shown.expense)}, surplus (deficit) {formatBillions(shown.surplus)}.
      </p>
      {width > 0 && (
        <svg
          width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img"
          aria-label={`Total revenue and expense, ${series[0].year} to ${series.at(-1).year}. Choose a year with the slider above.`}
          onPointerMove={(event) => setHover(nearest(event))}
          onPointerLeave={() => setHover(null)}
          onClick={(event) => onYear(series[nearest(event)].year)}
        >
          {ticks.map((tick) => (
            <g key={tick} className="gov-budget__axis">
              <line x1={margin.left} x2={margin.left + plotWidth} y1={y(tick)} y2={y(tick)} />
              <text x={margin.left - 6} y={y(tick) + 4} textAnchor="end">{tick ? `$${tick / 1000}B` : '0'}</text>
            </g>
          ))}
          {series.map((point, at) => (series.length - 1 - at) % labelEvery === 0 && (
            <text key={point.year} className="gov-budget__axis-year" x={x(at)} y={height - 8} textAnchor="middle">{point.year}</text>
          ))}
          <line className="gov-budget__rule" x1={x(chosen)} x2={x(chosen)} y1={margin.top} y2={margin.top + plotHeight} />
          {hover !== null && hover !== chosen && <line className="gov-budget__rule gov-budget__rule--hover" x1={x(hover)} x2={x(hover)} y1={margin.top} y2={margin.top + plotHeight} />}
          <path className="gov-budget__line gov-budget__line--revenue" d={line('revenue')} />
          <path className="gov-budget__line gov-budget__line--expense" d={line('expense')} />
          {['revenue', 'expense'].map((key) => (
            <circle key={key} className={`gov-budget__dot gov-budget__dot--${key}`} cx={x(hover ?? chosen)} cy={y(shown[key])} r="4" />
          ))}
          <text className="gov-budget__end" x={x(series.length - 1) + 8} y={ends.revenue + 4 + apart[0]}>Revenue</text>
          <text className="gov-budget__end" x={x(series.length - 1) + 8} y={ends.expense + 4 + apart[1]}>Expense</text>
        </svg>
      )}
      <figcaption className="gov-budget__legend">
        <span><span className="gov-budget__key gov-budget__key--revenue" aria-hidden="true" />Total revenue</span>
        <span><span className="gov-budget__key gov-budget__key--expense" aria-hidden="true" />Total expense</span>
        <span className="gov-muted">Nominal dollars, as first published. Choose a year on the chart or with the slider.</span>
      </figcaption>
    </figure>
  )
}

// ── Lists ────────────────────────────────────────────────────────────────────────────────────────

const Restated = ({ line }) => line.restated
  ? <span className="gov-money__tag">Restated in the {line.restated.year} statements as {formatFigure(line.restated.amount)}</span>
  : null

const LinesTable = ({ lines, total, caption, whole, swatches = false }) => (
  <div className="gov-money__scroll gov-budget__table" tabIndex={0} role="region" aria-label={caption}>
    <table className="gov-money__table">
      <caption className="gov-budget__sr">{caption}</caption>
      <thead><tr><th scope="col">As printed</th><th scope="col">Actual</th><th scope="col">Estimates</th><th scope="col">Share</th></tr></thead>
      <tbody>
        {lines.map((line) => (
          <tr key={line.key}>
            <th scope="row">{swatches && <><Swatch line={line} />{' '}</>}{line.heading}<Restated line={line} />{line.note && <span className="gov-money__tag">{line.note}</span>}</th>
            <td>{formatFigure(line.actual)}</td>
            <td>{formatFigure(line.estimate)}</td>
            <td>{formatShare(line.actual, whole)}</td>
          </tr>
        ))}
        <tr className="gov-budget__total">
          <th scope="row">Total<Restated line={total} /></th>
          <td>{formatFigure(total.actual)}</td>
          <td>{formatFigure(total.estimate)}</td>
          <td />
        </tr>
      </tbody>
    </table>
  </div>
)

const BodiesTable = ({ rows, figures, label }) => (
  <div className="gov-money__scroll gov-budget__table" tabIndex={0} role="region" aria-label={label}>
    <table className="gov-money__table">
      <thead><tr><th scope="col">Body</th>{figures.map(([, heading]) => <th scope="col" key={heading}>{heading}</th>)}</tr></thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.name}>
            <th scope="row" className="gov-budget__body"><BodyName entry={row} /></th>
            {figures.map(([key, heading]) => <td key={heading}>{formatFigure(row[key])}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)

const FunctionBodies = ({ fn, bodies, defaultOpen }) => {
  const crowns = bodies.crowns.filter((row) => row.function === fn)
  const such = bodies.such.filter((row) => row.function === fn)
  const members = bodies.members.filter((row) => row.function === fn)
  const schools = fn === 'education' && such.some((row) => row.name === 'School Districts')
  const count = crowns.length + members.length + (schools ? SCHOOL_DISTRICTS.length : 0)
  if (!count && !such.length) return <p className="gov-muted gov-budget__none">No body is listed under this sector in the table this year.</p>
  return (
    <Disclosure defaultOpen={defaultOpen} summary="Bodies under this sector" hint={`${count} named${such.length ? `, ${such.length} SUCH sector rows` : ''}`}>
      {() => <div className="gov-budget__bodies">
        {such.length > 0 && <>
          <h4 className="gov-budget__group">SUCH sector rows</h4>
          <p className="gov-muted">Sector totals, $ millions. The table gives no figure for each school district, university, college or health authority.</p>
          <BodiesTable rows={such} figures={[['revenue', 'Revenue'], ['expense', 'Expense']]} label="SUCH sector rows" />
        </>}
        {members.length > 0 && <>
          <h4 className="gov-budget__group">Counted in those rows</h4>
          <p className="gov-muted">Bodies with a statement this year. Open one for its own figures.</p>
          <ul className="gov-budget__names">
            {members.map((row) => <li key={row.name}><BodyName entry={row} /></li>)}
          </ul>
        </>}
        {schools && <>
          <h4 className="gov-budget__group">School districts</h4>
          <Disclosure summary={`All ${SCHOOL_DISTRICTS.length} school districts`} hint="Today's list">
            {() => <ul className="gov-budget__names">
              {SCHOOL_DISTRICTS.map((body) => <li key={body.id}><SiteLink to={relatedBodyPlace(body.id)}>{body.shortName ?? body.name}</SiteLink></li>)}
            </ul>}
          </Disclosure>
        </>}
        {crowns.length > 0 && <>
          <h4 className="gov-budget__group">Crown corporations and agencies</h4>
          <p className="gov-muted">Each body's own figures, $ millions, before eliminations.</p>
          <BodiesTable rows={crowns} figures={[['revenue', 'Revenue'], ['expense', 'Expense']]} label="Crown corporations and agencies" />
        </>}
      </div>}
    </Disclosure>
  )
}

// ── The page ─────────────────────────────────────────────────────────────────────────────────────

/**
 * @param {object} props
 * @param {(view: string) => void} props.onChangeView
 * @param {'light' | 'dark'} props.themeName
 * @param {() => void} props.onToggleTheme
 */
export const BudgetView = ({ onChangeView, themeName, onToggleTheme }) => {
  const [year, setYear] = useState(() => readBudgetYear(globalThis.location?.search ?? ''))
  const [opened, setOpened] = useState(null)
  const phone = usePhone()
  const statement = statementFor(year)
  const { data: bodies, error } = useBodies(year)
  const index = BUDGET_YEARS.indexOf(year)
  useEffect(() => writeYear(year), [year])

  const pick = (key) => {
    setOpened(key)
    globalThis.document?.getElementById(`budget-function-${key}`)?.scrollIntoView({ block: 'start', behavior: 'smooth' })
  }
  const step = (by) => setYear(BUDGET_YEARS[Math.min(BUDGET_YEARS.length - 1, Math.max(0, index + by))])
  const source = statement.source
  const pageNote = `PDF page ${source.pdfPage}${source.printedPage ? ` (printed page ${source.printedPage})` : ''}`
  const unsectored = bodies ? bodies.crowns.filter((row) => !row.function) : []
  const crownsLine = statement.revenue.lines.find((line) => line.key === 'crowns')

  return (
    <div className="gov gov-budget" data-theme={themeName}>
      <nav className="gov-card gov-breadcrumb" aria-label="Breadcrumb">
        <SunGlyph fill={themeName === 'dark' ? '#fcba19' : '#e8a412'} />
        <strong className="gov-breadcrumb__site">Province of BC</strong>
        <span className="gov-muted" aria-hidden="true">/</span>
        <ViewSwitcher view="government" onChange={onChangeView} className="gov-breadcrumb__views" compact={phone} />
        <span className="gov-muted" aria-hidden="true">/</span>
        <span className="gov-breadcrumb__page" aria-current="page">Budget</span>
        <span className="gov-breadcrumb__tools">
          <button className="gov-button gov-button--icon" type="button" onClick={onToggleTheme} aria-label={`Switch to ${themeName === 'dark' ? 'light' : 'dark'} mode`}>
            <ThemeIcon name={themeName} />
          </button>
        </span>
      </nav>

      <main className="gov-budget__main">
        <header className="gov-card gov-budget__intro">
          <p className="gov-eyebrow">Public Accounts · {BUDGET_YEARS[0]} to {BUDGET_YEARS.at(-1)}</p>
          <h1 className="gov-title">Where the Province's money comes from and goes</h1>
          <p className="gov-description">
            Total revenue by source and total expense by function, year by year. The figures are the actual results in the
            Province's consolidated Summary Financial Statements.
          </p>
          <div className="gov-budget__year">
            <label className="gov-budget__year-label" htmlFor="budget-year">Fiscal year</label>
            <div className="gov-budget__year-row">
              <button type="button" className="gov-button gov-button--icon" onClick={() => step(-1)} disabled={index === 0} aria-label="Previous year">‹</button>
              <input
                id="budget-year" type="range" min="0" max={BUDGET_YEARS.length - 1} step="1" value={index}
                onChange={(event) => setYear(BUDGET_YEARS[Number(event.target.value)])}
                aria-valuetext={`${year}, ending ${statement.fyEnd}`}
              />
              <button type="button" className="gov-button gov-button--icon" onClick={() => step(1)} disabled={index === BUDGET_YEARS.length - 1} aria-label="Next year">›</button>
              <output htmlFor="budget-year" className="gov-budget__year-value">{year}</output>
            </div>
          </div>
          <dl className="gov-budget__totals">
            <div><dt>Revenue</dt><dd>{formatMillions(statement.revenue.total.actual)}</dd></div>
            <div><dt>Expense</dt><dd>{formatMillions(statement.expense.total.actual)}</dd></div>
            <div><dt>Surplus (deficit) for the year</dt><dd>{formatMillions(statement.surplus.actual)}</dd></div>
          </dl>
          {statement.between.length > 0 && (
            <p className="gov-muted">
              The result also takes in {statement.between.map((line) => `${line.heading.replace(/^Less: /, '').toLowerCase()} (${formatMillions(line.actual)})`).join(' and ')}, printed below the expense total.
            </p>
          )}
          <p className="gov-links"><SiteLink to={{ view: 'government' }}>← The government diagram</SiteLink></p>
        </header>

        <section className="gov-card" aria-labelledby="budget-flow-title">
          <h2 className="gov-card__heading" id="budget-flow-title">Revenue and expense, {year}</h2>
          <BudgetFlow statement={statement} onPick={pick} />
        </section>

        <section className="gov-card" aria-labelledby="budget-trend-title">
          <h2 className="gov-card__heading" id="budget-trend-title">Totals across the years</h2>
          <BudgetTrend year={year} onYear={setYear} />
        </section>

        <section className="gov-card" aria-labelledby="budget-sources-title">
          <h2 className="gov-card__heading" id="budget-sources-title">Where it comes from</h2>
          <p className="gov-muted">Revenue by source, $ millions, with the year's Estimates.</p>
          <LinesTable lines={statement.revenue.lines} total={statement.revenue.total} whole={statement.revenue.total.actual} caption={`Revenue by source, ${year}`} />
          {crownsLine && bodies && bodies.selfSupported.length > 0 && <>
            <h3 className="gov-budget__function-title">{crownsLine.heading}</h3>
            <p className="gov-muted">These corporations are not added in line by line. Only their net income comes into revenue.</p>
            <Disclosure summary="Self-supported Crown corporations and agencies" hint={`${bodies.selfSupported.length} rows`}>
              {() => <BodiesTable rows={bodies.selfSupported} figures={[['netIncome', 'Net income']]} label="Self-supported Crown corporations and agencies" />}
            </Disclosure>
          </>}
        </section>

        <section className="gov-card" aria-labelledby="budget-functions-title">
          <h2 className="gov-card__heading" id="budget-functions-title">Where it goes</h2>
          <p className="gov-muted">Expense by function, $ millions. Under each function are the bodies the Public Accounts list under that sector.</p>
          <LinesTable lines={statement.expense.lines} total={statement.expense.total} whole={statement.expense.total.actual} caption={`Expense by function, ${year}`} swatches />
          {error && <p className="gov-money__warning">The bodies for {year} could not be loaded. The totals above are complete.</p>}
          {!bodies && !error && <p className="gov-muted">Loading the bodies…</p>}
          {bodies && statement.expense.lines.map((line) => (
            <div key={line.key} className="gov-budget__function" id={`budget-function-${line.key}`}>
              <h3 className="gov-budget__function-title"><Swatch line={line} /> {line.heading}</h3>
              <p className="gov-muted">{formatMillions(line.actual)} · {formatShare(line.actual, statement.expense.total.actual)} of expense</p>
              <FunctionBodies key={`${year}-${opened === line.key}`} fn={line.key} bodies={bodies} defaultOpen={opened === line.key} />
            </div>
          ))}
          {bodies && unsectored.length > 0 && (
            <div className="gov-budget__function">
              <h3 className="gov-budget__function-title">Not under a sector heading</h3>
              <p className="gov-muted">The Public Accounts lists give no sector for these rows this year.</p>
              <BodiesTable rows={unsectored} figures={[['revenue', 'Revenue'], ['expense', 'Expense']]} label="Bodies with no sector" />
            </div>
          )}
        </section>

        <section className="gov-card" aria-labelledby="budget-about-title">
          <h2 className="gov-card__heading" id="budget-about-title">What these numbers are</h2>
          <ul className="gov-budget__about">
            <li>They are the Province's consolidated summary: ministries, Crown corporations and agencies, school districts, universities, colleges and health authorities together.</li>
            <li>Money that moves between these bodies is removed before the totals are made. This is called an inter-entity elimination. The bodies' own figures are before that step, so they do not add up to a function's total.</li>
            <li>Amounts are in millions of nominal dollars. They are not adjusted for inflation.</li>
            <li>The figures are actual results, not the plan. The Estimates column is the plan the year began with. The first year, {BUDGET_YEARS[0]}, prints no Estimates.</li>
            <li>Each year is shown as first published. Where the next year's statements restated a line, the restated figure is given beside it.</li>
            <li>Self-supported Crown corporations, such as BC Hydro and ICBC, count only by their net income, under revenue.</li>
            <li>The headings are the Province's own. They change slightly over the years, for example "Fees and licenses" from 2013-14 to 2019-20.</li>
          </ul>
          <div className="gov-money__sources">
            <strong>Sources</strong>
            <ul className="gov-budget__sources">
              <li><a href={source.url} target="_blank" rel="noreferrer">Public Accounts {year}, Summary Financial Statements: {source.title}</a> <span className="gov-muted">{pageNote}</span></li>
              {bodies?.source && <li><a href={bodies.source.url} target="_blank" rel="noreferrer">{bodies.source.title}, {year}</a></li>}
              <li><a href={BUDGET_SOURCES.sectors.url} target="_blank" rel="noreferrer">{BUDGET_SOURCES.sectors.title}</a></li>
            </ul>
            <p className="gov-muted">Read from the PDFs on {BUDGET_CHECKED}. Every printed subtotal was checked against its lines.</p>
          </div>
        </section>
      </main>
    </div>
  )
}

export default BudgetView
