#!/usr/bin/env node
// Offline, reproducible comparison of the saved OpenCompensation directory with
// the published employer exports and the immutable original compilation.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'
import { gunzipSync } from 'node:zlib'
import { loadRepositoryCoverage } from './lib/sunshine-coverage.mjs'
import { toCsv } from './lib/sunshine-compare.mjs'
import { canonicalSlug } from './lib/salary-employers.mjs'
import { aggregateSignatures, candidatePeriodLabels, compareOpenCompensation, validateOpenCompensationSnapshot } from './lib/opencompensation.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const base = join(root, 'research/salaries/opencompensation')
const options = { snapshot: join(base, 'observed-snapshot.json'), aliases: join(base, 'aliases.json'), out: base, check: false }
const args = process.argv.slice(2)
for (let at = 0; at < args.length; at++) {
  if (args[at] === '--check') { options.check = true; continue }
  if (args[at] === '--help') {
    console.log('Usage: node scripts/audit-opencompensation.mjs [--snapshot PATH] [--aliases PATH] [--out DIRECTORY] [--check]\nCompares saved evidence offline. Does not download or modify salary records. --check rejects stale committed reports.')
    process.exit(0)
  }
  if (!['--snapshot', '--aliases', '--out'].includes(args[at]) || !args[at + 1] || args[at + 1].startsWith('--')) throw new Error(`Invalid argument ${args[at]}`)
  options[args[at].slice(2)] = resolve(args[++at])
}
const sha = bytes => createHash('sha256').update(bytes).digest('hex')
const read = path => JSON.parse(readFileSync(path, 'utf8'))
const snapshotBytes = readFileSync(options.snapshot)
const snapshot = validateOpenCompensationSnapshot(JSON.parse(snapshotBytes))
const aliasBytes = readFileSync(options.aliases)
const aliases = JSON.parse(aliasBytes).aliases
if (!Array.isArray(aliases) || aliases.some(row => !row.reason?.trim() || !snapshot.employers.some(employer => employer.name === row.externalName))) throw new Error('Every alias needs an observed name and a review reason')
const repository = loadRepositoryCoverage(root)
// First resolve identities; then read only the candidate period/source slices.
const identities = compareOpenCompensation(snapshot, repository, { aliases })
const requested = new Map()
for (const row of identities.employers.filter(row => row.match.slug)) {
  if (!requested.has(row.match.slug)) requested.set(row.match.slug, new Set())
  for (const label of candidatePeriodLabels(row.reference.periodLabel)) requested.get(row.match.slug).add(label)
}
const publishedMetrics = new Map()
for (const [slug, labels] of requested) {
  const rows = JSON.parse(gunzipSync(readFileSync(join(root, 'public/salaries/employers', `${slug}.json.gzip`))))
  const groups = new Map()
  for (const row of rows) {
    const label = repository.years[row[4]].label
    if (!labels.has(label)) continue
    const key = `${slug}|${label}|${row[5]}`
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(row)
  }
  for (const [key, group] of groups) publishedMetrics.set(key, aggregateSignatures(group))
}
const manifestPath = join(root, 'research/salaries/baseline-manifest.json')
const manifest = read(manifestPath)
const baselineBytes = readFileSync(join(root, 'research/salaries', manifest.file))
if (sha(baselineBytes) !== manifest.sha256) throw new Error('Historical compilation fingerprint mismatch')
const baseline = JSON.parse(gunzipSync(baselineBytes))
const baselineGroups = new Map()
for (const employer of baseline.employers) {
  const slug = canonicalSlug(employer.slug)
  const labels = requested.get(slug)
  if (!labels) continue
  for (const row of employer.rows) {
    const label = baseline.years[row[4]]
    if (!labels.has(label)) continue
    const key = `${slug}|${label}`
    if (!baselineGroups.has(key)) baselineGroups.set(key, [])
    baselineGroups.get(key).push(row)
  }
}
const baselineMetrics = new Map([...baselineGroups].map(([key, rows]) => [key, aggregateSignatures(rows)]))
const report = compareOpenCompensation(snapshot, repository, { aliases, publishedMetrics, baselineMetrics })
report.fingerprints = { snapshotSha256: sha(snapshotBytes), aliasesSha256: sha(aliasBytes), repositoryInputsSha256: repository.inputsSha256,
  historicalCompilationSha256: manifest.sha256, historicalCompilationManifestSha256: sha(readFileSync(manifestPath)) }
report.repositoryInputs = repository.inputs
report.historicalCompilationNotes = manifest.notes

const fmt = value => value == null ? '—' : Number(value).toLocaleString('en-CA')
const md = value => String(value ?? '—').replaceAll('|', '\\|').replaceAll('\n', ' ')
const sourceCounts = row => row.candidates.map(period => `${period.yearLabel}: ${period.cohorts.map(cohort => `${cohort.rows} ${cohort.scope}${cohort.sourceKind === 'compiled' ? '' : ' (official)'}`).join(' + ')}`).join('; ')
const diagnostic = row => row.originalCompilation?.matchingAggregateDefinitions.includes('remunerationPlusKnownExpenses')
  ? row.originalCompilation.matchingAggregateDefinitions.includes('remuneration') ? 'Both measures reproduce the three aggregates' : 'Remuneration + expenses reproduces the three aggregates'
  : row.originalCompilation?.matchingAggregateDefinitions.includes('remunerationPlusKnownExpensesForPositiveRemuneration') ? 'Positive remuneration rows + expenses reproduce the three aggregates'
    : row.originalCompilation?.matchingAggregateDefinitions.includes('remuneration') ? 'Remuneration reproduces the three aggregates' : 'No matching compilation signature'
const summary = report.summary
const examples = ['public-service', 'bc-hydro', 'northern-health', 'vancouver-police', 'bc-financial-services-authority', 'bc-infrastructure-benefits']
  .map(slug => report.employers.find(row => row.match.slug === slug && row.reference.periodLabel === '2023-2024')).filter(Boolean)
const lines = [
  '# OpenCompensation comparison', '',
  `Observed ${snapshot.source.retrievedAt}. Status: **${report.status}**.`, '',
  `The [published employer directory](${snapshot.source.url}) contains **${summary.referencePublishedNames} published names** selected by its minimum of 15 positive compensation records and latest period per name. **${summary.matchedPublishedNames} names map to ${summary.uniqueMappedRepositoryEmployers} PofBC employer IDs**; ${summary.unmatchedPublishedNames} are unmatched and ${summary.ambiguousPublishedNames} are ambiguous. Employer IDs are the repository's identities, not an independent legal-entity census.`, '',
  `The comparison reconciles **${fmt(summary.repository.rows)} PofBC disclosure observations**, including **${fmt(summary.repository.officialRows)} official-source observations** and **${fmt(summary.repository.compiledRows)} compiled observations**, across **${summary.repository.employers} employers** and **${summary.repository.availableEmployerYears} populated employer/periods**. These totals span different years and scopes from the external table and are not subtracted.`, '',
  snapshot.datasetSummary ? `The saved site coverage statement reports **${fmt(snapshot.datasetSummary.bcLatestPeriodRecords)} B.C. salary records** under **${md(snapshot.datasetSummary.bcLatestPeriodLabel)}**. Its national record total also includes other provinces and physician-payment datasets. The B.C. latest snapshot does not imply continuous annual coverage.` : '', '',
  '## What the arithmetic comparison establishes', '',
  `For **${summary.namesWithOriginalCompilationAggregateMatch} of ${summary.referencePublishedNames} entries**, the record count, rounded mean and rounded maximum can be reproduced from PofBC's immutable historical compilation. **${summary.namesMatchingCompilationOnlyWhenExpensesAdded}** reproduce those three values only after reported expenses are added to remuneration. This is evidence of aggregate similarity and a measure-definition problem; it does **not** prove row-level equality or common provenance.`, '',
  `For **${summary.namesMatchingOnlyWithPositiveRemunerationFilter}** of those entries, reproduction also requires selecting positive-remuneration rows before adding expenses. Expense-only rows change the denominator under the other diagnostic. These are tested arithmetic interpretations, not verified site-wide selection rules.`, '',
  'The immutable compilation contains retained original input, including data later replaced or held. Its period labels remain unverified. A matching signature never restores those historical rows or elevates them to official evidence.', '',
  '## Examples requiring source and period review', '',
  '| Published name | External label | External records | Candidate PofBC source counts | Historical compilation diagnostic |',
  '| --- | --- | ---: | --- | --- |',
  ...examples.map(row => `| [${md(row.reference.name)}](${row.reference.url}) | ${row.reference.periodLabel} | ${fmt(row.reference.recordCount)} | ${md(sourceCounts(row))} | ${diagnostic(row)} |`), '',
  'Candidate counts preserve official employee, board, appointee and compiled scopes separately. An official schedule plus a retained compiled copy can represent overlapping evidence. A directory label alone cannot establish that either corresponds to the external rows. The JSON contains each original source URL, actual dates, threshold rule, source warnings and monetary diagnostics.', '',
  '## All observed directory entries', '',
  '| Published employer name | External period label | External positive records | PofBC employer ID | Compilation aggregate match |',
  '| --- | --- | ---: | --- | --- |',
  ...report.employers.map(row => `| [${md(row.reference.name)}](${row.reference.url}) | ${row.reference.periodLabel} | ${fmt(row.reference.recordCount)} | ${md(row.match.slug ?? row.match.status)} | ${diagnostic(row)} |`), '',
  '## Interpretation and follow-up', '',
  ...report.limitations.map(value => `- ${value}`), '',
  'For a discrepancy, obtain the exact originating employer report, verify its reporting dates and compensation definition, then reconcile individual rows and source controls. The existing source queue remains the route for accepting salary additions. A count difference, matching name or matching mean is insufficient.', '',
  'The separate [PSA-2024-42006 workforce companion](../workforce/README.md) adds the all-employee and Victoria-office aggregate series. It is excluded from employee-record totals and from the Public Accounts FTE series.', '',
  '## Reproduce', '',
  '```sh', 'npm run audit:opencompensation', 'npm run check:opencompensation', '```', '',
  '[Detailed comparison](comparison.json) · [Directory comparison CSV](comparison.csv) · [Observed input](observed-snapshot.json) · [Methods and source findings](README.md)', '',
  `Repository salary input SHA-256: \`${report.fingerprints.repositoryInputsSha256}\`.`,
  `Saved directory input SHA-256: \`${report.fingerprints.snapshotSha256}\`.`, ''
]
const csvRows = report.employers.map(row => ({
  publishedName: row.reference.name, externalPeriodLabel: row.reference.periodLabel, externalPositiveRecords: row.reference.recordCount,
  externalAverageCompensation: row.reference.averageCompensation, externalHighestCompensation: row.reference.highestCompensation,
  externalUrl: row.reference.url, repositorySlug: row.match.slug, identityStatus: row.match.status, comparisonStatus: row.status,
  candidateSourceCounts: sourceCounts(row), compilationAggregateMatches: row.originalCompilation?.matchingAggregateDefinitions ?? [],
  referencePeriodVerified: false, recordLevelParityChecked: false
}))
const outputs = {
  'comparison.json': JSON.stringify(report, null, 2) + '\n',
  'comparison.md': lines.join('\n'),
  'comparison.csv': toCsv(csvRows, Object.keys(csvRows[0] ?? {}))
}
if (!options.check) mkdirSync(options.out, { recursive: true })
for (const [file, content] of Object.entries(outputs)) {
  const path = join(options.out, file)
  if (options.check) {
    if (readFileSync(path, 'utf8') !== content) throw new Error(`${file} is stale; rerun npm run audit:opencompensation`)
  } else writeFileSync(path, content)
}
console.log(JSON.stringify({ status: report.status, ...summary, output: options.out, checked: options.check }, null, 2))
