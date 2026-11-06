import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { buildEmployerStats, employerSnapshot, employerRanking } from './employerStats.js'

const years = ['2022', '2023', '2024']
const source = (year, extra = {}) => ({ sourceKind: 'official', scope: 'employee-remuneration',
  currency: 'CAD', periodType: 'calendar', periodStart: `${year}-01-01`, periodEnd: `${year}-12-31`,
  threshold: 75000, thresholdComparison: '>', ...extra })
const rows = (year, count, id, pay = 100000) => Array.from({ length: count }, (_, n) => [`Person, ${n}`, null, pay + n, null, year, id, null])
const build = (list, sources) => buildEmployerStats(list, { slug: 'test', years, sources })

test('employee measures keep exact cents, zero payments and the even median', () => {
  const list = rows(0, 4, 'a')
  ;[0, 100000.25, 100000.75, 200000].forEach((pay, at) => { list[at][2] = pay })
  const [cell] = build(list, { a: source(2022) })
  assert.equal(cell.count, 4)
  assert.equal(cell.median, 100000.5)
  assert.equal(cell.mean, 100000.25)
  assert.equal(cell.total, 400001)
  assert.equal(cell.above100k, 3)
})

test('comparisons exclude compiled, council, executive, foreign, incomplete and partial schedules', () => {
  const sources = {
    good: source(2022), compiled: source(2022, { sourceKind: 'compiled' }),
    council: source(2022, { scope: 'elected-officials' }), executive: source(2022, { scope: 'executive-only' }),
    usd: source(2022, { currency: 'USD' }), incomplete: source(2022, { completeEmployeeSchedule: false }),
    partial: source(2022, { periodEnd: '2022-06-30' })
  }
  const list = Object.keys(sources).flatMap((id) => rows(0, 10, id))
  assert.equal(build(list, sources)[0].count, 10)
  assert.deepEqual(build(list, sources)[0].sourceIds, ['good'])
})

test('overlapping employee cohorts with different definitions are not pooled', () => {
  assert.deepEqual(build([...rows(0, 10, 'a'), ...rows(0, 10, 'b')], {
    a: source(2022), b: source(2022, { threshold: 125000 })
  }), [])
})

const cells = () => build([...rows(0, 10, 'a'), ...rows(1, 12, 'b'), ...rows(2, 15, 'c')], {
  a: source(2022), b: source(2023), c: source(2024)
})

test('growth uses the latest adjacent comparable year inside the selected range', () => {
  assert.equal(employerSnapshot(cells()).growth, 0.25)
  assert.equal(employerSnapshot(cells()).added, 3)
  assert.equal(employerSnapshot(cells()).from, 1)
  assert.ok(Math.abs(employerSnapshot(cells(), [0, 1]).growth - 0.2) < 1e-12)
  assert.equal(employerSnapshot(cells(), [2, 2]).growth, null)
  assert.equal(employerSnapshot(cells(), [3, 4]), null)
})

test('gaps, changing thresholds, boundary rules, scope and duplicate names suppress growth', () => {
  const original = cells()
  for (const changes of [{ threshold: 125000 }, { comparison: '>=' }, { scope: 'new cohort' },
    { start: '2024-02-01' }, { uniqueNames: 14 }, { named: 14 }, { qualified: true }, { count: 9 }]) {
    const edited = structuredClone(original)
    Object.assign(edited[2], changes)
    assert.equal(employerSnapshot(edited).growth, null, JSON.stringify(changes))
  }
  assert.equal(employerSnapshot([original[0], original[2]]).growth, null)
})

test('a later compiled edition does not substitute for an official employee period', () => {
  const result = build([...rows(0, 12, 'a'), ...rows(2, 100, 'b')], {
    a: source(2022), b: source(2024, { sourceKind: 'compiled' })
  })
  assert.equal(employerSnapshot(result).year, 0)
  assert.equal(employerSnapshot(result).growth, null)
})

test('an observation repeated across official source editions is not counted twice', () => {
  assert.deepEqual(build([...rows(0, 10, 'a'), ...rows(0, 10, 'b')], {
    a: source(2022), b: source(2022)
  }), [])
})

test('rankings omit missing and small samples and sort declines without treating missing as zero', () => {
  const list = [
    { name: 'Small', stats: { count: 1, median: 900000, growth: 2 } },
    { name: 'Missing', stats: null },
    { name: 'Unknown', stats: { count: 20, median: 150000, growth: null } },
    { name: 'Decline', stats: { count: 20, median: 100000, growth: -0.1 } }
  ]
  assert.deepEqual(employerRanking(list, 'median').map((row) => row.name), ['Unknown', 'Decline'])
  assert.deepEqual(employerRanking(list, 'growth').map((row) => row.name), ['Decline'])
})

test('published statistics reproduce from every employer export without changing those exports', () => {
  execFileSync(process.execPath, ['scripts/build-employer-stats.mjs', '--check'], {
    cwd: new URL('../../', import.meta.url), stdio: 'pipe'
  })
})
