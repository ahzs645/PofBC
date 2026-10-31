import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'

const publicFile = (name) => new URL(`../../public/health-geography/${name}`, import.meta.url)
const researchFile = (name) => new URL(`../../research/health-geography/${name}`, import.meta.url)
const readJson = (url) => JSON.parse(readFileSync(url, 'utf8'))
const catalogue = readJson(publicFile('boundary-comparison.json'))
const mapIndex = readJson(researchFile('map-area-index.json'))
const crosswalk = readJson(researchFile('lha-code-crosswalk-1997-scheme-to-2018.json'))
const layers = Object.fromEntries(Object.entries(catalogue.datasets).map(([key, dataset]) => [
  key,
  readJson(publicFile(dataset.file)),
]))
const codes = Object.fromEntries(Object.entries(layers).map(([key, layer]) => [
  key,
  new Set(layer.features.map((feature) => feature.properties.code)),
]))
const matchKey = (row) => `${row.mapId}:${row.sourceLegendNumber}`
const body = (id) => {
  const result = catalogue.bodyMatches.find((row) => row.bodyId === id)
  assert.ok(result, `missing historical body ${id}`)
  return result
}

test('every original administrative-map label has one comparison record, including the unresolved label', () => {
  assert.equal(catalogue.bodyMatches.length, 52)
  assert.equal(new Set(catalogue.bodyMatches.map(matchKey)).size, 52)
  assert.deepEqual(
    catalogue.bodyMatches.map(matchKey).sort(),
    mapIndex.records.map(matchKey).sort(),
  )
  const counts = {}
  for (const row of catalogue.bodyMatches) counts[row.category] = (counts[row.category] ?? 0) + 1
  assert.deepEqual(counts, {
    'regional-health-boards': 11,
    'community-health-councils': 34,
    'community-health-services-societies': 7,
  })
})

test('the offline layers contain the expected modern polygons and match their manifest hashes', () => {
  assert.deepEqual(Object.keys(layers).sort(), ['ha', 'hsda', 'lha'])
  for (const [key, count] of Object.entries({ lha: 89, hsda: 16, ha: 5 })) {
    const dataset = catalogue.datasets[key]
    const layer = layers[key]
    assert.equal(dataset.featureCount, count)
    assert.equal(layer.type, 'FeatureCollection')
    assert.equal(layer.features.length, count)
    assert.equal(codes[key].size, count, `${key} codes must be unique`)
    assert.equal(layer.metadata.historicalGeometry, false)
    assert.equal(layer.metadata.coordinateSystem, 'EPSG:4326')
    assert.equal(
      createHash('sha256').update(readFileSync(publicFile(dataset.file))).digest('hex'),
      dataset.sha256,
      `${key} must match the checked-in manifest`,
    )
    for (const feature of layer.features) {
      assert.equal(typeof feature.properties.code, 'string')
      assert.equal(feature.properties.layer, key)
      assert.equal(feature.properties.geometryStatus, 'modern-pgmaps-comparison')
      assert.ok(['Polygon', 'MultiPolygon'].includes(feature.geometry.type))
      assert.ok(feature.geometry.coordinates.length > 0)
    }
  }
})

test('all selected geography codes and evidence references resolve', () => {
  const sources = new Set(catalogue.sources.map((source) => source.id))
  for (const row of catalogue.bodyMatches) {
    assert.ok(row.candidateLhaCodes.length > 0, matchKey(row))
    for (const [key, field] of [
      ['lha', 'candidateLhaCodes'],
      ['hsda', 'candidateHsdaCodes'],
      ['ha', 'candidateHaCodes'],
    ]) {
      assert.equal(new Set(row[field]).size, row[field].length, `${matchKey(row)} repeats ${field}`)
      for (const code of row[field]) {
        assert.ok(codes[key].has(code), `${matchKey(row)} references missing ${key} ${code}`)
      }
    }
    for (const id of row.sourceIds) assert.ok(sources.has(id), `${matchKey(row)} references missing source ${id}`)
  }
})

test('Nisga’a retains its source-map identity without a fabricated repository body', () => {
  const unresolved = catalogue.bodyMatches.filter((row) => row.bodyId === null)
  assert.equal(unresolved.length, 1)
  const nisgaa = unresolved[0]
  assert.equal(nisgaa.sourceLegendNumber, 32)
  assert.equal(nisgaa.sourceLabel, "Nisga'a Health Authority")
  assert.equal(nisgaa.status, 'identity-unresolved')
  assert.deepEqual(nisgaa.candidateLhaCodes, ['518'])
})

test('the North West society respects the original map’s explicit Nisga’a exclusion', () => {
  const northwest = body('north-west-community-health-services-society')
  assert.ok(!northwest.candidateLhaCodes.includes('518'))
  assert.deepEqual(northwest.candidateHsdaCodes, [], 'the full Northwest HSDA would include Nisga’a')
  assert.equal(northwest.status, 'scope-review-needed')
  assert.match(northwest.explanation, /explicitly excludes Nisga'a Health Authority/)
  const regionalCodes = catalogue.bodyMatches
    .filter((row) => row.category !== 'community-health-councils')
    .flatMap((row) => row.candidateLhaCodes)
  assert.equal(regionalCodes.length, 88)
  assert.equal(new Set(regionalCodes).size, 88)
  assert.deepEqual(
    [...regionalCodes].sort(),
    [...codes.lha].filter((code) => code !== '518').sort(),
  )
})

test('modern candidates and the current-data audit make no historical exact-match or overlap claim', () => {
  for (const row of catalogue.bodyMatches) {
    assert.equal(row.boundaryIdentityVerified, false, matchKey(row))
    assert.equal(row.historicalOverlapMeasured, false, matchKey(row))
    assert.ok(!Object.hasOwn(row, 'metrics'), 'current geometry metrics must not appear as historical body matches')
    assert.doesNotMatch(row.status, /exact|verified|matched/)
    assert.match(row.geometryCaveat, /modern PGMaps dataset/)
  }
  for (const audit of Object.values(catalogue.currentDataAudit)) {
    assert.match(audit.comparison, /not a historical validation/)
  }
  assert.match(catalogue.historicalGeometryStatus, /no historical area-overlap scores/i)
})

test('South Cariboo council uses the documented 100 Mile House identity, not the same-named modern LHA', () => {
  const southCariboo = body('south-cariboo-community-health-council')
  assert.deepEqual(southCariboo.candidateLhaCodes, ['144'])
  assert.ok(!southCariboo.candidateLhaCodes.includes('148'))
  assert.ok(southCariboo.sourceIds.includes('m225-1997'), 'M225/1997 is the rename instrument')
  const rename = catalogue.sources.find((source) => source.id === 'm225-1997')
  assert.equal(rename.url, 'https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/m0225_1997')
  assert.equal(crosswalk.rows.find((row) => row.newCode === '144').oldCode, '025')
  assert.equal(crosswalk.rows.find((row) => row.newCode === '148').oldCode, '030')
})

test('Northern Interior does not absorb historical Quesnel through the modern HSDA grouping', () => {
  const northernInterior = body('northern-interior-regional-health-board')
  assert.deepEqual(northernInterior.candidateLhaCodes, ['522', '523', '524'])
  assert.ok(!northernInterior.candidateLhaCodes.includes('521'))
  assert.deepEqual(northernInterior.candidateHsdaCodes, [])
  assert.ok(body('cariboo-community-health-services-society').candidateLhaCodes.includes('521'))
})
