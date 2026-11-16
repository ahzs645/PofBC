import { test } from 'node:test'
import assert from 'node:assert/strict'
import { nearestWithin, TAP_REACH } from './nearest.js'

const bodies = [{ id: 'forests', x: 100, y: 100 }, { id: 'finance', x: 124, y: 100 }, { id: 'hydro', x: 300, y: 40 }]

test('a tap between two bodies goes to the nearer one', () => {
  assert.equal(nearestWithin({ x: 110, y: 100 }, bodies), 'forests')
  assert.equal(nearestWithin({ x: 114, y: 104 }, bodies), 'finance')
})

test('a tap just off a body still chooses it, and one out in the open chooses nothing', () => {
  assert.equal(nearestWithin({ x: 300, y: 40 + TAP_REACH - 1 }, bodies), 'hydro')
  assert.equal(nearestWithin({ x: 300, y: 40 + TAP_REACH + 1 }, bodies), null)
  assert.equal(nearestWithin({ x: 10, y: 300 }, bodies), null)
  assert.equal(nearestWithin({ x: 10, y: 10 }, []), null)
})

test('a tap on a body chooses it even when a neighbour overlaps', () => {
  assert.equal(nearestWithin({ x: 100, y: 100 }, bodies), 'forests')
  assert.equal(nearestWithin({ x: 112, y: 100 }, bodies), 'forests', 'equidistant: the first drawn')
})
