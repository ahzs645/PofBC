import { assetUrl } from './healthStoryData.js'
import { GeoLibreReview } from './GeoLibreReview.jsx'

const verdicts = {
  'close-cartographic-fit': 'Close cartographic fit under the tested shifts',
  'partial-cartographic-fit': 'Partial or alignment-sensitive fit',
  'poor-cartographic-fit': 'Poor fit to the proposed modern combination',
  'detail-limited': 'Main-map detail too limited for a reuse decision',
}
const percent = (value) => `${Math.round(value * 100)}%`

export function RectificationEvidence({ report, area }) {
  const result = report.comparisons.find((entry) => entry.areaId === area.id)
  const check = report.registrations.find((entry) => entry.vancouverIslandCoastCheck)?.vancouverIslandCoastCheck
  return <section className="health-rectification-evidence" aria-label={`Drawing alignment for ${area.sourceLabel}`}>
    <h3>Does the drawn map fit modern areas?</h3>
    <p className="health-small">Magenta lines align the original main-map drawing to the BC comparison map. Insets are excluded. This initial registration experiment measures predefined modern candidates; the working-estimate review above also includes the council extraction.</p>
    {result ? <>
      <p><strong>{verdicts[result.verdict]}</strong></p>
      <dl className="health-match-facts">
        <div><dt>Drawing / proposed LHA combination overlap</dt><dd>{percent(result.metrics.iou)} intersection over union</dd></div>
        <div><dt>Sensitivity to shifts of {result.translationSensitivity.radiusMetres / 1000} km</dt><dd>{percent(result.translationSensitivity.minIou)}–{percent(result.translationSensitivity.maxIou)} overlap; translation scenarios only</dd></div>
      </dl>
      <p className="health-notice">{result.verdict === 'close-cartographic-fit'
        ? 'The predefined modern combination is a useful approximate display candidate. Keep its modern date and the source drawing visible; this does not verify the historical legal boundary.'
        : 'Keep this as a comparison candidate. Refine the registration, source-path assignment and legal-schedule review before using it to represent the historical territory.'}</p>
      <details className="health-details"><summary>Best individual feature in each modern layer</summary>
        <p>Each result below tests a single feature. A historical area may need several modern features; none is automatically selected or certified.</p>
        <ul>{Object.entries(result.bestIndividualModernFeature).map(([layer, best]) => <li key={layer}>{layer.toUpperCase()}: {best.name} ({best.code}) · {percent(best.iou)} drawing overlap</li>)}</ul>
      </details>
    </> : <p className="health-small">The extended review now provides a source-drawn approximation for all 34 council labels. See the working estimate and current-layer screening above. Small source-space gaps were closed without snapping to modern administrative edges; offshore detail and legal limits still need review.</p>}
    <details className="health-details"><summary>Alignment controls and uncertainty</summary>
      <p>{report.method}</p><p>{report.controlLimitation}</p>
      {check && <p>The board map’s held-out Vancouver Island shoreline check has a median separation of {(check.medianMetres / 1000).toFixed(1)} km and a 95th-percentile separation of {(check.p95Metres / 1000).toFixed(1)} km. These distances include shoreline generalization and reference differences; they are not an independent registration RMSE for all three pages.</p>}
      <p>{report.classificationRule}</p>
      <ul>{report.limitations.map((limit) => <li key={limit}>{limit}</li>)}</ul>
      <a href={assetUrl('rectification.json', import.meta.env.BASE_URL)} download>Download controls, measurements and path assignments ↓</a>
    </details>
    <GeoLibreReview mapId={area.mapId} compact />
  </section>
}
