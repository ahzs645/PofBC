import { test } from 'node:test'
import assert from 'node:assert/strict'
import { aggregateSignatures, candidatePeriodLabels, compareOpenCompensation, signatureMatches, validateOpenCompensationSnapshot } from './lib/opencompensation.mjs'

const row = { name: 'Employer A', url: 'https://www.opencompensation.org/british-columbia/employer/a', periodLabel: '2023-2024', recordCount: 15, averageCompensation: 100, highestCompensation: 100 }
const source = { url: 'https://www.opencompensation.org/british-columbia/employer', retrievedAt: '2026-11-04T20:21:38Z', reportedEntryCount: 1, minimumPositiveRecords: 15, latestPerPublishedName: true }
const snapshot = () => ({ version: 1, source, employers: [row] })

test('edition labels produce candidates without asserting fiscal reporting dates', () => {
  assert.deepEqual(candidatePeriodLabels('2023-2024'), ['2023/24', '2023', '2024'])
  assert.deepEqual(candidatePeriodLabels('1999/00'), ['1999/00', '1999', '2000'])
  assert.deepEqual(candidatePeriodLabels('2024'), ['2024'])
  assert.throws(() => candidatePeriodLabels('2023-2025'), /nonconsecutive/)
})

test('captured directory count and selection rules must reconcile', () => {
  assert.equal(validateOpenCompensationSnapshot(snapshot()).employers.length, 1)
  assert.throws(() => validateOpenCompensationSnapshot({ ...snapshot(), source: { ...source, reportedEntryCount: 2 } }), /reconcile/)
  assert.throws(() => validateOpenCompensationSnapshot({ ...snapshot(), employers: [{ ...row, recordCount: 14 }] }), /positive-record count/)
  assert.throws(() => validateOpenCompensationSnapshot({ ...snapshot(), employers: [{ ...row, url: 'javascript:alert(1)' }] }), /URL/)
})

test('expenses can explain a compensation signature without changing remuneration', () => {
  const values = [['A', null, 100, 20], ['B', null, 200, 40]]
  const signatures = aggregateSignatures(values)
  assert.deepEqual(signatures.remuneration, { recordCount: 2, averageRounded: 150, highestRounded: 200 })
  assert.deepEqual(signatureMatches({ recordCount: 2, averageCompensation: 180, highestCompensation: 240 }, signatures), ['remunerationPlusKnownExpenses', 'remunerationPlusKnownExpensesForPositiveRemuneration'])
  assert.equal(values[0][2], 100)
})

test('unknown expenses stay unknown and nonpositive amounts do not become positive records', () => {
  const signatures = aggregateSignatures([['A', null, 100, null], ['B', null, 100, 0], ['C', null, 0, 0], ['D', null, -5, 0]])
  assert.equal(signatures.unknownExpenses, 1)
  assert.equal(signatures.remuneration.recordCount, 2)
  assert.match(signatures.expenseTreatment, /missing expenses remain unknown/)
  assert.equal(aggregateSignatures([]).remuneration.averageRounded, null)
})

test('expense-only rows make selection by remuneration differ from selection by combined amount', () => {
  const signatures = aggregateSignatures([['A', null, 100, 20], ['B', null, 0, 30]])
  assert.equal(signatures.remunerationPlusKnownExpenses.recordCount, 2)
  assert.equal(signatures.remunerationPlusKnownExpensesForPositiveRemuneration.recordCount, 1)
  assert.deepEqual(signatureMatches({ recordCount: 1, averageCompensation: 120, highestCompensation: 120 }, signatures), ['remunerationPlusKnownExpensesForPositiveRemuneration'])
})

test('selection by positive remuneration preserves negative expense adjustments', () => {
  const signatures = aggregateSignatures([['A', null, 100, -150], ['B', null, 200, 0]])
  assert.deepEqual(signatures.remunerationPlusKnownExpenses, { recordCount: 1, averageRounded: 200, highestRounded: 200 })
  assert.deepEqual(signatures.remunerationPlusKnownExpensesForPositiveRemuneration, { recordCount: 2, averageRounded: 75, highestRounded: 200 })
})

test('calendar candidates and official/compiled coexistence cannot produce a parity pass', () => {
  const employer = { slug: 'employer-a', name: 'Employer A', names: ['Employer A'], rows: 30, periods: [
    { yearLabel: '2023', rows: 15, officialRows: 15, compiledRows: 0, cohorts: [{ sourceId: 'official', scope: 'employee-remuneration', rows: 15 }] },
    { yearLabel: '2023/24', rows: 15, officialRows: 0, compiledRows: 15, cohorts: [{ sourceId: 'compiled', scope: 'compiled-unverified', rows: 15 }] }
  ] }
  const report = compareOpenCompensation(snapshot(), { employers: [employer], totals: { rows: 30 } })
  assert.equal(report.employers[0].candidates.length, 2)
  assert.equal(report.employers[0].countDifference, null)
  assert.equal(report.employers[0].referencePeriodVerified, false)
  assert.equal(report.summary.recordLevelParityChecked, false)
  assert.equal(report.summary.importedSalaryRecords, 0)
})

test('historical names map to one repository ID without being counted as two employers', () => {
  const other = { ...row, name: 'Employer A Former', url: `${row.url}-former`, periodLabel: '2017-2018' }
  const report = compareOpenCompensation({ ...snapshot(), source: { ...source, reportedEntryCount: 2 }, employers: [row, other] }, {
    employers: [{ slug: 'employer-a', name: 'Employer A', names: ['Employer A', 'Employer A Former'], rows: 0, periods: [] }], totals: {}
  })
  assert.equal(report.summary.matchedPublishedNames, 2)
  assert.equal(report.summary.uniqueMappedRepositoryEmployers, 1)
  assert.equal(report.multiplePublishedNames[0].publishedNames.length, 2)
})
