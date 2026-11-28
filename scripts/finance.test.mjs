// The Money card's data: scripts/build-finance.mjs over research/finance/public-accounts-23-1/.

import test from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { HISTORICAL_BODIES, SUB_AGENCIES, LOCAL_BODIES } from '../src/government/historyData.js'
import { CURRENT_BODIES } from '../src/government/currentData.js'
import { RELATED_BODIES } from '../src/government/relatedBodies.js'
import { FINANCE_INDEX, FINANCE_TABLE_YEARS } from '../src/government/financeIndex.js'
import { MINISTRY_EPISODES } from '../src/government/episodes.js'

const RESEARCH = 'research/finance/public-accounts-23-1'
const ids = new Set([...HISTORICAL_BODIES, ...SUB_AGENCIES, ...LOCAL_BODIES, ...CURRENT_BODIES, ...RELATED_BODIES].map((body) => body.id))
// Ministries and the Legislative Assembly carry only their votes' estimates against actual.
const voteHolders = new Set([...MINISTRY_EPISODES.map((episode) => episode.id), 'legislative-assembly'])
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
    assert.ok(ids.has(body.body) || (voteHolders.has(body.body) && body.estimates && !body.statements.length), `${body.body} is not an atlas or related body`)
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

// ── Stages A to C: transfers, statement breakdowns, estimates against actual ───────────────────────

const FINANCE = 'research/finance'
const parse = (text) => {
  const rows = []
  let row = []; let field = ''; let quoted = false
  for (let i = 0; i < text.length; i += 1) {
    const c = text[i]
    if (quoted) { if (c === '"' && text[i + 1] === '"') { field += '"'; i += 1 } else if (c === '"') quoted = false; else field += c } else if (c === '"') quoted = true
    else if (c === ',') { row.push(field); field = '' } else if (c === '\n') { row.push(field); rows.push(row); row = []; field = '' } else if (c !== '\r') field += c
  }
  if (field || row.length) { row.push(field); rows.push(row) }
  const [head, ...body] = rows.filter((each) => each.length > 1 || each[0])
  return body.map((each) => Object.fromEntries(head.map((key, at) => [key, each[at] ?? ''])))
}
const table = (path) => parse(readFileSync(`${FINANCE}/${path}`, 'utf8'))

test('every alias resolves to a site body, and every matched transfer row comes through an alias', () => {
  const aliases = table('aliases.csv')
  assert.ok(aliases.length > 200, `only ${aliases.length} aliases`)
  for (const alias of aliases) if (alias.body_id) assert.ok(ids.has(alias.body_id), `${alias.payee_key} → ${alias.body_id}`)
  for (const decision of table('transfers/alias-decisions.csv')) if (decision.body_id) assert.ok(ids.has(decision.body_id), decision.payee_key)
  const totals = table('transfers/totals.csv')
  assert.deepEqual(totals.map((row) => Number(row.fye)), Array.from({ length: 20 }, (_, at) => 2007 + at))
  for (const file of totals) {
    const rows = table(`transfers/fye${file.fye}.csv`)
    assert.equal(rows.length, Number(file.matched_rows), `FYE ${file.fye} rows`)
    assert.equal(rows.reduce((sum, row) => sum + Number(row.amount), 0), Number(file.matched_total), `FYE ${file.fye} total`)
    for (const row of rows) {
      assert.ok(ids.has(row.body_id), `FYE ${file.fye}: ${row.body_id}`)
      assert.ok(aliases.some((alias) => alias.body_id === row.body_id), `${row.body_id} has no alias`)
      // No individual's name: a matched payee is never "SURNAME, GIVEN".
      assert.doesNotMatch(row.payee_as_printed, /^[A-Z'-]+, (?!THE$)[A-Z'-]+( [A-Z'-]+)?$/, `FYE ${file.fye}: ${row.payee_as_printed}`)
    }
  }
  // The proposal's worked example, FYE 2025.
  const fye25 = table('transfers/fye2025.csv')
  assert.equal(Number(totals.find((row) => row.fye === '2025').rows), 16648)
  const paid = (body, ministry) => fye25.filter((row) => row.body_id === body && row.ministry_as_printed === ministry).reduce((sum, row) => sum + Number(row.amount), 0)
  assert.equal(paid('northern-health', 'Health'), 1634729019)
  assert.equal(paid('bcnet', 'Post–Secondary Education and Future Skills'), 6028610)
  assert.equal(paid('college-of-new-caledonia', 'Post–Secondary Education and Future Skills'), 57138623)
})

test('statement breakdowns reconcile with the statement totals, line by line, with a page for each', () => {
  const index = table('statements/index.csv')
  assert.ok(index.length >= 20)
  for (const entry of index) {
    assert.ok(ids.has(entry.body_id), entry.body_id)
    assert.match(entry.url, /^https:\/\/.+\.pdf$/)
    assert.ok(Number(entry.pdf_page) > 0)
    const lines = table(`statements/${entry.body_id}/${entry.fiscal_year}.csv`)
    const sum = (section) => lines.filter((line) => line.section === section).reduce((total, line) => total + Number(line.amount_as_printed), 0)
    const one = (section) => { const found = lines.filter((line) => line.section === section); assert.equal(found.length, 1, `${entry.body_id} ${entry.fiscal_year} ${section}`); return Number(found[0].amount_as_printed) }
    const where = `${entry.body_id} ${entry.fiscal_year}`
    assert.equal(sum('revenue'), one('revenue-total'), `${where}: revenue`)
    assert.equal(sum('expense'), one('expense-total'), `${where}: expense`)
    assert.equal(one('revenue-total') - one('expense-total'), one('surplus'), `${where}: surplus`)
    for (const line of lines) assert.equal(line.pdf_page, entry.pdf_page, `${where}: ${line.label_as_printed}`)
    for (const line of lines.filter((each) => each.section === 'revenue')) assert.ok(['province', 'federal', 'own-source', 'other-entity', 'investment', 'deferred-capital-amortization', 'other'].includes(line.category), `${where}: ${line.label_as_printed}`)
    // The built file carries the same figures in whole dollars.
    const built = byId.get(entry.body_id).breakdowns.find((record) => record.year === entry.fiscal_year)
    const unit = { dollars: 1, thousands: 1000 }[entry.unit]
    assert.equal(built.revenueTotal.amount, one('revenue-total') * unit)
    assert.equal(built.expenseTotal.amount, one('expense-total') * unit)
  }
  // The proposal's worked example: Northern Health 2024-25, PDF page 7.
  const nh = byId.get('northern-health').breakdowns.find((record) => record.year === '2024-25')
  assert.equal(nh.revenueTotal.amount, 1672372000)
  assert.equal(nh.expenseTotal.amount, 1688433000)
  assert.equal(nh.revenue.find((line) => line.label === 'Ministry of Health contributions').amount, 1319628000)
  assert.equal(nh.page.pdf, 7)
})

test('each ministry’s vote rows sum to the printed vote totals and to the Total Voted Expense', () => {
  const votes = table('estimates/votes.csv')
  const totals = table('estimates/vote-totals.csv')
  const columns = ['estimates', 'other_authorizations', 'total_appropriation', 'actual_expense', 'variance']
  const years = [...new Set(votes.map((row) => row.fiscal_year))]
  assert.ok(years.length >= 16, `${years.length} years`)
  for (const total of totals) {
    const rows = votes.filter((row) => row.fiscal_year === total.fiscal_year && (total.vote === 'all' || row.vote === total.vote))
    assert.ok(rows.length > 0, `${total.fiscal_year} vote ${total.vote}`)
    for (const column of columns) {
      assert.equal(rows.reduce((sum, row) => sum + Number(row[column] || 0), 0), Number(total[column] || 0), `${total.fiscal_year} vote ${total.vote} ${column}`)
    }
  }
  for (const year of years) assert.ok(totals.some((row) => row.fiscal_year === year && row.vote === 'all'), `${year}: no Total Voted Expense`)
  // A vote that more than one ministry accessed has its printed total.
  for (const year of years) {
    const counts = Object.groupBy(votes.filter((row) => row.fiscal_year === year), (row) => row.vote)
    for (const [vote, rows] of Object.entries(counts)) if (rows.length > 1) assert.ok(totals.some((row) => row.fiscal_year === year && row.vote === vote), `${year} vote ${vote}`)
  }
})

test('the Supplement to the Estimates adds to the voted Estimates the Public Accounts print', () => {
  const supplement = table('estimates/supplement.csv')
  const totals = table('estimates/vote-totals.csv').filter((row) => row.vote === 'all')
  let compared = 0
  for (const year of [...new Set(supplement.map((row) => row.fiscal_year))]) {
    const printed = totals.find((row) => row.fiscal_year === year)
    if (!printed) continue
    const voted = supplement.filter((row) => row.fiscal_year === year && row.appropriation === 'voted').reduce((sum, row) => sum + Number(row.amount), 0)
    // Budget 2017 was re-tabled in September 2017; no catalogue file holds that update's Supplement.
    if (year === '2017-18') { assert.notEqual(voted, Number(printed.estimates) * 1000); continue }
    assert.equal(voted, Number(printed.estimates) * 1000, `${year}: Supplement ${voted} against ${printed.estimates} thousand`)
    compared += 1
  }
  assert.ok(compared >= 12, `${compared} years compared`)
})

test('ministry nodes carry their votes, and offices are joined by id', () => {
  const health = byId.get('ministry-of-health-2011')
  assert.ok(health.estimates.some((year) => year.year === '2024-25'))
  const vote = health.estimates.find((year) => year.year === '2024-25').votes[0]
  assert.match(vote.description, /Ministry Operations/)
  assert.ok(Number.isInteger(vote.page.pdf))
  for (const id of ['auditor-general', 'legislative-assembly', 'office-of-the-premier']) assert.ok(FINANCE_INDEX[id]?.e, id)
})
