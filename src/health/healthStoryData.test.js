import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { geoArea, geoContains } from 'd3-geo'
import {
  AREAS, DEFAULT_AREA_ID, areaById, areasIn, readHealthPlace, healthMapLink, filterAreas, assetUrl, relatedAreas, formatDate,
} from './healthStoryData.js'
import { forSphericalDrawing, prepareMap, selectionViewBox } from './mapGeometry.js'

const readPublic = (name) => JSON.parse(readFileSync(
  new URL(`../../public/health-geography/${name}`, import.meta.url), 'utf8',
))
const catalogue = readPublic('catalogue.json')

test('health-map links carry the layer and area, accept organization ids and recover from unknown values', () => {
  const id = 'south-cariboo-community-health-council'
  const link = healthMapLink(id)
  assert.equal(new URLSearchParams(link).get('view'), 'health-map')
  assert.deepEqual(readHealthPlace(link), { framework: 'councils', area: id })
  assert.deepEqual(readHealthPlace(healthMapLink('northern-health')), { framework: 'authorities-2001', area: 'northern-health-2001' })
  assert.deepEqual(readHealthPlace('?area=missing&layer=missing'), { framework: 'boards', area: DEFAULT_AREA_ID })
  assert.deepEqual(readHealthPlace('?layer=regions-2000'), { framework: 'regions-2000', area: null })
  assert.equal(healthMapLink('not-an-area'), '?view=health-map')
  assert.equal(assetUrl('/maps/example.svg', '/PofBC/'), '/PofBC/health-geography/maps/example.svg')
})

test('every printed map label and every statistical region has exactly one boundary', () => {
  for (const area of catalogue.areas) assert.ok(areaById(area.id), area.id)
  assert.equal(areasIn('boards').length, 11)
  assert.equal(areasIn('councils').length, 34)
  assert.equal(areasIn('societies').length, 7)
  assert.equal(areasIn('regions-2000').length, 20)
  assert.equal(areasIn('authorities-2001').length, 5)
  assert.equal(new Set(AREAS.map((area) => area.id)).size, AREAS.length)
  const nisgaa = areaById('nisgaa-source-area')
  assert.equal(nisgaa.organization, null, 'the Nisga’a label stays unlinked to an organization record')
})

test('boards with councils, and the statistical regions, each cover all 89 LHAs exactly once; the 2001 authorities all but Nisga’a', () => {
  const lhas = readPublic('display-lha.geojson').features.map((feature) => feature.properties.code).sort()
  for (const frameworks of [['boards', 'councils'], ['regions-2000'], ['authorities-2001']]) {
    const codes = frameworks.flatMap(areasIn).flatMap((area) => area.lhaCodes)
    // The Nisga'a area was not part of the 2001 amalgamation.
    const expected = frameworks[0] === 'authorities-2001' ? lhas.filter((code) => code !== '518') : lhas
    assert.deepEqual([...codes].sort(), expected, frameworks.join('+'))
  }
})

test('each society is exactly the union of the councils it served', () => {
  for (const society of areasIn('societies')) {
    const served = relatedAreas(society).find((group) => group.label === 'Council areas it served').areas
    assert.deepEqual(served.flatMap((council) => council.lhaCodes).sort(), [...society.lhaCodes].sort(), society.name)
  }
  const cariboo = areaById('cariboo-community-health-services-society')
  assert.deepEqual(cariboo.organization.successorIds, ['interior-health', 'northern-health'])
})

test('the 2001 authorities are rebuilt from the predecessors that amalgamated into them', () => {
  for (const authority of areasIn('authorities-2001')) {
    for (const id of authority.predecessorIds) assert.ok(areaById(id).organization.successorIds.includes(authority.organization.bodyId))
  }
  // Bella Coola and the Central Coast moved to Vancouver Coastal only in 2002.
  assert.ok(areaById('interior-health-2001').lhaCodes.includes('336'))
  assert.ok(areaById('vancouver-island-health-2001').lhaCodes.includes('337'))
  assert.ok(!areaById('vancouver-coastal-health-2001').lhaCodes.includes('336'))
})

test('the statistical regions follow the printed map: New Westminster in Simon Fraser, Burnaby alone', () => {
  assert.deepEqual(areaById('statistical-region-17').lhaCodes, ['222'])
  assert.ok(areaById('statistical-region-08').lhaCodes.includes('221'))
})

test('search spans names, earlier names and LHA places, and respects the layer filter', () => {
  assert.deepEqual(filterAreas('  CARIBOO  ', 'councils').map((area) => area.id).sort(), [
    'central-cariboo-chilcotin-health-council', 'south-cariboo-community-health-council',
  ])
  assert.ok(filterAreas('Vancouver Health Board').some((area) => area.id === 'vancouver-richmond-health-board'))
  assert.deepEqual(filterAreas('missing health area'), [])
  assert.equal(formatDate('1994-11-17'), '17 November 1994')
  assert.equal(formatDate('1997-03'), 'March 1997')
})

test('every boundary file is a valid collection whose features match the generated index', () => {
  for (const framework of ['boards', 'councils', 'societies', 'regions-2000', 'authorities-2001']) {
    const collection = readPublic(`boundaries/${framework}.geojson`)
    assert.deepEqual(collection.features.map((feature) => feature.id).sort(), areasIn(framework).map((area) => area.id).sort())
    const map = prepareMap(collection)
    for (const feature of map.features) {
      assert.doesNotMatch(map.path(feature), /NaN|Infinity/, feature.id)
      assert.ok(geoContains(feature, feature.properties.labelPoint) || feature.properties.lhaCodes.length > 0, feature.id)
    }
  }
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
