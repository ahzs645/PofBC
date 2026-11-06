import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { buildWorkforce, runWorkforceBuild } from './build-workforce.mjs'

const source = JSON.parse(readFileSync(new URL('../research/salaries/workforce/PSA-2024-42006.json', import.meta.url), 'utf8'))
const expected = {
  all: [[2017, 31153, 63704], [2018, 32787, 64956], [2019, 34333, 67187], [2020, 34783, 69170], [2021, 35565, 70917], [2022, 36149, 73775], [2023, 38352, 78802], [2024, 40787, 81718]],
  victoria: [[2017, 12210.83, 69074.72], [2018, 13100.33, 70311.53], [2019, 13972.25, 72593.09], [2020, 14135.33, 75033.52], [2021, 14653.75, 76699.98], [2022, 15200.08, 79590.49], [2023, 16516.58, 84508.68], [2024, 17564.38, 87527.87]],
}

test('all 32 visually verified source values are preserved in 16 unique observations', () => {
  assert.equal(source.observations.length, 16)
  for (const [populationId, series] of Object.entries(expected)) {
    assert.deepEqual(source.observations.filter(row => row.populationId === populationId).map(row => [Number(row.yearLabel), row.averageHeadCount, row.averageSalary]), series)
  }
  assert.equal(new Set(source.observations.map(row => `${row.populationId}:${row.yearLabel}`)).size, 16)
})

test('source pages, overlapping populations and original labels are retained', () => {
  assert.equal(source.source.pageCount, 4)
  assert.equal(source.source.requestMetadata, null)
  assert.equal(source.source.duplicatePages, undefined)
  assert.match(source.source.pageContents['2'], /telework/)
  assert.deepEqual(source.populations.map(row => [row.id, row.sourceLabel, row.sourcePage, row.parentPopulationId]), [
    ['all', 'Data for all BC Public Service Employees', 1, null],
    ['victoria', 'Data for BC Public Service Employees assigned to Victoria offices', 3, 'all'],
  ])
  assert.deepEqual(source.period, { label: 'Year label', periodType: 'unverified', periodStart: null, periodEnd: null })
  assert.equal(source.measures.averageHeadCount.label, 'Average HeadCount')
  assert.equal(source.measures.averageSalary.label, 'Average Salary')
  assert.equal(source.measures.averageSalary.calculationMethod, 'unknown')
  assert.match(source.measures.averageSalary.currencyBasis, /inferred/)
  assert.ok(source.notes.every(note => !note.includes('21,405')))
})

test('generation is deterministic and does not mutate input or double-count chart pages', () => {
  const original = structuredClone(source)
  const first = buildWorkforce(source)
  const reordered = structuredClone(source)
  reordered.observations.reverse()
  assert.deepEqual(buildWorkforce(reordered), first)
  assert.deepEqual(source, original)
  assert.equal(JSON.parse(first.json).observations.length, 16)
  assert.equal(first.csv.trimEnd().split('\r\n').length, 17)
})

test('checked-in public downloads match the curated input exactly', () => {
  assert.match(runWorkforceBuild({ check: true }), /Checked/)
})

test('original official PDF bytes match the verified transcription source', () => {
  assert.equal(createHash('sha256').update(readFileSync(new URL('../research/salaries/workforce/PSA-2024-42006.pdf', import.meta.url))).digest('hex'), source.source.sha256)
})
