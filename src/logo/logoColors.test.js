import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  BRAND_COLORS, TRANSPARENT, contrastRatio, describeContrast, isLightColor, parseHex, preferredInkFor, resolveColor
} from './logoColors.js'

test('names resolve to brand hex, anything else passes through', () => {
  assert.equal(resolveColor('green'), '#006837')
  assert.equal(resolveColor('GREEN'), '#006837')
  assert.equal(resolveColor('#abc'), '#abc')
  assert.equal(resolveColor('rgb(1 2 3)'), 'rgb(1 2 3)')
  assert.equal(resolveColor('transparent'), TRANSPARENT)
  assert.equal(resolveColor('none'), TRANSPARENT)
})

test('an absent colour falls back rather than becoming "undefined"', () => {
  assert.equal(resolveColor(undefined), BRAND_COLORS.white)
  assert.equal(resolveColor(''), BRAND_COLORS.white)
  assert.equal(resolveColor(null, TRANSPARENT), TRANSPARENT)
})

test('hex parsing handles both lengths and rejects nonsense', () => {
  assert.deepEqual(parseHex('#ffffff'), [255, 255, 255])
  assert.deepEqual(parseHex('006837'), [0, 104, 55])
  assert.deepEqual(parseHex('#abc'), [170, 187, 204])
  assert.equal(parseHex('#ggg'), null)
  assert.equal(parseHex('rebeccapurple'), null)
})

test('contrast is symmetric and bounded by the extremes', () => {
  assert.equal(Math.round(contrastRatio('#000', '#fff')), 21)
  assert.equal(contrastRatio('#123456', '#123456'), 1)

  const forward = contrastRatio('white', 'green')
  const backward = contrastRatio('green', 'white')
  assert.ok(Math.abs(forward - backward) < 1e-9, 'order does not matter')
})

test('a transparent background is judged against white', () => {
  assert.equal(contrastRatio('green', TRANSPARENT), contrastRatio('green', '#ffffff'))
})

test('contrast is described in terms a person can act on', () => {
  assert.equal(describeContrast('white', 'green').level, 'pass')
  assert.equal(describeContrast('white', 'gold').level, 'warn')
  assert.equal(describeContrast('#fffffe', '#ffffff').level, 'fail')
  assert.equal(describeContrast('not a colour', 'green').level, 'unknown')
})

test('light and dark backgrounds get the ink that reads on them', () => {
  assert.equal(isLightColor('white'), true)
  assert.equal(isLightColor('green'), false)
  assert.equal(isLightColor('gold'), true)

  assert.equal(preferredInkFor('white'), BRAND_COLORS.green)
  assert.equal(preferredInkFor('green'), BRAND_COLORS.white)
})

test('every palette entry is a colour the rest of the module can read', () => {
  for (const [name, value] of Object.entries(BRAND_COLORS)) {
    assert.ok(parseHex(value), `${name} (${value}) must parse as hex`)
    assert.equal(resolveColor(name), value, `${name} resolves to itself`)
    assert.equal(value, value.toLowerCase(), `${name} is lower case, so swatch matching works`)
  }
})
