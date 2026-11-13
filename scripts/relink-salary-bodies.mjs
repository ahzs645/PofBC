// Rebuild government links from accepted employer exports without rerunning salary acquisition.
// The three reviewed mappings are also applied by build-salaries.mjs. No employer rows, source
// decisions, name links, periods or disclosure scopes are modified by this bounded projection.
import assert from 'node:assert/strict'
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gunzipSync } from 'node:zlib'
import { REVIEWED_BODY_LINKS } from './lib/salary-employers.mjs'
import { governmentSalaryPeriods, salaryIndexModule } from './lib/salary-government.mjs'
import { sha256 } from './lib/salary-data.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

export const relinkSalaryBodies = ({
  salaries = join(root, 'public/salaries'),
  indexPath = join(root, 'src/government/salaryIndex.js'),
  check = false
} = {}) => {
  const read = (path) => JSON.parse(readFileSync(join(salaries, path), 'utf8'))
  const employers = read('employers/index.json')
  const people = read('people/index.json')
  const index = read('index.json')
  const audit = read('coverage.json')
  assert.deepEqual(employers.years, index.years.map((year) => year.label), 'Salary indexes use different periods')
  assert.deepEqual(people.years, employers.years, 'People index uses different periods')
  assert.deepEqual(index.sources, employers.sources, 'Salary indexes use different sources')
  assert.deepEqual(people.sources, employers.sources, 'People index uses different sources')

  const pending = new Map()
  const summaries = []
  const json = (path, value) => pending.set(join(salaries, path), JSON.stringify(value) + '\n')
  for (const [slug, body] of Object.entries(REVIEWED_BODY_LINKS)) {
    const info = employers.employers.find((employer) => employer.slug === slug)
    assert.ok(info, `Missing accepted employer ${slug}`)
    assert.ok(!info.body || info.body === body, `Conflicting existing body link for ${slug}`)
    assert.ok(!employers.employers.some((employer) => employer.slug !== slug && employer.body === body), `Body ${body} already belongs to another employer`)
    const bytes = readFileSync(join(salaries, `employers/${slug}.json.gzip`))
    const exported = JSON.parse(gunzipSync(bytes).toString('utf8'))
    assert.ok(Array.isArray(exported), `Invalid accepted records for ${slug}`)
    assert.equal(exported.length, info.counts.reduce((sum, count) => sum + count, 0), `${slug}: count changed`)
    for (const row of exported) {
      assert.ok(Array.isArray(row) && row.length === 7 && Number.isFinite(row[2]), `${slug}: invalid accepted row`)
      assert.ok(Number.isInteger(row[4]) && index.years[row[4]] && employers.sources[row[5]], `${slug}: unresolved period or source`)
    }
    for (const [at, coverage] of info.coverage.entries()) {
      const rows = exported.filter((row) => row[4] === at)
      assert.equal(rows.length, coverage.rows, `${slug}: coverage changed in ${employers.years[at]}`)
      assert.equal(rows.length, info.counts[at], `${slug}: indexed count changed in ${employers.years[at]}`)
      if (rows.length) assert.deepEqual([...new Set(rows.map((row) => row[5]))].sort(), [...coverage.sourceIds].sort(), `${slug}: coverage sources changed`)
    }
    if (index.unmatched[slug] != null) assert.equal(index.unmatched[slug], exported.length, `${slug}: unmatched count changed`)
    info.body = body
    const peopleEmployer = people.employers.find((employer) => employer[3] === slug)
    assert.ok(peopleEmployer, `${slug}: missing people-index employer`)
    assert.ok(!peopleEmployer[2] || peopleEmployer[2] === body, `${slug}: conflicting people-index body`)
    peopleEmployer[2] = body
    const periods = governmentSalaryPeriods({ info, exported, coverage: info.coverage, years: index.years, sources: employers.sources })
    index.bodies[body] = Object.fromEntries(periods.map((period) => [period.slug, period.totals]))
    index.coverage[body] = info.coverage
    delete index.unmatched[slug]
    for (const period of periods) json(`${period.slug}/${body}.json`, period.data)
    summaries.push({ employer: slug, body, rows: exported.length, periods: periods.length, employerRowsSha256: sha256(bytes) })
  }
  index.employers = Object.fromEntries(employers.employers.filter((employer) => employer.body).map((employer) => [employer.body, employer.slug]))
  audit.output.atlasBodies = Object.keys(index.bodies).length
  json('employers/index.json', employers)
  json('people/index.json', people)
  json('index.json', index)
  json('coverage.json', audit)
  pending.set(indexPath, salaryIndexModule(index))

  // All inputs and proposed outputs are resolved before any file is replaced.
  for (const [path, content] of pending) {
    if (check) {
      assert.ok(existsSync(path), `Missing derived file: ${path}`)
      assert.equal(readFileSync(path, 'utf8'), content, `Stale body-link projection: ${path}`)
    } else {
      mkdirSync(dirname(path), { recursive: true })
      writeFileSync(`${path}.relink-tmp`, content)
    }
  }
  if (!check) for (const path of pending.keys()) renameSync(`${path}.relink-tmp`, path)
  for (const summary of summaries) {
    assert.equal(sha256(readFileSync(join(salaries, `employers/${summary.employer}.json.gzip`))), summary.employerRowsSha256, 'Accepted employer records changed')
  }
  return { check, atlasBodies: audit.output.atlasBodies, files: pending.size, employers: summaries }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(JSON.stringify(relinkSalaryBodies({ check: process.argv.includes('--check') }), null, 2))
}
