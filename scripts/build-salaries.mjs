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
// Run: npm run build:salaries -- <folder holding the data/ directory>

import { readFileSync, readdirSync, statSync, writeFileSync, mkdirSync, rmSync } from 'node:fs'
import { resolve, dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

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
const index = { source: 'pssdb public-sector salary disclosures, as supplied 2026-10-22', years: YEARS.map(({ label, slug }) => ({ label, slug })), bodies: {}, unmatched: {} }

for (const year of YEARS) {
  const byBody = new Map()
  for (const file of year.files.flatMap((path) => filesOf(resolve(source, path)))) {
    const rows = csvRows(readFileSync(file, 'utf8').replace(/^﻿/, ''))
    const header = rows.next().value.map((name) => name.trim().toLowerCase())
    const at = (name) => header.indexOf(name)
    for (const row of rows) {
      const agency = row[at('agency')]?.trim()
      const id = BODIES[agency]
      if (!id) {
        const sector = row[at('sector')]?.trim() ?? ''
        const key = `${agency} (${sector})`
        index.unmatched[key] = (index.unmatched[key] ?? 0) + 1
        continue
      }
      const remuneration = money(row[at('remuneration')])
      if (remuneration === null) continue
      const department = at('department') >= 0 ? row[at('department')]?.trim() || null : null
      if (!byBody.has(id)) byBody.set(id, { agencies: new Set(), rows: [] })
      const body = byBody.get(id)
      body.agencies.add(agency)
      body.rows.push([row[at('name')]?.trim() || null, row[at('position')]?.trim() || null, remuneration, money(row[at('expenses')]), ...(department ? [department] : [])])
    }
  }
  mkdirSync(resolve(out, year.slug), { recursive: true })
  for (const [id, { agencies, rows }] of byBody) {
    rows.sort((a, b) => b[2] - a[2] || String(a[0]).localeCompare(String(b[0])))
    writeFileSync(resolve(out, year.slug, `${id}.json`), JSON.stringify({ year: year.label, agencies: [...agencies].sort(), rows }))
    const pay = rows.map((row) => row[2])
    ;(index.bodies[id] ??= {})[year.slug] = {
      count: rows.length, total: pay.reduce((a, b) => a + b, 0), median: median(pay), max: pay[0], agencies: [...agencies].sort()
    }
  }
  console.log(`${year.label}: ${byBody.size} bodies, ${[...byBody.values()].reduce((sum, body) => sum + body.rows.length, 0)} rows`)
}

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
