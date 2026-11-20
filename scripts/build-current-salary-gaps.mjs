// Refresh current coverage without rewriting the dated municipal audit.
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { canonicalSlug } from './lib/salary-employers.mjs'

export function summarizeSalaryGaps(index, roster, asOf) {
  const employers = new Map(index.employers.map((entry) => [entry.slug, entry]))
  const reports = (entry, predicate) => index.years.filter((_, i) =>
    (entry?.counts[i] ?? 0) > 0 && entry.coverage[i]?.sourceIds.some((id) => {
      const source = index.sources[id]
      if (!source) throw new Error(`Unknown salary source: ${id}`)
      return /^official(?:-|$)/.test(source.sourceKind) && predicate(source)
    }),
  )
  const hasEmployeeRecords = (source) => ['employee-remuneration', 'named-employees-over-threshold'].includes(source.scope)
  const districtRows = index.employers.filter((entry) => entry.sector === 'School districts').map((entry) => ({
    slug: entry.slug, name: entry.names[0], officialYears: reports(entry, () => true),
  }))
  const active = roster.municipalities.filter((entry) => entry.status !== 'pending-incorporation' ||
    (entry.effectiveFrom && entry.effectiveFrom <= asOf))
  const municipalRows = active.map(({ employerSlug, municipality, effectiveFrom }) => {
    const entry = employers.get(canonicalSlug(employerSlug))
    return {
      slug: canonicalSlug(employerSlug), municipality, ...(effectiveFrom ? { incorporated: effectiveFrom } : {}),
      hasRecords: entry?.counts.some((count) => count > 0) ?? false,
      hasOfficialRecords: reports(entry, () => true).length > 0,
      hasOfficialEmployeeRecords: reports(entry, hasEmployeeRecords).length > 0,
    }
  })
  return {
    recordCounts: index.recordCounts,
    schoolDistricts: {
      total: districtRows.length,
      soleOfficialYear2024_25: districtRows.filter(({ officialYears }) => officialYears.length === 1 && officialYears[0] === '2024/25').length,
      districts: districtRows,
    },
    municipalities: {
      total: municipalRows.length,
      withRecords: municipalRows.filter((row) => row.hasRecords).length,
      withOfficialRecords: municipalRows.filter((row) => row.hasOfficialRecords).length,
      withOfficialEmployeeRecords: municipalRows.filter((row) => row.hasOfficialEmployeeRecords).length,
      withoutRecords: municipalRows.filter((row) => !row.hasRecords).map(({ slug, municipality, incorporated }) => ({
        slug, municipality, ...(incorporated ? { incorporated } : {}),
      })),
    },
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const read = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'))
  const index = read('../public/salaries/employers/index.json')
  const roster = read('../research/salaries/municipal-audit/roster.json')
  const args = process.argv.slice(2)
  const value = args.find((arg) => arg.startsWith('--as-of='))
  const asOf = value?.slice('--as-of='.length) ?? new Date().toISOString().slice(0, 10)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(asOf) || args.some((arg) => arg !== value && arg !== '--check')) {
    throw new Error('Usage: node scripts/build-current-salary-gaps.mjs [--check] [--as-of=YYYY-MM-DD]')
  }
  const out = new URL('../research/salaries/current-coverage-gaps.json', import.meta.url)
  const text = JSON.stringify(summarizeSalaryGaps(index, roster, asOf), null, 2) + '\n'
  if (args.includes('--check')) {
    if (readFileSync(out, 'utf8') !== text) throw new Error('Current salary gaps have drifted. Regenerate this report.')
  } else {
    writeFileSync(out, text)
  }
}
