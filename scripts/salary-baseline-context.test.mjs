import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { gzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'
import { salaryBaselineContext } from './lib/salary-baseline-context.mjs'
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex')
const zip = (value) => gzipSync(JSON.stringify(value) + '\n', { level: 9, mtime: 0 })
const original = ['Kim, Ada', 'Analyst', 100000, -5, 0, 0, 'old-source', 3]
const oldIndex = { years: ['2020/21'], employers: [['A', 'Government', null, 'a']], sources: { 'old-source': { currency: 'CAD' } }, shards: { ki: 1 } }
const current = { years: ['2019', '2020/21'], employers: [['New', 'Government', null, 'new'], ...oldIndex.employers], sources: { ...oldIndex.sources, 'new-source': { currency: 'CAD' } } }
const carried = [...original]; carried[4] = 1; carried[5] = 1
const extra = [...carried]; extra[2] = 150000; extra[6] = 'new-source'
const fixture = () => {
  const root = mkdtempSync(join(tmpdir(), 'salary-context-')), area = join(root, 'research/salaries/source-follow-through-2026-11-02')
  mkdirSync(area, { recursive: true })
  const index = Buffer.from(JSON.stringify(oldIndex) + '\n')
  writeFileSync(join(area, 'baseline-people-index.json.gzip'), gzipSync(index))
  writeFileSync(join(area, 'baseline.json.gzip'), zip({ baselinePeopleIndexSha256: hash(index), exportFiles: [{ path: 'public/salaries/people/ki.json.gzip', sha256: hash(zip([original])) }] }))
  return { root, index }
}

test('new observations and index shifts cannot change the byte-exact historical context', () => {
  const f = fixture()
  try {
    const context = salaryBaselineContext([carried, extra], current, f.root)
    assert.deepEqual(context.rows, [original])
    assert.deepEqual(context.readInput('public/salaries/people/index.json'), f.index)
    assert.deepEqual(context.readInput('public/salaries/people/ki.json.gzip'), zip([original]), 'the original newline and gzip encoding are preserved')
  } finally { rmSync(f.root, { recursive: true, force: true }) }
})

test('loss, duplication, value changes and provenance changes of old records fail closed', () => {
  const f = fixture()
  try {
    assert.throws(() => salaryBaselineContext([extra], current, f.root), /observations changed/)
    assert.throws(() => salaryBaselineContext([carried, carried, extra], current, f.root), /observations changed/)
    for (const at of [0, 1, 2, 3, 7]) {
      const changed = [...carried]; changed[at] = typeof changed[at] === 'number' ? changed[at] + 1 : `${changed[at]}X`
      assert.throws(() => salaryBaselineContext([changed, extra], current, f.root), /export differs|surname slice/)
    }
    const changed = structuredClone(current); changed.sources['old-source'].currency = 'USD'
    assert.throws(() => salaryBaselineContext([carried, extra], changed, f.root), /source definition changed/)
  } finally { rmSync(f.root, { recursive: true, force: true }) }
})
