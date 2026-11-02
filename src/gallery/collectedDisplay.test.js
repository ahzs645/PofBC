import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { COLLECTED_BODIES, COLLECTED_SPECIMENS } from './collectedData.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'
import { collectedDisplay, logoScale } from './tileArt.js'

const assets = new Map([...COLLECTED_BODIES, ...COLLECTED_SPECIMENS].flatMap((each) => each.assets).map((asset) => [asset.id, asset]))
const publicFile = (path) => new URL(`../../public/${path}`, import.meta.url)

test('every display copy is of a collected vector file, for both themes, and exists', () => {
  for (const [id, entry] of Object.entries(COLLECTED_DISPLAY)) {
    const asset = assets.get(id)
    assert.ok(asset, `${id} is a collected file`)
    assert.ok(asset.format === 'svg' && asset.isVector, `${id} is a vector file`)
    for (const theme of ['light', 'dark']) {
      const copy = entry[theme]
      assert.ok(copy, `${id} has a ${theme} copy`)
      assert.match(copy.file, /^identity-display\/[A-Za-z0-9._-]+\.svg$/)
      assert.ok(existsSync(publicFile(copy.file)), `${copy.file} exists`)
      assert.ok(copy.aspect > 0, `${id} has its proportions`)
      assert.equal(typeof copy.recoloured, 'boolean')
    }
  }
})

test('a display copy keeps the source file as it is, apart from its viewBox and colours', () => {
  for (const [id, entry] of Object.entries(COLLECTED_DISPLAY)) {
    const copy = readFileSync(publicFile(entry.light.file), 'utf8')
    assert.doesNotMatch(copy, /<script/i, `${id} carries no script`)
    assert.match(copy, /viewBox="[-\d. ]+"/, `${id} is trimmed by its viewBox`)
  }
})

test('raster files have no display copy and keep their plate', () => {
  const raster = [...assets.values()].find((asset) => asset.format !== 'svg')
  assert.equal(collectedDisplay(raster, 'dark'), null)
})

test('a long wordmark is drawn shorter than a square emblem, within bounds', () => {
  assert.equal(logoScale(1), 1)
  assert.equal(logoScale(2.4), 1)
  assert.ok(logoScale(5) < 1 && logoScale(5) > logoScale(10))
  assert.equal(logoScale(100), 0.42)
})
