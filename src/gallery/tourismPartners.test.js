import { test } from 'node:test'
import assert from 'node:assert/strict'
import { browseGallery } from './gallerySearch.js'
import { identitySubjectById, relationsOf } from './identityCoverage.js'
import { TOURISM_SECTOR_RECORDS } from './tourismSectorPartners.js'
import { NORTHERN_TRAVEL_GUIDE_ARTWORK } from './northernTravelGuides.js'
import { findGalleryEntry } from './collections.js'
import { defaultCollectedAsset, tileArt } from './tileArt.js'
import { relatedBodyById } from '../government/relatedBodies.js'

test('VCM keeps its earlier society and Destination BC operation distinct', () => {
  const region = identitySubjectById('vancouver-coast-mountains')
  const society = identitySubjectById('vancouver-coast-mountains-tourism-society')
  assert.ok(relatedBodyById(society.id).historical)
  assert.match(society.note, /9836.*July 31, 2015/)
  assert.deepEqual(society.entries, [])
  assert.equal(relationsOf(region).outgoing.find(({ type }) => type === 'operated-by')?.subject, 'destination-bc')

  const { collections } = browseGallery('', 'tourism')
  const collection = collections.find(({ id }) => id === `collected-${region.id}`)
  const entry = collection.entries.find(({ id }) => id === collection.cover)
  assert.equal(entry.id, 'vcm-stacked')
  assert.deepEqual(entry.versions.map(({ format }) => format), ['svg', 'jpg', 'svg'])
  for (const theme of ['light', 'dark']) {
    assert.equal(defaultCollectedAsset(entry, theme).id, 'vcm-stacked-colour-vector')
    assert.match(tileArt(entry, theme, { cover: true }), new RegExp(`vcm-stacked-colour-vector\\.${theme}\\.svg`))
  }
})

test('the Co-op roster preserves its 15 sector specimens and keeps the operators separately searchable', () => {
  const program = identitySubjectById('destination-bc-co-op-marketing')
  const roster = relationsOf(program).incoming.filter(({ type }) => type === 'listed-by')
  const { collections } = browseGallery('', 'tourism')
  assert.equal(roster.length, 15)
  assert.equal(relationsOf(program).outgoing[0].target.id, 'destination-bc')

  for (const { target } of roster) {
    const record = TOURISM_SECTOR_RECORDS.find(({ id }) => id === target.id)
    const collection = collections.find(({ id }) => id === `collected-${target.id}`)
    const cover = collection.entries.find(({ id }) => id === collection.cover)
    const guidelineDesign = collection.entries.find(({ id }) => id === record.cover)
    if (cover.id !== guidelineDesign.id) assert.ok(cover.asset.isVector && !cover.asset.reconstruction)
    assert.ok(relatedBodyById(target.id).relationships.some(({ id }) => id === program.id))
    assert.ok((guidelineDesign.versions ?? [guidelineDesign.asset]).some(({ versionLabel }) => versionLabel === '2024–25 guidelines · raster'))
  }

  const birdTrail = identitySubjectById('bc-bird-trail')
  assert.equal(relationsOf(birdTrail).outgoing.find(({ type }) => type === 'operated-by').target.id, 'tourism-richmond')
  assert.ok(identitySubjectById('tourism-richmond').entries.every(({ owner }) => owner === 'tourism-richmond'))
})

test('a matching sector vector is the cover and the sourced raster remains selectable', () => {
  const subject = identitySubjectById('mountain-biking-bc')
  const design = subject.entries.find(({ id }) => id === 'mountain-biking-bc-appendix-2024')
  assert.equal(design.asset.id, 'mountain-biking-bc-tagline-vector')
  assert.deepEqual(design.versions.map(({ format }) => format), ['svg', 'png'])
  assert.ok(subject.entries.some(({ id }) => id === 'mountain-biking-bc-website-horizontal'))
  for (const theme of ['light', 'dark']) {
    assert.match(tileArt(design, theme, { cover: true }), new RegExp(`mountain-biking-bc-tagline-vector\\.${theme}\\.svg`))
  }
})

test('travel guide specimens resolve to their designs and retain their cited source and formats', () => {
  for (const asset of Object.values(NORTHERN_TRAVEL_GUIDE_ARTWORK).flat()) {
    const entry = findGalleryEntry(asset.id)
    assert.ok(entry, asset.id)
    assert.ok((entry.versions ?? [entry.asset]).some(({ id }) => id === asset.id), asset.id)
    assert.match(asset.sourcePage, new RegExp(`#page=${asset.extraction.pdfPage}$`))
    if (asset.isVector) {
      assert.equal(asset.format, 'svg')
      assert.ok(asset.extraction.nativePathCount > 0, asset.id)
    }
  }
  const olderAssociation = findGalleryEntry('atbc-hands-and-tagline')
  assert.equal(olderAssociation.asset.id, 'atbc-hands-and-tagline-2012-vector')
  assert.deepEqual(olderAssociation.versions.map(({ format }) => format), ['svg', 'jpg'])
  for (const theme of ['light', 'dark']) {
    assert.match(tileArt(olderAssociation, theme), new RegExp(`atbc-hands-and-tagline-2012-vector\\.${theme}\\.svg`))
  }
})
