import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { gunzipSync, gzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'
import { surnameShard } from '../../src/salaries/people.js'

const digest = (data) => createHash('sha256').update(data).digest('hex')
const area = 'research/salaries/source-follow-through-2026-11-02'

/** Reconstruct prior named exports from unchanged original source IDs, never from new rows.
 * Old review receipts stay immutable. Every reconstructed byte must match its release pin.
 */
export const salaryBaselineContext = (rows, index, root) => {
  const manifest = JSON.parse(gunzipSync(readFileSync(join(root, area, 'baseline.json.gzip'))))
  const bytes = gunzipSync(readFileSync(join(root, area, 'baseline-people-index.json.gzip')))
  if (digest(bytes) !== manifest.baselinePeopleIndexSha256) throw new Error('Historical people index changed')
  const baseline = JSON.parse(bytes)
  for (const [id, source] of Object.entries(baseline.sources)) {
    if (JSON.stringify(source) !== JSON.stringify(index.sources[id])) throw new Error(`Prior source definition changed: ${id}`)
  }
  const employers = new Map(baseline.employers.map((e, at) => [e[3], at]))
  const years = new Map(baseline.years.map((year, at) => [year, at]))
  const shards = new Map(Object.keys(baseline.shards).map((shard) => [shard, []]))
  for (const row of rows) {
    if (!baseline.sources[row[6]]) continue
    const employer = employers.get(index.employers[row[4]][3]), year = years.get(index.years[row[5]])
    if (employer == null || year == null) throw new Error('An original observation moved employer or period')
    const copy = [...row]; copy[4] = employer; copy[5] = year
    const shard = surnameShard(row[0])
    if (!shards.has(shard)) throw new Error('An original observation acquired a new surname slice')
    shards.get(shard).push(copy)
  }
  const files = new Map([['public/salaries/people/index.json', bytes]])
  const expected = new Map(manifest.exportFiles.map((p) => [p.path, p.sha256]))
  for (const [shard, list] of shards) {
    if (list.length !== baseline.shards[shard]) throw new Error(`Original named observations changed: ${shard}`)
    list.sort((a, b) => a[0].localeCompare(b[0]) || a[5] - b[5] || b[2] - a[2] || a[4] - b[4])
    const path = `public/salaries/people/${shard}.json.gzip`
    const bytes = gzipSync(JSON.stringify(list) + '\n', { level: 9, mtime: 0 })
    if (digest(bytes) !== expected.get(path)) throw new Error(`Original named export differs: ${shard}`)
    files.set(path, bytes)
  }
  return { rows: [...shards.values()].flat(), index: baseline,
    readInput: (path) => files.get(path) ?? readFileSync(join(root, path)) }
}
