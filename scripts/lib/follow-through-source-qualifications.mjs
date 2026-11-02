import { applyCompiledRetentionDecisions } from './salary-data.mjs'
import { createHash } from 'node:crypto'

export const qualificationMetadataFingerprint = (source, employers) => createHash('sha256').update(JSON.stringify([
  source.id, source.url, source.year, source.periodType, source.periodStart, source.periodEnd,
  source.sourceKind, source.scope, source.scopeDescription, source.threshold, source.thresholdComparison,
  source.nameDisclosure, source.positionDisclosure, source.currency, source.completeEmployeeSchedule,
  [...employers].sort()
])).digest('hex')

/** Qualify only explicitly reviewed new source fingerprints; keep old manifests immutable. */
export function applyFollowThroughQualifications (sources, review, employersBySource) {
  if (review?.accepted !== true || review.noOutreach !== true || !Array.isArray(review.decisions)) throw new Error('Additional source qualifications require a reviewed decision')
  const seen = new Set()
  for (const decision of review.decisions) {
    const source = sources[decision.sourceId]
    const employers = employersBySource?.get(decision.sourceId)
    if (seen.has(decision.sourceId) || !source || source.sha256 !== decision.sourceSha256 || source.dataSha256 !== decision.dataSha256 ||
      !Array.isArray(employers) || employers.length !== 1 || employers[0] !== decision.employerSlug ||
      qualificationMetadataFingerprint(source, employers) !== decision.metadataSha256 ||
      !source.sourceKind?.startsWith('official') || source.scope !== 'employee-remuneration' || source.completeEmployeeSchedule !== true ||
      decision.approvedBy !== 'root' || decision.completeEmployeeSchedule !== true || decision.retainCompiledPartition !== true || !decision.reason?.trim()) {
      throw new Error(`Additional source qualification is stale or invalid: ${decision.sourceId}`)
    }
    seen.add(decision.sourceId)
    source.publicWarning = [source.publicWarning, decision.reason].filter(Boolean).join(' ')
    source.validation = { ...source.validation, completeEmployeeSchedule: true, compiledPartitionRetained: true, compiledPartitionRetentionReason: decision.reason }
  }
  applyCompiledRetentionDecisions(sources, review)
}
