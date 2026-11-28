import test from 'node:test'
import assert from 'node:assert/strict'
import {
  BALANCE, BUDGET_YEARS, FUNCTION_ORDER, LATEST_YEAR, axisTicks, flowColumns, formatMillions, layoutFlow, readBudgetYear,
  statementFor, wrap
} from './budgetLayout.js'

test('the address picks a year, or the latest', () => {
  assert.equal(readBudgetYear('?view=government&mode=budget&fy=2008-09'), '2008-09')
  assert.equal(readBudgetYear('?fy=1850-51'), LATEST_YEAR)
  assert.equal(readBudgetYear(''), LATEST_YEAR)
  assert.equal(BUDGET_YEARS[0], '1999-00')
})

test('a deficit enters the flow as its own band, so both sides meet the total', () => {
  const statement = statementFor('2024-25')
  const { sources, uses, total } = flowColumns(statement)
  assert.equal(total, 91393)
  assert.equal(sources.find((line) => line.key === BALANCE).actual, 91393 - 84046)
  assert.ok(!uses.some((line) => line.key === BALANCE))
  const sum = (lines) => lines.reduce((add, line) => add + line.actual, 0)
  assert.equal(sum(sources), total)
  assert.equal(sum(uses), total)
  assert.deepEqual(uses.map((line) => line.key), FUNCTION_ORDER.filter((key) => uses.some((line) => line.key === key)))
})

test('a surplus leaves the flow as its own band', () => {
  const { sources, uses } = flowColumns(statementFor('2006-07'))
  assert.equal(uses.find((line) => line.key === BALANCE).actual, 38504 - 34448)
  assert.ok(!sources.some((line) => line.key === BALANCE))
})

test('every year lays out inside its box, the ribbons filling the total exactly', () => {
  for (const year of BUDGET_YEARS) {
    const flow = layoutFlow(statementFor(year), { width: 360, hubHeight: 300, gap: 8, slot: () => 40 })
    for (const side of [flow.sources, flow.uses]) {
      const thickness = side.reduce((add, line) => add + line.size, 0)
      assert.ok(Math.abs(thickness - flow.hub.size) < 1e-6, year)
      for (const line of side) assert.ok(line.y >= 0 && line.y + line.size <= flow.height + 1e-6, `${year} ${line.key}`)
    }
  }
})

test('each bar has a slot at least its label tall, so labels never overlap', () => {
  const flow = layoutFlow(statementFor('2024-25'), { width: 360, hubHeight: 300, gap: 8, slot: () => 40 })
  for (const side of [flow.sources, flow.uses]) {
    side.forEach((line, at) => {
      assert.ok(line.slotSize >= 40)
      if (at) assert.ok(line.slotTop >= side[at - 1].slotTop + side[at - 1].slotSize - 1e-9)
    })
  }
  assert.ok(flow.height >= 9 * 40)
})

test('headings wrap by words and figures read as the Province prints them', () => {
  assert.deepEqual(wrap('Net earnings of self–supported Crown corporations and agencies', 24), ['Net earnings of', 'self–supported Crown', 'corporations and', 'agencies'])
  assert.equal(formatMillions(-7347), '−$7,347 million')
  assert.equal(formatMillions(84046), '$84,046 million')
  assert.deepEqual(axisTicks(91393), [0, 20000, 40000, 60000, 80000, 100000])
})
