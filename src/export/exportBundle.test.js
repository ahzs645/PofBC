// Bundle planning is pure, so it can be checked without a browser. The rendering it drives cannot
// (canvas, Blob), and is covered by the end-to-end download instead.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { BUNDLE_DEFAULTS, bundleName, planBundle } from './exportBundle.js'

const FORESTS = { ministry: 'Ministry of Forests', markColor: '#ffffff', textColor: '#ffffff' }

test('the default bundle is every lockup in vector plus two PNG sizes', () => {
  const plan = planBundle(FORESTS)

  // 3 layouts × (svg + pdf + png at two widths).
  assert.equal(plan.length, 12)
  assert.deepEqual([...new Set(plan.map((entry) => entry.layout))], ['stacked', 'centred', 'horizontal'])
  assert.deepEqual([...new Set(plan.map((entry) => entry.format))], ['svg', 'pdf', 'png'])
})

test('vector formats are rendered once, raster once per width', () => {
  const plan = planBundle({ ...FORESTS, layouts: ['stacked'], formats: ['svg', 'png'], sizes: [512, 1024, 2048] })

  const svg = plan.filter((entry) => entry.format === 'svg')
  const png = plan.filter((entry) => entry.format === 'png')

  assert.equal(svg.length, 1, 'a vector file has no size')
  assert.equal(svg[0].pixelWidth, undefined)
  assert.equal(png.length, 3, 'one per requested width')
  assert.deepEqual(png.map((entry) => entry.pixelWidth), [512, 1024, 2048])
})

test('paths are grouped by lockup under one folder', () => {
  const plan = planBundle(FORESTS)

  for (const entry of plan) {
    assert.ok(
      entry.path.startsWith(`${bundleName(FORESTS)}/${entry.layout}/`),
      `unexpected path: ${entry.path}`
    )
  }

  // Unzipping should leave one directory behind, not three.
  assert.equal(new Set(plan.map((entry) => entry.path.split('/')[0])).size, 1)
})

test('the pixel width appears in raster filenames so sizes cannot be confused', () => {
  const [entry] = planBundle({ ...FORESTS, layouts: ['stacked'], formats: ['png'], sizes: [2048] })
  assert.ok(entry.path.endsWith('-2048.png'), entry.path)
})

test('an empty selection plans nothing rather than falling back to everything', () => {
  assert.deepEqual(planBundle({ ...FORESTS, layouts: [] }), [])
  assert.deepEqual(planBundle({ ...FORESTS, formats: [] }), [])
})

test('no widths selected still produces the default raster sizes', () => {
  // The UI stops you clearing the last one, but a caller of the library might.
  const plan = planBundle({ ...FORESTS, layouts: ['stacked'], formats: ['png'], sizes: [] })
  assert.equal(plan.length, BUNDLE_DEFAULTS.sizes.length)
})

test('layouts come out in the canonical order however they are asked for', () => {
  const plan = planBundle({ ...FORESTS, layouts: ['horizontal', 'stacked'], formats: ['svg'] })
  assert.deepEqual(plan.map((entry) => entry.layout), ['stacked', 'horizontal'])
})

test('the bundle is named after the ministry, or the wordmark without one', () => {
  assert.equal(bundleName(FORESTS), 'bc-ministry-of-forests')
  assert.equal(bundleName({ ministry: '' }), 'bc-wordmark')
  assert.equal(bundleName({}), 'bc-wordmark')
})
