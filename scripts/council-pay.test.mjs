import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { buildCouncilPay, checkTable, checkCbc2021, checkSourceComparisons, checkPaymentPrecisionEvidence, checkExpansionPreservation, normalizePayment, validateDataset, datasetCsv } from './build-council-pay.mjs'

const old = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/vancouver-payments-transcription.json', import.meta.url)))
const modern = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/vancouver-modern-payments-transcription.json', import.meta.url)))
const earlierExtension = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/vancouver-2004-2011-payments-transcription.json', import.meta.url)))
const laterExtension = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/vancouver-2012-2019-payments-transcription.json', import.meta.url)))
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

test('all original Vancouver tables retain their exact printed column controls', () => {
  const controls = [...old.tables, ...modern.tables].flatMap(checkTable)
  assert.equal(controls.length, 61)
  assert.equal([...old.tables, ...modern.tables].reduce((n, table) => n + table.rows.length, 0), 182)
  const damaged = structuredClone(old.tables[0]); damaged.rows[0].values[0] += 0.01
  assert.throws(() => checkTable(damaged), /printed total mismatch/)
})

test('the added payment years close the 2004–2019 gap without promoting the held 1996 report', () => {
  const { data, validation } = buildCouncilPay()
  assert.deepEqual(data.coverage.vancouverPaymentYears, [1994, 1995, ...Array.from({ length: 29 }, (_, at) => 1997 + at)])
  assert.deepEqual(data.coverage.vancouverPaymentGaps, [1996])
  assert.equal(earlierExtension.tables.reduce((sum, table) => sum + table.rows.length, 0), 104)
  assert.equal(laterExtension.tables.reduce((sum, table) => sum + table.rows.length, 0), 99)
  assert.equal(validation.counts.exactColumnControls, 114)
  assert.equal(validation.counts.roundingQualifiedControls, 15)
  assert.equal(data.coverage.paymentObservations, 385)
  const councilRates = data.coverage.timeSeries.find((series) => series.employerSlug === 'city-of-vancouver' && series.role === 'Councillor' && series.measure === 'annual-base-rate')
  assert.equal(councilRates.ranges, '1995–2026')
  assert.deepEqual(councilRates.missingYears, [])
})

test('older transportation allowances are included once and office budgets remain excluded', () => {
  const table = laterExtension.tables.find((entry) => entry.year === 2012)
  const mayor = normalizePayment(table, table.rows.find((row) => row.role === 'Mayor'))
  assert.equal(mayor.name, 'Robertson, G.')
  assert.equal(mayor.remuneration, 145581)
  assert.equal(mayor.expenses, 34441)
  assert.deepEqual(mayor.expenseComponentKeys, ['localExpenses', 'transportationAllowance', 'travelConferences'])
  const later = laterExtension.tables.find((entry) => entry.year === 2017)
  const laterMayor = normalizePayment(later, later.rows.find((row) => row.role === 'Mayor'))
  assert.equal(laterMayor.expenses, 60994)
  assert.equal(laterMayor.components.discretionaryExpenses, 706165)
  const invalid = structuredClone(later); invalid.expenseColumns.push('discretionaryExpenses')
  assert.throws(() => checkTable(invalid), /invalid personal expense component/)
})

test('Sullivan’s two 2005 roles retain separate amounts, source keys and term labels', () => {
  const { data } = buildCouncilPay()
  const rows = data.payments.filter((row) => row.year === 2005 && row.name === 'Sullivan, S.')
  assert.equal(rows.length, 2)
  assert.equal(new Set(rows.map((row) => row.id)).size, 2)
  assert.equal(rows.find((row) => row.role === 'Mayor').remuneration, 5935)
  assert.equal(rows.find((row) => row.role === 'Councillor').remuneration, 50269)
  assert.deepEqual(new Set(rows.map((row) => row.term)), new Set(['2005-2008', '2002-2005']))
  assert.ok(rows.every((row) => row.sourceRowLabel && row.sourceRowKey))
})

test('2018 keeps both actual printed subtables under one primary source', () => {
  const { data, validation } = buildCouncilPay()
  assert.equal(data.payments.filter((row) => row.year === 2018).length, 20)
  assert.equal(data.sources.filter((source) => source.id === 'vancouver-council-payments-2018').length, 1)
  const controls = validation.controls.filter((row) => row.year === 2018)
  assert.equal(controls.length, 8)
  assert.equal(new Set(controls.map((row) => row.tableLabel)).size, 2)
  assert.equal(controls.filter((row) => row.status === 'within-reported-rounding').length, 2)
})

test('rounding qualifications retain differences and cannot mask larger or cent-level errors', () => {
  const table = laterExtension.tables.find((entry) => entry.year === 2012)
  const control = checkTable(table).find((row) => row.column === 'transportationAllowance')
  assert.equal(control.printedTotal, 30262)
  assert.equal(control.sumOfDisclosedCells, 30263)
  assert.equal(control.difference, 1)
  assert.equal(control.status, 'within-reported-rounding')
  const unqualified = structuredClone(table); delete unqualified.rounding
  assert.throws(() => checkTable(unqualified), /printed total mismatch/)
  const large = structuredClone(table); large.rows[0].values[2] += 100
  assert.throws(() => checkTable(large), /exceeds documented rounding bound/)
  const centsError = structuredClone(table); centsError.rows[0].values[2] += 0.01
  assert.throws(() => checkTable(centsError), /whole-dollar cells/)
})

test('independent exact-cent evidence checks rounded cells without replacing source editions', () => {
  const first = earlierExtension.tables.find((table) => table.year === 2004)
  const [comparison] = checkPaymentPrecisionEvidence(first)
  assert.equal(comparison.checkedCells, 44)
  assert.equal(comparison.totalDifferences.find((row) => row.column === 'travelConferences').roundedPrimaryMinusCompared, 1)
  const evidence = earlierExtension.tables.filter((table) => [2010, 2011].includes(table.year)).flatMap(checkPaymentPrecisionEvidence)
  assert.equal(evidence.reduce((sum, entry) => sum + entry.checkedPersonAmounts, 0), 22)
  assert.deepEqual(evidence.map((entry) => entry.exactSum), [73089.62, 55988.82])
  const damaged = structuredClone(first); damaged.sourceComparisons[0].rows[0].values[0] += 1
  assert.throws(() => checkPaymentPrecisionEvidence(damaged), /rounded comparison cell differs/)
})

test('all prior companion amounts, roles, years and primary source URLs remain protected', () => {
  const { data } = buildCouncilPay()
  const baseline = JSON.parse(readFileSync(new URL('../research/salaries/council-pay-history-2026-11-04/timeseries-expansion-baseline.json', import.meta.url)))
  const result = checkExpansionPreservation(data, baseline)
  assert.equal(result.officeObservations, 430)
  assert.equal(result.namedPayments, 182)
  const modified = structuredClone(data)
  modified.observations.find((row) => row.id === baseline.protectedOfficeIds[0]).amount += 1
  assert.throws(() => checkExpansionPreservation(modified, baseline), /Prior council monetary values/)
})

test('survey years and precision do not fill gaps in an adopted-rate series', () => {
  const { data } = buildCouncilPay()
  const rates = data.coverage.timeSeries.find((entry) => entry.municipality === 'Victoria' && entry.role === 'Mayor' && entry.measure === 'annual-base-rate')
  assert.deepEqual(rates.years, [2022, 2024])
  assert.deepEqual(rates.missingYears, [2023])
  const survey = data.observations.find((row) => row.municipality === 'Victoria' && row.role === 'Mayor' && row.year === 2023)
  assert.equal(survey.measure, 'reported-office-pay')
  assert.equal(survey.amountPrecisionCad, 100)
  assert.ok(data.payments.filter((row) => row.year >= 2012 && row.year <= 2019).every((row) => row.sourcePrecision === 1))
})

test('Abbotsford’s explicitly stated rate interval retains its 2011 transition and source precision', () => {
  const { data } = buildCouncilPay()
  const rows = data.observations.filter((row) => row.sourceId === 'abbotsford-rate-interval-2007-2011-original-review')
  assert.equal(rows.length, 10)
  assert.ok(rows.every((row) => row.sourceEffectiveFrom === '2007-01-01' && row.sourceEffectiveTo === '2011-11-30' && row.amountPrecisionCad === 100))
  const earlier = rows.find((row) => row.year === 2011 && row.role === 'Mayor')
  const later = data.observations.find((row) => row.municipality === 'Abbotsford' && row.year === 2011 && row.role === 'Mayor' && row.effectiveFrom === '2011-12-01')
  assert.equal(earlier.effectiveTo, '2011-11-30')
  assert.equal(earlier.amount, 86600)
  assert.equal(later.amount, 94500)
  assert.match(datasetCsv({ ...data, observations: [earlier], payments: [] }), /"2007-01-01","2011-11-30"/)
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
