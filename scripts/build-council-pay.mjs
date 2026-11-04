// Build the independently sourced council-pay companion without rewriting salary/name indexes.
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gunzipSync } from 'node:zlib'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const researchPath = 'research/salaries/council-pay-history-2026-11-04'
export const cents = (value) => Math.round(value * 100)
const dollars = (value) => value / 100
const total = (values) => dollars(values.reduce((sum, value) => sum + cents(value ?? 0), 0))
const slug = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const sortedYears = (values) => [...new Set(values)].sort((a, b) => a - b)
const json = (path) => JSON.parse(readFileSync(path, 'utf8'))

/** A table's source spelling, precision and missing cells survive normalization. */
export function checkTable(table) {
  assert.ok(table.rows.length > 0, `${table.year}: empty council schedule`)
  assert.equal(table.printedTotals.length, table.columns.length)
  const names = new Set()
  for (const row of table.rows) {
    assert.equal(row.values.length, table.columns.length, `${table.year} ${row.sourceName}: columns`)
    assert.ok(row.sourceName && !names.has(row.sourceName), `${table.year}: duplicate or empty name`)
    names.add(row.sourceName)
    assert.ok(row.values.every((value) => value === null || Number.isFinite(value)), `${table.year}: numeric cells`)
  }
  return table.columns.map((column, index) => {
    const actual = table.rows.reduce((sum, row) => sum + cents(row.values[index] ?? 0), 0)
    const expected = cents(table.printedTotals[index])
    assert.equal(actual, expected, `${table.year} ${column}: printed total mismatch`)
    return { year: table.year, column, printedTotal: table.printedTotals[index], sumOfDisclosedCells: dollars(actual), missingCells: table.rows.filter((row) => row.values[index] === null).length }
  })
}

export function normalizePayment(table, row) {
  const modern = table.columns.includes('remuneration')
  const components = Object.fromEntries(table.columns.map((key, index) => [key, row.values[index]]))
  const expenseKeys = modern ? ['localExpenses', 'travelConferences'] : table.columns.filter((key) => !['income', 'municipalOfficersAllowance'].includes(key))
  const expensesKnown = expenseKeys.every((key) => components[key] !== null)
  const remuneration = modern ? components.remuneration : total([components.income, components.municipalOfficersAllowance ?? 0])
  const mayor = /^(P\.?\s*Owen|L\.?\s*Campbell|L\.?\s*Campell|Stewart,\s*K|Sim,\s*K)/i.test(row.sourceName)
  const notes = []
  if (table.year <= 1995) notes.push('Remuneration includes income plus the separately printed municipal officers allowance. Both source components are retained.')
  if (table.year === 1995) notes.push('The municipal officers allowance ended during 1995 and local-expense reimbursement began; the table records actual payments through that change.')
  if (!expensesKnown) notes.push('At least one expense cell is blank or unstated. The expense total is unknown; knownExpenses is only the sum of disclosed components.')
  if (table.year === 1998 && /Sullivan/i.test(row.sourceName)) {
    components.priorPeriodAutoAllowancePaidSeparately = 1563.65
    notes.push('A footnote separately reports $1,563.65 paid in 1998 for 1997 auto allowance, in addition to this table. It is retained as a separate component and excluded from the table expense sum.')
  }
  if ([1999, 2002, 2022, 2025].includes(table.year)) notes.push('Council changed during this year. Payments may cover partial terms or transition amounts and are not annualized.')
  if (table.year === 2002 && /Campell|Woodworth/i.test(row.sourceName)) notes.push('The name retains the spelling in this report. It has not been silently expanded or merged with another identity.')
  if (table.year === 2003) notes.push('Travel and conference amounts are net of recoveries.')
  if (modern) {
    notes.push('Remuneration may include additional council duties and deferred remuneration. It is actual reported pay, not an annual base rate.')
    notes.push('Expenses here sum local expenses and travel/conferences, net of recoveries. The separate discretionary budget is retained in components and excluded; mayoral expenses can also include political staff travel.')
    if (mayor) notes.push('Discretionary expenses can include political staff salaries and office costs; they are not the mayor’s salary.')
  }
  if (table.year === 2024 && /Boyle,/i.test(row.sourceName)) notes.push('Boyle resigned effective December 12, 2024. This payment includes deferred remuneration for the outgoing council member.')
  if (table.year === 2020) notes.push('The source notes minor remuneration overpayments repaid in 2021 and December duties paid in January 2021.')
  if (table.year === 2021) notes.push('December duty and deputy-mayor payments were made in January 2022.')
  if (row.footnote === 5) notes.push(/Carr/i.test(row.sourceName) ? 'Carr resigned during 2025.' : 'Maloney and Orr were elected during 2025.')
  return {
    id: `vancouver-council-${table.year}-${slug(row.sourceName)}`,
    municipality: 'Vancouver', employerSlug: 'city-of-vancouver', name: row.sourceName,
    role: mayor ? 'Mayor' : 'Councillor', year: table.year, currency: 'CAD', measure: 'actual-remuneration',
    remuneration, expenses: expensesKnown ? total(expenseKeys.map((key) => components[key])) : null,
    knownExpenses: total(expenseKeys.map((key) => components[key])), components,
    sourceId: `vancouver-council-payments-${table.year}`, ...(table.pdfPage ? { pdfPage: table.pdfPage } : {}), notes
  }
}

export function validateDataset(data) {
  const ids = new Set(); const sources = new Set(data.sources.map((source) => source.id))
  assert.equal(sources.size, data.sources.length, 'Duplicate source ID')
  for (const source of data.sources) assert.match(source.url, /^https?:\/\//, `${source.id}: source URL`)
  for (const row of [...data.observations, ...data.payments]) {
    assert.ok(!ids.has(row.id), `Duplicate observation ID: ${row.id}`); ids.add(row.id)
    assert.ok(sources.has(row.sourceId), `${row.id}: missing source`)
    assert.ok(row.municipality && row.employerSlug, `${row.id}: missing municipality`)
    assert.ok(['Mayor', 'Councillor'].includes(row.role), `${row.id}: role`)
    assert.ok(Number.isInteger(row.year) && row.year >= 1800 && row.year <= 2026, `${row.id}: year`)
    assert.equal(row.currency, 'CAD'); assert.ok(Array.isArray(row.notes))
  }
  const officeKeys = new Set()
  for (const row of data.observations) {
    assert.ok(Number.isFinite(row.amount) && row.amount >= 0, `${row.id}: amount`)
    assert.ok(['reported-office-pay', 'annual-base-rate'].includes(row.measure), `${row.id}: measure`)
    const key = [row.sourceId, row.employerSlug, row.year, row.role, row.effectiveFrom ?? '', row.effectiveTo ?? ''].join('|')
    assert.ok(!officeKeys.has(key), `Duplicate office observation: ${key}`); officeKeys.add(key)
  }
  for (const row of data.payments) {
    assert.ok(row.name && Number.isFinite(row.remuneration), `${row.id}: named payment`)
    assert.ok(row.expenses === null || Number.isFinite(row.expenses), `${row.id}: expense amount`)
  }
  return true
}

/** Verify both sides of retained source editions; a supplied agreement flag is never trusted. */
export function checkSourceComparisons(comparisons, payments, compiled, years) {
  const seen = new Set()
  for (const comparison of comparisons) {
    assert.ok(!seen.has(comparison.officialObservationId), 'Duplicate source-edition comparison')
    seen.add(comparison.officialObservationId)
    const row = payments.find((payment) => payment.id === comparison.officialObservationId)
    assert.ok(row, `${comparison.officialObservationId}: source comparison missing payment`)
    assert.equal(row.year, comparison.officialYear)
    assert.equal(row.name, comparison.officialName)
    assert.equal(row.remuneration, comparison.officialRemuneration)
    assert.equal(row.expenses, comparison.officialExpenses)
    const matches = compiled.filter((entry) => entry[0] === comparison.compiledName && entry[1] === row.role && entry[2] === comparison.compiledRemuneration && entry[3] === comparison.compiledExpenses && years[entry[4]].label === comparison.compiledEditionLabel && entry[5] === comparison.compiledSourceId)
    assert.equal(matches.length, 1, `${row.id}: compiled source-edition record differs`)
    assert.equal(comparison.expensesAgree, row.expenses === comparison.compiledExpenses, `${row.id}: expense agreement flag differs`)
  }
}

/** Reconcile every CBC figure to its wide-table transcription, including the older-year exception. */
export function checkCbc2021(evidence, observations) {
  assert.equal(evidence.blocks.length, 8, 'CBC 2021: eight table blocks required')
  const selected = observations.filter((row) => row.sourceId === 'cbc-bc-municipal-office-pay-2021')
  assert.equal(selected.length, 320, 'CBC 2021: 320 office observations required')
  const names = new Set(); let verified = 0
  for (const block of evidence.blocks) {
    assert.equal(block.rows.length, 20, `CBC block ${block.block}: incomplete table`)
    for (const original of block.rows) {
      assert.ok(!names.has(original.municipality), `CBC: repeated municipality ${original.municipality}`)
      names.add(original.municipality)
      for (const role of ['Mayor', 'Councillor']) {
        const rows = selected.filter((row) => row.sourceMunicipalityOriginal === original.municipality && row.role === role)
        assert.equal(rows.length, 1, `CBC ${original.municipality}: ${role} missing or repeated`)
        assert.equal(rows[0].amount, original[role.toLowerCase()], `CBC ${original.municipality} ${role}: amount differs`)
        assert.equal(rows[0].year, original.municipality === 'Port Hardy' ? 2020 : 2021, `CBC ${original.municipality}: reference year`)
        assert.equal(rows[0].tableBlock, block.block, 'CBC: source block differs')
        verified += 1
      }
    }
  }
  assert.equal(new Set(selected.map((row) => row.employerSlug)).size, 160, 'CBC: municipality mapping collision')
  return verified
}

export const csvCell = (value) => {
  const text = String(value ?? '')
  return `"${(typeof value === 'string' && /^[=+\-@\t\r]/.test(text) ? `'${text}` : text).replace(/"/g, '""')}"`
}
export function datasetCsv(data) {
  const sources = new Map(data.sources.map((source) => [source.id, source]))
  const headings = ['id', 'record_type', 'municipality', 'employer_slug', 'role', 'name_as_reported', 'year', 'measure', 'amount_cad', 'expenses_cad', 'known_expenses_cad', 'annual_supplement_cad', 'effective_from', 'effective_to', 'effective_date_note', 'source_id', 'source_url', 'source_original_url', 'source_title', 'source_kind', 'source_locator', 'row_locator', 'pdf_page', 'table_page', 'table_block', 'components_json', 'notes']
  const rows = [...data.observations.map((row) => [row, 'office']), ...data.payments.map((row) => [row, 'payment'])].map(([row, kind]) => {
    const source = sources.get(row.sourceId)
    return [row.id, kind, row.municipality, row.employerSlug, row.role, row.name, row.year, row.measure, row.amount ?? row.remuneration, row.expenses, row.knownExpenses, row.annualSupplement, row.effectiveFrom, row.effectiveTo, row.effectiveDateNote, row.sourceId, source.url, source.originalUrl, source.title, source.kind, source.locator, row.sourceLocator, row.pdfPage, row.tablePage, row.tableBlock, row.components ? JSON.stringify(row.components) : '', [...(source.notes ?? []), ...row.notes].join(' | ')]
  })
  headings.push('schedule_version', 'effective_date_sources', 'supporting_sources_json')
  const all = [...data.observations, ...data.payments]
  rows.forEach((values, index) => values.push(all[index].scheduleVersion, (all[index].effectiveDateSources ?? []).join(' | '), JSON.stringify(sources.get(all[index].sourceId)?.supportingSources ?? [])))
  return [headings, ...rows].map((row) => row.map(csvCell).join(',')).join('\r\n') + '\r\n'
}

export function buildCouncilPay(repoRoot = root) {
  const research = join(repoRoot, researchPath)
  const files = readdirSync(research).filter((file) => file.endsWith('.json') && !['validation.json', 'coverage.json'].includes(file)).sort()
  const inputs = files.map((file) => ({ file, value: json(join(research, file)) }))
  const data = { version: 1, asOf: '2026-11-04', sources: [], observations: [], payments: [], coverage: {} }
  const controls = []; const held = []
  for (const { file, value } of inputs) {
    if (value.sources && value.observations) {
      data.sources.push(...value.sources)
      data.observations.push(...value.observations)
    }
    if (file.startsWith('vancouver-') && value.tables) {
      for (const table of value.tables) {
        controls.push(...checkTable(table))
        data.sources.push({ id: `vancouver-council-payments-${table.year}`, title: `City of Vancouver — ${table.year} council remuneration and expenses`, url: table.sourceUrl, kind: 'official-named-payments', retrievedOn: '2026-11-04', ...(table.pdfPage ? { locator: `PDF page ${table.pdfPage}` } : {}), notes: ['Factual table transcribed from the official municipal report; all printed numeric column totals reconcile. Names remain as reported.'] })
        data.payments.push(...table.rows.map((row) => normalizePayment(table, row)))
      }
      held.push(...(value.held ?? []))
    }
  }
  const surveyValueChecks = checkCbc2021(inputs.find(({ file }) => file === 'cbc-2021-transcription-evidence.json').value, data.observations)
  const comparisons = inputs.find(({ file }) => file === 'existing-source-comparison.json')?.value.comparisons ?? []
  const compiledPath = 'public/salaries/employers/city-of-vancouver.json.gzip'
  const salaryYearsPath = 'src/government/salaryIndex.js'
  const salaryYears = JSON.parse(readFileSync(join(repoRoot, salaryYearsPath), 'utf8').match(/^export const SALARY_YEARS = (.+)$/m)[1])
  checkSourceComparisons(comparisons, data.payments, JSON.parse(gunzipSync(readFileSync(join(repoRoot, compiledPath)))), salaryYears)
  for (const comparison of comparisons) {
    const row = data.payments.find((payment) => payment.id === comparison.officialObservationId)
    row.existingEdition = { sourceId: comparison.compiledSourceId, editionLabel: comparison.compiledEditionLabel, name: comparison.compiledName, remuneration: comparison.compiledRemuneration, expenses: comparison.compiledExpenses, expensesAgree: comparison.expensesAgree }
    row.notes.push(`A retained compiled ${comparison.compiledEditionLabel} edition has a candidate record with the same surname, role and remuneration. It remains a separate source edition; do not add the records together or infer an identity link.`)
    if (!comparison.expensesAgree) row.notes.push(`Source discrepancy: the compiled edition records $${comparison.compiledExpenses.toLocaleString('en-CA')} in expenses; this official calendar-year schedule records $${row.expenses.toLocaleString('en-CA')}. Both source amounts are retained.`)
  }
  data.observations.sort((a, b) => a.municipality.localeCompare(b.municipality, 'en') || a.year - b.year || a.role.localeCompare(b.role) || a.id.localeCompare(b.id))
  data.payments.sort((a, b) => a.year - b.year || a.name.localeCompare(b.name))
  data.sources.sort((a, b) => a.id.localeCompare(b.id))
  const roster = json(join(repoRoot, 'research/salaries/municipal-audit/roster.json')).municipalities
  data.coverage = {
    officeObservations: data.observations.length, paymentObservations: data.payments.length,
    municipalityCount: new Set([...data.observations, ...data.payments].map((row) => row.employerSlug)).size,
    officeYears: sortedYears(data.observations.map((row) => row.year)), paymentYears: sortedYears(data.payments.map((row) => row.year)),
    sourceCount: data.sources.length, held,
    candidateSourceEditionOverlaps: comparisons.length,
    sourceEditionExpenseDifferences: comparisons.filter((comparison) => !comparison.expensesAgree).length,
    surveys: inputs.filter(({ value }) => value.extractionStatus).map(({ file, value }) => ({ input: `${researchPath}/${file}`, status: value.extractionStatus, ...value.coverage })),
    notes: [
      'This is a source inventory with selected historical coverage, not a complete annual series for every BC municipality. Missing years are unknown, not zero.',
      'Office survey figures, scheduled annual rates and payments to named officials have distinct definitions. No combined pay total, inflation adjustment, interpolation or automatic growth comparison is calculated.',
      'Council records are separate from employee disclosures. Existing salary files and name-link groups are not rebuilt or merged by this companion.',
      'Some modern Vancouver officials already appear in retained compiled editions. The official calendar-year source remains separate; do not add the two source editions together.',
      'Vancouver named-payment coverage currently omits 1996 (source errors), 2004–2019 (not extracted here), and years before 1994. Annual-rate coverage does not fill those payment gaps.',
      'A current municipal roster is a discovery aid and does not establish that every municipality existed in each historical year.'
    ],
    municipalities: roster.map((entry) => ({ municipality: entry.municipality, employerSlug: entry.employerSlug, website: entry.website, officeYears: sortedYears(data.observations.filter((row) => row.employerSlug === entry.employerSlug).map((row) => row.year)), paymentYears: sortedYears(data.payments.filter((row) => row.employerSlug === entry.employerSlug).map((row) => row.year)) }))
  }
  validateDataset(data)
  const output = JSON.stringify(data) + '\n'
  const outputs = { 'public/salaries/council-pay.json': output, 'public/salaries/council-pay.csv': datasetCsv(data), [`${researchPath}/coverage.json`]: JSON.stringify(data.coverage, null, 2) + '\n' }
  const validation = {
    version: 1, asOf: data.asOf, scope: 'Council-pay companion only; existing salary and name-link exports are untouched.',
    counts: { sources: data.sources.length, officeObservations: data.observations.length, namedPayments: data.payments.length, columnControls: controls.length, surveyValueChecks },
    inputs: [...inputs.filter(({ value }) => value.sources || value.tables || value.comparisons || value.blocks).map(({ file }) => `${researchPath}/${file}`), 'research/salaries/municipal-audit/roster.json', compiledPath, salaryYearsPath].map((path) => ({ path, sha256: createHash('sha256').update(readFileSync(join(repoRoot, path))).digest('hex') })),
    controls,
    outputs: Object.entries(outputs).map(([path, content]) => ({ path, sha256: createHash('sha256').update(content).digest('hex'), bytes: Buffer.byteLength(content) }))
  }
  outputs[`${researchPath}/validation.json`] = JSON.stringify(validation, null, 2) + '\n'
  return { data, outputs, validation }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { outputs, validation } = buildCouncilPay()
  const check = process.argv.includes('--check')
  for (const [path, content] of Object.entries(outputs)) {
    if (check) assert.equal(readFileSync(join(root, path), 'utf8'), content, `${path}: stale output; run npm run build:council-pay`)
    else { mkdirSync(dirname(join(root, path)), { recursive: true }); writeFileSync(join(root, path), content) }
  }
  console.log(`${check ? 'Verified' : 'Built'} council pay: ${validation.counts.officeObservations} office observations; ${validation.counts.namedPayments} named payments; ${validation.counts.columnControls} source-column totals reconcile.`)
}
