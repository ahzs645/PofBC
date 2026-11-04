import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { buildWorkforce, runWorkforceBuild } from './build-workforce.mjs'

const source = JSON.parse(readFileSync(new URL('../research/salaries/workforce/PSA-2024-42006.json', import.meta.url), 'utf8'))
const expected = {
  all: [[2017, 31153, 63704], [2018, 32787, 64956], [2019, 34333, 67187], [2020, 34783, 69170], [2021, 35565, 70917], [2022, 36149, 73775], [2023, 38352, 78802], [2024, 40787, 81718]],
  victoria: [[2017, 14366, 72066], [2018, 15180, 73680], [2019, 21405, 73715], [2020, 15662, 78082], [2021, 15686, 80035], [2022, 15535, 83047], [2023, 15388, 88262], [2024, 15493, 91347]],
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
  assert.deepEqual(source.source.duplicatePages, [{ tablePage: 1, repeatPage: 2 }, { tablePage: 3, repeatPage: 4 }])
  assert.deepEqual(source.populations.map(row => [row.id, row.sourceLabel, row.sourcePage, row.corroboratingPage, row.parentPopulationId]), [
    ['all', 'Data for all BC Public Service employees', 1, 2, null],
    ['victoria', 'Data for BC Public Service employees whose office is located in Victoria', 3, 4, 'all'],
  ])
  assert.deepEqual(source.period, { label: 'Year label', periodType: 'unverified', periodStart: null, periodEnd: null })
  assert.equal(source.measures.averageHeadCount.label, 'Average HeadCount')
  assert.equal(source.measures.averageSalary.label, 'Average Salary')
  assert.equal(source.measures.averageSalary.calculationMethod, 'unknown')
  assert.match(source.measures.averageSalary.currencyBasis, /inferred/)
  assert.ok(source.notes.some(note => note.includes('21,405') && note.includes('does not explain')))
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
