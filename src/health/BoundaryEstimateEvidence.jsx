import { assetUrl } from './healthStoryData.js'

const asset = (path) => assetUrl(path, import.meta.env.BASE_URL)
const methodNames = { 'modern-single': 'Predefined modern area', 'modern-combination': 'Combination of predefined modern areas', 'source-drawn': 'Approximation traced from the historical drawing' }
export const comparisonLayerNames = { lha: 'Local health areas', hsda: 'Service delivery areas', ha: 'Health authorities', municipalities: 'Municipalities', regionalDistricts: 'Regional districts', schoolDistricts: 'School districts' }

export function estimateFor(report, areaId) {
  return report?.assessments.find((entry) => entry.areaId === areaId)
}

export function BoundaryEstimateEvidence({ report, area }) {
  const assessment = estimateFor(report, area.id)
  if (!assessment) return null
  const definition = assessment.definition
  const alignmentReview = report.alignmentReviews?.[area.id]
  const working = alignmentReview?.workingAlignment
  return <section className="health-estimate-evidence" aria-label={`Working estimate for ${area.sourceLabel}`}>
    <h3>Best available working estimate</h3>
    <p><strong>{methodNames[assessment.method]}</strong> · {assessment.confidence} confidence in the display approximation; legal boundary unverified.</p>
    <p>{assessment.reason}</p>
    {alignmentReview && <p className="health-notice">The previous 29% comparison is withdrawn: Richmond was missing from the source trace. Both components are now included without modern-land clipping. {working?.enabled ? `The working trace now applies a provisional ${working.northShiftMetres / 1000} km northward local adjustment.` : 'Local alignment remains unverified.'} <a href={`${asset('comparisons.html')}#${area.id}/lha/${working?.northShiftMetres ?? 0}`} target="_blank" rel="noreferrer">Open the reference map and both traces ↗</a></p>}
    {working?.enabled && <><dl className="health-match-facts"><div><dt>Adjusted trace / modern LHA reference overlap</dt><dd>{Math.round(assessment.workingDrawingVsModernCandidate.iou * 100)}% · provisional local alignment</dd></div><div><dt>Original trace / same reference</dt><dd>{Math.round(assessment.sourceDrawingVsModernCandidate.iou * 100)}% · global registration retained</dd></div></dl>
      <figure className="health-source-inset"><img src={asset('vancouver-richmond-source-detail.png')} alt="Original published inset showing Vancouver and Richmond both labelled 9." /><figcaption>Original inset: Vancouver and Richmond both carry the map number 9. The inset itself has not been georeferenced.</figcaption></figure>
      <p className="health-small"><a href={asset(working.downloadFile)} download>Download reference map + original and adjusted traces ↓</a>{' · '}<a href={asset('geolibre/vancouver-richmond-alignment.geolibre')} download>Download GeoLibre alignment workspace ↓</a></p>
    </>}
    {assessment.method !== 'source-drawn' && <p className="health-small">Modern LHA codes: {assessment.modernLhaCodes.join(', ')}. Their combined intersection-over-union with the original, unadjusted source drawing is {Math.round(assessment.sourceDrawingVsModernCandidate.iou * 100)}%.</p>}
    {definition ? <details className="health-details"><summary>What sets this boundary in the written record?</summary>
      <p><a href={definition.sourceUrl} target="_blank" rel="noreferrer">{definition.heading} ↗</a><br />{definition.dateContext}</p>
      {definition.relatedEntityOnly && <p className="health-notice">This definition belongs to a related statutory council. Its identity with the map’s Nisga’a health authority label remains unresolved.</p>}
      <p>{definition.summary}</p>
      {definition.namedWaterFeatures?.length > 0 && <p><strong>Water features to trace:</strong> {definition.namedWaterFeatures.join('; ')}.</p>}
      {definition.municipalReferences?.length > 0 && <p><strong>Municipal references:</strong> {definition.municipalReferences.join('; ')}.</p>}
      {!definition.relatedEntityOnly && <p className="health-small">The 2001 descriptions postdate the 1997/98 drawing. Earlier orders and amendments must be reconciled before applying a legal edge to the map.</p>}
    </details> : <p className="health-small">A society’s service-area agreement and geographic schedules are still needed. The drawing and constituent council areas support a display estimate only.</p>}
    {report.findings.filter((finding) => finding.areaId === area.id).map((finding) => <p className="health-notice" key={finding.areaId}>{finding.finding} <a href={finding.sourceUrl} target="_blank" rel="noreferrer">Read definition ↗</a></p>)}
    <details className="health-details"><summary>Other boundaries that resemble the drawing</summary>
      <p>Best individual feature in each current layer, screened against the original registration. Overlap is intersection over union with the source drawing, not proof that the territory is the same. A historical area may span multiple features.</p>
      <ul>{Object.entries(comparisonLayerNames).map(([layer, name]) => {
        const best = assessment.currentBoundaryScreening[layer][0]
        return <li key={layer}><strong>{name}:</strong> {best ? `${best.name} (${best.code}) · ${Math.round(best.iou * 100)}% drawing overlap` : 'No intersection in this comparison'}</li>
      })}</ul>
      <p>{assessment.screeningCaveat}</p>
    </details>
    <p className="health-small"><strong>Still needed:</strong> {assessment.remaining}</p>
    <p className="health-small"><a href={`${asset('comparisons.html')}#${area.id}/lha`} target="_blank" rel="noreferrer">Open this comparison side by side ↗</a>{' · '}<a href={asset('estimate-catalogue.csv')} download>All 72 estimates · CSV ↓</a>{' · '}<a href={asset('boundary-estimates.md')} download>Area-by-area boundary review ↓</a></p>
  </section>
}

export function EstimateDownloads({ report }) {
  return <section className="health-estimate-evidence" aria-label="Boundary estimate coverage and downloads">
    <h3>Working geometry for every map label</h3>
    <p>{report.summary.administrativeAreas} administrative estimates, {report.summary.sourceDrawnAreas} independent source-drawing approximations and {report.summary.statisticalRegions} separately labelled statistical illustrations. Screened against {report.summary.comparisonFeatureCount} current features across six boundary types.</p>
    <p>Written territories located: {report.summary.writtenTerritoriesLocated}, plus one related Nisga’a council definition. All historical legal boundaries remain unverified.</p>
    <p><a className="health-button health-button--quiet" href={asset('comparisons.html')} target="_blank" rel="noreferrer">Explore all 52 comparisons side by side ↗</a></p>
    <ul>{[['best-estimates.geojson', '52 best working estimates'], ['source-drawn-estimates.geojson', '52 source-drawing approximations'], ['statistical-region-estimates.geojson', '20 statistical illustrations'], ['estimate-catalogue.csv', 'All 72 estimates as CSV'], ['boundary-estimates.md', 'Definitions, choices and remaining records']].map(([file, label]) => <li key={file}><a href={asset(file)} download>{label} ↓</a></li>)}</ul>
    <p className="health-notice">These are provisional display geometries. Mixed source and modern edges can overlap. Marine jurisdiction, southern insets, dated cadastral references and legal amendments still need review.</p>
  </section>
}
