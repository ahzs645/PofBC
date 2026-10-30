// A disclosed name's years: its pay as a chart, then year by year as a table, with the years it is
// absent from folded into runs that give the reason. Names that only may be the same — a surname with
// compatible initials — are kept apart, below. None of this is a verified employment history.

import { displayName, nameMatch } from './people.js'
import { titleKey } from './positions.js'
import { expenseLabel, GAP_LABELS, gapReason, gapRuns, missingYearMessage, samePeriodKinds, sourceHref } from './coverage.js'
import { SourceLink } from './DisclosureEvidence.jsx'
import { formatMoney as money } from './money.js'
import { PayChart, yearSpan } from './parts.jsx'
import { hasExpenseAmount } from './viewState.js'

/** A position in a record opens that position's page at its employer, in the record's year. */
export const PersonPage = ({ chosen, all, index, back, onEmployer, onRole, onOpenGovernment, remember }) => {
  const employerOf = (row) => index.employers[row[4]]
  const slugOf = (row) => employerOf(row)[3]
  const associated = [...new Set(chosen.rows.map(slugOf))]
  const employers = [...new Map(chosen.rows.map((row) => {
    const [name, , body, slug] = employerOf(row)
    return [slug, { name, body, slug }]
  })).values()]
  const near = all.filter((row) => !chosen.rows.includes(row))
    .map((row) => ({ row, link: nameMatch(row[0], chosen.name) }))
    .filter(({ link }) => link === 'initial' || link === 'partial')
    .map(({ row }) => row)
  const yearLabels = chosen.years.map((at) => index.years[at])
  const hasTruncatedNames = chosen.rows.some((row) => index.sources?.[row[6]]?.nameDisclosure === 'published-truncated-names')
  // The chart plots a year's highest record: where a name has more than one in a year, the table
  // shows them all.
  const points = chosen.years.map((at) => ({ year: at, pay: Math.max(...chosen.rows.filter((row) => row[5] === at).map((row) => row[2])) }))
  // Gaps are counted only among periods of the kinds the name appears in: a name in calendar-year
  // reports has no gap at every fiscal label.
  const missing = samePeriodKinds(index.years, chosen.years).filter((at) => !chosen.years.includes(at))
  const runs = gapRuns(missing, (at) => gapReason(index.coverage, associated, at))
  const lines = [
    ...chosen.years.map((at) => ({ at, rows: chosen.rows.filter((row) => row[5] === at).sort((a, b) => b[2] - a[2]) })),
    ...runs.map((run) => ({ at: run.from, run }))
  ].sort((a, b) => b.at - a.at)

  const recordLine = (row, as, rowIndex = 0) => {
    const [employerName, , , slug] = employerOf(row)
    return (
      <div className="salaries-record" key={`${row[5]}-${row[2]}-${row[4]}-${as ?? ''}-${rowIndex}`}>
        <span className="salaries-record__what">
          {row[1] && (titleKey(row[1])
            ? <span className="salaries__name"><button type="button" className="salaries__link" onClick={() => onRole(slug, titleKey(row[1]), row[5])}>{row[1]}</button></span>
            : <span className="salaries__name">{row[1]}</span>)}
          {/* The employer, unless it is the one employer the header names. */}
          {(employers.length > 1 || !employers.some((each) => each.slug === slug)) && (
            <span className={row[1] ? 'salaries__line' : 'salaries__name'}>
              <button type="button" className="salaries__link" onClick={() => onEmployer(slug)}>{employerName}</button>
            </span>
          )}
          {as && <span className="salaries__line">As “{as}”</span>}
        </span>
        <span className="salaries-row__pay">
          {money(row[2])}
          <span className="salaries__line">
            {hasExpenseAmount(row[3]) ? `${expenseLabel(row[6], index.sources)} ${money(row[3])} · ` : ''}
            {sourceHref(index.sources?.[row[6]], row[7])
              ? <SourceLink sourceId={row[6]} sources={index.sources} pdfPage={row[7]} />
              : 'Original source not attached'}
          </span>
        </span>
      </div>
    )
  }

  const heading = displayName(chosen.name, index.sources?.[chosen.latest[6]]?.nameDisclosure)
  remember?.(heading)

  return (
    <section className="salaries__person" aria-labelledby="salaries-person">
      {back}
      <h2 id="salaries-person" className="salaries__heading">{heading}</h2>
      <p className="salaries__note">
        {employers.map((employer, at) => (
          <span key={employer.slug}>
            {at > 0 ? ', ' : ''}
            <button type="button" className="salaries__link" onClick={() => onEmployer(employer.slug)}>{employer.name}</button>
            {employer.body && onOpenGovernment && <> (<button type="button" className="salaries__link" onClick={() => onOpenGovernment(employer.body, Number(index.years[chosen.latest[5]].slice(0, 4)))}>in Government</button>)</>}
          </span>
        ))}
        {' '}· {yearLabels.length} {yearLabels.length === 1 ? 'disclosure period' : 'disclosure periods'}, {yearSpan(yearLabels)} · disclosed as “{chosen.name}”
      </p>
      <p className="salaries__hint salaries__hint--small">
        Records are grouped by the disclosed name only, so they may not all concern one person.
        {chosen.shared ? ' Some years have more than one record under this name: different people, separate payments or source duplicates.' : ''}
        {hasTruncatedNames ? ' At least one source publishes truncated names. The published text is preserved; an incomplete name may hide other records or combine different people.' : ''}
      </p>

      <dl className="salaries__tiles salaries__tiles--three">
        <div><dt>Latest</dt><dd>{money(chosen.latest[2])}</dd><dd className="salaries__line">{index.years[chosen.latest[5]]}</dd></div>
        <div><dt>Highest</dt><dd>{money(Math.max(...points.map((point) => point.pay)))}</dd><dd className="salaries__line">{index.years[points.reduce((best, point) => (point.pay > best.pay ? point : best)).year]}</dd></div>
        <div><dt>Periods</dt><dd>{yearLabels.length}</dd><dd className="salaries__line">of {samePeriodKinds(index.years, chosen.years).length} corresponding periods</dd></div>
      </dl>

      {points.length > 1 && <PayChart years={index.years} points={points} multiple={chosen.shared} />}

      <h3 className="salaries__title salaries__title--spaced">Year by year</h3>
      <ol className="salaries-years">
        {lines.map((line) => line.run
          ? (
            <li key={`gap-${line.run.from}`} className="salaries-years__gap" title={missingYearMessage(index.coverage, associated, line.run.from)}>
              <span className="salaries-years__label">{line.run.from === line.run.to ? index.years[line.run.from] : `${index.years[line.run.from]} – ${index.years[line.run.to]}`}</span>
              <span className="salaries__line">{GAP_LABELS[line.run.reason]}</span>
            </li>
          )
          : (
            <li key={line.at} className="salaries-years__year">
              <span className="salaries-years__label">{index.years[line.at]}</span>
              <span className="salaries-years__records">{line.rows.map((row, at) => recordLine(row, null, at))}</span>
            </li>
          ))}
      </ol>

      {near.length > 0 && (
        <>
          <h3 className="salaries__title salaries__title--spaced">Possible matches</h3>
          <p className="salaries__hint salaries__hint--small">The same surname with compatible initials or given names. These may be the same person or someone else.</p>
          <ol className="salaries-years salaries-years--weak">
            {[...new Set(near.map((row) => row[5]))].sort((a, b) => b - a).map((at) => (
              <li key={at} className="salaries-years__year">
                <span className="salaries-years__label">{index.years[at]}</span>
                <span className="salaries-years__records">{near.filter((row) => row[5] === at).sort((a, b) => b[2] - a[2]).map((row, at) => recordLine(row, row[0], at))}</span>
              </li>
            ))}
          </ol>
        </>
      )}

    </section>
  )
}
