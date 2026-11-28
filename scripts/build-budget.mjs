// Builds the government view's Budget mode from the Province's Summary Financial Statements
// (research/finance/province-summary/) and the Public Accounts table of Crown corporations, agencies
// and the SUCH sector (research/finance/public-accounts-23-1/):
//
//   * for each fiscal year, total revenue by source and total expense by function, as printed in the
//     Consolidated Statement of Operations, with the year's PDF and page;
//   * under each function, the bodies the Public Accounts list under that sector, with their own
//     revenue and expense from the Adjusted Net Income table, and the SUCH sector totals;
//   * under "Net earnings of self-supported Crown corporations and agencies", those corporations.
//
// Every printed subtotal is checked: the lines against the revenue and expense totals, and the
// totals and the items below them against each "Surplus (deficit)" line, in every column printed
// (Estimates, actual, prior year). Any difference fails the build. The statements print whole
// millions, and the Province rounds each line so that its totals add exactly: no rounding
// allowance is needed, so none is given.
//
// The bodies are joined to site ids through public/finance/<id>.json, which scripts/build-finance.mjs
// writes, so run build:finance first when the finance research changes.
//
// Outputs: src/government/budgetData.js (the statements, which ship with the Budget page) and
// public/budget/<year>.json (the bodies, fetched when a year is shown).
//
//   node scripts/build-budget.mjs          write the outputs
//   node scripts/build-budget.mjs --check  fail if any differs from what is on disk, or a sum fails

import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

export const BUDGET_CHECKED = '2026-11-27'
const SUMMARY = resolve('research/finance/province-summary')
const ACCOUNTS = resolve('research/finance/public-accounts-23-1')
const FINANCE = resolve('public/finance')
const OUT = resolve('src/government/budgetData.js')
const PUBLIC_OUT = resolve('public/budget')

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
const csv = (dir, name) => parseCsv(readFileSync(join(dir, name), 'utf8'))

/** A name reduced to its words, so "B.C. Games Society" and "BC Games Society" meet (as build-finance.mjs). */
export const nameKey = (name) => String(name).toLowerCase().normalize('NFD').replace(/\p{M}/gu, '')
  .replace(/\(pdf[^)]*\)/g, ' ').replace(/[’'.]/g, '').replace(/&/g, ' and ').replace(/[–—-]/g, ' ')
  .replace(/\bbritish columbia\b/g, 'bc').replace(/\bb c\b/g, 'bc').replace(/^the /, '')
  .replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim()
  .replace(/ (ltd|inc|limited|corp|corporation|society)$/g, '').trim()

const number = (text) => (text === '' || text === undefined ? null : Number(text))

// ── The Province's headings ──────────────────────────────────────────────────────────────────────

// A key per heading, so a line keeps its colour and its bodies across the years. The heading shown
// is always the one printed that year ("Fees and licenses" 2013-14 to 2019-20, "Investment earnings"
// to 2004-05).
const REVENUE_KEYS = [
  [/^Taxation$/, 'taxation'],
  [/^Contributions from the federal government$/, 'federal'],
  [/^Fees and licen[cs]es$/, 'fees'],
  [/^Natural resources$/, 'resources'],
  [/^Net earnings of self.supported Crown corporations and agencies$/, 'crowns'],
  [/^Investment (income|earnings)$/, 'investment'],
  [/^Miscellaneous$/, 'miscellaneous'],
  [/^Recoveries$/, 'recoveries']
]
const EXPENSE_KEYS = [
  [/^Health$/, 'health'],
  [/^Education$/, 'education'],
  [/^Social services$/, 'social'],
  [/^Protection of persons and property$/, 'protection'],
  [/^Transportation$/, 'transportation'],
  [/^Natural resources and economic development$/, 'development'],
  [/^General government$/, 'general'],
  [/^Interest$/, 'interest'],
  [/^Other$/, 'other']
]
export const keyFor = (section, heading) => {
  const found = (section === 'revenue' ? REVENUE_KEYS : EXPENSE_KEYS).find(([pattern]) => pattern.test(heading))
  if (!found) throw new Error(`No key for the ${section} heading "${heading}": add it to build-budget.mjs`)
  return found[1]
}

// The financial-statements index lists each organization under a sector heading; the sector is the
// function its spending is reported in.
const SECTOR_KEYS = {
  'Health sector': 'health',
  'Education sector': 'education',
  'Social services sector': 'social',
  'Protection of persons and property': 'protection',
  'Transportation sector': 'transportation',
  'Natural resources and economic development sector': 'development',
  'Other sector': 'other'
}
const SUCH_KEYS = {
  'School Districts': 'education', Universities: 'education', 'Colleges and Institutes': 'education',
  'Health Authorities': 'health', 'Hospital Societies': 'health'
}

// ── Checks ───────────────────────────────────────────────────────────────────────────────────────

const COLUMNS = ['estimate', 'actual', 'prior_year']

/**
 * Every printed subtotal of one year's statement of operations, against what it should be. Returns
 * the failures as sentences; an empty list means every sum holds.
 */
export const reconcile = (rows) => {
  const failures = []
  const year = rows[0]?.fiscal_year
  for (const column of COLUMNS) {
    const value = (row) => number(row[column])
    if (!rows.some((row) => value(row) !== null)) continue
    const totals = {}
    for (const section of ['revenue', 'expense']) {
      const items = rows.filter((row) => row.section === section && row.kind === 'item')
      const total = rows.filter((row) => row.section === section && row.kind === 'total')
      if (total.length !== 1) { failures.push(`${year} ${section}: ${total.length} totals printed`); continue }
      totals[section] = value(total[0])
      if (totals[section] === null) { failures.push(`${year} ${section} ${column}: no total`); continue }
      const sum = items.reduce((add, row) => add + (value(row) ?? 0), 0)
      if (sum !== totals[section]) failures.push(`${year} ${section} ${column}: the lines add to ${sum}, the total printed is ${totals[section]}`)
    }
    if (totals.revenue === undefined || totals.expense === undefined) continue
    // Down the result: each "Surplus (deficit)" line is the one above it plus what is between; a
    // "Less:" line is printed as a positive amount taken away.
    let running = totals.revenue - totals.expense
    const results = rows.filter((row) => row.section === 'result')
    if (!results.some((row) => row.kind === 'result')) failures.push(`${year}: no surplus (deficit) line`)
    for (const row of results) {
      const amount = value(row)
      if (row.kind === 'result') {
        if (amount === null) continue
        if (amount !== running) failures.push(`${year} ${column}: "${row.heading}" is printed ${amount}; the lines above give ${running}`)
        running = amount
      } else if (amount !== null) running += /^Less:/.test(row.heading) ? -amount : amount
    }
  }
  return failures
}

// ── The statement of operations ──────────────────────────────────────────────────────────────────

const statementRows = csv(SUMMARY, 'statement-of-operations.csv')
const footnoteRows = existsSync(join(SUMMARY, 'statement-of-operations-footnotes.csv')) ? csv(SUMMARY, 'statement-of-operations-footnotes.csv') : []
const byYear = new Map()
for (const row of statementRows) {
  if (!byYear.has(row.fiscal_year)) byYear.set(row.fiscal_year, [])
  byYear.get(row.fiscal_year).push(row)
}
const years = [...byYear.keys()].sort()

const failures = years.flatMap((year) => reconcile(byYear.get(year)))

/** The same line in the next year's statement, as that year restated it, when it differs. */
const restatedIn = (year, section, heading) => {
  const next = years[years.indexOf(year) + 1]
  const row = next && byYear.get(next).find((each) => each.section === section && each.heading === heading)
  return row ? { year: next, amount: number(row.prior_year) } : null
}

const statementFor = (year) => {
  const rows = byYear.get(year)
  const first = rows[0]
  const marks = new Map(footnoteRows.filter((row) => row.fiscal_year === year).map((row) => [row.mark, row.text]))
  const line = (row) => {
    const restated = row.kind === 'item' || row.kind === 'total' ? restatedIn(year, row.section, row.heading) : null
    return {
      ...(row.kind === 'item' ? { key: keyFor(row.section, row.heading) } : {}),
      heading: row.heading,
      actual: number(row.actual),
      ...(number(row.estimate) !== null ? { estimate: number(row.estimate) } : {}),
      ...(restated && restated.amount !== null && restated.amount !== number(row.actual) ? { restated } : {}),
      ...(row.footnotes ? { note: marks.get(row.footnotes) ?? null } : {})
    }
  }
  const section = (name) => ({
    lines: rows.filter((row) => row.section === name && row.kind === 'item').map(line).sort((a, b) => b.actual - a.actual),
    total: line(rows.find((row) => row.section === name && row.kind === 'total'))
  })
  const results = rows.filter((row) => row.section === 'result')
  const final = results.filter((row) => row.kind === 'result' && number(row.actual) !== null).at(-1)
  return {
    year,
    fyEnd: first.fy_end,
    source: { url: first.source_url, pdfPage: Number(first.pdf_page), ...(first.printed_page ? { printedPage: Number(first.printed_page) } : {}), title: first.table_title },
    revenue: section('revenue'),
    expense: section('expense'),
    // What stands between the totals and the year's result: a forecast allowance, a pension
    // settlement, a restructuring. Only lines with an actual figure.
    between: results.filter((row) => row.kind === 'adjustment' && number(row.actual) !== null)
      .map((row) => ({ heading: row.heading, actual: /^Less:/.test(row.heading) ? -number(row.actual) : number(row.actual) })),
    surplus: { heading: final.heading, actual: number(final.actual), ...(number(final.estimate) !== null ? { estimate: number(final.estimate) } : {}) }
  }
}

// ── The bodies ───────────────────────────────────────────────────────────────────────────────────

const { HISTORICAL_BODIES, SUB_AGENCIES, LOCAL_BODIES } = await import(pathToFileURL(resolve('src/government/historyData.js')).href)
const { CURRENT_BODIES } = await import(pathToFileURL(resolve('src/government/currentData.js')).href)
const { RELATED_BODIES } = await import(pathToFileURL(resolve('src/government/relatedBodies.js')).href)
const atlas = new Map()
for (const body of [...HISTORICAL_BODIES, ...SUB_AGENCIES, ...LOCAL_BODIES]) if (body.name && !atlas.has(body.id)) atlas.set(body.id, body)
for (const body of CURRENT_BODIES) if (!atlas.has(body.id)) atlas.set(body.id, body)
const related = new Map(RELATED_BODIES.map((body) => [body.id, body]))

// The atlas as the government view draws it in a year (unconfirmed and local bodies included), so a
// link opens a year the body is on the diagram.
const { governmentIn, FIRST_YEAR, PRESENT_YEAR } = await import(pathToFileURL(resolve('src/government/snapshot.js')).href)
const drawn = new Map()
const drawnIn = (at) => {
  if (!drawn.has(at)) drawn.set(at, new Set(governmentIn(at, { includeUndated: true, includeLocal: true }).nodes.map((node) => node.id)))
  return drawn.get(at)
}
const localIds = new Set(LOCAL_BODIES.map((body) => body.id))

/**
 * Where a body's page is: a related body's record, or the atlas in the year nearest the fiscal year
 * that draws it (the fiscal year's first calendar year, then its second, then outward).
 */
export const placeOf = (id, year) => {
  if (related.has(id)) return { related: true }
  if (!atlas.has(id)) return null
  const first = Number(year.slice(0, 4))
  const local = localIds.has(id) ? { local: true } : {}
  for (const at of [first, first + 1]) if (at <= PRESENT_YEAR && drawnIn(at).has(id)) return { at, ...local }
  for (let step = 1; step <= PRESENT_YEAR - FIRST_YEAR; step += 1) {
    for (const at of [first - step, first + 1 + step]) {
      if (at >= FIRST_YEAR && at <= PRESENT_YEAR && drawnIn(at).has(id)) return { at, ...local }
    }
  }
  return null
}

const financeFiles = existsSync(FINANCE) ? readdirSync(FINANCE).filter((name) => name.endsWith('.json') && name !== 'sectors.json') : []
const tableId = new Map() // `${year}|${printed name}` → id
const statementId = new Map() // statement URL → id
const sectorOf = new Map() // `${id}|${year}` → sector heading
for (const name of financeFiles) {
  const file = JSON.parse(readFileSync(join(FINANCE, name), 'utf8'))
  for (const row of file.table ?? []) tableId.set(`${row.year}|${row.name}`, file.body)
  for (const statement of file.statements ?? []) {
    statementId.set(statement.url, file.body)
    if (statement.sector) sectorOf.set(`${file.body}|${statement.year}`, statement.sector)
  }
}

// The site's names, for SUCH members the finance files do not carry; only a name that one body holds.
const siteNames = new Map()
const addName = (name, id) => {
  if (!name) return
  const key = nameKey(name)
  siteNames.set(key, siteNames.has(key) && siteNames.get(key) !== id ? null : id)
}
for (const body of RELATED_BODIES) for (const name of [body.name, body.shortName, ...(body.aliases ?? [])]) addName(name, body.id)
for (const body of atlas.values()) if (!body.id.startsWith('sub-')) addName(body.name, body.id)

const inventory = csv(ACCOUNTS, 'inventory.csv')
const inventorySector = new Map() // `${nameKey}|${year}` → sector, and `${nameKey}` → the latest
for (const row of inventory) {
  inventorySector.set(`${nameKey(row.organization)}|${row.fiscal_year}`, row.sector)
  inventorySector.set(nameKey(row.organization), row.sector)
}
const postSecondary = csv(ACCOUNTS, 'post-secondary-statements.csv')

const table = csv(ACCOUNTS, 'adjusted-net-income.csv')
// One table URL per year; each row keeps its PDF page.
const tableSource = (row) => Number(row.pdf_page)
const unsectored = new Set()

const bodiesFor = (year) => {
  const rows = table.filter((row) => row.fiscal_year === year && row.is_subtotal !== 'yes')
  const crowns = []
  const selfSupported = []
  const such = []
  const named = new Set()
  for (const row of rows) {
    const figures = { revenue: number(row.c1), expense: number(row.c2) === null ? null : -number(row.c2), netIncome: number(row.c3) }
    const id = tableId.get(`${year}|${row.name_as_printed}`) ?? null
    const link = id ? { id, ...placeOf(id, year) } : {}
    named.add(nameKey(row.name_as_printed))
    if (/^SUCH/i.test(row.section_as_printed)) {
      const key = SUCH_KEYS[row.name_as_printed]
      if (key) such.push({ name: row.name_as_printed, function: key, revenue: figures.revenue, expense: figures.expense, page: tableSource(row) })
      continue
    }
    if (/^Self/i.test(row.section_as_printed)) {
      selfSupported.push({ name: row.name_as_printed, ...link, netIncome: figures.netIncome, page: tableSource(row) })
      continue
    }
    const sector = (id && sectorOf.get(`${id}|${year}`)) ?? inventorySector.get(`${nameKey(row.name_as_printed)}|${year}`) ?? inventorySector.get(nameKey(row.name_as_printed)) ?? null
    const key = SECTOR_KEYS[sector] ?? null
    if (!key) unsectored.add(`${year} ${row.name_as_printed}`)
    crowns.push({ name: row.name_as_printed, ...link, function: key, revenue: figures.revenue, expense: figures.expense, page: tableSource(row) })
  }
  // The SUCH sector's members: Health and Education organizations with a statement this year and no
  // row of their own in the table.
  const members = new Map()
  const member = (name, url, sector) => {
    const key = nameKey(name)
    if (named.has(key) || members.has(key) || key === 'school districts') return
    const id = statementId.get(url) ?? siteNames.get(key) ?? null
    members.set(key, { name, ...(id ? { id, ...placeOf(id, year) } : {}), function: SECTOR_KEYS[sector] })
  }
  for (const row of inventory) if (row.fiscal_year === year && (row.sector === 'Health sector' || row.sector === 'Education sector') && !/self/i.test(row.reporting_basis)) member(row.organization, row.document_url, row.sector)
  for (const row of postSecondary) if (row.fiscal_year === year) member(row.institution.replace(/\s*\(PDF[^)]*\)\s*$/, ''), row.document_url, 'Education sector')
  const byName = (a, b) => a.name.localeCompare(b.name, 'en-CA')
  const url = rows[0]?.source_url ?? null
  return {
    year,
    checked: BUDGET_CHECKED,
    note: 'Each body\'s own revenue and expense, $ millions as printed in the Adjusted Net Income table, before inter-entity eliminations. Expense is printed there as a deduction; here it is shown as a positive amount.',
    source: url ? { title: 'Public Accounts, Supplementary Information: Adjusted Net Income of Crown Corporations, Agencies and the SUCH Sector', url } : null,
    crowns: crowns.sort(byName),
    selfSupported: selfSupported.sort(byName),
    such,
    members: [...members.values()].sort(byName)
  }
}

// ── Writing ──────────────────────────────────────────────────────────────────────────────────────

/** Every output file, by path, with its text. */
export const build = () => {
  const statements = years.map(statementFor)
  const files = new Map()
  for (const year of years) files.set(join(PUBLIC_OUT, `${year}.json`), `${JSON.stringify(bodiesFor(year))}\n`)
  const sources = {
    statements: { title: 'Province of British Columbia, Public Accounts: Summary Financial Statements, Consolidated Statement of Operations', url: 'https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts' },
    table: { title: 'Public Accounts, Supplementary Information: Adjusted Net Income of Crown Corporations, Agencies and the SUCH Sector', url: 'https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts' },
    sectors: { title: 'Public Accounts: financial statements of government organizations, by sector', url: 'https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements' }
  }
  files.set(OUT, [
    '// Generated by scripts/build-budget.mjs from research/finance/province-summary/ and',
    '// research/finance/public-accounts-23-1/. Do not edit.',
    '//',
    '// BUDGET_STATEMENTS: each fiscal year\'s Consolidated Statement of Operations, in $ millions as',
    '// printed, lines largest first. The bodies under each function are in public/budget/<year>.json.',
    '',
    `export const BUDGET_CHECKED = ${JSON.stringify(BUDGET_CHECKED)}`,
    `export const BUDGET_SOURCES = ${JSON.stringify(sources, null, 2)}`,
    `export const BUDGET_STATEMENTS = ${JSON.stringify(statements)}`,
    ''
  ].join('\n'))
  return files
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  const CHECK = process.argv.includes('--check')
  if (failures.length) {
    console.error(`${failures.length} printed subtotal(s) do not reconcile:\n  ${failures.join('\n  ')}`)
    process.exit(1)
  }
  const files = build()
  const stale = existsSync(PUBLIC_OUT) ? readdirSync(PUBLIC_OUT).map((name) => join(PUBLIC_OUT, name)).filter((path) => !files.has(path)) : []
  if (CHECK) {
    const differ = [...files].filter(([path, text]) => !existsSync(path) || readFileSync(path, 'utf8') !== text).map(([path]) => path)
    if (differ.length || stale.length) {
      console.error(`Out of date (run npm run build:budget):\n  ${[...differ, ...stale].map((path) => relative(process.cwd(), path)).join('\n  ')}`)
      process.exit(1)
    }
  } else {
    mkdirSync(PUBLIC_OUT, { recursive: true })
    for (const path of stale) rmSync(path)
    for (const [path, text] of files) writeFileSync(path, text)
  }
  const lines = statementRows.length
  console.log(`${years.length} years (${years[0]} to ${years.at(-1)}), ${lines} printed lines, every subtotal reconciles${unsectored.size ? `; ${unsectored.size} table rows with no sector` : ''}${CHECK ? ' — up to date' : ''}`)
}
