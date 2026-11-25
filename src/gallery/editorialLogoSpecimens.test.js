import assert from 'node:assert/strict'
import { test } from 'node:test'
import { EDITORIAL_LOGO_SPECIMENS } from './editorialLogoSpecimens.js'

test('editorial specimens for CNC and BCIT are small, attributed WebP excerpts', () => {
  assert.deepEqual(Object.keys(EDITORIAL_LOGO_SPECIMENS).sort(), ['bcit', 'college-of-new-caledonia'])
  const specimens = Object.values(EDITORIAL_LOGO_SPECIMENS).flat()
  assert.equal(specimens.length, 4)
  assert.equal(new Set(specimens.map((item) => item.id)).size, specimens.length)
  for (const item of specimens) {
    assert.match(item.url, /^https:\/\/.+#page=1$/)
    assert.ok(item.alt && item.caption && item.credit)
    assert.ok(item.width <= 512 && item.height <= 512)
    const b = Buffer.from(item.src.replace(/^data:image\/webp;base64,/, ''), 'base64')
    assert.equal(b.toString('ascii', 0, 4), 'RIFF')
    assert.equal(b.toString('ascii', 8, 12), 'WEBP')
    assert.ok(b.byteLength < 16_000)
  }
})
