import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { filterTitles, titleMedians } from './titleScope.js'
import { keyedTitles } from './positions.js'

const sectors = [{ sector: 'A' }, { sector: 'B' }, { sector: 'B' }]
const years = ['2018', '2019', '2020', '2021']
const title = { key: 'manager', raise: { rate: 0.05 } }
const scopes = { manager: [[0, 0, 1, 40000], [1, 1, 3, 90000], [2, 1, 1, 50000], [0, 3, 1, 70000]] }

test('filtered positions require actual rows and show the weighted mean for the latest matching period', () => {
  assert.deepEqual(filterTitles([title], scopes, sectors, years, 'all', [2, 2]), [])
  assert.deepEqual(filterTitles([title], scopes, sectors, years, 'A', [1, 2]), [])
  const [result] = filterTitles([title], scopes, sectors, years, 'B', [1, 2])
  assert.equal(result.mean, 350)
  assert.equal(result.first, 1)
  assert.equal(result.last, 1)
  assert.equal(result.rows, 4)
  assert.equal(result.employers, 2)
  assert.equal(result.raise, null)
})

test('a pooled median belongs to the sectors and periods represented in the pool', () => {
  const cells = sectors.map((entry, at) => ({ entry, year: 1, median: 10 * at }))
  const pooled = { all: [[1, 12]], B: [[1, 15]] }
  assert.deepEqual(titleMedians(cells, pooled, 'A', years), [null, 0, null, null])
  assert.equal(titleMedians(cells, pooled, 'B', years)[1], 15)
  assert.deepEqual(titleMedians(cells, pooled, 'Unknown', years), [null, null, null, null])
  assert.equal(titleMedians(cells.slice(1), { all: [[1, 15]] }, 'B', years)[1], 15)
})

const read = (name) => {
  const bytes = readFileSync(new URL(name, new URL('../../public/salaries/', import.meta.url)))
  return JSON.parse(name.endsWith('gzip') ? gunzipSync(bytes) : bytes)
}

test('browser indexes agree with the published employer, surname and position indexes', () => {
  const browse = read('browse.json.gzip')
  const employers = read('employers/index.json')
  const people = read('people/index.json')
  const { shards, ...rest } = browse
  assert.deepEqual(rest, employers)
  assert.deepEqual(shards, people.shards)
  assert.deepEqual(browse.employers.map(({ names, sector, body, slug }) => [names.at(-1), sector, body, slug]), people.employers)
  const titles = keyedTitles(read('positions/index.json.gzip'))
  const scopes = read('position-scopes.json.gzip')
  assert.equal(Object.keys(scopes).length, titles.length)
  for (const { key, rows, first, last, employers } of titles) {
    const cells = scopes[key]
    assert.equal(cells.reduce((sum, cell) => sum + cell[2], 0), rows)
    assert.equal(cells[0][1], first)
    assert.equal(cells.at(-1)[1], last)
    assert.equal(new Set(cells.map(([employer]) => employer)).size, employers)
  }
})
