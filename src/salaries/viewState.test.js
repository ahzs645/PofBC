import { test } from 'node:test'
import assert from 'node:assert/strict'
import { filterPositionGroups, hasExpenseAmount, matchesRecordQuery, readSalaryPlace, salaryPlaceUrl, salaryYearIndex } from './viewState.js'

test('shared salary filters and employer year survive reload and catalog expansion', () => {
  const place = { q: 'Smith, J', person: 'smith|j', personAt: 'city-of-vancouver', employer: 'northern-health', role: 'nurse', title: null, show: 'positions', browse: 'people', layout: 'table', year: '2020/21', sector: 'Health authorities', employerYear: '2023/24' }
  const url = salaryPlaceUrl('https://example.org/PofBC/?view=salaries&year=1950', place)
  assert.deepEqual(readSalaryPlace(url.search), place)
  assert.equal(url.searchParams.get('year'), '1950')
  assert.equal(salaryYearIndex(place.year, ['2020/21', '2023/24']), '0')
  assert.equal(salaryYearIndex(place.year, ['2019/20', '2020/21', '2023/24']), '1')
  assert.equal(salaryYearIndex('2099/00', ['2020/21']), 'all')
  assert.equal(salaryPlaceUrl(url.href, { ...place, employer: null }).searchParams.has('employer-year'), false)
  assert.equal(salaryPlaceUrl(url.href, { ...place, employer: null, title: 'nurse' }).searchParams.get('employer-year'), '2023/24')
})

test('a name search returns matching people within a position group', () => {
  const jane = ['Smith, Jane', 'Registered Nurse', 88000, 0]
  const mark = ['Jones, Mark', 'Registered Nurse', 96000, null]
  const groups = [{ label: 'Registered Nurse', rows: [jane, mark] }]
  const result = filterPositionGroups(groups, 'Jane Smith')
  assert.equal(result.length, 1)
  assert.deepEqual(result[0].rows, [jane])
  assert.equal(result[0].totalRows, 2)
  assert.deepEqual(filterPositionGroups(groups, 'registered nurse')[0].rows, [jane, mark])
  assert.deepEqual(filterPositionGroups(groups, 'no such name'), [])
  assert.ok(matchesRecordQuery(['Tremblay, Émilie', 'Nurse'], 'emilie'))
})

test('zero expenses and negative recoveries remain reported values', () => {
  assert.equal(hasExpenseAmount(0), true)
  assert.equal(hasExpenseAmount(-12.5), true)
  assert.equal(hasExpenseAmount(null), false)
  assert.equal(hasExpenseAmount(undefined), false)
})

test('a period filter is one period or a range, and survives the catalog growing', async () => {
  const { salaryYearRange, salaryYearValue } = await import('./viewState.js')
  const years = ['2018', '2018/19', '2019', '2019/20', '2020/21']
  assert.deepEqual(salaryYearRange('2018/19..2020/21', years), [1, 4])
  assert.deepEqual(salaryYearRange('2020/21..2018/19', years), [1, 4])
  assert.deepEqual(salaryYearRange('2019/20', years), [3, 3])
  assert.equal(salaryYearRange('all', years), null)
  assert.equal(salaryYearRange('1999/00..2019/20', years), null)
  assert.equal(salaryYearValue([1, 4], years), '2018/19..2020/21')
  assert.equal(salaryYearValue([3, 3], years), '2019/20')
  assert.equal(salaryYearValue(null, years), 'all')
})
