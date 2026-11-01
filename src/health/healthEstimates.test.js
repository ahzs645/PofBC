import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { forSphericalDrawing, prepareMap } from './mapGeometry.js'

const file = (name) => new URL(`../../public/health-geography/${name}`, import.meta.url)
const read = (name) => JSON.parse(readFileSync(file(name), 'utf8'))
const report = read('estimates-index.json')

test('estimate manifest delivers every geometry and the three additional comparison layers', () => {
  assert.deepEqual(Object.values(report.datasets).map((dataset) => dataset.featureCount), [52, 52, 20, 28, 160, 59, 1])
  for (const dataset of Object.values(report.datasets)) {
    const bytes = readFileSync(file(dataset.file))
    assert.equal(createHash('sha256').update(bytes).digest('hex'), dataset.sha256)
    assert.equal(JSON.parse(bytes).features.length, dataset.featureCount)
  }
})

test('all estimate and extra-layer polygons produce finite, local map paths', () => {
  const { path } = prepareMap(read('display-ha.geojson'))
  for (const dataset of Object.values(report.datasets)) {
    for (const feature of read(dataset.file).features) {
      const normalized = forSphericalDrawing(feature)
      const rendered = path(normalized)
      assert.ok(rendered?.length > 0, feature.properties.name)
      assert.doesNotMatch(rendered, /NaN|Infinity/)
      const [[west, north], [east, south]] = path.bounds(normalized)
      assert.ok(east - west < 1000 && south - north < 1000, feature.properties.name)
    }
  }
})

test('every decision retains legal uncertainty and comparable independent-drawing scores', () => {
  const ids = new Set(read('catalogue.json').areas.map((area) => area.id))
  assert.equal(report.assessments.length, ids.size)
  for (const area of report.assessments) {
    assert.ok(ids.has(area.areaId))
    assert.equal(area.boundaryIdentityVerified, false)
    assert.ok(area.reason.length > 40)
    assert.ok(['low', 'medium'].includes(area.confidence))
    for (const ranked of Object.values(area.currentBoundaryScreening)) {
      assert.ok(ranked.length <= 3)
      ranked.forEach((match, i) => {
        assert.ok(match.iou >= 0 && match.iou <= 1)
        assert.ok(!i || ranked[i - 1].iou >= match.iou)
      })
    }
  }
  assert.equal(report.summary.comparisonFeatureCount, 357)
  assert.equal(report.summary.writtenTerritoriesLocated, 44)
})

test('downloads include decisions for all 72 areas and the remaining acquisition routes', () => {
  const csv = readFileSync(file('estimate-catalogue.csv'), 'utf8').trim().split('\n')
  assert.equal(csv.length, 73)
  const markdown = readFileSync(file('boundary-estimates.md'), 'utf8')
  for (const area of report.assessments) assert.ok(markdown.includes(area.areaId))
  assert.match(markdown, /Records still needed/)
  assert.match(markdown, /FOI/)
  assert.match(markdown, /M87\/1997 is a partial amendment/)
})
