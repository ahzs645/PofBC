import { test } from 'node:test'
import assert from 'node:assert/strict'
import { sourceWarnings } from './coverage.js'
import { coverageAt, categoryCoverage, shortYearLabel, reportingYearLabel, relevantYearIndexes, samePeriodKinds, coverageStatus, disclosurePeriod, expenseLabel, filterEmployers, gapReason, gapRuns, missingYearMessage, rowCoverage, scopeLabel, sourceHref, thresholdLabel, yearAvailability } from './coverage.js'

test('source caveats follow the selected cohort without leaking into a separate council schedule', () => {
  const sources = { staff: { publicWarning: 'Employee expenses do not reconcile.' }, council: {},
    other: { publicWarning: 'Employee expenses do not reconcile.' } }
  assert.deepEqual(sourceWarnings(['staff', 'staff', 'other', 'missing'], sources), ['Employee expenses do not reconcile.'])
  assert.deepEqual(sourceWarnings(['council'], sources), [])
})

test('calendar labels stay distinct and elected officials do not inherit employee thresholds', () => {
  assert.equal(shortYearLabel('2020'), '2020')
  assert.equal(shortYearLabel('2020/21'), '20/21')
  assert.equal(reportingYearLabel('2020'), '2020 (calendar year)')
  const sources = { staff: { scope: 'employee-remuneration', threshold: 75000, thresholdComparison: '>', periodType: 'calendar' },
    council: { scope: 'elected-officials', threshold: null, sourceKind: 'compiled', periodType: 'unverified' } }
  const filtered = categoryCoverage({ scope: 'mixed-disclosure', sourceIds: ['staff', 'council'], threshold: 75000 }, 'elected-officials', sources)
  assert.deepEqual(filtered.sourceIds, ['council'])
  assert.equal(filtered.threshold, null)
  assert.equal(filtered.periodType, 'unverified')
  assert.equal(coverageStatus({ ...filtered, status: 'available' }, sources).kind, 'compiled')
})
test('calendar imports do not invent gaps between every fiscal disclosure', () => {
  const years = ['2019', '2019/20', '2020', '2020/21', '2021', '2021/22']
  const coverage = years.map((label) => label.includes('/') ? { status: 'available', periodType: 'fiscal' } : { status: 'not-applicable' })
  assert.deepEqual(relevantYearIndexes(years, coverage, [0, 10, 0, 20, 0, 30]), [1, 3, 5])
  assert.deepEqual(samePeriodKinds(years, [1, 5]), [1, 3, 5])
  assert.deepEqual(samePeriodKinds(years, [0, 4]), [0, 2, 4])
  assert.equal(coverageStatus({ status: 'aggregate-only' }).label, 'Verified aggregate disclosure')
  assert.equal(yearAvailability({ status: 'not-applicable' }, 0), 'different reporting-period type')
})

test('missing or excluded employer data cannot imply no employment', () => {
  const coverage = { hydro: [{ status: 'excluded' }], school: [{ status: 'missing' }] }
  assert.match(missingYearMessage(coverage, ['hydro', 'school'], 0), /coverage gap/)
  assert.match(missingYearMessage(coverage, ['hydro', 'school'], 0), /does not establish/)
  assert.match(missingYearMessage(undefined, ['hydro'], 0), /coverage has not been established/)
  assert.match(missingYearMessage({ hydro: [{ status: 'available', scope: 'executive-only' }] }, ['hydro'], 0), /executives only/)
})

test('board and elected-only schedules cannot imply ordinary employee coverage', () => {
  for (const scope of ['board-remuneration', 'school-trustees', 'elected-officials']) {
    const coverage = { employer: [{ status: 'available', scope }] }
    assert.equal(gapReason(coverage, ['employer'], 0), 'limited-disclosure')
    assert.match(missingYearMessage(coverage, ['employer'], 0), /do not establish employee coverage/)
  }
})

test('scope and exact period come from evidence, never the collection label', () => {
  assert.equal(scopeLabel('executive-only'), 'Executive compensation only')
  assert.equal(scopeLabel('school-trustees'), 'School trustee remuneration')
  assert.equal(scopeLabel('board-remuneration'), 'Board remuneration disclosure')
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

test('source leads and held reports are distinct from accepted source data', () => {
  assert.equal(coverageStatus({ status: 'excluded' }).kind, 'held')
  assert.equal(coverageStatus({ status: 'source-found' }).kind, 'found')
  assert.equal(coverageStatus({ status: 'missing' }).kind, 'missing')
  assert.equal(coverageStatus({ status: 'available', sourceIds: ['compiled'], sourceLeads: [{ url: 'https://example.org/report.pdf' }] }, {
    compiled: { scope: 'compiled-unverified' }
  }).kind, 'compiled')
  assert.equal(coverageStatus({ status: 'available', sourceIds: ['official'] }, {
    official: { scope: 'employee-remuneration', url: 'https://example.org/report.pdf' }
  }).kind, 'primary')
  assert.match(yearAvailability({ status: 'excluded' }, 0), /held/)
  assert.match(yearAvailability({ status: 'source-found' }, 0), /source found/)
  assert.equal(yearAvailability({ status: 'available' }, 1000), '1,000 records')
})

test('source links open the physical PDF page without guessing absent page data', () => {
  const source = { url: 'https://example.org/report.PDF?download=true#old' }
  assert.equal(sourceHref(source, 12), 'https://example.org/report.PDF?download=true#page=12')
  assert.equal(sourceHref(source, null), source.url)
  assert.equal(sourceHref(source, -1), source.url)
  assert.equal(sourceHref({ url: 'https://example.org/report.csv' }, 12), 'https://example.org/report.csv')
  assert.equal(sourceHref({ url: 'javascript:alert(1)' }, 12), null)
})

test('inclusive and strict disclosure thresholds keep their source meaning', () => {
  assert.equal(thresholdLabel({ threshold: 75000, thresholdComparison: '>=' }), 'at least $75,000')
  assert.equal(thresholdLabel({ threshold: 75000, thresholdComparison: '>' }), 'over $75,000')
  assert.equal(thresholdLabel({ threshold: 75000 }), 'threshold $75,000')
  assert.equal(thresholdLabel({ threshold: null }), null)
})
