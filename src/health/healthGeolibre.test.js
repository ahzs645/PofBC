import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { unzipSync } from 'fflate'
import { geolibreControlReport } from '../../scripts/health-geolibre-controls.mjs'
import { parseGcpsCsv, gcpsToCsv, solveAffine } from '../../vendor/geolibre-georeference/georeference.js'

const file = (name) => new URL(`../../public/health-geography/${name}`, import.meta.url)
const read = (name) => JSON.parse(readFileSync(file(name), 'utf8'))
const manifest = read('geolibre/image-manifest.json')
const controls = JSON.parse(readFileSync(new URL('../../research/health-geography/rectification-controls.json', import.meta.url), 'utf8'))

test('GeoLibre images and CSVs use the actual crop origin and resolution', () => {
  assert.equal(manifest.images.length, 3)
  for (const image of manifest.images) {
    const bytes = readFileSync(file(`geolibre/${image.file}`))
    assert.equal(createHash('sha256').update(bytes).digest('hex'), image.sha256)
    assert.equal(bytes.readUInt32BE(16), image.width)
    assert.equal(bytes.readUInt32BE(20), image.height)
    const original = controls.pages.find((page) => page.mapId === image.mapId)
    image.controls.forEach((point, index) => {
      for (let axis = 0; axis < 2; axis++) {
        assert.ok(Math.abs(point.pixel[axis] / image.pixelsPerPdfPoint + image.pageOrigin[axis] - original.controls[index].pagePoint[axis]) < 1e-6)
      }
    })
    const csv = readFileSync(file(`geolibre/${image.mapId}-gcps.csv`), 'utf8')
    assert.equal(gcpsToCsv(parseGcpsCsv(csv)), csv)
    assert.equal(image.warp.independentAccuracyEstablished, false)
  }
})

test('actual GeoLibre fitting code reports three-control capability without invented accuracy', () => {
  const reports = geolibreControlReport(manifest)
  assert.deepEqual(reports, read('geolibre/geolibre-fit-report.json'))
  for (const report of reports) {
    assert.equal(report.gcps.length, 3)
    assert.ok(report.nativeGeographicFitResiduals.rms < .1)
    assert.equal(report.independentAccuracyEstablished, false)
    assert.deepEqual(report.canExportWithCurrentControlCount, { affine: true, polynomial: false, tps: false })
  }
  assert.equal(solveAffine([{ px: 0, py: 0, lng: 0, lat: 0 }, { px: 1, py: 1, lng: 1, lat: 1 }, { px: 2, py: 2, lng: 2, lat: 2 }]), null)
})

test('GeoLibre project embeds the modern data and projected images without machine-specific paths', () => {
  const project = read('geolibre/health-map-review.geolibre')
  assert.equal(project.layers.length, 16)
  assert.equal(project.basemapStyleUrl, '')
  assert.deepEqual(project.layers.filter((layer) => layer.type === 'geojson').map((layer) => layer.geojson.features.length), [5, 16, 89, 1, 11, 34, 7, 52, 20, 160, 28, 59, 1])
  const images = project.layers.filter((layer) => layer.type === 'image')
  assert.equal(images.length, 3)
  for (const image of images) {
    assert.match(image.source.url, /^data:image\/png;base64,/)
    assert.equal(image.metadata.registration.sourceCrs, 'EPSG:3005')
    assert.equal(image.metadata.registration.displayCrs, 'EPSG:3857')
    assert.equal(image.source.coordinates.length, 4)
    assert.ok(image.source.coordinates.every(([lng, lat]) => Number.isFinite(lng + lat) && Math.abs(lng) <= 180 && Math.abs(lat) <= 90))
  }
  assert.equal(project.metadata.sourceSha256, controls.sourceSha256)
  assert.doesNotMatch(JSON.stringify(project), /\/workspace\/|localhost|file:\/\//)
})

test('the focused alignment workspace retains original and reference geometry with a provisional working trace', () => {
  const project = read('geolibre/vancouver-richmond-alignment.geolibre')
  assert.deepEqual(project.layers.map((layer) => layer.geojson.features.length), [5, 7, 1, 1])
  assert.deepEqual(project.layers.map((layer) => layer.visible), [true, true, false, true])
  assert.equal(project.metadata.northShiftMetres, 5000)
  assert.equal(project.metadata.globalRegistrationChanged, false)
  assert.equal(project.metadata.alignmentStatus, 'provisional-local-display')
})

test('the downloadable package contains matching images, controls, GeoTIFFs and a project', () => {
  const entries = unzipSync(readFileSync(file('health-geolibre-review.zip')))
  for (const image of manifest.images) {
    for (const name of [image.file, `${image.mapId}-gcps.csv`, image.cog]) assert.ok(entries[name]?.length > 0, name)
    assert.equal(createHash('sha256').update(entries[image.cog]).digest('hex'), image.cogSha256)
  }
  for (const name of ['health-map-review.geolibre', 'health-map-review.html', 'image-manifest.json', 'README.txt']) assert.ok(entries[name])
  for (const name of ['vancouver-richmond-alignment.geolibre', 'vancouver-richmond-reference-and-traces.geojson', 'vancouver-richmond-source-detail.png']) assert.ok(entries[name])
})
