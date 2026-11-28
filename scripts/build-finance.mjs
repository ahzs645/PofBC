// Builds the atlas's Money card data from the Public Accounts research
// (research/finance/public-accounts-23-1/):
//
//   * every published financial statement of a body the atlas or the related-body catalogue holds,
//     by fiscal year, from inventory.csv (the Public Accounts' own lists) and
//     post-secondary-statements.csv (the ministry's page for universities and colleges);
//   * every row of the Supplementary Information table "Adjusted Net Income of Crown Corporations,
//     Agencies and the SUCH Sector", as printed, from adjusted-net-income.csv
//     (scripts/extract_adjusted_net_income.py reads it from the PDFs).
//
// Outputs, following the Salaries split (a small index with the page, detail fetched on demand):
//
//   src/government/financeIndex.js     per body: how many statements and table years it has
//   public/finance/<body>.json         per body: its statements and its table rows, with sources
//   public/finance/sectors.json        the SUCH sector rows, which stay sector totals
//
// A Public Accounts organization is joined to a site id by crosswalk.csv, corrected and extended by
// site-ids.csv. Where the crosswalk gives several ids for one organization (a body renamed in the
// atlas), the one standing at the fiscal year's end is used. A table row is joined by its printed
// name to an organization's published names, or by site-ids.csv. Figures are kept exactly as printed,
// in $ millions; nothing is restated, adjusted for inflation or summed across bodies.
//
//   node scripts/build-finance.mjs          write the outputs
//   node scripts/build-finance.mjs --check  fail if any output differs from what is on disk

import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { HISTORICAL_BODIES, SUB_AGENCIES, LOCAL_BODIES } from '../src/government/historyData.js'
import { CURRENT_BODIES } from '../src/government/currentData.js'
import { RELATED_BODIES } from '../src/government/relatedBodies.js'
import { MINISTRY_EPISODES } from '../src/government/episodes.js'

const CHECK = process.argv.includes('--check')
const RESEARCH = resolve('research/finance/public-accounts-23-1')
const INDEX_OUT = resolve('src/government/financeIndex.js')
const PUBLIC_OUT = resolve('public/finance')
export const FINANCE_CHECKED = '2026-11-27'

// ── Reading ──────────────────────────────────────────────────────────────────────────────────────

/** RFC 4180 CSV, as Python's csv module writes it. */
export const parseCsv = (text) => {
  const rows = []
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
      row.push(field); rows.push(row); row = []; field = ''
    } else field += c
  }
  if (field || row.length) { row.push(field); rows.push(row) }
  const [head, ...body] = rows.filter((each) => each.length > 1 || each[0])
  return body.map((each) => Object.fromEntries(head.map((key, at) => [key, each[at] ?? ''])))
}
const csv = (name) => parseCsv(readFileSync(join(RESEARCH, name), 'utf8'))

/** A name reduced to its words, so "B.C. Games Society" and "BC Games Society" meet. */
export const nameKey = (name) => String(name).toLowerCase().normalize('NFD').replace(/\p{M}/gu, '')
  .replace(/\(pdf[^)]*\)/g, ' ').replace(/[’'.]/g, '').replace(/&/g, ' and ').replace(/[–—-]/g, ' ')
  .replace(/\bbritish columbia\b/g, 'bc').replace(/\bb c\b/g, 'bc').replace(/^the /, '')
  .replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim()
  .replace(/ (ltd|inc|limited|corp|corporation|society)$/g, '').trim()

const fyEnd = (year) => `${Number(year.slice(0, 4)) + 1}-03-31`

// ── The site's bodies ────────────────────────────────────────────────────────────────────────────

const atlas = new Map()
for (const body of [...HISTORICAL_BODIES, ...SUB_AGENCIES, ...LOCAL_BODIES]) if (body.name && !atlas.has(body.id)) atlas.set(body.id, body)
for (const body of CURRENT_BODIES) if (!atlas.has(body.id)) atlas.set(body.id, body)
const related = new Map(RELATED_BODIES.map((body) => [body.id, body]))
export const isSiteBody = (id) => atlas.has(id) || related.has(id)
const nameOf = (id) => atlas.get(id)?.name ?? related.get(id)?.name ?? id

/** Whether a body stood on a day, from its atlas record; a related body, or one with no dates, does. */
const standsOn = (id, day) => {
  const body = atlas.get(id)
  if (!body) return true
  const start = body.established ? String(body.established) : null
  const end = body.ended ? String(body.ended) : null
  const pad = (date) => (date.length === 4 ? `${date}-01-01` : date.length === 7 ? `${date}-01` : date)
  return (!start || pad(start) <= day) && (!end || pad(end) > day)
}

// ── Organizations to site ids ────────────────────────────────────────────────────────────────────

const crosswalk = new Map(csv('crosswalk.csv').map((row) => [row.org_key, row]))
const siteIds = csv('site-ids.csv')
const byOrgKey = new Map(siteIds.filter((row) => row.match === 'org_key').map((row) => [row.key, row.body_id]))
const byName = new Map(siteIds.filter((row) => row.match === 'name').map((row) => [nameKey(row.key), row.body_id]))
// A blank body_id keeps a name off every body: an organization the site does not hold, filed in the
// Public Accounts under another's key.
for (const id of [...byOrgKey.values(), ...byName.values()]) if (id && !isSiteBody(id)) throw new Error(`site-ids.csv names ${id}, which is not an atlas or related body`)

/** The site id for an organization in a fiscal year, or null. */
const bodyFor = (orgKey, year) => {
  if (byOrgKey.has(orgKey)) return byOrgKey.get(orgKey)
  const row = crosswalk.get(orgKey)
  if (!row) return null
  const ids = [...new Set([...row.atlas_ids.split(';'), ...row.related_body_ids.split(';')].filter((id) => id && isSiteBody(id)))]
  if (ids.length <= 1) return ids[0] ?? null
  // None standing at the year's end: the statements are a wound-up body's last, so the one that ended last.
  const ended = ids.filter((id) => atlas.get(id)?.ended).sort((x, y) => String(atlas.get(y).ended).localeCompare(String(atlas.get(x).ended)))
  const standing = ids.filter((id) => standsOn(id, fyEnd(year)))
  if (!standing.length && ended.length) standing.push(ended[0])
  // An atlas body standing that day first, then a related body, then a sub-agency of the same name.
  const tiers = [standing.filter((id) => atlas.has(id) && !id.startsWith('sub-')), standing.filter((id) => related.has(id)), standing]
  const ranked = tiers.find((tier) => tier.length) ?? []
  if (ranked.length !== 1) throw new Error(`${orgKey} ${year}: ${ranked.length ? ranked.join(', ') : 'none of ' + ids.join(', ')} stand(s) at ${fyEnd(year)}; settle it in site-ids.csv`)
  return ranked[0]
}

// ── Statements ───────────────────────────────────────────────────────────────────────────────────

const basisOf = (text) => (/self-supported|GBE|modified equity/i.test(text) ? 'self-supported' : /taxpayer/i.test(text) ? 'taxpayer-supported' : null)
const inventory = csv('inventory.csv')
const statements = new Map()
const unmatched = new Map()
const add = (id, entry) => {
  if (!statements.has(id)) statements.set(id, [])
  const list = statements.get(id)
  if (!list.some((each) => each.year === entry.year && each.url === entry.url)) list.push(entry)
}
const orgKeyByName = new Map()
for (const row of inventory) {
  orgKeyByName.set(nameKey(row.organization), row.org_key)
  if (row.org_key === 'school-districts') continue
  const id = byName.has(nameKey(row.organization)) ? byName.get(nameKey(row.organization)) : bodyFor(row.org_key, row.fiscal_year)
  if (!id) { unmatched.set(row.org_key, row.organization); continue }
  add(id, {
    year: row.fiscal_year, fyEnd: row.fy_end, name: row.organization, url: row.document_url,
    sector: row.sector, basis: basisOf(row.reporting_basis),
    hosted: /ministry|page/.test(row.hosted) ? 'ministry page' : 'Public Accounts',
    ...(row.note ? { note: row.note } : {})
  })
}
const POST_SECONDARY_PAGE = 'https://www2.gov.bc.ca/gov/content/education-training/post-secondary-education/institution-resources-administration/financial-reporting/audited-financial-statements'
for (const row of csv('post-secondary-statements.csv')) {
  const name = row.institution.replace(/\s*\(PDF[^)]*\)\s*$/, '')
  const orgKey = orgKeyByName.get(nameKey(name))
  const id = orgKey ? bodyFor(orgKey, row.fiscal_year) : null
  if (!id) { unmatched.set(orgKey ?? nameKey(name), name); continue }
  add(id, { year: row.fiscal_year, fyEnd: fyEnd(row.fiscal_year), name, url: row.document_url, sector: 'Education sector', basis: 'taxpayer-supported', hosted: 'ministry page' })
}

// ── The Adjusted Net Income table ────────────────────────────────────────────────────────────────

const KEYS = ['revenue', 'expense', 'netIncome', 'adjustments', 'fifth', 'adjustedNetIncome']
const headings = new Map()
for (const row of csv('adjusted-net-income-columns.csv')) {
  if (!headings.has(row.fiscal_year)) headings.set(row.fiscal_year, [])
  headings.get(row.fiscal_year)[Number(row.position) - 1] = row.heading_as_printed
}
const footnotes = new Map()
for (const row of csv('adjusted-net-income-footnotes.csv')) footnotes.set(`${row.fiscal_year}#${row.mark}`, row.text)
const SECTORS = /^(School Districts|Universities|Colleges and Institutes|Health Authorities|Hospital Societies|SUCH sector)$/
const table = new Map()
const sectors = []
const unmatchedRows = new Map()
for (const row of csv('adjusted-net-income.csv')) {
  // Subtotals are left out, except the SUCH sector's own total, which is kept with the sector rows.
  if (row.is_subtotal === 'yes' && !(/^SUCH/i.test(row.section_as_printed) && row.name_as_printed === 'SUCH sector')) continue
  const figures = Object.fromEntries(KEYS.map((key, at) => [key, row[`c${at + 1}`] === '' ? null : Number(row[`c${at + 1}`])]))
  const marks = row.footnotes ? row.footnotes.split(' ') : []
  const notes = marks.map((mark) => {
    const [, column, number] = mark.match(/^(?:c(\d):)?(\d+)$/) ?? []
    const text = footnotes.get(`${row.fiscal_year}#${number}`)
    return text ? { ...(column ? { column: KEYS[Number(column) - 1] } : {}), text } : null
  }).filter(Boolean)
  const entry = {
    year: row.fiscal_year, fyEnd: row.fy_end, name: row.name_as_printed,
    basis: /^self/i.test(row.section_as_printed) ? 'self-supported' : 'taxpayer-supported',
    figures, headings: headings.get(row.fiscal_year), unit: row.unit,
    source: { url: row.source_url, pdfPage: Number(row.pdf_page), ...(row.printed_page ? { printedPage: Number(row.printed_page) } : {}) },
    ...(notes.length ? { notes } : {})
  }
  if (/^SUCH/i.test(row.section_as_printed) && SECTORS.test(row.name_as_printed)) { sectors.push(entry); continue }
  const key = nameKey(row.name_as_printed)
  const orgKey = orgKeyByName.get(key)
  const id = byName.has(key) ? byName.get(key) : orgKey ? bodyFor(orgKey, row.fiscal_year) : null
  if (!id) { unmatchedRows.set(row.name_as_printed, (unmatchedRows.get(row.name_as_printed) ?? 0) + 1); continue }
  if (!table.has(id)) table.set(id, [])
  // One row per body, year and basis: a body reclassified during a year is printed in both sections
  // (Transportation Investment Corporation, 2017-18), and both rows are kept, each with its basis.
  if (table.get(id).some((each) => each.year === entry.year && each.basis === entry.basis)) throw new Error(`${id} has two ${entry.basis} table rows for ${entry.year}`)
  table.get(id).push(entry)
}

// ── Statement breakdowns (stage B) ───────────────────────────────────────────────────────────────
//
// research/finance/statements/<body>/<year>.csv, transcribed from each body's own statement of
// operations by scripts/transcribe_statement.py and checked against the page. Figures are kept as
// printed in the CSV, in the statement's unit, and turned into whole dollars here.

const FINANCE = resolve('research/finance')
const financeCsv = (name) => parseCsv(readFileSync(join(FINANCE, name), 'utf8'))
export const REVENUE_CATEGORIES = ['province', 'federal', 'own-source', 'other-entity', 'investment', 'deferred-capital-amortization', 'other']
const UNITS = { dollars: 1, thousands: 1000, millions: 1000000 }
const breakdowns = new Map()
if (existsSync(join(FINANCE, 'statements', 'index.csv'))) {
  for (const entry of financeCsv('statements/index.csv')) {
    const id = entry.body_id
    if (!isSiteBody(id)) throw new Error(`statements/index.csv: ${id} is not an atlas or related body`)
    const unit = UNITS[entry.unit]
    if (!unit) throw new Error(`statements/index.csv: ${id} ${entry.fiscal_year} has unit ${entry.unit}`)
    const lines = financeCsv(`statements/${id}/${entry.fiscal_year}.csv`)
    const pick = (section) => lines.filter((line) => line.section === section)
    const one = (section) => {
      const [line, ...more] = pick(section)
      if (!line || more.length) throw new Error(`${id} ${entry.fiscal_year}: needs one ${section} line`)
      return { label: line.label_as_printed, amount: Number(line.amount_as_printed) * unit }
    }
    const revenue = pick('revenue').map((line) => {
      if (!REVENUE_CATEGORIES.includes(line.category)) throw new Error(`${id} ${entry.fiscal_year}: ${line.label_as_printed} has category ${line.category}`)
      return { label: line.label_as_printed, amount: Number(line.amount_as_printed) * unit, category: line.category }
    })
    const expense = pick('expense').map((line) => ({ label: line.label_as_printed, amount: Number(line.amount_as_printed) * unit }))
    const record = {
      year: entry.fiscal_year, url: entry.url, title: entry.statement_title, unit: entry.unit,
      page: { pdf: Number(entry.pdf_page), ...(entry.printed_page ? { printed: entry.printed_page } : {}) },
      revenue, revenueTotal: one('revenue-total'), expense, expenseTotal: one('expense-total'), surplus: one('surplus'),
      ...(entry.expense_basis ? { expenseBasis: entry.expense_basis } : {}),
      ...(entry.note ? { note: entry.note } : {}),
      checked: entry.checked
    }
    const sum = (rows) => rows.reduce((total, row) => total + row.amount, 0)
    if (sum(revenue) !== record.revenueTotal.amount) throw new Error(`${id} ${entry.fiscal_year}: revenue lines do not add to the total`)
    if (sum(expense) !== record.expenseTotal.amount) throw new Error(`${id} ${entry.fiscal_year}: expense lines do not add to the total`)
    if (record.revenueTotal.amount - record.expenseTotal.amount !== record.surplus.amount) throw new Error(`${id} ${entry.fiscal_year}: revenue less expense is not the printed result`)
    if (!breakdowns.has(id)) breakdowns.set(id, [])
    breakdowns.get(id).push(record)
  }
}

// ── Government transfers (stage A) ───────────────────────────────────────────────────────────────
//
// research/finance/transfers/fye<YYYY>.csv: the rows of the Province's "Government Transfers"
// schedule whose payee aliases.csv matches to a site body (scripts/build_transfers.py). Unmatched
// payees, and every individual, are not in the research files at all.

const TRANSFERS_DATASET = 'https://catalogue.data.gov.bc.ca/dataset/903c41c4-09c7-4af9-a43c-af3b6ff5c705'
const transfers = new Map()
const transferYears = []
if (existsSync(join(FINANCE, 'transfers', 'totals.csv'))) {
  for (const alias of financeCsv('aliases.csv')) if (alias.body_id && !isSiteBody(alias.body_id)) throw new Error(`aliases.csv: ${alias.payee_key} names ${alias.body_id}, which is not an atlas or related body`)
  for (const file of financeCsv('transfers/totals.csv')) {
    const fye = Number(file.fye)
    const year = `${fye - 1}-${String(fye).slice(2)}`
    transferYears.push({ fye, year, url: file.source_url, rows: Number(file.rows), total: Number(file.total), matchedRows: Number(file.matched_rows), matchedTotal: Number(file.matched_total) })
    const byBody = new Map()
    for (const row of financeCsv(`transfers/fye${fye}.csv`)) {
      if (!isSiteBody(row.body_id)) throw new Error(`transfers/fye${fye}.csv: ${row.body_id} is not a site body`)
      if (!byBody.has(row.body_id)) byBody.set(row.body_id, [])
      byBody.get(row.body_id).push({ ministry: row.ministry_as_printed, amount: Number(row.amount), payee: row.payee_as_printed })
    }
    for (const [id, rows] of byBody) {
      if (!transfers.has(id)) transfers.set(id, [])
      rows.sort((a, b) => b.amount - a.amount || a.ministry.localeCompare(b.ministry))
      transfers.get(id).push({ year, fye, url: file.source_url, rows, total: rows.reduce((sum, row) => sum + row.amount, 0) })
    }
  }
}

// ── Estimates against actual, by vote (stage C) ──────────────────────────────────────────────────
//
// research/finance/estimates/votes.csv: the Public Accounts' "Schedule of Voted Appropriations by
// Ministry" (CRF Supplementary Schedules), one row per vote and the ministry or office that accessed
// it, in $ thousands as printed (scripts/extract_voted_appropriations.py). A ministry is joined to
// its atlas episode by its name, the one standing at the fiscal year's end (or its start); ids.csv
// names the offices and settles the rest.

const STOP = new Set(['of', 'and', 'the', 'for', 'minister', 'ministry', 'department', 'dept', 'provincial', 'responsible'])
const ministryKey = (name) => String(name).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[‘’ʼ']/g, '')
  .replace(/&/g, ' and ').replace(/[–—-]/g, ' ').replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter((word) => word && !STOP.has(word)).join(' ')
const episodesByKey = new Map()
for (const episode of MINISTRY_EPISODES) {
  const key = ministryKey(episode.name)
  if (!episodesByKey.has(key)) episodesByKey.set(key, [])
  episodesByKey.get(key).push(episode)
}
const episodeIds = new Set(MINISTRY_EPISODES.map((episode) => episode.id))
const OFFICE_IDS = new Set([...atlas.keys(), 'legislative-assembly'])
const estimateIds = existsSync(join(FINANCE, 'estimates', 'ids.csv')) ? financeCsv('estimates/ids.csv') : []
for (const row of estimateIds) if (!episodeIds.has(row.body_id) && !OFFICE_IDS.has(row.body_id)) throw new Error(`estimates/ids.csv: ${row.body_id} is not a ministry episode or an atlas body`)
const spends = (episode, year) => episode.from <= year && (episode.to === null || episode.to >= year)
/** The atlas id that accessed a vote, by the name printed in a year's schedule, or null. */
export const ministryFor = (printed, year) => {
  const named = estimateIds.find((row) => row.as_printed === printed && (!row.fiscal_year || row.fiscal_year === year))
  if (named) return named.body_id
  const end = Number(year.slice(0, 4)) + 1
  const candidates = episodesByKey.get(ministryKey(printed)) ?? []
  for (const pick of [candidates.filter((episode) => spends(episode, end)), candidates.filter((episode) => spends(episode, end - 1)), candidates]) if (pick.length === 1) return pick[0].id
  return null
}
const estimates = new Map()
const unplaced = new Map()
const voteFile = join(FINANCE, 'estimates', 'votes.csv')
if (existsSync(voteFile)) {
  const figure = (value) => (value === '' ? null : Number(value))
  const accessors = new Map()
  const votes = financeCsv('estimates/votes.csv')
  for (const row of votes) accessors.set(`${row.fiscal_year} ${row.vote}`, (accessors.get(`${row.fiscal_year} ${row.vote}`) ?? 0) + 1)
  for (const row of votes) {
    const id = ministryFor(row.ministry_as_printed, row.fiscal_year)
    if (!id) { unplaced.set(`${row.fiscal_year} ${row.ministry_as_printed}`, Number(row.estimates || 0)); continue }
    if (!estimates.has(id)) estimates.set(id, new Map())
    const years = estimates.get(id)
    if (!years.has(row.fiscal_year)) years.set(row.fiscal_year, { year: row.fiscal_year, url: row.source_url, unit: '$ thousands', names: new Set(), votes: [] })
    const year = years.get(row.fiscal_year)
    year.names.add(row.ministry_as_printed)
    year.votes.push({
      vote: row.vote, description: row.description, ministry: row.ministry_as_printed,
      estimates: figure(row.estimates), other: figure(row.other_authorizations), appropriation: figure(row.total_appropriation),
      actual: figure(row.actual_expense), variance: figure(row.variance),
      page: { pdf: Number(row.pdf_page), ...(row.printed_page ? { printed: row.printed_page } : {}) },
      ...(accessors.get(`${row.fiscal_year} ${row.vote}`) > 1 ? { shared: true } : {})
    })
  }
}
const estimateYears = [...new Set(existsSync(voteFile) ? financeCsv('estimates/votes.csv').map((row) => row.fiscal_year) : [])].sort()

// ── Writing ──────────────────────────────────────────────────────────────────────────────────────

const bodies = [...new Set([...statements.keys(), ...table.keys(), ...breakdowns.keys(), ...transfers.keys(), ...estimates.keys()])].sort()
const byYearDesc = (a, b) => b.year.localeCompare(a.year)
const files = new Map()
const index = {}
for (const id of bodies) {
  // The Public Accounts list links a university's or college's year to the ministry's page; where that
  // page's own list gives the PDF for the year, the PDF stands for it.
  const listed = statements.get(id) ?? []
  const isPdf = (entry) => /\.pdf$/i.test(entry.url)
  const own = listed.filter((entry) => isPdf(entry) || !listed.some((other) => other.year === entry.year && isPdf(other)))
    .sort((a, b) => byYearDesc(a, b) || a.url.localeCompare(b.url))
  const rows = (table.get(id) ?? []).sort((a, b) => byYearDesc(a, b) || a.basis.localeCompare(b.basis))
  const years = [...new Set(own.map((each) => each.year))].sort()
  const parts = (breakdowns.get(id) ?? []).sort(byYearDesc)
  const paid = (transfers.get(id) ?? []).sort(byYearDesc)
  const voted = [...(estimates.get(id)?.values() ?? [])].map(({ names, ...year }) => ({ ...year, names: [...names] })).sort(byYearDesc)
  index[id] = {
    s: own.length, ...(years.length ? { sy: [years[0], years.at(-1)] } : {}),
    t: rows.length, ...(rows.length ? { ty: [rows.at(-1).year, rows[0].year] } : {}),
    ...(parts.length ? { b: parts.map((each) => each.year).sort() } : {}),
    ...(paid.length ? { tr: [paid.at(-1).year, paid[0].year] } : {}),
    ...(voted.length ? { e: [voted.at(-1).year, voted[0].year] } : {})
  }
  const name = atlas.get(id)?.name ?? related.get(id)?.name ?? MINISTRY_EPISODES.find((episode) => episode.id === id)?.name ?? (id === 'legislative-assembly' ? 'Legislative Assembly of British Columbia' : id)
  files.set(`${id}.json`, `${JSON.stringify({
    body: id, name, checked: FINANCE_CHECKED, statements: own, table: rows,
    ...(parts.length ? { breakdowns: parts } : {}),
    ...(paid.length ? { transfers: paid } : {}),
    ...(voted.length ? { estimates: voted } : {})
  })}\n`)
}
files.set('sectors.json', `${JSON.stringify({ checked: FINANCE_CHECKED, note: 'SUCH sector rows of the Adjusted Net Income table: totals for each sector, never attributed to a body.', rows: sectors.sort(byYearDesc) })}\n`)

const tableYears = [...headings.keys()].sort()
const indexSource = `// Generated by scripts/build-finance.mjs from research/finance/public-accounts-23-1/. Do not edit.
//
// Per body: s, the number of published financial statements found (sy, their first and last fiscal
// years); t, the number of years the Public Accounts' Adjusted Net Income table has a row for it
// (ty, the first and last); b, the fiscal years whose statement of operations is transcribed line by
// line; tr, the first and last fiscal years with government transfers paid to it; e, for a ministry
// or office, the first and last fiscal years of its votes' estimates against actual. The records
// themselves are in public/finance/<id>.json.

export const FINANCE_CHECKED = ${JSON.stringify(FINANCE_CHECKED)}
export const FINANCE_TABLE_YEARS = ${JSON.stringify(tableYears)}
export const FINANCE_TRANSFER_YEARS = ${JSON.stringify(transferYears)}
export const FINANCE_ESTIMATE_YEARS = ${JSON.stringify(estimateYears)}
export const FINANCE_SOURCES = ${JSON.stringify({
  statements: { title: 'Province of British Columbia, Public Accounts: financial statements of government organizations', url: 'https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements' },
  postSecondary: { title: 'Post-secondary institutions’ audited financial statements (Ministry of Post-Secondary Education and Future Skills)', url: POST_SECONDARY_PAGE },
  table: { title: 'Public Accounts, Supplementary Information: Adjusted Net Income of Crown Corporations, Agencies and the SUCH Sector', url: 'https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts' },
  transfers: { title: 'CRF Detailed Schedules of Payments – Government Transfers (BC Data Catalogue, Open Government Licence – British Columbia)', url: TRANSFERS_DATASET },
  votes: { title: 'Public Accounts, Consolidated Revenue Fund Supplementary Schedules: Schedule of Voted Appropriations by Ministry', url: 'https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts' },
  supplement: { title: 'Supplement to the Estimates (BC Data Catalogue, Treasury Board Staff)', url: 'https://catalogue.data.gov.bc.ca/dataset?q=supplement+to+the+estimates' }
}, null, 2)}
export const FINANCE_INDEX = ${JSON.stringify(index)}
`

let stale = []
if (CHECK) {
  if (!existsSync(INDEX_OUT) || readFileSync(INDEX_OUT, 'utf8') !== indexSource) stale.push(INDEX_OUT)
  const onDisk = existsSync(PUBLIC_OUT) ? readdirSync(PUBLIC_OUT) : []
  for (const [name, text] of files) if (!onDisk.includes(name) || readFileSync(join(PUBLIC_OUT, name), 'utf8') !== text) stale.push(`public/finance/${name}`)
  for (const name of onDisk) if (!files.has(name)) stale.push(`public/finance/${name} (no longer generated)`)
  if (stale.length) { console.error(`Finance outputs need rebuilding (node scripts/build-finance.mjs):\n${stale.join('\n')}`); process.exit(1) }
} else {
  writeFileSync(INDEX_OUT, indexSource)
  if (existsSync(PUBLIC_OUT)) rmSync(PUBLIC_OUT, { recursive: true })
  mkdirSync(PUBLIC_OUT, { recursive: true })
  for (const [name, text] of files) writeFileSync(join(PUBLIC_OUT, name), text)
}

const statementCount = Object.values(index).reduce((sum, entry) => sum + entry.s, 0)
const figureCount = [...table.values(), sectors].flat().reduce((sum, row) => sum + Object.values(row.figures).filter((value) => value !== null).length, 0)
console.log(`${bodies.length} bodies: ${statementCount} statements, ${[...table.values()].flat().length} table rows (${tableYears[0]} to ${tableYears.at(-1)}), ${sectors.length} sector rows, ${figureCount} figures; ${[...breakdowns.values()].flat().length} statement breakdowns; transfers to ${transfers.size} bodies (${transferYears.length} years); estimates for ${estimates.size} ministries and offices (${estimateYears.length} years)${CHECK ? ' — up to date' : ''}`)
if (process.argv.includes('--report')) {
  console.log('Organizations with statements and no site body:', [...unmatched.entries()].map(([key, name]) => `${key} (${name})`).join('; '))
  console.log('Table rows with no site body:', [...unmatchedRows.entries()].map(([name, count]) => `${name} ×${count}`).join('; '))
  console.log('Votes accessed by a name with no atlas id:', [...unplaced.keys()].join('; '))
}
