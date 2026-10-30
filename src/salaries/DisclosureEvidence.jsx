import { coverageStatus, disclosurePeriod, scopeLabel, sourceHref, thresholdLabel } from './coverage.js'

const date = (value) => new Intl.DateTimeFormat('en-CA', {
  day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'
}).format(new Date(`${value}T00:00:00Z`))

export const SourceLink = ({ sourceId, sources = {}, pdfPage, label }) => {
  const source = sources[sourceId]
  const href = sourceHref(source, pdfPage)
  const page = Number.isInteger(pdfPage) && pdfPage > 0 && href?.includes('#page=')
  return href
    ? <a href={href} target="_blank" rel="noreferrer" title={source.title}>{label ?? (page ? `Source · p. ${pdfPage}` : 'Source')}</a>
    : null
}

const SourceLeads = ({ coverage }) => (coverage?.sourceLeads?.length > 0 ? (
  <div className="salaries-disclosure__leads">
    <p><strong>Located reports awaiting extraction or review</strong></p>
    {coverage.sourceLeads.map((lead, at) => (
      <p key={`${lead.id ?? lead.url}-${at}`}>
        {sourceHref(lead) ? <a href={lead.url} target="_blank" rel="noreferrer">{lead.title ?? lead.id ?? 'Located report'}</a> : (lead.title ?? lead.id ?? 'Located report')}
        {lead.nextAction ? ` — ${lead.nextAction}` : ''}
        {lead.notes ? ` ${Array.isArray(lead.notes) ? lead.notes.join(' ') : lead.notes}` : ''}
      </p>
    ))}
    <p>These reports have not supplied accepted records for the figures shown here.</p>
  </div>
) : null)

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
        {period ? `Reporting period: ${date(period[0])} – ${date(period[1])}.` : 'The exact reporting period has not been verified; this is a retained compilation label.'}
        {thresholdLabel(coverage) ? ` Reporting ${thresholdLabel(coverage)}.` : ''}
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
      <SourceLeads coverage={coverage} />
    </div>
  )
}

const month = (value) => new Intl.DateTimeFormat('en-CA', { month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T00:00:00Z`))

/**
 * The same evidence as DisclosureEvidence, read at a glance: what was disclosed, for when, above what
 * threshold and where from, on one line; the notes, expense sources and caveats folded under it.
 * `more` adds to what is folded.
 */
export const DisclosureSummary = ({ coverage, sources = {}, className = '', more = null, details = true }) => {
  const period = disclosurePeriod(coverage, sources)
  const ids = [...new Set(coverage?.sourceIds ?? [])]
  // One link a document: two disclosure categories (employees, mayor and council) can share a report.
  const linked = [...new Map(ids.map((id) => sources[id]).filter((source) => source?.url && /^https?:\/\//.test(source.url)).map((source) => [source.url, source])).values()]
  const notes = coverage?.notes ?? []
  const status = coverageStatus(coverage, sources)
  // Records still from the retained compilation have no report of their own to describe: their
  // limits are in the salary documentation (research/salaries/README.md), not repeated on each page.
  if (status.kind === 'compiled') return null
  const expenseEvidence = [...new Map(ids.map((id) => sources[id]).filter((source) => source?.expensesNote || source?.travelSource)
    .map((source) => [`${source.expensesNote ?? ''}|${source.travelSource?.url ?? ''}`, source])).values()]
  const folded = Boolean(notes.length || expenseEvidence.length || coverage?.duplicateRows > 0 || coverage?.sourceLeads?.length || more || (ids.length && !linked.length))
  return (
    <div className={`salaries-disclosure ${className}`}>
      <p className="salaries-disclosure__status" data-kind={status.kind}>{status.label}</p>
      <p className="salaries-disclosure__line">
        <strong>{coverage?.scope ? scopeLabel(coverage.scope) : 'Disclosure details not yet verified'}</strong>
        {period ? <> · {coverage?.periodType === 'calendar' ? 'Calendar year · ' : ''}{month(period[0])} – {month(period[1])}</> : ' · reporting period not verified'}
        {thresholdLabel(coverage) ? ` · ${thresholdLabel(coverage)}` : ''}
        {linked.length > 0 && <> · {linked.map((source, at) => (
          <span key={source.url}>{at > 0 ? ', ' : ''}<a href={source.url} target="_blank" rel="noreferrer" title={source.title}>{linked.length > 1 ? `Source ${at + 1}` : 'Source'}</a></span>
        ))}</>}
        {!ids.length && (coverage?.sourceLeads?.length ? ' · located source links below' : ' · no source document attached')}
      </p>
      {details && folded && (
        <details className="salaries-disclosure__more">
          <summary>About this disclosure</summary>
          {period && <p>Reporting period: {date(period[0])} – {date(period[1])}.</p>}
          {ids.length > 0 && <p>Sources: {ids.map((id, at) => {
            const source = sources[id]
            return <span key={id}>{at > 0 ? '; ' : ''}{source?.url && /^https?:\/\//.test(source.url)
              ? <a href={source.url} target="_blank" rel="noreferrer">{source.title ?? id}</a>
              : (source?.title ?? 'Compiled disclosure; original document not attached')}</span>
          })}.</p>}
          {expenseEvidence.map((source, at) => <p key={`expenses-${at}`}>
            {source.expensesNote}{' '}
            {source.travelSource?.url && /^https?:\/\//.test(source.travelSource.url) && <>
              <a href={source.travelSource.url} target="_blank" rel="noreferrer">Travel expense disclosure</a>
              {source.travelSource.threshold != null ? ` (reporting threshold: $${Number(source.travelSource.threshold).toLocaleString('en-CA')})` : ''}.
            </>}
          </p>)}
          {coverage?.duplicateRows > 0 && <p>{coverage.duplicateRows.toLocaleString('en-CA')} repeated rows are flagged for source review; record counts may exceed the number of people.</p>}
          {notes.map((note, at) => <p key={at}>{note}</p>)}
          <SourceLeads coverage={coverage} />
          {more}
        </details>
      )}
    </div>
  )
}
