// A small companion to the existing published employer exports. Those exports stay untouched.
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { gzipSync, gunzipSync } from 'node:zlib'
import { gzipContentMatches } from './lib/gzip-content.mjs'
import { buildEmployerStats } from '../src/salaries/employerStats.js'

const root = new URL('../public/salaries/', import.meta.url)
const index = JSON.parse(readFileSync(new URL('employers/index.json', root), 'utf8'))
const employers = Object.fromEntries(index.employers.map(({ slug }) => {
  const rows = JSON.parse(gunzipSync(readFileSync(new URL(`employers/${slug}.json.gzip`, root))))
  return [slug, buildEmployerStats(rows, { slug, years: index.years, sources: index.sources })]
}))
const result = {
  schemaVersion: 1, years: index.years,
  note: 'CAD remuneration in official annual employee schedules only. Excludes compiled editions, incomplete schedules, executives, boards and council. Each cell has one disclosure definition. Counts are records, not employee headcount. Growth requires adjacent annual periods with matching scope, threshold and boundary rule, unique disclosed names, and at least 10 records at both ends. Latest periods differ between employers.',
  employers
}
const target = new URL('employer-stats.json.gzip', root)
const payload = JSON.stringify(result) + '\n'
const current = existsSync(target) && gzipContentMatches(readFileSync(target), payload)
if (process.argv.includes('--check')) {
  if (!current) throw new Error('Published employer statistics are stale; run npm run build:employer-stats')
} else if (!current) writeFileSync(target, gzipSync(payload, { level: 9 }))
console.log(`Employer statistics: ${Object.values(employers).filter((cells) => cells.length).length} employers, ${Object.values(employers).reduce((sum, cells) => sum + cells.length, 0)} annual periods → ${fileURLToPath(target)}`)
