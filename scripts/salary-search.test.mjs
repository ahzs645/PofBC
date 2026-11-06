import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { gunzipSync, gzipSync } from 'node:zlib'
import { buildSalarySearch } from './build-salary-search.mjs'
import { chooseNameSearchBucket, searchNameSearchDocuments } from '../src/salaries/nameSearch.js'

const read = (path) => JSON.parse(gunzipSync(readFileSync(path)).toString('utf8'))
const writeGzip = (path, value) => writeFileSync(path, gzipSync(JSON.stringify(value)))

const fixture = (t) => {
  const salaries = mkdtempSync(join(tmpdir(), 'salary-name-search-'))
  t.after(() => rmSync(salaries, { recursive: true, force: true }))
  mkdirSync(join(salaries, 'people'))
  mkdirSync(join(salaries, 'links'))
  const index = {
    years: ['2022/23', '2023/24'],
    employers: [['Northern Health', 'Health authorities', null, 'northern-health'], ['Elsewhere', 'Government', null, 'elsewhere']],
    sources: { original: { currency: 'CAD' } },
    shards: { br: 2, fa: 2, mi: 1, sm: 1 }
  }
  writeFileSync(join(salaries, 'people/index.json'), JSON.stringify(index))
  writeGzip(join(salaries, 'people/fa.json.gzip'), [
    ['Fathi Baghbadorani, Milad', null, 111792, 11664, 0, 0, 'original', 18],
    ['Fathi Baghbadorani, Milad', null, 78500, null, 0, 1, 'original', 24]
  ])
  writeGzip(join(salaries, 'people/mi.json.gzip'), [['Miladinovic, Josephine', null, 94000, null, 0, 1, 'original', 1]])
  writeGzip(join(salaries, 'people/sm.json.gzip'), [['Smith, Jane', null, 90000, null, 0, 1, 'original', 1]])
  writeGzip(join(salaries, 'people/br.json.gzip'), [
    ['Browne, Janet', null, 80000, null, 0, 0, 'original', 1],
    ['Browne, Janet', null, 82000, null, 1, 1, 'original', 2]
  ])
  const links = { links: [['northern-health', 'smith|jane', 'Smith, Jane', [['browne|janet', 'Browne, Janet', 'verified', 'Fixture source review']]]] }
  writeGzip(join(salaries, 'links/sm.json.gzip'), links)
  writeGzip(join(salaries, 'links/br.json.gzip'), links)
  return { salaries, index }
}

const find = (salaries, manifest, query, filters) => {
  const bucket = chooseNameSearchBucket(query, manifest)
  return bucket ? searchNameSearchDocuments(read(join(salaries, 'search', manifest.buckets[bucket].file)), query, filters) : []
}

test('published surname exports build a first-name directory and preserve employer-scoped links', (t) => {
  const { salaries } = fixture(t)
  const before = readFileSync(join(salaries, 'people/fa.json.gzip'))
  const manifest = buildSalarySearch({ salaries })
  for (const query of ['Milad', '  MILAD  ', 'Fathi', 'Baghbadorani', 'milad fathi', 'baghbadorani milad', 'mi fat']) {
    assert.ok(find(salaries, manifest, query).some((entry) => entry.key === 'fathibaghbadorani|milad'), query)
  }
  assert.deepEqual(find(salaries, manifest, 'milad').map((entry) => entry.key), ['fathibaghbadorani|milad', 'miladinovic|josephine'])
  const aliases = find(salaries, manifest, 'janet')
  assert.deepEqual(aliases.map((entry) => [entry.key, entry.employerIds]), [['browne|janet', [1]], ['smith|jane', [0]]])
  assert.deepEqual(aliases.find((entry) => entry.key === 'smith|jane').recordShards, ['br', 'sm'], 'a reviewed surname change keeps both original record routes')
  assert.equal(find(salaries, manifest, 'janet', { employerIds: new Set([1]), yearIds: new Set([0]) }).length, 0)
  assert.deepEqual(readFileSync(join(salaries, 'people/fa.json.gzip')), before, 'search build must not change original records')
  assert.equal(manifest.records, 6)
  assert.equal(manifest.documents, 4)
})

test('name-search builds reproduce byte for byte and reject incomplete source shards before replacing output', (t) => {
  const { salaries } = fixture(t)
  const first = buildSalarySearch({ salaries })
  const output = join(salaries, 'search')
  const bytes = new Map(readdirSync(output).map((file) => [file, readFileSync(join(output, file))]))
  assert.deepEqual(buildSalarySearch({ salaries }), first)
  for (const [file, content] of bytes) assert.deepEqual(readFileSync(join(output, file)), content, file)
  writeGzip(join(salaries, 'people/fa.json.gzip'), [])
  assert.throws(() => buildSalarySearch({ salaries }), /does not match the published index/)
  for (const [file, content] of bytes) assert.deepEqual(readFileSync(join(output, file)), content, 'a failed rebuild must leave the previous directory usable')
})
