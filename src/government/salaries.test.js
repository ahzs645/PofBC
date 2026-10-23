import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { SALARY_INDEX, SALARY_YEARS } from './salaryIndex.js'
import { governmentIn, PRESENT_YEAR } from './snapshot.js'
import { salaryKeyOf } from './salaries.js'
import { HISTORICAL_BODIES, SUB_AGENCIES } from './historyData.js'
import { CURRENT_BODIES } from './currentData.js'

const known = new Set([...HISTORICAL_BODIES, ...SUB_AGENCIES, ...CURRENT_BODIES].map((body) => body.id))

test('every body with disclosed pay is one the atlas holds, bar the public service as a whole', () => {
  for (const id of Object.keys(SALARY_INDEX)) if (id !== 'public-service') assert.ok(known.has(id), id)
})

test('each year’s file is there, and its rows add up to the index', () => {
  for (const [id, years] of Object.entries(SALARY_INDEX)) {
    for (const [slug, totals] of Object.entries(years)) {
      const data = JSON.parse(readFileSync(new URL(`../../public/salaries/${slug}/${id}.json`, import.meta.url)))
      assert.equal(data.rows.length, totals.count, `${id} ${slug}`)
      assert.equal(data.rows.reduce((sum, row) => sum + row[2], 0), totals.total, `${id} ${slug}`)
      assert.equal(data.rows[0][2], totals.max)
    }
  }
  const labels = SALARY_YEARS.map(({ label }) => label)
  for (const label of ['2017/18', '2020/21', '2023/24']) assert.ok(labels.includes(label), label)
  assert.equal(new Set(labels).size, labels.length)
})

test('a ministry shows the public service’s pay, which is not disclosed by ministry', () => {
  const ministry = governmentIn(PRESENT_YEAR).nodes.find((node) => node.kind === 'ministry')
  assert.equal(salaryKeyOf(ministry), 'public-service')
  assert.equal(salaryKeyOf(governmentIn(PRESENT_YEAR).nodes.find((node) => node.id === 'bc-hydro')), 'bc-hydro')
  // A renamed body's earlier disclosures stay with the body it was then.
  assert.ok(SALARY_INDEX['oil-and-gas-commission']?.['2020-21'])
  assert.ok(SALARY_INDEX['bc-energy-regulator']?.['2023-24'])
})
