#!/usr/bin/env node
// Offline comparison. Obtaining an authorized reference snapshot is a separate
// step; this command never scrapes Sunshine Lists or imports salary records.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve, dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadRepositoryCoverage } from './lib/sunshine-coverage.mjs'
import { normalizeSunshineSnapshot } from './lib/sunshine-lists.mjs'
import { buildSunshineComparison, compareReportChanges, renderSunshineReport, toCsv, QUEUE_FIELDS, EMPLOYER_FIELDS } from './lib/sunshine-compare.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const base = join(root, 'research/salaries/sunshine-lists')
const options = { snapshot: join(base, 'observed-snapshot.json'), aliases: join(base, 'aliases.json'), out: base, previous: null, requireComplete: false }
const args = process.argv.slice(2)
const help = `Compare an authorized Sunshine Lists snapshot with all published PofBC salary exports.

Usage: node scripts/audit-sunshine-lists.mjs [options]
  --snapshot PATH       Normalized JSON snapshot (default: committed observed snapshot)
  --aliases PATH        Reviewed employer aliases JSON
  --out DIRECTORY       Output comparison.json, comparison.md and CSV inventories
  --previous PATH       Previous comparison.json; include changes in the new report
  --require-complete    Exit 2 after writing reports if the reference directory is incomplete
  --help                Show this help

No network requests or salary imports are performed. Incomplete and summary-only
snapshots remain explicitly incomplete; equal counts do not prove record equality.
`
for (let i = 0; i < args.length; i++) {
  const arg = args[i]
  if (arg === '--help') { console.log(help); process.exit(0) }
  if (arg === '--require-complete') { options.requireComplete = true; continue }
  if (['--snapshot', '--aliases', '--out', '--previous'].includes(arg)) {
    if (!args[i + 1] || args[i + 1].startsWith('--')) throw new Error(`${arg} requires a path`)
    options[arg.slice(2)] = resolve(args[++i]); continue
  }
  throw new Error(`Unknown option ${arg}; use --help`)
}

const read = path => JSON.parse(readFileSync(path, 'utf8'))
const snapshot = normalizeSunshineSnapshot(read(options.snapshot))
const aliasFile = read(options.aliases)
const aliases = aliasFile.aliases ?? aliasFile
const previous = options.previous ? read(options.previous) : null
const repository = loadRepositoryCoverage(root)
const report = buildSunshineComparison(snapshot, repository, aliases)
if (previous) report.changes = compareReportChanges(previous, report)
mkdirSync(options.out, { recursive: true })
writeFileSync(join(options.out, 'comparison.json'), JSON.stringify(report, null, 2) + '\n')
writeFileSync(join(options.out, 'comparison.md'), renderSunshineReport(report))
writeFileSync(join(options.out, 'repository-employers.csv'), toCsv(report.repositoryEmployers, EMPLOYER_FIELDS))
writeFileSync(join(options.out, 'work-queue.csv'), toCsv(report.queue, QUEUE_FIELDS))
console.log(JSON.stringify({ status: report.status, ...report.summary, output: options.out }, null, 2))
if (options.requireComplete && !report.summary.directoryComplete) {
  console.error('Reference directory is incomplete. Reports were written with that limitation; no completeness pass is possible.')
  process.exitCode = 2
}
