import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { findGalleryEntry } from './collections.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'
import reviewed from './primaryLogoVersions.json' with { type: 'json' }

const readPublic = (file) => readFileSync(new URL(`../../public/${file}`, import.meta.url))

test('primary-logo variants preserve the gallery design IDs, published sources, and provenance', () => {
  for (const [id, record] of Object.entries(reviewed)) {
    const entry = findGalleryEntry(id)
    const variant = record.asset
    assert.equal(entry.id, id)
    assert.ok(entry.versions.some((source) => source.id === id && source.sourcePage && source.isVector === false))
    assert.equal(findGalleryEntry(variant.id), entry)
    assert.equal(entry.asset.id, record.preferred ?? id)
    if (record.preferred) {
      assert.equal(entry.identity.provenance, 'third_party_reconstruction')
      assert.equal(variant.reconstruction, true)
    } else {
      assert.equal(entry.identity.provenance, 'published_raster')
      assert.equal(variant.evidenceType, 'native-pdf-vector-extraction')
      assert.equal(variant.reconstruction, false)
      assert.match(variant.sourcePage, /#page=2$/)
    }
  }
})

test('source and generated display SVGs are self-contained vector geometry', () => {
  for (const { asset } of Object.values(reviewed)) {
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
  const vancouver = findGalleryEntry('source-recovered-municipal-vancouver-website-logo')
  assert.equal(vancouver.identity.provenance, 'published_raster')
  assert.match(vancouver.brandGuidelines.url, /#page=5$/)
  assert.match(findGalleryEntry('rd-thompson-nicola-horizontal').brandGuidelines.url, /#page=5$/)
  assert.match(findGalleryEntry('sd79-full-colour-landscape-2022').brandGuidelines.url, /#page=11$/)
})
