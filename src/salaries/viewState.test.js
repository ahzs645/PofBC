import { test } from 'node:test'
import assert from 'node:assert/strict'
import { filterPositionGroups, hasExpenseAmount, matchesRecordQuery, personEmployerForBack, readSalaryPlace, salaryPlaceUrl, salaryYearIndex } from './viewState.js'

test('shared salary filters and employer year survive reload and catalog expansion', () => {
  const place = { q: 'Smith, J', person: 'smith|j', personAt: 'city-of-vancouver', employer: 'northern-health', role: 'nurse', title: null, show: 'positions', browse: 'people', layout: 'table', year: '2020/21', sector: 'Health authorities', employerYear: '2023/24' }
  const url = salaryPlaceUrl('https://example.org/PofBC/?view=salaries&year=1950', place)
  assert.deepEqual(readSalaryPlace(url.search), place)
  assert.equal(url.searchParams.get('year'), '1950')
  assert.equal(salaryYearIndex(place.year, ['2020/21', '2023/24']), '0')
  assert.equal(salaryYearIndex(place.year, ['2019/20', '2020/21', '2023/24']), '1')
  assert.equal(salaryYearIndex('2099/00', ['2020/21']), 'all')
  assert.equal(salaryPlaceUrl(url.href, { ...place, employer: null }).searchParams.get('employer-year'), '2023/24')
  assert.equal(salaryPlaceUrl(url.href, { ...place, employer: null, personAt: null }).searchParams.has('employer-year'), false)
  assert.equal(salaryPlaceUrl(url.href, { ...place, employer: null, title: 'nurse' }).searchParams.get('employer-year'), '2023/24')
})

test('shared person Back retains the originating employer, with a unique-employer fallback for old links', () => {
  const employers = [['Company A', 'Sector', null, 'company-a'], ['Company B', 'Sector', null, 'company-b']]
  const row = (at) => ['Smith, Jane', 'Nurse', 88000, 0, at]
  assert.equal(personEmployerForBack(null, [row(0), row(0)], employers), 'company-a')
  assert.equal(personEmployerForBack('company-b', [row(0), row(1)], employers), 'company-b')
  assert.equal(personEmployerForBack(null, [row(0), row(1)], employers), null)
  assert.equal(personEmployerForBack('missing-employer', [row(0), row(1)], employers), null)
  assert.equal(personEmployerForBack('missing-employer', [row(0)], employers), 'company-a')
  assert.equal(personEmployerForBack(null, [], employers), null)

  const place = readSalaryPlace('?view=salaries&person=smith%7Cjane&person-at=company-b&employer-year=2020%2F21')
  const shared = salaryPlaceUrl('https://example.org/PofBC/?view=salaries', place)
  assert.equal(readSalaryPlace(shared.search).personAt, 'company-b')
  assert.equal(readSalaryPlace(shared.search).employerYear, '2020/21')
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

test('council filters round-trip independently of salary year, sector and the site timeline', () => {
  const place = readSalaryPlace('?view=salaries&browse=council&council-tab=payments&council-municipality=Vancouver&council-year=1994&council-role=Councillor&q=Hemer&salary-year=2020%2F21&salary-sector=Municipalities')
  const url = salaryPlaceUrl('https://example.org/PofBC/?view=salaries&year=1950', place)
  assert.deepEqual(readSalaryPlace(url.search), place)
  assert.equal(place.councilTab, 'payments')
  assert.equal(place.councilYear, '1994')
  assert.equal(place.year, '2020/21')
  assert.equal(url.searchParams.get('year'), '1950')
  assert.equal(url.searchParams.get('salary-sector'), 'Municipalities')
})

test('leaving the council view removes its parameters and retains the regular salary filters', () => {
  const href = 'https://example.org/PofBC/?view=salaries&browse=council&council-tab=payments&council-year=1996&council-role=Mayor&council-municipality=Saanich&salary-year=2021'
  const place = { ...readSalaryPlace(new URL(href).search), browse: 'employers' }
  const url = salaryPlaceUrl(href, place)
  assert.equal([...url.searchParams.keys()].some((key) => key.startsWith('council-')), false)
  assert.equal(readSalaryPlace(url.search).year, '2021')
  assert.equal('councilYear' in readSalaryPlace(url.search), false)
})

test('a bare council link defaults to office observations without borrowing a salary year', () => {
  const place = readSalaryPlace('?view=salaries&browse=council&salary-year=2020%2F21')
  assert.equal(place.councilTab, 'rates')
  assert.equal(place.councilYear, 'all')
  assert.equal(place.councilMunicipality, 'all')
  assert.equal(place.councilRole, 'all')
  const url = salaryPlaceUrl('https://example.org/PofBC/', place)
  assert.equal(url.searchParams.has('council-tab'), false)
  assert.equal(url.searchParams.has('council-year'), false)
})

test('workforce population is independent of named salary filters and cleared on exit', () => {
  const href = 'https://example.org/PofBC/?view=salaries&browse=workforce&workforce-population=victoria&salary-year=2023%2F24&salary-sector=Government'
  const place = readSalaryPlace(new URL(href).search)
  assert.equal(place.workforcePopulation, 'victoria')
  assert.equal(place.year, '2023/24')
  assert.deepEqual(readSalaryPlace(salaryPlaceUrl(href, place).search), place)
  const next = salaryPlaceUrl(href, { ...place, browse: 'employers' })
  assert.equal(next.searchParams.has('workforce-population'), false)
  assert.equal(readSalaryPlace(next.search).year, '2023/24')
  assert.equal('workforcePopulation' in readSalaryPlace(next.search), false)
  const council = salaryPlaceUrl(href, { ...place, browse: 'council' })
  assert.equal(council.searchParams.has('workforce-population'), false)
})

test('a shared workforce link does not borrow a council filter', () => {
  const href = 'https://example.org/PofBC/?view=salaries&browse=workforce&council-year=2021&council-tab=payments'
  const place = readSalaryPlace(new URL(href).search)
  assert.equal(place.workforcePopulation, 'all')
  assert.equal('councilYear' in place, false)
  const url = salaryPlaceUrl(href, place)
  assert.equal(url.searchParams.has('council-year'), false)
  assert.equal(url.searchParams.has('council-tab'), false)
  assert.equal(url.searchParams.has('workforce-population'), false)
})
