// Builds src/government/historyData.js from the government-history research.
//
// The government diagram knows who led every ministry, and which Crown corporations, agencies and
// officers stood around it, for the present. This brings the past up to the same standard:
//
//   * every cabinet portfolio since 1871 and who held it, matched to the ministry episode it
//     headed — mostly from the Legislative Library's "British Columbia Executive Council
//     Appointments 1871–1986" and its cabinet lists since, cross-checked against Wikipedia;
//   * Crown corporations and agencies that stood at some point, including the ones since wound up
//     or renamed, with the years they stood and what each became;
//   * who held the Speakership, the officers of the Legislature and the chief justiceships, year by
//     year.
//
// Run with the research directory's path:
//
//   npm run build:government-history
//
// It reads the committed research in research/history/ (see research/README.md); GOVERNMENT_HISTORY_SOURCE points it
// elsewhere.
//
// The output is committed: like the ministry history it is a fixed record, not something that
// re-derives per machine.

import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { MINISTRY_EPISODES } from '../src/government/episodes.js'
import { applyDecisions, readDecisions } from './research-decisions.mjs'

const SOURCE = process.env.GOVERNMENT_HISTORY_SOURCE || 'research/history'

const read = (name) => JSON.parse(readFileSync(resolve(SOURCE, name), 'utf8'))
const ERAS = ['1871-1903', '1903-1941', '1941-1975', '1975-1991', '1991-2011', '2011-2026']
const OUT = resolve('src/government/historyData.js')

// ── Sources, stored once and referred to by index ────────────────────────────────────────────────

const sources = []
const sourceIndex = (url) => {
  if (!url) return null
  const clean = String(url).split('#')[0].trim()
  let index = sources.indexOf(clean)
  if (index < 0) { sources.push(clean); index = sources.length - 1 }
  return index
}

// ── Portfolios to ministry episodes ──────────────────────────────────────────────────────────────

/** The words that name what a portfolio or ministry is for, with the furniture folded away. */
const STOP = new Set(['of', 'and', 'the', 'for', 'minister', 'ministry', 'department', 'dept', 'provincial', 'responsible', 'chief', 'commissioner'])
const words = (name) => String(name).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[‘’ʼ']/g, '').replace(/&/g, ' and ').replace(/-/g, ' ').replace(/\bsports\b/g, 'sport')
  .replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter((word) => word && !STOP.has(word))
const key = (name) => words(name).join(' ')

/** Old department names that differ from the portfolio that headed them. */
const ALIASES = {
  'railway': 'railways',
  'treasury': 'finance',
  'fisheries': 'fisheries',
  'justice': 'justice attorney general'
}

const day = (value, end = false) => {
  if (!value) return null
  const text = String(value)
  if (text.length === 4) return `${text}-${end ? '12-31' : '01-01'}`
  if (text.length === 7) return `${text}-${end ? '28' : '01'}`
  return text
}
const episodeSpan = (episode) => [`${episode.from}-01-01`, episode.to === null ? '9999-12-31' : `${episode.to}-12-31`]
const overlaps = (a0, a1, b0, b1) => a0 <= b1 && b0 <= a1

const terms = ERAS.flatMap((era) => read(`ministers-${era}.json`).records)
const byEpisode = new Map()
let matched = 0
const unmatched = new Map()

for (const term of terms) {
  const from = day(term.from)
  const to = day(term.to, true) ?? '9999-12-31'
  const termKey = key(term.portfolio)
  const candidates = MINISTRY_EPISODES.filter((episode) => {
    const [start, end] = episodeSpan(episode)
    return overlaps(from, to, start, end)
  })
  // Exact, then an alias, then the closest word set that contains the other.
  let hits = candidates.filter((episode) => key(episode.name) === termKey || ALIASES[key(episode.name)] === termKey)
  if (!hits.length) {
    const mine = new Set(words(term.portfolio))
    const scored = candidates.map((episode) => {
      const theirs = new Set(words(episode.name))
      if (!theirs.size || !mine.size) return null
      const contains = [...theirs].every((word) => mine.has(word)) || [...mine].every((word) => theirs.has(word))
      if (!contains) return null
      const extra = [...mine].filter((word) => !theirs.has(word)).length + [...theirs].filter((word) => !mine.has(word)).length
      return { episode, extra }
    }).filter(Boolean).sort((a, b) => a.extra - b.extra)
    // Only a near match, and only one: a one-word portfolio must not claim every ministry it is part of.
    if (scored.length && scored[0].extra <= 2 && (scored.length === 1 || scored[1].extra > scored[0].extra)) hits = [scored[0].episode]
  }
  if (!hits.length) {
    unmatched.set(term.portfolio, (unmatched.get(term.portfolio) ?? 0) + 1)
    continue
  }
  matched += 1
  for (const episode of hits) {
    if (!byEpisode.has(episode.id)) byEpisode.set(episode.id, [])
    byEpisode.get(episode.id).push([
      term.holder,
      String(term.from ?? ''),
      term.to ? String(term.to) : null,
      term.portfolio,
      term.party ? String(term.party).replace(/^New Democratic( Party)?$/, 'NDP').replace(/^British Columbia /, '') : null,
      term.acting ? 1 : 0,
      sourceIndex(term.source)
    ])
  }
}

for (const list of byEpisode.values()) list.sort((a, b) => a[1].localeCompare(b[1]))

// ── Bodies that stood, and what became of them ───────────────────────────────────────────────────

/** Research ids of bodies the present already draws, under their present ids. */
const SAME_AS = {
  'bc-hydro': 'bc-hydro',
  'insurance-corporation-of-bc': 'icbc',
  'bc-lottery-corporation': 'bclc',
  'bc-housing': 'bc-housing',
  'bc-transit': 'bc-transit',
  'bc-assessment-authority': 'bc-assessment',
  'bc-securities-commission': 'bc-securities-commission',
  'bc-financial-services-authority': 'bc-financial-services-authority',
  'innovate-bc': 'innovate-bc',
  'columbia-basin-trust': 'columbia-basin-trust',
  'columbia-power-corporation': 'columbia-power',
  'destination-bc': 'destination-bc',
  'bc-pavilion-corporation': 'bc-pavilion-corporation',
  'knowledge-network-corporation': 'knowledge-network',
  'royal-bc-museum': 'royal-bc-museum',
  'bc-games-society': 'bc-games-society',
  'transportation-investment-corporation': 'transportation-investment-corporation',
  'infrastructure-bc': 'infrastructure-bc',
  'inbc-investment-corp': 'inbc',
  'legal-services-society': 'legal-aid-bc',
  'skilledtradesbc': 'skilledtradesbc',
  'community-living-bc': 'community-living-bc',
  'first-peoples-cultural-council': 'first-peoples-cultural-council',
  'liquor-distribution-branch': 'liquor-distribution-branch',
  'bc-energy-regulator': 'bc-energy-regulator',
  'fraser-health': 'fraser-health',
  'interior-health': 'interior-health',
  'northern-health': 'northern-health',
  'vancouver-coastal-health': 'vancouver-coastal-health',
  'vancouver-island-health': 'island-health',
  'provincial-health-services-authority': 'provincial-health-services-authority'
}

/**
 * Left out: regional rather than provincial bodies (TransLink and its predecessor), a company the
 * Province no longer owns (BC Ferry Services since 2003), and the Merit Commissioner, which is an
 * officer of the Legislature and is drawn from the office-holders instead.
 */
const OMIT = new Set([
  'bc-ferry-services-inc', 'greater-vancouver-transportation-authority', 'south-coast-bc-transportation-authority', 'merit-commissioner'
])

const researched = read('bodies.json').records
const idOf = (id) => SAME_AS[id] ?? id
const bodies = researched
  .filter((record) => !OMIT.has(record.id))
  .map((record) => ({
    id: idOf(record.id),
    name: record.name,
    ...(record.shortName ? { shortName: record.shortName } : {}),
    kind: record.kind,
    established: record.established ? String(record.established) : null,
    ended: record.ended ? String(record.ended) : null,
    became: record.becameId && !OMIT.has(record.becameId) ? idOf(record.becameId) : null,
    responsible: (record.responsible ?? []).map(({ ministry, from, to }) => [ministry, from ? String(from) : null, to ? String(to) : null]),
    description: record.description ?? null,
    source: sourceIndex(record.source),
    // Whether the present already draws it, from its own record.
    current: Boolean(SAME_AS[record.id])
  }))

// Which ministry answered for each body, period by period, from the follow-up research where it
// found one: added to the research record, or — for a body only the present's record has — to a
// record of its own that carries nothing else.
// Every responsible-*.json file, so a new round of research is a new file.
const responsibleFiles = readdirSync(SOURCE).filter((name) => /^responsible-.*\.json$/.test(name)).sort()
let periods = 0
for (const name of responsibleFiles) {
  for (const [researchId, list] of Object.entries(read(name).records ?? {})) {
    const id = idOf(researchId)
    let body = bodies.find((entry) => entry.id === id)
    if (!body) {
      body = { id, name: null, kind: null, established: null, ended: null, became: null, responsible: [], description: null, source: null, current: true }
      bodies.push(body)
    }
    for (const period of list ?? []) {
      if (!period?.ministry) continue
      const row = [period.ministry, period.from ? String(period.from) : null, period.to ? String(period.to) : null, sourceIndex(period.source)]
      if (!body.responsible.some((existing) => existing[0] === row[0] && existing[1] === row[1])) {
        body.responsible.push(row)
        periods += 1
      }
    }
    body.responsible.sort((a, b) => String(a[1] ?? '').localeCompare(String(b[1] ?? '')))
  }
}

// BC Rail and the Workers' Compensation Board, from the follow-up research pass: each interval is
// one kind of relation. Only statutory or designated ministerial responsibility becomes a
// responsible-ministry period, which the diagram draws as a line; appointments, funding, a report
// tabled by a minister and the rest are kept as typed relations that the panel lists, because none
// of them says which ministry answered for the body.
const railWcb = resolve(SOURCE, '../atlas/responsibility-rail-wcb.json')
let typedRelations = 0
if (existsSync(railWcb)) {
  const officeToMinistry = (office) => String(office ?? '')
    .replace(/^Minister (of|for) /, 'Ministry of ')
    .replace(/^Minister responsible for /i, 'Ministry of ')
  for (const interval of JSON.parse(readFileSync(railWcb, 'utf8')).intervals ?? []) {
    const id = idOf(interval.subject_id)
    const body = bodies.find((entry) => entry.id === id)
    if (!body || !interval.from) continue
    const source = sourceIndex(interval.source_url)
    if (interval.relation === 'minister_responsible_for' && interval.office) {
      const row = [officeToMinistry(interval.office), String(interval.from), interval.to ? String(interval.to) : null, source]
      if (!body.responsible.some((existing) => existing[0] === row[0] && existing[1] === row[1])) body.responsible.push(row)
    } else {
      ;(body.relations ??= []).push([interval.relation, interval.office ?? null, interval.holder ?? null, String(interval.from), interval.to ? String(interval.to) : null, source, interval.locator ?? null])
      typedRelations += 1
    }
  }
  for (const body of bodies) body.responsible.sort((a, b) => String(a[1] ?? '').localeCompare(String(b[1] ?? '')))
}

// ── Office-holders ───────────────────────────────────────────────────────────────────────────────

const offices = Object.fromEntries(read('holders.json').offices.map((office) => [office.id, {
  title: office.title,
  established: office.established ? String(office.established) : null,
  holders: office.holders.map((holder) => [holder.name, holder.from ? String(holder.from) : null, holder.to ? String(holder.to) : null, holder.acting ? 1 : 0, sourceIndex(holder.source)])
}]))

// ── Sub-agencies: ministries' divisions, tribunals, and the Crowns' subsidiaries ──────────────────
//
// The three collection files overlap — a tribunal is also a ministry's division — so a body found
// twice is merged field by field: the first copy's values stand, a later copy fills what the first
// left empty, and a start date keeps the source that gave it. (Keeping only the first copy used to
// drop the dates that only the tribunal file had.)

const subFiles = ['sub-divisions.json', 'sub-tribunals.json', 'sub-subsidiaries.json'].filter((name) => existsSync(resolve(SOURCE, name)))
const MERGED = ['name', 'shortName', 'parent', 'kind', 'established', 'description', 'url', 'source']
const collected = new Map()
const mergeWarnings = []
for (const name of subFiles) {
  for (const record of read(name).records ?? []) {
    if (!record?.id) continue
    const held = collected.get(record.id)
    if (!held) {
      collected.set(record.id, { ...record, establishedSource: record.established ? record.source : null })
      continue
    }
    for (const field of MERGED) {
      const value = record[field]
      if (value === null || value === undefined || value === '') continue
      if (held[field] === null || held[field] === undefined || held[field] === '') {
        held[field] = value
        if (field === 'established') held.establishedSource = record.source
      } else if (String(held[field]) !== String(value) && (field === 'established' || field === 'parent')) {
        mergeWarnings.push(`${record.id}: ${field} ${held[field]} kept, ${value} in ${name} set aside`)
      }
    }
  }
}

const subAgencies = []
for (const record of collected.values()) {
  if (!record.parent) continue
  subAgencies.push({
    id: `sub-${record.id}`,
    name: record.name,
    ...(record.shortName ? { shortName: record.shortName } : {}),
    parent: record.parent,
    type: record.kind ?? null,
    established: record.established ? String(record.established) : null,
    description: record.description ?? null,
    officialUrl: record.url ?? null,
    source: sourceIndex(record.source),
    ...(record.establishedSource && record.establishedSource !== record.source ? { establishedSource: sourceIndex(record.establishedSource) } : {})
  })
}

// ── Sub-agencies: the reviewed history (sub-agencies-researched.json) ────────────────────────────
//
// Claims, not a finished history. Each date keeps its precision and says what it dates ("opened",
// "statutory establishment provision in force"); an end is an exclusive boundary; names and parents
// are kept as periods where the source gives one and as single observations where it does not — an
// observation is not a period, and is never drawn as one. A record whose research is incomplete
// says so. Bodies that are gone are added, with no parent unless a source names one.

const RESEARCHED = 'sub-agencies-researched.json'
let researchedCount = 0
let goneCount = 0
if (existsSync(resolve(SOURCE, RESEARCHED))) {
  const research = read(RESEARCHED)
  if (!String(research.schema_version ?? '').startsWith('sub-agencies-research/1')) {
    console.error(`${RESEARCHED}: unknown schema ${research.schema_version}`)
    process.exit(1)
  }
  // Editorial decisions (research/decisions.json) come first: they pick between competing claims.
  for (const id of applyDecisions('sub-agencies', [...(research.records ?? []), ...(research.gone ?? [])], readDecisions(SOURCE))) {
    console.warn(`decision ${id} matches no sub-agency record`)
  }
  const dateOf = (claim) => claim?.date
    ? {
        date: String(claim.date),
        precision: claim.precision ?? null,
        meaning: claim.meaning ?? null,
        evidence: claim.evidence ?? null,
        source: sourceIndex(claim.source),
        locator: claim.locator ?? null,
        checked: claim.checked ?? null
      }
    : null
  const periodOf = (row, value) => ({
    ...value,
    from: row.from ?? null,
    to: row.to ?? null,
    fromPrecision: row.from_precision ?? null,
    toPrecision: row.to_precision ?? null,
    observedOn: row.observed_on ?? null,
    coverage: row.coverage ?? null,
    source: sourceIndex(row.source),
    locator: row.locator ?? null
  })
  const byId = new Map(subAgencies.map((entry) => [entry.id, entry]))
  const compile = (record, entry) => {
    const established = dateOf(record.established)
    const ended = dateOf(record.ended)
    // A researched start replaces the collected one; where the research left the start unresolved,
    // a collected year stands but is marked as needing reconciliation.
    if (established) entry.established = established.date
    Object.assign(entry, {
      researched: true,
      status: record.evidence_status ?? null,
      ...(established ? { establishedClaim: established } : {}),
      ...(ended ? { ended: ended.date, endedClaim: ended } : {}),
      names: (record.names ?? []).map((row) => periodOf(row, { name: row.name })),
      parents: (record.parents ?? []).map((row) => periodOf(row, { name: row.ministry_as_printed, relation: row.relation ?? 'part_of' })),
      relations: (record.relations ?? []).map((row) => ({
        type: row.type,
        body: `sub-${row.body}`,
        date: row.date ?? null,
        precision: row.precision ?? null,
        source: sourceIndex(row.source),
        locator: row.locator ?? null
      })),
      legalBasis: record.legal_basis
        ? { citation: record.legal_basis.citation, source: sourceIndex(record.legal_basis.source), locator: record.legal_basis.locator ?? null }
        : null,
      identityReview: Boolean(record.identity_review_required),
      decisions: (record.decisions ?? []).map(({ id, field, reason, decided }) => ({ id, field, reason, decided })),
      note: record.note || null,
      checked: record.review?.checked ?? null
    })
  }
  for (const record of research.records ?? []) {
    const entry = byId.get(`sub-${record.id}`)
    if (!entry) {
      console.warn(`${RESEARCHED}: no collected sub-agency ${record.id}`)
      continue
    }
    compile(record, entry)
    researchedCount += 1
  }
  for (const record of research.gone ?? []) {
    if (byId.has(`sub-${record.id}`)) continue
    const entry = {
      id: `sub-${record.id}`,
      name: record.name,
      ...(record.shortName ? { shortName: record.shortName } : {}),
      // Gone, and placed under nothing no source names.
      parent: record.parent_today ?? null,
      type: record.kind ?? null,
      established: null,
      description: record.description ?? null,
      officialUrl: record.official_url ?? null,
      source: sourceIndex(record.established?.source ?? record.ended?.source),
      gone: true
    }
    compile(record, entry)
    subAgencies.push(entry)
    byId.set(entry.id, entry)
    goneCount += 1
  }
}

// ── Write ─────────────────────────────────────────────────────────────────────────────────────────

const json = (value) => JSON.stringify(value)
const lines = [
  '// Generated by scripts/build-government-history.mjs — do not edit.',
  '//',
  '// Who held each ministry since 1871, the Crown corporations and agencies that stood in each year,',
  '// and who held the Speakership, the officers of the Legislature and the chief justiceships. Mostly',
  '// from the Legislative Library of British Columbia (Executive Council Appointments 1871–1986 and',
  '// its cabinet lists since), BC Archives and Wikipedia; every record keeps the index of its source.',
  '',
  '/** Source URLs, referred to by index below. */',
  `export const HISTORY_SOURCES = ${json(sources)}`,
  '',
  '/**',
  ' * Ministers by ministry episode id: [holder, from, to, portfolio as styled, party, acting, source].',
  ' * Dates are as precise as the source: a day, a month or a year.',
  ' */',
  'export const MINISTERS = {',
  ...[...byEpisode.entries()].map(([id, list]) => `  ${json(id)}: ${json(list)},`),
  '}',
  '',
  '/** Bodies that stood in some year: established and ended as precisely as known; `responsible` is',
  ' *  [ministry as styled then, from, to, source] where a source states it. A record with no name',
  ' *  only adds those periods to a body the present already draws. */',
  'export const HISTORICAL_BODIES = [',
  ...bodies.map((body) => `  ${json(body)},`),
  ']',
  '',
  '/** Sub-agencies: today\'s, with a parent id from the present diagram and where known the date each',
  ' *  began; and, where reviewed, dated claims ({date, precision, meaning, source, locator}), an',
  ' *  exclusive end, names and parents as periods or single observations, and succession. */',
  'export const SUB_AGENCIES = [',
  ...subAgencies.map((entry) => `  ${json(entry)},`),
  ']',
  '',
  '/** Office-holders by office id: [name, from, to, acting, source]. */',
  'export const OFFICE_HOLDERS = {',
  ...Object.entries(offices).map(([id, office]) => `  ${json(id)}: ${json(office)},`),
  '}',
  ''
]
writeFileSync(OUT, lines.join('\n'))

console.log(`${matched}/${terms.length} minister terms matched to ${byEpisode.size} of ${MINISTRY_EPISODES.length} episodes`)
console.log(`${bodies.length} bodies, ${Object.keys(offices).length} offices, ${sources.length} sources`)
console.log(`${subAgencies.length} sub-agencies from ${subFiles.length} files (${researchedCount} with reviewed history, ${goneCount} gone); ${typedRelations} typed relations for BC Rail and the WCB`)
for (const warning of mergeWarnings) console.warn(`sub-agency merge: ${warning}`)
console.log(`${periods} responsible-ministry periods from ${responsibleFiles.length} follow-up files; ${bodies.filter((body) => body.responsible.length).length} bodies have at least one`)
if (unmatched.size) {
  console.log('Unmatched portfolios (usually ones that headed no ministry of their own):')
  for (const [portfolio, count] of [...unmatched.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${count}× ${portfolio}`)
}
