import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { validateHeldNameConnections } from './lib/held-name-connections.mjs'
import { nameRecordFingerprint, nameRowsFingerprint } from './lib/reviewed-name-connections.mjs'
import { gzipSync } from 'node:zlib'
import { salaryBaselineContext } from './lib/salary-baseline-context.mjs'
import { personKey } from '../src/salaries/people.js'

const index = { employers: [['Employer', 'Health authorities', null, 'employer']], years: ['2023/24'],
  sources: { official: { sourceKind: 'official-pdf', sha256: 'primary-pdf' }, compiled: { sourceKind: 'compiled' } } }
const original = ['Murthy, Srinivasa', null, 120000, null, 0, 0, 'official', 5]
const alias = ['Murtby, Srinivasa', null, 120000, 0, 0, 0, 'compiled', null]
const payload = (left = alias, right = original) => ({ schemaVersion: 1, inputs: [], decisions: [{ employer: 'employer', names: [left[0], right[0]],
  decision: 'verified', note: 'Printed spelling reviewed; compiled expenses remain unverified', evidence: [{ sourceId: 'official', pdfPage: 5 }],
  proof: { method: 'unique-remuneration-row', observations: [left, right].map((row) => ({ nameKey: personKey(row[0]), rowsSha256: nameRowsFingerprint([row], index) })),
    witnesses: [{ rowSha256: nameRecordFingerprint(right, index), sourceId: 'official', pdfSha256: 'primary-pdf', pdfPage: 5, periodPrefix: '2023', payCents: 12000000 }] } }] })

test('a reviewed name correction can retain a compiled zero and an undisclosed primary expense without equating them', () => {
  assert.equal(validateHeldNameConnections(payload(), [alias, original], index, '.').length, 1)
  assert.equal(original[3], null)
  assert.equal(alias[3], 0)
  const bad = [...alias]; bad[3] = 50
  assert.throws(() => validateHeldNameConnections(payload(bad), [bad, original], index, '.'), /expense discrepancy/)
})

test('changed source data, pages or newly competing remuneration rows invalidate the review', () => {
  const other = [...original]; other[0] = 'Another, Person'
  assert.throws(() => validateHeldNameConnections(payload(), [alias, original, other], index, '.'), /no longer uniquely/)
  const changed = structuredClone(index); changed.sources.official.sha256 = 'changed'
  assert.throws(() => validateHeldNameConnections(payload(), [alias, original], changed, '.'), /witness changed/)
  const moved = [...original]; moved[7] = 6
  assert.throws(() => validateHeldNameConnections(payload(), [alias, moved], index, '.'), /observations changed/)
})

test('different initials require a likely source-copy assumption and the same published position', () => {
  const left = [...alias], right = [...original]
  left[0] = 'Rohan, J'; right[0] = 'Rohan, C'; left[1] = right[1] = 'Supervisor'
  const p = payload(left, right)
  assert.throws(() => validateHeldNameConnections(p, [left, right], index, '.'), /Conflicting initials/)
  p.decisions[0].decision = 'likely'
  assert.equal(validateHeldNameConnections(p, [left, right], index, '.').length, 1)
  right[1] = 'Other'
  assert.throws(() => validateHeldNameConnections(payload(left, right), [left, right], index, '.'), /Conflicting initials/)
})

test('a separator review never changes letters or expands an initial into a full name', () => {
  const left = [...original], right = [...alias]
  left[0] = 'LEONG P.'; right[0] = 'Leong, P.'
  const p = payload(left, right)
  p.decisions[0].proof.method = 'surname-initial-separator'
  p.decisions[0].proof.witnesses = payload(right, left).decisions[0].proof.witnesses
  assert.equal(validateHeldNameConnections(p, [left, right], index, '.').length, 1)
  right[0] = 'Leong, Paul'
  const expanded = payload(left, right); expanded.decisions[0].proof.method = 'surname-initial-separator'
  expanded.decisions[0].proof.witnesses = payload(right, left).decisions[0].proof.witnesses
  assert.throws(() => validateHeldNameConnections(expanded, [left, right], index, '.'), /cannot infer a full given name/)
})

test('a qualified inference needs its exact pinned case receipt and cannot become verified', () => {
  const root = mkdtempSync(join(tmpdir(), 'name-review-'))
  try {
    const p = payload(), entry = p.decisions[0]
    entry.candidateId = 10; entry.decision = 'likely'; entry.proof.method = 'conservative-inference'
    const raw = JSON.stringify([{ id: 10, employer: entry.employer, names: entry.names, assessment: 'supported-likely-source-inference' }])
    writeFileSync(join(root, 'receipt.json'), raw)
    p.inputs = [{ path: 'receipt.json', sha256: createHash('sha256').update(raw).digest('hex') }]
    entry.proof.receipts = [{ path: 'receipt.json', id: 10 }]
    assert.equal(validateHeldNameConnections(p, [alias, original], index, root).length, 1)
    entry.decision = 'verified'
    assert.throws(() => validateHeldNameConnections(p, [alias, original], index, root), /assumption cannot be verified/)
    entry.decision = 'likely'; entry.canonicalName = 'Murthy, Someone'
    assert.throws(() => validateHeldNameConnections(p, [alias, original], index, root), /full name requires/)
    delete entry.canonicalName
    writeFileSync(join(root, 'receipt.json'), '[]')
    assert.throws(() => validateHeldNameConnections(p, [alias, original], index, root), /evidence changed/)
  } finally { rmSync(root, { recursive: true, force: true }) }
})


test('frozen held receipts survive additive earlier periods but original row mutations still reject', () => {
  const root = mkdtempSync(join(tmpdir(), 'held-historical-'))
  const zip = (value) => gzipSync(JSON.stringify(value) + '\n', { level: 9, mtime: 0 })
  const sha = (bytes) => createHash('sha256').update(bytes).digest('hex')
  try {
    const area = join(root, 'research/salaries/source-follow-through-2026-11-02')
    mkdirSync(area, { recursive: true })
    const historicalIndex = { ...index, shards: { mu: 2 } }
    const historicalRows = [alias, original].toSorted((a, b) => a[0].localeCompare(b[0]))
    const indexBytes = Buffer.from(JSON.stringify(historicalIndex) + '\n')
    writeFileSync(join(area, 'baseline-people-index.json.gzip'), gzipSync(indexBytes))
    writeFileSync(join(area, 'baseline.json.gzip'), zip({ baselinePeopleIndexSha256: sha(indexBytes),
      exportFiles: [{ path: 'public/salaries/people/mu.json.gzip', sha256: sha(zip(historicalRows)) }] }))
    const liveIndex = { ...historicalIndex, years: ['2000/01', ...index.years],
      sources: { ...index.sources, early: { sourceKind: 'official-pdf', sha256: 'new-earlier-source' } } }
    const carried = historicalRows.map((row) => { const copy = [...row]; copy[5] = 1; return copy })
    const earlier = [...original]; earlier[2] = 85000; earlier[6] = 'early'
    const unrelated = [...earlier]; unrelated[0] = 'Other, Name'
    const review = payload(), originalReceipt = JSON.stringify(review)
    assert.throws(() => validateHeldNameConnections(review, [...carried, earlier, unrelated], liveIndex, root), /observations changed/)
    const baseline = salaryBaselineContext([...carried, earlier, unrelated], liveIndex, root)
    assert.deepEqual(baseline.rows, historicalRows)
    const decisions = validateHeldNameConnections(review, baseline.rows, baseline.index, root, { readInput: baseline.readInput })
    assert.equal(decisions.length, 1, 'only the original reviewed pair is returned')
    assert.deepEqual(decisions[0].names, review.decisions[0].names)
    assert.equal(JSON.stringify(review), originalReceipt, 'historical receipts are never reissued')
    const changed = carried.map((row) => [...row]); changed[0][2] += 1
    assert.throws(() => salaryBaselineContext([...changed, earlier, unrelated], liveIndex, root), /Original named export differs/)
  } finally { rmSync(root, { recursive: true, force: true }) }
})
