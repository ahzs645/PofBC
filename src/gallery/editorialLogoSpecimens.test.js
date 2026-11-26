import assert from 'node:assert/strict'
import { test } from 'node:test'
import { EDITORIAL_LOGO_SPECIMENS } from './editorialLogoSpecimens.js'

test('editorial logo specimens are small, attributed WebP excerpts', () => {
  assert.deepEqual(Object.keys(EDITORIAL_LOGO_SPECIMENS).sort(), ['bcit', 'capilano-college', 'capilano-university', 'college-of-the-rockies', 'east-kootenay-community-college', 'emily-carr-institute-of-art-and-design', 'emily-carr-university', 'kootenay-school-of-the-arts', 'kwantlen-college', 'kwantlen-university-college', 'pacific-vocational-institute'])
  const specimens = Object.values(EDITORIAL_LOGO_SPECIMENS).flat()
  assert.equal(specimens.length, 18)
  assert.equal(new Set(specimens.map((item) => item.id)).size, specimens.length)
  for (const item of specimens) {
    assert.match(item.url, /^https:\/\/.+#page=[1-9]\d*$/)
    assert.ok(item.alt && item.caption && item.credit)
    assert.ok(item.width <= 512 && item.height <= 512)
    const b = Buffer.from(item.src.replace(/^data:image\/webp;base64,/, ''), 'base64')
    assert.equal(b.toString('ascii', 0, 4), 'RIFF')
    assert.equal(b.toString('ascii', 8, 12), 'WEBP')
    assert.ok(b.byteLength < 16_000)
  }
})

test('each early Kwantlen specimen is shown under the name printed on its minutes', () => {
  const [college] = EDITORIAL_LOGO_SPECIMENS['kwantlen-college']
  const [universityCollege] = EDITORIAL_LOGO_SPECIMENS['kwantlen-university-college']
  assert.match(college.credit, /^Kwantlen College, Board minutes, November 23, 1994/)
  assert.match(universityCollege.credit, /^Kwantlen University College, Board minutes, May 24, 1995/)
  assert.notEqual(college.src, universityCollege.src)
})
