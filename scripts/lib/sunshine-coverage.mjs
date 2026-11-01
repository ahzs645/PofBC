// Read the published salary exports, retaining the distinction between actual
// records, compiled edition labels and verified employer reporting periods.
import { readFileSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { createHash } from 'node:crypto'
import { gunzipSync } from 'node:zlib'
import { canonicalSlug, employerSlug } from './salary-employers.mjs'

export const EMPLOYEE_SCOPES = new Set(['employee-remuneration', 'named-employees-over-threshold'])
const OFFICIAL_KINDS = new Set(['official', 'official-pdf', 'official-open-data',
  'official-statement-of-financial-information', 'official-native-pdf', 'official-scanned-pdf',
  'official-board-remuneration-disclosure', 'official-pdf-ocr-overlay', 'official-hybrid-pdf'])
const sum = (values) => values.reduce((total, value) => total + value, 0)
const unique = (values) => [...new Set(values)].sort()
const common = (values) => values.length && values.every(value => value === values[0]) ? values[0] : null
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex')
const fail = (message) => { throw new Error(`Repository salary coverage: ${message}`) }
const integer = (value) => Number.isSafeInteger(value) && value >= 0

/** Fold spelling and punctuation only; keep city/district and other legal qualifiers. */
export function normalizeEmployerName(value) {
  return String(value ?? '').normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase()
    .replace(/\bb\s*\.\s*c\.?(?=\s|$)/g, 'bc').replace(/\bbritish columbia\b/g, 'bc')
    .replace(/\bschool board\b/g, 'school district').replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ')
}

/**
 * A match establishes employer identity only. It never proves equivalent annual
 * disclosure scope or reporting periods. Reviewed aliases may be keyed by the
 * exact external name or supplied as {externalName, repositorySlug, reason} rows.
 */
export function resolveEmployer(external, { employers, aliases = {} } = {}) {
  if (!Array.isArray(employers)) fail('resolver requires an employer list')
  const name = typeof external === 'string' ? external : external?.name ?? external?.employerName ?? ''
  const bySlug = new Map(employers.map(employer => [employer.slug, employer]))
  const alias = Array.isArray(aliases)
    ? aliases.find(row => row.externalName === name)
    : Object.hasOwn(aliases, name) ? aliases[name] : undefined
  if (alias !== undefined) {
    const slug = canonicalSlug(typeof alias === 'string' ? alias : alias?.slug ?? alias?.repositorySlug)
    if (!bySlug.has(slug)) fail(`reviewed alias for ${JSON.stringify(name)} points to unknown employer ${JSON.stringify(slug)}`)
    return { status: 'matched', slug, method: 'reviewed-alias', candidates: [slug], reason: alias?.reason ?? null }
  }
  const normalized = normalizeEmployerName(name)
  if (!normalized) return { status: 'unmatched', slug: null, method: null, candidates: [] }
  const candidates = new Set()
  for (const employer of employers) {
    if ([...(employer.names ?? []), employer.name, employer.slug].filter(Boolean)
      .some(value => normalizeEmployerName(value) === normalized)) candidates.add(employer.slug)
  }
  // Use the repository's reviewed canonical identity rules, never approximate
  // similarity or a stripped municipal prefix to choose an employer.
  // employerSlug historically discards parenthetical text. That is useful for
  // known stored aliases, but unsafe for a new external legal entity or unit.
  // Parenthetical variants must match a retained name or a reviewed alias.
  const slug = canonicalSlug(employerSlug(name))
  if (!/[()]/.test(name) && bySlug.has(slug)) candidates.add(slug)
  const list = [...candidates].sort()
  if (list.length === 1) return { status: 'matched', slug: list[0], method: 'repository-name-or-slug', candidates: list }
  return { status: list.length ? 'ambiguous' : 'unmatched', slug: null, method: null, candidates: list }
}

/** Load and reconcile every published employer export against both metadata files. */
export function loadRepositoryCoverage(root) {
  root = resolve(root)
  const inputs = []
  function bytes(path) {
    const absolute = join(root, path)
    const data = readFileSync(absolute)
    inputs.push({ path: relative(root, absolute).split('\\').join('/'), bytes: data.length, sha256: hash(data) })
    return data
  }
  function json(path) {
    const data = bytes(path)
    try { return JSON.parse(path.endsWith('.gzip') ? gunzipSync(data).toString('utf8') : data.toString('utf8')) }
    catch (error) { fail(`${path}: cannot decode JSON (${error.message})`) }
  }
  const index = json('public/salaries/index.json')
  const coverage = json('public/salaries/coverage.json')
  if (!Array.isArray(index.years) || !index.years.length || !index.sources || !Array.isArray(coverage.employers)) fail('missing years, sources or employer metadata')
  if (!coverage.output || !integer(coverage.output.rows) || !integer(coverage.officialRows) || !integer(coverage.legacyRowsRetained)) fail('missing published control totals')
  const labels = index.years.map(year => year.label)
  if (new Set(labels).size !== labels.length || labels.some(label => typeof label !== 'string')) fail('invalid or duplicate year labels')
  if (JSON.stringify(coverage.output.years) !== JSON.stringify(labels)) fail('index and coverage year catalogs differ')
  const sources = index.sources
  const seenSlugs = new Set()
  const employers = []
  for (const employer of [...coverage.employers].sort((a, b) => a.slug.localeCompare(b.slug))) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(employer.slug ?? '') || seenSlugs.has(employer.slug)) fail(`invalid or duplicate employer slug ${employer.slug}`)
    seenSlugs.add(employer.slug)
    if (!Array.isArray(employer.coverage) || employer.coverage.length !== labels.length) fail(`${employer.slug}: coverage length differs from year catalog`)
    const rows = json(`public/salaries/employers/${employer.slug}.json.gzip`)
    if (!Array.isArray(rows)) fail(`${employer.slug}: employer export is not an array`)
    const byYear = new Map()
    for (const [at, row] of rows.entries()) {
      if (!Array.isArray(row) || row.length < 6 || !integer(row[4]) || row[4] >= labels.length) fail(`${employer.slug}: invalid row or year index at row ${at + 1}`)
      if (!Number.isFinite(row[2])) fail(`${employer.slug}: nonnumeric remuneration at row ${at + 1}`)
      const source = sources[row[5]]
      if (!source) fail(`${employer.slug}: unknown source ${row[5]} at row ${at + 1}`)
      if (source.sourceKind !== 'compiled' && !OFFICIAL_KINDS.has(source.sourceKind)) fail(`${employer.slug}: unrecognized source kind ${source.sourceKind} for ${row[5]}`)
      if (!byYear.has(row[4])) byYear.set(row[4], new Map())
      const bySource = byYear.get(row[4])
      if (!bySource.has(row[5])) bySource.set(row[5], { sourceId: row[5], rows: 0, namedRows: 0, remunerationCents: 0, over75000Rows: 0, atLeast75000Rows: 0, atLeast100000Rows: 0 })
      const cohort = bySource.get(row[5])
      cohort.rows++
      if (row[0]) cohort.namedRows++
      cohort.remunerationCents += Math.round(row[2] * 100)
      if (row[2] > 75000) cohort.over75000Rows++
      if (row[2] >= 75000) cohort.atLeast75000Rows++
      if (row[2] >= 100000) cohort.atLeast100000Rows++
    }
    const periods = employer.coverage.map((entry, yearIndex) => {
      if (!integer(entry.rows) || !integer(entry.namedRows)) fail(`${employer.slug} ${labels[yearIndex]}: invalid metadata counts`)
      const cohorts = [...(byYear.get(yearIndex)?.values() ?? [])].sort((a, b) => a.sourceId.localeCompare(b.sourceId)).map(cohort => {
        const source = sources[cohort.sourceId]
        const official = OFFICIAL_KINDS.has(source.sourceKind)
        const periodType = source.periodType ?? 'unverified'
        const validDate = (value) => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)
          && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value
        const verifiedPeriod = official && ['fiscal', 'calendar'].includes(periodType)
          && validDate(source.periodStart) && validDate(source.periodEnd) && source.periodStart <= source.periodEnd
        return { ...cohort, sourceKind: source.sourceKind, official, scope: source.scope ?? 'unknown',
          employeeDisclosure: official && EMPLOYEE_SCOPES.has(source.scope),
          yearLabel: labels[yearIndex], periodType, periodStart: source.periodStart ?? null, periodEnd: source.periodEnd ?? null,
          periodEndYear: verifiedPeriod ? Number(source.periodEnd.slice(0, 4)) : null,
          verifiedPeriod, threshold: source.threshold ?? null, thresholdComparison: source.thresholdComparison ?? null,
          url: source.url ?? null, title: source.title ?? null, publicWarning: source.publicWarning ?? null,
          partialDisclosure: Boolean(source.partialDisclosure || source.completeEmployeeSchedule === false
            || source.validation?.completeEmployeeSchedule === false),
          completeEmployeeSchedule: source.completeEmployeeSchedule ?? source.validation?.completeEmployeeSchedule ?? null,
          validation: source.validation ?? null, notes: source.notes ?? [] }
      })
      const count = sum(cohorts.map(cohort => cohort.rows))
      const named = sum(cohorts.map(cohort => cohort.namedRows))
      if (count !== entry.rows || named !== entry.namedRows) fail(`${employer.slug} ${labels[yearIndex]}: export counts ${count}/${named} differ from metadata ${entry.rows}/${entry.namedRows}`)
      const declaredIds = unique(entry.sourceIds ?? [])
      const actualIds = cohorts.map(cohort => cohort.sourceId).sort()
      if (count && JSON.stringify(declaredIds) !== JSON.stringify(actualIds)) fail(`${employer.slug} ${labels[yearIndex]}: export source IDs differ from metadata`)
      return { yearIndex, yearLabel: labels[yearIndex], label: labels[yearIndex], labelType: index.years[yearIndex].periodType,
        status: entry.status, rows: count, namedRows: named,
        officialRows: sum(cohorts.filter(cohort => cohort.official).map(cohort => cohort.rows)),
        compiledRows: sum(cohorts.filter(cohort => !cohort.official).map(cohort => cohort.rows)),
        employeeRows: sum(cohorts.filter(cohort => cohort.employeeDisclosure).map(cohort => cohort.rows)),
        scope: entry.scope ?? null, periodType: common(cohorts.map(cohort => cohort.periodType)) ?? entry.periodType ?? 'unverified',
        periodStart: common(cohorts.map(cohort => cohort.periodStart)), periodEnd: common(cohorts.map(cohort => cohort.periodEnd)),
        sourceIds: declaredIds, cohorts, sourceLeads: entry.sourceLeads ?? [], notes: entry.notes ?? [] }
    })
    employers.push({ slug: employer.slug, name: employer.names?.[0] ?? employer.slug, names: employer.names ?? [], sector: employer.sector,
      rows: rows.length, namedRows: sum(periods.map(period => period.namedRows)),
      officialRows: sum(periods.map(period => period.officialRows)), compiledRows: sum(periods.map(period => period.compiledRows)),
      employeeRows: sum(periods.map(period => period.employeeRows)), periods,
      leads: (coverage.sourceCatalog ?? []).filter(source => source.employerSlug === employer.slug && source.status !== 'imported') })
  }
  const totals = { employers: employers.length, rows: sum(employers.map(employer => employer.rows)),
    namedRows: sum(employers.map(employer => employer.namedRows)), officialRows: sum(employers.map(employer => employer.officialRows)),
    compiledRows: sum(employers.map(employer => employer.compiledRows)), employeeRows: sum(employers.map(employer => employer.employeeRows)),
    availableEmployerYears: sum(employers.map(employer => employer.periods.filter(period => period.rows > 0).length)) }
  for (const key of ['employers', 'rows', 'namedRows', 'availableEmployerYears']) {
    if (totals[key] !== coverage.output[key]) fail(`${key} control mismatch: exports ${totals[key]}, published ${coverage.output[key]}`)
  }
  if (totals.officialRows !== coverage.officialRows || totals.compiledRows !== coverage.legacyRowsRetained) fail('official/compiled source totals do not reconcile')
  inputs.sort((a, b) => a.path.localeCompare(b.path))
  return { employers, years: index.years, sources, sourceCatalog: coverage.sourceCatalog ?? [], totals, inputs,
    inputsSha256: hash(JSON.stringify(inputs)) }
}
