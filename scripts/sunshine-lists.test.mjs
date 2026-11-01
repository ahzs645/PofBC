import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import {
  normalizeSunshineSnapshot, parseSunshineCsv, parseSunshineEmployerHtml,
  sunshineSnapshotToCsv, sunshineInputSha256, SUNSHINE_DIRECTORY_URL
} from './lib/sunshine-lists.mjs'

const source = () => ({
  url: SUNSHINE_DIRECTORY_URL,
  retrievedAt: '2026-11-01T06:00:00Z',
  complete: false,
  expectedEmployerCount: null,
  collectionMethod: 'authorized-snapshot',
  notes: []
})
const employer = (name = 'Example Employer', years = [{ year: '2024', recordCount: 10 }]) => ({
  name, url: `${SUNSHINE_DIRECTORY_URL}/example-employer`, years
})
const snapshot = (record = employer()) => ({ version: 1, source: source(), employers: [record] })

test('partial annual observations retain unknown periods, unknown counts, and zero distinctly', () => {
  const result = normalizeSunshineSnapshot(snapshot(employer('Example Employer', [
    { year: 2024, recordCount: '1,234' }, { year: '2023', recordCount: null }, { year: '2022', recordCount: 0 }
  ])))
  assert.deepEqual(result.employers[0].years.map((year) => [year.year, year.recordCount, year.periodType]), [
    ['2022', 0, 'unknown'], ['2023', null, 'unknown'], ['2024', 1234, 'unknown']
  ])
  assert.equal(result.summary.employerYearsWithCounts, 2)
  assert.equal(result.summary.directoryComplete, false)
  assert.deepEqual(normalizeSunshineSnapshot(result), result)
})

test('a boolean or advertised total cannot turn a search result into complete directory coverage', () => {
  const input = snapshot()
  input.source.complete = true
  input.source.expectedEmployerCount = 1
  assert.throws(() => normalizeSunshineSnapshot(input), /completenessEvidence/)
  input.source.complete = 'true'
  assert.throws(() => normalizeSunshineSnapshot(input), /must be a boolean/)
})

test('directory receipts reconcile every page and unique employer URL but do not imply full annual records', () => {
  const input = snapshot(employer('Example Employer', []))
  input.source.complete = true
  input.source.expectedEmployerCount = 1
  input.source.completenessEvidence = {
    kind: 'paginated-directory', pageCount: 1, reportedTotal: 1,
    pages: [{ page: 1, url: `${SUNSHINE_DIRECTORY_URL}?page=1`, sha256: sunshineInputSha256('synthetic receipt'), employerUrls: [input.employers[0].url] }]
  }
  const result = normalizeSunshineSnapshot(input)
  assert.equal(result.summary.directoryComplete, true)
  assert.equal(result.summary.employerYearCount, 0)
  input.source.completenessEvidence.pages[0].employerUrls.push(input.employers[0].url)
  assert.throws(() => normalizeSunshineSnapshot(input), /repeated/)
  input.source.completenessEvidence.pages[0].employerUrls.pop()
  input.source.completenessEvidence.pageCount = 2
  assert.throws(() => normalizeSunshineSnapshot(input), /page receipts/)
})

test('conflicting reporting periods, malformed counts, and duplicate observations fail closed', () => {
  for (const entry of [
    { year: '2020/22', recordCount: 1 },
    { year: '2020/21', recordCount: 1, periodType: 'calendar' },
    { year: '2020', recordCount: 1, periodType: 'calendar', periodStart: '2020-04-01', periodEnd: '2021-03-31' },
    { year: '2020', recordCount: 1, periodStart: '2020-02-30', periodEnd: '2020-12-31' },
    { year: '2020', recordCount: 1, periodStart: '2020-01-01' },
    { year: '2020', recordCount: '1,2' },
    { year: '2020', recordCount: -1 },
    { year: '2020', recordCount: true }
  ]) assert.throws(() => normalizeSunshineSnapshot(snapshot(employer('Example Employer', [entry]))))
  assert.throws(() => normalizeSunshineSnapshot(snapshot(employer('Example Employer', [{ year: '2024' }, { year: '2024' }]))), /repeated year/)
  const repeated = snapshot(); repeated.employers.push(employer())
  assert.throws(() => normalizeSunshineSnapshot(repeated), /repeated employer URL/)
})

test('CSV preserves quoted employer names, aggregate-only observations, and missing counts', () => {
  const input = 'name,url,year,recordCount,periodType,aggregateRecordCount,uniqueIndividuals,yearRangeLabel,yearMin,yearMax\r\n' +
    `"Example, Employer",${SUNSHINE_DIRECTORY_URL}/example,2024,,unknown,,,,,\r\n` +
    `Another Employer,${SUNSHINE_DIRECTORY_URL}/another,,,,1234,900,2005–2025,2005,2025\n`
  const parsed = parseSunshineCsv(input, source())
  assert.equal(parsed.summary.employerCount, 2)
  assert.equal(parsed.summary.employerYearCount, 1)
  assert.equal(parsed.summary.aggregateOnlyEmployers, 1)
  const aggregate = parsed.employers.find((record) => record.name === 'Another Employer')
  assert.equal(aggregate.aggregate.recordCount, 1234)
  assert.equal(aggregate.years.length, 0)
  const roundTrip = parseSunshineCsv(sunshineSnapshotToCsv(parsed), source())
  assert.deepEqual(roundTrip.employers, parsed.employers)
})

test('CSV rejects truncated input and annual values without an identified year', () => {
  assert.throws(() => parseSunshineCsv('name,url,year,recordCount\n"unfinished', source()), /Unclosed/)
  assert.throws(() => parseSunshineCsv(`name,url,year,recordCount\nExample,${SUNSHINE_DIRECTORY_URL}/example,,42`, source()), /without a year/)
  assert.throws(() => parseSunshineCsv('name,url,year,recordCount\nExample,url,2024', source()), /columns/)
  assert.throws(() => parseSunshineCsv('name,url,year,recordCount,salary\n', source()), /unsupported CSV column/)
})

test('JSON and CSV retain the comparison operator and record-count basis used by the coverage comparator', () => {
  const observation = {
    year: '2024', recordCount: 123, periodType: 'calendar', periodStart: '2024-01-01', periodEnd: '2024-12-31',
    scope: 'named-employees-over-threshold', threshold: 75000, thresholdComparison: '>=', countBasis: 'records'
  }
  const parsed = normalizeSunshineSnapshot(snapshot(employer('Example Employer', [observation])))
  assert.deepEqual(parsed.employers[0].years[0], observation)
  assert.deepEqual(parseSunshineCsv(sunshineSnapshotToCsv(parsed), source()).employers[0].years[0], observation)
  assert.throws(() => normalizeSunshineSnapshot(snapshot(employer('Example Employer', [{ ...observation, thresholdComparison: '<=' }]))), /thresholdComparison/)
  assert.throws(() => normalizeSunshineSnapshot(snapshot(employer('Example Employer', [{ ...observation, countBasis: 'people-ish' }]))), /countBasis/)
  const unique = normalizeSunshineSnapshot(snapshot(employer('Example Employer', [{ ...observation, countBasis: 'unique-individuals' }])))
  assert.equal(unique.employers[0].years[0].countBasis, 'unique-individuals')
})

test('saved HTML extracts explicit aggregates without inventing intervening annual observations', () => {
  const html = `<html><body><script>const misleading = 'Total Records: 999 across 1 unique individuals'</script>
    <h3> Example&nbsp; <span>Employer</span> </h3>
    <div>Total Records: <strong>12,345</strong> across <b>1,234</b> unique individuals</div>
    <p>Years Present: 2007&ndash;2025</p><h2>Employer Analysis By Year</h2><table></table></body></html>`
  const result = parseSunshineEmployerHtml(html, { ...source(), url: `${SUNSHINE_DIRECTORY_URL}/example`, employerName: 'Example Employer' })
  assert.deepEqual(result.employers[0].aggregate, {
    recordCount: 12345, uniqueIndividuals: 1234, yearRangeLabel: '2007–2025', yearMin: 2007, yearMax: 2025
  })
  assert.deepEqual(result.employers[0].years, [])
  assert.equal(result.source.complete, false)
  assert.throws(() => parseSunshineEmployerHtml('<html><h3>Example</h3>Loading...</html>', { ...source(), employerName: 'Example' }), /no recognized employer summary/)
})

test('saved HTML cannot relabel another employer or borrow a summary from its next h3 block', () => {
  const summary = '<p>Total Records: 12,345 across 1,234 unique individuals</p><p>Years Present: 2007–2025</p>'
  const metadata = { ...source(), employerName: 'Provincial Health Services Authority' }
  assert.throws(() => parseSunshineEmployerHtml(`<h3>Fraser Health Authority</h3>${summary}`, metadata), /identity mismatch/)
  assert.throws(() => parseSunshineEmployerHtml(`<h3>Provincial Health Services Authority</h3><p>Related employer:</p><h3>Fraser Health Authority</h3>${summary}`, metadata), /different h3 identity/)
  assert.throws(() => parseSunshineEmployerHtml(summary, metadata), /missing an observed employer h3 heading/)
  assert.throws(() => parseSunshineEmployerHtml(`<script>const heading = '<h3>Provincial Health Services Authority</h3>'</script>${summary}`, metadata), /missing an observed employer h3 heading/)
  assert.throws(() => parseSunshineEmployerHtml(`<h3>Provincial Health Services Authority (Subsidiary)</h3>${summary}`, metadata), /identity mismatch/)
})

test('invalid input cannot overwrite the last successful CLI output', () => {
  const dir = mkdtempSync(join(tmpdir(), 'pofbc-sunshine-test-'))
  try {
    const input = join(dir, 'input.json'); const out = join(dir, 'output.json')
    writeFileSync(input, JSON.stringify({ ...snapshot(), source: { ...source(), complete: true } }))
    writeFileSync(out, 'previous successful result')
    const result = spawnSync(process.execPath, [resolve('scripts/import-sunshine-snapshot.mjs'), '--input', input, '--out', out], { encoding: 'utf8' })
    assert.notEqual(result.status, 0)
    assert.equal(readFileSync(out, 'utf8'), 'previous successful result')
    writeFileSync(input, JSON.stringify(snapshot()))
    const success = spawnSync(process.execPath, [resolve('scripts/import-sunshine-snapshot.mjs'), '--input', input, '--out', out], { encoding: 'utf8' })
    assert.equal(success.status, 0, success.stderr)
    const parsed = JSON.parse(readFileSync(out, 'utf8'))
    assert.equal(parsed.source.inputSha256, sunshineInputSha256(readFileSync(input)))
  } finally { rmSync(dir, { recursive: true, force: true }) }
})
