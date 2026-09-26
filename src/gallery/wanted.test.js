// The bodies still being sought are shown as sought: named, routed, and drawn with nothing.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ASSET_STATUS, WANTED } from './wanted.js'
import { findGalleryEntry } from './collections.js'

test('the five routes from the research package are all here, once each', () => {
  assert.deepEqual(WANTED.map((item) => item.source), ['L01', 'L02', 'L03', 'L04', 'L05'])
  assert.equal(new Set(WANTED.map((item) => item.id)).size, WANTED.length)
})

test('a wanted body has no artwork, and is not also a mark in the gallery', () => {
  for (const item of WANTED) {
    for (const key of ['kind', 'mark', 'draw', 'presets', 'svg', 'cover', 'identity']) {
      assert.equal(item[key], undefined, `${item.id} carries ${key}`)
    }
    assert.equal(findGalleryEntry(item.id), undefined, `${item.id} is in the gallery`)
  }
})

test('each says what is verified, what comes next and how to ask', () => {
  for (const item of WANTED) {
    assert.ok(item.assetStatus in ASSET_STATUS, `${item.id}: ${item.assetStatus}`)
    for (const key of ['label', 'verified', 'nextAction', 'contact', 'warning']) {
      assert.ok(item[key]?.trim(), `${item.id} has no ${key}`)
    }
  }
})
