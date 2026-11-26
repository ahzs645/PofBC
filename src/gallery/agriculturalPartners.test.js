import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { AGRICULTURAL_PARTNER_BODIES } from './agriculturalPartners.js'
import { COLLECTIONS_ON_SHELF, findGalleryEntry } from './collections.js'
import { IDENTITY_COVERAGE, INVERSE_RELATION_LABELS, relationsOf } from './identityCoverage.js'
import { tileArt } from './tileArt.js'

test('program delivery partners keep independent owners, and related organizations retain evidence leads', () => {
  const subjects = IDENTITY_COVERAGE.filter((subject) => subject.family === 'agricultural-partners')
  assert.equal(subjects.length, 5)
  const holdings = subjects.filter((subject) => subject.hasArtwork)
  assert.equal(holdings.length, 2)
  for (const subject of holdings) {
    assert.equal(subject.graphNode, null)
    assert.equal(subject.collections.length, 1)
    assert.ok(COLLECTIONS_ON_SHELF('partners').includes(subject.collections[0]))
    assert.ok(subject.entries.every((entry) => entry.owner === subject.id))
    const cover = findGalleryEntry(subject.collections[0].cover)
    assert.equal(cover.asset.format, 'svg')
    for (const theme of ['light', 'dark']) {
      assert.match(tileArt(cover, theme, { cover: true }), /src="[^"]+\.svg"/)
    }
    assert.ok(subject.entries.some((entry) => (entry.versions ?? [entry.asset]).some((version) => version.format === 'png')))
  }
  assert.ok(subjects.filter((subject) => !subject.hasArtwork).every((subject) => subject.state === 'source-located'))
  assert.equal(holdings[0].collections[0].cover, 'iaf-field-monogram')
  const handover = relationsOf(holdings[0]).incoming.find((relation) => relation.type === 'transferred-operations-to')
  assert.equal(handover.subject, holdings[1].id)
  assert.equal(INVERSE_RELATION_LABELS[handover.type], 'Received operations from')
})

test('source artwork keeps its recorded digest and distinct raster and vector formats', () => {
  const assets = AGRICULTURAL_PARTNER_BODIES.flatMap((body) => body.assets)
  assert.deepEqual(assets.map((asset) => asset.format).sort(), ['png', 'png', 'png', 'svg', 'svg', 'svg', 'svg', 'svg', 'svg'])
  for (const asset of assets) {
    const bytes = readFileSync(new URL('../../public/' + asset.file, import.meta.url))
    assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, asset.id)
  }
})
