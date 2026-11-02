import { displayName } from './people.js'
import { employerAnnotation, employerCurrency } from './recordAnnotations.js'
import { formatMoney } from './money.js'
import { SourceLink } from './DisclosureEvidence.jsx'

export const RecordAnnotation = ({ annotation }) => annotation && (
  <span className="salaries__line">
    {annotation.currency} · {annotation.measure} · excluded from CAD comparisons.{' '}
    {annotation.evidence.map((e, at) => <span key={`${e.url}|${e.pdfPage}`}>
      {at > 0 && ' · '}<a href={`${e.url}#page=${e.pdfPage}`} target="_blank" rel="noreferrer">Currency evidence · p. {e.pdfPage}</a>
    </span>)}
  </span>
)
export const ForeignObservations = ({ rows, employer, years, sources, onPerson }) => rows?.length > 0 && (
  <section className="salaries__records" aria-label="Other currencies">
    <h3 className="salaries__title">Other currencies</h3>
    <p className="salaries__hint salaries__hint--small">These observations retain their published currencies. They are excluded from CAD rankings, averages and growth; no exchange rate is assumed.</p>
    <ul className="salaries__grid salaries__grid--list">
      {rows.map((row, at) => {
        const annotation = employerAnnotation(row, employer, years)
        return <li className="salaries__card salaries__card--still" key={`${row[5]}|${row[6]}|${at}`}>
          <span className="salaries__text">
            <button type="button" className="salaries__link salaries__name" onClick={() => onPerson(row[0])}>{displayName(row[0])}</button>
            <span className="salaries__line">{row[1]} · {years[row[4]]}</span>
            <RecordAnnotation annotation={annotation} />
            <SourceLink sourceId={row[5]} sources={sources} pdfPage={row[6]} />
          </span>
          <span className="salaries__aside">{formatMoney(row[2], '—', employerCurrency(row, employer, years, sources))}</span>
        </li>
      })}
    </ul>
  </section>
)
