// Builds src/government/atlasData.js: the Lieutenant Governors as the Legislative Library records
// them, ministries' staffing by fiscal year, and the members of the 43rd Parliament.
//
// Each is kept as its source gives it, not reduced to what a single field would hold:
//
//   * A Lieutenant Governor's commission, the appointment's effective date and the swearing-in are
//     separate facts, and a commission does not make its holder the incumbent. The Library's list
//     numbers 31 Lieutenant Governors; administrators are listed apart, and one (December 1920) rests
//     on Wikipedia alone and says so.
//   * Staffing is full-time equivalents from the Public Accounts' Statement of Staff Utilization,
//     budget and actual kept apart, each with the ministry named as the statement printed it and the
//     statement's own words on what it counts.
//   * A member's party at election is not their caucus later; every later change is dated and
//     sourced, and where the Assembly's records and the announced affiliations differ, both are kept.
//
// Run with the research directory:
//
//   npm run build:government-atlas
//
// It reads the committed research in research/ (see research/README.md); GOVERNMENT_RESEARCH points it
// elsewhere.

import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { ledger } from './evidence-integrity.mjs'
import { MINISTRY_EPISODES } from '../src/government/episodes.js'

const accounting = ledger()
const ROOT = process.env.GOVERNMENT_RESEARCH || 'research'
const read = (path) => JSON.parse(readFileSync(resolve(ROOT, path), 'utf8'))
const OUT = resolve('src/government/atlasData.js')

// Election returns have their own observation date. They cannot refresh cabinet/office-holder
// facts checked earlier, or certify that a declared candidate has been sworn into office.
const finalCountPath = 'atlas/election-2026-final-count.json'
const finalCount = existsSync(resolve(ROOT, finalCountPath)) ? read(finalCountPath) : null
if (finalCount) {
  const actual = {}
  for (const candidate of finalCount.candidates) actual[candidate.party] = (actual[candidate.party] ?? 0) + 1
  if (finalCount.candidates.length !== finalCount.totalSeats ||
      new Set(finalCount.candidates.map((candidate) => candidate.district)).size !== finalCount.totalSeats ||
      Object.keys(actual).length !== Object.keys(finalCount.parties).length ||
      Object.entries(finalCount.parties).some(([party, total]) => actual[party] !== total)) {
    throw new Error('Election final-count candidates do not match the declared seat totals')
  }
  accounting.record(finalCountPath, 'accepted', finalCount, { reason: 'Declared election results, with recount qualifications; not a certified sitting-member or cabinet roster' })
}

// ── Lieutenant Governors ─────────────────────────────────────────────────────────────────────────

const lg = read('atlas/lieutenant-governors.json')
const lieutenantGovernors = lg.officeholders.map((holder) => ({
  sequence: holder.sequence ?? null,
  name: holder.name,
  category: holder.category,
  commissioned: holder.commissioned ?? null,
  effective: holder.effective ?? null,
  sworn: holder.sworn_in ?? null,
  // In office from the swearing-in, or failing that the effective date; a commission alone is not
  // taking office.
  from: holder.sworn_in ?? holder.effective ?? null,
  to: holder.end ?? null,
  evidence: holder.evidence_status ?? 'unreviewed',
  source: holder.source_url ?? lg.source?.url ?? null,
  locator: holder.locator ?? null,
  note: holder.notes ?? null,
  periodAsStated: holder.period_as_stated ?? null,
  datePrecision: holder.date_precision ?? null
})).filter((holder) => holder.from)
for (const holder of lg.officeholders) accounting.record(`lieutenant-governors.json#${holder.name}/${holder.period_as_stated ?? holder.sworn_in ?? holder.effective}`, holder.sworn_in || holder.effective ? 'accepted' : 'unresolved_unmapped', holder, { reason: holder.sworn_in || holder.effective ? 'Dated officeholder' : 'No supported start; stated period retained in audit' })
lieutenantGovernors.sort((a, b) => a.from.localeCompare(b.from))

// ── Staffing ─────────────────────────────────────────────────────────────────────────────────────

const STOP = new Set(['of', 'and', 'the', 'for', 'minister', 'ministry', 'department', 'dept', 'provincial', 'responsible'])
const words = (name) => String(name).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[‘’ʼ']/g, '').replace(/&/g, ' and ').replace(/-/g, ' ')
  .replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter((word) => word && !STOP.has(word))
const key = (name) => words(name).join(' ')

/** Rows that are not ministries, by the body the diagram draws for them. */
const BODIES = [
  [/^legislation$|legislative assembly/i, 'legislative-assembly'],
  [/office of the premier/i, 'office-of-the-premier'],
  [/public service agency/i, 'bc-public-service-agency']
]

const standsIn = (episode, year) => episode.from <= year && (episode.to === null || episode.to >= year)
const staffing = read('atlas/staffing.json')

// Rows the name matcher cannot place are reviewed in atlas/staffing-scope-review.json: a combined
// row (Officers of the Legislature, Other Appropriations) stays an aggregate and is never given to
// one node; a single ministry row is mapped only to an existing node, with its dated evidence.
const scopeReviewPath = 'atlas/staffing-scope-review.json'
const scopeReview = existsSync(resolve(ROOT, scopeReviewPath)) ? read(scopeReviewPath) : { aggregate_scopes: [], ministry_mappings: [] }
const episodeIds = new Set(MINISTRY_EPISODES.map((episode) => episode.id))
for (const mapping of scopeReview.ministry_mappings) {
  if (!episodeIds.has(mapping.output_id)) throw new Error(`Reviewed staffing mapping names an unknown ministry: ${mapping.output_id}`)
  const hits = staffing.measures.filter((measure) => measure.fiscal_year === mapping.fiscal_year && measure.basis === mapping.basis && measure.ministry_as_printed === mapping.ministry_as_printed)
  if (hits.length !== 1) throw new Error(`Reviewed staffing mapping matches ${hits.length} measures: ${mapping.fiscal_year} ${mapping.basis} ${mapping.ministry_as_printed}`)
}
const reviewedMapping = (measure) => scopeReview.ministry_mappings.find((mapping) => mapping.fiscal_year === measure.fiscal_year && mapping.basis === measure.basis && mapping.ministry_as_printed === measure.ministry_as_printed)
const aggregateScope = (measure) => scopeReview.aggregate_scopes.find((scope) => scope.ministry_as_printed === measure.ministry_as_printed)

const byEpisode = {}
const unmatched = new Map()
const aggregates = new Map()
for (const measure of staffing.measures) {
  const start = Number(String(measure.fiscal_year).slice(0, 4))
  const printed = measure.full_name_per_document_abbreviation_table || measure.ministry_as_printed
  const aggregate = aggregateScope(measure)
  if (aggregate) {
    accounting.record(`staffing.json#${staffing.measures.indexOf(measure)}`, 'aggregate_scope', measure, { scope: aggregate.scope, reason: aggregate.reason })
    aggregates.set(printed, (aggregates.get(printed) ?? 0) + 1)
    continue
  }
  const reviewed = reviewedMapping(measure)
  const body = BODIES.find(([pattern]) => pattern.test(printed))?.[1]
  let target = reviewed?.output_id ?? body ?? null
  if (!target) {
    // The episode standing in the fiscal year's first or last calendar year, by name, or failing
    // that by the one near name that contains the other.
    const candidates = MINISTRY_EPISODES.filter((episode) => standsIn(episode, start) || standsIn(episode, start + 1))
    const exact = candidates.filter((episode) => key(episode.name) === key(printed))
    const mine = new Set(words(printed))
    const near = candidates.filter((episode) => {
      const theirs = new Set(words(episode.name))
      return theirs.size && ([...theirs].every((word) => mine.has(word)) || [...mine].every((word) => theirs.has(word)))
    })
    target = (exact.length === 1 ? exact[0] : near.length === 1 ? near[0] : null)?.id ?? null
  }
  if (!target) {
    accounting.record(`staffing.json#${staffing.measures.indexOf(measure)}`, 'unresolved_unmapped', measure, { reason: 'No unique ministry/body mapping' })
    unmatched.set(printed, (unmatched.get(printed) ?? 0) + 1)
    continue
  }
  accounting.record(`staffing.json#${staffing.measures.indexOf(measure)}`, 'accepted', measure, { output_id: target, ...(reviewed ? { reason: `Reviewed mapping (${scopeReviewPath}): ${reviewed.reason}` } : {}) })
  ;(byEpisode[target] ??= []).push([measure.fiscal_year, measure.basis, measure.value, printed, measure.source_url, measure.locator])
}
for (const rows of Object.values(byEpisode)) rows.sort((a, b) => a[0].localeCompare(b[0]) || a[1].localeCompare(b[1]))
const totals = (staffing.totals ?? []).map((total) => [total.fiscal_year, total.basis, total.value ?? total.total ?? null]).filter((row) => row[2] !== null)

// ── The 43rd Parliament ──────────────────────────────────────────────────────────────────────────

const parliament = existsSync(resolve(ROOT, 'atlas/parliament-43.json')) ? read('atlas/parliament-43.json') : null
if (parliament) accounting.record('parliament-43.json', 'accepted', parliament, { reason: 'Source data retained; display remains specific to Parliament 43' })
const seats = (parliament?.seats ?? []).map((seat) => ({
  district: seat.district,
  member: seat.member,
  partyAtElection: seat.party_at_election_full_name ?? seat.party_at_election,
  votes: seat.margin_or_votes?.winner_votes ?? null,
  share: seat.margin_or_votes?.winner_pct_valid ?? null,
  margin: seat.margin_or_votes?.margin_votes ?? null,
  changes: (seat.later_changes ?? []).map((change) => ({
    date: change.date,
    precision: change.date_precision ?? 'day',
    change: change.change,
    from: change.from ?? null,
    to: change.to ?? null,
    detail: change.detail ?? null,
    source: change.source_url ?? null,
    status: change.evidence_status ?? 'documented'
  })),
  atDissolution: seat.assembly_designation_at_dissolution?.value ?? null
}))
const standings = parliament?.standings_at_dissolution
  ? {
      assembly: parliament.standings_at_dissolution.assembly_records?.counts ?? null,
      announced: parliament.standings_at_dissolution.announced_affiliations_before_2026_09_22_changes?.counts ?? null,
      note: 'The Assembly records OneBC and CentreBC members as Independent, and did not record the moves made on the day of dissolution.'
    }
  : null

const json = (value) => JSON.stringify(value)
writeFileSync(OUT, [
  '// Generated by scripts/build-government-atlas.mjs — do not edit.',
  '//',
  '// The Lieutenant Governors from the Legislative Library\'s list (January 2025), ministries\' staffing',
  '// from the Public Accounts\' Statements of Staff Utilization (2000/01–2025/26), and the 43rd',
  '// Parliament from Elections BC\'s Statement of Votes and the Assembly\'s records, with dated changes.',
  '',
  '/** {sequence, name, category, commissioned, effective, sworn, from, to, evidence, source, locator, note} */',
  `export const LIEUTENANT_GOVERNORS_OFFICIAL = ${json(lieutenantGovernors)}`,
  '',
  '/** The statement\'s own words on what it counts, and where its wording changed. */',
  `export const STAFFING_NOTES = ${json((staffing.comparability_notes ?? []).map((note) => note.note ?? note))}`,
  '',
  '/** Staffing by episode id (or body id): [fiscal year, basis, FTE, ministry as printed, source, locator]. */',
  'export const STAFFING = {',
  ...Object.entries(byEpisode).map(([id, rows]) => `  ${json(id)}: ${json(rows)},`),
  '}',
  '',
  `export const STAFFING_TOTALS = ${json(totals)}`,
  '',
  '/** The 43rd Parliament (elected 2024-10-19, dissolved 2026-09-22): one entry per electoral district. */',
  `export const PARLIAMENT_43 = ${json({ elected: parliament?.election?.date ?? '2024-10-19', dissolved: '2026-09-22', seats, standings })}`,
  '',
  '/** Declared 2026 election results, separately dated and retaining judicial-recount qualifications. */',
  `export const ELECTION_RESULTS_2026 = ${json(finalCount)}`,
  ''
].join('\n'))

accounting.write(resolve(ROOT, 'audit/atlas-import.json'))
console.log(`${lieutenantGovernors.length} Lieutenant Governors and administrators`)
const sum = (counts) => [...counts.values()].reduce((a, b) => a + b, 0)
console.log(`${staffing.measures.length - sum(unmatched) - sum(aggregates)}/${staffing.measures.length} staffing figures matched to ${Object.keys(byEpisode).length} ministries and bodies`)
if (aggregates.size) console.log('aggregate staffing rows kept unattributed:', [...aggregates.entries()].map(([name, count]) => `${count}× ${name}`).join('; '))
if (unmatched.size) console.log('unmatched staffing rows:', [...unmatched.entries()].map(([name, count]) => `${count}× ${name}`).join('; '))
console.log(`${seats.length} seats in the 43rd Parliament`)
