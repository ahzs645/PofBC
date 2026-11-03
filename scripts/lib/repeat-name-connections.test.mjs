import { test } from 'node:test'
import assert from 'node:assert/strict'
import { validateRepeatNameConnections } from './repeat-name-connections.mjs'

const index = {
  employers: [['Health', 'Health authorities', null, 'health']],
  years: ['2022/23', '2023/24'],
  sources: { report: { url: 'https://example.test/report.pdf', sha256: 'hash', sourceKind: 'official' }, copy: { sourceKind: 'compiled' } }
}
// People index rows: [name, position, pay, expenses, employer, year, source, page].
const report = ['Adams,Michael', null, 134969, 1200, 0, 1, 'report', 12]
const copy = ['Adarns, Michael', null, 134969, 1200, 0, 1, 'copy', null]
const decision = { employer: 'health', names: ['Adarns, Michael', 'Adams,Michael'], preferredName: 'Adams,Michael', decision: 'verified', note: 'misread',
  witnesses: [{ year: '2023/24', pay: 134969, expenses: 1200, sourceId: 'report' }] }
const payload = (decisions) => ({ schemaVersion: 1, decisions })

test('a repeat review joins a compiled misreading to the report record it copies', () => {
  const [entry] = validateRepeatNameConnections(payload([decision]), [report, copy], index)
  assert.deepEqual(entry.names, decision.names)
  assert.equal(entry.preferredName, 'Adams,Michael')
  assert.equal(entry.witnesses, undefined, 'witnesses are checked, not passed on')
})

test('a repeat review stops the build when its witness no longer holds', () => {
  assert.throws(() => validateRepeatNameConnections(payload([decision]), [report, { ...copy, 2: 1 }].map((row) => Object.values(row)), index), /No compiled record/)
  assert.throws(() => validateRepeatNameConnections(payload([decision]), [report, copy, ['Other,Person', null, 134969, 1200, 0, 1, 'report', 13]], index), /not unique/)
  assert.throws(() => validateRepeatNameConnections(payload([decision]), [report, copy, ['Adarns,Michael', null, 90000, 0, 0, 0, 'report', 3]], index), /printed the compiled spelling/)
  assert.throws(() => validateRepeatNameConnections(payload([{ ...decision, preferredName: 'Adarns, Michael' }]), [report, copy], index), /Incomplete/)
})
