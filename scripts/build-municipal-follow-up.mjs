// Turn the complete reviewed municipal audit into an actionable acquisition and processing list.
// No live requests, inferred reporting years, new source acceptance or invented contact details.
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const folder = join(root, 'research/salaries/municipal-audit')
const read = (file) => JSON.parse(readFileSync(join(folder, file), 'utf8'))
const coverage = read('coverage.json')
const policy = read('import-policy.json')
const ocrFolder = join(root, 'research/salaries/municipal-ocr')
const ocrRegister = existsSync(join(ocrFolder, 'ocr-register.json')) ? JSON.parse(readFileSync(join(ocrFolder, 'ocr-register.json'), 'utf8')) : null
const ocrRequests = existsSync(join(ocrFolder, 'additional-requests.json')) ? JSON.parse(readFileSync(join(ocrFolder, 'additional-requests.json'), 'utf8')).requests : []
const municipalityBySlug = new Map(coverage.municipalities.map((m) => [m.employerSlug, m]))
const mtext = (text) => String(text ?? '—').replaceAll('|', '\\|').replaceAll('\n', ' ')
const requestOverrides = new Map([
  ['city-of-abbotsford', { year: null, blocker: 'Official finance page says SOFI is available on request; no accepted official records.',
    ask: 'Public adopted 2025 SOFI employee and council schedules and existing spreadsheet/CSV; an index of earlier available years and amendments.',
    route: 'routine-public-record-request', url: 'https://www.abbotsford.ca/city-hall/finance' }],
  ['city-of-west-kelowna', { year: '2025', blocker: 'Linked report is labelled draft and its approval page is unsigned.',
    ask: 'Final/adopted 2025 SOFI, or the adoption resolution and confirmation that the linked tables are the adopted version.',
    route: 'final-version-or-adoption-evidence' }],
  ['city-of-salmon-arm', { year: '2025', blocker: 'SOFI-labelled download contains financial statements without the named remuneration schedules.',
    ask: 'Actual adopted 2025 employee and council remuneration/expense schedules, including amendments and existing electronic tables.',
    route: 'missing-schedules' }],
  ['district-of-new-hazelton', { year: null, blocker: 'Attachment filename says 2023 but its first remuneration schedule says 2022.',
    ask: 'Separate adopted 2022 and 2023 employee and council schedules, with confirmation of each schedule’s reporting period.',
    route: 'reporting-period-clarification' }],
])
const sourceTasks = coverage.municipalities.flatMap((m) => m.heldOrUnparsedSources.map((s, at) => {
  const specific = requestOverrides.get(m.employerSlug)
  const needsRequest = specific && (specific.year == null || specific.year === s.year)
  const description = [s.reason, ...(s.notes ?? [])].join(' ')
  const ocr = ocrRegister?.sources.find((r) => r.sourceUrl === s.url)
  const scanned = s.status === 'requires-ocr' || /scann|requires? OCR|no extractable text|image-based/i.test(description)
  const retrieval = /HTTP|403|404|retriev.*fail|download.*fail|inaccessible/i.test(description)
  const route = needsRequest ? specific.route : ocr?.pageDiscoveryComplete ? 'verify-completed-ocr-or-layout' : scanned ? 'ocr-and-independent-review' : retrieval ? 'public-retrieval-or-routine-copy-request' : 'public-source-processing'
  return { id: s.id ?? `${m.employerSlug}-${s.year ?? 'period-unverified'}-${at}`, employerSlug: m.employerSlug,
    municipality: m.employerName, year: s.year, periodVerified: false, scope: s.scope ?? null, status: s.status,
    sourceUrl: s.url, archiveUrl: s.indexUrl ?? m.archiveUrl, blocker: s.reason ?? 'Located source has not completed extraction and validation.',
    route, nextAction: needsRequest ? specific.ask : ocr?.pageDiscoveryComplete ? `${s.nextAction} OCR discovery is complete for all ${ocr.discoveryPages} pages, with ${ocr.candidatePages.length} two-pass candidate pages retained. Verify names, titles, actual periods and complete controls against the originals before importing; keyword discovery is not proof of exhaustive table coverage.` : scanned ? 'OCR/transcribe the existing public original, then independently verify all row fields, reporting period, pages and controls. An existing spreadsheet is an optional shortcut.' : s.nextAction,
    ocrEvidence: ocr ? { file: `../municipal-ocr/${ocr.evidenceFile}`, sha256: ocr.evidenceSha256, pages: ocr.discoveryPages, candidatePages: ocr.candidatePages, status: ocr.status } : null,
    requestNeededNow: Boolean(needsRequest), requestStatus: 'not-sent',
    notes: s.notes ?? [] }
}))
const qualifiedSources = policy.qualifiedSources.map((decision) => {
  const m = municipalityBySlug.get(decision.employerSlug)
  const s = m?.acceptedSources.find((s) => s.id === decision.sourceId)
  if (!s || s.rows !== decision.rows) throw new Error(`${decision.sourceId}: qualified source not reconciled in municipal audit`)
  return { ...decision, municipality: m.employerName, sourceUrl: s.sourceUrl,
    sourceSha256: s.sourceSha256, dataSha256: s.dataSha256, archiveUrl: s.sourceIndexUrl,
    requestStatus: 'not-sent', route: 'source-control-clarification',
    ask: `Explain the recorded component differences (${decision.componentResiduals.join(', ')} CAD; row sums minus controls), or provide an amended ${decision.year} schedule and existing electronic file. Do not allocate differences to an individual without source evidence.` }
})
const requests = [
  ...[...requestOverrides].map(([slug, entry]) => {
    const m = municipalityBySlug.get(slug)
    const sources = sourceTasks.filter((s) => s.employerSlug === slug && (entry.year == null || s.year === entry.year))
    return { employerSlug: slug, municipality: m.employerName, ...entry,
      archiveUrl: entry.url ?? sources[0]?.archiveUrl ?? m.archiveUrl, sourceUrls: sources.map((s) => s.sourceUrl),
      firstRoute: 'Check the linked public archive for the final/correct schedule, then ask Finance or Corporate Services routinely.',
      formalAccessFallback: 'Only if routine access does not resolve it: verify the municipality’s official access-to-information process, recipient and any fee before filing.',
      contactVerified: false, requestStatus: 'not-sent' }
  }),
  ...qualifiedSources.map((s) => ({ ...s, year: s.year, blocker: s.action,
    firstRoute: 'Routine clarification/correction request to Finance; accepted published rows remain in the app with their warning.',
    formalAccessFallback: 'If necessary, request existing source tables/corrections through the verified official access process; an access request cannot require a new explanation to be created.',
    contactVerified: false })),
  ...ocrRequests.map((s) => ({ ...s, blocker: s.ask, requestStatus: 'not-sent', contactVerified: false,
    firstRoute: 'Routine public-record or clarification request to Finance or Corporate Services.',
    formalAccessFallback: 'Verify the official access process only if routine access does not resolve it; seek existing records, not newly created explanations.' }))
]
const gaps = coverage.municipalities.filter((m) => m.status !== 'pending-incorporation' && !m.officialRecords).map((m) => ({
  employerSlug: m.employerSlug, municipality: m.employerName, archiveUrl: m.archiveUrl, website: m.website,
  status: m.salaryStatus, compiledUnverifiedRecords: m.compiledUnverifiedRecords,
  heldOrUnparsedSources: m.heldOrUnparsedSources.length, explicitSalaryLeadCount: m.explicitSalaryLeadCount,
  route: m.status === 'special-governance' ? 'separate-governance-review' : requestOverrides.has(m.employerSlug) ? requestOverrides.get(m.employerSlug).route : m.heldOrUnparsedSources.length ? 'process-or-resolve-listed-source-first' : m.explicitSalaryLeadCount ? 'validate-public-source-leads-first' : 'archive-search-then-routine-request',
  targetPeriod: 'Prioritize calendar 2025, then establish earlier available periods from actual schedules and an archive index. No complete list of missing historical years has been proved.',
  nextAction: m.status === 'special-governance' ? m.nextAction : requestOverrides.get(m.employerSlug)?.ask ?? m.nextAction,
  formalAccessFallback: m.status === 'special-governance' ? 'Do not assume ordinary municipal SOFI or provincial FOI requirements; establish applicable governance and voluntary disclosure routes.' : 'If a needed public schedule cannot be obtained routinely, verify the official access process and submit a narrowly scoped request for existing records.',
  requestStatus: 'not-sent'
}))
if (gaps.length !== coverage.summary.withNoOfficialRecords) throw new Error('Incomplete gap inventory')
const routeCounts = Object.fromEntries([...new Set(sourceTasks.map((s) => s.route))].sort().map((route) => [route, sourceTasks.filter((s) => s.route === route).length]))
const result = { version: 1, asOf: coverage.asOf, baseline: policy.baseline,
  scope: 'Municipal follow-up to PR #23. Other-sector requests remain in research/salaries/requests/source-requests-2026-10-30.md.',
  requestStatus: 'Draft list only. No messages, formal access requests or fee commitments have been made.',
  summary: { qualifiedCohorts: qualifiedSources.length, additionalRows: qualifiedSources.reduce((n, s) => n + s.rows, 0),
    currentJurisdictionsWithoutOfficialRecords: gaps.length, unresolvedSourceTasks: sourceTasks.length,
    specificRequestCandidates: requests.length, sourceTasksByRoute: routeCounts,
    ocr: ocrRegister?.summary ?? null },
  qualifiedSources, requests, jurisdictionsWithoutOfficialRecords: gaps, sourceTasks,
  pending: coverage.municipalities.filter((m) => m.status === 'pending-incorporation').map((m) => ({ employerSlug: m.employerSlug, effectiveFrom: m.effectiveFrom, nextAction: m.nextAction })) }
writeFileSync(join(folder, 'follow-up.json'), JSON.stringify(result, null, 2) + '\n')
const csvRows = [
  ...requests.map((r) => ['request', r.municipality, r.year ?? 'period to verify', r.route, r.archiveUrl, r.sourceUrl ?? r.sourceUrls?.join(' '), r.blocker, r.ask, r.requestStatus]),
  ...gaps.map((r) => ['jurisdiction gap', r.municipality, 'available years to establish', r.route, r.archiveUrl, '', r.status, r.nextAction, r.requestStatus]),
  ...sourceTasks.map((r) => ['source processing', r.municipality, r.year ?? 'period to verify', r.route, r.archiveUrl, r.sourceUrl, r.blocker, r.nextAction, r.requestStatus]),
]
const quote = (s) => `"${String(s ?? '').replaceAll('"', '""')}"`
writeFileSync(join(folder, 'follow-up.csv'), [['type', 'municipality', 'year or target', 'route', 'official archive', 'source', 'blocker', 'next action or request', 'request status'], ...csvRows].map((r) => r.map(quote).join(',')).join('\n') + '\n')
const lines = [
  '# Municipal import decisions and acquisition list', '', `As of ${coverage.asOf}. Generated by \`npm run follow-up:municipal-salaries\`.`, '',
  `The original PR #23 baseline has 878,615 records. The source-policy follow-up accepts **${result.summary.additionalRows.toLocaleString('en-CA')} further employee observations** in three cohorts, with visible source warnings.${ocrRegister ? ` The subsequent OCR review accepts **${ocrRegister.summary.acceptedRows} further employee/council observations**; [its full evidence and remaining work](../municipal-ocr/README.md) are separate from unaccepted OCR candidates.` : ''} The rebuilt app has **${coverage.summary.allRecordsAfter.toLocaleString('en-CA')} records**. No individual value is changed to force agreement.`, '',
  `**${gaps.length} current jurisdictions still have no accepted official records.** There are **${sourceTasks.length} unresolved source tasks**. These are separate counts: a jurisdiction can have multiple reports, and a covered jurisdiction can still have held years or council schedules. Neither count is a count of required FOI applications.`, '',
  '[Spreadsheet-ready complete list](follow-up.csv) · [Machine-readable evidence and actions](follow-up.json) · [Import assumptions and rules](import-policy.json)', '',
  '## What can enter the app', '',
  '| Municipality / original | Calendar year | Employee rows | Decision |', '|---|---|---:|---|',
  ...qualifiedSources.map((s) => `| [${s.municipality}](${s.sourceUrl}) | ${s.year} | ${s.rows.toLocaleString('en-CA')} | ${s.action} Component residuals (row sums minus controls): ${s.componentResiduals.join(', ')} CAD. |`), '',
  'Acceptance means the published rows were reproduced faithfully, not that the issuer’s subtotals have been explained. The exact residuals, original hashes, normalized hashes and reader comparisons are pinned. The app shows source caveats on employer and person pages and marks affected source links. No unresolved OCR, name/title boundary, reporting-year conflict or draft-only source is promoted by this policy.', '',
  'The earlier accepted source interpretations remain: actual calendar years; source-specific remuneration components; missing versus zero expenses; separately tracked council; published threshold exceptions; and compiled replacements only with complete proved matches. See [the policy](import-policy.json) and the collection evidence. Victoria’s early CSV/PDF reconciliation and other previously disclosed caveats remain open.', '',
  '## Specific records or clarifications to obtain', '',
  'Start with the linked public archive, then a routine request to Finance or Corporate Services for existing public schedules/electronic files. Contact recipients and formal access routes still need verification; the list does not invent email addresses. Use the public body’s verified formal access process only where needed. For a discrepancy, request existing corrected tables, source files or records of amendments; a formal request cannot compel a new explanation.', '',
  '| Municipality / official starting route | Period | What to obtain |', '|---|---|---|',
  ...requests.map((r) => `| [${r.municipality}](${r.archiveUrl}) | ${r.year ?? 'Verify period / available history'} | ${mtext(r.ask)} |`), '',
  '## All current jurisdictions lacking accepted official records', '',
  'This table includes processing work on already located sources. A scan does not automatically require FOI. Prioritize 2025, then establish older available years from actual reports; compiled fiscal-looking editions do not prove municipal calendar years. For ordinary municipalities, a public-record request is the fallback after archive work; the separate governance case has its own route.', '',
  '| Municipality / official starting route | Existing compiled rows | Route | Next useful action |', '|---|---:|---|---|',
  ...gaps.map((g) => `| [${g.municipality}](${g.archiveUrl}) | ${g.compiledUnverifiedRecords} | ${g.route} | ${mtext(g.nextAction)} |`), '',
  '## Existing sources needing processing', '',
  '| Work route | Source tasks |', '|---|---:|', ...Object.entries(routeCounts).map(([r, n]) => `| ${r} | ${n} |`), '',
  'Every source task, including older years and council cohorts at municipalities already covered, is listed with the source URL, recorded blocker and next action in the CSV and JSON above. Located-year labels remain unverified until the schedule is checked. OCR and multiline layouts need complete row review, not assumptions about omitted names or cells. Original spreadsheets are an optional acquisition shortcut.', '',
  '## Request text to adapt', '',
  '> Please provide the existing adopted Statement of Financial Information employee and council remuneration/expense schedules for [verified calendar years], any amended versions, and the existing Excel/CSV or other electronic tables used to publish them. Include the original headings, scope notes, row counts and printed control totals. We seek the already publicly disclosed cohort, not additional personal information or identities below the disclosure threshold. Please identify which earlier years remain available and any record-retention limits. For [specific discrepancy], please provide any existing corrected schedule or records of the correction. If routine release is unavailable, please advise the applicable formal access process and any fee estimate before costs are incurred.', '',
  'No requests have been sent. No fees have been authorized. shíshálh Nation Government District requires a separate governance review. Okanagan Falls is pending until 6 November 2026; earlier municipal years are not procurement gaps. The province-wide roster excludes Metro Vancouver regional district.', '',
  '## Reproduce', '', '```bash', 'npm run compare:municipal-periods', 'npm run build:salaries', 'npm run check:salaries', 'npm run audit:municipal-salaries', 'npm run follow-up:municipal-salaries', '```', '',
]
writeFileSync(join(folder, 'follow-up.md'), lines.join('\n'))
console.log(JSON.stringify(result.summary, null, 2))
