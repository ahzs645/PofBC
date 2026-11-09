import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { BC_CPI, CPI_LATEST, cpiFor, inDollarsOf, inflationRate } from './inflation.js'

test('the index in code matches the committed Statistics Canada extract', () => {
  const csv = readFileSync(new URL('../../research/salaries/cpi/bc-cpi-all-items-annual.csv', import.meta.url), 'utf8')
  const rows = csv.trim().split('\n').slice(1).map((line) => line.split(',').map(Number))
  assert.deepEqual(Object.fromEntries(rows), Object.fromEntries(Object.entries(BC_CPI).map(([year, value]) => [Number(year), value])))
})

test('calendar years use their own average; fiscal years blend into the next', () => {
  assert.equal(cpiFor('2002'), 100)
  assert.ok(Math.abs(cpiFor('2023/24') - (0.75 * 151.2 + 0.25 * 155.2)) < 1e-9)
  assert.equal(cpiFor(`${CPI_LATEST + 1}`), BC_CPI[CPI_LATEST], 'later periods use the latest published average')
  assert.equal(cpiFor('not a year'), null)
})

test('amounts convert to the latest year’s dollars', () => {
  assert.ok(Math.abs(inDollarsOf(75000, '2002') - 75000 * 1.585) < 1e-6)
  assert.equal(inDollarsOf(100, String(CPI_LATEST)), 100)
  assert.equal(inDollarsOf(null, '2002'), null)
  assert.ok(Math.abs(inflationRate('2002', '2025', 23) - (1.585 ** (1 / 23) - 1)) < 1e-12)
})
