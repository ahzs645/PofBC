import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { keyedTitles, meanMoney, relatedTitles, titleKey, titleLabel, titleMatcher, titleShard } from './positions.js'

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
