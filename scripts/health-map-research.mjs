// Compile the evidence review without promoting candidate geography to verified history.
export function buildHealthResearch(catalogue, comparison, plan) {
  const sources = [...comparison.sources, ...plan.sources]
  const sourceIds = new Set(sources.map((source) => source.id))
  const areaIds = new Set(catalogue.areas.map((area) => area.id))
  const taskIds = new Set(plan.workItems.map((item) => item.id))
  if (sourceIds.size !== sources.length || taskIds.size !== plan.workItems.length) throw new Error('Duplicate research source or work item')
  for (const entry of [...plan.usableNow, ...plan.assumptions, ...plan.workItems]) {
    for (const id of entry.sourceIds) if (!sourceIds.has(id)) throw new Error(`Unknown research source: ${id}`)
  }
  for (const item of plan.workItems) {
    if (!['analysis', 'records'].includes(item.kind)) throw new Error(`Unknown work type: ${item.id}`)
    if (!item.areaIds.length) throw new Error(`No area scope: ${item.id}`)
    for (const id of item.areaIds) if (id !== '*' && !areaIds.has(id)) throw new Error(`Unknown work area: ${id}`)
    if (item.kind === 'records' && !item.requestText) throw new Error(`Missing request draft: ${item.id}`)
  }
  const mapIds = { boards: 'oag-1997-98-exhibit-3', councils: 'oag-1997-98-exhibit-4', societies: 'oag-1997-98-exhibit-5' }
  const assessments = catalogue.areas.map((area) => {
    const match = comparison.bodyMatches.find((row) => row.mapId === mapIds[area.mapId] && row.sourceLegendNumber === area.number)
    if (!match) throw new Error(`Missing comparison: ${area.id}`)
    const workItemIds = plan.workItems.filter((item) => item.areaIds.includes('*') || item.areaIds.includes(area.id)).map((item) => item.id)
    if (!workItemIds.length) throw new Error(`Missing research coverage: ${area.id}`)
    return { areaId: area.id, sourceLabel: area.sourceLabel, identityConfirmed: area.identityConfirmed,
      boundaryIdentityVerified: match.boundaryIdentityVerified, historicalOverlapMeasured: match.historicalOverlapMeasured,
      candidateStatus: match.status, candidateLabel: match.label, assumption: match.explanation,
      sourceIds: match.sourceIds, workItemIds }
  })
  return { ...plan, sources, assessments, coverage: {
    sourceAreas: assessments.length,
    institutionalMatches: assessments.filter((area) => area.identityConfirmed).length,
    verifiedHistoricalBoundaries: assessments.filter((area) => area.boundaryIdentityVerified).length,
    scopeReviewNeeded: assessments.filter((area) => area.candidateStatus === 'scope-review-needed').length,
    analysisItems: plan.workItems.filter((item) => item.kind === 'analysis').length,
    recordsItems: plan.workItems.filter((item) => item.kind === 'records').length,
  } }
}

export function researchMarkdown(plan) {
  const sourceLinks = (ids) => ids.map((id) => {
    const source = plan.sources.find((entry) => entry.id === id)
    return `[${source.title}](${source.url})`
  }).join('; ')
  return `# Health-map evidence review and records to obtain

Reviewed ${plan.reviewedOn}. ${plan.scope}

${plan.requestStatus}

${plan.coverage.sourceAreas} source labels; ${plan.coverage.institutionalMatches} institutional links; ${plan.coverage.verifiedHistoricalBoundaries} verified historical boundaries; ${plan.coverage.scopeReviewNeeded} candidates flagged for extent review.

## What can be shown now

${plan.usableNow.map((item) => `### ${item.title}\n\n${item.statement}\n\nLimit: ${item.limit}\n\nSources: ${sourceLinks(item.sourceIds)}`).join('\n\n')}

## Assumptions retained in the app

${plan.assumptions.map((item) => `### ${item.title}\n\n${item.statement}\n\nTo resolve: ${item.resolution}\n\nSources: ${sourceLinks(item.sourceIds)}`).join('\n\n')}

## Work from existing sources (${plan.coverage.analysisItems})

${plan.workItems.filter((item) => item.kind === 'analysis').map(renderTask).join('\n\n')}

## Records to obtain (${plan.coverage.recordsItems})

Start with public releases, finding aids and direct requests. For provincial records that remain unavailable, confirm the custodian and narrow the FOI scope. No holding, accession, fee or access outcome is confirmed by this plan.

${plan.workItems.filter((item) => item.kind === 'records').map(renderTask).join('\n\n')}

## Area-by-area assumptions

${plan.assessments.map((area) => `### ${area.sourceLabel} (${area.areaId})\n\nInstitutional identity: ${area.identityConfirmed ? 'linked' : 'unresolved'}. Historical boundary: ${area.boundaryIdentityVerified ? 'verified' : 'unverified'}.\n\n${area.assumption}\n\nWork items: ${area.workItemIds.join(', ')}.\n\nSources: ${sourceLinks(area.sourceIds)}`).join('\n\n')}

## Closing an item

Record the retrieved file, source URL or archival/registry reference, retrieval date, checksum where appropriate, page/clause locator, operative date meaning and reuse terms. Check the document against the question and completion evidence above. Update the research inputs and regenerate the catalogue. Receiving a file does not automatically verify a boundary, an identity or a completed transfer.
`
  function renderTask(item) {
    const affected = item.areaIds.includes('*') ? 'All 52 source areas (where applicable)' : item.areaIds.map((id) => plan.assessments.find((area) => area.areaId === id).sourceLabel).join('; ')
    return `### P${item.priority} · ${item.title} (${item.id})\n\nStatus: ${item.status}.\n\nQuestion: ${item.question}\n\nAffected: ${affected}.\n\nNeeded: ${item.recordsNeeded}\n\nDates: ${item.dateRange}.\n\nProposed custodian: ${item.likelyCustodian}. Current custody confirmed: ${item.custodyConfirmed ? 'yes' : 'no'}.\n\nRoute: ${item.route}\n\nCompletion evidence: ${item.completionEvidence}\n\nBasis: ${sourceLinks(item.sourceIds)}${item.requestText ? `\n\nDraft request — not sent:\n\n> ${item.requestText}` : ''}`
  }
}
