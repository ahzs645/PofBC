import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

test('current Sunshine reports reproduce without reissuing archived comparison evidence', () => {
  const files = ['comparison.json', 'comparison.md', 'repository-employers.csv', 'work-queue.csv']
  const archived = files.map(file => readFileSync(resolve('research/salaries/sunshine-lists', file)))
  const out = mkdtempSync(join(tmpdir(), 'pofbc-current-sunshine-'))
  try {
    const result = spawnSync(process.execPath, ['scripts/audit-sunshine-lists.mjs', '--out', out], { encoding: 'utf8' })
    assert.equal(result.status, 0, result.stderr)
    files.forEach((file, i) => {
      assert.deepEqual(readFileSync(join(out, file)), readFileSync(resolve('research/salaries/current-preservation-2026-11-06/sunshine', file)))
      assert.deepEqual(readFileSync(resolve('research/salaries/sunshine-lists', file)), archived[i])
    })
  } finally { rmSync(out, { recursive: true, force: true }) }
})
