import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { spawnSync } from 'node:child_process'
import { ledger, eventCollector, dateBound } from './evidence-integrity.mjs'

const seed = { id: 'same', subject: 'body', type: 'established', title: 'Established', date: { start: '2004', end: null, precision: 'year', inclusive: false }, status: 'source_reported_past', sources: [0], reviewed: null, locator: 'p. 1' }
test('corroboration keeps independently located evidence and does not create a review date', () => {
  const audit = ledger(); const { events, add } = eventCollector(audit)
  add(seed, 'a'); add({ ...seed, sources: [1], locator: 's. 2', reviewed: '2026-09-30' }, 'b')
  assert.equal(events.length, 1); assert.deepEqual(events[0].sources, [0, 1])
  assert.equal(events[0].reviewed, null)
  assert.deepEqual(events[0].evidence.map((e) => [e.locator, e.reviewed]), [['p. 1', null], ['s. 2', '2026-09-30']])
  assert.equal(audit.rows[1].disposition, 'corroborating_duplicate')
})
test('conflicting assertions both survive, with stable ids and traceable duplicates', () => {
  const run = (order) => { const audit = ledger(); const c = eventCollector(audit); for (const e of order) c.add(e, e.date.start); return { ...c, audit } }
  const other = { ...seed, date: { ...seed.date, start: '2005' } }
  const a = run([seed, seed, other]);const b = run([other, seed])
  assert.equal(a.events.length, 2)
  assert.deepEqual(a.events.map((e) => e.id).sort(), b.events.map((e) => e.id).sort())
  assert.ok(a.events.every((e) => e.status === 'conflicting' && e.conflictGroup === 'same'))
  assert.ok(a.audit.rows.every((r) => a.events.some((e) => e.id === r.output_id)))
})
test('calendar month bounds include the 29th, 30th and 31st without changing source dates', () => {
  for (const [value, expected] of [['2000-02', '2000-02-29'], ['1900-02','1900-02-28'], ['2024-04','2024-04-30'], ['2024-01','2024-01-31']]) assert.equal(dateBound(value, true), expected)
})
test('actual event compiler retains fragments and rejected input, with no review-date fallback', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'government-evidence-'))
  try {
    mkdirSync(join(directory, 'research/atlas'), { recursive: true }); mkdirSync(join(directory, 'src/government'), { recursive: true })
    const row = { id: 'test', subject_id: 'body', event_type: 'established', title: 'Body established', date: { start: '2004', precision: 'year' }, evidence: { source_url: 'https://example.org/report#page=5', locator: 's. 4' } }
    writeFileSync(join(directory, 'research/atlas/events-test.json'), JSON.stringify({ events: [row, { ...row, date: { start: '2005', precision: 'year' } }, { ...row, id: 'missing', subject_id: null }] }))
    const result = spawnSync(process.execPath, [resolve('scripts/build-government-events.mjs')], { cwd: directory, encoding: 'utf8', env: { ...process.env, GOVERNMENT_RESEARCH: 'research' } })
    assert.equal(result.status, 0, result.stderr)
    const { EVENTS, EVENT_SOURCES } = await import(pathToFileURL(join(directory, 'src/government/eventsData.js')))
    assert.equal(EVENTS.length, 2); assert.ok(EVENTS.every((e) => e.reviewed === null && e.status === 'conflicting'))
    assert.equal(EVENT_SOURCES[0].url, 'https://example.org/report#page=5')
    assert.equal(EVENT_SOURCES[0].documentUrl, 'https://example.org/report')
    const report = JSON.parse(readFileSync(join(directory, 'research/audit/events-import.json')))
    assert.equal(report.rows.length, 3); assert.equal(report.rows[2].input.id, 'missing'); assert.equal(report.rows[2].disposition, 'unresolved_unmapped')
  } finally { rmSync(directory, { recursive: true, force: true }) }
})
test('history projection retains predecessor sets, source fragments, and competing end bounds', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'government-history-'))
  const put = (name, value) => writeFileSync(join(directory, 'research/history', name), JSON.stringify(value))
  try {
    mkdirSync(join(directory, 'research/history'), { recursive: true }); mkdirSync(join(directory, 'src/government'), { recursive: true })
    for (const era of ['1871-1903','1903-1941','1941-1975','1975-1991','1991-2011','2011-2026']) put(`ministers-${era}.json`, { records: [] })
    put('bodies.json', { records: [{ id: 'new-body', name: 'New body', kind: 'agency', established: '2001', predecessorIds: ['a','b'], source: 'https://example.org/body#history' }] })
    put('responsible-a.json', { records: { 'new-body': [{ ministry: 'Ministry of Finance', from: '2001', to: '2003', source: 'https://example.org/a#page=7', locator: 'p. 7' }] } })
    put('responsible-b.json', { records: { 'new-body': [{ ministry: 'Ministry of Finance', from: '2001', to: '2004', source: 'https://example.org/b#page=8', locator: 'p. 8' }] } })
    put('holders.json', { offices: [] })
    const result = spawnSync(process.execPath, [resolve('scripts/build-government-history.mjs')], { cwd: directory, encoding: 'utf8', env: { ...process.env, GOVERNMENT_HISTORY_SOURCE: 'research/history' } })
    assert.equal(result.status, 0, result.stderr)
    const data = await import(pathToFileURL(join(directory, 'src/government/historyData.js')))
    assert.deepEqual(data.HISTORICAL_BODIES[0].predecessors, ['a','b'])
    assert.deepEqual(data.HISTORICAL_BODIES[0].responsible.map((r) => [r[2],r[4]]), [['2003','p. 7'],['2004','p. 8']])
    assert.ok(data.HISTORY_SOURCES.includes('https://example.org/a#page=7'))
    const audit = JSON.parse(readFileSync(join(directory, 'research/audit/history-import.json')))
    assert.ok(audit.rows.some((r) => r.disposition === 'conflicting' && r.input.to === '2004'))
  } finally { rmSync(directory, { recursive: true, force: true }) }
})
test('different historical meanings do not become corroboration merely because dates agree', () => {
  const audit = ledger(); const c = eventCollector(audit)
  c.add({ ...seed, notes: 'Legal incorporation' }, 'legal')
  c.add({ ...seed, notes: 'Opening to the public' }, 'opening')
  assert.equal(c.events.length, 2)
  assert.ok(c.events.every((e) => e.status === 'conflicting'))
})
test('a claim under another id that dates the same happening becomes evidence, not a second event', () => {
  const audit = ledger(); const c = eventCollector(audit)
  c.add(seed, 'atlas')
  c.attach(c.events[0], { ...seed, id: 'review', title: 'Body: as the body dates itself', sources: [2], locator: 'release', reviewed: '2026-09-30' }, 'review', undefined, 'same date')
  assert.equal(c.events.length, 1); assert.deepEqual(c.events[0].sources, [0, 2])
  assert.deepEqual(c.events[0].evidence.map((e) => [e.title, e.locator, e.reviewed]), [['Established', 'p. 1', null], ['Body: as the body dates itself', 'release', '2026-09-30']])
  assert.deepEqual(audit.rows.map((r) => [r.origin, r.disposition, r.output_id]), [['atlas', 'accepted', 'same'], ['review', 'corroborating_duplicate', 'same']])
})
