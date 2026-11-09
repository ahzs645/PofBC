import { test } from 'node:test'
import assert from 'node:assert/strict'
import { councilCsv, councilMoney, councilRows, councilSourceMap, councilSourceUrl, councilYearCoverage, describeCouncilYears, filterCouncilRows, loadCouncilPay, validateCouncilPay } from './councilPay.js'

const data = {
  version: 1,
  sources: [{ id: 'survey', title: 'CBC office survey', kind: 'reported-survey', url: 'https://example.org/survey', notes: ['Most common reported amount.'] }, { id: 'official', title: 'Official schedule', kind: 'official-rate-schedule', url: 'https://example.org/schedule' }],
  observations: [
    { id: 'survey-2021', municipality: 'Saanich', role: 'Councillor', year: 2021, amount: 42000, measure: 'reported-office-pay', sourceId: 'survey' },
    { id: 'official-2021', municipality: 'Saanich', role: 'Councillor', year: 2021, amount: 44000, measure: 'annual-base-rate', sourceId: 'official', effectiveFrom: '2021-06-01', notes: ['Changed partway through the year.'] },
    { id: 'official-2023', municipality: 'Vancouver', role: 'Mayor', year: 2023, amount: 190000, measure: 'annual-base-rate', sourceId: 'official' }
  ],
  payments: [{ id: 'payment-1994', municipality: 'Vancouver', name: 'Émilie Test', role: 'Councillor', year: 1994, remuneration: 30000, expenses: null, knownExpenses: 0, components: { travel: 0, missingComponent: null }, measure: 'actual-remuneration', sourceId: 'official' }]
}
const sources = councilSourceMap(data)

test('separate record kinds retain contradictory source observations without inferring named payments', () => {
  assert.equal(councilRows(data, 'rates'), data.observations)
  assert.equal(councilRows(data, 'payments'), data.payments)
  const rows = filterCouncilRows(data.observations, { municipality: 'Saanich', year: '2021' }, sources)
  assert.equal(rows.length, 2)
  assert.deepEqual(new Set(rows.map((row) => row.amount)), new Set([42000, 44000]))
  assert.ok(rows.every((row) => !('name' in row)))
  assert.equal(data.observations[0].id, 'survey-2021', 'sorting must not mutate published source order')
})

test('search is accent-insensitive, combines words in either order, and respects every filter', () => {
  assert.equal(filterCouncilRows(data.payments, { query: 'test emilie' }, sources).length, 1)
  assert.equal(filterCouncilRows(data.observations, { query: 'CBC Saanich', role: 'Councillor', year: 2021 }, sources)[0].sourceId, 'survey')
  assert.equal(filterCouncilRows(data.observations, { query: 'CBC Saanich', role: 'Mayor' }, sources).length, 0)
  assert.equal(filterCouncilRows(data.payments, { municipality: 'Saanich' }, sources).length, 0)
  assert.equal(filterCouncilRows(data.observations, { year: '1996' }, sources).length, 0, 'an uncovered year must not fall back to all records')
})

test('coverage uses each tab and municipality independently and leaves gaps explicit', () => {
  const rows = [1994, 1995, 1997, 1997, 2000].map((year) => ({ year }))
  assert.deepEqual(councilYearCoverage(rows), { years: [1994, 1995, 1997, 2000], missing: [1996, 1998, 1999] })
  assert.equal(describeCouncilYears([1995, 1994, 1997, 2000, 1997]), '1994–1995, 1997, 2000')
  assert.deepEqual(councilYearCoverage([]), { years: [], missing: [] })
  assert.deepEqual(councilYearCoverage(data.payments).years, [1994])
})

test('missing expenses are not zero; zero and negative disclosed values retain their values', () => {
  assert.equal(councilMoney(null), 'Not reported')
  assert.equal(councilMoney(undefined), 'Not reported')
  assert.equal(councilMoney(NaN), 'Not reported')
  assert.equal(councilMoney(0), '$0.00')
  assert.equal(councilMoney(-12.5), '-$12.50')
})

test('CSV retains source, measure, effective dates and missing expense components', () => {
  const rateCsv = councilCsv([data.observations[1]], 'rates', sources)
  assert.match(rateCsv, /"annual-base-rate"/)
  assert.match(rateCsv, /"2021-06-01"/)
  assert.match(rateCsv, /"https:\/\/example.org\/schedule"/)
  assert.match(rateCsv, /Changed partway through the year/)
  const paymentCsv = councilCsv(data.payments, 'payments', sources)
  assert.match(paymentCsv, /"actual-remuneration",,30000,,0,/)
  assert.match(paymentCsv, /""missingComponent"":null/)
  assert.match(paymentCsv, /"named-payment"/)
  assert.equal(paymentCsv.split('\r\n').length, 3)
})

test('CSV safely quotes names and neutralizes text formulas without changing numeric recoveries', () => {
  const row = { ...data.payments[0], name: '=SUM(1,2)', remuneration: -2, notes: ['One "quoted", comma-separated note.'] }
  const csv = councilCsv([row], 'payments', sources)
  assert.match(csv, /"'=SUM\(1,2\)"/)
  assert.match(csv, /,-2,,0,/)
  assert.match(csv, /One ""quoted"", comma-separated note/)
})

test('source URLs accept only web references', () => {
  assert.equal(councilSourceUrl('https://example.org/report.pdf'), 'https://example.org/report.pdf')
  assert.equal(councilSourceUrl('javascript:alert(1)'), null)
  assert.equal(councilSourceUrl(undefined), null)
})

test('CSV keeps supplements separate and includes original article and exact source locations', () => {
  const source = { ...data.sources[1], originalUrl: 'https://example.org/original', locator: 'Schedule A' }
  const row = { ...data.observations[1], annualSupplement: 3048, sourceLocator: 'Councillor row', tablePage: 5, tableBlock: 2 }
  const csv = councilCsv([row], 'rates', new Map([[source.id, source]]))
  assert.match(csv, /annual_supplement/)
  assert.match(csv, /44000,,,,3048,/)
  assert.match(csv, /"https:\/\/example.org\/original","Schedule A","Councillor row",,5,2,/)
})

test('CSV retains split-role provenance, expense definitions and reported precision', () => {
  const row = { ...data.payments[0], sourceRowKey: 'mayor-term', sourceRowLabel: 'Mayor (2005–2008)', tableLabel: 'Council payments', term: '2005–2008', expenseComponentKeys: ['localExpenses', 'transportationAllowance', 'travelConferences'], sourcePrecision: 1 }
  const csv = councilCsv([row], 'payments', sources)
  assert.match(csv, /source_row_key,source_row_label,table_label,council_term_label,expense_component_keys,reported_precision_cad/)
  assert.match(csv, /"mayor-term","Mayor \(2005–2008\)","Council payments","2005–2008","localExpenses \| transportationAllowance \| travelConferences",1\r\n/)
  const survey = councilCsv([{ ...data.observations[0], amountPrecisionCad: 100 }], 'rates', sources)
  assert.match(survey, /,100\r\n$/)
})

test('loader makes exactly one companion request under the deployed base path', async () => {
  const requests = []
  const signal = new AbortController().signal
  const loaded = await loadCouncilPay({ base: '/PofBC/', signal, fetcher: async (url, options) => {
    requests.push([url, options.signal])
    return { ok: true, json: async () => data }
  } })
  assert.equal(loaded, data)
  assert.deepEqual(requests, [['/PofBC/salaries/council-pay.json', signal]])
})

test('bad fetches and missing source references fail explicitly instead of presenting an empty history', async () => {
  await assert.rejects(loadCouncilPay({ fetcher: async () => ({ ok: false, status: 404 }) }), /404/)
  assert.throws(() => validateCouncilPay({ version: 2, sources: [], observations: [], payments: [] }), /Unsupported/)
  assert.throws(() => validateCouncilPay({ ...data, sources: [] }), /Incomplete/)
  assert.throws(() => validateCouncilPay({ ...data, observations: [...data.observations, data.observations[0]] }), /Incomplete/)
})

test('municipalities summarise their latest figure for each office', async () => {
  const { councilMunicipalities } = await import('./councilPay.js')
  const data = {
    observations: [
      { id: 'a', municipality: 'Kelowna', employerSlug: 'city-of-kelowna', role: 'Councillor', year: 2025, amount: 58080, measure: 'annual-base-rate' },
      { id: 'b', municipality: 'Kelowna', role: 'Councillor', year: 2025, amount: 58080, measure: 'reported-office-pay' },
      { id: 'c', municipality: 'Kelowna', role: 'Mayor', year: 2021, amount: 100000, measure: 'reported-office-pay' },
      { id: 'd', municipality: 'Kelowna', role: 'Mayor', year: 2025, amount: 140000, measure: 'reported-office-pay' },
      { id: 'e', municipality: 'Kelowna', role: 'Mayor', year: 2025, amount: 139000, measure: 'annual-base-rate' }
    ],
    payments: [{ id: 'p', municipality: 'Kelowna', role: 'Mayor', year: 2024, remuneration: 1 }]
  }
  const [kelowna] = councilMunicipalities(data)
  assert.equal(kelowna.employerSlug, 'city-of-kelowna')
  assert.deepEqual([kelowna.first, kelowna.last, kelowna.figures, kelowna.payments], [2021, 2025, 5, 1])
  assert.deepEqual(kelowna.offices, [{ role: 'Mayor', year: 2025, amount: 140000, disagree: true }, { role: 'Councillor', year: 2025, amount: 58080, disagree: false }])
})

test('the same amount from two sources is one figure; different amounts stay apart', async () => {
  const { councilFiguresByYear } = await import('./councilPay.js')
  const years = councilFiguresByYear([
    { id: 'a', role: 'Councillor', year: 2025, amount: 58080, measure: 'annual-base-rate', sourceId: 's1' },
    { id: 'b', role: 'Councillor', year: 2025, amount: 58080, measure: 'reported-office-pay', sourceId: 's2' },
    { id: 'c', role: 'Mayor', year: 2025, amount: 140000, measure: 'reported-office-pay', sourceId: 's2' },
    { id: 'd', role: 'Mayor', year: 2025, amount: 139000, measure: 'annual-base-rate', sourceId: 's1' },
    { id: 'e', role: 'Mayor', year: 2021, amount: 100000, measure: 'reported-office-pay', sourceId: 's3' }
  ])
  assert.deepEqual(years.map(({ year }) => year), [2025, 2021])
  const [mayor, councillor] = years[0].roles
  assert.equal(mayor.role, 'Mayor')
  assert.deepEqual(mayor.figures.map(({ amount }) => amount), [140000, 139000])
  assert.deepEqual(councillor.figures.map(({ measures, rows }) => [measures, rows.length]), [[['annual-base-rate', 'reported-office-pay'], 2]])
})

test('an amount rounded to the dollar agrees with the same amount in cents', async () => {
  const { councilFiguresByYear } = await import('./councilPay.js')
  const [{ roles: [mayor] }] = councilFiguresByYear([
    { id: 'a', role: 'Mayor', year: 2025, amount: 139502, measure: 'reported-office-pay', sourceId: 's1' },
    { id: 'b', role: 'Mayor', year: 2025, amount: 139502.08, measure: 'annual-base-rate', sourceId: 's2' }
  ])
  assert.equal(mayor.figures.length, 1)
  assert.equal(mayor.figures[0].amount, 139502.08)
})
