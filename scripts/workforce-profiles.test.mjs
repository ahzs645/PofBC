import test from 'node:test'
import assert from 'node:assert/strict'
import { buildProfiles, parseProfileCsv, runProfileBuild } from './build-workforce-profiles.mjs'
import { filterProfileRows, loadProfiles, profileAssetUrl, validateProfiles } from '../src/salaries/workforceProfiles.js'

const { data, json } = buildProfiles()
test('30 checksummed official CSVs retain all 10435 source rows, separately typed', () => {
  assert.equal(data.tables.length, 30)
  assert.equal(data.tables.reduce((n, table) => n + table.rows.length, 0), 10435)
  assert.equal(data.tables.filter(t => t.recordType === 'ministry-lookup').reduce((n, t) => n + t.rows.length, 0), 111)
  assert.deepEqual([...new Set(data.tables.map(t => t.yearLabel))], ['2018', '2020', '2022', '2024'])
  assert.ok(data.tables.every(t => !t.columns.includes('salary') && !t.columns.includes('name')))
  assert.equal(validateProfiles(data), data)
})
test('profile employee counts preserve source scope and do not substitute FOI headcount', () => {
  assert.deepEqual(data.tables.filter(t => t.tableType === 'EmpCounts').map(t => [t.yearLabel, t.rows.find(r => r[0] === 'BCPS' && r[1] === 'ALL')[2]]), [['2018','27220'], ['2020','29931'], ['2022','30696'], ['2024','34632']])
})
test('blank, suppressed and not-applicable values remain strings, never zero or estimates', () => {
  const table = data.tables.find(t => t.name === 'WP2024_Rep_Occ_Rgn')
  assert.ok(table.rows.some(r => r.includes('S')))
  assert.ok(table.rows.some(r => r.includes('NA')))
  assert.ok(table.rows.some(r => r.includes('')))
  assert.ok(data.tables.every(t => t.rows.every(r => r.every(c => typeof c === 'string'))))
  assert.ok(filterProfileRows(table, ' af ').every(r => r.some(c => c.toLowerCase().includes('af'))))
})
test('CSV parser preserves escaped quotes, embedded newlines, CRLF, BOM and trailing blanks', () => {
  assert.deepEqual(parseProfileCsv('\uFEFFa,b,c\r\n"quoted,comma","a""b","line\nline"\r\nx,,\r\n'), [['a','b','c'],['quoted,comma','a"b','line\nline'],['x','','']])
  assert.throws(() => parseProfileCsv('a\n"missing'), /Unterminated/)
})
test('profile build is deterministic and checked-in download matches', () => {
  assert.equal(buildProfiles().json, json)
  assert.match(runProfileBuild({ check: true }), /Checked 30/)
})
test('profile loader supports base paths, aborts and retry errors', async () => {
  const controller = new AbortController()
  let seen
  const loaded = await loadProfiles({ base: '/PofBC', signal: controller.signal, fetcher: async (url, options) => { seen = [url, options.signal]; return { ok: true, json: async () => data } } })
  assert.equal(loaded, data)
  assert.deepEqual(seen, ['/PofBC/salaries/workforce-profiles.json', controller.signal])
  assert.equal(profileAssetUrl('/PofBC/'), '/PofBC/salaries/workforce-profiles.json')
  await assert.rejects(loadProfiles({ fetcher: async () => ({ ok: false, status: 503 }) }), /503/)
  const invalid = structuredClone(data); invalid.tables[0].rows[0][0] = 0
  assert.throws(() => validateProfiles(invalid), /Invalid/)
  const duplicate = structuredClone(data); duplicate.tables[1] = duplicate.tables[0]
  assert.throws(() => validateProfiles(duplicate), /Invalid/)
})
