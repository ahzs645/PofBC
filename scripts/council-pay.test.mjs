import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { buildCouncilPay, checkTable, checkCbc2021, checkSourceComparisons, normalizePayment, validateDataset, datasetCsv } from './build-council-pay.mjs'

const old = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/vancouver-payments-transcription.json', import.meta.url)))
const modern = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/vancouver-modern-payments-transcription.json', import.meta.url)))
const payment = (year, pattern) => {
  const table = [...old.tables, ...modern.tables].find((table) => table.year === year)
  return normalizePayment(table, table.rows.find((row) => pattern.test(row.sourceName)))
}

test('all 320 CBC figures reconcile to source blocks and Port Hardy keeps its actual year', () => {
  const evidence = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/cbc-2021-transcription-evidence.json', import.meta.url)))
  const { data } = buildCouncilPay()
  assert.equal(checkCbc2021(evidence, data.observations), 320)
  const portHardy = data.observations.filter((row) => row.sourceId === 'cbc-bc-municipal-office-pay-2021' && row.municipality === 'Port Hardy')
  assert.equal(portHardy.length, 2)
  assert.ok(portHardy.every((row) => row.year === 2020))
  const changed = structuredClone(data.observations); changed.find((row) => row.id === portHardy[0].id).year = 2021
  assert.throws(() => checkCbc2021(evidence, changed), /reference year/)
})

test('CBC and official rate differences remain independently sourced observations', () => {
  const { data } = buildCouncilPay()
  const saanich = data.observations.filter((row) => row.municipality === 'Saanich' && row.role === 'Councillor' && row.year === 2021)
  assert.deepEqual(new Set(saanich.map((row) => row.amount)), new Set([49423, 49242.57]))
  assert.equal(new Set(saanich.map((row) => row.sourceId)).size, 2)
  const earlier = data.observations.filter((row) => row.sourceId === 'cbc-bc-municipal-office-pay-2019-viewroyal-extract')
  assert.equal(earlier.length, 20)
  assert.equal(data.coverage.surveys.find((survey) => survey.input.includes('2019')).status, 'partial')
})

test('every accepted Vancouver table reconciles every published component total', () => {
  const controls = [...old.tables, ...modern.tables].flatMap(checkTable)
  assert.equal(controls.length, 61)
  assert.equal([...old.tables, ...modern.tables].reduce((n, table) => n + table.rows.length, 0), 182)
  const damaged = structuredClone(old.tables[0]); damaged.rows[0].values[0] += 0.01
  assert.throws(() => checkTable(damaged), /printed total mismatch/)
})

test('old tax-free officers allowance stays remuneration and source components survive', () => {
  const row = payment(1994, /Owen/)
  assert.equal(row.role, 'Mayor')
  assert.equal(row.remuneration, 66107.08)
  assert.equal(row.expenses, 9661.28)
  assert.equal(row.components.municipalOfficersAllowance, 22035.78)
})

test('blank expenses remain unknown, while explicit zero remains known', () => {
  const missing = payment(1998, /SULLIVAN/i)
  assert.equal(missing.expenses, null)
  assert.equal(missing.components.autoAllowance, null)
  assert.equal(missing.components.priorPeriodAutoAllowancePaidSeparately, 1563.65)
  assert.equal(payment(1999, /SULLIVAN/i).expenses, null)
  assert.equal(payment(2024, /Montague/i).components.travelConferences, 0)
})

test('modern office budgets are excluded from remuneration and personal expense sums', () => {
  const row = payment(2025, /Sim,/)
  assert.equal(row.remuneration, 212531)
  assert.equal(row.expenses, 47404)
  assert.equal(row.components.discretionaryExpenses, 1048221)
  assert.match(row.notes.join(' '), /political staff/)
})

test('election-year terms and printed names are not annualized or silently repaired', () => {
  const sim = payment(2022, /Sim,/)
  assert.equal(sim.remuneration, 20970)
  assert.equal(sim.role, 'Mayor')
  assert.equal(payment(2022, /Stewart,/).role, 'Mayor')
  const campell = payment(2002, /Campell/i)
  assert.match(campell.name, /Campell/)
  assert.equal(campell.role, 'Mayor')
  assert.match(campell.notes.join(' '), /spelling/)
})

test('1996 remains held and never leaks into the named payment dataset', () => {
  const { data } = buildCouncilPay()
  assert.equal(data.payments.some((row) => row.year === 1996), false)
  assert.equal(data.coverage.held[0].year, 1996)
  assert.match(data.coverage.held[0].evidenceUrl, /970722\/regmin/)
  assert.ok(data.observations.some((row) => row.year === 1996 && row.measure === 'annual-base-rate'))
})

test('base salary and supplements stay distinct from actual named pay', () => {
  const { data } = buildCouncilPay()
  const rate = data.observations.find((row) => row.municipality === 'Vancouver' && row.role === 'Councillor' && row.year === 2025)
  assert.equal(rate.amount, 104180)
  assert.equal(rate.annualSupplement, 3048)
  assert.notEqual(rate.amount, payment(2025, /Bligh/).remuneration)
  const saanich = data.observations.find((row) => row.sourceId === 'saanich-official-annual-rates' && row.role === 'Councillor' && row.year === 2021)
  assert.equal(saanich.amount, 49242.57)
  assert.match(saanich.effectiveDateNote, /June/)
})

test('source IDs and observation identities are checked before export', () => {
  const { data } = buildCouncilPay()
  assert.equal(validateDataset(data), true)
  const missingSource = structuredClone(data); missingSource.payments[0].sourceId = 'not-a-source'
  assert.throws(() => validateDataset(missingSource), /missing source/)
  const duplicate = structuredClone(data); duplicate.observations.push(duplicate.observations[0])
  assert.throws(() => validateDataset(duplicate), /Duplicate observation/)
})

test('retained compiled editions are cross-referenced without inflating pay or hiding a discrepancy', () => {
  const { data } = buildCouncilPay()
  assert.equal(data.coverage.candidateSourceEditionOverlaps, 22)
  assert.equal(data.coverage.sourceEditionExpenseDifferences, 1)
  const wiebe = data.payments.find((row) => row.year === 2020 && /Wiebe/i.test(row.name))
  assert.equal(wiebe.expenses, 7109)
  assert.equal(wiebe.existingEdition.expenses, 6929)
  assert.match(wiebe.notes.join(' '), /Source discrepancy/)
  const comparison = { officialObservationId: wiebe.id, officialName: wiebe.name, officialYear: 2020, officialRemuneration: 92721, officialExpenses: 7109, compiledName: 'Wiebe, M.', compiledSourceId: 'vancouver-compiled-council-2020-21', compiledEditionLabel: '2020/21', compiledRemuneration: 92721, compiledExpenses: 6929, expensesAgree: false }
  const compiled = [['Wiebe, M.', 'Councillor', 92721, 6929, 0, comparison.compiledSourceId]]
  checkSourceComparisons([comparison], [wiebe], compiled, [{ label: '2020/21' }])
  assert.throws(() => checkSourceComparisons([{ ...comparison, expensesAgree: true }], [wiebe], compiled, [{ label: '2020/21' }]), /agreement flag/)
  assert.throws(() => checkSourceComparisons([{ ...comparison, compiledExpenses: 7109 }], [wiebe], compiled, [{ label: '2020/21' }]), /compiled source-edition record/)
})

test('CSV preserves expense zero versus blank, measure and source attribution', () => {
  const { data } = buildCouncilPay()
  const csv = datasetCsv(data)
  assert.match(csv, /"record_type"/)
  assert.match(csv, /"annual-base-rate"/)
  assert.match(csv, /"actual-remuneration"/)
  assert.match(csv, /"source_url"/)
  assert.equal(csv.split('\r\n').filter(Boolean).length, data.observations.length + data.payments.length + 1)
})

test('generated output is deterministic and cannot write existing salary or name-link indexes', () => {
  const one = buildCouncilPay(); const two = buildCouncilPay()
  assert.deepEqual(one.outputs, two.outputs)
  assert.deepEqual(Object.keys(one.outputs).filter((path) => path.startsWith('public/')).sort(), ['public/salaries/council-pay.csv', 'public/salaries/council-pay.json'])
  const pkg = JSON.parse(readFileSync(new URL('../package.json', import.meta.url)))
  assert.match(pkg.scripts['build:salaries'], /build-council-pay\.mjs$/, 'The full salary build replaces its output directory; the council companion must be restored last.')
})
