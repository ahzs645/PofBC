// The Money card's three detailed parts, each from its own source and cited to its page:
//
//   * Breakdown — revenue by source and expense as the body's own audited statement of operations
//     lists them (research/finance/statements/), with the statement's own labels;
//   * FromMinistries — cash the Province's ministries paid the body, from the Government Transfers
//     schedule (research/finance/transfers/);
//   * BudgetActual — for a ministry or office, its votes' estimates against actual expense, from the
//     Public Accounts' Schedule of Voted Appropriations by Ministry (research/finance/estimates/).
//
// Figures are shown as their sources print them. Nothing is added across bodies.

import { useId, useMemo, useState } from 'react'

export const CATEGORY_LABELS = {
  province: 'Province',
  federal: 'Federal',
  'own-source': 'Own revenue',
  'other-entity': 'Other public bodies',
  investment: 'Investment income',
  'deferred-capital-amortization': 'Capital grants recognized',
  other: 'Other'
}
const CATEGORY_NOTES = {
  province: 'ministries of the Province, including the Medical Services Plan',
  'other-entity': 'other bodies in the Province’s reporting entity, such as other health authorities',
  'deferred-capital-amortization': 'capital grants received in earlier years and recognized as the assets are used',
  'own-source': 'fees, tuition, sales and other earned revenue'
}

export const fyLabel = (year) => `${year.slice(0, 4)}/${year.slice(5)}`
/** The fiscal year that ends on 31 March of a calendar year, as "2024-25". */
export const fiscalYearEnding = (calendarYear) => `${calendarYear - 1}-${String(calendarYear).slice(2)}`
/** The year on screen if a record has it, else the latest; `years` run newest first. */
export const pickYear = (years, calendarYear) => (calendarYear && years.includes(fiscalYearEnding(Number(calendarYear))) ? fiscalYearEnding(Number(calendarYear)) : years[0])

const whole = (value) => (value === null || value === undefined ? '' : value < 0 ? `(${Math.abs(value).toLocaleString('en-CA')})` : value.toLocaleString('en-CA'))
const UNIT_DIVISOR = { dollars: 1, thousands: 1000, millions: 1000000 }
const UNIT_LABEL = { dollars: '$', thousands: '$ thousands', millions: '$ millions' }
const share = (part, total) => (total ? `${((part / total) * 100).toFixed(1)}%` : '')

/** A choice of fiscal year, newest first. */
const YearSelect = ({ years, value, onChange, label }) => {
  const id = useId()
  if (years.length < 2) return <span className="gov-money__year">{fyLabel(value)}</span>
  return (
    <label className="gov-money__select" htmlFor={id}>
      <span className="gov-money__visually-hidden">{label}</span>
      <select id={id} value={value} onChange={(event) => onChange(event.target.value)}>
        {years.map((year) => <option key={year} value={year}>{fyLabel(year)}</option>)}
      </select>
    </label>
  )
}

/** One stacked bar: segments in order, each a share of the total. A picture of the list below it. */
const Stack = ({ segments, total, label }) => (
  <svg className="gov-money__stack" viewBox="0 0 100 10" preserveAspectRatio="none" role="img" aria-label={label}>
    {segments.reduce((out, segment) => {
      const x = out.at ?? 0
      const width = total ? (Math.max(0, segment.amount) / total) * 100 : 0
      out.items.push(<rect key={segment.key} x={x} y="0" width={Math.max(0, width - 0.25)} height="10" className={segment.className} style={segment.style}><title>{segment.title}</title></rect>)
      out.at = x + width
      return out
    }, { items: [], at: 0 }).items}
  </svg>
)

const PageLink = ({ url, page, children }) => (
  <a href={`${url}#page=${page.pdf}`} target="_blank" rel="noreferrer">{children}</a>
)
const pageText = (page) => `PDF page ${page.pdf}${page.printed ? ` (printed page ${page.printed})` : ''}`

export const Breakdown = ({ records, calendarYear }) => {
  const years = records.map((record) => record.year)
  const [year, setYear] = useState(() => pickYear(years, calendarYear))
  const record = records.find((each) => each.year === year) ?? records[0]
  const divisor = UNIT_DIVISOR[record.unit]
  const revenueTotal = record.revenueTotal.amount
  const expenseTotal = record.expenseTotal.amount
  const byCategory = useMemo(() => {
    const totals = new Map()
    for (const line of record.revenue) totals.set(line.category, (totals.get(line.category) ?? 0) + line.amount)
    return Object.keys(CATEGORY_LABELS).filter((key) => totals.has(key)).map((key) => ({ key, amount: totals.get(key) }))
  }, [record])
  // Revenue lines in category order, so each category is one run of colour in the bar.
  const ordered = Object.keys(CATEGORY_LABELS).flatMap((key) => record.revenue.filter((line) => line.category === key))
  const printed = (amount) => whole(amount / divisor)
  const heading = useId()
  return (
    <section className="gov-money__part" aria-labelledby={heading}>
      <div className="gov-money__head">
        <h3 id={heading} className="gov-card__subheading">Revenue and expense</h3>
        <YearSelect years={years} value={record.year} onChange={setYear} label="Fiscal year of the statement" />
      </div>
      <p className="gov-money__about">
        From its audited <PageLink url={record.url} page={record.page}>{record.title || 'statement of operations'}</PageLink>, {pageText(record.page)}, fiscal year {fyLabel(record.year)}.
        {' '}Lines are as the statement prints them, in <strong>{UNIT_LABEL[record.unit]}</strong>.
      </p>

      <figure className="gov-money__figure">
        <figcaption className="gov-money__caption"><span>Revenue by source</span><span>{printed(revenueTotal)}</span></figcaption>
        <Stack
          label={`Revenue by source, ${fyLabel(record.year)}: ${byCategory.map((each) => `${CATEGORY_LABELS[each.key]} ${share(each.amount, revenueTotal)}`).join(', ')}`}
          total={revenueTotal}
          segments={ordered.map((line, at) => ({ key: `${line.label}-${at}`, amount: line.amount, className: `gov-money__seg gov-money__seg--${line.category}`, title: `${line.label}: ${printed(line.amount)} (${share(line.amount, revenueTotal)})` }))}
        />
        <ul className="gov-money__legend gov-money__legend--categories">
          {byCategory.map((each) => (
            <li key={each.key} title={CATEGORY_NOTES[each.key]}><i className={`gov-money__swatch gov-money__seg--${each.key}`} />{CATEGORY_LABELS[each.key]} <span className="gov-muted">{share(each.amount, revenueTotal)}</span></li>
          ))}
        </ul>
      </figure>
      <table className="gov-money__lines">
        <caption className="gov-money__visually-hidden">Revenue lines, {UNIT_LABEL[record.unit]}</caption>
        <thead><tr><th scope="col">As the statement lists it</th><th scope="col">Category</th><th scope="col">{UNIT_LABEL[record.unit]}</th></tr></thead>
        <tbody>
          {ordered.map((line, at) => (
            <tr key={`${line.label}-${at}`}>
              <th scope="row"><i className={`gov-money__swatch gov-money__seg--${line.category}`} />{line.label}</th>
              <td className="gov-money__category">{CATEGORY_LABELS[line.category]}</td>
              <td>{printed(line.amount)}</td>
            </tr>
          ))}
          <tr className="gov-money__total"><th scope="row">{/^\(total/.test(record.revenueTotal.label) ? 'Total revenue' : record.revenueTotal.label}</th><td className="gov-money__category" /><td>{printed(revenueTotal)}</td></tr>
        </tbody>
      </table>

      <figure className="gov-money__figure">
        <figcaption className="gov-money__caption"><span>Expense{record.expenseBasis === 'object' ? ' by type' : ' by function'}</span><span>{printed(expenseTotal)}</span></figcaption>
        <Stack
          label={`Expense, ${fyLabel(record.year)}: ${record.expense.map((line) => `${line.label} ${share(line.amount, expenseTotal)}`).join(', ')}`}
          total={expenseTotal}
          segments={record.expense.map((line, at) => ({ key: `${line.label}-${at}`, amount: line.amount, className: 'gov-money__seg gov-money__seg--expense', style: { opacity: Math.max(0.28, 1 - at * 0.14) }, title: `${line.label}: ${printed(line.amount)} (${share(line.amount, expenseTotal)})` }))}
        />
      </figure>
      <table className="gov-money__lines">
        <caption className="gov-money__visually-hidden">Expense lines, {UNIT_LABEL[record.unit]}</caption>
        <thead><tr><th scope="col">As the statement lists it</th><th scope="col">Share</th><th scope="col">{UNIT_LABEL[record.unit]}</th></tr></thead>
        <tbody>
          {record.expense.map((line, at) => (
            <tr key={`${line.label}-${at}`}>
              <th scope="row"><i className="gov-money__swatch gov-money__seg--expense" style={{ opacity: Math.max(0.28, 1 - at * 0.14) }} />{line.label}</th>
              <td className="gov-money__category">{share(line.amount, expenseTotal)}</td>
              <td>{printed(line.amount)}</td>
            </tr>
          ))}
          <tr className="gov-money__total"><th scope="row">{/^\(total/.test(record.expenseTotal.label) ? 'Total expense' : record.expenseTotal.label}</th><td className="gov-money__category" /><td>{printed(expenseTotal)}</td></tr>
          <tr className="gov-money__total"><th scope="row">{record.surplus.label}</th><td className="gov-money__category" /><td>{printed(record.surplus.amount)}</td></tr>
        </tbody>
      </table>
      <p className="gov-muted gov-money__note">The categories are this site’s grouping of the statement’s own lines. “Province” is the ministries’ funding the statement recognizes as revenue; “Capital grants recognized” is earlier capital funding recognized over time.{record.note ? ` ${record.note}` : ''}</p>
    </section>
  )
}

/** Totals across years, as small bars; the chosen year is marked. A picture of the figures beside it. */
const YearBars = ({ points, chosen, label }) => {
  const max = Math.max(1, ...points.flatMap((point) => point.values.map((value) => Math.abs(value ?? 0))))
  const step = 10
  const height = 40
  const series = points[0]?.values.length ?? 1
  const width = (step - 2) / series
  return (
    <svg className="gov-money__bars gov-money__bars--small" viewBox={`0 0 ${points.length * step} ${height}`} preserveAspectRatio="none" role="img" aria-label={label}>
      {points.map((point, at) => (
        <g key={point.year} className={point.year === chosen ? 'gov-money__bar-chosen' : undefined}>
          {point.values.map((value, which) => {
            const h = (Math.abs(value ?? 0) / max) * height
            return <rect key={which} className={`gov-money__bar gov-money__bar--s${which}`} x={at * step + 1 + which * width} width={width - 0.4} y={height - h} height={h}><title>{`${fyLabel(point.year)}: ${point.titles[which]}`}</title></rect>
          })}
        </g>
      ))}
    </svg>
  )
}

export const FromMinistries = ({ records, calendarYear, statementProvince }) => {
  const years = records.map((record) => record.year)
  const [year, setYear] = useState(() => pickYear(years, calendarYear))
  const record = records.find((each) => each.year === year) ?? records[0]
  const heading = useId()
  const payees = [...new Set(record.rows.map((row) => row.payee))]
  const recognized = statementProvince?.[record.year]
  const chronological = [...records].reverse()
  return (
    <section className="gov-money__part" aria-labelledby={heading}>
      <div className="gov-money__head">
        <h3 id={heading} className="gov-card__subheading">From ministries</h3>
        <YearSelect years={years} value={record.year} onChange={setYear} label="Fiscal year of the payments" />
      </div>
      <p className="gov-money__about">
        Cash the Province’s ministries paid it in fiscal year {fyLabel(record.year)}, from the <a href={record.url} target="_blank" rel="noreferrer">Government Transfers schedule for the year ended 31 March {record.fye}</a>.
        {' '}The schedule lists only payees paid <strong>$25,000 or more</strong> in the year. Cash paid need not equal the revenue the body recognizes: capital grants, for one, are recognized over the life of what they buy.
      </p>
      {records.length > 1 && <YearBars
        points={chronological.map((each) => ({ year: each.year, values: [each.total], titles: [`$${each.total.toLocaleString('en-CA')}`] }))}
        chosen={record.year}
        label={`Total paid by ministries each fiscal year, ${fyLabel(chronological[0].year)} to ${fyLabel(chronological.at(-1).year)}`}
      />}
      <table className="gov-money__lines">
        <caption className="gov-money__visually-hidden">Paid by ministry, {fyLabel(record.year)}, dollars</caption>
        <thead><tr><th scope="col">Ministry, as printed</th><th scope="col">$</th></tr></thead>
        <tbody>
          {record.rows.map((row, at) => (
            <tr key={`${row.ministry}-${row.payee}-${at}`}><th scope="row">{row.ministry}</th><td>{row.amount.toLocaleString('en-CA')}</td></tr>
          ))}
          {record.rows.length > 1 && <tr className="gov-money__total"><th scope="row">Total paid</th><td>{record.total.toLocaleString('en-CA')}</td></tr>}
        </tbody>
      </table>
      <p className="gov-muted gov-money__note">
        Paid to {payees.map((payee) => `“${payee}”`).join(', ')}, as the schedule spells it.
        {recognized ? ` Its statement for the same year recognizes $${recognized.toLocaleString('en-CA')} as revenue from the Province (the lines marked “Province” above).` : ''}
      </p>
    </section>
  )
}

export const BudgetActual = ({ records, calendarYear }) => {
  const years = records.map((record) => record.year)
  const [year, setYear] = useState(() => pickYear(years, calendarYear))
  const record = records.find((each) => each.year === year) ?? records[0]
  const heading = useId()
  const sum = (votes, key) => votes.reduce((total, vote) => total + (vote[key] ?? 0), 0)
  const chronological = [...records].reverse()
  const shared = record.votes.some((vote) => vote.shared)
  const pages = [...new Set(record.votes.map((vote) => vote.page.pdf))]
  return (
    <section className="gov-money__part" aria-labelledby={heading}>
      <div className="gov-money__head">
        <h3 id={heading} className="gov-card__subheading">Budget and actual</h3>
        <YearSelect years={years} value={record.year} onChange={setYear} label="Fiscal year of the votes" />
      </div>
      <p className="gov-money__about">
        Each vote it spent from in fiscal year {fyLabel(record.year)}: the Estimates the Legislative Assembly voted, the total appropriation after other authorizations, and the actual expense.
        {' '}From the Public Accounts’ <PageLink url={record.url} page={record.votes[0].page}>Schedule of Voted Appropriations by Ministry</PageLink>, PDF page{pages.length > 1 ? 's' : ''} {pages.join(', ')}, in <strong>$ thousands</strong>.
      </p>
      {records.length > 1 && <>
        <YearBars
          points={chronological.map((each) => ({ year: each.year, values: [sum(each.votes, 'estimates'), sum(each.votes, 'actual')], titles: [`Estimates ${whole(sum(each.votes, 'estimates'))} thousand`, `Actual ${whole(sum(each.votes, 'actual'))} thousand`] }))}
          chosen={record.year}
          label={`Estimates and actual expense on its votes each fiscal year, ${fyLabel(chronological[0].year)} to ${fyLabel(chronological.at(-1).year)}`}
        />
        <p className="gov-money__legend">
          <span><i className="gov-money__swatch gov-money__swatch--s0" />Estimates</span>
          <span><i className="gov-money__swatch gov-money__swatch--s1" />Actual</span>
          <span className="gov-muted">{fyLabel(chronological[0].year)} → {fyLabel(chronological.at(-1).year)}</span>
        </p>
      </>}
      <div className="gov-money__scroll" tabIndex={0} role="region" aria-label={`Votes, ${fyLabel(record.year)}, $ thousands`}>
        <table className="gov-money__table">
          <thead>
            <tr><th scope="col">Vote</th><th scope="col">Estimates</th><th scope="col">Appropriation</th><th scope="col">Actual</th><th scope="col">Variance</th></tr>
          </thead>
          <tbody>
            {record.votes.map((vote) => (
              <tr key={`${vote.vote}-${vote.ministry}`}>
                <th scope="row">
                  <a href={`${record.url}#page=${vote.page.pdf}`} target="_blank" rel="noreferrer" title={pageText(vote.page)}>{vote.vote}</a> {vote.description}
                  {vote.shared && <span className="gov-money__tag">shared vote: this ministry’s part</span>}
                </th>
                <td>{whole(vote.estimates)}</td>
                <td>{whole(vote.appropriation)}</td>
                <td>{whole(vote.actual)}</td>
                <td>{whole(vote.variance)}</td>
              </tr>
            ))}
            {record.votes.length > 1 && <tr className="gov-money__total">
              <th scope="row">Total</th>
              <td>{whole(sum(record.votes, 'estimates'))}</td><td>{whole(sum(record.votes, 'appropriation'))}</td><td>{whole(sum(record.votes, 'actual'))}</td><td>{whole(sum(record.votes, 'variance'))}</td>
            </tr>}
          </tbody>
        </table>
      </div>
      <p className="gov-muted gov-money__note">
        {record.names.length ? `Printed as “${record.names.join('”, “')}”. ` : ''}
        Votes only: statutory appropriations and special accounts are not in this schedule. Other authorizations include contingencies and supplementary estimates.
        {shared ? ' After a reorganization several ministries can spend from one vote; a shared vote shows only this ministry’s row.' : ''}
        {' '}Blank cells are blank in the schedule. A negative variance is spending under the appropriation.
      </p>
    </section>
  )
}
