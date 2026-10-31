// Rebuild every salary view from an immutable legacy snapshot plus verified official schedules.
// Run npm run build:salaries. Optional legacy CSV input: npm run build:salaries -- <folder holding data/>.
// Importers download public reports separately; this build is deterministic and needs no network.
import { readFileSync, readdirSync, statSync, writeFileSync, mkdirSync, rmSync, renameSync, existsSync, mkdtempSync } from 'node:fs'
import { resolve, dirname, join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gzipSync, gunzipSync } from 'node:zlib'
import { surnameShard } from '../src/salaries/people.js'
import { titleKey, titleShard } from '../src/salaries/positions.js'
import { pooledGrowth, stayerRaises, typicalRaise } from '../src/salaries/growth.js'
import { BODIES, EMPLOYER_ALIASES, canonicalSlug, employerSector, employerSlug, sectorOf } from './lib/salary-employers.mjs'
import { periodMean, TOP_PER_PERIOD, topRecords, csvRows, money, median, sha256, yearSlug, reportingPeriodType, applyCompiledReplacements, applyTravelJoinCorrections, sumMoney, duplicateStats, repeatedCandidates, validateRow, validateReplacementScopes } from './lib/salary-data.mjs'
import { sourceCatalog, sourceLeadsFor, hasLocatedSource } from './lib/salary-sources.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const args = process.argv.slice(2)
const option = (name, fallback) => { const at = args.indexOf(name); return at < 0 ? fallback : args[at + 1] }
const out = resolve(option('--out', join(root, 'public/salaries')))
const indexPath = resolve(option('--index-out', args.includes('--out') ? join(dirname(out), 'salaryIndex.js') : join(root, 'src/government/salaryIndex.js')))
const research = resolve(option('--research', join(root, 'research/salaries')))
const legacyInput = args[0] && !args[0].startsWith('--') ? resolve(args[0]) : null
const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'))
const readGzip = (path) => JSON.parse(gunzipSync(readFileSync(path)).toString('utf8'))
const LEGACY = [
  { label: '2017/18', files: ['data/pssdb-fye17_18.csv'] },
  { label: '2020/21', files: ['data/pssdb-fye22_21'] },
  { label: '2023/24', files: ['data/pssdb-fye23_24'] }
]
const baselineManifest = readJson(join(research, 'baseline-manifest.json'))
const baselineBytes = readFileSync(join(research, baselineManifest.file))
if (sha256(baselineBytes) !== baselineManifest.sha256) throw new Error('Legacy snapshot hash does not match its manifest')
const snapshot = JSON.parse(gunzipSync(baselineBytes).toString('utf8'))
const sourceId = 'pssdb-2026-10-22'
const sources = { [sourceId]: {
  id: sourceId, title: 'Supplied pssdb compilation, retained export snapshot (22 October 2026)', url: null,
  scope: 'compiled-unverified', sourceKind: 'compiled', periodType: 'unverified', threshold: null, provenance: snapshot.provenance.description,
  repositoryCommit: baselineManifest.repositoryCommit, sha256: baselineManifest.sha256,
  notes: ['Edition labels are not verified employer reporting periods. Coverage and disclosure categories vary.']
} }
const employerInfo = new Map()
const remember = (slug, info) => {
  slug = canonicalSlug(slug)
  if (!employerInfo.has(slug)) employerInfo.set(slug, { slug, names: [], body: info.body ?? null, sector: employerSector(slug, info.sector ?? 'Crown corporations') })
  const existing = employerInfo.get(slug)
  existing.names = [...new Set([...existing.names, ...(info.names ?? [])])].sort()
  if (!existing.body && info.body) existing.body = info.body
  return existing
}
for (const employer of snapshot.employers) remember(employer.slug, employer)
let baseline = []
if (legacyInput) {
  sources[sourceId] = { id: sourceId, title: 'Supplied pssdb CSV input', url: null, scope: 'compiled-unverified', threshold: null, provenance: 'Imported directly from the supplied CSV directory; individual input hashes are recorded. Reporting periods and coverage have not been independently verified.', inputFiles: [], notes: ['Edition labels are not verified employer reporting periods.'] }
  for (const year of LEGACY) {
    for (const path of year.files) {
      const input = resolve(legacyInput, path)
      const files = statSync(input).isDirectory() ? readdirSync(input).filter((name) => name.endsWith('.csv')).sort().map((name) => join(input, name)) : [input]
      if (!files.length) throw new Error(`No CSV inputs in ${input}`)
      for (const file of files) {
        const bytes = readFileSync(file)
        sources[sourceId].inputFiles.push({ path: relative(legacyInput, file), sha256: sha256(bytes) })
        const iter = csvRows(bytes.toString('utf8').replace(/^\uFEFF/, ''))
        const header = iter.next().value?.map((name) => name.trim().toLowerCase())
        for (const required of ['agency', 'name', 'remuneration']) if (!header?.includes(required)) throw new Error(`${file}: missing ${required} header`)
        const at = (name) => header.indexOf(name)
        for (const fields of iter) {
          if (fields.length !== header.length) throw new Error(`${file}: row has ${fields.length} fields, expected ${header.length}`)
          const agency = fields[at('agency')]?.trim()
          const pay = money(fields[at('remuneration')])
          if (!agency || pay === null) continue
          const slug = employerSlug(agency)
          remember(slug, { names: [agency], body: BODIES[agency], sector: sectorOf(fields[at('sector')]?.trim() ?? '') })
          baseline.push({ slug, year: year.label, name: fields[at('name')]?.trim() || null,
            position: [fields[at('position')]?.trim(), fields[at('department')]?.trim()].filter(Boolean).join(' · ') || null,
            pay, expenses: money(fields[at('expenses')]), sourceId })
        }
      }
    }
  }
  sources[sourceId].sha256 = sha256(JSON.stringify(sources[sourceId].inputFiles))
} else {
  for (const employer of snapshot.employers) {
    for (const row of employer.rows) baseline.push({ slug: canonicalSlug(employer.slug), year: snapshot.years[row[4]], name: row[0], position: row[1], pay: row[2], expenses: row[3], sourceId })
  }
}

// Preserve anonymous rank identifiers on the employer page; never present them as named people.
let anonymousLabels = 0
for (const row of baseline) {
  if (['metro-vancouver-transit-police', 'transit-police'].includes(row.slug) && /^(?:constable|sergeant|staff sergeant|inspector|special constable)\s+\d+$/i.test(row.name ?? '')) {
    row.position = row.position ? `${row.position} · ${row.name}` : row.name
    row.name = null; anonymousLabels += 1
  }
}
for (const [at, row] of baseline.entries()) validateRow(row, `legacy row ${at + 1}`)

// Only reviewed source decisions can quarantine a partition. Similar pay alone is insufficient.
const reviewed = existsSync(join(research, 'reviewed-decisions.json')) ? readJson(join(research, 'reviewed-decisions.json')).decisions : []
const knownExclusions = [...snapshot.repeated.map((entry) => ({ ...entry, reason: 'Compiled later-year rows repeat an earlier disclosure; original source period is unreliable.' })), ...reviewed.filter((entry) => entry.kind !== 'replace-partition-scope')]
const excluded = new Set(knownExclusions.map((entry) => `${entry.employer}|${entry.year}`))
let official = []
const importedPartitions = new Set()
const deferred = []
const importStats = []
const aggregateSources = []
const sourceCollections = []
const manifests = []
const collectionConfig = join(research, 'collections.json')
const requiredCollections = existsSync(collectionConfig) ? readJson(collectionConfig).collections : null
for (const directory of requiredCollections ?? readdirSync(research).sort()) {
  const manifestPath = join(research, directory, 'sources.json')
  if (!existsSync(manifestPath)) {
    if (requiredCollections) throw new Error(`Required source collection is missing: ${manifestPath}`)
    continue
  }
  const manifest = readJson(manifestPath)
  manifests.push({ collection: directory, manifest })
  for (const source of manifest.aggregateOnlySources ?? []) {
    if (source.status !== 'verified-aggregate-only') continue
    if (!source.id || sources[source.id] || source.rowCount !== 0 || !source.sha256 || !source.sourceUrl) throw new Error(`${directory}: invalid aggregate-only source`)
    yearSlug(source.year)
    const entry = { ...source, collection: directory }
    aggregateSources.push(entry)
    sources[source.id] = { id: source.id, title: source.title, url: source.sourceUrl, year: source.year,
      periodType: source.periodType ?? reportingPeriodType(source.year), periodStart: source.periodStart, periodEnd: source.periodEnd,
      scope: 'aggregate-only', sourceKind: 'official', sha256: source.sha256, threshold: source.threshold,
      thresholdComparison: source.thresholdComparison ?? (source.thresholdRule === 'over' ? '>' : null),
      currency: source.currency ?? 'CAD', validation: source.validation, notes: source.notes }
    if (!employerInfo.has(source.employerSlug)) remember(source.employerSlug, { names: [source.employerName], sector: source.sector, body: Object.values(BODIES).includes(source.employerSlug) ? source.employerSlug : null })
  }
  sourceCollections.push({ collection: directory, coverageNotes: manifest.coverageNotes ?? manifest.notes ?? [], excludedSources: manifest.excludedSources ?? [], unparsedSources: manifest.unparsedSources ?? [], compiledYearCorrection: manifest.compiledYearCorrection ?? null })
  deferred.push(...(manifest.deferredEmployers ?? manifest.deferred ?? []).map((entry) => ({ collection: directory, ...entry })))
  for (const source of manifest.sources ?? []) {
    if (source.status && !['accepted', 'verified', 'imported'].includes(source.status)) { deferred.push(source); continue }
    if (!source.file) continue
    if (!source.id || sources[source.id]) throw new Error(`${manifestPath}: missing or duplicate source id ${source.id}`)
    if (!source.category && !source.scope) throw new Error(`${source.id}: explicit disclosure scope is required before import`)
    const year = source.year ?? source.label
    yearSlug(year)
    if (source.periodType && source.periodType !== reportingPeriodType(year)) throw new Error(`${source.id}: reporting period type contradicts its year label`)
    if (reportingPeriodType(year) === 'calendar' && (source.periodStart !== `${year}-01-01` || source.periodEnd !== `${year}-12-31`)) throw new Error(`${source.id}: calendar source requires its actual January–December dates`)
    deferred.push(...(source.deferredEmployers ?? []).map((entry) => ({ collection: directory, sourceId: source.id, year, sourceUrl: source.sourceUrl, ...entry })))
    const path = resolve(dirname(manifestPath), source.file)
    if (relative(dirname(manifestPath), path).startsWith(`..${sep}`)) throw new Error(`${source.id}: data file outside source collection`)
    const bytes = readFileSync(path)
    if (!source.dataSha256 && !source.normalizedSha256) throw new Error(`${source.id}: normalized data hash is required`)
    if (sha256(bytes) !== (source.dataSha256 ?? source.normalizedSha256)) throw new Error(`${source.id}: normalized data hash mismatch`)
    const payload = JSON.parse(gunzipSync(bytes).toString('utf8'))
    const sourceRows = Array.isArray(payload) ? payload : payload.rows
    if (!Array.isArray(sourceRows) || !sourceRows.length) throw new Error(`${source.id}: empty or malformed source`)
    const allowed = source.employers?.map((entry) => typeof entry === 'string' ? entry : entry.slug ?? entry.employerSlug) ?? [source.employerSlug]
    const accepted = []
    for (const [at, fields] of sourceRows.entries()) {
      if (!Array.isArray(fields) || fields.length < 5) throw new Error(`${source.id}: malformed row ${at + 1}`)
      const [slug_, name, position, pay, expenses, page] = fields
      const slug = canonicalSlug(slug_)
      if (!allowed.includes(slug_)) throw new Error(`${source.id}: unexpected employer ${slug_}`)
      if (page != null && (!Number.isInteger(page) || page < 1)) throw new Error(`${source.id}: invalid physical PDF page on row ${at + 1}`)
      const row = { slug, year, name, position, pay, expenses, sourceId: source.id, page: page ?? null }
      validateRow(row, `${source.id} row ${at + 1}`)
      accepted.push(row)
      importedPartitions.add(`${slug}|${year}`)
      if (!employerInfo.has(slug)) remember(slug, { names: [source.employerName ?? slug], body: Object.values(BODIES).includes(slug) ? slug : null, sector: source.sector ?? 'Crown corporations' })
    }
    for (const employer of source.employers ?? []) {
      if (typeof employer === 'string') continue
      const partition = accepted.filter((row) => row.slug === canonicalSlug(employer.slug ?? employer.employerSlug))
      if (employer.rowCount !== undefined && partition.length !== employer.rowCount) throw new Error(`${source.id}: ${employer.slug} row count mismatch`)
      if (employer.totalRemuneration !== undefined && Math.abs(sumMoney(partition.map((row) => row.pay)) - employer.totalRemuneration) > 0.011) throw new Error(`${source.id}: ${employer.slug} total mismatch`)
      const expectedExpenses = employer.totalExpenses ?? employer.totalDisclosedExpenses
      if (expectedExpenses !== undefined && Math.abs(sumMoney(partition.map((row) => row.expenses ?? 0)) - expectedExpenses) > 0.011) throw new Error(`${source.id}: ${employer.slug} expenses total mismatch`)
    }
    if (source.rowCount !== undefined && accepted.length !== source.rowCount) throw new Error(`${source.id}: row count mismatch`)
    if (source.totalRemuneration !== undefined && Math.abs(sumMoney(accepted.map((row) => row.pay)) - source.totalRemuneration) > 0.011) throw new Error(`${source.id}: imported remuneration total mismatch`)
    const expectedExpenses = source.totalExpenses ?? source.totalDisclosedExpenses
    if (expectedExpenses !== undefined && Math.abs(sumMoney(accepted.map((row) => row.expenses ?? 0)) - expectedExpenses) > 0.011) throw new Error(`${source.id}: imported expenses total mismatch`)
    sources[source.id] = {
      id: source.id, title: source.title ?? source.sourceTitle ?? `${source.employerName ?? directory} ${year} ${source.category ?? 'remuneration'}`,
      url: source.sourceUrl ?? source.url, year, periodType: source.periodType ?? reportingPeriodType(year), sourceKind: source.sourceKind ?? 'official', periodStart: source.periodStart ?? null, periodEnd: source.periodEnd ?? null,
      scope: source.category ?? source.scope, scopeDescription: source.scopeDescription ?? source.scope ?? null, threshold: source.threshold ?? null,
      thresholdComparison: source.thresholdComparison ?? (source.thresholdRule === 'at-least' ? '>=' : source.thresholdRule === 'over' ? '>' : null),
      provenance: 'Official published schedule; independently downloaded and validated by the source importer.',
      sha256: source.sha256 ?? source.pdfSha256, dataSha256: sha256(bytes), notes: source.notes ?? [],
      validation: source.validation ?? null, nameDisclosure: source.nameDisclosure ?? null, positionDisclosure: source.positionDisclosure ?? null,
      travelSource: source.travelSource ?? null, expensesNote: source.expensesNote ?? null, currency: source.currency ?? 'CAD'
    }
    official.push(...accepted)
    importStats.push({ id: source.id, year, rows: accepted.length, employers: [...new Set(accepted.map((row) => row.slug))], totalRemuneration: sumMoney(accepted.map((row) => row.pay)) })
  }
}
const travelRecovery = applyTravelJoinCorrections(official, sources, manifests.flatMap(({ manifest }) => manifest.invalidatedTravelJoins ?? []))
official = travelRecovery.rows
const recoveredOicYears = new Set(official.filter((row) => row.sourceId.startsWith('public-accounts-oic-')).map((row) => row.year))
for (const source of Object.values(sources)) {
  if (!recoveredOicYears.has(source.year)) continue
  source.notes = (source.notes ?? []).map((note) => note.startsWith('The OIC/appointee schedule for this fiscal year is not imported:')
    ? 'The catalogue OIC resource incorrectly supplies the Other Employees schedule and remains excluded. This year’s appointee records have now been recovered separately from the original provincial PDF.' : note)
}
if (recoveredOicYears.size) {
  const previousCollection = sourceCollections.find((entry) => entry.collection === 'public-accounts')
  if (previousCollection) previousCollection.coverageNotes = [...previousCollection.coverageNotes,
    'The public-accounts-oic collection restores the missing appointee cohorts from original PDFs; the invalid catalogue CSV resources remain excluded.']
}
for (const correction of travelRecovery.corrections) {
  const source = sources[correction.employeeSourceId]
  source.notes = [...source.notes, 'An inferred travel match was withheld after a recovered appointee schedule made that disclosed name non-unique. The original travel schedule remains cited; the amount is not reassigned.']
  source.validation = { ...source.validation, invalidatedTravelJoins: travelRecovery.corrections.filter((entry) => entry.employeeSourceId === correction.employeeSourceId) }
}
validateReplacementScopes(baseline, official, sources, reviewed)
const compiledRecovery = applyCompiledReplacements(baseline, official, sources, manifests.flatMap(({ manifest }) => manifest.compiledReplacements ?? []))
const backlogPath = join(research, 'source-backlog.json')
const catalog = sourceCatalog(existsSync(backlogPath) ? readJson(backlogPath) : {}, manifests)
const legacyRetained = compiledRecovery.rows.filter((row) => !importedPartitions.has(`${row.slug}|${row.year}`) && !excluded.has(`${row.slug}|${row.year}`))
const rows = [...legacyRetained, ...official]
if (!rows.length) throw new Error('No salary rows; refusing to replace the published data')
const labels = [...new Set([...LEGACY.map(({ label }) => label), ...rows.map((row) => row.year), ...catalog.map((entry) => entry.year).filter(Boolean)])].sort()
const years = labels.map((label) => ({ label, slug: yearSlug(label), periodType: reportingPeriodType(label) }))
const yearAt = new Map(labels.map((label, at) => [label, at]))
const bySlug = new Map()
for (const row of rows) { if (!bySlug.has(row.slug)) bySlug.set(row.slug, []); bySlug.get(row.slug).push(row) }
const audit = {
  version: 1, baseline: { rows: baseline.length, employers: snapshot.employers.length, years: snapshot.years, commit: baselineManifest.repositoryCommit },
  imports: importStats, legacyRowsRetained: legacyRetained.length, officialRows: official.length,
  replacedLegacyRows: baseline.length - legacyRetained.length,
  corrections: [...knownExclusions.map((entry) => ({ ...entry, status: importedPartitions.has(`${entry.employer}|${entry.year}`) ? 'replaced-from-official-source' : 'excluded' })), ...compiledRecovery.corrections],
  deferred, aggregateSources, travelJoinCorrections: travelRecovery.corrections, sourceCollections, sourceCatalog: catalog, anonymousLabels, repeatedCandidates: repeatedCandidates(rows), duplicates: [],
  notes: ['An absent record does not establish unemployment or below-threshold pay.', 'Exact duplicate-looking rows remain flagged unless an official replacement resolves them; shared names can be different people.', 'Legacy edition labels are unverified reporting periods.']
}
const index = { source: 'Official remuneration schedules with retained, explicitly unverified pssdb snapshots', years, sources, bodies: {}, unmatched: {}, repeated: audit.corrections.filter((entry) => entry.status === 'excluded'), corrections: audit.corrections }

// Stage all outputs first. A rejected input cannot erase a working website.
mkdirSync(dirname(out), { recursive: true })
const stage = mkdtempSync(join(dirname(out), '.salaries-build-'))
const write = (path, value, gzip = false) => {
  const target = join(stage, path); mkdirSync(dirname(target), { recursive: true })
  const text = JSON.stringify(value) + '\n'
  writeFileSync(target, gzip ? gzipSync(text, { level: 9 }) : text)
}
const compiledNotes = ['Compiled edition; the employer’s exact reporting period and completeness have not been verified against its report.']
const employerList = []
try {
  for (const [slug, list] of [...bySlug].sort(([a], [b]) => a.localeCompare(b))) {
    const info = employerInfo.get(slug)
    const periodTypes = new Set(list.map((row) => sources[row.sourceId]?.periodType).filter((type) => ['calendar', 'fiscal'].includes(type)))
    if (!periodTypes.size) for (const row of list) periodTypes.add(reportingPeriodType(row.year))
    const coverage = labels.map((label) => {
      const subset = list.filter((row) => row.year === label)
      const sourceLeads = sourceLeadsFor(catalog, slug, label)
      if (!subset.length) {
        const aggregate = aggregateSources.find((entry) => entry.employerSlug === slug && entry.year === label)
        if (aggregate) return { status: 'aggregate-only', scope: 'aggregate-only', sourceIds: [aggregate.id], sourceLeads: [],
          periodType: aggregate.periodType ?? reportingPeriodType(label), periodStart: aggregate.periodStart, periodEnd: aggregate.periodEnd,
          threshold: aggregate.threshold, thresholdComparison: sources[aggregate.id].thresholdComparison, aggregate: aggregate.validation?.sourceControls ?? null,
          rows: 0, namedRows: 0, positions: 0, duplicateRows: 0, notes: aggregate.notes ?? ['The verified report publishes aggregate payroll without individual employee rows.'] }
        if (!sourceLeads.length && !excluded.has(`${slug}|${label}`) && !periodTypes.has(reportingPeriodType(label))) return {
          status: 'not-applicable', sourceIds: [], sourceLeads: [], rows: 0, namedRows: 0, positions: 0, duplicateRows: 0,
          notes: ['This label uses a different reporting-period type from this employer’s imported sources. Use its corresponding calendar or fiscal periods.'] }
        const held = deferred.filter((entry) => (entry.slug ?? entry.employerSlug) === slug && entry.year === label)
        const heldLeads = sourceLeads.filter((entry) => entry.status === 'held-for-review')
        return { status: held.length || heldLeads.length || excluded.has(`${slug}|${label}`) ? 'excluded' : hasLocatedSource(sourceLeads) ? 'source-found' : 'missing', sourceIds: held.map((entry) => entry.sourceId).filter((id) => sources[id]), sourceLeads, scope: held.length || hasLocatedSource(sourceLeads) ? 'employee-remuneration' : undefined,
          rows: 0, namedRows: 0, positions: 0, duplicateRows: 0,
          notes: held.length ? held.map((entry) => entry.reason ?? 'The source was found but held for reconciliation; its records are not published here.') : heldLeads.length ? heldLeads.map((entry) => entry.nextAction) : hasLocatedSource(sourceLeads) ? ['A potential official source has been located, but its employee records have not yet passed extraction and validation.'] : ['No imported records for this employer and year; this is not evidence that it had no employees.'] }
      }
      const sourceIds = [...new Set(subset.map((row) => row.sourceId))].sort()
      const details = sourceIds.map((id) => sources[id])
      const isLegacy = details.some((detail) => detail.sourceKind === 'compiled' || detail.scope === 'compiled-unverified')
      const scope = slug === 'bc-investment-management-corporation' && label === '2023/24' && isLegacy ? 'executive-only' : details.every((detail) => detail.scope === details[0].scope) ? details[0].scope : 'mixed-disclosure'
      const duplicates = duplicateStats(subset)
      if (duplicates.duplicateRows) audit.duplicates.push({ employer: slug, year: label, ...duplicates })
      const periods = new Set(details.map((detail) => JSON.stringify([detail.periodStart, detail.periodEnd])))
      const thresholds = new Set(details.map((detail) => detail.threshold))
      const thresholdComparisons = new Set(details.map((detail) => detail.thresholdComparison ?? null))
      const notes = [...new Set([
        ...(isLegacy ? compiledNotes : []), ...details.flatMap((detail) => detail.notes ?? []),
        ...(scope === 'executive-only' ? ['Only five executive positions are present; this is not a full employee disclosure.'] : []),
        ...(duplicates.duplicateRows ? [`${duplicates.duplicateRows} identical-looking extra rows require source review; totals include these rows.`] : []),
        ...(subset.some((row) => row.name && !row.name.includes(',')) ? ['Some source names lack a verified surname/given-name separator; matches across years may be incomplete.'] : []),
        ...(scope === 'mixed-disclosure' ? ['Includes separate disclosure categories. Select a category to compare records with the same coverage rules.'] : [])
      ])]
      return { status: 'available', scope, sourceIds, sourceLeads, periodType: isLegacy ? 'unverified' : reportingPeriodType(label), periodStart: periods.size === 1 ? details[0].periodStart ?? null : null, periodEnd: periods.size === 1 ? details[0].periodEnd ?? null : null,
        threshold: thresholds.size === 1 ? details[0].threshold : null, rows: subset.length, namedRows: subset.filter((row) => row.name).length,
        thresholdComparison: thresholds.size === 1 && thresholdComparisons.size === 1 ? details[0].thresholdComparison ?? null : null,
        positions: subset.filter((row) => row.position).length, ...duplicates, notes }
    })
    const exported = list.map((row) => [row.name, row.position, row.pay, row.expenses, yearAt.get(row.year), row.sourceId, row.page ?? null])
      .sort((a, b) => a[4] - b[4] || b[2] - a[2] || String(a[0]).localeCompare(String(b[0])) || String(a[1]).localeCompare(String(b[1])))
    write(`employers/${slug}.json.gzip`, exported, true)
    employerList.push({ ...info, counts: coverage.map((entry) => entry.rows), repeated: index.repeated.filter((entry) => entry.employer === slug).map((entry) => entry.year), coverage })
    for (const [at, year] of years.entries()) {
      const subset = list.filter((row) => row.year === year.label)
      if (!subset.length) continue
      if (!info.body) { index.unmatched[slug] = (index.unmatched[slug] ?? 0) + subset.length; continue }
      const bodyRows = exported.filter((row) => row[4] === at).map((row) => [row[0], row[1], row[2], row[3], row[5], row[6]])
      const details = coverage[at]
      write(`${year.slug}/${info.body}.json`, { ...details, year: year.label, agencies: info.names, rows: bodyRows })
      ;(index.bodies[info.body] ??= {})[year.slug] = { count: bodyRows.length, total: sumMoney(subset.map((row) => row.pay)), median: median(subset.map((row) => row.pay)), max: Math.max(...subset.map((row) => row.pay)), agencies: info.names, sourceIds: details.sourceIds, scope: details.scope, notes: details.notes, periodStart: details.periodStart, periodEnd: details.periodEnd, threshold: details.threshold, duplicateRows: details.duplicateRows }
    }
  }
  const coverage = Object.fromEntries(employerList.map((entry) => [entry.slug, entry.coverage]))
  write('employers/index.json', { schemaVersion: 2, note: 'Rows: [disclosed name, position, remuneration, expenses, year index, source id, physical PDF page or null]. Counts are disclosure rows, not a workforce census.', years: labels, sources, aliases: EMPLOYER_ALIASES, employers: employerList })
  const employerAt = new Map(employerList.map((employer, at) => [employer.slug, at]))
  const shards = new Map()
  for (const row of rows) {
    if (!row.name) continue
    const shard = surnameShard(row.name)
    if (!shards.has(shard)) shards.set(shard, [])
    shards.get(shard).push([row.name, row.position, row.pay, row.expenses, employerAt.get(row.slug), yearAt.get(row.year), row.sourceId, row.page ?? null])
  }
  const shardCounts = {}
  for (const [shard, list] of [...shards].sort(([a], [b]) => a.localeCompare(b))) {
    list.sort((a, b) => a[0].localeCompare(b[0]) || a[5] - b[5] || b[2] - a[2] || a[4] - b[4])
    write(`people/${shard}.json.gzip`, list, true); shardCounts[shard] = list.length
  }
  write('people/top.json.gzip', { note: `Each period's ${TOP_PER_PERIOD} highest-paid named records across every employer, in the people index's row schema, highest first. The top only, not every record.`, perPeriod: TOP_PER_PERIOD, rows: topRecords([...shards.values()].flat()) }, true)
  write('people/index.json', { schemaVersion: 2, note: 'Rows: [disclosed name, position, remuneration, expenses, employer index, year index, source id, physical PDF page or null]. Names are not personal identifiers.', years: labels, sources, coverage, employers: employerList.map(({ slug, names, sector, body }) => [names.at(-1), sector, body, slug]), shards: shardCounts })
  // Every position title across employers (src/salaries/positions.js reads one title however it was
  // spelled): a list to search, then each title's employers and years in slices by its first letters.
  const titles = new Map()
  for (const row of rows) {
    const key = row.position ? titleKey(row.position) : ''
    if (!key) continue
    if (!titles.has(key)) titles.set(key, { spellings: new Map(), cells: new Map(), employers: new Set(), rows: 0, records: [] })
    const title = titles.get(key)
    const cell = `${employerAt.get(row.slug)}|${yearAt.get(row.year)}`
    title.rows += 1
    title.records.push({ name: row.name, group: row.slug, pay: row.pay, year: yearAt.get(row.year) })
    title.employers.add(row.slug)
    title.spellings.set(row.position, (title.spellings.get(row.position) ?? 0) + 1)
    if (!title.cells.has(cell)) title.cells.set(cell, [])
    title.cells.get(cell).push(row.pay)
  }
  const titleList = []
  const titleShards = new Map()
  for (const [key, title] of [...titles].sort(([a], [b]) => a.localeCompare(b))) {
    const spellings = [...title.spellings].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    const cells = [...title.cells].map(([cell, pay]) => {
      const [employer, year] = cell.split('|').map(Number)
      return [employer, year, pay.length, Math.round(sumMoney(pay) / pay.length * 100) / 100, median(pay), Math.min(...pay), Math.max(...pay)]
    }).sort((a, b) => a[1] - b[1] || a[0] - b[0])
    // How its pay moved (src/salaries/growth.js): each employer's average from end to end, and the
    // median raise of a name kept under the title at one employer.
    const byEmployer = new Map()
    for (const [employer, year, count, mean] of cells) {
      if (!byEmployer.has(employer)) byEmployer.set(employer, [])
      byEmployer.get(employer).push({ year, count, mean })
    }
    const growth = pooledGrowth([...byEmployer], labels)
    const raise = typicalRaise(stayerRaises(title.records, labels))
    const rate = (value) => Math.round(value * 10000) / 10000
    const entry = [spellings[0][0], title.rows, title.employers.size, cells[0][1], cells.at(-1)[1], periodMean(cells, cells.at(-1)[1]),
      growth ? rate(growth.rate) : null, growth?.weight ?? 0, growth?.employers ?? 0, growth?.from ?? null, growth?.to ?? null,
      raise ? rate(raise.rate) : null, raise?.pairs ?? 0, raise?.people ?? 0]
    // Most titles have neither measure: their entries stop at the average.
    while (entry.length > 6 && (entry.at(-1) === null || entry.at(-1) === 0)) entry.pop()
    titleList.push(entry)
    // The median of every record under the title in each year, across every employer and, where it
    // spans several sectors, within each. Employers' own medians cannot be combined into it. A year
    // with one employer in it is left out: its median is that employer's, already in its cell.
    const pooled = new Map()
    for (const [cell, pay] of title.cells) {
      const [employer, year] = cell.split('|').map(Number)
      for (const group of ['all', employerList[employer].sector]) {
        if (!pooled.has(group)) pooled.set(group, new Map())
        const years = pooled.get(group)
        if (!years.has(year)) years.set(year, { employers: 0, pay: [] })
        const entry = years.get(year)
        entry.employers += 1
        for (const value of pay) entry.pay.push(value)
      }
    }
    let medians
    for (const [group, years] of pooled) {
      if (group !== 'all' && pooled.size === 2) continue
      const list = [...years].filter(([, entry]) => entry.employers > 1).sort((a, b) => a[0] - b[0]).map(([year, entry]) => [year, median(entry.pay)])
      if (list.length) (medians ??= {})[group] = list
    }
    const shard = titleShard(key)
    if (!titleShards.has(shard)) titleShards.set(shard, {})
    titleShards.get(shard)[key] = medians ? { spellings: spellings.slice(0, 12), cells, medians } : { spellings: spellings.slice(0, 12), cells }
  }
  titleList.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  for (const [shard, entries] of titleShards) write(`positions/${shard}.json.gzip`, entries, true)
  write('positions/index.json.gzip', { note: 'Titles: [most common spelling, rows, employers, first year index, last year index, average in the last period, average growth a year (each employer from its first to its last period with 5 or more records, 3 or more years apart, weighed by records; src/salaries/growth.js), records weighing it, employers in it, its first year index, its last year index, median yearly raise of a name kept under the title at one employer, raises in it, names in it]; growth and raise are null where none could be measured, and an entry ends where its remaining fields would all be empty. Slices by key: cells [employer index in employers/index.json, year index, rows, mean, median, lowest, highest]. Medians, where several employers share a year: { all, or a sector where the title spans several: [[year index, median of every record that year]] }; a year with one employer has that cell’s median. Rows are disclosure records, not positions filled.', years: labels, titles: titleList, shards: [...titleShards.keys()].sort() }, true)
  audit.output = { rows: rows.length, namedRows: Object.values(shardCounts).reduce((sum, count) => sum + count, 0), employers: employerList.length, atlasBodies: Object.keys(index.bodies).length, years: labels, availableEmployerYears: employerList.reduce((sum, entry) => sum + entry.coverage.filter((year) => year.status === 'available').length, 0) }
  write('coverage.json', { ...audit, employers: employerList.map(({ slug, names, sector, coverage }) => ({ slug, names, sector, coverage })) })
  index.coverage = Object.fromEntries(employerList.filter((entry) => entry.body).map((entry) => [entry.body, entry.coverage]))
  write('index.json', index)
  const generated = `// Generated by scripts/build-salaries.mjs — do not edit.\n// Counts and totals describe the imported disclosure rows, not a full workforce census.\nexport const SALARY_YEARS = ${JSON.stringify(years)}\nexport const SALARY_INDEX = ${JSON.stringify(index.bodies)}\nexport const SALARY_SOURCES = ${JSON.stringify(sources)}\nexport const SALARY_COVERAGE = ${JSON.stringify(index.coverage)}\n`
  // Keep a backup until both the directory and generated module have been replaced successfully.
  const backup = `${out}.previous-build`
  if (existsSync(backup)) throw new Error(`Previous backup exists: ${backup}; inspect before rebuilding`)
  const hadOutput = existsSync(out)
  if (hadOutput) renameSync(out, backup)
  try {
    renameSync(stage, out)
    mkdirSync(dirname(indexPath), { recursive: true })
    writeFileSync(`${indexPath}.tmp`, generated)
    renameSync(`${indexPath}.tmp`, indexPath)
  } catch (error) {
    rmSync(out, { recursive: true, force: true })
    if (hadOutput) renameSync(backup, out)
    throw error
  }
  rmSync(backup, { recursive: true, force: true })
  console.log(JSON.stringify(audit.output, null, 2))
  console.log(`Official rows: ${official.length}; retained compiled rows: ${legacyRetained.length}; duplicate-looking rows flagged: ${audit.duplicates.reduce((sum, entry) => sum + entry.duplicateRows, 0)}`)
} finally {
  rmSync(stage, { recursive: true, force: true })
}
