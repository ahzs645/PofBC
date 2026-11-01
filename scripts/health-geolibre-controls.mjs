// GeoLibre's real parser/fitter verifies the pixel-scaled exchange files.
import { readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  gcpsToCsv, parseGcpsCsv, solveAffine, gcpResidualsMeters, minGcpsForTransform,
} from '../vendor/geolibre-georeference/georeference.js'

export function geolibreControlReport(manifest) {
  return manifest.images.map((image) => {
    const gcps = image.controls.map((point) => ({ px: point.pixel[0], py: point.pixel[1], lng: point.longitudeLatitude[0], lat: point.longitudeLatitude[1] }))
    const csv = gcpsToCsv(gcps)
    const parsed = parseGcpsCsv(csv)
    if (parsed.length !== gcps.length) throw new Error(`Control CSV did not round-trip: ${image.mapId}`)
    const affine = solveAffine(parsed)
    if (!affine) throw new Error(`GeoLibre could not fit controls: ${image.mapId}`)
    const residuals = gcpResidualsMeters(affine, parsed)
    return { mapId: image.mapId, image: image.file, csv: `${image.mapId}-gcps.csv`, gcps: parsed,
      nativeGeographicAffine: affine, nativeGeographicFitResiduals: residuals,
      independentAccuracyEstablished: false,
      canExportWithCurrentControlCount: Object.fromEntries(['affine', 'polynomial', 'tps'].map((method) => [method, parsed.length >= minGcpsForTransform(method)])),
      note: 'Three controls have no redundant fit check. Polynomial needs six and TPS at least four independently identified controls; do not pad controls with interpolated points.' }
  })
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  const directory = process.argv[2]
  const manifest = JSON.parse(readFileSync(join(directory, 'image-manifest.json'), 'utf8'))
  const reports = geolibreControlReport(manifest)
  for (const report of reports) writeFileSync(join(directory, report.csv), gcpsToCsv(report.gcps))
  writeFileSync(join(directory, 'geolibre-fit-report.json'), JSON.stringify(reports, null, 2) + '\n')
}
