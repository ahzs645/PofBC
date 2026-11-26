import test from 'node:test'
import assert from 'node:assert/strict'
import { checkPlacement } from './programPlacement.js'
import { CLEANBC_BODY } from './cleanbc.js'
import { ENDORSED_2019 } from './endorsed2019.js'
import { allCollectedAssets } from './collectedBodies.js'

const assets = new Map(allCollectedAssets().map((asset) => [asset.id, asset]))
const check = (id, medium, height, margin = null) =>
  checkPlacement(assets.get(id).placement, medium, height, margin)

test('placed height is independent of clearance, medium and artwork canvas', () => {
  for (const [id, px, print] of [
    ['cleanbc-base-wordmark', 45, .4], ['cleanbc-tagline-wordmark', 50, .46], ['cleanbc-base-endorsed', 50, .46],
    ['vector-BCID_StrongerBC_RGB_pos', 50, .46], ['vector-StrongerBC_Solid_rev', 25, .23],
    ['strongerbc-for-everyone-endorsed', 50, .46], ['strongerbc-for-everyone-wordmark', 40, .35],
    ['endorsed-2019-lockup', 30, 10]
  ]) {
    for (const [medium, min] of [['screen', px], ['print', print]]) {
      assert.equal(check(id, medium, min, 0).sizeOK, true)
      assert.equal(check(id, medium, min - .01, 999).sizeOK, false)
      assert.equal(check(id, medium, min, 0).spacingOK, false)
      const { target } = check(id, medium, min)
      assert.equal(check(id, medium, min, target).spacingOK, true)
    }
  }
})

test('unpublished minima stay unspecified across source versions', () => {
  for (const a of CLEANBC_BODY.assets) {
    assert.ok(a.placement.spacing > 0)
    if (!['base-endorsed', 'base-wordmark', 'tagline-wordmark'].some((id) => (a.variantOf ?? a.id) === 'cleanbc-' + id))
      assert.equal(check(a.id, 'screen', 50).sizeOK, null)
  }
  for (const a of ENDORSED_2019.assets.filter((a) => !a.id.includes('lockup'))) {
    const proof = check(a.id, 'screen', 30)
    assert.equal(proof.sizeOK, null)
    assert.equal(proof.spacingOK, null)
  }
})

test('blank and invalid measurements cannot pass', () => {
  for (const height of ['', ' ', 0, -1, Infinity, 'bad'])
    assert.equal(check('endorsed-2019-lockup', 'screen', height).height, undefined)
  for (const margin of ['', -1, Infinity, 'bad'])
    assert.equal(check('endorsed-2019-lockup', 'screen', 30, margin).spacingOK, null)
})

test('the clearance reference changes with the drawing at the same placed height', () => {
  for (const [id, margin] of [
    ['cleanbc-base-wordmark', 72.1], ['cleanbc-base-endorsed', 49], ['cleanbc-tagline-wordmark', 47.2],
    ['vector-BCID_StrongerBC_RGB_pos', 30.78], ['vector-StrongerBC_RGB_pos', 47.25],
    ['strongerbc-for-everyone-endorsed', 33.63], ['strongerbc-for-everyone-wordmark', 32.26],
    ['endorsed-2019-lockup', 31.3], ['endorsed-2019-lockup-blue-positive', 31.6]
  ]) assert.equal(check(id, 'screen', 100).target, margin, id)
})

test('a measured margin can meet the guide before display rounding', () => {
  const proof = check('endorsed-2019-lockup', 'print', 10.1, 3.162)
  assert.equal(proof.target, 3.17)
  assert.equal(proof.spacingOK, true)
  assert.equal(check('endorsed-2019-lockup', 'print', 10.1, 3.16).spacingOK, false)
})
