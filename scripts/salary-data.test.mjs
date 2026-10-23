import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { gzipSync, gunzipSync } from 'node:zlib'
import { spawnSync } from 'node:child_process'
import { csvRows, money, sumMoney, median, duplicateStats, repeatedCandidates, sha256 } from './lib/salary-data.mjs'

const row = (name, pay = 100000.01, year = '2017/18') => ({ slug: 'bc-hydro', year, name, position: null, pay, expenses: null })
test('money retains cents, distinguishes missing from zero, and permits published recoveries', () => {
  assert.equal(money('$100,000.01'), 100000.01)
  assert.equal(money('0'), 0)
  assert.equal(money('NA'), null)
  assert.equal(money(''), null)
  assert.equal(money('-5,110'), -5110)
  assert.throws(() => money('100000x'), /Invalid money/)
  assert.equal(sumMoney([0.1, 0.2]), 0.3)
  assert.equal(median([1.01, 1.02]), 1.02)
})
test('CSV rejects truncated quoted rows and keeps embedded delimiters', () => {
  assert.deepEqual([...csvRows('Name,Amount\r\n"Smith, A",100\n"line\nname",200')], [['Name', 'Amount'], ['Smith, A', '100'], ['line\nname', '200']])
  assert.throws(() => [...csvRows('Name\n"unterminated')], /Unclosed/)
})
test('repetition compares earlier populated years but remains review-only', () => {
  const old = Array.from({ length: 25 }, (_, at) => row(`Surname${at}, A`))
  const next = old.map((entry) => ({ ...entry, year: '2023/24' }))
  const result = repeatedCandidates([...old, ...next])
  assert.equal(result.length, 1)
  assert.equal(result[0].repeats, '2017/18')
  assert.equal(result[0].action, 'review-only')
  assert.equal(result[0].same, 25)
  assert.equal(next.length, 25)
})
test('repetition respects multiplicity and does not use anonymous rows as identity matches', () => {
  const old = Array.from({ length: 25 }, (_, at) => row(`Surname${at}, A`))
  const repeatsOneName = Array.from({ length: 25 }, () => row('Surname0, A', 100000.01, '2020/21'))
  assert.deepEqual(repeatedCandidates([...old, ...repeatsOneName]), [])
  assert.deepEqual(repeatedCandidates(Array.from({ length: 50 }, (_, at) => row(null, 100000, at < 25 ? '2017/18' : '2020/21'))), [])
  assert.deepEqual(repeatedCandidates([...old, ...old.map((entry) => ({ ...entry, pay: entry.pay + 0.01, year: '2020/21' }))]), [])
})
test('duplicate-looking rows are counted without deleting possible distinct people', () => {
  const rows = [row('Lee, A'), row('Lee, A'), row('Lee, B')]
  assert.deepEqual(duplicateStats(rows), { duplicateRows: 1, duplicateGroups: 1 })
  assert.equal(rows.length, 3)
})

const fixture = () => {
  const dir = mkdtempSync(join(tmpdir(), 'pofbc-salary-test-'))
  const research = join(dir, 'research'); mkdirSync(research)
  const baseline = { provenance: { description: 'Fixture compiled input' }, years: ['2017/18', '2020/21', '2023/24'],
    repeated: [{ employer: 'bc-hydro', year: '2020/21', repeats: '2017/18', rows: 20, same: 20 }],
    employers: [{ slug: 'bc-hydro', names: ['BC Hydro'], sector: 'Crown corporations', body: 'bc-hydro', counts: [1, 0, 0], rows: [['Old, A', null, 90000, null, 0]] }] }
  const bytes = gzipSync(JSON.stringify(baseline))
  writeFileSync(join(research, 'baseline.json.gzip'), bytes)
  writeFileSync(join(research, 'baseline-manifest.json'), JSON.stringify({ file: 'baseline.json.gzip', sha256: sha256(bytes), repositoryCommit: 'fixture' }))
  const sourceDir = join(research, 'official'); mkdirSync(sourceDir)
  const data = gzipSync(JSON.stringify([['bc-hydro', 'New, Alice', null, 122528.25, 704.02]]))
  writeFileSync(join(sourceDir, '2020-21.json.gzip'), data)
  const manifest = { sources: [{ id: 'official-2021', year: '2020/21', employerSlug: 'bc-hydro', file: '2020-21.json.gzip', dataSha256: sha256(data), sourceUrl: 'https://example.test/2021.pdf', periodStart: '2020-04-01', periodEnd: '2021-03-31', rowCount: 1, totalRemuneration: 122528.25 }] }
  writeFileSync(join(sourceDir, 'sources.json'), JSON.stringify(manifest))
  const out = join(dir, 'published'); mkdirSync(out); writeFileSync(join(out, 'sentinel'), 'working site')
  const run = () => spawnSync(process.execPath, [resolve('scripts/build-salaries.mjs'), '--research', research, '--out', out], { encoding: 'utf8' })
  return { dir, research, sourceDir, manifest, out, run }
}
test('a corrupted official input cannot erase the previous published output', () => {
  const f = fixture()
  try {
    f.manifest.sources[0].dataSha256 = 'incorrect'
    writeFileSync(join(f.sourceDir, 'sources.json'), JSON.stringify(f.manifest))
    const result = f.run()
    assert.notEqual(result.status, 0)
    assert.match(result.stderr, /hash mismatch/)
    assert.equal(readFileSync(join(f.out, 'sentinel'), 'utf8'), 'working site')
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})
test('verified replacements restore quarantined years consistently in every view with row provenance', () => {
  const f = fixture()
  try {
    const result = f.run()
    assert.equal(result.status, 0, result.stderr)
    const employers = JSON.parse(readFileSync(join(f.out, 'employers/index.json')))
    const year = employers.years.indexOf('2020/21')
    assert.equal(employers.employers[0].counts[year], 1)
    assert.equal(employers.employers[0].coverage[year].status, 'available')
    assert.deepEqual(employers.employers[0].repeated, [])
    const atlas = JSON.parse(readFileSync(join(f.out, '2020-21/bc-hydro.json')))
    assert.deepEqual(atlas.rows[0], ['New, Alice', null, 122528.25, 704.02, 'official-2021'])
    const people = JSON.parse(gunzipSync(readFileSync(join(f.out, 'people/ne.json.gzip'))))
    assert.equal(people[0][5], year)
    assert.equal(people[0][6], 'official-2021')
    const coverage = JSON.parse(readFileSync(join(f.out, 'coverage.json')))
    assert.equal(coverage.corrections[0].status, 'replaced-from-official-source')
    assert.equal(coverage.output.rows, 2)
    const again = f.run()
    assert.equal(again.status, 0, again.stderr)
    assert.equal(JSON.parse(readFileSync(join(f.out, 'coverage.json'))).output.rows, 2)
  } finally { rmSync(f.dir, { recursive: true, force: true }) }
})
