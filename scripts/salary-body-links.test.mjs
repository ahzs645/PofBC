import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { gzipSync, gunzipSync } from 'node:zlib'
import { bodyOfEmployer, employerSlug, REVIEWED_BODY_LINKS } from './lib/salary-employers.mjs'
import { governmentSalaryPeriods } from './lib/salary-government.mjs'
import { relinkSalaryBodies } from './relink-salary-bodies.mjs'
import { SALARY_COVERAGE, SALARY_INDEX, SALARY_EMPLOYERS } from '../src/government/salaryIndex.js'
import { salaryEmployerOf, salaryKeyOf } from '../src/government/salaries.js'
import { HISTORICAL_BODIES } from '../src/government/historyData.js'
import { CURRENT_BODIES } from '../src/government/currentData.js'

const root = new URL('../', import.meta.url)
const read = (path) => JSON.parse(readFileSync(new URL(path, root), 'utf8'))
const index = read('public/salaries/employers/index.json')

test('reviewed government links preserve the existing disclosure employer IDs', () => {
  assert.equal(employerSlug('Justice Institute of British Columbia'), 'justice-institute-of-bc')
  assert.equal(employerSlug('British Columbia Railway Company'), 'bc-railway-company')
  assert.equal(employerSlug('BC Family Maintenance Agency'), 'bc-family-maintenance-agency')
  const known = new Set([...HISTORICAL_BODIES, ...CURRENT_BODIES].map((body) => body.id))
  for (const [slug, body] of Object.entries(REVIEWED_BODY_LINKS)) {
    assert.ok(known.has(body), body)
    assert.equal(bodyOfEmployer(slug), body)
    assert.equal(salaryKeyOf({ id: body }), body)
    assert.equal(SALARY_EMPLOYERS[body], slug)
    assert.equal(salaryEmployerOf(body), slug)
  }
  assert.equal(salaryEmployerOf('public-service'), 'public-service')
})

test('government routes retain every accepted row, period, source and disclosure qualification', () => {
  for (const [slug, body] of Object.entries(REVIEWED_BODY_LINKS)) {
    const employer = index.employers.find((entry) => entry.slug === slug)
    assert.equal(employer.body, body)
    assert.deepEqual(SALARY_COVERAGE[body], employer.coverage)
    const rows = JSON.parse(gunzipSync(readFileSync(new URL(`public/salaries/employers/${slug}.json.gzip`, root))))
    let records = 0
    for (const [at, year] of index.years.entries()) {
      const expected = rows.filter((row) => row[4] === at).map((row) => [...row.slice(0, 4), row[5], row[6]])
      if (!expected.length) continue
      const period = year.replace('/', '-')
      const data = read(`public/salaries/${period}/${body}.json`)
      assert.deepEqual(data.rows, expected, `${slug} ${year}: all amounts and source fields`)
      assert.equal(SALARY_INDEX[body][period].count, expected.length)
      assert.equal(data.scope, employer.coverage[at].scope)
      assert.deepEqual(data.sourceIds, employer.coverage[at].sourceIds)
      records += data.rows.length
    }
    assert.equal(records, rows.length)
  }
  assert.ok(Object.values(SALARY_INDEX['bc-family-maintenance-agency']).every((period) => period.scope === 'board-remuneration'))
  assert.ok(Object.values(SALARY_INDEX['justice-institute']).every((period) => period.scope === 'compiled-unverified'))
})

test('the shared government projection preserves currencies and cents without ranking foreign payments as CAD', () => {
  const periods = governmentSalaryPeriods({
    info: { slug: 'fixture-employer', body: 'fixture-body', names: ['Fixture'] },
    exported: [['CAD, A', null, 100.01, null, 0, 'cad', 1], ['USD, B', null, 900, 0, 0, 'usd', 2]],
    years: [{ label: '2024/25', slug: '2024-25' }],
    coverage: [{ sourceIds: ['cad', 'usd'], scope: 'mixed-disclosure', notes: ['Retained source scopes.'], duplicateRows: 0 }],
    sources: { cad: { currency: 'CAD' }, usd: { currency: 'USD' } }
  })
  assert.equal(periods[0].totals.total, 100.01)
  assert.equal(periods[0].totals.nonCadRecords, 1)
  assert.equal(periods[0].totals.count, 2)
  assert.deepEqual(periods[0].data.rows[1], ['USD, B', null, 900, 0, 'usd', 2])
})

const fixture = () => {
  const dir = mkdtempSync(join(tmpdir(), 'salary-body-links-'))
  const write = (path, data) => { mkdirSync(join(dir, path, '..'), { recursive: true }); writeFileSync(join(dir, path), JSON.stringify(data) + '\n') }
  const years = ['2024/25']
  const sources = { fixture: { scope: 'board-remuneration', sourceKind: 'official', currency: 'CAD' } }
  const employers = Object.keys(REVIEWED_BODY_LINKS).map((slug) => ({ slug, body: null, names: [slug], counts: [1], coverage: [{ rows: 1, sourceIds: ['fixture'], scope: 'board-remuneration', notes: ['Board payments only.'], duplicateRows: 0 }] }))
  write('employers/index.json', { years, sources, employers })
  for (const { slug } of employers) writeFileSync(join(dir, `employers/${slug}.json.gzip`), gzipSync(JSON.stringify([['Name, A', null, 123.45, null, 0, 'fixture', 2]])))
  write('people/index.json', { years, sources, employers: employers.map((entry) => [entry.names[0], 'Crown corporations', null, entry.slug]) })
  write('index.json', { years: [{ label: years[0], slug: '2024-25' }], sources, bodies: {}, coverage: {}, unmatched: Object.fromEntries(employers.map((entry) => [entry.slug, 1])) })
  write('coverage.json', { output: { rows: 3, atlasBodies: 0 } })
  return { dir, options: { salaries: dir, indexPath: join(dir, 'salaryIndex.js') }, write }
}

test('bounded rebuild is repeatable and fails before writes if accepted counts no longer agree', () => {
  const { dir, options, write } = fixture()
  try {
    const first = relinkSalaryBodies(options)
    assert.equal(first.atlasBodies, 3)
    assert.equal(relinkSalaryBodies({ ...options, check: true }).files, first.files)
    const before = readFileSync(join(dir, 'employers/index.json'))
    const broken = JSON.parse(readFileSync(join(dir, 'index.json')))
    broken.unmatched['bc-railway-company'] = 999
    write('index.json', broken)
    assert.throws(() => relinkSalaryBodies(options), /unmatched count changed/)
    assert.deepEqual(readFileSync(join(dir, 'employers/index.json')), before)
  } finally { rmSync(dir, { recursive: true, force: true }) }
})
