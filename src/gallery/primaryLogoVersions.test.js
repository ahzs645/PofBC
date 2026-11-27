import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { findGalleryEntry } from './collections.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'
import reviewed from './primaryLogoVersions.json' with { type: 'json' }
import { RECOVERY_PACKAGES } from './vectorRecovery.js'

const readPublic = (file) => readFileSync(new URL(`../../public/${file}`, import.meta.url))

test('primary-logo variants preserve the gallery design IDs, published sources, and provenance', () => {
  for (const [id, record] of Object.entries(reviewed)) {
    const entry = findGalleryEntry(id)
    const variant = record.asset
    // A lead whose vector was later extracted and held keeps its raster as a version, upgraded
    // only by that held file (vectorRecovery.js), never by the lead's link.
    const held = RECOVERY_PACKAGES.flatMap((pack) => Object.values(pack.additions ?? {}).flat())
      .find((asset) => asset.id === entry.asset.id && asset.variantOf === id)
    if (!variant && held) {
      assert.equal(entry.id, id)
      assert.ok(entry.versions.some((source) => source.id === id && source.isVector === false), id)
      assert.equal(entry.identity.provenance, 'extracted_from_official_vector')
      for (const source of record.alsoSeen) assert.ok(entry.versions.find((source) => source.id === id).alsoSeen.includes(source))
      continue
    }
    if (!variant) {
      assert.equal(entry.asset.id, id)
      assert.equal(entry.identity.provenance, 'published_raster')
      assert.equal(entry.versions, undefined)
      for (const source of record.alsoSeen) assert.ok(entry.asset.alsoSeen.includes(source))
      continue
    }
    assert.equal(entry.id, id)
    assert.ok(entry.versions.some((source) => source.id === id && source.sourcePage && source.isVector === false))
    assert.equal(findGalleryEntry(variant.id), entry)
    assert.equal(entry.asset.id, record.preferred ?? id)
    if (record.preferred) {
      assert.equal(entry.identity.provenance, 'third_party_reconstruction')
      assert.equal(variant.reconstruction, true)
    } else {
      assert.equal(entry.identity.provenance, 'published_raster')
      if (variant.reconstruction) {
        assert.equal(variant.provenance, 'third_party_reconstruction')
        assert.equal(variant.derivedFrom, id)
      } else {
        assert.equal(variant.evidenceType, 'native-pdf-vector-extraction')
        assert.match(variant.sourcePage, /#page=2$/)
      }
    }
  }
})

test('source and generated display SVGs are self-contained vector geometry', () => {
  for (const { asset } of Object.values(reviewed).filter(({ asset }) => asset)) {
    const source = readPublic(asset.file)
    assert.equal(source.length, asset.bytes)
    assert.equal(createHash('sha256').update(source).digest('hex'), asset.sha256)
    const display = COLLECTED_DISPLAY[asset.id]
    assert.ok(display, asset.id)
    for (const file of [asset.file, display.light.file, display.dark.file]) {
      const svg = readPublic(file).toString()
      assert.match(svg, /<svg\b[^>]+viewBox=/)
      assert.match(svg, /<(?:path|circle)\b/)
      assert.doesNotMatch(svg, /<(?:image|feImage|text|script|foreignObject)\b|\son\w+\s*=|data:image\//i)
    }
  }
})

test('official PDF leads link to their verified page without upgrading a raster', () => {
  // Vancouver's guide is now held as extracted paths (vancouverVisualStandards.test.js); its link stays.
  const vancouver = findGalleryEntry('source-recovered-municipal-vancouver-website-logo')
  assert.equal(vancouver.asset.id, 'vancouver-emblem-2006-colour')
  assert.match(vancouver.brandGuidelines.url, /#page=5$/)
  assert.match(findGalleryEntry('rd-thompson-nicola-horizontal').brandGuidelines.url, /#page=5$/)
  assert.match(findGalleryEntry('sd79-full-colour-landscape-2022').brandGuidelines.url, /#page=11$/)
})
