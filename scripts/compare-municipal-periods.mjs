// Prove cross-period compiled replacements from the accepted municipal originals.
// Exact name/pay multisets only; a partial overlap is a research finding, never a deletion.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs'
import { dirname, resolve, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gunzipSync } from 'node:zlib'
import { sha256 } from './lib/salary-data.mjs'
import { canonicalSlug } from './lib/salary-employers.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const research = join(root, 'research/salaries')
const json = (path) => JSON.parse(readFileSync(path, 'utf8'))
const baselineManifest = json(join(research, 'baseline-manifest.json'))
const baselineBytes = readFileSync(join(research, baselineManifest.file))
if (sha256(baselineBytes) !== baselineManifest.sha256) throw new Error('Baseline fingerprint mismatch')
const baseline = JSON.parse(gunzipSync(baselineBytes))
const directories = ['municipal-north', 'municipal-island', 'municipal-lower-mainland', 'municipal-small', 'municipal-ocr', 'sector-municipal', 'sector-government-police',
  ...json(join(research, 'collections.json')).collections.filter(name => name.startsWith('municipal-wave-') || name.startsWith('municipal-history-'))]
const official = new Map()
const fingerprints = []
for (const directory of directories) {
  const path = join(research, directory, 'sources.json')
  if (!existsSync(path)) throw new Error(`Municipal collection missing: ${directory}`)
  const manifest = json(path)
  for (const source of manifest.sources) {
    // Mixed-sector collections may contain fiscal or nonmunicipal schedules.
    if (directory === 'sector-government-police' && source.employerSlug !== 'metro-vancouver') continue
    if (!source.file || (source.status && !['verified', 'accepted', 'imported'].includes(source.status))) continue
    if (!/^\d{4}$/.test(source.year) || !source.employerSlug) throw new Error(`${source.id}: expected one municipality and a calendar year`)
    const bytes = readFileSync(join(research, directory, source.file))
    if (sha256(bytes) !== source.dataSha256) throw new Error(`${source.id}: source data hash mismatch`)
    const payload = JSON.parse(gunzipSync(bytes))
    const rows = Array.isArray(payload) ? payload : payload.rows
    const slug = canonicalSlug(source.employerSlug)
    if (!official.has(slug)) official.set(slug, new Map())
    const years = official.get(slug)
    if (!years.has(source.year)) years.set(source.year, [])
    years.get(source.year).push({ ...source, rows })
    fingerprints.push({ id: source.id, dataSha256: source.dataSha256 })
  }
}
// Preserve order of the disclosed name tokens. Do not expand initials, guess surnames,
// reverse first/last names, or join identities from outside the source documents.
const nameKey = (name) => String(name ?? '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '')
const rowKey = (row) => JSON.stringify([nameKey(row[0]), Math.round(row[2])])
const multiset = (rows) => {
  const counts = new Map()
  for (const row of rows) { const key = rowKey(row); counts.set(key, (counts.get(key) ?? 0) + 1) }
  return counts
}
const overlap = (a, b) => [...a].reduce((n, [key, count]) => n + Math.min(count, b.get(key) ?? 0), 0)
const elected = (position) => /^(?:mayor|councillor|councilor|council member)(?:$|\s*[·,/])/i.test(position ?? '')
const existingReplacements = new Set(json(join(research, 'vancouver/sources.json')).compiledReplacements.map(r => `${r.employerSlug}|${r.compiledYear}`))
// The build merges aliases before applying replacement rules. Preserve its row
// order while combining aliases here, so a rule cannot omit an older name of
// the same municipal employer (for example the two Langley City spellings).
const baselineBySlug = new Map()
for (const employer of baseline.employers) {
  const slug = canonicalSlug(employer.slug)
  if (!baselineBySlug.has(slug)) baselineBySlug.set(slug, [])
  baselineBySlug.get(slug).push(...employer.rows)
}
const findings = [], rules = []
for (const [slug, employerRows] of baselineBySlug) {
  const sourcesByYear = official.get(slug)
  if (!sourcesByYear) continue
  for (const [at, compiledYear] of baseline.years.entries()) {
    if (existingReplacements.has(`${slug}|${compiledYear}`)) continue
    const partition = employerRows.filter(r => r[4] === at)
    if (partition.length < 5) continue
    const retainedPositions = [...new Set(partition.filter(r => elected(r[1])).map(r => r[1]))]
    const modes = [{ name: 'all-published-cohorts', selected: partition, retainPositions: [], sources: () => true },
      { name: 'employee-cohort', selected: partition.filter(r => !retainedPositions.includes(r[1])), retainPositions: retainedPositions,
        sources: source => ['employee-remuneration', 'named-employees-over-threshold'].includes(source.category ?? source.scope) }]
    let chosen = null
    const comparisons = []
    for (const mode of modes) {
      if (mode.selected.length < 5 || mode.selected.some(r => !r[0])) continue
      const left = multiset(mode.selected)
      const matches = []
      for (const [year, allSources] of sourcesByYear) {
        const selectedSources = allSources.filter(mode.sources)
        if (!selectedSources.some(s => ['employee-remuneration', 'named-employees-over-threshold'].includes(s.category ?? s.scope))) continue
        const rows = selectedSources.flatMap(s => s.rows.map(r => r.slice(1, 5)))
        const same = overlap(left, multiset(rows))
        const result = { mode: mode.name, calendarYear: year, compiledRows: mode.selected.length, officialRows: rows.length,
          matchingNamePayRows: same, unmatchedCompiledRows: mode.selected.length - same,
          unmatchedOfficialRows: rows.length - same, sourceIds: selectedSources.map(s => s.id) }
        comparisons.push(result)
        if (same === mode.selected.length && selectedSources.every(s => s.completeEmployeeSchedule !== false && s.validation?.completeEmployeeSchedule !== false)) matches.push(result)
      }
      if (matches.length === 1) { chosen = { mode, match: matches[0] }; break }
    }
    const finding = { employerSlug: slug, compiledYear, status: chosen ? 'exact-contained-multiset-replacement' : 'unresolved-retained',
      compiledRows: partition.length, comparisons: comparisons.sort((a, b) => b.matchingNamePayRows - a.matchingNamePayRows || a.calendarYear.localeCompare(b.calendarYear)) }
    if (chosen) {
      const { mode, match } = chosen
      const retained = partition.filter(r => mode.retainPositions.includes(r[1]))
      const rule = { employerSlug: slug, compiledYear, replacementYear: match.calendarYear, sourceIds: match.sourceIds,
        sourceDataSha256: Object.fromEntries(match.sourceIds.map(id => [id, fingerprints.find(s => s.id === id).dataSha256])),
        retainPositions: mode.retainPositions, expectedRows: mode.selected.length, expectedRetainedRows: retained.length,
        selectedRowsSha256: sha256(JSON.stringify(mode.selected.map(r => r.slice(0, 4)))),
        reason: `Every one of the ${mode.selected.length} selected compiled name/remuneration observations is present, with multiplicity, in the independently dated calendar ${match.calendarYear} official schedule after documented comparison-only punctuation/case and whole-dollar normalization. Replace that proved cohort under its actual calendar period.`,
        evidence: 'municipal-corrections/comparison.json' }
      if (retained.length) rule.retainedSource = { id: `municipal-compiled-council-${slug}-${compiledYear.replace('/', '-')}`,
        title: `${slug} council rows retained from unverified compiled edition ${compiledYear}`, scope: 'elected-officials',
        notes: ['These compiled council observations are preserved. Matching the employee schedule does not establish the council reporting period or verify its values.'] }
      rules.push(rule)
      finding.replacement = { calendarYear: match.calendarYear, removedRows: mode.selected.length, retainedRows: retained.length }
    }
    findings.push(finding)
  }
}
const out = join(research, 'municipal-corrections')
mkdirSync(out, { recursive: true })
const report = { version: 1, reviewedOn: '2026-10-31', baselineSha256: baselineManifest.sha256, inputFingerprints: fingerprints,
  method: 'For each municipality and compiled partition, compare multiset counts of disclosed name and remuneration rounded with JavaScript Math.round to whole CAD dollars. Name normalization is NFKC, lowercase, and removal of punctuation/whitespace; token order is preserved and no given names or initials are inferred. Each selected compiled observation must occur in exactly one tested accepted calendar-year cohort. Source cents, expenses, names and titles are untouched on import. All source hashes and exact selected baseline row hashes are pinned. Partial matches never remove rows.',
  findings, summary: { comparedPartitions: findings.length, replacements: rules.length, replacedRows: rules.reduce((n, r) => n + r.expectedRows, 0),
    unresolvedPartitions: findings.filter(f => f.status === 'unresolved-retained').length } }
writeFileSync(join(out, 'comparison.json'), JSON.stringify(report, null, 2) + '\n')
writeFileSync(join(out, 'sources.json'), JSON.stringify({ version: 1, sources: [], compiledReplacements: rules,
  coverageNotes: ['Only complete, uniquely matched compiled cohorts are replaced across reporting-period labels. Partial overlaps remain explicitly unverified.'] }, null, 2) + '\n')
console.log(JSON.stringify(report.summary))
