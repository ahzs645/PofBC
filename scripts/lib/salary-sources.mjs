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
    add(lead, lead.employerSlug, lead.status === 'imported'
      ? { status: 'source-found-awaiting-extraction', nextAction: 'Reconcile this source lead with an accepted source manifest.' } : {})
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
  .map(({ id, title, url, status, nextAction, notes }) => ({ id, title, url, status, nextAction, notes }))
