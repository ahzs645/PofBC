import { disclosurePeriod, scopeLabel } from './coverage.js'

const date = (value) => new Intl.DateTimeFormat('en-CA', {
  day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'
}).format(new Date(`${value}T00:00:00Z`))

export const SourceLink = ({ sourceId, sources = {} }) => {
  const source = sources[sourceId]
  return source?.url && /^https?:\/\//.test(source.url)
    ? <a href={source.url} target="_blank" rel="noreferrer" title={source.title}>Source</a>
    : null
}

/** The evidence and reporting boundaries attached to the records currently on screen. */
export const DisclosureEvidence = ({ coverage, sources = {}, className = 'salaries__source' }) => {
  const period = disclosurePeriod(coverage, sources)
  const ids = [...new Set(coverage?.sourceIds ?? [])]
  const notes = coverage?.notes ?? []
  const expenseEvidence = [...new Map(ids.map((id) => sources[id]).filter((source) => source?.expensesNote || source?.travelSource)
    .map((source) => [`${source.expensesNote ?? ''}|${source.travelSource?.url ?? ''}`, source])).values()]
  return (
    <div className={className}>
      <p>
        <strong>{scopeLabel(coverage?.scope)}.</strong>{' '}
        {period ? `Reporting period: ${date(period[0])} – ${date(period[1])}.` : 'The exact reporting period has not been verified; a collection year can include calendar-year and fiscal-year reports.'}
        {coverage?.threshold != null ? ` Reporting threshold: $${Number(coverage.threshold).toLocaleString('en-CA')}.` : ''}
      </p>
      {ids.length > 0 ? (
        <p>
          Sources:{' '}
          {ids.map((id, at) => {
            const source = sources[id]
            return <span key={id}>{at > 0 ? '; ' : ''}{source?.url && /^https?:\/\//.test(source.url)
              ? <a href={source.url} target="_blank" rel="noreferrer">{source.title ?? id}</a>
              : (source?.title ?? 'Compiled disclosure; original document not attached')}</span>
          })}.
        </p>
      ) : <p>An employer-issued source document has not been attached to these records.</p>}
      {expenseEvidence.map((source, at) => <p key={`expenses-${at}`}>
        {source.expensesNote}{' '}
        {source.travelSource?.url && /^https?:\/\//.test(source.travelSource.url) && <>
          <a href={source.travelSource.url} target="_blank" rel="noreferrer">Travel expense disclosure</a>
          {source.travelSource.threshold != null ? ` (reporting threshold: $${Number(source.travelSource.threshold).toLocaleString('en-CA')})` : ''}.
        </>}
      </p>)}
      {coverage?.duplicateRows > 0 && <p>{coverage.duplicateRows.toLocaleString('en-CA')} repeated rows are flagged for source review; record counts may exceed the number of people.</p>}
      {notes.map((note, at) => <p key={at}>{note}</p>)}
    </div>
  )
}
