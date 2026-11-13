// Build the catalogue of legislation, orders and policy documents (src/government/instrumentsData.js)
// from evidence already in the repository, and the list of citations it could not read safely
// (research/audit/instruments-review.json).
//
// Each instrument has a stable ID and a type. Each relationship says what the instrument did for a
// body, with the date the evidence gives it and that evidence. Nothing is inferred beyond what a
// structured field or an event's own wording says:
//
//   - a sub-agency's `legalBasis` is a citation to the current consolidation: it says what the body
//     stands on today ("current_legal_basis"), never that it was founded by it, and it is not dated
//     back over the body's history;
//   - "designated by M327/1994, effective that day" (a body's establishedMeaning) is an establishment
//     by that order on the body's start date;
//   - an event that cites BC Laws becomes a milestone of the one instrument its title (or failing
//     that, its BC Laws source title) names. Its type decides whether it also states a relationship
//     with its subject. A title naming no instrument, or several, is left for review;
//   - instruments an event names explicitly (`instruments`, e.g. a policy document) are taken as given.

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { EVENTS, EVENT_SOURCES } from '../src/government/eventsData.js'
import { HISTORICAL_BODIES, HISTORY_SOURCES, SUB_AGENCIES } from '../src/government/historyData.js'

const OUT = resolve('src/government/instrumentsData.js')
// Reviewed decisions for citations the rules below cannot read safely (research/legislation/README.md).
const DECISIONS = JSON.parse(readFileSync(resolve('research/legislation/instrument-decisions.json'), 'utf8'))
const REVIEW = resolve('research/audit/instruments-review.json')

// ── Reading a citation ───────────────────────────────────────────────────────────────────────────

const slug = (text) => text.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[’']/g, '')
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const fullYear = (year) => year.length === 4 ? year : Number(year) > 30 ? `19${year}` : `20${year}`

const ORDER_PATTERNS = [
  // Orders in Council, B.C. regulations and ministerial orders are identified by number and year.
  { re: /\bO\.?I\.?C\.?\s+(\d+)\/(\d{2,4})\b/g, type: 'order_in_council', id: (n, y) => `oic-${fullYear(y)}-${n}`, title: (n, y) => `OIC ${n}/${fullYear(y)}` },
  { re: /\bB\.?C\.?\s*Reg\.?\s*(\d+)\/(\d{2,4})\b/g, type: 'regulation', id: (n, y) => `bc-reg-${fullYear(y)}-${n}`, title: (n, y) => `B.C. Reg. ${n}/${fullYear(y)}` },
  { re: /\bM\s?(\d+)\/(\d{4})\b/g, type: 'ministerial_order', id: (n, y) => `mo-${y}-${n}`, title: (n, y) => `Ministerial Order M${n}/${y}` }
]
// An Act's short title: capitalized words ending in "Act", with an optional year that is part of the
// title ("Budget Measures Implementation Act, 2002"). "The Act" or "1916 Act" names nothing.
const ACT = /\b((?:[A-Z][\w’'.-]*)(?:\s+(?:[A-Z][\w’'.-]*|of|and|the|for|on|in|to|de|des|du))*?\s+Act\b(?:\s+Amendment\s+Act\b)?(?:\s+\(No\.\s*\d+\))?)(?:,?\s+(\d{4})\b)?(?:\s*\(?\[?(?:SBC|S\.B\.C\.|RSBC|R\.S\.B\.C\.)\s*(\d{4})\]?,?\s*c\.\s*(\d+)\)?)?/g
const NOT_A_TITLE = /^(The|This|That|An?|Its|New|Modern|Former|Federal|Provincial)\s+Act$/

/** The instruments a piece of text names, each once. */
export const readInstruments = (text) => {
  if (!text) return []
  const found = new Map()
  for (const pattern of ORDER_PATTERNS) {
    for (const match of text.matchAll(pattern.re)) {
      const id = pattern.id(match[1], match[2])
      found.set(id, { id, type: pattern.type, title: pattern.title(match[1], match[2]) })
    }
  }
  for (const match of text.matchAll(ACT)) {
    let name = match[1].replace(/^(?:The|the)\s+/, '')
    if (NOT_A_TITLE.test(name) || name.split(/\s+/).length < 2) continue
    // A year that is part of the short title stays in it; a chapter citation is kept as a citation.
    const titled = match[2] ? `${name}, ${match[2]}` : name
    const id = `act-${slug(titled)}`
    const citation = match[3] ? `SBC ${match[3]}, c. ${match[4]}` : null
    const entry = found.get(id) ?? { id, type: 'act', title: titled, citations: [] }
    if (citation && !entry.citations.includes(citation)) entry.citations.push(citation)
    found.set(id, entry)
  }
  return [...found.values()]
}

/** The sections a citation names: "s. 2", "ss. 2–5", "s. 19(1)", "Part 12". */
const provisionsOf = (text) => [...(text ?? '').matchAll(/\b(ss?\.\s*[\d.()–-]+(?:\s*(?:and|,)\s*[\d.()–-]+)*|Part\s+\d+)/g)].map((match) => match[1])

// ── What an event's type says about its subject ──────────────────────────────────────────────────

const ESTABLISHING = new Set(['established', 'enabling_statute_assented', 'legal_establishment', 'statutory_establishment', 'designation', 'designation_order_made'])
const REORGANIZING = new Set(['amalgamation', 'amalgamation_authorized', 'reorganization', 'governance_change',
  'legal_status_change', 'legal_basis_change', 'statutory_rename', 'legal_name_change', 'statutory_name_change', 'rename',
  'executive_names_directive', 'department_split', 'regulatory_name_and_function_transition', 'powers_restricted',
  'responsibility_changed', 'enabling_statute_retitled', 'office_retitled', 'legislative_title_amendment', 'territory_transferred',
  'assets_and_obligations_transferred'])
const ENDING = new Set(['dissolution', 'dissolution_and_asset_transfer', 'dissolved', 'ended', 'designation_removed'])
const CONTINUING = new Set(['special_account_continued'])
const ADMINISTERING = new Set(['statute_administration_assigned'])

/** The relationship an event states between its subject and the instrument, or null for a milestone only. */
const NAMING = /name|retitled|rename/
const relationOf = (event) => {
  // A ministry is where the events of bodies the diagram does not draw (hospital districts, regional
  // boards) are filed, so only a change of the ministry's own name is read as being about it.
  if (/^(ministry|department)-/.test(event.subject)) return NAMING.test(event.type) && REORGANIZING.has(event.type) ? 'reorganized_by' : null
  const continued = /\bcontinu|\bconver/i.test(event.title)
  const established = /\bestablish|constituted a body corporate/i.test(event.title)
  // Words for both (a new authority established, the old corporation converted) do not say which the subject was.
  if (continued && established && (ESTABLISHING.has(event.type) || /assent/.test(event.type))) return 'mixed'
  if (CONTINUING.has(event.type) || (continued && (ESTABLISHING.has(event.type) || REORGANIZING.has(event.type) || /assent/.test(event.type)))) return 'continued_under'
  if (ESTABLISHING.has(event.type)) return 'established_by'
  // An assent whose own words say the body is established by it.
  if (/assent/.test(event.type) && established) return 'established_by'
  if (REORGANIZING.has(event.type)) return 'reorganized_by'
  if (ENDING.has(event.type)) return 'ended_by'
  if (ADMINISTERING.has(event.type)) return 'administers'
  return null
}

// ── Collecting ───────────────────────────────────────────────────────────────────────────────────

const instruments = new Map()
const review = []
const instrument = (cited) => {
  // A citation reviewed as another form of an instrument already held (a short title read without its
  // year or number) is that instrument.
  const alias = DECISIONS.aliases?.[cited.id]
  const found = alias ? { id: alias.id, type: alias.type ?? cited.type, title: alias.title, citations: cited.citations } : cited
  const held = instruments.get(found.id)
  if (held) {
    for (const citation of found.citations ?? []) if (!held.citations.includes(citation)) held.citations.push(citation)
    return held
  }
  const entry = { id: found.id, type: found.type, title: found.title, citations: [...(found.citations ?? [])], relations: [], milestones: [] }
  instruments.set(found.id, entry)
  return entry
}
/** One reviewed instrument: its citation must read as exactly one instrument, so its ID is the catalogue's. */
const decided = (entry, origin) => {
  const found = readInstruments(entry.cite)
  if (found.length !== 1) throw new Error(`${origin}: decision cite "${entry.cite}" reads as ${found.length} instruments`)
  return instrument(found[0])
}
const applied = { events: 0, bodies: 0, legalBasis: 0 }

const historySource = (index) => (index === null || index === undefined ? null : HISTORY_SOURCES[index] ?? null)

// 1. The sub-agencies' legal-basis citations, as the current consolidation gives them.
for (const sub of SUB_AGENCIES.filter((entry) => entry.legalBasis)) {
  const { citation, source, locator } = sub.legalBasis
  const decision = DECISIONS.legalBasis?.[sub.id]
  if (decision) {
    applied.legalBasis += 1
    for (const entry of decision.instruments ?? []) {
      decided(entry, `legalBasis#${sub.id}`).relations.push({ body: sub.id, relation: entry.relation ?? 'current_legal_basis', provisions: entry.provisions ?? [], from: null, to: null, precision: null,
        asOf: 'current consolidation', citation, source: historySource(source), locator: locator ?? null, ...(entry.note ? { note: entry.note } : {}) })
    }
    continue
  }
  const parts = citation.split(/;\s*/)
  const read = parts.map((part) => ({ part, found: readInstruments(part) }))
  for (const { part, found } of read) {
    if (found.length !== 1) {
      review.push({ origin: `historyData.SUB_AGENCIES#${sub.id}/legalBasis`, citation: part, reason: found.length ? `Names ${found.length} instruments; which provision does what is not stated` : 'No instrument could be read from the citation' })
      continue
    }
    const entry = instrument(found[0])
    entry.relations.push({
      body: sub.id, relation: 'current_legal_basis', provisions: provisionsOf(part), from: null, to: null, precision: null,
      asOf: /current consolidation/i.test(locator ?? '') ? 'current consolidation' : 'as cited',
      // A citation of several instruments is kept whole, so each part reads in its context.
      citation, source: historySource(source), locator: locator ?? null,
      ...(parts.length > 1 ? { note: 'One of several instruments in a combined citation; the role of each is not stated separately.' } : {})
    })
  }
}

// 2. Bodies designated by a ministerial order, as their establishedMeaning records it.
const precisionOf = (date) => String(date).length === 10 ? 'day' : String(date).length === 7 ? 'month' : 'year'
for (const body of HISTORICAL_BODIES.filter((entry) => entry.establishedMeaning && entry.established)) {
  const decision = DECISIONS.bodies?.[body.id]
  if (decision) {
    applied.bodies += 1
    for (const entry of decision.instruments ?? []) {
      const from = entry.from === undefined ? String(body.established) : entry.from
      decided(entry, `body#${body.id}`).relations.push({ body: body.id, relation: entry.relation, provisions: entry.provisions ?? [], from, to: null,
        precision: from ? precisionOf(from) : null, citation: body.establishedMeaning, source: historySource(body.establishedSource ?? body.source), locator: null,
        ...(entry.note ? { note: entry.note } : {}) })
    }
    continue
  }
  // A later clause ("; the December 1996 order calls it …") qualifies the name, not the order.
  const match = body.establishedMeaning.match(/^designated (?:as the [^,]+? )?by (M\d+\/\d{4}), effective that day(?:;.*)?$/)
  if (!match) {
    if (/\b(?:M\d+\/\d{4}|OIC \d+\/\d{4}|Act)\b/.test(body.establishedMeaning)) {
      review.push({ origin: `historyData.HISTORICAL_BODIES#${body.id}/establishedMeaning`, citation: body.establishedMeaning, reason: 'Names an instrument in prose that does not follow a reviewed pattern' })
    }
    continue
  }
  const [found] = readInstruments(match[1])
  instrument(found).relations.push({
    body: body.id, relation: 'established_by', provisions: [], from: String(body.established), to: null,
    precision: precisionOf(body.established),
    citation: body.establishedMeaning, source: historySource(body.establishedSource ?? body.source), locator: null
  })
}

// 3. Relationships read from an instrument's own text and checked against it (the decisions file says how).
for (const entry of DECISIONS.relations ?? []) {
  decided(entry, `relation#${entry.body}`).relations.push({ body: entry.body, relation: entry.relation, provisions: entry.provisions ?? [], from: entry.from ?? null, to: null,
    precision: entry.from ? precisionOf(entry.from) : null, citation: entry.note ?? entry.cite, source: entry.source ?? null, locator: entry.locator ?? null, ...(entry.note ? { note: entry.note } : {}) })
}

// 4. Events citing BC Laws, and instruments any event names explicitly.
const bcLaws = (index) => /bclaws/.test(EVENT_SOURCES[index]?.url ?? '')
for (const event of EVENTS) {
  const sources = event.sources.map((index) => EVENT_SOURCES[index]).filter(Boolean)
  const milestone = (entry, relation, note, body = event.subject, provisions) => {
    if (!entry.milestones.some((held) => held.event === event.id)) entry.milestones.push({ event: event.id, subject: event.subject, related: event.related ?? [], type: event.type, title: event.title, date: event.date })
    if (relation) {
      entry.relations.push({ body, relation, provisions: provisions ?? provisionsOf(event.title), from: event.date.start, to: null,
        precision: event.date.precision, event: event.id, citation: event.title, source: sources[0] ?? null, locator: event.locator ?? null, ...(note ? { note } : {}) })
    }
  }
  for (const named of event.instruments ?? []) milestone(instrument({ ...named, citations: [] }), named.relation, named.note)
  if (event.instruments?.length) continue
  const decision = DECISIONS.events?.[event.id]
  if (decision) {
    applied.events += 1
    for (const entry of decision.instruments ?? []) milestone(decided(entry, `event#${event.id}`), entry.relation ?? null, entry.note ?? null, entry.body ?? event.subject, entry.provisions)
    continue
  }
  if (!event.sources.some(bcLaws)) continue

  // A BC Laws source title that is itself one instrument's citation ("Coroners Act [SBC 2007] c. 15",
  // "OIC 2604/1981: …") names the event's instrument better than an Act the title mentions in passing.
  // A page that only mentions an Act ("FAQ … Teachers Act directory") is not such a citation.
  const sourceTitle = EVENT_SOURCES[event.sources.find(bcLaws)]?.title ?? ''
  const cited = readInstruments(sourceTitle).filter((entry) => sourceTitle.startsWith(entry.title.replace(/, \d{4}$/, '').replace(/^Ministerial Order /, '')))
  let found = cited.length === 1 ? cited : readInstruments(event.title)
  let from = cited.length === 1 ? 'source title' : 'title'
  // An event whose title names nothing often cites its instrument in its locator ("B.C. Reg. 293/2001,
  // sections 2-4 and Schedule A"); one instrument there is read the same way.
  if (!found.length) {
    const located = readInstruments(event.locator ?? '')
    if (located.length === 1) { found = located; from = 'locator' }
  }
  if (found.length !== 1) {
    review.push({ origin: `eventsData#${event.id}`, citation: event.title, reason: found.length ? `The ${from} names ${found.length} instruments (${found.map((each) => each.title).join('; ')})` : 'No instrument could be read from the title or its BC Laws source title' })
    continue
  }
  const read = relationOf(event)
  const relation = read === 'mixed' ? null : read
  if (read === 'mixed') review.push({ origin: `eventsData#${event.id}`, citation: event.title, reason: `Kept as a milestone of ${found[0].title}; the title both establishes and continues or converts, without saying which applies to ${event.subject}` })
  if (!read && /^(ministry|department)-/.test(event.subject) && (ESTABLISHING.has(event.type) || ENDING.has(event.type) || REORGANIZING.has(event.type))) {
    review.push({ origin: `eventsData#${event.id}`, citation: event.title, reason: `Kept as a milestone of ${found[0].title}; filed under ${event.subject}, but its words concern bodies the diagram does not draw` })
  }
  // The one instrument the title names, when the source is another, is cited by the event too. Where the
  // source is an order or regulation and the title names one Act ("Teachers Act section … in force
  // (B.C. Reg. 239/2011)"), the Act is what the relationship is with; the order brought it into force.
  const named = from === 'source title' ? readInstruments(event.title).filter((entry) => entry.id !== found[0].id) : []
  const actFirst = named.length === 1 && named[0].type === 'act' && found[0].type !== 'act'
  if (actFirst) {
    milestone(instrument(named[0]), relation, `Through ${found[0].title}, the source cited.`)
    milestone(instrument(found[0]), null)
  } else {
    milestone(instrument(found[0]), relation, from === 'source title' ? 'Instrument read from the BC Laws source title, the citation of the document itself.' : from === 'locator' ? 'Instrument read from the event\'s locator.' : null)
    if (named.length === 1) milestone(instrument(named[0]), null)
  }
  if (!read && !/^(ministry|department)-/.test(event.subject) && !/assent|in_force|commence|proclamation|royal|enacted|repeal|deposit|regulation_made|observed|appoint|members|origin|provision|establishment_set|increased|defined|scheduled|approved|named_in/.test(event.type)) {
    review.push({ origin: `eventsData#${event.id}`, citation: event.title, reason: `Kept as a milestone of ${found[0].title}; event type ${event.type} does not say what the instrument did for ${event.subject}` })
  }
}

// One short title cited with different enactment years may be separate Acts: said, not merged silently.
for (const entry of instruments.values()) {
  const years = new Set(entry.citations.map((citation) => citation.match(/\d{4}/)?.[0]))
  if (years.size > 1) review.push({ origin: `instrument#${entry.id}`, citation: entry.citations.join('; '), reason: 'One short title with several enactment years; these may be separate Acts' })
}

// A title with a year and the same title without one may be one Act cited two ways, or two Acts.
for (const entry of instruments.values()) {
  const bare = entry.type === 'act' && entry.title.match(/^(.*), \d{4}$/)?.[1]
  const other = bare && instruments.get(`act-${slug(bare)}`)
  if (other && !(DECISIONS.distinct ?? []).includes(entry.id)) review.push({ origin: `instrument#${entry.id}`, citation: `${entry.title} / ${other.title}`, reason: 'The same short title with and without a year; one Act cited two ways, or two enactments' })
}

// ── Writing ──────────────────────────────────────────────────────────────────────────────────────

// One relationship evidenced by several events (an Act's assent, then its coming into force) is one
// relationship with each dated event kept, its start the earliest of them.
for (const entry of instruments.values()) {
  const merged = []
  for (const relation of entry.relations) {
    const held = relation.event && merged.find((other) => other.event && other.body === relation.body && other.relation === relation.relation)
    const dated = { event: relation.event, date: relation.from, precision: relation.precision, citation: relation.citation, source: relation.source, locator: relation.locator, ...(relation.note ? { note: relation.note } : {}) }
    if (held) { held.evidence.push(dated); continue }
    merged.push(relation.event ? { ...relation, evidence: [dated] } : relation)
  }
  entry.relations = merged
}

const TYPE_ORDER = ['act', 'regulation', 'order_in_council', 'ministerial_order', 'policy']
const list = [...instruments.values()]
  .map((entry) => ({ ...entry, relations: entry.relations.sort((a, b) => String(a.from ?? '').localeCompare(String(b.from ?? '')) || a.body.localeCompare(b.body)),
    milestones: entry.milestones.sort((a, b) => a.date.start.localeCompare(b.date.start) || a.event.localeCompare(b.event)) }))
  .sort((a, b) => TYPE_ORDER.indexOf(a.type) - TYPE_ORDER.indexOf(b.type) || a.title.localeCompare(b.title))

const json = (value) => JSON.stringify(value)
writeFileSync(OUT, [
  '// Generated by scripts/build-government-instruments.mjs — do not edit.',
  '//',
  '// Acts, regulations, orders and policy documents, each with the bodies it stands in a stated',
  '// relationship to and the dated events that cite it. A relationship is only what its evidence says:',
  '// "current_legal_basis" is today\'s consolidation, not a founding date.',
  '',
  '/** {id, type, title, citations, relations: [{body, relation, provisions, from, to, precision, asOf?, event?, citation, source, locator, note?}], milestones: [{event, subject, related, type, title, date}]} */',
  'export const INSTRUMENTS = [',
  ...list.map((entry) => `  ${json(entry)},`),
  ']',
  ''
].join('\n'))
review.sort((a, b) => a.origin.localeCompare(b.origin))
writeFileSync(REVIEW, JSON.stringify({ schema: 'instrument-review/1', note: 'Citations the instrument catalogue did not read into a relationship, with why. Nothing here is guessed into the catalogue. Reviewed citations are decided in research/legislation/instrument-decisions.json.', decided: applied, count: review.length, rows: review }, null, 2) + '\n')

const relations = list.reduce((total, entry) => total + entry.relations.length, 0)
console.log(`${list.length} instruments, ${relations} relationships, ${list.reduce((total, entry) => total + entry.milestones.length, 0)} milestones; ${review.length} citations for review`)
