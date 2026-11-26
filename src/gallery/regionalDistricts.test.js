import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { findGalleryEntry } from './collections.js'
import { IDENTITY_COVERAGE, identitySubjectById, relationsOf } from './identityCoverage.js'
import { gallerySections } from './gallerySearch.js'
import { regionalDistrictOf } from './regionalDistricts.js'
import { tileArt } from './tileArt.js'

const districts = IDENTITY_COVERAGE.filter(({ regionalDistrict }) => regionalDistrict)
const currentDistricts = districts.filter(({ regionalDistrict }) => regionalDistrict.current)

test('all 27 districts have current covers in the regional district shelf', () => {
  assert.equal(currentDistricts.length, 27)
  const collections = gallerySections('regional-districts')[0].collections
  const municipalCollections = gallerySections('local')[0].collections
  for (const { id, entries } of currentDistricts) {
    const collection = collections.find((item) => item.id === `collected-${id}`)
    assert.ok(collection, id)
    assert.ok(!municipalCollections.includes(collection), id)
    const cover = entries.find((entry) => entry.id === collection.cover)
    assert.equal(cover.owner, id)
    assert.notEqual(cover.asset.role, 'historical')
  }
})

test('municipal membership resolves across the register, with the former split kept distinct', () => {
  const municipalities = IDENTITY_COVERAGE.filter(({ municipal }) => municipal)
  assert.equal(municipalities.filter(({ municipal }) => municipal.regionalDistrict).length, 161)
  for (const { municipal, label } of municipalities) {
    assert.equal(regionalDistrictOf(municipal)?.name ?? null, municipal.regionalDistrict, label)
  }
  for (const id of ['regional-district-comox-valley', 'regional-district-strathcona']) {
    assert.ok(relationsOf(identitySubjectById(id)).outgoing.some(({ target }) =>
      target.id === 'regional-district-comox-strathcona' && !target.regionalDistrict.current))
  }
  for (const mark of ['rdffg-colour-sponsor-2012', 'bulkley-nechako-seal-2015']) {
    assert.ok(findGalleryEntry(mark), mark)
  }
})

test('district provenance matches local files and raster dark colourways appear on covers', () => {
  for (const { entries } of districts) for (const entry of entries) for (const asset of entry.versions ?? [entry.asset]) {
    const file = readFileSync(new URL(`../../public/${asset.file}`, import.meta.url))
    assert.equal(createHash('sha256').update(file).digest('hex'), asset.sha256, asset.id)
    if (asset.isVector) assert.doesNotMatch(file.toString(), /<image\b/i, asset.id)
  }
  const [entry] = identitySubjectById('regional-district-strathcona').entries
  assert.match(tileArt(entry, 'light'), /strathcona\/signature\.png/)
  assert.match(tileArt(entry, 'dark'), /strathcona\/website\.png/)
})
