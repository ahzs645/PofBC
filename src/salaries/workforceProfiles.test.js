import test from 'node:test'
import assert from 'node:assert/strict'
import { numericColumns, profileNumber, profileParts, withMinistryNames } from './workforceProfiles.js'

const tables = [
  { name: 'WP2024_EmpCounts', recordType: 'aggregate-profile', columns: ['Ministry_Key', 'Employee_Type', 'Employee_Count'], rows: [['AF', 'ALL', '425'], ['ZZ', 'ALL', 'S']] },
  { name: 'WP2024_MinistryKey', recordType: 'ministry-lookup', columns: ['Ministry_Key', 'Ministry_Title'], rows: [['AF', 'Agriculture and Food']] },
  { name: 'WP2022_MinistryKey', recordType: 'ministry-lookup', columns: ['Ministry_Key', 'Ministry_Title'], rows: [['AF', 'Something else']] }
]

test('profile names split into edition and kind', () => {
  assert.deepEqual(profileParts('WP2024_Rep_Occ_Rgn'), { edition: '2024', kind: 'Rep_Occ_Rgn' })
})

test('ministry names come from the same edition’s key, and unknown keys stay blank', () => {
  const named = withMinistryNames(tables[0], tables)
  assert.deepEqual(named.columns, ['Ministry_Key', 'Ministry', 'Employee_Type', 'Employee_Count'])
  assert.deepEqual(named.rows, [['AF', 'Agriculture and Food', 'ALL', '425'], ['ZZ', '', 'ALL', 'S']])
  assert.equal(withMinistryNames(tables[1], tables), tables[1])
})

test('suppressed and missing cells are not numbers, and do not make a column text', () => {
  assert.equal(profileNumber('S'), null)
  assert.equal(profileNumber('4.3'), 4.3)
  assert.deepEqual(numericColumns(tables[0]), [false, false, true])
})
