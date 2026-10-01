// Builds research/queue/: the sub-agency work list, split into batches that can each be handed to a
// researcher (or another AI) on its own. Regenerated from the compiled atlas, so a body leaves the
// queue's top priority as soon as research for it is merged and rebuilt:
//
//   npm run build:research-queue
//
// research/queue/README.md is written by hand and is not touched here.

import { mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const R = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const { SUB_AGENCIES, HISTORY_SOURCES } = await import(`${R}/src/government/historyData.js`)
const { EVENTS, EVENT_SOURCES } = await import(`${R}/src/government/eventsData.js`)
const { MINISTRY_EPISODES, forerunnerIn } = await import(`${R}/src/government/episodes.js`)
const { governmentIn } = await import(`${R}/src/government/snapshot.js`)
const OUT = `${R}/research/queue`

const asOf = process.env.GOVERNMENT_AS_OF ?? '2026-09-30'
if (!/^\d{4}-\d{2}-\d{2}$/.test(asOf)) throw new Error('GOVERNMENT_AS_OF must be YYYY-MM-DD')
const present = Number(asOf.slice(0, 4))
const today = governmentIn(present)
const nameOf = (id) => today.nodes.find((n) => n.id === id)?.name ?? MINISTRY_EPISODES.find((e) => e.id === id)?.name ?? id ?? 'no parent recorded'

// The years a researcher checks for a first sighting: budget books and service plans are online for
// each of them (2002 is the first year of service plans on bcbudget.gov.bc.ca).
const CHECKPOINTS = [2025, 2020, 2015, 2010, 2005, 2002]
const BATCH_SIZE = 14
const SMALL = 6

const src = (index) => (index === null || index === undefined ? null : HISTORY_SOURCES[index] ?? null)
const eventsOf = (id) => EVENTS.filter((e) => e.subject === id).sort((a, b) => String(a.date?.start ?? '').localeCompare(String(b.date?.start ?? '')))
const rows = (list) => (list ?? []).map((row) => ({
  name: row.name, from: row.from, to: row.to, observed_on: row.observedOn, coverage: row.coverage, source: src(row.source), locator: row.locator
}))

/** Which ministry the parent most likely was in a checkpoint year — a lead from lineage, not a finding. */
const parentIn = (parent, year) => /^ministry-/.test(parent ?? '') ? forerunnerIn(parent, year)?.name ?? null : null

const items = SUB_AGENCIES.filter((s) => !s.gone && !s.ended).map((s) => {
  const events = eventsOf(s.id)
  const firstSeen = s.firstObservedClaim?.date ?? null
  const undated = !s.established
  const priority = undated && !firstSeen && !events.length ? 1 : undated ? 2 : 3
  const tracks = [...(undated ? ['A', 'B'] : []), 'C']
  const names = rows(s.names)
  const parents = rows(s.parents)
  const questions = []
  let generic = true
  if (undated) {
    if (firstSeen || events.length) generic = false
    questions.push(firstSeen
      ? `A. It is already seen in ${firstSeen}. Look earlier: ${[...CHECKPOINTS.filter((y) => y < Number(String(firstSeen).slice(0, 4))).map((y) => `the ${y} checkpoint`), 'before 2002, the ministry annual reports and Estimates held by the Legislative Library'].join(', then ')}. Record every source you look at, whatever the outcome; a non-match does not date a start.`
      : 'A. First sighting: is it listed in the Estimates or service plan at each checkpoint year (table above)? Record every checkpoint you look at, with its outcome, the pages read, and the name and ministry as printed.')
    questions.push(events.length
      ? `B. Start: ${events.length} dated event${events.length === 1 ? ' is' : 's are'} already on file (listed above). Which, if any, is the start of this body rather than of its function or a predecessor? If none, find the Act, order in council or announcement that created it.`
      : 'B. Start: the Act, order in council, news release or annual report that created it, with the date at the precision the source gives. A first sighting is not a start.')
  }
  if (names.length || parents.length || !undated || s.researched) generic = false
  questions.push(names.length > 1 || names.some((row) => row.coverage !== 'observation_only')
    ? 'C. Names and parents: extend what is on file; fill the years between observations.'
    : `C. Names and parents: each earlier name, and the ministry or Crown it sat under, by period${/^ministry-/.test(s.parent ?? '') ? ' — the cabinet shuffles of 2001, 2005, 2017, 2020, 2022 and 2024 moved many branches' : ''}.`)
  if (s.status === 'requires_reconciliation') generic = false
  if (s.status === 'requires_reconciliation') questions.push('D. Reconcile: the review found competing dates. Find the instrument that settles it; do not choose between them yourself — record every claim with its source.')
  return {
    id: s.id.replace(/^sub-/, ''),
    name: s.name,
    ...(s.shortName ? { shortName: s.shortName } : {}),
    kind: s.type ?? null,
    priority,
    tracks,
    parent_today: s.parent ?? null,
    parent_today_name: nameOf(s.parent),
    parent_likely_by_year: Object.fromEntries(CHECKPOINTS.map((year) => [year, parentIn(s.parent, year)])),
    official_url: s.officialUrl ?? null,
    source_today: src(s.source),
    description: s.description ?? null,
    held: {
      established: s.established ?? null,
      established_meaning: s.establishedClaim?.meaning ?? null,
      first_observed: firstSeen,
      names: names,
      parents: parents,
      events: events.map((e) => ({ date: e.date?.start ?? null, precision: e.date?.precision ?? null, type: e.type, title: e.title, sources: (e.sources ?? []).map((i) => EVENT_SOURCES[i]?.url ?? null).filter(Boolean), locator: e.locator ?? null, status: e.status ?? null }))
    },
    review_status: s.researched ? s.status ?? 'reviewed' : 'not_researched',
    questions,
    generic_questions: generic
  }
})

// Batches: one parent's bodies together, most undated first; a large family is split, and small
// families are pooled so no batch is trivially short.
const families = new Map()
for (const item of items) (families.get(item.parent_today) ?? families.set(item.parent_today, []).get(item.parent_today)).push(item)
const order = (a, b) => a.priority - b.priority || a.name.localeCompare(b.name)
const ranked = [...families.entries()]
  .map(([parent, list]) => [parent, [...list].sort(order)])
  .sort((a, b) => b[1].filter((i) => i.priority < 3).length - a[1].filter((i) => i.priority < 3).length || nameOf(a[0]).localeCompare(nameOf(b[0])))
const batches = []
let pool = null
for (const [parent, list] of ranked) {
  if (list.length > SMALL) {
    const parts = Math.ceil(list.length / BATCH_SIZE)
    const size = Math.ceil(list.length / parts)
    for (let part = 0; part < parts; part++) batches.push({ parents: [parent], items: list.slice(part * size, (part + 1) * size), part: parts > 1 ? `${part + 1} of ${parts}` : null })
    continue
  }
  if (!pool || pool.items.length + list.length > BATCH_SIZE) { pool = { parents: [], items: [], part: null }; batches.push(pool) }
  pool.parents.push(parent)
  pool.items.push(...list)
}
const slug = (text) => String(text).toLowerCase().replace(/^ministry of /, '').replace(/[’']/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
batches.forEach((batch, index) => {
  const title = batch.parents.length > 2 ? `${nameOf(batch.parents[0])} and ${batch.parents.length - 1} more` : batch.parents.map(nameOf).join(' and ')
  batch.number = String(index + 1).padStart(2, '0')
  batch.title = `${title}${batch.part ? ` (${batch.part})` : ''}`
  batch.file = `batches/${batch.number}-${slug(nameOf(batch.parents[0]))}${batch.parents.length > 1 ? '-and-more' : ''}${batch.part ? `-${batch.part.split(' ')[0]}` : ''}.md`
  for (const item of batch.items) item.batch = batch.number
})

// ── Writing ──────────────────────────────────────────────────────────────────────────────────────

const cell = (value) => String(value ?? '').replace(/\|/g, '\\|').replace(/\n/g, ' ')
const PRIORITY = { 1: 'P1 — disappears before today, nothing on file', 2: 'P2 — undated, but some history on file', 3: 'P3 — dated; history over time' }
const counts = (list) => ({ total: list.length, p1: list.filter((i) => i.priority === 1).length, p2: list.filter((i) => i.priority === 2).length, p3: list.filter((i) => i.priority === 3).length })
const drawn = (year) => governmentIn(year).nodes.filter((n) => n.kind === 'sub').length
const all = counts(items)

const batchMarkdown = (batch) => {
  const lines = []
  const parentsTable = batch.parents.filter((p) => /^ministry-/.test(p ?? ''))
  lines.push(`# Research batch ${batch.number}: ${batch.title}

_Generated by \`npm run build:research-queue\` on the data as of ${asOf}. Do not edit; hand results back as described below and the batch regenerates._

This is a self-contained work packet for the **PofBC government atlas**, a site that draws the Government of British Columbia in any year since 1871. The full guide is \`research/queue/README.md\`; what you need is repeated here.

**The problem.** Each body below is a sub-agency — a division, office, program, board, tribunal or Crown subsidiary — collected from ${present} sources. The site draws a body in a past year only if a source shows it existed by then. Most have no start date and no earlier sighting, so they disappear the moment the timeline leaves ${present}. Your findings are the evidence that will let them be drawn back to when they are known to have existed.

**What to find, per body** (in this order):

- **A. First sighting.** Look for the body in the Estimates and service plan of each checkpoint year below. For each one you check, record the outcome, the pages you read, the name as printed and the ministry it is printed under. Record non-matches too, but never take a start or end from one: budgets omit, merge and move units. Do not stop at the first non-match.
- **B. Start.** The instrument or announcement that created it (Act, order in council, news release, annual report), with the date at the precision the source gives. A first sighting is not a start.
- **C. Names and parents over time.** Each earlier name, and the ministry or Crown it sat under, with dates.

**Rules.** Every claim needs a URL and a locator (page, section, paragraph). Keep the source's precision: "2004" stays "2004". Unknown stays \`null\`, with the reason in \`note\`. Record a parent only where a source places the body inside that ministry; a budget heading, funding or appointments are not parentage (record the heading in \`sources_checked\`). A function is not a body: "fire protection began in 1874" does not date the Wildfire Service. Wikipedia is a lead, never the only source.
`)
  if (parentsTable.length) {
    lines.push(`**Where to look, by year.** The ministry that most likely held these bodies in each checkpoint year, following the ministry lineage the atlas holds. It is a lead: branches moved between ministries, so if a body is not under the expected ministry, search the whole volume.

| Parent today | ${CHECKPOINTS.join(' | ')} |
|---|${CHECKPOINTS.map(() => '---').join('|')}|
${parentsTable.map((p) => `| ${cell(nameOf(p))} | ${CHECKPOINTS.map((y) => cell(parentIn(p, y) ?? '—')).join(' | ')} |`).join('\n')}
`)
  }
  const crowns = batch.parents.filter((p) => !/^ministry-/.test(p ?? ''))
  if (crowns.length) lines.push(`**Crown and agency parents** (${crowns.map(nameOf).join(', ')}): look in the parent's annual reports and service plans, and the notes to its consolidated financial statements, which list subsidiaries each year.
`)
  lines.push(`**Sources that work** (checked ${asOf}): Estimates \`https://www.bcbudget.gov.bc.ca/<year>/pdf/<year>_Estimates.pdf\` (2020 onward) or \`https://www.bcbudget.gov.bc.ca/<year>/estimates/<year>_Estimates.pdf\` (2010–2019); for 2002–2009 start at \`https://www.bcbudget.gov.bc.ca/<year>/default.htm\` (per-ministry service plans at \`<year>/sp/<ministry>/<ministry>.pdf\`, Estimates under \`<year>/est/toc.htm\`). Service plans from 2010 are at \`https://www.bcbudget.gov.bc.ca/<year>/sp/pdf/ministry/<abbr>.pdf\`, where the abbreviation varies by year; find it from the year's \`default.htm\`. Beyond these: BC Laws for Acts and orders in council, news.gov.bc.ca for announcements (2001 onward), BC Archives authority records, and the Wayback Machine for old gov.bc.ca pages.

## The bodies (${batch.items.length})
`)
  batch.items.forEach((item, index) => {
    const held = item.held
    lines.push(`### ${index + 1}. ${item.name}${item.shortName ? ` (${item.shortName})` : ''}

- **id** \`${item.id}\` · ${item.kind ?? 'kind unknown'} · **${PRIORITY[item.priority]}**
- **Today:** under ${item.parent_today_name}.${item.official_url ? ` Official site: ${item.official_url}` : ''}
- **Collected from:** ${item.source_today ?? 'no source recorded'}
${item.description ? `- **What it does:** ${item.description}\n` : ''}- **Held:** ${held.established ? `began ${held.established}${held.established_meaning ? ` (${held.established_meaning})` : ''}` : 'no start date'}${held.first_observed ? `; first seen ${held.first_observed}` : ''}${held.names.length ? `; names on file: ${held.names.map((n) => `${n.name} (${n.coverage === 'observation_only' ? `seen ${n.observed_on}` : `${n.from ?? '?'}–${n.to ?? ''}`})`).join(', ')}` : ''}${held.parents.length ? `; parents on file: ${held.parents.map((p) => `${p.name} (${p.coverage === 'observation_only' ? `seen ${p.observed_on}` : `${p.from ?? '?'}–${p.to ?? ''}`})`).join(', ')}` : ''}
${held.events.length ? `- **Events on file:** ${held.events.map((e) => `${e.date ?? '?'} ${String(e.type).replace(/_/g, ' ')}`).join('; ')}\n` : ''}- **Review:** ${item.review_status === 'not_researched' ? 'not yet researched' : `partly reviewed (${item.review_status}): extend the existing record, do not start again`}
- **Search for:** "${item.name}"${item.shortName ? `, "${item.shortName}"` : ''}${held.names.filter((n) => n.name !== item.name).map((n) => `, "${n.name}"`).join('')}
${item.generic_questions ? '- **Questions:** A, B and C, as above.\n' : `- **Questions:**\n${item.questions.map((q) => `  - ${q}`).join('\n')}\n`}`)
  })
  const skeleton = batch.items.map((item) => ({
    id: item.id,
    name: item.name,
    kind: item.kind,
    parent_today: item.parent_today,
    established: null,
    first_observed: null,
    ended: null,
    names: [],
    parents: [],
    relations: [],
    research_events: [],
    date_claims: [],
    legal_basis: null,
    evidence_status: null,
    note: '',
    review: { checked: null, by: null, scope: `Batch ${batch.number}`, sources_checked: [], unresolved_fields: [], full_history_complete: false }
  }))
  lines.push(`## Hand back

Return **one JSON object for the batch, with one record per body**, in the shape of this skeleton, with every field you could not establish left \`null\` or empty and the reason in \`note\`. The field-by-field format, with a worked example, is in \`research/queue/README.md\` §6. Return new sources with them as \`{id, url, title, evidence}\`.

\`\`\`json
${JSON.stringify({ batch: batch.number, records: skeleton, sources: [] }, null, 2)}
\`\`\`
`)
  return lines.join('\n')
}

rmSync(`${OUT}/batches`, { recursive: true, force: true })
mkdirSync(`${OUT}/batches`, { recursive: true })
for (const batch of batches) writeFileSync(`${OUT}/${batch.file}`, batchMarkdown(batch))

writeFileSync(`${OUT}/sub-agencies.json`, JSON.stringify({
  schema: 'research-queue/1',
  generated_from: 'src/government/historyData.js and eventsData.js',
  as_of: asOf,
  checkpoints: CHECKPOINTS,
  priorities: PRIORITY,
  counts: all,
  batches: batches.map((b) => ({ number: b.number, title: b.title, file: b.file, parents: b.parents, items: b.items.map((i) => i.id) })),
  items
}, null, 2) + '\n')

writeFileSync(`${OUT}/INDEX.md`, `# Sub-agency research queue

_Generated by \`npm run build:research-queue\` on the data as of ${asOf}. Start with [README.md](README.md), which explains the work; each batch below is a self-contained packet you can hand to one researcher._

**Where things stand.** ${all.total} of today's sub-agencies. **${all.p1}** have nothing on file before ${present} (P1), **${all.p2}** are undated but have some history (P2), and **${all.p3}** are dated and need their history over time (P3). Sub-agencies drawn: ${[present, present - 1, 2020, 2010, 2000].map((y) => `${y}: ${drawn(y)}`).join(' · ')}.

| Batch | Parents | Bodies | P1 | P2 | P3 |
|---|---|---:|---:|---:|---:|
${batches.map((b) => { const c = counts(b.items); return `| [${b.number}](${b.file}) | ${cell(b.title)} | ${c.total} | ${c.p1 || ''} | ${c.p2 || ''} | ${c.p3 || ''} |` }).join('\n')}

The machine-readable list, with every body's questions and what is held, is [sub-agencies.json](sub-agencies.json).
`)

console.log(`${items.length} sub-agencies in ${batches.length} batches (P1 ${all.p1}, P2 ${all.p2}, P3 ${all.p3})`)
