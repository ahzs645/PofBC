import { useState } from 'react'
import { HEALTH_RESEARCH as research } from './healthResearch.generated.js'
import { areaById, assetUrl } from './healthStoryData.js'
import { GeoLibreReview } from './GeoLibreReview.jsx'
import { EstimateDownloads } from './BoundaryEstimateEvidence.jsx'

const sources = new Map(research.sources.map((source) => [source.id, source]))
const assessments = new Map(research.assessments.map((area) => [area.areaId, area]))
const asset = (path) => assetUrl(path, import.meta.env.BASE_URL)
const kindLabel = { analysis: 'Review existing sources', records: 'Obtain records' }

function Sources({ ids }) {
  return <ul className="health-research-sources">{ids.map((id) => {
    const source = sources.get(id)
    return <li key={id}><a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a></li>
  })}</ul>
}

export function AreaResearchNotes({ areaId }) {
  const area = assessments.get(areaId)
  if (!area) return null
  return <details className="health-details health-area-research">
    <summary>Working assumption and missing evidence</summary>
    <p><strong>Historical boundary {area.boundaryIdentityVerified ? 'verified' : 'unverified'}.</strong> {area.assumption}</p>
    <p>Work still needed for this area:</p>
    <ul>{area.workItemIds.map((id) => {
      const item = research.workItems.find((entry) => entry.id === id)
      return <li key={id}>{item.title} · {kindLabel[item.kind]}</li>
    })}</ul>
    <p><a href="#health-research">Open the research and records list ↓</a></p>
    <Sources ids={area.sourceIds} />
  </details>
}

export function HealthResearchPanel({ selectedAreaId, estimates }) {
  const [kind, setKind] = useState('all')
  const [scope, setScope] = useState('all')
  const selected = areaById(selectedAreaId)
  const items = research.workItems.filter((item) => (kind === 'all' || item.kind === kind)
    && (scope === 'all' || item.areaIds.includes('*') || item.areaIds.includes(selectedAreaId)))
  return <section className="health-research-section" id="health-research" aria-labelledby="health-research-title">
    <div className="health-section-heading">
      <div><p className="health-kicker">Evidence review · {research.reviewedOn}</p><h2 id="health-research-title">What we know, what we assume, what we need</h2></div>
      <a href={asset('records-to-obtain.md')} download>Download review and request drafts ↓</a>
    </div>
    <p className="health-small">This review covers the health maps and their linked institutions. It draws on the repository’s existing evidence; it does not establish new historical boundaries.</p>
    <dl className="health-research-counts">
      <div><dt>Original map labels</dt><dd>{research.coverage.sourceAreas}</dd></div>
      <div><dt>Institutional links</dt><dd>{research.coverage.institutionalMatches}</dd></div>
      <div><dt>Verified historical boundaries</dt><dd>{research.coverage.verifiedHistoricalBoundaries}</dd></div>
      <div><dt>Extents flagged for review</dt><dd>{research.coverage.scopeReviewNeeded}</dd></div>
    </dl>
    {estimates && <EstimateDownloads report={estimates} />}
    <h3>Available to use now</h3>
    <div className="health-research-grid">{research.usableNow.map((item) => <article key={item.title} className="health-research-card">
      <h4>{item.title}</h4><p>{item.statement}</p><p className="health-muted"><strong>Limit:</strong> {item.limit}</p>
      <details className="health-details"><summary>Supporting sources</summary><Sources ids={item.sourceIds} /></details>
    </article>)}</div>
    <details className="health-details"><summary>Assumptions we are keeping explicit</summary>
      {research.assumptions.map((item) => <article key={item.title} className="health-research-assumption">
        <h4>{item.title}</h4><p>{item.statement}</p><p><strong>To resolve:</strong> {item.resolution}</p><Sources ids={item.sourceIds} />
      </article>)}
    </details>
    {selected && <div className="health-selected-research"><h3>Selected area: {selected.sourceLabel}</h3><AreaResearchNotes areaId={selected.id} /></div>}
    <GeoLibreReview />
    <h3>Research and records list</h3>
    <p className="health-small">{research.coverage.analysisItems} tasks start with existing sources; {research.coverage.recordsItems} targets need records or provenance. Try public downloads, archives and direct requests first, then a focused FOI for remaining provincial records.</p>
    <p className="health-notice">{research.requestStatus}</p>
    <div className="health-index-filters">
      <label className="health-field" htmlFor="health-work-kind"><span>Next step</span><select id="health-work-kind" value={kind} onChange={(event) => setKind(event.target.value)}>
        <option value="all">All research and records</option><option value="analysis">Review existing sources</option><option value="records">Obtain records</option>
      </select></label>
      <label className="health-field" htmlFor="health-work-scope"><span>Area scope</span><select id="health-work-scope" value={scope} onChange={(event) => setScope(event.target.value)}>
        <option value="all">All source areas</option><option value="selected">Selected area: {selected?.sourceLabel}</option>
      </select></label>
    </div>
    <p className="health-small" role="status">{items.length} of {research.workItems.length} work items shown</p>
    <div className="health-research-work">{research.workItems.map((item) => <details key={item.id} id={`health-research-${item.id}`} className="health-details health-research-task" hidden={!items.includes(item)}>
      <summary><span className="health-kicker">Priority {item.priority} · {kindLabel[item.kind]} · {({ 'not-requested': 'Not requested', 'not-started': 'Not started', 'in-progress': 'In progress', 'completed-estimate': 'Source estimate available' })[item.status] || item.status}</span>{item.title}</summary>
      <p><strong>Question:</strong> {item.question}</p>
      <p><strong>Records or inputs:</strong> {item.recordsNeeded}</p>
      <p><strong>Dates:</strong> {item.dateRange}</p>
      <p><strong>Areas:</strong> {item.areaIds.includes('*') ? 'All source areas, where applicable.' : item.areaIds.map((id) => areaById(id).sourceLabel).join('; ')}</p>
      <p><strong>Route:</strong> {item.route}</p>
      <p><strong>Proposed custodian:</strong> {item.likelyCustodian}. Current custody is unconfirmed.</p>
      <p><strong>Evidence needed to close:</strong> {item.completionEvidence}</p>
      <Sources ids={item.sourceIds} />
      {item.requestText && <details className="health-details"><summary>Draft request wording — not sent</summary><blockquote className="health-request-draft">{item.requestText}</blockquote></details>}
    </details>)}</div>
    <p className="health-small"><a href={asset('research-plan.json')} download>Download the structured evidence register ↓</a></p>
  </section>
}

export default HealthResearchPanel
