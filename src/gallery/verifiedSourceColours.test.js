import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { findGalleryEntry } from './collections.js'
import { defaultCollectedAsset } from './tileArt.js'

const publicDir = new URL('../../public/', import.meta.url)
const readArtwork = (asset) => readFileSync(new URL(asset.file, publicDir), 'utf8')

test('published inks on native paths retain all original drawing commands and source versions', () => {
  const cases = [
    ['airport-cbc7-operator-emblem', '#06357a', '#253b75', 56],
    ['source-expanded-west-coast-express-performance-report-logo', '#ffffff', '#052a49', 3],
    ['source-municipal-prince-rupert-website-logo', '#ffffff', '#000000', 21],
    ['source-recovered-municipal-white-rock-website-logo', '#ffffff', '#002f65', 14]
  ]
  for (const [id, originalInk, publishedInk, count] of cases) {
    const entry = findGalleryEntry(id)
    const asset = defaultCollectedAsset(entry, 'light')
    assert.equal(asset.variantOf, id)
    assert.ok(entry.versions.some((version) => version.id === id && !version.isVector))
    const source = entry.versions.find((version) => version.id === asset.derivedFrom)
    const oldFill = `fill="${originalInk}"`
    const sourceSvg = readArtwork(source)
    assert.equal(sourceSvg.split(oldFill).length - 1, count)
    assert.equal(readArtwork(asset), sourceSvg.replaceAll(oldFill, `fill="${publishedInk}"`))
    assert.equal(createHash('sha256').update(readArtwork(asset)).digest('hex'), asset.sha256)
    assert.equal(asset.colourReferenceUrl, entry.versions.find((version) => version.id === id).sourceUrl)
    if (source.darkBackground) assert.equal(defaultCollectedAsset(entry, 'dark'), source)
  }
})

test('Nanaimo’s colour signature retains the native gradients and opens the official reverse on dark', () => {
  const entry = findGalleryEntry('airport-cycd-signature')
  assert.equal(entry.asset.id, 'airport-cycd-colour-signature-2025')
  assert.equal(defaultCollectedAsset(entry, 'dark').id, 'airport-cycd-reverse')
  assert.ok(entry.versions.some(({ id }) => id === 'airport-cycd-colour-2025'))
  const svg = readArtwork(entry.asset)
  assert.equal((svg.match(/<linearGradient\b/g) ?? []).length, 2)
  assert.equal((svg.match(/<clipPath\b/g) ?? []).length, 4)
  assert.doesNotMatch(svg, /<(?:image|text|feImage)\b|data:image/i)
  assert.equal(createHash('sha256').update(svg).digest('hex'), entry.asset.sha256)
})

test('GameSense opens the standalone website knockout while the endorsed version keeps its own design', () => {
  const entry = findGalleryEntry('source-recovered-gamesense-website')
  const source = findGalleryEntry('source-recovered-gamesense-bclc-2025-reverse')
  assert.equal(entry.asset.derivedFrom, source.asset.id)
  assert.notEqual(source.id, entry.id)
  assert.equal(entry.asset.sourceGround, 'dark')
  assert.ok(entry.versions.some((version) => version.id === entry.id && version.format === 'png'))
  const svg = readArtwork(entry.asset)
  assert.match(svg, /fill="#ffffff" fill-rule="evenodd"/)
  assert.equal((svg.match(/<path\b/g) ?? []).length, 1)
  assert.doesNotMatch(svg, /<(?:image|text|feImage)\b/)
  assert.equal(createHash('sha256').update(svg).digest('hex'), entry.asset.sha256)
})

test('Northern Development’s two-tone script uses the same 35 native outlines as the 2014 white brochure', () => {
  const entry = findGalleryEntry('ndit-northern-development-script-2015')
  const source = entry.versions.find((version) => version.id === entry.asset.derivedFrom)
  assert.equal(source.id, 'ndit-script-smithers-2014-white')
  assert.equal(entry.asset.id, 'ndit-script-2015-source-colours')
  const colour = readArtwork(entry.asset)
  const white = readArtwork(source)
  const outlines = (svg) => [...svg.matchAll(/<path\b[^>]*\sd="([^"]+)"/g)].map((match) => match[1])
  assert.equal(outlines(white).length, 35)
  assert.deepEqual(outlines(colour), outlines(white))
  assert.equal((colour.match(/fill="#0083c0"/g) ?? []).length, 8)
  assert.equal((colour.match(/fill="#1e285b"/g) ?? []).length, 27)
  assert.doesNotMatch(colour + white, /<(?:image|text|feImage)\b/)
  for (const version of [source, entry.asset]) {
    assert.equal(createHash('sha256').update(readArtwork(version)).digest('hex'), version.sha256)
  }
})
