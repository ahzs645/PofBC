// Exercise name discovery against the complete published dataset, including the reported miss.
// Run after build-salary-search.mjs. Timings are diagnostic only, never a flaky CI threshold.
import assert from 'node:assert/strict'
import { readFileSync, statSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { performance } from 'node:perf_hooks'
import { gunzipSync } from 'node:zlib'
import { chooseNameSearchBucket, searchNameSearchDocuments } from '../src/salaries/nameSearch.js'
import { nameQueryTier, personKey } from '../src/salaries/people.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const salaries = join(root, 'public/salaries')
const json = (file) => JSON.parse(readFileSync(join(salaries, file), 'utf8'))
const gzip = (file) => JSON.parse(gunzipSync(readFileSync(join(salaries, file))).toString('utf8'))
const index = json('people/index.json')
const manifest = json('search/index.json')
assert.deepEqual(manifest.context, { years: index.years, employers: index.employers.map((employer) => employer[3]) })
assert.equal(manifest.records, Object.values(index.shards).reduce((sum, value) => sum + value, 0))
const buckets = new Map()
const search = (query, filters) => {
  const prefix = chooseNameSearchBucket(query, manifest)
  if (!prefix) return { results: [], prefix: null, milliseconds: 0 }
  const bucket = manifest.buckets[prefix]
  if (!buckets.has(prefix)) buckets.set(prefix, gzip(`search/${bucket.file}`))
  const start = performance.now()
  const results = searchNameSearchDocuments(buckets.get(prefix), query, filters)
  return { results, prefix, milliseconds: Math.round((performance.now() - start) * 10) / 10 }
}

const key = 'fathibaghbadorani|milad'
const sourceRows = gzip('people/fa.json.gzip').filter((row) => personKey(row[0]) === key)
assert.ok(sourceRows.length > 0, 'the real reported name must remain in the source exports')
const expectedYears = [...new Set(sourceRows.map((row) => row[5]))].sort((a, b) => a - b)
const expectedEmployers = [...new Set(sourceRows.map((row) => row[4]))].sort((a, b) => a - b)
const checks = []
for (const query of ['milad', 'MILAD', '  Milad  ', 'fathi', 'baghbadorani', 'Milad Fathi', 'Fathi Milad', 'Milad    Fathi', 'Milad Fathi Baghbadorani', 'Baghbadorani Milad Fathi', 'mila fath']) {
  const found = search(query)
  const target = found.results.find((entry) => entry.key === key)
  assert.ok(target, `Missing reported name for ${query}`)
  assert.deepEqual(target.years, expectedYears, `${query}: preserve all reporting periods`)
  assert.deepEqual(target.employerIds, expectedEmployers, `${query}: preserve employer scope`)
  assert.ok(found.results.findIndex((entry) => entry.key === key) < 24, `${query}: the exact name must appear on the first page`)
  checks.push({ query, matches: found.results.length, targetPosition: found.results.indexOf(target) + 1, bucket: found.prefix, bucketBytes: manifest.buckets[found.prefix].bytes, milliseconds: found.milliseconds })
}
const milad = search('milad').results
const firstPrefix = milad.findIndex((entry) => entry.tier === 1)
assert.ok(firstPrefix === -1 || milad.slice(firstPrefix).every((entry) => entry.tier === 1), 'complete-word results must precede prefixes')
assert.ok(sourceRows.every((row) => nameQueryTier(row[0], 'Fathi Baghbadorani, Milad', index.sources[row[6]]?.nameDisclosure) === 0), 'precise comma matching remains available')

for (const year of expectedYears) {
  const target = search('milad', { yearIds: new Set([year]), employerIds: new Set(expectedEmployers) }).results.find((entry) => entry.key === key)
  assert.deepEqual(target?.years, [year], 'period filtering must precede card grouping')
}
const absentYears = new Set(index.years.flatMap((_, at) => expectedYears.includes(at) ? [] : [at]))
assert.ok(!search('milad', { yearIds: absentYears }).results.some((entry) => entry.key === key), 'a name must not appear in an undisclosed period')
const otherEmployers = new Set(index.employers.flatMap((_, at) => expectedEmployers.includes(at) ? [] : [at]))
assert.ok(!search('milad', { employerIds: otherEmployers }).results.some((entry) => entry.key === key), 'a name must not acquire another employer')

const pageCosts = ['milad', 'john', 'ma'].map((query) => {
  const found = search(query)
  const page = found.results.slice(0, 24)
  const shards = [...new Set(page.flatMap((entry) => entry.recordShards))]
  const rowBytes = shards.reduce((sum, shard) => sum + statSync(join(salaries, `people/${shard}.json.gzip`)).size, 0)
  assert.ok(page.length <= 24)
  assert.ok(shards.length < Object.keys(index.shards).length, 'a page must not fetch the complete record database')
  return { query, matches: found.results.length, pageNames: page.length, recordShards: shards.length, recordBytes: rowBytes, bucketBytes: manifest.buckets[found.prefix].bytes, milliseconds: found.milliseconds }
})

console.log(JSON.stringify({
  status: 'passed', sourceSha256: manifest.sourceSha256,
  records: manifest.records, names: manifest.names, employerNameDocuments: manifest.documents,
  buckets: Object.keys(manifest.buckets).length,
  totalBucketBytes: Object.values(manifest.buckets).reduce((sum, bucket) => sum + bucket.bytes, 0),
  target: { key, periods: expectedYears.map((at) => index.years[at]), sourceRows: sourceRows.length },
  queries: checks, firstPageCosts: pageCosts
}, null, 2))
