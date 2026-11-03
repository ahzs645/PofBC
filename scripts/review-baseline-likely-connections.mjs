// Build/check the11 approved likely continuity guards without writing salary/name exports.
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { gunzipSync } from 'node:zlib'
import { BASELINE_LIKELY_PAIRS, createBaselineLikelyConnections, validateBaselineLikelyConnections } from './lib/baseline-likely-connections.mjs'
const root = resolve(import.meta.dirname, '..'), area = 'research/salaries/source-follow-through-2026-11-02'
const index = JSON.parse(readFileSync(resolve(root, 'public/salaries/people/index.json')))
const baselineIndex = JSON.parse(gunzipSync(readFileSync(resolve(root, area, 'baseline-people-index.json.gzip'))))
const path = resolve(root, area, 'likely-continuity.json'), committedBytes = readFileSync(path)
const committed = JSON.parse(committedBytes)
const oldEmployers = new Map(baselineIndex.employers.map((e, i) => [e[3], i])), oldYears = new Map(baselineIndex.years.map((y, i) => [y, i]))
const wantedShards = [...new Set(BASELINE_LIKELY_PAIRS.map(([key]) => key.split('|')[0].slice(0, 2)))]
const rows = [], oldRows = []
for (const shard of wantedShards) {
  const current = JSON.parse(gunzipSync(readFileSync(resolve(root, `public/salaries/people/${shard}.json.gzip`))))
  rows.push(...current)
  const previous = current.filter((r) => baselineIndex.sources[r[6]]).map((r) => {
    const copy = [...r]; copy[4] = oldEmployers.get(index.employers[r[4]][3]); copy[5] = oldYears.get(index.years[r[5]])
    if (copy[4] == null || copy[5] == null) throw new Error('Original history moved employer or year')
    return copy
  })
  oldRows.push(...previous)
}
// Validate the committed endpoint, whole-family and source-definition pins first.
// Whole-export byte replay remains the financial build's separate baseline gate;
// this review CLI is independent of platform collation and gzip encodings.
const baseline = { rows: oldRows, index: baselineIndex }
validateBaselineLikelyConnections(committed, rows, index, baseline, root)
const payload = createBaselineLikelyConnections(rows, index, baseline, root)
const bytes = Buffer.from(JSON.stringify(payload, null, 2) + '\n')
if (process.argv.includes('--check')) {
  if (!committedBytes.equals(bytes)) throw new Error('Likely continuity receipt changed; review again')
} else writeFileSync(path, bytes)
console.log(`baseline likely continuity: ${payload.decisions.length} unchanged assumptions; full surname-family histories pinned`)
