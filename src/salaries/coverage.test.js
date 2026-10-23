import { test } from 'node:test'
import assert from 'node:assert/strict'
import { coverageAt, disclosurePeriod, expenseLabel, filterEmployers, gapReason, gapRuns, missingYearMessage, rowCoverage, scopeLabel } from './coverage.js'

test('missing or excluded employer data cannot imply no employment', () => {
  const coverage = { hydro: [{ status: 'excluded' }], school: [{ status: 'missing' }] }
  assert.match(missingYearMessage(coverage, ['hydro', 'school'], 0), /coverage gap/)
  assert.match(missingYearMessage(coverage, ['hydro', 'school'], 0), /does not establish/)
  assert.match(missingYearMessage(undefined, ['hydro'], 0), /coverage has not been established/)
  assert.match(missingYearMessage({ hydro: [{ status: 'available', scope: 'executive-only' }] }, ['hydro'], 0), /executives only/)
})

test('scope and exact period come from evidence, never the collection label', () => {
  assert.equal(scopeLabel('executive-only'), 'Executive compensation only')
  assert.match(scopeLabel('mixed-disclosure'), /Combined/)
  assert.equal(scopeLabel('deputy-minister-remuneration'), 'Deputy minister remuneration')
  assert.equal(scopeLabel('appointee-remuneration'), 'Order in Council appointee remuneration')
  assert.equal(disclosurePeriod({ sourceIds: ['compiled'] }, { compiled: {} }), null)
  assert.deepEqual(disclosurePeriod({ sourceIds: ['original'] }, {
    original: { periodStart: '2019-04-01', periodEnd: '2020-03-31' }
  }), ['2019-04-01', '2020-03-31'])
  assert.equal(disclosurePeriod({ sourceIds: ['a', 'b'] }, {
    a: { periodStart: '2020-01-01', periodEnd: '2020-12-31' },
    b: { periodStart: '2020-04-01', periodEnd: '2021-03-31' }
  }), null)
  assert.equal(coverageAt({ counts: [0, 20], years: ['2020/21', '2023/24'], repeated: ['2020/21'] }, 0).status, 'excluded')
  const individual = rowCoverage({ scope: 'mixed-disclosure', sourceIds: ['staff', 'deputies'] }, 'deputies', {
    deputies: { scope: 'deputy-ministers', periodStart: '2020-04-01', periodEnd: '2021-03-31' }
  })
  assert.equal(individual.scope, 'deputy-ministers')
  assert.deepEqual(individual.sourceIds, ['deputies'])
  assert.equal(rowCoverage({ scope: 'executive-only' }, 'compiled', { compiled: { scope: 'compiled-unverified' } }).scope, 'executive-only')
  assert.equal(expenseLabel('staff', { staff: { travelSource: { threshold: 5000 } } }), 'Travel expenses')
  assert.equal(expenseLabel('hydro', { hydro: {} }), 'Expenses')
})

test('employer filters honor both sector and selected collection year', () => {
  const employers = [
    { slug: 'a', sector: 'Government', counts: [20, 0] },
    { slug: 'b', sector: 'Government', counts: [0, 30] },
    { slug: 'c', sector: 'Health authorities', counts: [10, 15] }
  ]
  assert.deepEqual(filterEmployers(employers, 'Government', '1').map((entry) => entry.slug), ['b'])
  assert.deepEqual(filterEmployers(employers, 'all', '0').map((entry) => entry.slug), ['a', 'c'])
  assert.equal(filterEmployers(employers).length, 3)
})

test('a gap year gets the same reason as its long explanation', () => {
  assert.equal(gapReason({ hydro: [{ status: 'excluded' }] }, ['hydro'], 0), 'no-coverage')
  assert.equal(gapReason({ hydro: [{ status: 'available', scope: 'executive-only' }] }, ['hydro'], 0), 'executive-only')
  assert.equal(gapReason({ hydro: [{ status: 'available' }], school: [] }, ['hydro', 'school'], 0), 'partial')
  assert.equal(gapReason({ hydro: [{ status: 'available' }] }, ['hydro'], 0), 'not-found')
})

test('consecutive gap years with one reason are one run', () => {
  const reasons = ['a', 'a', 'b', 'a']
  assert.deepEqual(gapRuns([0, 1, 2, 3, 5], (year) => reasons[year] ?? 'a'), [
    { from: 0, to: 1, reason: 'a' }, { from: 2, to: 2, reason: 'b' }, { from: 3, to: 3, reason: 'a' }, { from: 5, to: 5, reason: 'a' }
  ])
})
