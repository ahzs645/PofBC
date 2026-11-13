import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { geoContains } from 'd3-geo'
import {
  AREAS, DEFAULT_AREA_ID, areaById, areasIn, readHealthPlace, healthMapLink, filterAreas, assetUrl, relatedAreas, formatDate,
} from './healthStoryData.js'
import { featureBounds, isInside, isSmall, padBounds } from './mapGeometry.js'

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
    for (const feature of collection.features) {
      const box = featureBounds([feature])
      assert.ok(box && box.flat().every(Number.isFinite), `${feature.id} has a finite extent`)
      const [[west, south], [east, north]] = box
      assert.ok(west >= -140 && east <= -113 && south >= 48 && north <= 60.1, `${feature.id} lies in British Columbia`)
      assert.ok(geoContains(feature, feature.properties.labelPoint) || feature.properties.lhaCodes.length > 0, feature.id)
    }
  }
})

test('the map framing helpers measure boxes in longitude and latitude without touching the data', () => {
  const polygon = {
    type: 'Feature', properties: {},
    geometry: { type: 'MultiPolygon', coordinates: [[[[-125, 50], [-123, 50], [-123, 52], [-125, 52], [-125, 50]]], [[[-122, 49], [-121, 49], [-121, 49.5], [-122, 49]]]] },
  }
  const source = structuredClone(polygon)
  assert.deepEqual(featureBounds([polygon]), [[-125, 49], [-121, 52]])
  assert.equal(featureBounds([]), null)
  assert.equal(featureBounds([{ type: 'Feature', geometry: null }]), null)
  assert.deepEqual(polygon, source, 'measuring does not rewrite the stored GeoJSON')
  const padded = padBounds([[-125, 49], [-121, 52]])
  assert.ok(padded[0][0] < -125 && padded[1][1] > 52)
  const tiny = padBounds([[-123, 49], [-123, 49]])
  assert.ok(tiny[1][0] - tiny[0][0] > 0, 'a point still gets a frame')
  const visible = { getWest: () => -130, getEast: () => -115, getSouth: () => 48, getNorth: () => 60 }
  assert.equal(isInside([[-125, 49], [-121, 52]], visible), true)
  assert.equal(isInside([[-135, 49], [-121, 52]], { ...visible, getWest: () => -126 }), false)
  const map = { project: ([x, y]) => ({ x: x * 10, y: -y * 10 }) }
  assert.equal(isSmall([[-123, 49], [-122, 49.5]], map, 40), true)
  assert.equal(isSmall([[-125, 49], [-115, 52]], map, 40), false)
})

test('all 89 modern LHA features have a finite, framable extent', () => {
  const collection = readPublic('display-lha.geojson')
  assert.equal(collection.features.length, 89)
  for (const feature of collection.features) {
    const box = featureBounds([feature])
    assert.ok(box && box.flat().every(Number.isFinite), feature.properties.code)
    const [[west, south], [east, north]] = padBounds(box)
    assert.ok(east > west && north > south, `${feature.properties.code} has a positive frame`)
  }
})
