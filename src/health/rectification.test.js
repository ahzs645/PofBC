import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { geoArea } from 'd3-geo'
import { forSphericalDrawing, prepareMap } from './mapGeometry.js'

const publicFile = (name) => new URL(`../../public/health-geography/${name}`, import.meta.url)
const read = (url) => JSON.parse(readFileSync(url, 'utf8'))
const report = read(publicFile('rectification.json'))
const controls = read(new URL('../../research/health-geography/rectification-controls.json', import.meta.url))
const hash = (url) => createHash('sha256').update(readFileSync(url)).digest('hex')

test('registered drawings retain source/reference hashes and honest control limitations', () => {
  assert.equal(report.sourceSha256, hash(publicFile(controls.sourcePdf)))
  assert.equal(report.referenceSha256, hash(publicFile(controls.referenceFile)))
  assert.equal(report.registrations.length, 3)
  for (const page of report.registrations) {
    assert.equal(page.controls.length, 3)
    assert.equal(page.independentRegistrationRmse, null, 'an exact three-control fit has no redundant control')
    assert.equal(page.affineToEpsg3005.length, 6)
    assert.ok(page.affineToEpsg3005.every(Number.isFinite))
    assert.ok(page.controlFitResidualMetres.every((value) => value < .01))
  }
  assert.match(report.limitations.join(' '), /insets are not registered/)
  assert.equal(report.comparisons.length, 18, 'no council polygon scores are fabricated')
  assert.ok(report.comparisons.every((entry) => entry.mapId !== 'councils'))
})

test('registered source GeoJSON matches its manifest and renders finite local paths', () => {
  const context = read(publicFile('display-ha.geojson'))
  const map = prepareMap(context)
  for (const [key, dataset] of Object.entries(report.datasets)) {
    assert.equal(hash(publicFile(dataset.file)), dataset.sha256)
    const collection = read(publicFile(dataset.file))
    assert.equal(collection.features.length, key === 'registeredLines' ? 3 : 18)
    for (const feature of collection.features) {
      assert.equal(feature.properties.geometryStatus, 'registered-source-drawing')
      const path = map.path(forSphericalDrawing(feature))
      assert.ok(path.length > 0)
      assert.doesNotMatch(path, /NaN|Infinity/)
      if (key === 'registeredAreas') {
        assert.ok(geoArea(forSphericalDrawing(feature)) < .1, 'source areas must not fill the globe')
        assert.equal(feature.properties.boundaryIdentityVerified, false)
      } else assert.equal(feature.properties.insetsIncluded, false)
    }
  }
})

test('cartographic scores include uncertainty without certifying predefined boundaries', () => {
  for (const result of report.comparisons) {
    assert.equal(result.boundaryIdentityVerified, false)
    for (const metric of Object.values(result.metrics)) assert.ok(metric >= 0 && metric <= 1)
    const sensitivity = result.translationSensitivity
    assert.ok(sensitivity.radiusMetres >= report.registrations[0].vancouverIslandCoastCheck.p95Metres)
    assert.ok(sensitivity.minIou <= result.metrics.iou && result.metrics.iou <= sensitivity.maxIou)
    assert.equal(result.bestIndividualModernFeature.ha.code.length, 1)
  }
  const peace = report.comparisons.find((row) => row.areaId === 'peace-liard-community-health-services-society')
  assert.equal(peace.bestIndividualModernFeature.hsda.name, 'Northeast')
  assert.ok(peace.metrics.iou > .95)
})
