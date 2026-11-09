import test from 'node:test'
import assert from 'node:assert/strict'
import { csvText, employerCsv, rankOf } from './exportCsv.js'

test('CSV quotes text, keeps numbers and defuses formulas', () => {
  assert.equal(csvText(['a', 'b'], [['=SUM(1)', 12.5], ['He said "hi"', null]]), '"a","b"\r\n"\'=SUM(1)",12.5\r\n"He said ""hi""",\r\n')
})

test('employer rows carry their period, source and page', () => {
  const text = employerCsv([['Smith, A', 'Clerk', 80000, 120, 0, 's', 4]], { employer: 'Town', years: ['2024'], sources: { s: { title: 'SOFI 2024', url: 'https://x', scope: 'employee-remuneration' } } })
  assert.match(text, /"Town","2024","Smith, A","Clerk",80000,120,"employee-remuneration","SOFI 2024","https:\/\/x",4/)
})

test('an amount ranks among the records, ties together', () => {
  assert.deepEqual(rankOf(100, [50, 100, 100, 200]), { rank: 2, of: 4, share: 0.25 })
  assert.deepEqual(rankOf(300, [50, 100]), { rank: 1, of: 2, share: 1 })
  assert.equal(rankOf(Number.NaN, [1]), null)
})
