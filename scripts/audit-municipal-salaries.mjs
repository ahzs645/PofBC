// Reconcile the complete provincial roster with accepted salary imports and
// separately recorded source leads. This command never downloads or imports rows.
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gunzipSync } from 'node:zlib'
import { canonicalSlug } from './lib/salary-employers.mjs'
import { sha256 } from './lib/salary-data.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const research = join(root, 'research/salaries')
const out = join(research, 'municipal-audit')
const read = (path) => JSON.parse(readFileSync(path, 'utf8'))
const save = (file, value) => writeFileSync(join(out, file), JSON.stringify(value, null, 2) + '\n')
const unique = (items) => [...new Set(items)].sort()
const sum = (items) => items.reduce((total, n) => total + n, 0)
const md = (value) => String(value ?? '').replaceAll('|', '\\|').replaceAll('\n', ' ')
const fmt = (n) => n.toLocaleString('en-CA')
const roster = read(join(out, 'roster.json'))
const baseline = read(join(out, 'baseline.json'))
const coverage = read(join(root, 'public/salaries/coverage.json'))
const index = read(join(root, 'public/salaries/index.json'))
const additions = ['municipal-north', 'municipal-island', 'municipal-lower-mainland', 'municipal-small', 'municipal-ocr', 'sector-municipal']
const rosterSlugs = new Set(roster.municipalities.map(r => canonicalSlug(r.employerSlug)))
if (rosterSlugs.size !== 162 || roster.municipalities.filter(r => r.status !== 'pending-incorporation').length !== 161) throw new Error('Reviewed municipal roster changed')
const accepted = []
const collections = []
for (const collection of read(join(research, 'collections.json')).collections) {
  const manifest = read(join(research, collection, 'sources.json'))
  const municipal = (manifest.sources ?? []).filter(s => s.file && (!s.status || ['verified', 'accepted', 'imported'].includes(s.status)) && rosterSlugs.has(canonicalSlug(s.employerSlug)))
  for (const source of municipal) {
    const bytes = readFileSync(join(research, collection, source.file))
    if (sha256(bytes) !== source.dataSha256) throw new Error(`${source.id}: normalized hash mismatch`)
    const payload = JSON.parse(gunzipSync(bytes))
    const rows = Array.isArray(payload) ? payload : payload.rows
    if (rows.length !== source.rowCount) throw new Error(`${source.id}: row count mismatch`)
    if (!coverage.imports.some(s => s.id === source.id && s.rows === rows.length)) throw new Error(`${source.id}: source not reconciled with published exports`)
    accepted.push({ collection, id: source.id, employerSlug: canonicalSlug(source.employerSlug), year: source.year,
      category: source.category ?? source.scope, rows: rows.length, namedRows: rows.filter(r => r[1]).length,
      sourceUrl: source.sourceUrl, sourceIndexUrl: source.sourceIndexUrl, sourceSha256: source.sha256,
      dataSha256: source.dataSha256, notes: source.notes ?? [], publicWarning: source.publicWarning ?? null, validation: source.validation ?? {} })
  }
  if (additions.includes(collection)) collections.push({ collection, sources: municipal.length,
    reportYears: new Set(municipal.map(s => `${canonicalSlug(s.employerSlug)}|${s.year}`)).size,
    municipalities: new Set(municipal.map(s => canonicalSlug(s.employerSlug))).size,
    records: sum(municipal.map(s => s.rowCount)),
    employeeRecords: sum(municipal.filter(s => (s.category ?? s.scope) === 'employee-remuneration').map(s => s.rowCount)),
    councilRecords: sum(municipal.filter(s => (s.category ?? s.scope) === 'elected-officials').map(s => s.rowCount)) })
}
if (collections.length !== additions.length) throw new Error('Municipal additions are not all registered')

const regional = new Map()
for (const collection of additions) {
  const path = join(research, collection, 'discovery.json')
  if (!existsSync(path)) continue
  const value = read(path)
  for (const row of Array.isArray(value) ? value : value.municipalities ?? []) {
    const slug = canonicalSlug(row.employerSlug)
    if (!rosterSlugs.has(slug)) throw new Error(`${collection}: discovery employer is outside the roster: ${slug}`)
    regional.set(slug, [...(regional.get(slug) ?? []), { ...row, collection }])
  }
}
const reviewedLeadsPath = join(out, 'reviewed-leads.json')
const reviewedLeads = existsSync(reviewedLeadsPath) ? read(reviewedLeadsPath).leads : []
const explicitSofi = (lead) => {
  let text = (lead.label ?? lead.title ?? '') + ' ' + (lead.url ?? '')
  try { text = decodeURIComponent(text) } catch { /* A malformed URL remains an unreviewed lead. */ }
  return /\bsofi\b|statement[\s_%-]*(?:of[\s_%-]*)?financial[\s_%-]*information|remuneration|employee.*salar/i.test(text)
}
const employeeCategory = (s) => ['employee-remuneration', 'named-employees-over-threshold'].includes(s.category)
const municipalities = []
for (const entry of roster.municipalities) {
  const slug = canonicalSlug(entry.employerSlug)
  const original = read(join(out, 'discovery', `${entry.employerSlug}.json`))
  const region = regional.get(slug) ?? []
  const sources = accepted.filter(s => s.employerSlug === slug)
  const reports = new Map()
  const addLead = (lead) => {
    if (!lead.url || !/^https?:\/\//.test(lead.url)) return
    const previous = reports.get(lead.url)
    if (previous) {
      previous.foundOn = unique([...(previous.foundOn ?? []), ...(lead.foundOn ?? [])])
      if (['imported', 'held-for-review', 'requires-ocr'].includes(lead.status)) Object.assign(previous, lead)
    } else reports.set(lead.url, lead)
  }
  for (const lead of original.candidates) addLead({ url: lead.url, label: lead.label,
    status: 'linked-unreviewed', kind: lead.kind, yearsMentioned: lead.yearsInLabel, periodVerified: false,
    foundOn: [lead.foundOn], discoveryFile: `discovery/${entry.employerSlug}.json` })
  for (const r of region) {
    if (r.indexUrl) addLead({ url: r.indexUrl, label: `${r.municipality} official source index`, status: 'index-located', periodVerified: false, foundOn: [], discoveryFile: `../${r.collection}/discovery.json` })
    for (const lead of r.reportUrls ?? []) addLead({ url: lead.url ?? lead.sourceUrl, label: lead.label ?? lead.title,
      indexedYear: lead.year ?? null, status: lead.status ?? 'linked-unreviewed', periodVerified: false,
      foundOn: [r.indexUrl].filter(Boolean), discoveryFile: `../${r.collection}/discovery.json` })
  }
  for (const lead of reviewedLeads.filter(s => canonicalSlug(s.employerSlug) === slug)) addLead({ ...lead,
    status: 'index-or-report-located', periodVerified: false, foundOn: lead.foundOn ? [lead.foundOn] : [], discoveryFile: 'reviewed-leads.json' })
  const backlog = coverage.sourceCatalog.filter(s => s.employerSlug === slug && s.status !== 'imported')
  for (const lead of backlog) addLead({ url: lead.url, label: lead.title, indexedYear: lead.year, status: lead.status,
    periodVerified: false, foundOn: [lead.indexUrl].filter(Boolean), reason: lead.reason, nextAction: lead.nextAction, notes: lead.notes })
  for (const source of sources) addLead({ url: source.sourceUrl, label: `${entry.employerName} ${source.year} ${source.category}`,
    status: 'imported', periodVerified: true, calendarYear: source.year, foundOn: [source.sourceIndexUrl].filter(Boolean) })
  const exportPath = join(root, 'public/salaries/employers', `${slug}.json.gzip`)
  const rows = existsSync(exportPath) ? JSON.parse(gunzipSync(readFileSync(exportPath))) : []
  const compiledRows = rows.filter(r => index.sources[r[5]]?.sourceKind === 'compiled')
  const officialRows = rows.length - compiledRows.length
  if (officialRows !== sum(sources.map(s => s.rows))) throw new Error(`${slug}: published official rows differ from accepted sources`)
  const employees = sources.filter(employeeCategory)
  const council = sources.filter(s => s.category === 'elected-officials')
  const strongLeads = [...reports.values()].filter(explicitSofi)
  let status, nextAction
  if (entry.status === 'pending-incorporation') {
    status = 'not-yet-incorporated'
    nextAction = `Revisit after incorporation on ${entry.effectiveFrom}; earlier municipal salary years are not missing records.`
  } else if (employees.length) {
    status = 'official-employee-records-imported'
    nextAction = 'Review remaining report years and council schedules; accepted employee years are not a claim of complete employment or historical coverage.'
  } else if (council.length) {
    status = 'official-council-only'
    nextAction = 'Resolve the held employee schedule; council records do not establish employee coverage.'
  } else if (backlog.length) {
    status = 'source-held-or-awaiting-extraction'
    nextAction = backlog[0].nextAction
  } else if (strongLeads.length) {
    status = 'salary-source-lead-awaiting-validation'
    nextAction = 'Retrieve the linked schedule, verify its actual reporting period and scope, then validate named rows and totals.'
  } else {
    status = 'further-source-discovery-needed'
    nextAction = 'Search the official finance and council archives; if necessary obtain the public SOFI from the municipality. No absence of records is inferred from the bounded search.'
  }
  if (entry.status === 'special-governance') nextAction = 'Review this government district’s own public financial disclosures. Do not assume provincial municipal SOFI requirements apply.'
  const archiveUrl = region.find(r => r.indexUrl)?.indexUrl
    ?? reviewedLeads.find(s => canonicalSlug(s.employerSlug) === slug)?.url
    ?? strongLeads.find(l => l.foundOn?.length)?.foundOn[0] ?? entry.website
  municipalities.push({ ...entry, employerSlug: slug, salaryStatus: status, nextAction, archiveUrl,
    records: rows.length, officialRecords: officialRows, compiledUnverifiedRecords: compiledRows.length,
    officialEmployeeYears: unique(employees.map(s => s.year)), officialCouncilYears: unique(council.map(s => s.year)),
    compiledUnverifiedEditionLabels: unique(compiledRows.map(r => coverage.output.years[r[4]])),
    acceptedSources: sources, heldOrUnparsedSources: backlog,
    sourceLeadCount: reports.size, explicitSalaryLeadCount: strongLeads.length,
    pagesChecked: original.pagesChecked.length,
    sourceSearchSucceeded: original.pagesChecked.some(p => p.status === 'html-read'),
    regionalNotes: region.flatMap(r => r.notes ?? []),
    sourceLeads: [...reports.values()].sort((a, b) => a.url.localeCompare(b.url)) })
}
const current = municipalities.filter(m => m.status !== 'pending-incorporation')
const addedSources = accepted.filter(s => additions.includes(s.collection))
const baselineMunicipal = baseline.municipalEmployers.filter(e => rosterSlugs.has(e.slug))
const summary = {
  currentJurisdictions: current.length,
  pendingJurisdictions: municipalities.length - current.length,
  auditedJurisdictions: municipalities.length,
  withAnySalaryRecordsBefore: baselineMunicipal.length,
  withAnySalaryRecordsAfter: current.filter(m => m.records).length,
  withOfficialRecordsBefore: baselineMunicipal.filter(e => e.coverage.some(c => c.periodType === 'calendar' && c.rows)).length,
  withOfficialRecordsAfter: current.filter(m => m.officialRecords).length,
  withOfficialEmployeeRecords: current.filter(m => m.officialEmployeeYears.length).length,
  withOfficialCouncilRecords: current.filter(m => m.officialCouncilYears.length).length,
  withNoOfficialRecords: current.filter(m => !m.officialRecords).length,
  withNoSalaryRecords: current.filter(m => !m.records).length,
  newlyAcceptedSourceCohorts: addedSources.length,
  newlyAcceptedReportYears: new Set(addedSources.map(s => `${s.employerSlug}|${s.year}`)).size,
  municipalitiesInAddedCollections: new Set(addedSources.map(s => s.employerSlug)).size,
  newlyAcceptedRecords: sum(addedSources.map(s => s.rows)),
  newEmployeeRecords: sum(addedSources.filter(employeeCategory).map(s => s.rows)),
  newCouncilRecords: sum(addedSources.filter(s => s.category === 'elected-officials').map(s => s.rows)),
  municipalOfficialRecords: sum(current.map(m => m.officialRecords)),
  municipalCompiledUnverifiedRecords: sum(current.map(m => m.compiledUnverifiedRecords)),
  municipalitiesWithExplicitSalarySourceLeads: current.filter(m => m.explicitSalaryLeadCount).length,
  distinctSourceLeadUrls: new Set(municipalities.flatMap(m => m.sourceLeads.map(l => l.url))).size,
  allRecordsBefore: baseline.overall.rows,
  allRecordsAfter: coverage.output.rows,
  allRecordsNetChange: coverage.output.rows - baseline.overall.rows,
  allEmployersBefore: baseline.overall.employers,
  allEmployersAfter: coverage.output.employers,
  replacedCompiledRecords: read(join(research, 'municipal-corrections/comparison.json')).summary.replacedRows,
}
save('coverage.json', { version: 1, asOf: roster.asOf, baselineCommit: baseline.repositoryCommit,
  scopeNotes: roster.scopeNotes, methodology: [
    'All roster entries received a bounded official-site link search; regional researchers also inspected finance/report/council archives. This is a province-wide inventory, not an exhaustive claim about every historical report.',
    'Only registered, hash-checked accepted source files count as official imported records. Each count is reconciled to the published employer exports.',
    'Archive links, search results, and dates in URLs are leads only. An indexed year is not a verified reporting period.',
    'The municipal denominator excludes Metro Vancouver regional district and pending Okanagan Falls; shíshálh Nation Government District is retained as a distinct governance case.',
    'Names and initials are observations as disclosed, not verified unique people; below-threshold aggregate payroll is not converted to individual records.',
  ], summary, collections, municipalities })
const lines = [
  '# BC municipal salary coverage audit', '', `As of **${roster.asOf}**. Generated by \`npm run audit:municipal-salaries\` after rebuilding the salary exports.`, '',
  `The roster covers **${summary.currentJurisdictions} current jurisdictions** and **${summary.pendingJurisdictions} pending incorporation**. Every entry was checked for public official-site source links. Accepted official salary coverage grew from **${summary.withOfficialRecordsBefore} to ${summary.withOfficialRecordsAfter} municipalities**. **${summary.withNoOfficialRecords} current jurisdictions still lack accepted official records**; finding a link is not a completed import.`, '',
  `This pass adds **${fmt(summary.newlyAcceptedRecords)} official observations** from **${summary.newlyAcceptedSourceCohorts} employee/council cohorts** covering **${summary.newlyAcceptedReportYears} municipality-years**. It replaces **${fmt(summary.replacedCompiledRecords)} proved duplicate compiled observations**, for a net increase of **${fmt(summary.allRecordsNetChange)} records** across the entire salary dataset.`, '',
  '## Added collections', '', '| Collection | Municipalities | Report years | Employee rows | Council rows | Total rows |', '|---|---:|---:|---:|---:|---:|',
  ...collections.map(c => `| [${c.collection}](../${c.collection}/README.md) | ${c.municipalities} | ${c.reportYears} | ${fmt(c.employeeRecords)} | ${fmt(c.councilRecords)} | ${fmt(c.records)} |`), '',
  '## All jurisdictions', '',
  'Calendar years below refer to accepted original schedules. Compiled edition labels remain unverified and can overlap official records until a complete cohort is proved. A dash means no accepted records in that category, not zero employees or no public report. Each municipality links to its official archive or website; the machine-readable audit contains every retained lead and hold.', '',
  '| Municipality / official source | Employee calendar years | Council calendar years | Official rows | Compiled rows | Next step |', '|---|---|---|---:|---:|---|',
  ...municipalities.map(m => `| [${md(m.employerName)}](${m.archiveUrl})${m.status === 'pending-incorporation' ? ' (pending)' : ''} | ${m.officialEmployeeYears.join(', ') || '—'} | ${m.officialCouncilYears.join(', ') || '—'} | ${fmt(m.officialRecords)} | ${fmt(m.compiledUnverifiedRecords)} | ${md(m.nextAction)} |`), '',
  '## How to use this inventory', '',
  '- [Complete machine-readable coverage and source inventory](coverage.json) includes all source links, accepted IDs, reporting years, caveats, and held-source actions.',
  '- [Roster and scope](roster.json) preserve the provincial workbook and directory crosswalk. Okanagan Falls is pending incorporation on 6 November 2026; Metro Vancouver is a regional district and is outside this denominator.',
  '- [Compiled-period comparison](../municipal-corrections/comparison.json) documents exact full-cohort matches and unresolved overlaps. Individual source values are not adjusted to make controls match.',
  '- [Source discovery receipts](discovery) record requests and links, including unsuccessful checks. Archive policies, audited financial statements and annual reports may not contain a named remuneration schedule.',
  '- Reports still requiring OCR, an adopted version, a corrected subtotal or a public-record request remain outside accepted imports. No requests were sent to municipalities in this pass.',
  '',
]
writeFileSync(join(out, 'coverage.md'), lines.join('\n'))
console.log(JSON.stringify(summary, null, 2))
