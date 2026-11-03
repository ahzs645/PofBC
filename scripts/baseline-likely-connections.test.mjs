import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, statSync } from 'node:fs'
import { resolve } from 'node:path'
import { gunzipSync } from 'node:zlib'
import { spawnSync } from 'node:child_process'
import { personKey } from '../src/salaries/people.js'
import { BASELINE_LIKELY_PAIRS, validateBaselineLikelyConnections } from './lib/baseline-likely-connections.mjs'

const root = resolve(import.meta.dirname, '..'), area = 'research/salaries/source-follow-through-2026-11-02'
const receiptPath = resolve(root, area, 'likely-continuity.json')
const payload = JSON.parse(readFileSync(receiptPath))
const index = JSON.parse(readFileSync(resolve(root, 'public/salaries/people/index.json')))
const oldIndex = JSON.parse(gunzipSync(readFileSync(resolve(root, area, 'baseline-people-index.json.gzip'))))
const surnames = new Set(BASELINE_LIKELY_PAIRS.map(([k]) => k.split('|')[0]))
const at = index.employers.findIndex((e) => e[3] === 'provincial-health-services-authority')
const shards = [...new Set([...surnames].map((n) => n.slice(0, 2)))]
const rows = shards.flatMap((s) => JSON.parse(gunzipSync(readFileSync(resolve(root, `public/salaries/people/${s}.json.gzip`)))).filter((r) => r[4] === at && surnames.has(personKey(r[0]).split('|')[0])))
const oldAt = oldIndex.employers.findIndex((e) => e[3] === 'provincial-health-services-authority')
const oldRows = rows.filter((r) => oldIndex.sources[r[6]]).map((r) => { const a = [...r]; a[4] = oldAt; a[5] = oldIndex.years.indexOf(index.years[r[5]]); return a })
const bytes = new Map(payload.inputs.map((p) => [p.path, readFileSync(resolve(root, p.path))]))
const readInput = (p) => bytes.get(p)
const fixture = () => ({ p: structuredClone(payload), rows: structuredClone(rows), index: { ...index, sources: { ...index.sources } }, baseline: { rows: structuredClone(oldRows), index: oldIndex } })
const run = (f, read = readInput) => validateBaselineLikelyConnections(f.p, f.rows, f.index, f.baseline, root, { readInput: read })
const alias = (f) => f.rows.find((r) => personKey(r[0]) === f.p.decisions[0].proof.aliasKey)

test('exact11 old likely connections survive unchanged endpoint and whole-family histories', () => {
  const f = fixture(); const before = structuredClone(f.rows); const result = run(f)
  assert.equal(result.length, 11); assert.ok(result.every((e) => e.decision === 'likely' && !e.canonicalName))
  assert.deepEqual(f.rows, before); assert.equal(new Set(result.map((e) => personKey(e.names[0]))).size, 11)
  assert.ok(result.every((e) => e.note.includes('assumption') && e.note.includes('no new identity evidence')))
})

test('a new alias occurrence invalidates complete history and multiplicity pins', () => {
  const f = fixture(); f.rows.push([...alias(f)])
  assert.throws(() => run(f), /alias or target history changed/)
})

test('a new target observation invalidates the old assumption', () => {
  const f = fixture(); const r = [...f.rows.find((r) => personKey(r[0]) === f.p.decisions[0].proof.targetKey)]; r[2] += 1; f.rows.push(r)
  assert.throws(() => run(f), /alias or target history changed/)
})

test('a third compatible given name invalidates the whole surname-family gate', () => {
  const f = fixture(); const r = [...alias(f)]; r[0] = 'Bell,Christopher Q'; f.rows.push(r)
  assert.throws(() => run(f), /surname family changed; review new competing names/)
})

test('a new surname-family record is blocked even outside the two endpoint keys', () => {
  const f = fixture(); const r = [...alias(f)]; r[0] = 'Bell,Another Employee'; f.rows.push(r)
  assert.throws(() => run(f), /surname family changed/)
})

test('modified original baseline history cannot be hidden behind unchanged live rows', () => {
  const f = fixture(); f.baseline.rows.find((r) => personKey(r[0]) === f.p.decisions[0].proof.aliasKey)[2] += 1
  assert.throws(() => run(f), /alias or target history changed/)
})

test('source key and full source-definition changes both invalidate continuity', () => {
  const f = fixture(); alias(f)[6] = 'unreviewed-new-source'; assert.throws(() => run(f), /history changed/)
  const g = fixture(); const id = alias(g)[6]; g.index.sources[id] = { ...g.index.sources[id], currency: 'USD' }
  assert.throws(() => run(g), /source IDs or definitions changed/)
})

test('changed baseline graph or concurrent repeat ledger bytes reject old receipts', () => {
  for (const path of [payload.inputs[0].path, payload.inputs[1].path]) {
    assert.throws(() => run(fixture(), (p) => p === path ? Buffer.from('changed evidence') : readInput(p)), /input changed/)
  }
})

test('removing either required evidence pin cannot retain the old assumption', () => {
  for (const path of [payload.inputs[0].path, payload.inputs[1].path]) {
    const f = fixture(); f.p.inputs = f.p.inputs.filter((p) => p.path !== path)
    assert.throws(() => run(f), /must both be pinned/)
  }
})

test('a prior verified status cannot be relabelled likely and likely can never become verified', () => {
  const f = fixture(); f.p.decisions[0].proof.oldStatus = 'verified'; assert.throws(() => run(f), /likely only/)
  const g = fixture(); g.p.decisions[0].decision = 'verified'; assert.throws(() => run(g), /likely only/)
  const h = fixture(); h.p.decisions[0].canonicalName = 'New identity'; assert.throws(() => run(h), /likely only/)
})

test('only the exact11 approved old pairs qualify; wrong targets, missing and duplicated entries fail', () => {
  const f = fixture(); f.p.decisions.pop(); assert.throws(() => run(f), /Invalid11-pair/)
  const g = fixture(); g.p.decisions[0] = structuredClone(g.p.decisions[1]); assert.throws(() => run(g), /approved11/)
  const h = fixture(); h.p.decisions[0].proof.targetKey = 'bell|someone else'; assert.throws(() => run(h), /approved11/)
})

test('the exact old likely reason and disclosed preferred name are mandatory', () => {
  const f = fixture(); f.p.decisions[0].proof.oldReason = 'New invented qualification'; assert.throws(() => run(f), /actual prior likely path/)
  const g = fixture(); g.p.decisions[0].preferredName = 'Bell,Someone Else'; assert.throws(() => run(g), /likely only/)
})

test('semantic employer and year fingerprints tolerate shifted live index offsets', () => {
  const f = fixture(); f.index = { ...f.index, employers: [['New', 'Other', null, 'new'], ...f.index.employers], years: ['1900/01', ...f.index.years] }
  f.rows.forEach((r) => { r[4] += 1; r[5] += 1 })
  assert.equal(run(f).length, 11)
})

test('baseline context must agree with the pinned original index', () => {
  const f = fixture(); f.baseline.index = { ...oldIndex, years: [...oldIndex.years, '2099/00'] }
  assert.throws(() => run(f), /baseline index context changed/)
})

test('readonly generation checks all11 source-family pins without changing the receipt', () => {
  const before = readFileSync(receiptPath), time = statSync(receiptPath).mtimeMs
  const result = spawnSync('node', ['scripts/review-baseline-likely-connections.mjs', '--check'], { cwd: root, encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr); assert.deepEqual(readFileSync(receiptPath), before); assert.equal(statSync(receiptPath).mtimeMs, time)
})
