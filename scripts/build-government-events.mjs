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
//   GOVERNMENT_RESEARCH=tmp/research npm run build:government-events

import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const ROOT = process.env.GOVERNMENT_RESEARCH
if (!ROOT) {
  console.error('GOVERNMENT_RESEARCH is not set — point it at the research directory (tmp/research).')
  process.exit(1)
}

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
  const key = source.url.split('#')[0]
  let index = sources.findIndex((entry) => entry.url === key)
  if (index < 0) {
    sources.push({ url: key, title: source.title ?? null, publisher: source.publisher ?? null })
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

const events = []
const add = (event) => {
  if (events.some((existing) => existing.id === event.id)) return
  events.push(event)
}

// ── The package's seeds ──────────────────────────────────────────────────────────────────────────

const packageSources = existsSync(resolve(ROOT, 'package/sources.json'))
  ? Object.fromEntries(read('package/sources.json').sources.map((source) => [source.id, source]))
  : {}

if (existsSync(resolve(ROOT, 'package/event_seeds.json'))) {
  for (const seed of read('package/event_seeds.json').events) {
    const subject = SUBJECTS[seed.subject_key]
    if (!subject) {
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
      locator: locatorText(seed.evidence.locator),
      notes: seed.interpretation_notes ?? null,
      reviewed: seed.reviewed_on ?? null
    })
  }
}

// ── The follow-up research pass ──────────────────────────────────────────────────────────────────

const atlas = resolve(ROOT, 'atlas')
const atlasFiles = existsSync(atlas) ? readdirSync(atlas).filter((name) => /^events-.*\.json$/.test(name)) : []
for (const name of atlasFiles) {
  for (const record of read(`atlas/${name}`).events ?? []) {
    const subject = record.subject_id ?? null
    if (!subject || !record.date?.start) continue
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
      reviewed: record.reviewed_on ?? '2026-09-25'
    })
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

console.log(`${events.length} events (${atlasFiles.length} research files), ${sources.length} sources`)
