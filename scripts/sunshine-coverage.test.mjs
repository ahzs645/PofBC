import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { gzipSync } from 'node:zlib'
import { loadRepositoryCoverage, normalizeEmployerName, resolveEmployer } from './lib/sunshine-coverage.mjs'

function fixture(t, mutate = () => {}) {
  const root = mkdtempSync(join(tmpdir(), 'pofbc-sunshine-coverage-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  const years = [
    { label: '2023', slug: '2023', periodType: 'calendar' },
    { label: '2023/24', slug: '2023-24', periodType: 'fiscal' },
    { label: '2024', slug: '2024', periodType: 'calendar' }
  ]
  const index = { years, sources: {
    employees: { sourceKind: 'official-pdf', scope: 'employee-remuneration', periodType: 'calendar',
      periodStart: '2023-01-01', periodEnd: '2023-12-31', threshold: 75000, thresholdComparison: '>',
      url: 'https://example.com/employees.pdf', publicWarning: 'Subtotal is not published.', partialDisclosure: true },
    compiled: { sourceKind: 'compiled', scope: 'compiled-unverified', periodType: 'unverified' },
    council: { sourceKind: 'official-open-data', scope: 'elected-officials', periodType: 'calendar',
      periodStart: '2024-01-01', periodEnd: '2024-12-31', threshold: null }
  } }
  const rows = [
    ['A', 'Analyst', 100000.12, 100, 0, 'employees', 2],
    [null, null, 75000, null, 0, 'employees', 2],
    ['B', null, 95000, null, 1, 'compiled', null],
    ['C', 'Mayor', 50000, null, 2, 'council', null]
  ]
  const coverage = { output: { rows: 4, namedRows: 3, employers: 1, availableEmployerYears: 3, years: years.map(year => year.label) },
    officialRows: 3, legacyRowsRetained: 1, sourceCatalog: [], employers: [{ slug: 'city-of-example', names: ['City of Example'], sector: 'Municipalities', coverage: [
      { status: 'available', rows: 2, namedRows: 1, sourceIds: ['employees'], scope: 'employee-remuneration', periodType: 'calendar' },
      { status: 'available', rows: 1, namedRows: 1, sourceIds: ['compiled'], scope: 'compiled-unverified', periodType: 'unverified' },
      { status: 'available', rows: 1, namedRows: 1, sourceIds: ['council'], scope: 'elected-officials', periodType: 'calendar' }
    ] }] }
  mutate({ index, coverage, rows })
  mkdirSync(join(root, 'public/salaries/employers'), { recursive: true })
  writeFileSync(join(root, 'public/salaries/index.json'), JSON.stringify(index))
  writeFileSync(join(root, 'public/salaries/coverage.json'), JSON.stringify(coverage))
  writeFileSync(join(root, 'public/salaries/employers/city-of-example.json.gzip'), gzipSync(JSON.stringify(rows), { mtime: 0 }))
  return root
}

test('published exports retain scope, reporting basis, source thresholds and record counts', t => {
  const root = fixture(t)
  const data = loadRepositoryCoverage(root)
  assert.deepEqual(data.totals, { employers: 1, rows: 4, namedRows: 3, officialRows: 3, compiledRows: 1, employeeRows: 2, availableEmployerYears: 3 })
  const [employees, compiled, council] = data.employers[0].periods
  assert.equal(employees.employeeRows, 2)
  assert.equal(employees.cohorts[0].remunerationCents, 17500012)
  assert.equal(employees.cohorts[0].over75000Rows, 1)
  assert.equal(employees.cohorts[0].atLeast75000Rows, 2)
  assert.equal(employees.cohorts[0].atLeast100000Rows, 1)
  assert.equal(employees.cohorts[0].thresholdComparison, '>')
  assert.equal(employees.cohorts[0].partialDisclosure, true)
  assert.equal(employees.cohorts[0].publicWarning, 'Subtotal is not published.')
  assert.equal(employees.cohorts[0].periodEndYear, 2023)
  assert.equal(compiled.labelType, 'fiscal')
  assert.equal(compiled.periodType, 'unverified')
  assert.equal(compiled.cohorts[0].periodEndYear, null)
  assert.equal(compiled.cohorts[0].verifiedPeriod, false)
  assert.equal(compiled.officialRows, 0)
  assert.equal(council.employeeRows, 0)
  assert.equal(council.officialRows, 1)
  assert.equal(data.inputs.length, 3)
  assert.deepEqual(data, loadRepositoryCoverage(root))
})

for (const [label, mutate, expected] of [
  ['wrong employer count', ({ coverage }) => { coverage.employers[0].coverage[0].rows++ }, /export counts/],
  ['unknown source', ({ rows }) => { rows[0][5] = 'unregistered' }, /unknown source/],
  ['out of range year', ({ rows }) => { rows[0][4] = 99 }, /invalid row or year index/],
  ['noninteger year', ({ rows }) => { rows[0][4] = 0.5 }, /invalid row or year index/],
  ['unexpected source kind', ({ index }) => { index.sources.employees.sourceKind = 'unreviewed-upload' }, /unrecognized source kind/],
  ['source ID drift', ({ coverage }) => { coverage.employers[0].coverage[0].sourceIds = ['council'] }, /source IDs differ/],
  ['year label drift', ({ coverage }) => { coverage.output.years[0] = '2022' }, /year catalogs differ/],
  ['published total drift', ({ coverage }) => { coverage.output.rows++ }, /rows control mismatch/],
  ['published provenance drift', ({ coverage }) => { coverage.officialRows++ }, /official\/compiled source totals/],
  ['invalid remuneration', ({ rows }) => { rows[0][2] = '100000' }, /nonnumeric remuneration/],
  ['duplicate employer', ({ coverage }) => { coverage.employers.push(coverage.employers[0]) }, /duplicate employer slug/]
]) test(`rejects ${label} instead of producing misleading coverage`, t => {
  assert.throws(() => loadRepositoryCoverage(fixture(t, mutate)), expected)
})

test('explicit incomplete employee schedules remain partial even without a public warning', t => {
  for (const metadata of [
    { completeEmployeeSchedule: false },
    { validation: { completeEmployeeSchedule: false } },
    { completeEmployeeSchedule: true, validation: { completeEmployeeSchedule: false } }
  ]) {
    const root = fixture(t, ({ index }) => {
      delete index.sources.employees.partialDisclosure
      delete index.sources.employees.publicWarning
      Object.assign(index.sources.employees, metadata)
    })
    const cohort = loadRepositoryCoverage(root).employers[0].periods[0].cohorts[0]
    assert.equal(cohort.partialDisclosure, true)
    assert.equal(cohort.publicWarning, null)
    assert.equal(cohort.completeEmployeeSchedule, metadata.completeEmployeeSchedule ?? false)
  }
})

test('an explicitly complete schedule preserves its flag without manufacturing a partial disclosure', t => {
  const root = fixture(t, ({ index }) => {
    delete index.sources.employees.partialDisclosure
    index.sources.employees.completeEmployeeSchedule = true
    index.sources.employees.validation = { completeEmployeeSchedule: true }
  })
  const cohort = loadRepositoryCoverage(root).employers[0].periods[0].cohorts[0]
  assert.equal(cohort.partialDisclosure, false)
  assert.equal(cohort.completeEmployeeSchedule, true)
})

const employers = [
  { slug: 'city-of-langley', names: ['City of Langley', 'Langley City'] },
  { slug: 'langley-township', names: ['Township of Langley'] },
  { slug: 'city-of-north-vancouver', names: ['City of North Vancouver'] },
  { slug: 'district-of-north-vancouver', names: ['District of North Vancouver'] },
  { slug: 'bc-hydro', names: ['B.C. Hydro'] },
  { slug: 'public-service', names: ['Provincial government'] },
  { slug: 'abbotsford-school-district', names: ['Abbotsford School Board'] }
]

test('punctuation normalization and reviewed repository aliases resolve identities', () => {
  assert.equal(normalizeEmployerName('B.C. Hydro'), normalizeEmployerName('British Columbia Hydro'))
  assert.equal(normalizeEmployerName('B.C Hydro'), normalizeEmployerName('BC Hydro'))
  assert.equal(resolveEmployer('BC Hydro', { employers }).slug, 'bc-hydro')
  assert.equal(resolveEmployer('Abbotsford school district', { employers }).slug, 'abbotsford-school-district')
  assert.equal(resolveEmployer('Township of Langley', { employers }).slug, 'langley-township')
  assert.equal(resolveEmployer('City of North Vancouver', { employers }).slug, 'city-of-north-vancouver')
})

test('municipal prefixes remain distinct and approximate similarity is never accepted', () => {
  assert.notEqual(normalizeEmployerName('City of North Vancouver'), normalizeEmployerName('District of North Vancouver'))
  assert.equal(resolveEmployer('Langley', { employers }).status, 'unmatched')
  assert.equal(resolveEmployer('North Vancouver', { employers }).status, 'unmatched')
  assert.equal(resolveEmployer('City of Langlee', { employers }).status, 'unmatched')
  assert.equal(resolveEmployer('BC Hydro (separate subsidiary)', { employers }).status, 'unmatched')
})

test('a name collision remains ambiguous even when one canonical slug matches', () => {
  const duplicate = [...employers, { slug: 'different-entity', names: ['B.C. Hydro'] }]
  const result = resolveEmployer('BC Hydro', { employers: duplicate })
  assert.equal(result.status, 'ambiguous')
  assert.equal(result.slug, null)
  assert.deepEqual(result.candidates, ['bc-hydro', 'different-entity'])
})

test('explicit reviewed aliases are traceable and unknown targets fail', () => {
  const result = resolveEmployer({ name: 'Core Government' }, { employers, aliases: { 'Core Government': { slug: 'public-service', reason: 'Same BC public service employer.' } } })
  assert.equal(result.method, 'reviewed-alias')
  assert.equal(result.slug, 'public-service')
  assert.match(result.reason, /BC public service/)
  assert.equal(resolveEmployer('Core Government', { employers, aliases: [{ externalName: 'Core Government', repositorySlug: 'public-service', reason: 'Reviewed.' }] }).slug, 'public-service')
  assert.throws(() => resolveEmployer('Core Government', { employers, aliases: { 'Core Government': 'missing-employer' } }), /unknown employer/)
})
