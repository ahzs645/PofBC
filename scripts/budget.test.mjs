// The Budget mode's data: scripts/build-budget.mjs over research/finance/province-summary/ and
// research/finance/public-accounts-23-1/.

import test from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { parseCsv, reconcile } from './build-budget.mjs'
import { BUDGET_STATEMENTS } from '../src/government/budgetData.js'
import { HISTORICAL_BODIES, SUB_AGENCIES, LOCAL_BODIES } from '../src/government/historyData.js'
import { CURRENT_BODIES } from '../src/government/currentData.js'
import { RELATED_BODIES } from '../src/government/relatedBodies.js'
import { governmentIn } from '../src/government/snapshot.js'

const rows = parseCsv(readFileSync('research/finance/province-summary/statement-of-operations.csv', 'utf8'))
const yearRows = (year) => rows.filter((row) => row.fiscal_year === year).map((row) => ({ ...row }))
const years = [...new Set(rows.map((row) => row.fiscal_year))].sort()
const bodyFiles = readdirSync('public/budget').map((name) => JSON.parse(readFileSync(`public/budget/${name}`, 'utf8')))
const atlasIds = new Set([...HISTORICAL_BODIES, ...SUB_AGENCIES, ...LOCAL_BODIES, ...CURRENT_BODIES].map((body) => body.id))
const relatedIds = new Set(RELATED_BODIES.map((body) => body.id))

test('the outputs are what the generator makes from the research', () => {
  const result = spawnSync(process.execPath, ['scripts/build-budget.mjs', '--check'], { encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
})

test('every fiscal year from 1999-00 to 2025-26 is covered, one after the other', () => {
  assert.equal(years[0], '1999-00')
  assert.equal(years.at(-1), '2025-26')
  years.forEach((year, at) => assert.equal(Number(year.slice(0, 4)), 1999 + at))
  assert.deepEqual(BUDGET_STATEMENTS.map((statement) => statement.year), years)
})

test('every printed subtotal reconciles, in every column', () => {
  for (const year of years) assert.deepEqual(reconcile(yearRows(year)), [], year)
})

test('the check fails when a line no longer adds to its total', () => {
  const changed = yearRows('2024-25')
  changed.find((row) => row.heading === 'Health').actual = String(Number(changed.find((row) => row.heading === 'Health').actual) + 1)
  const failures = reconcile(changed)
  assert.ok(failures.some((text) => /expense actual: the lines add to 91394, the total printed is 91393/.test(text)), failures.join('\n'))
})

test('the check fails when a surplus line does not follow from the totals', () => {
  const changed = yearRows('2001-02')
  const result = changed.find((row) => row.kind === 'result' && row.heading === 'Surplus (deficit) for the year')
  result.actual = String(Number(result.actual) - 1)
  assert.ok(reconcile(changed).some((text) => /"Surplus \(deficit\) for the year" is printed -1234; the lines above give -1233/.test(text)))
})

test('a "Less:" line is taken away and a missing total is reported', () => {
  assert.deepEqual(reconcile(yearRows('2000-01')), [])
  const missing = yearRows('2008-09').filter((row) => !(row.section === 'revenue' && row.kind === 'total'))
  assert.ok(reconcile(missing).some((text) => /revenue: 0 totals printed/.test(text)))
})

test('figures read from the PDFs match the printed statement', () => {
  const statement = (year) => BUDGET_STATEMENTS.find((each) => each.year === year)
  const line = (year, heading) => [...statement(year).revenue.lines, ...statement(year).expense.lines].find((each) => each.heading === heading).actual
  assert.equal(statement('2024-25').revenue.total.actual, 84046)
  assert.equal(statement('2024-25').expense.total.actual, 91393)
  assert.equal(statement('2024-25').surplus.actual, -7347)
  assert.equal(line('2024-25', 'Health'), 38182)
  assert.equal(line('2024-25', 'Taxation'), 49446)
  assert.equal(statement('2008-09').revenue.total.actual, 38328)
  assert.equal(statement('2008-09').surplus.actual, 78)
  assert.equal(line('2015-16', 'Fees and licenses'), 5836)
  assert.equal(statement('1999-00').surplus.actual, 52)
  assert.equal(line('1999-00', 'Recoveries'), 1311)
})

test('every year cites its own Summary Financial Statements PDF and page', () => {
  for (const statement of BUDGET_STATEMENTS) {
    assert.equal(statement.source.url, `https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/${statement.year}/pa-${statement.year}-summary-financial-statements.pdf`)
    assert.ok(Number.isInteger(statement.source.pdfPage) && statement.source.pdfPage > 0, statement.year)
    assert.match(statement.source.title, /Statement of Operations/)
    assert.ok(statement.revenue.lines.every((line) => line.key && line.heading && Number.isInteger(line.actual)), statement.year)
    assert.ok(statement.expense.lines.some((line) => line.key === 'health') && statement.expense.lines.some((line) => line.key === 'education'), statement.year)
  }
})

test('the self-supported net earnings line agrees with the Crown table where both are on the same basis', () => {
  // Two publications: the statement of operations and the Supplementary Information table. Before
  // 2018-19 consolidation adjustments make them differ; from then they are printed equal.
  const table = parseCsv(readFileSync('research/finance/public-accounts-23-1/adjusted-net-income.csv', 'utf8'))
  for (const statement of BUDGET_STATEMENTS.filter((each) => each.year >= '2018-19')) {
    const row = table.find((each) => each.fiscal_year === statement.year && /^net impact of self/i.test(each.name_as_printed))
    assert.equal(statement.revenue.lines.find((line) => line.key === 'crowns').actual, Number(row.c3), statement.year)
  }
})

test('every linked body is a site body, and an atlas link opens a year the diagram draws it', () => {
  const drawn = new Map()
  for (const file of bodyFiles) {
    for (const entry of [...file.crowns, ...file.selfSupported, ...file.members]) {
      if (!entry.id) continue
      if (entry.related) { assert.ok(relatedIds.has(entry.id), `${file.year} ${entry.id}`); continue }
      assert.ok(atlasIds.has(entry.id), `${file.year} ${entry.id}`)
      if (!drawn.has(entry.at)) drawn.set(entry.at, new Set(governmentIn(entry.at, { includeUndated: true, includeLocal: true }).nodes.map((node) => node.id)))
      assert.ok(drawn.get(entry.at).has(entry.id), `${file.year} ${entry.id} is not drawn in ${entry.at}`)
    }
  }
})

test('SUCH sector rows sit under Health and Education, and each body row cites its table page', () => {
  for (const file of bodyFiles) {
    assert.match(file.source?.url ?? '', /pa-\d{4}-\d{2}-supplementary-information\.pdf$/, file.year)
    for (const row of file.such) assert.ok(['health', 'education'].includes(row.function), `${file.year} ${row.name}`)
    for (const row of [...file.crowns, ...file.selfSupported, ...file.such]) assert.ok(Number.isInteger(row.page) && row.page > 0, `${file.year} ${row.name}`)
  }
  const latest = bodyFiles.find((file) => file.year === '2024-25')
  assert.ok(latest.members.some((row) => row.name === 'Northern Health Authority' && row.function === 'health' && row.id === 'northern-health'))
  assert.ok(latest.such.some((row) => row.name === 'School Districts' && row.function === 'education'))
  assert.ok(latest.selfSupported.some((row) => /Hydro/.test(row.name)))
})
