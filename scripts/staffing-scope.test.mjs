import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { STAFFING } from '../src/government/atlasData.js'

const ledger = JSON.parse(readFileSync('research/audit/atlas-import.json', 'utf8'))
const staffingRows = ledger.rows.filter((row) => row.origin.startsWith('staffing.json#'))

test('combined staffing rows stay aggregates and are never attributed to a node', () => {
  const aggregates = staffingRows.filter((row) => row.disposition === 'aggregate_scope')
  assert.equal(aggregates.length, 70)
  assert.deepEqual([...new Set(aggregates.map((row) => row.input.ministry_as_printed))].sort(), ['Officers of the Legislature', 'Other Appropriations'])
  assert.ok(aggregates.every((row) => row.scope === 'aggregate' && row.reason && !row.output_id))
  const printed = Object.values(STAFFING).flat().map((row) => row[3])
  assert.ok(!printed.includes('Officers of the Legislature') && !printed.includes('Other Appropriations'))
})

test('the three reviewed ministry rows map to the node standing under the printed name', () => {
  assert.equal(staffingRows.filter((row) => row.disposition === 'unresolved_unmapped').length, 0)
  const row = (id, year) => STAFFING[id].find((entry) => entry[0] === year && entry[1] === 'actual')
  assert.equal(row('ministry-of-public-safety-and-solicitor-general-2017', '2015/16')[2], 2737)
  assert.equal(row('ministry-of-advanced-education-skills-and-training-2017', '2019/20')[2], 373)
  assert.equal(row('ministry-of-advanced-education-and-skills-training-2020', '2020/21')[2], 383)
  assert.equal(STAFFING['ministry-of-advanced-education-and-skills-training-2020'].find((entry) => entry[0] === '2019/20'), undefined)
})
