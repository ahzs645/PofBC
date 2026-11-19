import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { summarizeSalaryGaps } from './build-current-salary-gaps.mjs'

const index = {
  years: ['2023/24', '2024/25'],
  recordCounts: { compiled: 1, official: 2 },
  sources: {
    legacy: { sourceKind: 'compiled', scope: 'employee-remuneration' },
    board: { sourceKind: 'official-pdf', scope: 'board-remuneration' },
    employee: { sourceKind: 'official-scanned-pdf', scope: 'employee-remuneration' },
  },
  employers: [
    { slug: 'school', names: ['School'], sector: 'School districts', counts: [1, 1],
      coverage: [{ sourceIds: ['legacy'] }, { sourceIds: ['employee'] }] },
    { slug: 'city', counts: [0, 1], coverage: [{ sourceIds: [] }, { sourceIds: ['board'] }] },
  ],
}
const roster = { municipalities: [
  { employerSlug: 'city', municipality: 'City', status: 'current' },
  { employerSlug: 'new-district', municipality: 'New District', status: 'pending-incorporation', effectiveFrom: '2026-11-06' },
] }

test('current gaps distinguish official editions and board-only disclosures', () => {
  const summary = summarizeSalaryGaps(index, roster, '2026-11-06')
  assert.equal(summary.schoolDistricts.soleOfficialYear2024_25, 1)
  assert.deepEqual(summary.schoolDistricts.districts[0].officialYears, ['2024/25'])
  assert.equal(summary.municipalities.withOfficialRecords, 1)
  assert.equal(summary.municipalities.withOfficialEmployeeRecords, 0)
})

test('incorporation changes the current roster, without adding historic salary periods', () => {
  assert.equal(summarizeSalaryGaps(index, roster, '2026-11-05').municipalities.total, 1)
  const summary = summarizeSalaryGaps(index, roster, '2026-11-06')
  assert.equal(summary.municipalities.total, 2)
  assert.deepEqual(summary.municipalities.withoutRecords, [
    { slug: 'new-district', municipality: 'New District', incorporated: '2026-11-06' },
  ])
})

test('committed current salary report matches the public employer index', () => {
  const read = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'))
  assert.deepEqual(
    read('../research/salaries/current-coverage-gaps.json'),
    summarizeSalaryGaps(read('../public/salaries/employers/index.json'), read('../research/salaries/municipal-audit/roster.json'), new Date().toISOString().slice(0, 10)),
  )
})
