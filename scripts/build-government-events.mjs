// Builds src/government/eventsData.js: dated events in the life of the government's bodies.
//
// A body's history is more than a start year. The provincial parks system began with Strathcona
// Park in 1911, a Parks Branch became independent in 1957, and today's BC Parks is neither; the
// Workers' Compensation Board kept its legal name when it began operating as WorkSafeBC in 2005.
// Collapsing these into one "founded" field would say something false about each, so they are kept
// as typed events — function origin, establishment, name change, logo change, appointment,
// transfer — each with the precision its source gives (a year stays a year) and the source itself.
//
// The events come from two places:
//
//   * the "BC government atlas" research package of 2026-09-25 (event_seeds.json and its
//     sources.json), whose subject keys are mapped to this diagram's ids below; and
//   * the follow-up research pass (events-*.json), which uses the diagram's ids directly.
//
// Run with the research directory that holds both:
//
//   npm run build:government-events
//
// It reads the committed research in research/ (see research/README.md); GOVERNMENT_RESEARCH points it
// elsewhere.

import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { eventCollector, ledger } from './evidence-integrity.mjs'
import { applyDecisions, readDecisions } from './research-decisions.mjs'

const ROOT = process.env.GOVERNMENT_RESEARCH || 'research'

const OUT = resolve('src/government/eventsData.js')
const read = (path) => JSON.parse(readFileSync(resolve(ROOT, path), 'utf8'))

/**
 * The package's subjects, as this diagram names them. A subject that is not a body on the diagram —
 * the flag, the coat of arms — keeps a key of its own; the timeline shows those as context.
 */
const SUBJECTS = {
  'workers-compensation-board-bc': 'workers-compensation-board',
  'bc-general-election-2026': 'legislative-assembly',
  'bc-general-election-1903': 'legislative-assembly',
  'bc-general-election-1871': 'legislative-assembly',
  'lieutenant-governor-bc': 'lieutenant-governor',
  'first-nations-health-authority': 'first-nations-health-authority',
  'first-nations-health-governance-bc': 'first-nations-health-authority',
  'bc-parks-function': 'sub-bc-parks',
  'parks-branch-historical': 'sub-bc-parks',
  'bc-wildfire-service-lineage': 'sub-bc-wildfire-service',
  'bc-provincial-flag': 'symbol:flag',
  'bc-coat-of-arms': 'symbol:arms'
}

const sources = []
const sourceIndex = (source) => {
  if (!source?.url) return null
  const key = source.url.trim()
  let index = sources.findIndex((entry) => entry.url === key)
  if (index < 0) {
    sources.push({ url: key, documentUrl: key.split('#')[0], title: source.title ?? null, publisher: source.publisher ?? null })
    index = sources.length - 1
  }
  return index
}

/** A locator as text: some research gives it as {pdf_page_1_based, printed_page}. */
const locatorText = (locator) => {
  if (!locator) return null
  if (typeof locator === 'string') return locator
  if (typeof locator === 'object') {
    const pdf = locator.pdf_page_1_based ?? locator.pdf_page
    const printed = locator.printed_page
    return [pdf && `PDF page ${pdf}`, printed && `printed page ${printed}`].filter(Boolean).join(', ') || JSON.stringify(locator)
  }
  return String(locator)
}

const accounting = ledger()
const { events, add, attach } = eventCollector(accounting)

// ── The package's seeds ──────────────────────────────────────────────────────────────────────────

const packageSources = existsSync(resolve(ROOT, 'package/sources.json'))
  ? Object.fromEntries(read('package/sources.json').sources.map((source) => [source.id, source]))
  : {}

// Locators found later for seeds that shipped without one, recorded beside the atlas events.
const atlas = resolve(ROOT, 'atlas')
const atlasFiles = existsSync(atlas) ? readdirSync(atlas).filter((name) => /^events-.*\.json$/.test(name)).sort() : []
const seedLocators = new Map(atlasFiles.flatMap((name) => (read(`atlas/${name}`).seed_locator_updates ?? []).map((update) => [update.seed_id, update.locator])))

if (existsSync(resolve(ROOT, 'package/event_seeds.json'))) {
  for (const seed of read('package/event_seeds.json').events) {
    const subject = SUBJECTS[seed.subject_key]
    if (!subject) {
      accounting.record(`package/event_seeds.json#${seed.id}`, 'unresolved_unmapped', seed, { reason: `Unmapped subject ${seed.subject_key}` })
      console.warn(`unmapped package subject: ${seed.subject_key}`)
      continue
    }
    add({
      id: seed.id.replace(/^seed:/, 'pkg:'),
      subject,
      type: seed.event_type,
      title: seed.title,
      date: { start: seed.date.start, end: seed.date.end, precision: seed.date.precision, inclusive: seed.date.range_end_inclusive },
      status: seed.temporal_status,
      sources: seed.evidence.source_ids.map((id) => sourceIndex(packageSources[id])).filter((index) => index !== null),
      locator: locatorText(seed.evidence.locator) ?? seedLocators.get(seed.id) ?? null,
      notes: seed.interpretation_notes ?? null,
      reviewed: seed.reviewed_on ?? null
    }, `package/event_seeds.json#${seed.id}`, seed)
  }
}

// ── The follow-up research pass ──────────────────────────────────────────────────────────────────

for (const name of atlasFiles) {
  for (const record of read(`atlas/${name}`).events ?? []) {
    const subject = record.subject_id ?? null
    if (!subject || !record.date?.start) {
      accounting.record(`atlas/${name}#${record.id ?? 'unknown'}`, 'unresolved_unmapped', record, { reason: 'Missing subject or date' })
      continue
    }
    add({
      id: record.id,
      subject,
      type: record.event_type,
      title: record.title,
      date: {
        start: String(record.date.start),
        end: record.date.end ? String(record.date.end) : null,
        precision: record.date.precision ?? 'unknown',
        inclusive: Boolean(record.date.range_end_inclusive)
      },
      status: record.temporal_status ?? 'source_reported_past',
      sources: [sourceIndex({ url: record.evidence?.source_url, title: record.evidence?.source_title })].filter((index) => index !== null),
      locator: locatorText(record.evidence?.locator),
      notes: record.interpretation_notes ?? record.notes ?? null,
      reviewed: record.reviewed_on ?? null
    }, `atlas/${name}#${record.id}`, record)
  }
}

// ── The sub-agency research (history/sub-agencies-researched.json) ──────────────────────────────
//
// What each reviewed start and end dates, the milestones that compete with a start (BC Timber
// Sales has three), a name's first sighting, and events the review found — each typed as the
// research types it, so an opening is not shown as a founding.

const reviewed = resolve(ROOT, 'history/sub-agencies-researched.json')
let reviewedEvents = 0
if (existsSync(reviewed)) {
  const research = JSON.parse(readFileSync(reviewed, 'utf8'))
  applyDecisions('sub-agencies', [...(research.records ?? []), ...(research.gone ?? [])], readDecisions(ROOT))
  const catalogue = existsSync(resolve(ROOT, 'history/sub-agencies-sources.json'))
    ? Object.fromEntries(read('history/sub-agencies-sources.json').sources.map((source) => [source.id, source]))
    : {}
  const sourceOf = (claim) => sourceIndex({ url: claim.source, title: catalogue[claim.source_id]?.title ?? null })
  const eventOf = (record, claim, type, title, suffix) => {
    if (!claim?.date) {
      if (claim) accounting.record(`history/sub-agencies-researched.json#${record.id}/${suffix}`, 'unresolved_unmapped', claim, { reason: 'No supported event date; claim retained without inventing a timestamp' })
      return
    }
    const event = {
      id: `sub:${record.id}:${suffix}`,
      subject: `sub-${record.id}`,
      type,
      title,
      date: { start: String(claim.date), end: null, precision: claim.precision ?? 'unknown', inclusive: false },
      status: 'source_reported_past',
      sources: [sourceOf(claim)].filter((index) => index !== null),
      locator: locatorText(claim.locator),
      notes: claim.boundary === 'exclusive' ? 'The end is the day its successor began: it stood until then, not through it.' : null,
      reviewed: claim.checked ?? null
    }
    const origin = `history/sub-agencies-researched.json#${record.id}/${suffix}`
    // An earlier pass may already have the same start or end as an event of its own: this review's
    // claim becomes further evidence for it, so the one founding is not drawn twice.
    const kind = /establish/.test(type) ? /establish/ : /dissol|replace|abolish/.test(type) ? /dissol|replace|abolish|succession/ : null
    const earlier = kind && events.find((existing) => existing.subject === event.subject && existing.date.start === event.date.start && kind.test(existing.type))
    if (earlier) attach(earlier, event, origin, claim, `Same subject, date and kind as ${earlier.id}`)
    else {
      add(event, origin, claim)
      reviewedEvents += 1
    }
  }
  for (const record of [...(research.records ?? []), ...(research.gone ?? [])]) {
    const name = record.name
    eventOf(record, record.established, 'established', record.established?.meaning ? `${name}: ${record.established.meaning}` : `${name} established`, 'established')
    eventOf(record, record.ended, 'dissolved', record.ended?.meaning ? `${name}: ${record.ended.meaning}` : `${name} ended`, 'ended')
    eventOf(record, record.first_observed, 'name_first_observed', `${name}: the name first seen in this review's sources`, 'first-observed')
    ;(record.research_events ?? []).forEach((event, index) => eventOf(record, event, event.type, `${name}: ${event.summary}`, `event-${index}`))
    ;(record.date_claims ?? []).forEach((claim, index) => eventOf(record, claim, claim.type ?? 'establishment_claim', `${name}: ${claim.summary ?? 'a competing start date'}`, `claim-${index}`))
  }
}

events.sort((a, b) => a.date.start.localeCompare(b.date.start) || a.id.localeCompare(b.id))

const json = (value) => JSON.stringify(value)
writeFileSync(OUT, [
  '// Generated by scripts/build-government-events.mjs — do not edit.',
  '//',
  '// Typed, dated events in the life of the government\'s bodies, each with the precision its source',
  '// gives and the source itself. Package events (ids "pkg:") come from the BC government atlas',
  '// research package of 2026-09-25; the rest from the follow-up research pass.',
  '',
  `export const EVENT_SOURCES = ${json(sources)}`,
  '',
  '/** {id, subject, type, title, date: {start, end, precision, inclusive}, status, sources, locator, notes, reviewed} */',
  'export const EVENTS = [',
  ...events.map((event) => `  ${json(event)},`),
  ']',
  ''
].join('\n'))

accounting.write(resolve(ROOT, 'audit/events-import.json'))

console.log(`${events.length} events (${atlasFiles.length} research files, ${reviewedEvents} from the sub-agency review), ${sources.length} sources`)
