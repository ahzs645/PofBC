import { assetUrl } from './healthStoryData.js'

const asset = (name) => assetUrl(name, import.meta.env.BASE_URL)

export function GeoLibreReview({ mapId, compact = false }) {
  return <section className={`health-geolibre-review${compact ? ' is-compact' : ''}`} aria-label="Continue georeferencing in GeoLibre">
    <h3>Continue the alignment in GeoLibre</h3>
    <p className="health-small">Open the prepared project to inspect the original drawings with the modern layers. The package includes three exact image/control-file pairs and three georeferenced GeoTIFFs. The viewer needs internet access; project data and images are embedded.</p>
    {!compact && <p className="health-small">The project also includes all 52 working estimates, their source-drawing approximations, 20 statistical illustrations, and current municipal, regional-district and school-district layers. Enable one historical framework at a time; the estimate layers start hidden.</p>}
    <div className="health-actions">
      <a className="health-button health-button--quiet" href={asset('geolibre/health-map-review.html')} target="_blank" rel="noreferrer">Open GeoLibre review ↗</a>
      <a href={asset('health-geolibre-review.zip')} download>Download the complete review package ↓</a>
      {!compact && <a href={asset('geolibre/health-map-review.geolibre')} download>Download GeoLibre project ↓</a>}
    </div>
    {mapId && <p className="health-small">For this source map: <a href={asset(`geolibre/${mapId}-source.png`)} download>original image crop</a> · <a href={asset(`geolibre/${mapId}-gcps.csv`)} download>GeoLibre control points</a> · <a href={asset(`geolibre/${mapId}-registered.tif`)} download>registered GeoTIFF</a>.</p>}
    <p className="health-small health-muted">Three controls per main map currently support an affine fit. Polynomial/TPS warps need additional independent landmarks. A zero fit residual does not establish accuracy. Edited control files can be imported as separate proposals; they do not silently replace the working boundaries.</p>
  </section>
}
