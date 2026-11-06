import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { formatWorkforceNumber, formatWorkforceSalary, loadWorkforce, normalizeWorkforcePopulation, selectWorkforceRows, validateWorkforce, workforceAssetUrl, workforceCsv } from './workforce.js'

const source = JSON.parse(readFileSync(new URL('../../research/salaries/workforce/PSA-2024-42006.json', import.meta.url), 'utf8'))

test('population selection stays separate and defaults to all employees', () => {
  assert.equal(normalizeWorkforcePopulation(undefined), 'all')
  assert.equal(normalizeWorkforcePopulation('unknown'), 'all')
  assert.equal(normalizeWorkforcePopulation('victoria'), 'victoria')
  assert.equal(selectWorkforceRows(source, 'all').length, 8)
  assert.equal(selectWorkforceRows(source, 'victoria').length, 8)
  assert.equal(selectWorkforceRows(source, 'victoria')[2].averageHeadCount, 13972.25)
  assert.deepEqual(selectWorkforceRows(source, undefined).at(-1), { populationId: 'all', yearLabel: '2024', averageHeadCount: 40787, averageSalary: 81718 })
})

test('loader supports a deployment base and propagates cancellation', async () => {
  const controller = new AbortController()
  let request
  const result = await loadWorkforce({ base: '/PofBC', signal: controller.signal, fetcher: async (url, options) => {
    request = { url, options }
    return { ok: true, json: async () => structuredClone(source) }
  } })
  assert.equal(request.url, '/PofBC/salaries/workforce.json')
  assert.equal(request.options.signal, controller.signal)
  assert.equal(result.observations.length, 16)
  assert.equal(workforceAssetUrl('csv', '/PofBC/'), '/PofBC/salaries/workforce.csv')
})

test('loader rejects HTTP failures and invalid data for the retry state', async () => {
  await assert.rejects(loadWorkforce({ fetcher: async () => ({ ok: false, status: 503 }) }), /503/)
  await assert.rejects(loadWorkforce({ fetcher: async () => ({ ok: true, json: async () => ({}) }) }), /Unsupported workforce data/)
})

test('validation rejects duplicate chart-page observations and unverified method changes', () => {
  const duplicate = structuredClone(source)
  duplicate.observations[1] = { ...duplicate.observations[0] }
  assert.throws(() => validateWorkforce(duplicate), /Duplicate/)
  const extra = structuredClone(source)
  extra.observations.push({ ...extra.observations[0] })
  assert.throws(() => validateWorkforce(extra), /Incomplete/)
  const period = structuredClone(source)
  period.period.periodType = 'calendar'
  assert.throws(() => validateWorkforce(period), /periods have not been established/)
  const salary = structuredClone(source)
  salary.measures.averageSalary.calculationMethod = 'actual earnings'
  assert.throws(() => validateWorkforce(salary), /calculation methods have not been established/)
  const disjoint = structuredClone(source)
  disjoint.populations[1].parentPopulationId = null
  assert.throws(() => validateWorkforce(disjoint), /subset/)
})

test('CSV keeps exact labels, numeric amounts and provenance, and escapes text cells', () => {
  const csv = workforceCsv(source)
  assert.equal(csv.trimEnd().split('\r\n').length, 17)
  assert.match(csv, /"Year label","Average HeadCount","Average Salary"/)
  assert.match(csv, /"2017",31153,63704,"unverified",,,"unknown","unknown"/)
  assert.match(csv, /"PSA-2024-42006","https:\/\/docs.openinfo.gov.bc.ca\/Response_Package_PSA-2024-42006.pdf",3/)
  const escaped = structuredClone(source)
  escaped.populations[0].sourceLabel = '=SUM("untrusted")'
  assert.match(workforceCsv(escaped), /"'=SUM\(""untrusted""\)"/)
})

test('formatting preserves printed decimal precision', () => {
  assert.equal(formatWorkforceNumber(13972.25), '13,972.25')
  assert.equal(formatWorkforceSalary(81718), '$81,718')
})
