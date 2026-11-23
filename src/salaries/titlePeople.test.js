import { test } from 'node:test'
import assert from 'node:assert/strict'
import { personKey } from './people.js'
import { AUTO_EMPLOYERS, cellEmployers, employerTotals, loadsUnasked, matchesPerson, PEOPLE_ORDER, scopedCells, titlePeople } from './titlePeople.js'

const health = { slug: 'health', names: ['Old Health', 'Health Authority'], sector: 'Health' }
const school = { slug: 'school', names: ['School District'], sector: 'Education' }
const cell = (entry, year, count, mean, low, high) => ({ entry, name: entry.names.at(-1), year, count, mean, median: mean, low, high })

const cells = [
  cell(health, 3, 2, 100000, 90000, 110000),
  cell(health, 4, 1, 120000, 120000, 120000),
  cell(school, 4, 5, 80000, 70000, 95000)
]

test('the people of a few employers are read unasked, and of many only when asked', () => {
  assert.equal(loadsUnasked(1), true)
  assert.equal(loadsUnasked(AUTO_EMPLOYERS), true)
  assert.equal(loadsUnasked(AUTO_EMPLOYERS + 1), false)
})

test('a title’s cells narrow to a sector and a year, or keep every year', () => {
  assert.equal(scopedCells(cells).length, 3)
  assert.equal(scopedCells(cells, 'all', 4).length, 2)
  assert.deepEqual(scopedCells(cells, 'Health').map((each) => each.year), [3, 4])
  assert.deepEqual(scopedCells(cells, 'Health', 3).map((each) => each.count), [2])
  assert.deepEqual(cellEmployers(cells), ['school', 'health'])
  assert.deepEqual(cellEmployers(scopedCells(cells, 'all', 3)), ['health'])
})

test('each employer over every year: its records, range, weighted average and latest year', () => {
  const [first, second] = employerTotals(cells)
  assert.equal(first.slug, 'health')
  assert.equal(first.name, 'Health Authority')
  assert.equal(first.count, 3)
  assert.equal(first.low, 90000)
  assert.equal(first.high, 120000)
  assert.equal(first.mean, Math.round((2 * 100000 + 120000) / 3))
  assert.equal(first.first, 3)
  assert.equal(first.latest, 4)
  assert.equal(first.year, 4)
  assert.equal(first.periods, 2)
  assert.equal(first.median, null)
  assert.equal(second.count, 5)
  assert.equal(second.periods, 1)
})

test('the people under a title at each employer, a name at two employers kept as two rows', () => {
  const sources = { official: { url: 'https://example.org/a.pdf', sha256: 'x' }, compiled: { sourceKind: 'compiled' } }
  const files = [
    {
      entry: health,
      nameKeys: null,
      rows: [
        ['Smith, Jane', 'Director, Clinical Informatics', 120000, 1000, 4, 'official', 7],
        ['Smith, Jane', 'DIRECTOR CLINICAL INFORMATICS', 120000, 1000, 4, 'compiled', null],
        ['Doe, John', 'Director Clinical Informatics', 100000, null, 3, 'official', null],
        ['Roe, Ann', 'Nurse', 90000, null, 4, 'official', null],
        ['Low, Bo', 'Director Clinical Informatics', 99000, null, 4, 'usd', null]
      ]
    },
    { entry: school, nameKeys: null, rows: [['Smith, Jane', 'Directors, Clinical Informatics', 80000, null, 4, 'official', null], [null, 'Director Clinical Informatics', 75000, null, 4, 'official', null]] }
  ]
  const keep = (row) => row[5] !== 'usd'
  const every = titlePeople(files, 'director clinical informatic', { sources, keep })
  // The compiled copy of Jane Smith's official record is folded; the other currency is set aside.
  assert.equal(every.people.length, 4)
  assert.equal(every.setAside, 1)
  assert.deepEqual(every.people.filter((person) => person.name === 'Smith, Jane').map((person) => person.slug), ['health', 'school'])
  const jane = every.people[0]
  assert.equal(jane.employer, 'Health Authority')
  assert.equal(jane.sector, 'Health')
  assert.equal(jane.page, 7)
  assert.equal(every.people.find((person) => person.slug === 'school' && !person.name).pay, 75000)

  const inYear = titlePeople(files, 'director clinical informatic', { sources, keep, year: 3 })
  assert.deepEqual(inYear.people.map((person) => person.name), ['Doe, John'])
  assert.equal(inYear.setAside, 0)
})

test('reviewed name joins at an employer decide which compiled copies fold', () => {
  const sources = { official: { url: 'https://example.org/a.pdf', sha256: 'x' }, compiled: { sourceKind: 'compiled' } }
  const rows = [['Garant, Daniel', 'Clerk', 50000, null, 1, 'official', null], ['Garant, D.', 'Clerk', 50000, null, 1, 'compiled', null]]
  assert.equal(titlePeople([{ entry: school, rows, nameKeys: null }], 'clerk', { sources }).people.length, 2)
  const nameKeys = new Map([[personKey('Garant, D.'), personKey('Garant, Daniel')]])
  const { people } = titlePeople([{ entry: school, rows, nameKeys }], 'clerk', { sources })
  assert.equal(people.length, 1)
  assert.equal(people[0].name, 'Garant, Daniel')
})

test('people are found by name, employer or position, and ordered by pay, year or name', () => {
  const people = [
    { name: 'Smith, Jane', employer: 'Health Authority', position: 'Director', pay: 100, year: 4 },
    { name: 'Émile, Zoé', employer: 'School District', position: 'Director', pay: 200, year: 3 },
    { name: null, employer: 'School District', position: 'Director', pay: 150, year: 4 }
  ]
  assert.equal(matchesPerson(people[0], 'jane health'), true)
  assert.equal(matchesPerson(people[1], 'emile school'), true)
  assert.equal(matchesPerson(people[0], 'school'), false)
  assert.equal(matchesPerson(people[2], ''), true)
  assert.deepEqual([...people].sort(PEOPLE_ORDER.pay).map((person) => person.pay), [200, 150, 100])
  assert.deepEqual([...people].sort(PEOPLE_ORDER.recent).map((person) => person.pay), [150, 100, 200])
  assert.deepEqual([...people].sort(PEOPLE_ORDER.name).map((person) => person.name), ['Émile, Zoé', 'Smith, Jane', null])
})
