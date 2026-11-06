import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, statSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'
import { gunzipSync } from 'node:zlib'
import { nameRecordFingerprint, nameRowsFingerprint } from './lib/reviewed-name-connections.mjs'
import { validateFollowThroughNameReview } from './lib/follow-through-name-connections.mjs'

const root = resolve(import.meta.dirname, '..')
const payload = JSON.parse(readFileSync(resolve(root, 'research/salaries/source-follow-through-2026-11-02/name-review-rru.json')))
const fullIndex = JSON.parse(readFileSync(resolve(root, 'public/salaries/people/index.json')))
const at = fullIndex.employers.findIndex((e) => e[3] === 'royal-roads-university')
const cncAt = fullIndex.employers.findIndex((e) => e[3] === 'college-of-new-caledonia')
const relevantRows = Object.keys(fullIndex.shards).flatMap((s) => JSON.parse(gunzipSync(readFileSync(resolve(root, `public/salaries/people/${s}.json.gzip`)))).filter((r) => r[4] === at || r[4] === cncAt))
const allRows = relevantRows.filter((r) => r[4] === at)
const index = { years: fullIndex.years, employers: [fullIndex.employers[at]], sources: Object.fromEntries([...new Set(allRows.map((r) => r[6]))].map((id) => [id, fullIndex.sources[id]])) }
const rows = allRows.map((r) => { const a = [...r]; a[4] = 0; return a })
const inputs = new Map(payload.inputs.map((p) => [p.path, readFileSync(resolve(root, p.path))]))
const readInput = (path) => inputs.get(path) ?? readFileSync(resolve(root, path))
const fixture = (which = 0) => ({ p: { ...structuredClone(payload), decisions: [structuredClone(payload.decisions[which])] }, rs: structuredClone(rows), ix: structuredClone(index) })
const run = (f, reader = readInput) => validateFollowThroughNameReview(f.p, f.rs, f.ix, root, { readInput: reader })
const alias = (f) => f.rs.find((r) => nameRecordFingerprint(r, f.ix) === f.p.decisions[0].proof.compiled.rowSha256)
const official = (f) => f.rs.find((r) => nameRecordFingerprint(r, f.ix) === f.p.decisions[0].proof.official.rowSha256)
const compiledRows = (f) => f.rs.filter((r) => f.ix.sources[r[6]].sourceKind === 'compiled' && f.ix.years[r[5]] === '2020/21')
const officialRows = (f) => f.rs.filter((r) => r[6] === 'rru-sofi-2021-22-employees')

// These tests exercise the real root-reviewed receipt and both223-row source cohorts.
test('all12 individually reviewed RRUsource spellings validate without changing observations', () => {
  const frozen = rows.map((r) => Object.freeze([...r]))
  assert.equal(validateFollowThroughNameReview(payload, frozen, index, root, { readInput }).length, 12)
  assert.deepEqual(frozen, rows)
  assert.equal(payload.decisions.filter((d) => d.queueMembership === 'original-3173').length, 11)
  assert.equal(payload.decisions.filter((d) => d.queueMembership === 'additional-source-copy').length, 1)
})

test('any new alias observation invalidates the complete livehistory pin', () => {
  const f = fixture(); const r = [...alias(f)]; r[2] += 1; f.rs.push(r)
  assert.throws(() => run(f), /alias or target observations changed/)
})

test('any new target observation in a later period invalidates the review', () => {
  const f = fixture(); const r = [...official(f)]; r[5] = f.ix.years.indexOf('2025/26'); r[2] += 100; f.rs.push(r)
  assert.throws(() => run(f), /alias or target observations changed/)
})

test('an existing target position change is stale even outside the witness year', () => {
  const f = fixture(); const target = f.p.decisions[0].proof.targetNameKey
  const r = f.rs.find((r) => r[0].toLowerCase().replaceAll(' ', '') === 'mittelman,robert' && r[6] !== 'rru-sofi-2021-22-employees')
  assert.ok(r, target); r[1] = 'Unreviewed new title'
  assert.throws(() => run(f), /alias or target observations changed/)
})

test('index offset changes preserve the semantic source and row fingerprints', () => {
  const f = fixture(); f.ix.employers.unshift(['Another', 'Other', null, 'another']); f.ix.years.unshift('1900/01')
  f.rs = f.rs.map((r) => { r[4] += 1; r[5] += 1; return r })
  assert.equal(run(f).length, 1)
})

test('missing expenses use remuneration uniqueness in BOTH cohorts, not a nullzero tuple', () => {
  const f = fixture(); assert.equal(f.p.decisions[0].proof.financialWitness.mode, 'unique-remuneration-only-missing-expense')
  assert.equal(alias(f)[3], null); assert.equal(official(f)[3], null); assert.equal(run(f).length, 1)
  f.p.decisions[0].proof.financialWitness.nullExpensesEqualZero = true
  assert.throws(() => run(f), /missing expenses are not zero/)
})

test('a second compiled pay occurrence blocks a missingexpense witness even with different expenses', () => {
  const f = fixture(); const extra = [...alias(f)]; extra[0] = 'Another, Employee'; extra[3] = 12345; f.rs.push(extra)
  const c = compiledRows(f); f.p.decisions[0].proof.cohorts.compiled = { rowCount: c.length, rowsSha256: nameRowsFingerprint(c, f.ix) }
  assert.throws(() => run(f), /no longer unique in both/)
})

test('a second official pay occurrence independently blocks a missingexpense witness', () => {
  const f = fixture(); const extra = [...official(f)]; extra[0] = 'Another, Employee'; extra[3] = 45678; f.rs.push(extra)
  const c = officialRows(f); f.p.decisions[0].proof.cohorts.official = { rowCount: c.length, rowsSha256: nameRowsFingerprint(c, f.ix) }
  assert.throws(() => run(f), /no longer unique in both/)
})

test('known expenses must match exactly and cannot silently fall back to pay alone', () => {
  const f = fixture(1); assert.equal(f.p.decisions[0].proof.financialWitness.mode, 'unique-remuneration-and-expenses')
  f.p.decisions[0].proof.financialWitness.mode = 'unique-remuneration-only-missing-expense'
  assert.throws(() => run(f), /Financial witness changed/)
})

test('changing a missing expense to numericzero invalidates the observation signature', () => {
  const f = fixture(); alias(f)[3] = 0
  assert.throws(() => run(f), /alias or target observations changed/)
})

test('even repinned nullzero metadata cannot fabricate a compiled source cell', () => {
  const f = fixture(); const r = alias(f); r[3] = 0; const p = f.p.decisions[0].proof
  p.compiled.rowSha256 = nameRecordFingerprint(r, f.ix); p.observations[0].rowsSha256 = nameRowsFingerprint([r], f.ix)
  const c = compiledRows(f); p.cohorts.compiled = { rowCount: c.length, rowsSha256: nameRowsFingerprint(c, f.ix) }; p.financialWitness.compiledExpensesCents = 0
  assert.throws(() => run(f), /retained compiled source observation changed/)
})

test('PDF, normalizeddata, fiscalperiod and currency source changes each invalidate the review', () => {
  for (const [field, value] of [['sha256', 'a'.repeat(64)], ['dataSha256', 'b'.repeat(64)], ['year', '2020/21'], ['periodStart', '2020-04-01'], ['currency', 'USD']]) {
    const f = fixture(); f.ix.sources['rru-sofi-2021-22-employees'][field] = value
    assert.throws(() => run(f), /source definition changed|source witness changed/, field)
  }
})

test('the actual witness page and the recorded sourcecopy page cannot drift', () => {
  const f = fixture(); f.p.decisions[0].proof.official.pdfPage += 1
  assert.throws(() => run(f), /row, page, year or currency witness changed/)
  const g = fixture(); g.p.decisions[0].proof.crop.pdfPage += 1
  assert.throws(() => run(g), /source crop, physical page/)
})

test('the compiled2020/21 and original2021/22 labels remain separately pinned', () => {
  const f = fixture(); assert.equal(f.p.decisions[0].proof.compiled.year, '2020/21'); assert.equal(f.p.decisions[0].proof.official.year, '2021/22')
  f.p.decisions[0].proof.periodReview.compiledYear = '2021/22'
  assert.throws(() => run(f), /period qualification changed/)
  const g = fixture(); g.p.decisions[0].proof.redateCompiledObservations = true
  assert.throws(() => run(g), /Incomplete individual/)
})

test('changed source pixels, page images and normalized data bytes cannot reuse old receipts', () => {
  for (const field of ['path', 'fullPagePath']) {
    const f = fixture(); const changed = f.p.decisions[0].proof.crop[field]
    assert.throws(() => run(f, (path) => path === changed ? Buffer.from('changed pixels') : readInput(path)), /input changed/)
  }
  const f = fixture(); const changed = f.p.decisions[0].proof.official.normalizedPath
  assert.throws(() => run(f, (path) => path === changed ? Buffer.from('changed data') : readInput(path)), /input changed/)
})

test('unreviewed or invented preferred names and canonical identities are rejected', () => {
  const f = fixture(); f.p.decisions[0].preferredName = 'Another, Person'; assert.throws(() => run(f), /Incomplete individual/)
  const g = fixture(); g.p.decisions[0].canonicalName = 'Invented complete identity'; assert.throws(() => run(g), /Incomplete individual/)
})

test('original candidateIDs and the extraFunklead cannot change queue membership', () => {
  const f = fixture(); f.p.decisions[0].candidateId = 'missing'; assert.throws(() => run(f), /candidate membership changed/)
  const g = fixture(11); assert.equal(g.p.decisions[0].candidateId, null); g.p.decisions[0].queueMembership = 'original-3173'
  assert.throws(() => run(g), /candidate id/)
})

test('duplicate aliases cannot acquire competing or repeated decisions', () => {
  const f = fixture(); f.p.decisions.push(structuredClone(f.p.decisions[0])); assert.throws(() => run(f), /Conflicting source-copy names/)
})

const cncPayload = JSON.parse(readFileSync(resolve(root, 'research/salaries/source-follow-through-2026-11-02/name-review-cnc.json')))
const cncLive = relevantRows.filter((r) => r[4] === cncAt)
const cncIndex = { years: fullIndex.years, employers: [fullIndex.employers[cncAt]], sources: Object.fromEntries([...new Set(cncLive.map((r) => r[6]))].map((id) => [id, fullIndex.sources[id]])) }
const cncRows = cncLive.map((r) => { const a = [...r]; a[4] = 0; return a })
const cncFixture = (which = 0) => ({ p: { ...structuredClone(cncPayload), decisions: [structuredClone(cncPayload.decisions[which])] }, rs: structuredClone(cncRows), ix: structuredClone(cncIndex) })

test('all6 CNC reviews use the same validator and preserve4original plus2extra membership', () => {
  assert.equal(validateFollowThroughNameReview(cncPayload, cncRows, cncIndex, root, { readInput }).length, 6)
  assert.equal(cncPayload.decisions.filter((d) => d.queueMembership === 'original-3173').length, 4)
  assert.equal(cncPayload.decisions.filter((d) => d.queueMembership === 'additional-source-copy').length, 2)
})

test('CNC Stuart-Clarke unknown source expense and compiled0 support only unique remuneration', () => {
  const d = cncPayload.decisions.find((d) => d.candidateId === '2022')
  assert.equal(d.proof.financialWitness.mode, 'unique-remuneration-only-missing-expense')
  assert.equal(d.proof.financialWitness.officialExpensesCents, null)
  assert.equal(d.proof.financialWitness.compiledExpensesCents, 0)
  assert.equal(d.proof.financialWitness.nullExpensesEqualZero, false)
  assert.equal(d.proof.financialWitness.compiledOccurrenceCount, 1)
  assert.equal(d.proof.financialWitness.officialOccurrenceCount, 1)
})

test('CNC ambiguous45-occurrence Maides and Rourke remain explicitly held', () => {
  assert.deepEqual(cncPayload.holds.map((d) => d.candidateId).sort(), ['1973', '1974'])
  assert.ok(!cncPayload.decisions.some((d) => ['1973', '1974'].includes(d.candidateId)))
  for (const official of [true, false]) {
    const count = cncRows.filter((r) => r[2] === 113947 && (official ? r[6] === 'cnc-sofi-2023-24-employees' : r[6] === 'pssdb-2026-10-22' && cncIndex.years[r[5]] === '2023/24')).length
    assert.equal(count, 45)
  }
})

test('both compressed r+n CNC spellings require their earlier native source crops', () => {
  const supported = cncPayload.decisions.filter((d) => d.proof.requiresEarlierNativeSpellingSupport)
  assert.equal(supported.length, 2)
  assert.deepEqual(supported.map((d) => d.preferredName).sort(), ['Cornelis, Suzanne', 'Thorne, Sandra'])
  const f = cncFixture(cncPayload.decisions.findIndex((d) => d.preferredName === 'Cornelis, Suzanne'))
  delete f.p.decisions[0].proof.supportingOriginals
  assert.throws(() => run(f), /Required earlier native spelling/)
})

test('earlier native CNC source pages and normalized rows cannot drift', () => {
  const which = cncPayload.decisions.findIndex((d) => d.preferredName === 'Thorne, Sandra')
  const f = cncFixture(which); f.p.decisions[0].proof.supportingOriginals[0].pdfPage += 1
  assert.throws(() => run(f), /row, page, year or currency witness changed/)
  const g = cncFixture(which); g.p.decisions[0].proof.supportingOriginals[0].pdfSha256 = 'a'.repeat(64)
  assert.throws(() => run(g), /Earlier native spelling source/)
})

test('generator check is read-only for ALL RRU/CNC outputs and works without upload scratchfiles', () => {
  const names = ['name-review-original-outcomes.json.gzip', 'name-review-overlay.json', 'review-results.json', 'held-pair-outcomes.csv', 'remaining-evidence.md', ...['rru', 'cnc'].flatMap((e) => [`name-review-${e}.json`, `name-review-${e}-observations.json.gzip`, `name-review-${e}.csv`])]
  const paths = names.map((n) => resolve(root, `research/salaries/source-follow-through-2026-11-02/${n}`))
  const before = paths.map((p) => [statSync(p).mtimeMs, readFileSync(p)])
  const result = spawnSync('python3', ['scripts/check_follow_through_name_replay.py', '--check', '--outcomes', '/nonexistent-review-upload.csv'], { cwd: root, encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
  paths.forEach((p, i) => { assert.equal(statSync(p).mtimeMs, before[i][0]); assert.deepEqual(readFileSync(p), before[i][1]) })
})


test('pinned native registry makes removing BOTH support fields or settingfalse invalid', () => {
  const which = cncPayload.decisions.findIndex((d) => d.preferredName === 'Cornelis, Suzanne')
  const f = cncFixture(which); delete f.p.decisions[0].proof.requiresEarlierNativeSpellingSupport; delete f.p.decisions[0].proof.supportingOriginals
  assert.throws(() => run(f), /Required earlier native spelling/)
  const g = cncFixture(which); g.p.decisions[0].proof.requiresEarlierNativeSpellingSupport = false
  assert.throws(() => run(g), /Required earlier native spelling/)
})


test('current overlay preserves exactly3173 original IDs, old confidence and separate3extra leads', () => {
  const base = JSON.parse(readFileSync(resolve(root, 'research/salaries/name-links/held-completion-2026-11-02/review-results.json')))
  const current = JSON.parse(readFileSync(resolve(root, 'research/salaries/source-follow-through-2026-11-02/review-results.json')))
  const metadata = JSON.parse(readFileSync(resolve(root, 'research/salaries/source-follow-through-2026-11-02/name-review-overlay.json')))
  assert.equal(current.length, 3173); assert.equal(base.length, 3173)
  const byId = new Map(current.map((r) => [r.id, r]))
  assert.equal(byId.size, 3173)
  for (const r of base) {
    const next = byId.get(r.id); assert.deepEqual(next.names, r.names); assert.equal(next.employer, r.employer); assert.equal(next.priorOutcome, r.outcome)
    if (r.outcome === 'connected-verified') assert.equal(next.outcome, 'connected-verified')
    if (r.outcome === 'connected-likely') assert.ok(['connected-verified', 'connected-likely'].includes(next.outcome))
  }
  assert.deepEqual(metadata.baseline.verified, 130); assert.equal(metadata.baseline.likely, 25); assert.equal(metadata.baseline.unconnected, 3018)
  assert.equal(metadata.current.verified, 145); assert.equal(metadata.current.likely, 25); assert.equal(metadata.current.unconnected, 3003)
  assert.equal(metadata.changedOriginalCandidates.length, 15); assert.ok(metadata.changedOriginalCandidates.every((r) => r.manualReview))
  assert.equal(metadata.additionalReviewedConnections.length, 3); assert.equal(metadata.usesUploadedOutcomeLabelsAsEvidence, false)
})

test('likely review CLI uses pinned semantic histories without whole-shard platform collation', () => {
  const path = resolve(root, 'research/salaries/source-follow-through-2026-11-02/likely-continuity.json')
  const before = readFileSync(path), time = statSync(path).mtimeMs
  const code = `process.argv.push('--check');
String.prototype.localeCompare = () => { throw new Error('Whole-shard platform collation must not run in the review CLI') };
await import('./scripts/review-baseline-likely-connections.mjs');`
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', code], { cwd: root, encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
  assert.deepEqual(readFileSync(path), before); assert.equal(statSync(path).mtimeMs, time)
})

test('review gzip outputs retain alternate encoding bytes only for exactly matching canonical payloads', () => {
  const code = `import gzip, importlib.util, pathlib, tempfile
spec=importlib.util.spec_from_file_location('review','scripts/review_follow_through_names.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
value={'name':'Same, Row','expenses':None,'pay':123.45}
payload=review.dumpbytes(value)+b'\\n'
changed=review.dumpbytes({**value,'pay':123.46})+b'\\n'
with tempfile.TemporaryDirectory() as tmp:
 path=pathlib.Path(tmp)/'snapshot.json.gzip'
 for level,mtime,osbyte in [(1,123456789,0),(5,123456790,3),(9,123456791,255)]:
  encoded=bytearray(gzip.compress(payload,compresslevel=level,mtime=mtime));encoded[9]=osbyte;encoded=bytes(encoded)
  assert gzip.decompress(encoded)==payload
  path.write_bytes(encoded)
  assert review.output_gzip(path,payload)==encoded
  review.write_gzip(path,value)
  assert path.read_bytes()==encoded
  replacement=review.output_gzip(path,changed)
  assert replacement!=encoded and gzip.decompress(replacement)==changed
  assert path.read_bytes()==encoded
`
  const result = spawnSync('python3', ['-c', code], { cwd: root, encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
})

test('changed canonical output payload remains stale in actual readonly review check', () => {
  const names = ['name-review-original-outcomes.json.gzip', ...['rru', 'cnc'].flatMap((e) => [`name-review-${e}.json`, `name-review-${e}-observations.json.gzip`, `name-review-${e}.csv`])]
  const paths = names.map((n) => resolve(root, `research/salaries/source-follow-through-2026-11-02/${n}`))
  const before = paths.map((p) => [statSync(p).mtimeMs, readFileSync(p)])
  const code = `import csv,gzip,json,pathlib,subprocess,tempfile
snapshot=json.loads(gzip.decompress(pathlib.Path('research/salaries/source-follow-through-2026-11-02/name-review-original-outcomes.json.gzip').read_bytes()))
rows=snapshot['rows'];rows[0]['next_action']+=' Changed canonical review payload.'
with tempfile.TemporaryDirectory() as tmp:
 path=pathlib.Path(tmp)/'changed-outcomes.csv'
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 result=subprocess.run(['python3','scripts/review_follow_through_names.py','--check','--outcomes',str(path)],capture_output=True,text=True)
 assert result.returncode!=0,result.stdout
 assert 'Name-review output is stale:' in result.stderr,result.stderr
 assert 'name-review-original-outcomes.json.gzip' in result.stderr,result.stderr
`
  const result = spawnSync('python3', ['-c', code], { cwd: root, encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
  paths.forEach((p, i) => { assert.equal(statSync(p).mtimeMs, before[i][0]); assert.deepEqual(readFileSync(p), before[i][1]) })
})
