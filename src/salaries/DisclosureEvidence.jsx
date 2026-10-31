import { coverageStatus, disclosurePeriod, scopeLabel, sourceHref, thresholdLabel } from './coverage.js'

export const SourceLink = ({ sourceId, sources = {}, pdfPage, label }) => {
  const source = sources[sourceId]
  const href = sourceHref(source, pdfPage)
  const page = Number.isInteger(pdfPage) && pdfPage > 0 && href?.includes('#page=')
  return href
    ? <a href={href} target="_blank" rel="noreferrer" title={source.title}>{label ?? (page ? `Source · p. ${pdfPage}` : 'Source')}</a>
    : null
}

const month = (value) => new Intl.DateTimeFormat('en-CA', { month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T00:00:00Z`))

/**
 * A disclosure at a glance, on one line: what was disclosed, for when, above what threshold, and
 * where from. Its notes, caveats and the kind of source behind it are in the salary documentation
 * (research/salaries/README.md and each collection's README), not on the page.
 */
export const DisclosureSummary = ({ coverage, sources = {}, className = '' }) => {
  const period = disclosurePeriod(coverage, sources)
  const ids = [...new Set(coverage?.sourceIds ?? [])]
  // One link a document: two disclosure categories (employees, mayor and council) can share a report.
  const linked = [...new Map(ids.map((id) => sources[id]).filter((source) => source?.url && /^https?:\/\//.test(source.url)).map((source) => [source.url, source])).values()]
  // Records still from the retained compilation have no report of their own to describe.
  if (coverageStatus(coverage, sources).kind === 'compiled') return null
  return (
    <div className={`salaries-disclosure ${className}`}>
      <p className="salaries-disclosure__line">
        <strong>{coverage?.scope ? scopeLabel(coverage.scope) : 'Disclosure details not yet verified'}</strong>
        {period ? <> · {coverage?.periodType === 'calendar' ? 'Calendar year · ' : ''}{month(period[0])} – {month(period[1])}</> : ' · reporting period not verified'}
        {thresholdLabel(coverage) ? ` · ${thresholdLabel(coverage)}` : ''}
        {linked.length > 0 && <> · {linked.map((source, at) => (
          <span key={source.url}>{at > 0 ? ', ' : ''}<a href={source.url} target="_blank" rel="noreferrer" title={source.title}>{linked.length > 1 ? `Source ${at + 1}` : 'Source'}</a></span>
        ))}</>}
        {!ids.length && ' · no source document attached'}
      </p>
    </div>
  )
}
