// Merges a research batch handed back from research/queue/ into the sub-agency research files,
// after checking it against the rules in research/queue/README.md. Nothing is written unless the
// whole batch passes:
//
//   npm run research:merge -- path/to/batch-03-results.json [--dry-run]
//   npm run build:government
//
// A claim that competes with one already held is kept beside it, never over it, and the record is
// marked for reconciliation: choosing between them is an editorial decision (research/decisions.json).

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const ROOT = process.env.GOVERNMENT_RESEARCH || 'research'
const RESEARCHED = resolve(ROOT, 'history/sub-agencies-researched.json')
const SOURCES = resolve(ROOT, 'history/sub-agencies-sources.json')
const QUEUE = resolve(ROOT, 'queue/sub-agencies.json')

export const PRECISIONS = ['day', 'month', 'year', 'decade', 'circa']
export const EVIDENCE = ['statute', 'order_in_council', 'regulation', 'news_release', 'annual_report', 'service_plan', 'estimates', 'public_accounts', 'official_webpage', 'archival_description', 'financial_statements', 'gazette', 'secondary']
export const COVERAGE = ['observation_only', 'documented_period', 'start_documented_end_unknown', 'continuing_as_of_source']
export const PARENT_RELATIONS = ['part_of', 'subsidiary_of']
export const SUCCESSION = ['formed_from', 'split_from', 'merged_into', 'replaced_by', 'absorbed']
// What a checkpoint search found; only the first two say the body is there, and only the last says it
// is not — and then only in the pages read.
export const OUTCOMES = { found_name: true, found_contextual_name: true, related_label_identity_unresolved: null, function_only: null, not_found_in_scope: false }
const SHAPE = { day: /^\d{4}-\d{2}-\d{2}$/, month: /^\d{4}-\d{2}$/, year: /^\d{4}$/, decade: /^\d{3}0s?$/, circa: /^\d{4}$/ }

/** Every problem with one handed-back batch, as readable lines; empty when it may be merged. */
export function validate(batch, { known = new Set(), catalogue = new Map(), asOf = '9999-12-31' } = {}) {
  const errors = []
  const warnings = []
  const incoming = new Map((batch.sources ?? []).map((source) => [source.id, source]))
  for (const source of batch.sources ?? []) {
    if (!source.id || !source.url) errors.push(`source ${JSON.stringify(source)}: needs id and url`)
    else if (catalogue.has(source.id) && catalogue.get(source.id).url !== source.url) errors.push(`source ${source.id}: id already used for ${catalogue.get(source.id).url}`)
  }
  const sourced = (where, row) => {
    if (!row.source) errors.push(`${where}: no source URL`)
    if (!row.locator) errors.push(`${where}: no locator (page, section or paragraph)`)
    if (row.evidence && !EVIDENCE.includes(row.evidence)) warnings.push(`${where}: unfamiliar evidence type "${row.evidence}"`)
    if (row.source_id && !catalogue.has(row.source_id) && !incoming.has(row.source_id)) warnings.push(`${where}: source_id ${row.source_id} is not in the catalogue or this batch's sources`)
  }
  const dated = (where, claim) => {
    if (!claim || claim.date === null || claim.date === undefined) return
    const date = String(claim.date)
    if (!PRECISIONS.includes(claim.precision)) errors.push(`${where}: precision must be one of ${PRECISIONS.join(', ')}`)
    else if (!SHAPE[claim.precision].test(date)) errors.push(`${where}: "${date}" does not match precision "${claim.precision}" (a year stays "2004", never "2004-01-01")`)
    if (date.slice(0, 10) > asOf) errors.push(`${where}: ${date} is after ${asOf}`)
    sourced(where, claim)
  }
  const period = (where, row) => {
    if (!COVERAGE.includes(row.coverage)) errors.push(`${where}: coverage must be one of ${COVERAGE.join(', ')}`)
    if (row.coverage === 'observation_only' && !row.observed_on) errors.push(`${where}: an observation needs observed_on`)
    if (row.coverage !== 'observation_only' && !row.from) errors.push(`${where}: a period needs from (or record it as an observation)`)
    sourced(where, row)
  }
  for (const record of [...(batch.records ?? []), ...(batch.gone ?? [])]) {
    const at = `record ${record.id ?? '(no id)'}`
    if (!record.id) { errors.push(`${at}: no id`); continue }
    const gone = (batch.gone ?? []).includes(record)
    if (!gone && !known.has(record.id)) errors.push(`${at}: not a sub-agency in the queue (bodies that no longer exist go in "gone")`)
    if (gone && !record.ended?.date) errors.push(`${at}: a body in "gone" needs ended`)
    if (!record.review?.checked || !/^\d{4}-\d{2}-\d{2}$/.test(record.review.checked)) errors.push(`${at}: review.checked must be the day the research was done (YYYY-MM-DD)`)
    dated(`${at} established`, record.established)
    dated(`${at} ended`, record.ended)
    dated(`${at} first_observed`, record.first_observed)
    ;(record.research_events ?? []).forEach((event, i) => { if (!event.type) errors.push(`${at} research_events[${i}]: no type`); dated(`${at} research_events[${i}]`, event) })
    ;(record.date_claims ?? []).forEach((claim, i) => dated(`${at} date_claims[${i}]`, claim))
    ;(record.names ?? []).forEach((row, i) => { if (!row.name) errors.push(`${at} names[${i}]: no name`); period(`${at} names[${i}]`, row) })
    ;(record.parents ?? []).forEach((row, i) => {
      if (!row.ministry_as_printed) errors.push(`${at} parents[${i}]: no ministry_as_printed`)
      if (!PARENT_RELATIONS.includes(row.relation ?? 'part_of')) errors.push(`${at} parents[${i}]: relation "${row.relation}" is not parentage; record funding or appointment in note or research_events`)
      period(`${at} parents[${i}]`, row)
    })
    ;(record.relations ?? []).forEach((row, i) => {
      if (!SUCCESSION.includes(row.type)) errors.push(`${at} relations[${i}]: type must be one of ${SUCCESSION.join(', ')}`)
      if (!row.body) errors.push(`${at} relations[${i}]: no body id`)
      dated(`${at} relations[${i}]`, row)
      if (!row.date) sourced(`${at} relations[${i}]`, row)
    })
    if (record.legal_basis && (!record.legal_basis.citation || !record.legal_basis.source)) errors.push(`${at} legal_basis: needs citation and source`)
    ;(record.review?.sources_checked ?? []).forEach((check, i) => {
      if (!check.source) errors.push(`${at} review.sources_checked[${i}]: no source`)
      if (check.outcome === undefined) {
        if (typeof check.listed !== 'boolean') errors.push(`${at} review.sources_checked[${i}]: listed must be true or false, or give an outcome`)
      } else if (!(check.outcome in OUTCOMES)) errors.push(`${at} review.sources_checked[${i}]: outcome must be one of ${Object.keys(OUTCOMES).join(', ')}`)
      else if ((check.listed ?? null) !== OUTCOMES[check.outcome]) errors.push(`${at} review.sources_checked[${i}]: outcome ${check.outcome} needs listed ${OUTCOMES[check.outcome]}`)
      if (check.listed === false && !check.scope && !check.locator) warnings.push(`${at} review.sources_checked[${i}]: a non-match should say which pages were read (scope)`)
    })
  }
  return { errors, warnings }
}

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)
const append = (list, rows) => { for (const row of rows ?? []) if (!list.some((held) => same(held, row))) list.push(row) }

/** Folds one checked batch into the research file's records, returning what changed. */
export function merge(research, catalogue, batch, queueItems = new Map()) {
  const log = []
  const byId = new Map([...research.records, ...(research.gone ?? [])].map((record) => [record.id, record]))
  for (const source of batch.sources ?? []) if (!catalogue.sources.some((held) => held.id === source.id)) catalogue.sources.push(source)
  const fold = (record, list) => {
    let held = byId.get(record.id)
    if (!held) {
      const item = queueItems.get(record.id) ?? {}
      held = {
        id: record.id,
        name: record.name ?? item.name,
        kind: record.kind ?? item.kind ?? null,
        parent_today: record.parent_today ?? item.parent_today ?? null,
        parent_today_name: item.parent_today_name ?? null,
        official_url: item.official_url ?? null,
        source_today: item.source_today ?? null,
        description: item.description ?? null,
        established: null, ended: null, first_observed: null,
        names: [], parents: [], relations: [], research_events: [], date_claims: [],
        legal_basis: null, evidence_status: null, note: '',
        review: { checked: null, sources_checked: [] }
      }
      list.push(held)
      byId.set(held.id, held)
      log.push(`${record.id}: new record`)
    }
    for (const field of ['established', 'ended']) {
      const claim = record[field]
      if (!claim?.date) continue
      if (!held[field]?.date) { held[field] = claim; log.push(`${record.id}: ${field} ${claim.date}`) } else if (!same(held[field], claim) && String(held[field].date) !== String(claim.date)) {
        append(held.date_claims ??= [], [{ ...claim, type: field === 'established' ? 'establishment_claim' : 'end_claim', summary: claim.meaning ?? `A competing ${field === 'established' ? 'start' : 'end'}` }])
        held.evidence_status = 'requires_reconciliation'
        log.push(`${record.id}: ${field} ${claim.date} competes with ${held[field].date}; kept both, marked for reconciliation`)
      }
    }
    // The first sighting is the earliest one; a later one is still kept among the checks.
    if (record.first_observed?.date && (!held.first_observed?.date || String(record.first_observed.date) < String(held.first_observed.date))) {
      held.first_observed = record.first_observed
      log.push(`${record.id}: first seen ${record.first_observed.date}`)
    }
    for (const field of ['names', 'parents', 'relations', 'research_events', 'date_claims']) {
      const before = (held[field] ??= []).length
      append(held[field], record[field])
      if (held[field].length > before) log.push(`${record.id}: ${held[field].length - before} ${field}`)
    }
    if (record.legal_basis && !held.legal_basis) held.legal_basis = record.legal_basis
    else if (record.legal_basis && !same(record.legal_basis, held.legal_basis)) append(held.research_events ??= [], [{ type: 'legal_basis_claim', date: null, summary: record.legal_basis.citation, ...record.legal_basis }])
    if (record.evidence_status && held.evidence_status !== 'requires_reconciliation') held.evidence_status = record.evidence_status
    if (record.note && !String(held.note ?? '').includes(record.note)) held.note = [held.note, record.note].filter(Boolean).join(' ')
    const review = (held.review && typeof held.review === 'object') ? held.review : (held.review = {})
    review.checked = [review.checked, record.review?.checked].filter(Boolean).sort().at(-1) ?? null
    append(review.sources_checked ??= [], record.review?.sources_checked)
    if (record.review?.unresolved_fields) review.unresolved_fields = record.review.unresolved_fields
    if (record.review?.scope) review.scope = [review.scope, record.review.scope].filter((s, i, all) => s && all.indexOf(s) === i).join('; ')
    if (record.review?.by) review.by = [review.by, record.review.by].filter((s, i, all) => s && all.indexOf(s) === i).join('; ')
    review.full_history_complete = Boolean(record.review?.full_history_complete)
  }
  for (const record of batch.records ?? []) fold(record, research.records)
  for (const record of batch.gone ?? []) fold(record, research.gone ??= [])
  return log
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [path, flag] = process.argv.slice(2)
  if (!path) { console.error('usage: npm run research:merge -- <results.json> [--dry-run]'); process.exit(2) }
  const read = (file) => JSON.parse(readFileSync(file, 'utf8'))
  const raw = read(path)
  const batch = Array.isArray(raw) ? { records: raw } : raw
  const research = read(RESEARCHED)
  const catalogue = read(SOURCES)
  const queue = read(QUEUE)
  const queueItems = new Map(queue.items.map((item) => [item.id, item]))
  const known = new Set([...queueItems.keys(), ...research.records.map((r) => r.id)])
  const { errors, warnings } = validate(batch, { known, catalogue: new Map(catalogue.sources.map((s) => [s.id, s])), asOf: queue.as_of })
  for (const warning of warnings) console.warn(`warning: ${warning}`)
  if (errors.length) {
    for (const error of errors) console.error(`error: ${error}`)
    console.error(`\n${errors.length} problem${errors.length === 1 ? '' : 's'}; nothing was merged. Fix the batch and run again.`)
    process.exit(1)
  }
  const log = merge(research, catalogue, batch, queueItems)
  for (const line of log) console.log(line)
  if (flag === '--dry-run') { console.log('\ndry run: nothing written'); process.exit(0) }
  writeFileSync(RESEARCHED, JSON.stringify(research, null, 2) + '\n')
  writeFileSync(SOURCES, JSON.stringify(catalogue, null, 2) + '\n')
  console.log(`\nmerged ${(batch.records ?? []).length + (batch.gone ?? []).length} records. Now run: npm run build:government`)
}
