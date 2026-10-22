// Public-sector pay, as employers disclose it, joined to the bodies the government atlas draws.
//
// British Columbia's public employers publish what they paid each employee over $75,000 (and every
// elected official) under the Financial Information Act and the Public Sector Employers Act. The
// files read here are those disclosures as compiled in the "pssdb" data supplied on 22 October
// 2026 (data/pssdb-fye17_18.csv, data/pssdb-fye22_21/, data/pssdb-fye23_24/): one row per person,
// with the employer as the compiler names it. This script names each employer as the atlas does, so
// a body's panel can show who it paid, and writes one small file per body and year to
// public/salaries/, fetched only when that body is opened.
//
// Only provincial bodies are kept. Municipalities, school districts, universities, police boards,
// TransLink, Metro Vancouver, Providence Health Care and BC Ferries (a company since 2003) are not
// bodies the atlas draws, and the index says how many rows of each were left out. The provincial
// public service is disclosed as one employer, not by ministry, so it is kept as one.
//
// A year that only repeats the one before is left out. The compiled 2020/21 files give BC Hydro,
// Powerex and Powertech the 2017/18 rows again — every name at the same pay to the dollar — so
// for an employer whose rows in a year are, nearly all, the previous year's names at the previous
// year's pay, that year is dropped everywhere and listed in the index as repeated.
//
// It also writes the salary search's index (public/salaries/people/): every named row of every
// employer in the files — cities, schools and universities too — grouped by the first two letters
// of the surname and gzipped, so a search loads only the slice its surname falls in, and a person
// can be followed from one year's disclosure to the next.
//
// Run: npm run build:salaries -- <folder holding the data/ directory>

import { readFileSync, readdirSync, statSync, writeFileSync, mkdirSync, rmSync } from 'node:fs'
import { resolve, dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gzipSync } from 'node:zlib'
import { surnameShard } from '../src/salaries/people.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const source = process.argv[2]
if (!source) { console.error('usage: npm run build:salaries -- <folder holding data/>'); process.exit(2) }
const out = resolve(root, 'public/salaries')

/** Each disclosure year: the files that hold it and the label it is shown under. */
const YEARS = [
  { label: '2017/18', slug: '2017-18', files: ['data/pssdb-fye17_18.csv'] },
  { label: '2020/21', slug: '2020-21', files: ['data/pssdb-fye22_21'] },
  { label: '2023/24', slug: '2023-24', files: ['data/pssdb-fye23_24'] }
]

/**
 * The employer as compiled, to the atlas body it is. A body renamed between disclosures keeps the
 * id it had in that year (the Oil and Gas Commission is not the BC Energy Regulator's 2020 self).
 */
const BODIES = {
  'B.C. Assessment': 'bc-assessment',
  'B.C. Housing': 'bc-housing',
  'B.C. Investment Management Corporation': 'bc-investment-management-corporation',
  'B.C. Investment Management Corporation (BCI)': 'bc-investment-management-corporation',
  'B.C. Lottery Corporation': 'bclc',
  'B.C. Lottery Corporation (BCLC)': 'bclc',
  'B.C. Oil and Gas Commission': 'oil-and-gas-commission',
  'B.C. Energy Regulator': 'bc-energy-regulator',
  'B.C. Pavilion Corporation': 'bc-pavilion-corporation',
  'B.C. Securities Commission': 'bc-securities-commission',
  'B.C. Transit': 'bc-transit',
  'B.C. Utilities Commission': 'bc-utilities-commission',
  'BC Hydro and Power Authority': 'bc-hydro',
  'B.C. Hydro': 'bc-hydro',
  'Columbia Basin Trust': 'columbia-basin-trust',
  'Columbia Power Corporation': 'columbia-power',
  'Community Living B.C.': 'community-living-bc',
  'Forestry Innovation Investsment': 'forestry-innovation-investment',
  'Forestry Innovation Investment': 'forestry-innovation-investment',
  'ICBC': 'icbc',
  'Legal Services Society': 'legal-aid-bc',
  'Legal Aid B.C.': 'legal-aid-bc',
  'Powerex Corporation': 'sub-powerex',
  'Powerex': 'sub-powerex',
  'Powertech Labs. Inc.': 'sub-powertech-labs',
  'PowerTech': 'sub-powertech-labs',
  'Royal B.C. Museum': 'royal-bc-museum',
  'Technical Safety B.C.': 'technical-safety-bc',
  'Worksafe B.C.': 'workers-compensation-board',
  'WorkSafe B.C.': 'workers-compensation-board',
  'B.C. Council for International Education': 'bc-council-for-international-education',
  'B.C. Financial Services Authority': 'bc-financial-services-authority',
  'B.C. Infrastructure Benefits': 'bc-infrastructure-benefits',
  'B.C. Liquor Distribution Branch': 'liquor-distribution-branch',
  'Liquor Distribution Branch': 'liquor-distribution-branch',
  'B.C. Pension Corp.': 'bc-pension-corporation',
  'Destination B.C.': 'destination-bc',
  "First Peoples' Cultural Council": 'first-peoples-cultural-council',
  'First Peoples’ Heritage, Language and Culture Council': 'first-peoples-cultural-council',
  'Forest Enhancement Society of B.C.': 'forest-enhancement-society',
  'InBC Investment Corp.': 'inbc',
  'Industry Training Authority of B.C.': 'industry-training-authority',
  'Skilled Trades B.C.': 'skilledtradesbc',
  'Infrastructure B.C.': 'infrastructure-bc',
  'Innovate B.C.': 'innovate-bc',
  'Knowledge Network': 'knowledge-network',
  'Transportation Investment Corporation': 'transportation-investment-corporation',
  'Fraser Health': 'fraser-health',
  'Interior Health': 'interior-health',
  'Northern Health': 'northern-health',
  'PHSA': 'provincial-health-services-authority',
  'Provincial Health Services Authority (PHSA)': 'provincial-health-services-authority',
  'Vancouver Coastal Health': 'vancouver-coastal-health',
  'Vancouver Island Health': 'island-health',
  'Island Health': 'island-health',
  // The public service, disclosed as one employer: shown on every ministry, and on its agency.
  'Provincial government': 'public-service'
}

/** RFC 4180 rows, with quoted fields that may hold commas, quotes and line breaks. */
function * csvRows (text) {
  let row = []
  let field = ''
  let quoted = false
  for (let i = 0; i < text.length; i += 1) {
    const c = text[i]
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i += 1 } else if (c === '"') quoted = false
      else field += c
    } else if (c === '"') quoted = true
    else if (c === ',') { row.push(field); field = '' } else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i += 1
      row.push(field); field = ''
      if (row.some((value) => value !== '')) yield row
      row = []
    } else field += c
  }
  if (field || row.length) { row.push(field); yield row }
}

const filesOf = (path) => (statSync(path).isDirectory()
  ? readdirSync(path).filter((name) => name.endsWith('.csv')).sort().map((name) => join(path, name))
  : [path])

const money = (value) => {
  const number = Number(String(value ?? '').replace(/[$,\s]/g, ''))
  return Number.isFinite(number) && String(value ?? '').trim() !== '' && value !== 'NA' ? Math.round(number) : null
}

const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[middle] : Math.round((sorted[middle - 1] + sorted[middle]) / 2)
}

rmSync(out, { recursive: true, force: true })
const index = { source: 'pssdb public-sector salary disclosures, as supplied 2026-10-22', years: YEARS.map(({ label, slug }) => ({ label, slug })), bodies: {}, unmatched: {}, repeated: [] }

// One employer under the names it is filed as from year to year: an atlas body by its id, any other
// by its name read plainly ("B.C." and "British Columbia" as "BC", a school board as its district, a
// parenthesis dropped), and a few spellings that are plainly one employer. Names that differ in more
// than that ("Ridge-Meadows" for "Maple Ridge/Pitt Meadows") stay apart.
const SAME_EMPLOYER = {
  emilycarr: 'emily-carr-university', 'emily-carr': 'emily-carr-university', 'oakanagan-college': 'okanagan-college',
  'providence-health': 'providence-health-care', 'township-of-langley': 'langley-township', 'district-of-delta': 'city-of-delta',
  'district-of-mission': 'city-of-mission'
}
const employerSlug = (name) => {
  if (BODIES[name]) return BODIES[name]
  const slug = String(name).toLowerCase()
    .replace(/\([^)]*\)/g, ' ').replace(/\bb\.\s*c\./g, 'bc').replace(/\bbritish columbia\b/g, 'bc').replace(/&/g, ' and ')
    .replace(/\bschool board\b/g, 'school district').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  return SAME_EMPLOYER[slug] ?? slug
}
// The compilers spell the sectors differently from year to year.
const SECTORS = [
  [/crown/i, 'Crown corporations'], [/health/i, 'Health authorities'], [/school/i, 'School districts'],
  [/universit|college/i, 'Universities and colleges'], [/police/i, 'Municipal police'], [/government/i, 'Government']
]
const sectorOf = (sector) => SECTORS.find(([pattern]) => pattern.test(sector))?.[1] ?? sector

// ── Reading: every row with pay, as { year, agency, sector, slug, name, position, pay, expenses } ──

const all = []
for (const [yearIndex, year] of YEARS.entries()) {
  for (const file of year.files.flatMap((path) => filesOf(resolve(source, path)))) {
    const rows = csvRows(readFileSync(file, 'utf8').replace(/^﻿/, ''))
    const header = rows.next().value.map((name) => name.trim().toLowerCase())
    const at = (name) => header.indexOf(name)
    for (const row of rows) {
      const agency = row[at('agency')]?.trim()
      const pay = money(row[at('remuneration')])
      if (!agency || pay === null) continue
      const position = row[at('position')]?.trim() || null
      const department = at('department') >= 0 ? row[at('department')]?.trim() || null : null
      all.push({
        year: yearIndex, agency, sector: sectorOf(row[at('sector')]?.trim() ?? ''), slug: employerSlug(agency),
        name: row[at('name')]?.trim() || null, position: [position, department].filter(Boolean).join(' · ') || null,
        pay, expenses: money(row[at('expenses')])
      })
    }
  }
}

// ── A year that repeats the one before, by employer ──

const keyOf = (row) => `${(row.name ?? '').toLowerCase()}|${row.pay}`
const dropped = new Set()
const grouped = new Map()
for (const row of all) {
  if (!grouped.has(row.slug)) grouped.set(row.slug, YEARS.map(() => []))
  grouped.get(row.slug)[row.year].push(row)
}
for (const [slug, years] of grouped) {
  for (let year = 1; year < YEARS.length; year += 1) {
    const before = new Set(years[year - 1].map(keyOf))
    const now = years[year]
    if (now.length < 20 || before.size < 20) continue
    const same = now.filter((row) => before.has(keyOf(row))).length
    if (same / now.length >= 0.8) {
      dropped.add(`${slug}|${year}`)
      index.repeated.push({ employer: slug, year: YEARS[year].label, repeats: YEARS[year - 1].label, rows: now.length, same })
    }
  }
}
const rows = all.filter((row) => !dropped.has(`${row.slug}|${row.year}`))
for (const each of index.repeated) console.log(`left out: ${each.employer} ${each.year}, which repeats ${each.repeats} (${each.same} of ${each.rows} rows)`)

// ── Each atlas body's rows by year, for its panel ──

for (const [yearIndex, year] of YEARS.entries()) {
  mkdirSync(resolve(out, year.slug), { recursive: true })
  const byBody = new Map()
  for (const row of rows.filter((each) => each.year === yearIndex)) {
    const id = BODIES[row.agency]
    if (!id) {
      const key = `${row.agency} (${row.sector})`
      index.unmatched[key] = (index.unmatched[key] ?? 0) + 1
      continue
    }
    if (!byBody.has(id)) byBody.set(id, { agencies: new Set(), rows: [] })
    byBody.get(id).agencies.add(row.agency)
    byBody.get(id).rows.push([row.name, row.position, row.pay, row.expenses])
  }
  for (const [id, { agencies, rows: list }] of byBody) {
    list.sort((a, b) => b[2] - a[2] || String(a[0]).localeCompare(String(b[0])))
    writeFileSync(resolve(out, year.slug, `${id}.json`), JSON.stringify({ year: year.label, agencies: [...agencies].sort(), rows: list }))
    const pay = list.map((row) => row[2])
    ;(index.bodies[id] ??= {})[year.slug] = {
      count: list.length, total: pay.reduce((a, b) => a + b, 0), median: median(pay), max: pay[0], agencies: [...agencies].sort()
    }
  }
  console.log(`${year.label}: ${byBody.size} bodies, ${[...byBody.values()].reduce((sum, body) => sum + body.rows.length, 0)} rows`)
}

// ── Employers: each one's rows, for its page of positions ──

mkdirSync(resolve(out, 'employers'), { recursive: true })
const employerList = []
const bySlug = new Map()
for (const row of rows) {
  if (!bySlug.has(row.slug)) bySlug.set(row.slug, [])
  bySlug.get(row.slug).push(row)
}
for (const [slug, list] of [...bySlug].sort(([a], [b]) => a.localeCompare(b))) {
  const out_ = list.map((row) => [row.name, row.position, row.pay, row.expenses, row.year])
    .sort((a, b) => a[4] - b[4] || b[2] - a[2] || String(a[0]).localeCompare(String(b[0])))
  // Node writes no timestamp into the gzip header, so the same rows always make the same bytes.
  writeFileSync(resolve(out, 'employers', `${slug}.json.gzip`), gzipSync(JSON.stringify(out_), { level: 9 }))
  const tally = new Map()
  for (const row of list) tally.set(row.sector, (tally.get(row.sector) ?? 0) + 1)
  employerList.push({
    slug,
    names: [...new Set(list.map((row) => row.agency))].sort(),
    sector: [...tally].sort((a, b) => b[1] - a[1])[0][0],
    body: BODIES[list[0].agency] ?? null,
    counts: YEARS.map((_, at) => list.filter((row) => row.year === at).length),
    repeated: index.repeated.filter((each) => each.employer === slug).map((each) => each.year)
  })
}
writeFileSync(resolve(out, 'employers', 'index.json'), JSON.stringify({
  note: 'Each employer, under every name it is filed as; rows in <slug>.json.gzip are [name, position, remuneration, expenses, year].',
  years: YEARS.map(({ label }) => label),
  employers: employerList
}) + '\n')
console.log(`employers: ${employerList.length}`)

// ── People: the named rows by the first two letters of the surname ──

const employerAt = new Map(employerList.map((employer, at) => [employer.slug, at]))
mkdirSync(resolve(out, 'people'), { recursive: true })
const shards = new Map()
for (const row of rows) {
  if (!row.name) continue
  const shard = surnameShard(row.name)
  if (!shards.has(shard)) shards.set(shard, [])
  shards.get(shard).push([row.name, row.position, row.pay, row.expenses, employerAt.get(row.slug), row.year])
}
const counts = {}
for (const [shard, list] of [...shards].sort(([a], [b]) => a.localeCompare(b))) {
  list.sort((a, b) => a[0].localeCompare(b[0]) || a[5] - b[5] || b[2] - a[2])
  writeFileSync(resolve(out, 'people', `${shard}.json.gzip`), gzipSync(JSON.stringify(list), { level: 9 }))
  counts[shard] = list.length
}
writeFileSync(resolve(out, 'people', 'index.json'), JSON.stringify({
  note: 'Rows: [name, position, remuneration, expenses, employer, year]; employer is an index into employers ([name, sector, atlas body, slug]), year into years.',
  years: YEARS.map(({ label }) => label),
  employers: employerList.map(({ slug, names, sector, body }) => [names.at(-1), sector, body, slug]),
  shards: counts
}) + '\n')
console.log(`people: ${Object.values(counts).reduce((a, b) => a + b, 0)} rows in ${shards.size} slices`)

index.unmatched = Object.fromEntries(Object.entries(index.unmatched).sort((a, b) => b[1] - a[1]))
writeFileSync(resolve(out, 'index.json'), JSON.stringify(index, null, 1) + '\n')
writeFileSync(resolve(root, 'src/government/salaryIndex.js'), `// Generated by scripts/build-salaries.mjs — do not edit.
//
// Which bodies have disclosed pay, and its totals by year; the rows themselves are fetched from
// public/salaries/<year>/<body>.json when a body is opened.

export const SALARY_YEARS = ${JSON.stringify(index.years)}

export const SALARY_INDEX = ${JSON.stringify(index.bodies)}
`)
console.log(`index: ${Object.keys(index.bodies).length} bodies; ${Object.values(index.unmatched).reduce((a, b) => a + b, 0)} rows not of an atlas body`)
