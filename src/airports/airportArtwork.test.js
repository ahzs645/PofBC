import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { AIRPORT_BODIES } from './airportArtwork.js'
import facilities from './facilities.json' with { type: 'json' }
import { collectedEntriesOf } from '../gallery/collectedCollections.js'
import { collectedDisplay } from '../gallery/tileArt.js'
import { gallerySections } from '../gallery/gallerySearch.js'

const publicRoot = new URL('../../public/', import.meta.url)

test('Prince George uses its full-colour vector and Terrace keeps its two positive treatments selectable', () => {
  const princeGeorge = collectedEntriesOf('airport-cyxs').find(({ id }) => id === 'airport-cyxs-signature')
  assert.equal(princeGeorge.asset.id, 'airport-cyxs-colour-annual-report-2023')
  assert.match(readFileSync(new URL(princeGeorge.asset.file, publicRoot), 'utf8'), /<radialGradient\b/)
  assert.ok(princeGeorge.versions.some(({ id }) => id === 'airport-cyxs-signature'))
  assert.ok(princeGeorge.versions.some(({ id }) => id === 'airport-cyxs-reverse'))

  const terrace = collectedEntriesOf('airport-cyxt')
  const print = terrace.find(({ id }) => id === 'airport-cyxt-advertising-signature-2024')
  const website = terrace.find(({ id }) => id === 'airport-cyxt-signature')
  assert.equal(print.asset.isVector, true)
  assert.equal(print.asset.specimenDate, '2024')
  assert.ok(print.versions.some(({ id }) => id === print.asset.darkVariant))
  assert.equal(website.asset.file, 'identity-airports/cyxt/signature.png')
})

test('airport artwork has a directory record, a gallery collection and local downloads', () => {
  const locationCodes = new Set(facilities.map(({ code }) => code.toLowerCase()))
  const [shelf] = gallerySections('airports')
  assert.equal(new Set(facilities.map(({ id }) => id)).size, facilities.length)
  assert.equal(shelf.collections.length, AIRPORT_BODIES.length)

  for (const { id, assets, cover } of AIRPORT_BODIES) {
    assert.ok(locationCodes.has(id.slice('airport-'.length)), id)
    const entries = collectedEntriesOf(id)
    assert.ok(entries.some(({ id }) => id === cover), cover)
    const galleryIds = new Set(entries.flatMap((entry) => (entry.versions ?? [entry.asset]).map(({ id }) => id)))

    for (const asset of assets) {
      assert.ok(galleryIds.has(asset.id), asset.id)
      assert.match(asset.file, /^identity-airports\/[a-z0-9]+\/[a-z0-9-]+\.(svg|png|jpg|gif|webp)$/)
      const bytes = readFileSync(new URL(asset.file, publicRoot))
      assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, asset.id)
      if (asset.isVector) {
        assert.doesNotMatch(bytes.toString(), /<(?:\w+:)?(?:image|script|foreignObject)\b/i, asset.id)
        for (const theme of ['light', 'dark']) {
          assert.ok(readFileSync(new URL(collectedDisplay(asset, theme).file, publicRoot)).length, asset.id)
        }
      }
    }
  }
})
