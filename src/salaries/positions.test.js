import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { EMPLOYER_LAYOUT, personKey, withoutCompiledRepeats } from './people.js'
import { keyedTitles, meanMoney, relatedTitles, shortTitle, titleKey, titleLabel, titleMatcher, titleRecords, titleShard } from './positions.js'

const DIR = new URL('../../public/salaries/positions/', import.meta.url)
const read = (file) => JSON.parse(gunzipSync(readFileSync(new URL(file, DIR))))

test('one title however an employer spelled it, and no further', () => {
  assert.equal(titleKey('TEACHERS'), titleKey('Teacher'))
  assert.equal(titleKey('Sr. Policy Analyst'), titleKey('Senior Policy Analyst'))
  assert.equal(titleKey('Mayor (Jan0Oct) · City Council'), 'mayor')
  assert.equal(titleKey('Deputies'), 'deputy')
  assert.equal(titleKey('Status Clerk'), 'status clerk')
  assert.equal(titleKey('Chair & CEO'), 'chair and ceo')
  assert.notEqual(titleKey('Teacher'), titleKey('Teacher Elementary'))
  assert.equal(titleKey(null), '')
  assert.equal(titleShard('senior policy analyst'), 'se')
  assert.equal(titleShard(''), '__')
  assert.equal(titleLabel('Nurse 4 (C) · Ward 3'), 'Nurse 4')
  assert.equal(titleLabel('(Interim)'), '(Interim)')
})

test('a title search finds the same title, then those beginning with it, then those holding its words', () => {
  const match = titleMatcher('Teachers')
  assert.equal(match('teacher'), 0)
  assert.equal(match('teacher elementary'), 1)
  assert.equal(match('summer session teacher'), 2)
  assert.equal(match('principal'), null)
  assert.equal(titleMatcher('analyst policy')('senior policy analyst'), 2)
  assert.equal(titleMatcher('teach')('teaching staff'), 1)
  assert.equal(titleMatcher('')('teacher'), null)
})

test('related titles are the titles that add to one and those it adds to, never itself', () => {
  const titles = ['Senior Policy Analyst', 'Policy Analyst', 'Senior Policy Analyst Lead', 'Analyst', 'Nurse']
    .map((label, at) => ({ key: titleKey(label), label, rows: 10 - at, employers: 1 }))
  const { narrower, broader } = relatedTitles(titles, 'senior policy analyst')
  assert.deepEqual(narrower.map((title) => title.label), ['Senior Policy Analyst Lead'])
  assert.deepEqual(broader.map((title) => title.label), ['Policy Analyst', 'Analyst'])
})

test('an average is worked out to the dollar', () => {
  assert.equal(meanMoney([100000.5, 100001]), 100001)
  assert.equal(meanMoney([]), null)
})

test('the position index lists each title once, filed in the slice its key names', () => {
  const index = read('index.json.gzip')
  const titles = keyedTitles(index)
  assert.equal(new Set(titles.map((title) => title.key)).size, titles.length)
  assert.ok(titles.length > 1000)
  const teacher = titles.find((title) => title.key === 'teacher')
  assert.ok(teacher.employers > 1, 'one title gathered across employers')
  const slice = read(`${titleShard('teacher')}.json.gzip`)
  assert.equal(slice.teacher.cells.reduce((sum, cell) => sum + cell[2], 0), teacher.rows)
  for (const [, year, rows, mean, median, low, high] of slice.teacher.cells) {
    assert.ok(index.years[year] && rows > 0 && low <= mean && mean <= high && low <= median && median <= high)
  }
})

test('a card title drops a department it already names', () => {
  assert.equal(shortTitle('Senior Vice President, Private Equity · Private Equity'), 'Senior Vice President, Private Equity')
  assert.equal(shortTitle('Director · Finance'), 'Director · Finance')
})

const roleSources = {
  official: { url: 'https://example.test/employer-report.pdf', sha256: 'verified-report', scope: 'employee-remuneration' },
  compiled: { sourceKind: 'compiled', scope: 'compiled-unverified' }
}
const analyst = 'senior policy analyst'
const disclosedNameKey = (row) => personKey(row[0] ?? '')
const employerRow = (name, position, source, expenses = 2559) => [name, position, 84953, expenses, 0, source, source === 'official' ? 42 : null]

test('a role retains its compiled title when the identical official payment does not disclose a title', () => {
  const official = Object.freeze(employerRow('Greene, Alexis', null, 'official'))
  const compiled = Object.freeze(employerRow('Greene, Alexis', 'Senior Policy Analyst', 'compiled'))
  const rows = Object.freeze([official, compiled])
  // Employer-wide payment display keeps its existing rule; role discovery must start from originals.
  assert.deepEqual(withoutCompiledRepeats(rows, roleSources, undefined, { layout: EMPLOYER_LAYOUT, nameKey: disclosedNameKey }), [official])
  const found = titleRecords(rows, analyst, roleSources)
  assert.deepEqual(found, [compiled])
  assert.equal(found[0], compiled, 'the compiled source row is retained, not rewritten as an official title')
  assert.equal(official[1], null)
  assert.equal(found[0][5], 'compiled')
})

test('a role suppresses the compiled copy when both sources disclose the same title and payment', () => {
  const official = employerRow('Greene, Alexis', 'Senior Policy Analyst', 'official')
  const compiled = employerRow('GREENE, ALEXIS', 'SENIOR POLICY ANALYST', 'compiled')
  const found = titleRecords([compiled, official], analyst, roleSources)
  assert.deepEqual(found, [official])
  assert.equal(found[0], official)
})

test('role filtering does not borrow a different official title or join different people with equal pay', () => {
  const officialOtherTitle = employerRow('Greene, Alexis', 'Manager', 'official')
  const compiled = employerRow('Greene, Alexis', 'Senior Policy Analyst', 'compiled')
  assert.deepEqual(titleRecords([officialOtherTitle, compiled], analyst, roleSources), [compiled])
  assert.deepEqual(titleRecords([officialOtherTitle, compiled], 'manager', roleSources), [officialOtherTitle])
  const officialOtherPerson = employerRow('Smith, Blake', 'Senior Policy Analyst', 'official')
  assert.deepEqual(titleRecords([officialOtherPerson, compiled], analyst, roleSources), [officialOtherPerson, compiled])
  assert.deepEqual(titleRecords([officialOtherPerson, compiled], 'nurse', roleSources), [])
})

test('role deduplication accepts existing reviewed name joins without creating its own', () => {
  const official = employerRow('Greene, Alexis', 'Senior Policy Analyst', 'official')
  const compiled = employerRow('Greene, A', 'Senior Policy Analyst', 'compiled')
  assert.deepEqual(titleRecords([official, compiled], analyst, roleSources), [official, compiled])
  const joins = new Map([[personKey('Greene, A'), personKey('Greene, Alexis')]])
  const nameKey = (row) => joins.get(disclosedNameKey(row)) ?? disclosedNameKey(row)
  assert.deepEqual(titleRecords([official, compiled], analyst, roleSources, { nameKey }), [official])
})

test('role discovery preserves stricter existing payment agreement for title variants and conflicting expenses', () => {
  const official = employerRow('Greene, Alexis', 'Senior Policy Analyst', 'official')
  const abbreviated = employerRow('Greene, Alexis', 'Sr. Policy Analyst · Policy', 'compiled')
  assert.equal(titleKey(abbreviated[1]), analyst)
  assert.deepEqual(titleRecords([official, abbreviated], analyst, roleSources), [official, abbreviated])
  const conflictingExpenses = employerRow('Greene, Alexis', 'Senior Policy Analyst', 'compiled', 9999)
  assert.deepEqual(titleRecords([official, conflictingExpenses], analyst, roleSources), [official, conflictingExpenses])
})

test('titles published in capitals are shown in ordinary capitals; mixed case is left as published', async () => {
  const { displayTitle } = await import('./positions.js')
  assert.equal(displayTitle('TEACHER'), 'Teacher')
  assert.equal(displayTitle('TRADES II - CARPENTER'), 'Trades II - Carpenter')
  assert.equal(displayTitle('DIRECTOR OF FINANCE'), 'Director of Finance')
  assert.equal(displayTitle('MANAGER, IT SERVICES'), 'Manager, IT Services')
  assert.equal(displayTitle('ART TEACHER'), 'Art Teacher')
  assert.equal(displayTitle('Professor - ESM'), 'Professor - ESM')
  assert.equal(displayTitle('SrBrdgSeis&StrucHlthMntrngEng'), 'SrBrdgSeis&StrucHlthMntrngEng')
})
