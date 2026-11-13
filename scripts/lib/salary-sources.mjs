// Build a source register from accepted manifests and research leads without treating a
// located PDF as imported data. A shared PDF can be accepted for one employer and held
// for another, so source decisions are keyed by employer, period, and document URL.
import { canonicalSlug } from './salary-employers.mjs'

const acceptedStatuses = new Set(['accepted', 'verified', 'imported'])
const notes = (value) => value == null ? [] : Array.isArray(value) ? value : [value]
const urlOf = (source) => source.sourceUrl ?? source.url ?? null
const employersOf = (source) => source.employers?.map((entry) => typeof entry === 'string' ? entry : entry.slug ?? entry.employerSlug)
  ?? (source.employerSlug ? [source.employerSlug] : [])
const keyOf = (source) => JSON.stringify([source.employerSlug, source.year, source.url, source.scope])
const precedence = (status) => status === 'imported' ? 3 : status === 'held-for-review' ? 2 : 1

export const hasLocatedSource = (leads = []) => leads.some((lead) => lead.url && [
  'source-found-awaiting-extraction', 'official-source-indexed-awaiting-validation',
  'requires-ocr', 'held-for-review'
].includes(lead.status))

export function sourceCatalog (backlog = {}, collections = []) {
  const byKey = new Map()
  const add = (source, employer, extra = {}) => {
    if (!employer) return
    const entry = {
      id: source.id ?? source.sourceId ?? `${employer}-${source.year}`,
      employerSlug: canonicalSlug(employer), year: source.year ?? source.label ?? null,
      title: source.title ?? source.sourceTitle ?? `${source.employerName ?? employer} ${source.year ?? ''} disclosure`,
      url: urlOf(source), indexUrl: source.indexUrl ?? source.sourceIndexUrl ?? null,
      status: source.status ?? 'source-found-awaiting-extraction',
      scope: source.category ?? source.scope ?? null,
      reason: source.reason ?? null,
      nextAction: source.nextAction ?? source.reason ?? 'Verify the report period, employee schedule, extraction completeness, and totals before importing.',
      notes: notes(source.notes), ...extra
    }
    const key = keyOf(entry)
    const old = byKey.get(key)
    if (!old || precedence(entry.status) >= precedence(old.status)) byKey.set(key, entry)
  }
  for (const lead of backlog.sources ?? []) {
    // A stale handwritten "imported" label cannot certify data. Accepted manifests below
    // must establish the document, employer and year that actually reached the build.
    // A lead for an employer not yet in the dataset carries the employer's disclosed name.
    add(lead, lead.employerSlug, { ...(lead.employerName ? { employerName: lead.employerName } : {}), ...(lead.status === 'imported'
      ? { status: 'source-found-awaiting-extraction', nextAction: 'Reconcile this source lead with an accepted source manifest.' } : {}) })
  }
  for (const { collection, manifest } of collections) {
    for (const source of manifest.aggregateOnlySources ?? []) {
      if (source.status === 'verified-aggregate-only') add(source, source.employerSlug, { collection, status: 'aggregate-only', scope: 'aggregate-only', rows: 0,
        nextAction: 'Aggregate payroll and the absence of a named schedule were verified. No individual records are created from aggregate figures.' })
    }
    for (const source of manifest.sources ?? []) {
      const accepted = source.file && (!source.status || acceptedStatuses.has(source.status))
      for (const employer of employersOf(source)) {
        const details = source.employers?.find((entry) => typeof entry === 'object' && (entry.slug ?? entry.employerSlug) === employer)
        add(source, employer, {
          collection, status: accepted ? 'imported' : 'held-for-review',
          acceptedSourceId: accepted ? source.id : null,
          rows: accepted ? (details?.rowCount ?? source.rowCount ?? null) : 0,
          nextAction: accepted ? 'Accepted normalized records are included in the build; see the source manifest for validation and reporting scope.' : source.reason ?? 'Resolve the source validation issue before importing.'
        })
      }
      for (const held of source.deferredEmployers ?? []) {
        add({ ...source, ...held, id: source.id, year: source.year ?? source.label }, held.slug ?? held.employerSlug, {
          collection, status: 'held-for-review', acceptedSourceId: null, rows: 0,
          nextAction: held.reason ?? 'Resolve the source discrepancy before importing.'
        })
      }
    }
    for (const source of manifest.unparsedSources ?? []) {
      // A filename slug (e.g. 2010-11) is not an employer mapping.
      for (const employer of employersOf(source)) add(source, employer, { collection })
    }
    for (const source of manifest.deferredEmployers ?? manifest.deferred ?? []) {
      add(source, source.employerSlug ?? source.slug, { collection, status: 'held-for-review', rows: 0 })
    }
  }
  const entries = [...byKey.values()]
  // An unclassified document lead is satisfied by an accepted cohort from that
  // document. Explicitly different cohorts and held sources remain separate.
  return entries.filter((entry) => entry.scope || entry.status === 'imported' || entry.status === 'held-for-review' || !entries.some((accepted) =>
    accepted.status === 'imported' && accepted.employerSlug === entry.employerSlug && accepted.year === entry.year && accepted.url === entry.url))
    .sort((a, b) => a.employerSlug.localeCompare(b.employerSlug) || String(a.year).localeCompare(String(b.year)) || String(a.url).localeCompare(String(b.url)) || String(a.scope).localeCompare(String(b.scope)))
}

export const sourceLeadsFor = (catalog, employer, year) => catalog
  .filter((entry) => entry.employerSlug === employer && entry.year === year && entry.status !== 'imported')
  .map(({ id, title, url, status, reason, nextAction, notes }) => ({ id, title, url, status, reason, nextAction, notes }))

// A later collection register (research/audits/*/collection-priorities.json) records what a
// review recovered after the pinned backlog was reconciled: the original retrieved and
// fingerprinted, approval verified or still held. The pinned backlog stays as it was; each
// register lead becomes the current state of its source, and the earlier blocker is kept as
// dated history in its notes. Nothing here accepts rows: acceptance still needs a manifest.
// A lead later accepted through a manifest names it (accepted_source_ids). The claim is checked
// against the loaded manifests, and the lead then yields to that manifest's own catalog entry.
const acceptedLeadSources = (lead, slug, manifests) => {
  const ids = lead.accepted_source_ids
  if (!Array.isArray(ids) || !ids.length || lead.acceptance_status !== 'accepted-via-source-manifest') {
    throw new Error(`Collection lead ${lead.id} claims accepted rows; accept them through a manifest`)
  }
  if (!manifests) throw new Error(`Collection lead ${lead.id} claims accepted rows; the accepting manifests are needed to check it`)
  let rows = 0
  for (const id of ids) {
    const source = manifests.flatMap(({ manifest }) => manifest.sources ?? []).find((entry) => entry.id === id)
    if (!source || !source.file || (source.status && !['accepted', 'verified', 'imported'].includes(source.status))) throw new Error(`Collection lead ${lead.id} names no accepted manifest source ${id}`)
    if (source.employerSlug !== slug || (source.year ?? source.label) !== lead.reporting_period || source.sourceUrl !== lead.source_url ||
      source.sha256 !== lead.binary?.sha256 || source.registerLead !== lead.id) throw new Error(`Collection lead ${lead.id}: accepted source ${id} is a different document, employer or period`)
    rows += source.rowCount
  }
  if (rows !== lead.accepted_employee_rows) throw new Error(`Collection lead ${lead.id} claims ${lead.accepted_employee_rows} accepted rows; its manifests hold ${rows}`)
}
const leadStatus = (lead) => {
  if (lead.accepted_employee_rows) throw new Error(`Collection lead ${lead.id} claims accepted rows; accept them through a manifest`)
  // Approval not yet established is awaiting validation, not a failed check (held-for-review).
  if (!/approval-verified$/.test(lead.source_status ?? '')) return 'official-source-indexed-awaiting-validation'
  return /scanned/.test(lead.binary?.extraction_mode ?? '') ? 'requires-ocr' : 'source-found-awaiting-extraction'
}

export function applyCollectionRegisters (backlog = {}, registers = [], manifests = null) {
  const sources = [...(backlog.sources ?? [])]
  for (const { path, register } of registers) {
    for (const lead of register.leads ?? []) {
      const earlier = lead.existing_backlog_id ? sources.find((entry) => entry.id === lead.existing_backlog_id) : null
      if (lead.existing_backlog_id && !earlier) throw new Error(`Collection lead ${lead.id} names unknown backlog entry ${lead.existing_backlog_id}`)
      const slug = canonicalSlug(lead.employer_slug ?? earlier?.employerSlug ?? lead.employer.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''))
      if (lead.accepted_employee_rows) {
        // Superseded by its accepted manifest: the backlog lead goes, and the manifest's
        // imported entry (same employer, period and document) is the source's current state.
        acceptedLeadSources(lead, slug, manifests)
        if (earlier && earlier.sourceUrl !== lead.source_url) throw new Error(`Collection lead ${lead.id} points to a different document than ${earlier.id}`)
        if (earlier) sources.splice(sources.indexOf(earlier), 1)
        continue
      }
      const history = (earlier?.blockers ?? []).map((blocker) => `Earlier state (backlog reviewed ${earlier.reviewedOn ?? 'undated'}): ${blocker.reason}`)
      sources.push({
        id: lead.id,
        employerSlug: slug,
        employerName: lead.employer,
        year: lead.reporting_period,
        title: earlier?.title ?? `${lead.employer} Statement of Financial Information ${lead.reporting_period}`,
        sourceUrl: lead.source_url,
        indexUrl: lead.official_index_url ?? earlier?.indexUrl ?? null,
        scope: earlier?.scope ?? 'employee-remuneration',
        status: leadStatus(lead),
        nextAction: lead.next_action,
        notes: [
          `Current state from ${path} (reviewed ${register.reviewed_on}): ${lead.source_status}; ${lead.acceptance_status}. Original SHA-256 ${lead.binary?.sha256 ?? 'not recorded'}.`,
          lead.approval?.supports ?? lead.approval?.limitation ?? null,
          lead.progress_from_held_work ?? null,
          ...history
        ].filter(Boolean)
      })
      // The register's lead supersedes the backlog's view of the same document.
      if (earlier && earlier.sourceUrl !== lead.source_url) throw new Error(`Collection lead ${lead.id} points to a different document than ${earlier.id}`)
      if (earlier) sources.splice(sources.indexOf(earlier), 1)
    }
  }
  return { ...backlog, sources }
}
