import test from 'node:test'
import assert from 'node:assert/strict'
import { compareEmployerYear, buildSunshineComparison, compareReportChanges, toCsv } from './lib/sunshine-compare.mjs'
import { normalizeSunshineSnapshot, parseSunshineCsv, sunshineSnapshotToCsv } from './lib/sunshine-lists.mjs'

const cohort = changes => ({ sourceId: 'official-2024', rows: 10, namedRows: 10, official: true,
  scope: 'employee-remuneration', verifiedPeriod: true, periodType: 'calendar',
  periodStart: '2024-01-01', periodEnd: '2024-12-31', periodEndYear: 2024,
  threshold: 75000, thresholdComparison: '>', ...changes })
const employer = cohorts => ({ slug: 'city-of-example', name: 'City of Example', names: ['City of Example'], sector: 'Municipalities',
  rows: cohorts.reduce((n, c) => n + c.rows, 0), namedRows: 10, officialRows: cohorts.filter(c => c.official).reduce((n, c) => n + c.rows, 0),
  compiledRows: cohorts.filter(c => !c.official).reduce((n, c) => n + c.rows, 0), employeeRows: 10, leads: [],
  periods: [{ yearLabel: '2024', rows: cohorts.reduce((n, c) => n + c.rows, 0), officialRows: cohorts.filter(c => c.official).reduce((n, c) => n + c.rows, 0),
    compiledRows: cohorts.filter(c => !c.official).reduce((n, c) => n + c.rows, 0), employeeRows: 10, periodType: 'calendar', cohorts }] })
const reference = changes => ({ year: '2024', recordCount: 10, countBasis: 'records', periodType: 'calendar', scope: 'employee-remuneration', threshold: 75000, thresholdComparison: '>', ...changes })
const repository = entries => ({ employers: entries, sourceCatalog: [], inputs: [], inputsSha256: 'a'.repeat(64),
  totals: { employers: entries.length, rows: entries.reduce((n, e) => n + e.rows, 0), officialRows: entries.reduce((n, e) => n + e.officialRows, 0), compiledRows: 0 } })
const snapshot = (years, complete = false) => ({ version: 1, source: { url: 'https://www.sunshinelists.ca/british-columbia/employers', retrievedAt: '2026-11-01T04:00:00Z', complete },
  employers: [{ name: 'City of Example', url: 'https://www.sunshinelists.ca/british-columbia/employers/city-of-example', years }] })

test('a compiled edition never establishes exact calendar coverage', () => {
  const e = employer([cohort({ official: false, periodType: 'unverified', verifiedPeriod: false, scope: 'compiled-unverified' })])
  assert.equal(compareEmployerYear(reference(), e).status, 'compiled-only')
})

test('unknown reference year basis cannot produce a count match', () => {
  assert.equal(compareEmployerYear(reference({ periodType: 'unknown' }), employer([cohort()])).status, 'period-review')
})

test('fiscal ending year is only a candidate until exact dates are supplied', () => {
  const e = employer([cohort({ periodType: 'fiscal', periodStart: '2023-04-01', periodEnd: '2024-03-31' })])
  e.periods[0].yearLabel = '2023/24'
  assert.equal(compareEmployerYear(reference({ periodType: 'unknown' }), e).status, 'period-review')
  assert.equal(compareEmployerYear(reference({ periodType: 'fiscal', periodStart: '2023-04-01', periodEnd: '2024-03-31' }), e).status, 'aggregate-count-match')
  assert.equal(compareEmployerYear(reference(), e).status, 'missing-period')
})

test('a known fiscal period cannot be satisfied by a different fiscal year end', () => {
  const e = employer([cohort({ periodType: 'fiscal', periodStart: '2023-07-01', periodEnd: '2024-06-30' })])
  assert.equal(compareEmployerYear(reference({ periodType: 'fiscal', periodStart: '2023-04-01', periodEnd: '2024-03-31' }), e).status, 'missing-period')
})

test('council and executive records do not establish employee scope', () => {
  for (const scope of ['elected-officials', 'executive-compensation', 'board-remuneration']) {
    assert.equal(compareEmployerYear(reference(), employer([cohort({ scope })])).status, 'scope-mismatch')
  }
})

test('matching employee cohort ignores separate council records', () => {
  const result = compareEmployerYear(reference(), employer([cohort(), cohort({ sourceId: 'council-2024', scope: 'elected-officials', rows: 5 })]))
  assert.equal(result.status, 'aggregate-count-match')
  assert.equal(result.repositoryComparableRows, 10)
})

test('warned and partial disclosures cannot get an aggregate pass', () => {
  assert.equal(compareEmployerYear(reference(), employer([cohort({ publicWarning: 'A published control residual needs review' })])).status, 'source-warning-review')
  assert.equal(compareEmployerYear(reference(), employer([cohort({ partialDisclosure: true })])).status, 'partial-disclosure')
})

test('overlapping employee cohorts must be reviewed, not blindly summed', () => {
  assert.equal(compareEmployerYear(reference({ recordCount: 20 }), employer([cohort(), cohort({ sourceId: 'amendment' })])).status, 'multiple-cohorts-review')
})

test('unknown scope or threshold prevents a misleading count comparison', () => {
  assert.equal(compareEmployerYear(reference({ scope: undefined }), employer([cohort()])).status, 'scope-review')
  assert.equal(compareEmployerYear(reference({ threshold: null }), employer([cohort()])).status, 'threshold-review')
  assert.equal(compareEmployerYear(reference({ thresholdComparison: '>=' }), employer([cohort()])).status, 'threshold-review')
})

test('missing count does not become zero', () => {
  assert.equal(compareEmployerYear(reference({ recordCount: null }), employer([cohort()])).status, 'record-count-unavailable')
})

test('an observed zero does not invent missing salary rows', () => {
  assert.equal(compareEmployerYear(reference({ year: '2020', recordCount: 0 }), employer([cohort()])).status, 'zero-reference-count')
  const report = buildSunshineComparison(snapshot([reference({ recordCount: 0 })]), repository([]))
  assert.equal(report.employers[0].years[0].status, 'unmatched-employer-zero-count')
})

test('unique people and unknown count bases cannot match disclosure rows', () => {
  for (const countBasis of ['unique-individuals', 'named-records', 'unknown', undefined]) {
    assert.equal(compareEmployerYear(reference({ countBasis }), employer([cohort()])).status, 'count-basis-review')
  }
})

test('an unknown numeric year only suggests a verified fiscal ending year', () => {
  const e = employer([cohort({ periodType: 'fiscal', periodStart: '2024-04-01', periodEnd: '2025-03-31', periodEndYear: 2025 })])
  e.periods[0].yearLabel = '2024/25'
  assert.equal(compareEmployerYear(reference({ periodType: 'unknown' }), e).status, 'missing-period')
})

test('comparable lower, equal and higher counts stay distinct', () => {
  for (const [recordCount, status, difference] of [[12, 'repository-fewer-records', -2], [10, 'aggregate-count-match', 0], [8, 'repository-more-records', 2]]) {
    const result = compareEmployerYear(reference({ recordCount }), employer([cohort()]))
    assert.equal(result.status, status); assert.equal(result.countDifference, difference)
  }
})

test('partial directory never passes even when every observed annual count matches', () => {
  const report = buildSunshineComparison(snapshot([reference()]), repository([employer([cohort()])]))
  assert.equal(report.status, 'incomplete-reference')
  assert.equal(report.summary.annualStatuses['aggregate-count-match'], 1)
  assert.equal(report.summary.recordLevelParityChecked, false)
})

test('summary ranges are not expanded into assumed annual observations', () => {
  const input = snapshot([])
  input.employers[0].aggregate = { recordCount: 200, yearRangeLabel: '2005–2025', yearMin: 2005, yearMax: 2025 }
  const report = buildSunshineComparison(input, repository([employer([cohort()])]))
  assert.equal(report.summary.referenceAnnualObservations, 0)
  assert.equal(report.employers[0].status, 'summary-only')
  assert.equal(report.queue[0].status, 'summary-only')
})

test('unknown employer becomes a review task and is never auto-created', () => {
  const report = buildSunshineComparison(snapshot([reference()]), repository([]))
  assert.equal(report.summary.unmatchedEmployers, 1)
  assert.equal(report.employers[0].years[0].status, 'missing-employer')
})

test('source leads are kept separate from accepted records and deduplicated', () => {
  const repo = repository([employer([cohort()])])
  const lead = { id: 'pdf', employerSlug: 'city-of-example', year: '2023', url: 'https://example.ca/2023.pdf', status: 'requires-ocr', scope: 'employee-remuneration', nextAction: 'Verify OCR.' }
  repo.sourceCatalog = [lead, { ...lead }, { ...lead, year: '2024', status: 'imported' }]
  const report = buildSunshineComparison(snapshot([]), repo)
  assert.equal(report.summary.repositorySourceTasks, 1)
  assert.equal(report.summary.externalReferenceTasks, 1)
})

test('same-name source employers at different URLs retain distinct change-tracking IDs', () => {
  const input = snapshot([])
  input.employers.push({ ...input.employers[0], url: 'https://www.sunshinelists.ca/british-columbia/employers/another-example' })
  const report = buildSunshineComparison(input, repository([employer([cohort()])]))
  assert.equal(report.queue.length, 2)
  assert.equal(new Set(report.queue.map(task => task.id)).size, 2)
  const changed = buildSunshineComparison({ ...input, employers: [input.employers[1]] }, repository([employer([cohort()])]))
  assert.equal(compareReportChanges(report, changed).removedTasks.length, 1)
})

test('repeated comparisons are deterministic and report removed employee periods', () => {
  const input = snapshot([reference()])
  const repo = repository([employer([cohort()])])
  const first = buildSunshineComparison(input, repo)
  assert.deepEqual(buildSunshineComparison(input, repo), first)
  const second = buildSunshineComparison(input, repository([]))
  const changes = compareReportChanges(first, second)
  assert.deepEqual(changes.officialEmployeePeriodsRemoved, [{ employerSlug: 'city-of-example', year: '2024' }])
  assert.equal(changes.rowChange, -10)
})

test('CSV safely quotes multiline data and spreadsheet formulas', () => {
  assert.equal(toCsv([{ name: '=CMD()', note: 'one,"two"\nthree', amount: -3 }], ['name', 'note', 'amount']), 'name,note,amount\n\'=CMD(),"one,""two""\nthree",-3\n')
})

test('normalized JSON and CSV both reach the same observed annual count decision', () => {
  const input = snapshot([reference()])
  input.source.collectionMethod = 'authorized-snapshot'
  const normalized = normalizeSunshineSnapshot(input)
  const roundtrip = parseSunshineCsv(sunshineSnapshotToCsv(normalized), normalized.source)
  const repo = repository([employer([cohort()])])
  for (const source of [normalized, roundtrip]) {
    const report = buildSunshineComparison(source, repo)
    assert.equal(report.employers[0].years[0].status, 'aggregate-count-match')
    assert.equal(report.status, 'incomplete-reference')
  }
})
