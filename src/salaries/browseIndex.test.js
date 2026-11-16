import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { loadSalaryIndexes, packBrowseIndex, shownSources, unpackBrowseIndex, UNSHOWN_SOURCE_FIELDS } from './browseIndex.js'

const read = (path) => JSON.parse(readFileSync(new URL(`../../public/salaries/${path}`, import.meta.url)))

test('the packed index unpacks to the two published indexes, less the fields no screen shows', () => {
  const people = read('people/index.json')
  const employers = read('employers/index.json')
  const packed = packBrowseIndex(people, employers)
  // What the browser gets is what survives JSON, as the build writes it.
  const unpacked = unpackBrowseIndex(JSON.parse(JSON.stringify(packed)))
  const sources = shownSources(people.sources)
  assert.deepEqual(unpacked.people, { ...people, sources })
  assert.deepEqual(unpacked.employers, { ...employers, sources })
  for (const source of Object.values(unpacked.people.sources)) {
    for (const field of UNSHOWN_SOURCE_FIELDS) assert.equal(Object.hasOwn(source, field), false)
  }
  assert.ok(JSON.stringify(packed).length < 0.25 * (JSON.stringify(people).length + JSON.stringify(employers).length), 'packing should cut the pair to under a quarter')
})

const small = () => {
  const years = [{ label: '2023/24' }, { label: '2024/25' }]
  const sources = { a: { id: 'a', url: 'https://example.test/a.pdf', validation: { method: 'sums' }, dataSha256: 'f'.repeat(64), notes: ['One.'] } }
  const missing = { status: 'missing', sourceIds: [], notes: ['Nothing imported.'] }
  const available = { status: 'available', sourceIds: ['a'], rows: 3 }
  const employers = { schemaVersion: 2, years, sources, recordCounts: { official: 3, compiled: 0 }, aliases: {},
    employers: [{ slug: 'one', names: ['One'], body: null, sector: 'Government', counts: [0, 3], repeated: 0, coverage: [missing, available] },
      { slug: 'two', names: ['Two'], body: 'two', sector: 'Government', counts: [0, 0], repeated: 0, coverage: [missing, missing] }] }
  const people = { schemaVersion: 2, years, sources, shards: { on: 3 }, employers: [['One', 'Government', null, 'one'], ['Two', 'Government', 'two', 'two']],
    coverage: { one: [missing, available], two: [missing, missing] } }
  return { people, employers }
}

test('equal coverage cells are stored once', () => {
  const { people, employers } = small()
  const packed = packBrowseIndex(people, employers)
  assert.equal(packed.cells.length, 2)
  assert.deepEqual(packed.employers.employers.map((entry) => entry.coverage), [[0, 1], [0, 0]])
})

test('packing refuses indexes that disagree', () => {
  const { people, employers } = small()
  assert.throws(() => packBrowseIndex({ ...people, coverage: { ...people.coverage, two: [] } }, employers), /different coverage/)
  assert.throws(() => packBrowseIndex({ ...people, years: [] }, employers), /reporting periods/)
  assert.throws(() => packBrowseIndex({ ...people, employers: [...people.employers].reverse() }, employers), /Employer 0/)
})

test('the loader falls back to the published pair when the packed file is not there', async () => {
  const { people, employers } = small()
  const asked = []
  const files = { 'salaries/people/index.json': people, 'salaries/employers/index.json': employers }
  const loadJson = (path) => { asked.push(path); return path in files ? Promise.resolve(files[path]) : Promise.reject(new Error('404')) }
  assert.deepEqual(await loadSalaryIndexes(loadJson), { people, employers })
  assert.equal(asked.length, 3)
  const packedOnly = (path) => path.endsWith('.gzip') ? Promise.resolve(packBrowseIndex(people, employers)) : Promise.reject(new Error('unexpected'))
  const loaded = await loadSalaryIndexes(packedOnly)
  assert.deepEqual(loaded.employers.employers[0].coverage, employers.employers[0].coverage)
})
