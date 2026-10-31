import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { geoArea, geoContains } from 'd3-geo'
import {
  DEFAULT_AREA_ID, areaById, readHealthPlace, healthMapLink,
  comparisonFor, filterAreas, assetUrl,
} from './healthStoryData.js'
import { forSphericalDrawing, prepareMap, selectionViewBox } from './mapGeometry.js'

const readPublic = (name) => JSON.parse(readFileSync(
  new URL(`../../public/health-geography/${name}`, import.meta.url), 'utf8',
))

test('health-map deep links preserve a valid area and chapter and recover from unknown values', () => {
  const id = 'south-cariboo-community-health-council'
  const link = healthMapLink(id)
  assert.equal(new URLSearchParams(link).get('view'), 'health-map')
  assert.deepEqual(readHealthPlace(link), { area: id, chapter: 'community-councils' })
  assert.deepEqual(readHealthPlace(healthMapLink(id, 'compare-boundaries')), {
    area: id, chapter: 'compare-boundaries',
  })
  assert.deepEqual(readHealthPlace('?area=missing&chapter=missing'), {
    area: DEFAULT_AREA_ID, chapter: 'before-2001',
  })
  assert.deepEqual(readHealthPlace(`?area=${id}&chapter=missing`), {
    area: id, chapter: 'community-councils',
  })
  assert.equal(assetUrl('/maps/example.svg', '/PofBC/'), '/PofBC/health-geography/maps/example.svg')
})

test('the unresolved Nisga’a label is looked up by source map and legend number rather than null identity', () => {
  const area = areaById('nisgaa-source-area')
  assert.ok(area)
  assert.equal(area.bodyId, null)
  const comparison = readPublic('boundary-comparison.json')
  const expected = comparison.bodyMatches.find((row) => row.bodyId === null && row.sourceLegendNumber === 32)
  assert.ok(expected)
  const unrelated = { ...expected, sourceLegendNumber: 1 }
  assert.equal(comparisonFor({ bodyMatches: [unrelated, expected] }, area.id), expected)
  assert.equal(comparisonFor({ bodyMatches: [unrelated] }, area.id), null)
  assert.equal(comparisonFor(comparison, 'not-a-source-area'), null)
})

test('Cariboo filtering respects the council category and returns its two matching council labels', () => {
  const results = filterAreas('  CARIBOO  ', 'councils')
  assert.deepEqual(results.map((area) => area.id).sort(), [
    'central-cariboo-chilcotin-health-council',
    'south-cariboo-community-health-council',
  ])
  assert.ok(results.every((area) => area.mapId === 'councils'))
  assert.equal(filterAreas('Cariboo', 'societies').length, 1)
  assert.deepEqual(filterAreas('missing health area', 'councils'), [])
})

test('D3 spherical winding normalization preserves a local polygon and its hole without modifying the source', () => {
  const polygon = {
    type: 'Feature', properties: { code: 'example' },
    geometry: { type: 'Polygon', coordinates: [
      [[-125, 50], [-123, 50], [-123, 52], [-125, 52], [-125, 50]],
      [[-124.5, 50.5], [-124.5, 51.5], [-123.5, 51.5], [-123.5, 50.5], [-124.5, 50.5]],
    ] },
  }
  const source = structuredClone(polygon)
  assert.ok(geoArea(polygon) > 2 * Math.PI, 'the RFC7946 fixture exercises the opposite D3 winding')
  const normalized = forSphericalDrawing(polygon)
  assert.ok(geoArea(normalized) > 0 && geoArea(normalized) < 2 * Math.PI)
  assert.equal(geoContains(normalized, [-124.8, 51]), true, 'the polygon interior remains filled')
  assert.equal(geoContains(normalized, [-124, 51]), false, 'the hole remains empty')
  assert.equal(geoContains(normalized, [-130, 51]), false, 'the rest of the globe is excluded')
  assert.deepEqual(polygon, source, 'source coordinates are preserved')
  const multi = { ...polygon, geometry: { type: 'MultiPolygon', coordinates: [polygon.geometry.coordinates] } }
  const normalizedMulti = forSphericalDrawing(multi)
  assert.ok(geoArea(normalizedMulti) < 2 * Math.PI)
  assert.equal(geoContains(normalizedMulti, [-124, 51]), false)
})

test('all 89 modern LHA features produce finite SVG paths and usable selection view boxes', () => {
  const collection = readPublic('display-lha.geojson')
  const original = JSON.stringify(collection)
  const map = prepareMap(collection)
  assert.equal(map.features.length, 89)
  for (const feature of map.features) {
    const label = feature.properties.code
    const path = map.path(feature)
    assert.equal(typeof path, 'string', label)
    assert.ok(path.length > 0, `${label} has a visible path`)
    assert.doesNotMatch(path, /NaN|Infinity/, `${label} contains finite projected coordinates`)
    const box = selectionViewBox(map.path, [feature], map.width, map.height)
    assert.equal(box.length, 4)
    assert.ok(box.every(Number.isFinite), `${label} has a finite view box`)
    assert.ok(box[2] > 0 && box[3] > 0, `${label} has a positive view-box extent`)
  }
  assert.deepEqual(selectionViewBox(map.path, [], map.width, map.height), [0, 0, 800, 650])
  assert.equal(JSON.stringify(collection), original, 'projection does not rewrite the stored GeoJSON')
})
