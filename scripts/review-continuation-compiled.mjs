// Compare the new official cohorts to the immutable pre-pass compiled exports.
// This report makes no deletion, period repair, identity join or scope decision.
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { execFileSync } from 'node:child_process'
import { gunzipSync } from 'node:zlib'
import { canonicalSlug } from './lib/salary-employers.mjs'
import { sha256 } from './lib/salary-data.mjs'

const root = resolve(import.meta.dirname, '..')
const research = join(root, 'research/salaries')
const out = join(research, 'continuation-2026-11-01')
const read = (path) => JSON.parse(readFileSync(path, 'utf8'))
const baseline = read(join(out, 'baseline.json'))
const name = (value) => String(value ?? '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '')
const key = (row, mode) => mode === 'exact' ? JSON.stringify(row.slice(0, 4)) : JSON.stringify([name(row[0]), mode === 'whole' ? Math.round(row[2]) : row[2]])
const counts = (rows, mode) => rows.reduce((map, row) => map.set(key(row, mode), (map.get(key(row, mode)) ?? 0) + 1), new Map())
const overlap = (left, right, mode) => {
  const target = counts(right, mode)
  return [...counts(left, mode)].reduce((sum, [value, n]) => sum + Math.min(n, target.get(value) ?? 0), 0)
}
const official = new Map()
const load = (collection) => {
  for (const source of read(join(research, collection, 'sources.json')).sources) {
    if (!source.file || (source.status && !['accepted', 'verified', 'imported'].includes(source.status))) continue
    const slug = canonicalSlug(source.employerSlug)
    const raw = readFileSync(join(research, collection, source.file))
    if (sha256(raw) !== source.dataSha256) throw new Error(source.id + ': data hash mismatch')
    const payload = JSON.parse(gunzipSync(raw)); const rows = Array.isArray(payload) ? payload : payload.rows
    if (!official.has(slug)) official.set(slug, new Map())
    if (!official.get(slug).has(source.year)) official.get(slug).set(source.year, { rows: [], sources: [] })
    const group = official.get(slug).get(source.year)
    group.rows.push(...rows.map((row) => row.slice(1, 5)))
    group.sources.push({ id: source.id, collection, scope: source.category ?? source.scope, dataSha256: source.dataSha256, sourceSha256: source.sha256, retainCompiledPartition: source.retainCompiledPartition ?? false, completeEmployeeSchedule: source.completeEmployeeSchedule ?? source.validation?.completeEmployeeSchedule ?? null })
  }
}
for (const entry of readdirSync(research, { withFileTypes: true })) {
  if (!entry.isDirectory() || !entry.name.startsWith('continuation-')) continue
  if (existsSync(join(research, entry.name, 'sources.json'))) load(entry.name)
  for (const sub of readdirSync(join(research, entry.name), { withFileTypes: true })) {
    if (sub.isDirectory() && existsSync(join(research, entry.name, sub.name, 'sources.json'))) load(`${entry.name}/${sub.name}`)
  }
}
const findings = []
for (const [slug, periods] of official) {
  if (!baseline.employers.some((employer) => employer.slug === slug)) continue
  const bytes = execFileSync('git', ['show', `${baseline.repositoryCommit}:public/salaries/employers/${slug}.json.gzip`], { cwd: root, maxBuffer: 32 * 1024 * 1024 })
  const old = JSON.parse(gunzipSync(bytes)).filter((row) => baseline.sources[row[5]]?.sourceKind === 'compiled' || baseline.sources[row[5]]?.scope === 'compiled-unverified')
  for (const year of new Set(old.map((row) => baseline.years[row[4]]))) {
    // Calendar shifts are separately compared by the established municipal review.
    if (!periods.has(year) || !year.includes('/')) continue
    const selected = old.filter((row) => baseline.years[row[4]] === year)
    const comparisons = [...periods].map(([officialYear, group]) => ({ officialYear, officialRows: group.rows.length, exactFourFieldMatches: overlap(selected, group.rows, 'exact'), namePayMatches: overlap(selected, group.rows, 'cents'), nameRoundedPayMatches: overlap(selected, group.rows, 'whole'), sourceInputs: group.sources }))
      .sort((a, b) => b.nameRoundedPayMatches - a.nameRoundedPayMatches || a.officialYear.localeCompare(b.officialYear))
    findings.push({ employerSlug: slug, compiledYear: year, compiledRows: selected.length, compiledExportSha256: sha256(bytes), positionCounts: Object.fromEntries([...new Set(selected.map((row) => row[1]))].map((position) => [String(position), selected.filter((row) => row[1] === position).length])), comparisons, decision: 'Parent must review actual reporting periods and employee/board scope. This comparison does not authorize deletion.' })
  }
}
writeFileSync(join(out, 'compiled-comparison.json'), JSON.stringify({ version: 1, baselineCommit: baseline.repositoryCommit, method: 'Full multiset comparison preserving multiplicity. Name tokens retain order, case/punctuation are set aside; rounded-pay comparison uses Math.round to whole dollars. No initial expansion, aliases, expenses-as-zero or identity claims.', findings }, null, 2) + '\n')
for (const finding of findings) console.log(JSON.stringify({ employer: finding.employerSlug, compiledYear: finding.compiledYear, compiledRows: finding.compiledRows, best: finding.comparisons.slice(0, 2).map((row) => ({ year: row.officialYear, officialRows: row.officialRows, namePayMatches: row.namePayMatches, roundedMatches: row.nameRoundedPayMatches })) }))
