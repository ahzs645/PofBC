// The Money card's data: scripts/build-finance.mjs over research/finance/public-accounts-23-1/.

import test from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { HISTORICAL_BODIES, SUB_AGENCIES, LOCAL_BODIES } from '../src/government/historyData.js'
import { CURRENT_BODIES } from '../src/government/currentData.js'
import { RELATED_BODIES } from '../src/government/relatedBodies.js'
import { FINANCE_INDEX, FINANCE_TABLE_YEARS } from '../src/government/financeIndex.js'

const RESEARCH = 'research/finance/public-accounts-23-1'
const ids = new Set([...HISTORICAL_BODIES, ...SUB_AGENCIES, ...LOCAL_BODIES, ...CURRENT_BODIES, ...RELATED_BODIES].map((body) => body.id))
const files = readdirSync('public/finance').filter((name) => name !== 'sectors.json')
const bodies = files.map((name) => JSON.parse(readFileSync(`public/finance/${name}`, 'utf8')))
const byId = new Map(bodies.map((body) => [body.body, body]))
const researchText = ['inventory.csv', 'post-secondary-statements.csv'].map((name) => readFileSync(`${RESEARCH}/${name}`, 'utf8')).join('\n')

test('the outputs are what the generator makes from the research', () => {
  const result = spawnSync(process.execPath, ['scripts/build-finance.mjs', '--check'], { encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
})

test('every statement URL belongs to a known body and comes from the research lists', () => {
  for (const body of bodies) {
    assert.ok(ids.has(body.body), `${body.body} is not an atlas or related body`)
    for (const statement of body.statements) {
      assert.match(statement.url, /^https:\/\//, `${body.body} ${statement.year}`)
      assert.ok(researchText.includes(statement.url), `${body.body} ${statement.year}: ${statement.url} is not in the research lists`)
      assert.match(statement.year, /^\d{4}-\d{2}$/)
      assert.match(statement.fyEnd, /^\d{4}-03-31$/)
    }
  }
})

test('every table figure has its source PDF, page and unit, and is a whole number of millions', () => {
  let figures = 0
  for (const body of bodies) {
    for (const row of body.table) {
      assert.match(row.source.url, /pa-\d{4}-\d{2}-supplementary-information\.pdf$/, `${body.body} ${row.year}`)
      assert.ok(Number.isInteger(row.source.pdfPage) && row.source.pdfPage > 0, `${body.body} ${row.year}: no page`)
      assert.equal(row.unit, '$ millions', `${body.body} ${row.year}`)
      assert.equal(row.headings.length, 6, `${body.body} ${row.year}: headings`)
      for (const [key, value] of Object.entries(row.figures)) {
        if (value === null) continue
        assert.ok(Number.isInteger(value), `${body.body} ${row.year} ${key}: ${value}`)
        figures += 1
      }
    }
  }
  assert.ok(figures > 4000, `only ${figures} figures`)
})

test('no body has two rows for one year, except a body printed in both sections that year', () => {
  for (const body of bodies) {
    const statementKeys = body.statements.map((each) => `${each.year} ${each.url}`)
    assert.equal(new Set(statementKeys).size, statementKeys.length, `${body.body}: duplicate statements`)
    const rowKeys = body.table.map((row) => `${row.year} ${row.basis}`)
    assert.equal(new Set(rowKeys).size, rowKeys.length, `${body.body}: duplicate table rows`)
    const twice = Object.entries(Object.groupBy(body.table, (row) => row.year)).filter(([, rows]) => rows.length > 1)
    for (const [year, rows] of twice) assert.deepEqual(rows.map((row) => row.basis).sort(), ['self-supported', 'taxpayer-supported'], `${body.body} ${year}`)
  }
  // Transportation Investment Corporation moved from self- to taxpayer-supported on 1 September 2017.
  const ti = byId.get('transportation-investment-corporation').table.filter((row) => row.year === '2017-18')
  assert.equal(ti.length, 2)
  assert.ok(ti.some((row) => (row.notes ?? []).some((note) => /taxpayer–supported Crown corporation effective September 1, 2017/.test(note.text))))
})

test('the SUCH sector stays as sector totals and is not given to a body', () => {
  const sectors = JSON.parse(readFileSync('public/finance/sectors.json', 'utf8')).rows
  assert.deepEqual([...new Set(sectors.map((row) => row.name))].sort(), ['Colleges and Institutes', 'Health Authorities', 'Hospital Societies', 'SUCH sector', 'School Districts', 'Universities'])
  for (const body of bodies) for (const row of body.table) assert.doesNotMatch(row.name, /^(School Districts|Universities|Colleges and Institutes|Health Authorities|Hospital Societies|SUCH sector)$/)
  for (const id of ['northern-health', 'island-health', 'university-of-british-columbia']) assert.equal(FINANCE_INDEX[id].t, 0, id)
})

test('figures are as printed: BC Hydro 2024-25, BCNET 2024-25 and BC Ferries 1999-2000', () => {
  const hydro = byId.get('bc-hydro').table.find((row) => row.year === '2024-25')
  assert.deepEqual(hydro.figures, { revenue: 7478, expense: -6891, netIncome: 587, adjustments: null, fifth: -3, adjustedNetIncome: 584 })
  assert.equal(hydro.headings[4], 'Dividends')
  // The proposal's cross-check: BCNET revenue 28, expense (28), adjustments 4.
  const bcnet = byId.get('bcnet').table.find((row) => row.year === '2024-25')
  assert.deepEqual([bcnet.figures.revenue, bcnet.figures.expense, bcnet.figures.adjustments], [28, -28, 4])
  const ferries = byId.get('bc-ferry-corporation').table.find((row) => row.year === '1999-00')
  assert.deepEqual([ferries.figures.revenue, ferries.figures.expense, ferries.figures.netIncome, ferries.figures.adjustments, ferries.figures.adjustedNetIncome], [435, -734, -299, 1066, 767])
  assert.equal(ferries.headings[3], 'Policy Adjustments')
})

test('every printed subtotal matches the rows above it within rounding, in all 27 years', () => {
  assert.equal(FINANCE_TABLE_YEARS.length, 27)
  assert.equal(FINANCE_TABLE_YEARS[0], '1999-00')
  const checks = readFileSync(`${RESEARCH}/adjusted-net-income-checks.csv`, 'utf8').trim().split('\n').slice(1)
  assert.ok(checks.length > 700)
  assert.deepEqual(checks.filter((line) => !line.endsWith(',yes')), [])
})

test('the index agrees with the detail files, and new bodies are joined', () => {
  for (const body of bodies) {
    assert.equal(FINANCE_INDEX[body.body].s, body.statements.length, body.body)
    assert.equal(FINANCE_INDEX[body.body].t, body.table.length, body.body)
  }
  for (const id of ['bcnet', 'health-employers-association-of-bc', 'organized-crime-agency-of-bc', 'providence-health-care', 'creston-valley-wildlife-management-authority']) {
    assert.ok(FINANCE_INDEX[id]?.s > 0, id)
  }
})
