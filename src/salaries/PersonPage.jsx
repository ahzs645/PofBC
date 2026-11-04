// A disclosed name's years: its pay as a chart, then year by year as a table, with the years it is
// absent from folded into runs that give the reason. Names that only may be the same — a surname with
// compatible initials — are kept apart, below. None of this is a verified employment history.

import { displayName, nameMatch, nameOnly, personKey, withoutCompiledRepeats } from './people.js'
import { titleKey } from './positions.js'
import { expenseLabel, GAP_LABELS, gapReason, gapRuns, missingYearMessage, recordPeriodLabel, samePeriodKinds, sourceHref } from './coverage.js'
import { SourceLink, SourceNotes } from './DisclosureEvidence.jsx'
import { formatMoney as money } from './money.js'
import { PayChart, yearSpan } from './parts.jsx'
import { count, SalaryPageHeading } from './common.jsx'
import { hasExpenseAmount } from './viewState.js'
import { isCadPerson, personAnnotation, personCurrency } from './recordAnnotations.js'
import { RecordAnnotation } from './RecordAnnotation.jsx'

/** A change between two payments as a signed whole percentage, with a true minus sign. */
export const percentChange = (from, to) => {
  if (!Number.isFinite(from) || !Number.isFinite(to) || from <= 0) return null
  const change = Math.round(((to - from) / from) * 100)
  return change === 0 ? '0%' : `${change > 0 ? '+' : '−'}${Math.abs(change)}%`
}

/** A position in a record opens that position's page at its employer, in the record's year. */
export const PersonPage = ({ chosen, joins = [], joinedElsewhere = [], all, scope, index, back, onEmployer, onRole, onPerson, onOpenGovernment, remember }) => {
  // A record under a joined spelling says how it was disclosed.
  const disclosedAs = (row) => (personKey(row[0]) === chosen.key ? null : row[0])
  const sureness = (status) => (status === 'verified' ? 'verified' : 'likely the same person')
  const employerOf = (row) => index.employers[row[4]]
  const slugOf = (row) => employerOf(row)[3]
  // A compiled edition's copy of a record already shown is left out, so a payment is listed once.
  const rows = withoutCompiledRepeats(chosen.rows, index.sources, (row) => personCurrency(row, index))
  const cadRows = rows.filter((row) => isCadPerson(row, index))
  const hasOtherCurrencies = cadRows.length !== rows.length
  // Whether any label still has more than one record once repeats are left out.
  const shared = rows.some((row, at) => rows.findIndex((other) => other[5] === row[5]) !== at)
  const associated = [...new Set(rows.map(slugOf))]
  const employers = [...new Map(rows.map((row) => {
    const [name, , body, slug] = employerOf(row)
    return [slug, { name, body, slug }]
  })).values()]
  // A name this spelling is joined to is linked above, not offered again as a possible match.
  const joinedTo = new Set(joinedElsewhere.map((join) => `${join.employer}|${join.key}`))
  const near = all.filter((row) => !chosen.rows.includes(row) && !joinedTo.has(`${row[4]}|${personKey(row[0])}`))
    .map((row) => ({ row, link: nameMatch(row[0], chosen.name) }))
    .filter(({ link }) => link === 'initial' || link === 'partial')
    .map(({ row }) => row)
    // A period this name already has a record in is covered: a near spelling paid in the same period
    // would be a second salary, so it is most likely someone else and is not offered.
    .filter((row) => !chosen.years.includes(row[5]))
  const yearLabels = chosen.years.map((at) => index.years[at])
  // Compiled-edition records are shown under their plain label, without naming the compilation.
  // Only a record whose own source leaves its period unstated is marked.
  const periodOf = (row) => {
    const period = recordPeriodLabel(index.years[row[5]], index.sources?.[row[6]])
    return period.kind === 'compiled' ? { label: index.years[row[5]], kind: 'verified' } : period
  }
  const hasUnverifiedPeriods = rows.some((row) => periodOf(row).kind !== 'verified')
  const yearLabel = (at) => {
    const labels = rows.filter((row) => row[5] === at).map(periodOf)
    if (labels.some((period) => period.kind !== 'verified')) return `${index.years[at]} · period unverified`
    return index.years[at]
  }
  const hasTruncatedNames = rows.some((row) => index.sources?.[row[6]]?.nameDisclosure === 'published-truncated-names')
  // The chart plots a year's highest record: where a name has more than one in a year, the table
  // shows them all.
  const points = chosen.years.flatMap((at) => {
    const matching = cadRows.filter((row) => row[5] === at)
    return matching.length ? [{ year: at, pay: Math.max(...matching.map((row) => row[2])) }] : []
  })
  // Gaps are counted only among periods of the kinds the name appears in: a name in calendar-year
  // reports has no gap at every fiscal label.
  const periods = samePeriodKinds(index.years, chosen.years)
  const missing = periods.filter((at) => !chosen.years.includes(at))
  // Change from one period to the next, only where both have a single record and nothing missing
  // between them: several records in a year or a gap would make a percentage misleading.
  const single = (at) => rows.filter((row) => row[5] === at).length === 1
  const payAt = (at) => points.find((point) => point.year === at)?.pay
  const changeAt = new Map(chosen.years.map((at) => {
    const before = periods[periods.indexOf(at) - 1]
    return [at, before !== undefined && chosen.years.includes(before) && single(at) && single(before) && payAt(before) > 0 ? percentChange(payAt(before), payAt(at)) : null]
  }))
  const first = points.reduce((low, point) => (!low || point.year < low.year ? point : low), null)
  const last = points.reduce((high, point) => (!high || point.year > high.year ? point : high), null)
  const top = points.reduce((best, point) => (!best || point.pay > best.pay ? point : best), null)
  // Where the latest payment is also the highest, the second tile shows the change since the first
  // period — only when every record is in CAD, so the two ends are comparable.
  const sinceFirst = top && !hasOtherCurrencies && !shared && top.year === last.year && first.year !== last.year && first.pay > 0 ? percentChange(first.pay, last.pay) : null
  const runs = gapRuns(missing, (at) => gapReason(index.coverage, associated, at), periods)
  const lines = [
    ...chosen.years.map((at) => ({ at, rows: rows.filter((row) => row[5] === at).sort((a, b) => b[2] - a[2]) })),
    ...runs.map((run) => ({ at: run.from, run }))
  ].sort((a, b) => b.at - a.at)

  const recordLine = (row, as, rowIndex = 0) => {
    const [employerName, , , slug] = employerOf(row)
    const annotation = personAnnotation(row, index)
    const currency = personCurrency(row, index)
    const details = [
      hasExpenseAmount(row[3]) && `${expenseLabel(row[6], index.sources)} ${money(row[3], '—', annotation?.expenseCurrency ?? currency)}`,
      periodOf(row).kind !== 'verified' && 'Reporting period unverified',
      sourceHref(index.sources?.[row[6]], row[7]) && <SourceLink sourceId={row[6]} sources={index.sources} pdfPage={row[7]} />
    ].filter(Boolean)
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
          {as && <span className="salaries__line">As “{nameOnly(as)}”</span>}
          <RecordAnnotation annotation={annotation} />
        </span>
        <span className="salaries-row__pay">
          {money(row[2], '—', currency)}
          {details.length > 0 && (
            <span className="salaries__line">
              {details.map((detail, at) => <span key={at}>{at > 0 ? ' · ' : ''}{detail}</span>)}
            </span>
          )}
        </span>
      </div>
    )
  }

  const heading = displayName(chosen.name, index.sources?.[chosen.latest[6]]?.nameDisclosure)
  remember?.(heading)

  return (
    <section className="salaries__person" aria-labelledby="salaries-person">
      <SalaryPageHeading id="salaries-person" back={back}>{heading}</SalaryPageHeading>
      <p className="salaries__note">
        {employers.map((employer, at) => (
          <span key={employer.slug}>
            {at > 0 ? ', ' : ''}
            <button type="button" className="salaries__link" onClick={() => onEmployer(employer.slug)}>{employer.name}</button>
            {employer.body && onOpenGovernment && <span className="salaries__nowrap"> (<button type="button" className="salaries__link" onClick={() => onOpenGovernment(employer.body, Number(index.years[chosen.latest[5]].slice(0, 4)))}>in Government</button>)</span>}
          </span>
        ))}
      </p>
      <p className="salaries__note">
        {yearLabels.length} {hasUnverifiedPeriods ? (yearLabels.length === 1 ? 'reporting label' : 'reporting labels') : (yearLabels.length === 1 ? 'disclosure period' : 'disclosure periods')}, {yearSpan(yearLabels)} · {chosen.reviewedName ? 'reviewed name' : 'disclosed as'} “{nameOnly(chosen.name)}”
      </p>
      {scope && (
        <p className="salaries__hint salaries__hint--small">
          Showing records at {scope.employer} only. {count(scope.hidden, 'more record', 'more records')} under this name {scope.hidden === 1 ? 'is' : 'are'} at {count(scope.others, 'other employer', 'other employers')}.{' '}
          <button type="button" className="salaries__link" onClick={scope.onShowAll}>Show every employer</button>
        </p>
      )}
      {joinedElsewhere.map((join) => (
        <p key={`${join.employer}|${join.key}`} className="salaries__hint salaries__hint--small">
          At {index.employers[join.employer][0]} this spelling is joined to{' '}
          <button type="button" className="salaries__link" onClick={() => onPerson?.(join.key)}>{displayName(join.name)}</button>
          {' '}({sureness(join.status)}), whose page holds every spelling.
        </p>
      ))}

      <dl className="salaries__tiles salaries__tiles--three salaries__tiles--person">
        <div><dt>{periodOf(chosen.latest).kind === 'verified' ? 'Latest' : 'Latest label'}</dt><dd>{money(chosen.latest[2], '—', personCurrency(chosen.latest, index))}</dd><dd className="salaries__line">{periodOf(chosen.latest).label}</dd></div>
        {sinceFirst
          ? <div><dt>Change</dt><dd>{sinceFirst}</dd><dd className="salaries__line">since {index.years[first.year]}</dd></div>
          : <div><dt>{hasOtherCurrencies ? 'Highest CAD' : 'Highest'}</dt><dd>{top ? money(top.pay) : '—'}</dd><dd className="salaries__line">{top ? yearLabel(top.year) : 'No comparable CAD observation'}</dd></div>}
        <div><dt>{hasUnverifiedPeriods ? 'Labels' : 'Periods'}</dt><dd>{yearLabels.length}</dd><dd className="salaries__line">of {periods.length} corresponding {hasUnverifiedPeriods ? 'labels' : 'periods'}</dd></div>
      </dl>
      {hasOtherCurrencies && <p className="salaries__hint salaries__hint--small">CAD comparisons exclude observations in other currencies. Their original amounts and currency evidence are listed below; no exchange rate is assumed.</p>}

      {points.length > 1 && <PayChart years={index.years} points={points} multiple={shared} label={hasOtherCurrencies ? 'CAD observations only, by reporting label' : hasUnverifiedPeriods ? 'Disclosed payments by reporting label; some periods are unverified' : undefined} />}

      <h3 className="salaries__title salaries__title--spaced">{hasUnverifiedPeriods ? 'Records by label' : 'Year by year'}</h3>
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
              <span className="salaries-years__label">
                {yearLabel(line.at)}
                {changeAt.get(line.at) && <span className="salaries-years__change">{changeAt.get(line.at)}</span>}
              </span>
              <span className="salaries-years__records">{line.rows.map((row, at) => recordLine(row, disclosedAs(row), at))}</span>
            </li>
          ))}
      </ol>

      {near.length > 0 && (
        <details className="salaries__about salaries__matches">
          <summary className="salaries__title">Possible matches ({near.length})</summary>
          <p className="salaries__hint salaries__hint--small">The same surname with compatible initials or given names, in periods this name has no record. These may be the same person or someone else.</p>
          <ol className="salaries-years salaries-years--weak">
            {[...new Set(near.map((row) => row[5]))].sort((a, b) => b - a).map((at) => (
              <li key={at} className="salaries-years__year">
                <span className="salaries-years__label">{index.years[at]}</span>
                <span className="salaries-years__records">{near.filter((row) => row[5] === at).sort((a, b) => b[2] - a[2]).map((row, at) => recordLine(row, row[0], at))}</span>
              </li>
            ))}
          </ol>
        </details>
      )}

      <details className="salaries__about">
        <summary className="salaries__title">About these records</summary>
        <p className="salaries__hint salaries__hint--small">
          Amounts are payments disclosed for a reporting period, not annual salary rates.
          Records are grouped by the disclosed name only, so they may not all concern one person.
          {shared ? ' Some years have more than one record under this name: different people, separate payments or source duplicates.' : ''}
          {hasTruncatedNames ? ' At least one source publishes truncated names. The published text is preserved; an incomplete name may hide other records or combine different people.' : ''}
        </p>
        {hasUnverifiedPeriods && (
          <p className="salaries__hint salaries__hint--small">Some reporting periods are unverified. Labels on the chart and list do not establish separate payment years.</p>
        )}
        {joins.length > 0 && (
          <div className="salaries__hint salaries__hint--small">
            <p className="salaries__hint salaries__hint--small">Other spellings joined to this name:</p>
            <ul className="salaries__joins">
              {joins.map((join) => (
                <li key={`${join.employer}|${join.name}`} title={join.reason.replace(/^Reviewed: /, '')}>
                  “{nameOnly(join.name)}” at {index.employers[join.employer][0]} · {join.status === 'verified' && /^Reviewed: /.test(join.reason) ? 'verified on review' : sureness(join.status)}
                  {join.evidence?.map((evidence, at) => <span key={`${evidence.sourceId ?? evidence.url}|${evidence.pdfPage ?? ''}`}>{' · '}<SourceLink sourceId={evidence.sourceId} url={evidence.url} sources={index.sources} pdfPage={evidence.pdfPage} label={evidence.pdfPage ? `Evidence${join.evidence.length > 1 ? ` ${at + 1}` : ''} · p. ${evidence.pdfPage}` : 'Identity evidence'} /></span>)}
                </li>
              ))}
            </ul>
          </div>
        )}
        <SourceNotes sourceIds={chosen.rows.map((row) => row[6])} sources={index.sources} />
        {[...new Map(chosen.rows.map((row) => personAnnotation(row, index)).filter(Boolean).map((annotation) => [annotation.id, annotation])).values()].map((annotation) => <p className="salaries__hint salaries__hint--small" key={annotation.id}>{annotation.note}</p>)}
      </details>
    </section>
  )
}
