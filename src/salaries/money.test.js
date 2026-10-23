import { test } from 'node:test'
import assert from 'node:assert/strict'
import { formatMoney, medianMoney } from './money.js'

test('currency preserves published cents, integer formatting and expense recoveries', () => {
  assert.equal(formatMoney(123456.78), '$123,456.78')
  assert.equal(formatMoney(123456), '$123,456')
  assert.equal(formatMoney(123456.7), '$123,456.70')
  assert.equal(formatMoney(-5110.25), '-$5,110.25')
  assert.equal(formatMoney(-443), '-$443')
})

test('missing amounts remain distinct from an explicitly disclosed zero', () => {
  assert.equal(formatMoney(null), '—')
  assert.equal(formatMoney(undefined), '—')
  assert.equal(formatMoney(null, null), null)
  assert.equal(formatMoney(0), '$0')
})

test('position medians retain cents and handle half-cent midpoints explicitly', () => {
  assert.equal(medianMoney([123456.78]), 123456.78)
  assert.equal(medianMoney([100000.25, 100000.75]), 100000.5)
  assert.equal(formatMoney(medianMoney([100000.25, 100000.75])), '$100,000.50')
  assert.equal(medianMoney([1.01, 1.02]), 1.02)
  assert.equal(medianMoney([100000, 120000, 140000]), 120000)
  assert.equal(medianMoney([]), null)
})
