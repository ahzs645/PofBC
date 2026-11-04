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
const unique = (values) => [...new Set(values)]

export function yearRanges(values) {
  const ranges = []
  for (const year of sortedYears(values)) {
    const last = ranges.at(-1)
    if (last && year === last[1] + 1) last[1] = year
    else ranges.push([year, year])
  }
  return ranges.map(([first, last]) => first === last ? String(first) : `${first}–${last}`).join(', ')
}

export function seriesCoverage(rows) {
  const groups = new Map()
  for (const row of rows) {
    const key = [row.employerSlug, row.role, row.measure].join('|')
    if (!groups.has(key)) groups.set(key, { municipality: row.municipality, employerSlug: row.employerSlug, role: row.role, measure: row.measure, rows: [] })
    groups.get(key).rows.push(row)
  }
  return [...groups.values()].map(({ rows: entries, ...group }) => {
    const years = sortedYears(entries.map((row) => row.year))
    const missingYears = []
    for (let year = years[0]; year <= years.at(-1); year += 1) if (!years.includes(year)) missingYears.push(year)
    return { ...group, observations: entries.length, years, ranges: yearRanges(years), missingYears, sourceIds: unique(entries.map((row) => row.sourceId)).sort() }
  }).sort((a, b) => a.municipality.localeCompare(b.municipality, 'en') || a.role.localeCompare(b.role) || a.measure.localeCompare(b.measure))
}

/** A table's source spelling, precision and missing cells survive normalization. */
export function checkTable(table) {
  assert.ok(table.rows.length > 0, `${table.year}: empty council schedule`)
  assert.equal(table.printedTotals.length, table.columns.length)
  assert.ok(table.printedTotals.every(Number.isFinite), `${table.year}: missing printed numeric total`)
  assert.equal(new Set(table.columns).size, table.columns.length, `${table.year}: duplicate column`)
  if (table.expenseColumns) {
    assert.equal(new Set(table.expenseColumns).size, table.expenseColumns.length, `${table.year}: duplicate expense component`)
    assert.ok(table.expenseColumns.every((key) => table.columns.includes(key) && !['income', 'municipalOfficersAllowance', 'remuneration', 'discretionaryExpenses'].includes(key)), `${table.year}: invalid personal expense component`)
  }
  if (table.rounding) {
    assert.equal(table.rounding.unit, 1, `${table.year}: only documented whole-dollar rounding is supported`)
    assert.ok(table.rounding.reason && table.rounding.columns.every((key) => table.columns.includes(key)), `${table.year}: incomplete rounding evidence`)
    assert.match(table.rounding.evidenceUrl, /^https?:\/\//, `${table.year}: rounding verification source`)
  }
  const names = new Set()
  for (const row of table.rows) {
    assert.equal(row.values.length, table.columns.length, `${table.year} ${row.sourceName}: columns`)
    const rowKey = row.sourceRowKey ?? row.sourceName
    assert.ok(row.sourceName && rowKey && !names.has(rowKey), `${table.year}: duplicate or empty source row`)
    names.add(rowKey)
    if (row.role) assert.ok(['Mayor', 'Councillor'].includes(row.role), `${table.year}: invalid explicit role`)
    assert.ok(row.values.every((value) => value === null || Number.isFinite(value)), `${table.year}: numeric cells`)
  }
  return table.columns.map((column, index) => {
    const actual = table.rows.reduce((sum, row) => sum + cents(row.values[index] ?? 0), 0)
    const expected = cents(table.printedTotals[index])
    const missingCells = table.rows.filter((row) => row.values[index] === null).length
    const difference = actual - expected
    let roundingLimit = 0
    if (difference && table.rounding?.columns.includes(column)) {
      assert.ok(Number.isInteger(table.printedTotals[index]) && table.rows.every((row) => row.values[index] === null || Number.isInteger(row.values[index])), `${table.year} ${column}: rounding requires whole-dollar cells`)
      // Each independently rounded disclosed row and the printed total can differ
      // from its underlying value by at most half of the reported dollar unit.
      roundingLimit = (table.rows.length - missingCells + 1) * 0.5
      assert.ok(Math.abs(difference) <= cents(roundingLimit), `${table.year} ${column}: printed total mismatch exceeds documented rounding bound`)
    } else assert.equal(actual, expected, `${table.year} ${column}: printed total mismatch`)
    if (table.rowSum) assert.equal(cents(table.rowSum[index]), actual, `${table.year} ${column}: recorded row sum differs`)
    if (table.roundingDifference) assert.equal(cents(table.roundingDifference[index]), difference, `${table.year} ${column}: recorded difference differs`)
    return { year: table.year, ...(table.tableLabel ? { tableLabel: table.tableLabel } : {}), column, printedTotal: table.printedTotals[index], sumOfDisclosedCells: dollars(actual), difference: dollars(difference), status: difference ? 'within-reported-rounding' : 'exact', roundingLimit, missingCells, ...(difference ? { roundingReason: table.rounding.reason, evidenceUrl: table.rounding.evidenceUrl } : {}) }
  })
}

/** Verify independent source editions and cent-level appendices without adding payments. */
export function checkPaymentPrecisionEvidence(table) {
  const checks = []
  for (const comparison of table.sourceComparisons ?? []) {
    assert.deepEqual(comparison.columns, table.columns, `${table.year}: comparison column definitions differ`)
    assert.equal(comparison.sourcePrecision, 1, `${table.year}: comparison precision`)
    assert.equal(comparison.rows.length, table.rows.length, `${table.year}: comparison row count`)
    let checkedCells = 0
    for (const row of comparison.rows) {
      const matches = table.rows.filter((primary) => primary.sourceName === row.sourceName && primary.role === row.role)
      assert.equal(matches.length, 1, `${table.year}: ambiguous comparison row ${row.sourceName}`)
      row.values.forEach((value, index) => {
        assert.equal(value, Math.round(matches[0].values[index]), `${table.year}: rounded comparison cell differs for ${row.sourceName}`)
        checkedCells += 1
      })
    }
    const totalDifferences = comparison.printedTotals.map((value, index) => ({ column: table.columns[index], primaryPrintedTotal: table.printedTotals[index], comparedPrintedTotal: value, roundedPrimaryMinusCompared: Math.round(table.printedTotals[index]) - value }))
    checks.push({ year: table.year, type: 'rounded-source-edition', sourceUrl: comparison.sourceUrl, checkedCells, totalDifferences })
  }
  const evidence = table.precisionEvidence
  if (evidence) {
    const index = table.columns.indexOf(evidence.column)
    assert.ok(index >= 0, `${table.year}: appendix column missing`)
    const seen = new Set()
    for (const row of evidence.rows) {
      assert.ok(!seen.has(row.sourceName), `${table.year}: repeated appendix person`); seen.add(row.sourceName)
      const matches = table.rows.filter((primary) => primary.sourceName === row.sourceName)
      assert.equal(matches.length, 1, `${table.year}: ambiguous appendix person ${row.sourceName}`)
      assert.equal(Math.round(row.amount), row.annualTableRoundedAmount, `${table.year}: appendix amount does not round to published cell`)
      assert.equal(matches[0].values[index], row.annualTableRoundedAmount, `${table.year}: appendix and annual table differ`)
    }
    const sum = total(evidence.rows.map((row) => row.amount))
    assert.equal(cents(sum), cents(evidence.printedTotal), `${table.year}: exact appendix total mismatch`)
    assert.equal(Math.round(evidence.printedTotal), table.printedTotals[index], `${table.year}: rounded appendix aggregate differs from annual printed total`)
    const unlistedNonzero = table.rows.filter((row) => !seen.has(row.sourceName) && row.values[index] !== 0)
    assert.equal(unlistedNonzero.length, 0, `${table.year}: nonzero annual payment missing from appendix`)
    checks.push({ year: table.year, type: 'exact-cent-appendix', sourceUrl: evidence.sourceUrl, column: evidence.column, checkedPersonAmounts: evidence.rows.length, exactPrintedTotal: evidence.printedTotal, exactSum: sum, annualPrintedTotal: table.printedTotals[index] })
  }
  return checks
}

export function normalizePayment(table, row) {
  const modern = table.columns.includes('remuneration')
  const components = Object.fromEntries(table.columns.map((key, index) => [key, row.values[index]]))
  const expenseKeys = table.expenseColumns ?? (modern ? ['localExpenses', ...(table.columns.includes('transportationAllowance') ? ['transportationAllowance'] : []), 'travelConferences'] : table.columns.filter((key) => !['income', 'municipalOfficersAllowance'].includes(key)))
  const expensesKnown = expenseKeys.every((key) => Number.isFinite(components[key]))
  const remuneration = modern ? components.remuneration : total([components.income, components.municipalOfficersAllowance ?? 0])
  const role = row.role ?? (/^(P\.?\s*Owen|L\.?\s*Campbell|L\.?\s*Campell|Stewart,\s*K|Sim,\s*K)/i.test(row.sourceName) ? 'Mayor' : 'Councillor')
  const mayor = role === 'Mayor'
  const notes = [...(table.notes ?? []), ...(row.notes ?? [])]
  if (row.term) notes.push(`Council term label in the source: ${row.term}. This does not establish a full year of service.`)
  if (table.rounding) notes.push('The published whole-dollar cells and printed totals have a documented difference consistent with independent rounding. Source amounts are preserved; the validation receipt records the difference and bound.')
  if (table.year <= 1995) notes.push('Remuneration includes income plus the separately printed municipal officers allowance. Both source components are retained.')
  if (table.year === 1995) notes.push('The municipal officers allowance ended during 1995 and local-expense reimbursement began; the table records actual payments through that change.')
  if (!expensesKnown) notes.push('At least one expense cell is blank or unstated. The expense total is unknown; knownExpenses is only the sum of disclosed components.')
  if (table.year === 1998 && /Sullivan/i.test(row.sourceName)) {
    components.priorPeriodAutoAllowancePaidSeparately = 1563.65
    notes.push('A footnote separately reports $1,563.65 paid in 1998 for 1997 auto allowance, in addition to this table. It is retained as a separate component and excluded from the table expense sum.')
  }
  if ([1999, 2002, 2005, 2008, 2011, 2014, 2017, 2018, 2022, 2025].includes(table.year)) notes.push('Council changed during this year. Payments may cover partial terms or transition amounts and are not annualized.')
  if (table.year === 2002 && /Campell|Woodworth/i.test(row.sourceName)) notes.push('The name retains the spelling in this report. It has not been silently expanded or merged with another identity.')
  if (table.year === 2003) notes.push('Travel and conference amounts are net of recoveries.')
  if (modern) {
    notes.push('Remuneration may include additional council duties and deferred remuneration. It is actual reported pay, not an annual base rate.')
    if (table.year >= 2020) notes.push('Expenses here sum local expenses and travel/conferences, net of recoveries. The separate discretionary budget is retained in components and excluded; mayoral expenses can also include political staff travel.')
    else if (expenseKeys.includes('transportationAllowance')) notes.push('Expenses sum local expenses, the separately printed transportation allowance, and travel/conferences. Transportation is counted once.')
    else notes.push('Expenses sum the source-designated local and travel/conference components. Any separately printed discretionary office budget is excluded.')
    if (mayor && Object.hasOwn(components, 'discretionaryExpenses')) notes.push('Discretionary expenses can include political staff salaries and office costs; they are not the mayor’s salary.')
  }
  if (table.year === 2024 && /Boyle,/i.test(row.sourceName)) notes.push('Boyle resigned effective December 12, 2024. This payment includes deferred remuneration for the outgoing council member.')
  if (table.year === 2020) notes.push('The source notes minor remuneration overpayments repaid in 2021 and December duties paid in January 2021.')
  if (table.year === 2021) notes.push('December duty and deputy-mayor payments were made in January 2022.')
  if (table.year === 2025 && row.footnote === 5) notes.push(/Carr/i.test(row.sourceName) ? 'Carr resigned during 2025.' : 'Maloney and Orr were elected during 2025.')
  return {
    id: `vancouver-council-${table.year}-${slug(row.sourceRowKey ?? row.sourceName)}`,
    municipality: 'Vancouver', employerSlug: 'city-of-vancouver', name: row.sourceName,
    role, year: table.year, currency: 'CAD', measure: 'actual-remuneration',
    remuneration, expenses: expensesKnown ? total(expenseKeys.map((key) => components[key])) : null,
    knownExpenses: total(expenseKeys.map((key) => components[key])), components, expenseComponentKeys: expenseKeys,
    sourceId: `vancouver-council-payments-${table.year}`, ...(table.pdfPage ? { pdfPage: table.pdfPage } : {}),
    ...(table.sourceLocator ? { sourceLocator: table.sourceLocator } : {}),
    ...(table.tableLabel ? { tableLabel: table.tableLabel } : {}),
    ...(row.sourceRowKey ? { sourceRowKey: row.sourceRowKey } : {}),
    ...(row.sourceRowLabel ? { sourceRowLabel: row.sourceRowLabel } : {}),
    ...(table.sourcePrecision ? { sourcePrecision: table.sourcePrecision } : {}),
    ...(row.term ? { term: row.term } : {}), notes: unique(notes)
  }
}

/** Freeze the earlier published observations while adding independently sourced years. */
export function checkExpansionPreservation(data, baseline) {
  const select = (rows, ids) => {
    const byId = new Map(rows.map((row) => [row.id, row]))
    return ids.map((id) => { assert.ok(byId.has(id), `Prior council observation missing: ${id}`); return byId.get(id) })
      .sort((a, b) => a.id.localeCompare(b.id, 'en'))
      .map((row) => Object.fromEntries(baseline.protectedFields.filter((key) => Object.hasOwn(row, key)).map((key) => [key, row[key]])))
  }
  const core = { observations: select(data.observations, baseline.protectedOfficeIds), payments: select(data.payments, baseline.protectedPaymentIds) }
  assert.equal(createHash('sha256').update(JSON.stringify(core)).digest('hex'), baseline.protectedCoreSha256, 'Prior council monetary values, roles, years or source assignments changed')
  for (const source of baseline.protectedSources) assert.equal(data.sources.find((entry) => entry.id === source.id)?.url, source.url, `Prior council source changed: ${source.id}`)
  return { baselineCommit: baseline.baselineCommit, ...baseline.counts, protectedCoreSha256: baseline.protectedCoreSha256 }
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
  headings.push('schedule_version', 'effective_date_sources', 'supporting_sources_json', 'source_effective_from', 'source_effective_to', 'source_row_key', 'source_row_label', 'table_label', 'council_term_label', 'expense_component_keys', 'reported_precision_cad')
  const all = [...data.observations, ...data.payments]
  rows.forEach((values, index) => values.push(all[index].scheduleVersion, (all[index].effectiveDateSources ?? []).join(' | '), JSON.stringify(sources.get(all[index].sourceId)?.supportingSources ?? []), all[index].sourceEffectiveFrom, all[index].sourceEffectiveTo, all[index].sourceRowKey, all[index].sourceRowLabel, all[index].tableLabel, all[index].term, (all[index].expenseComponentKeys ?? []).join(' | '), all[index].sourcePrecision ?? all[index].amountPrecisionCad))
  return [headings, ...rows].map((row) => row.map(csvCell).join(',')).join('\r\n') + '\r\n'
}

export function buildCouncilPay(repoRoot = root) {
  const research = join(repoRoot, researchPath)
  const files = readdirSync(research).filter((file) => file.endsWith('.json') && !['validation.json', 'coverage.json'].includes(file)).sort()
  const inputs = files.map((file) => ({ file, value: json(join(research, file)) }))
  const data = { version: 1, asOf: '2026-11-04', sources: [], observations: [], payments: [], coverage: {} }
  const controls = []; const held = []; const precisionEvidence = []
  const paymentSources = new Map()
  for (const { file, value } of inputs) {
    if (value.sources && value.observations) {
      data.sources.push(...value.sources)
      data.observations.push(...value.observations)
    }
    if (file.startsWith('vancouver-') && value.tables) {
      for (const table of value.tables) {
        controls.push(...checkTable(table))
        precisionEvidence.push(...checkPaymentPrecisionEvidence(table))
        const id = `vancouver-council-payments-${table.year}`
        const notes = [table.year >= 2004 && table.year <= 2019 ? 'Factual table transcribed from the official municipal report. Printed column totals are checked at the reported precision; exact and rounding-qualified controls remain distinct in the validation receipt. Names and council-term groups remain as reported.' : 'Factual table transcribed from the official municipal report; all printed numeric column totals reconcile. Names remain as reported.', ...(table.sourceFootnotes ?? []).map((note) => typeof note === 'string' ? note : `${note.marker ? `(${note.marker}) ` : ''}${note.note}`), ...(table.sourceComparisons ?? []).flatMap((comparison) => comparison.notes ?? [])]
        const supportingSources = [...(table.supportingSources ?? []), ...(table.sourceComparisons ?? []).map((comparison) => ({ title: `Alternative official ${table.year} council report`, url: comparison.sourceUrl, locator: comparison.sourceLocator, notes: comparison.notes }))]
        const source = { id, title: `City of Vancouver — ${table.year} council remuneration and expenses`, url: table.sourceUrl, kind: 'official-named-payments', retrievedOn: '2026-11-04', ...(table.sourceLocator || table.pdfPage ? { locator: table.sourceLocator ?? `PDF page ${table.pdfPage}` } : {}), notes: unique(notes), ...(supportingSources.length ? { supportingSources } : {}) }
        if (paymentSources.has(id)) {
          const prior = paymentSources.get(id)
          assert.equal(prior.url, source.url, `${table.year}: multiple primary source editions require distinct IDs`)
          prior.notes = unique([...prior.notes, ...source.notes])
          prior.locator = unique([prior.locator, source.locator].filter(Boolean)).join('; ')
          const supports = [...(prior.supportingSources ?? []), ...(source.supportingSources ?? [])]
          if (supports.length) prior.supportingSources = [...new Map(supports.map((entry) => [entry.url, entry])).values()]
        } else paymentSources.set(id, source)
        data.payments.push(...table.rows.map((row) => normalizePayment(table, row)))
      }
      held.push(...(value.held ?? []))
    }
  }
  data.sources.push(...paymentSources.values())
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
  const paymentYears = sortedYears(data.payments.map((row) => row.year))
  const paymentGaps = []
  for (let year = paymentYears[0]; year <= paymentYears.at(-1); year += 1) if (!paymentYears.includes(year)) paymentGaps.push(year)
  const preservation = checkExpansionPreservation(data, inputs.find(({ file }) => file === 'timeseries-expansion-baseline.json').value)
  data.coverage = {
    officeObservations: data.observations.length, paymentObservations: data.payments.length,
    municipalityCount: new Set([...data.observations, ...data.payments].map((row) => row.employerSlug)).size,
    officeYears: sortedYears(data.observations.map((row) => row.year)), paymentYears: sortedYears(data.payments.map((row) => row.year)),
    sourceCount: data.sources.length, held,
    timeSeries: seriesCoverage([...data.observations, ...data.payments]),
    vancouverPaymentYears: paymentYears, vancouverPaymentGaps: paymentGaps,
    candidateSourceEditionOverlaps: comparisons.length,
    sourceEditionExpenseDifferences: comparisons.filter((comparison) => !comparison.expensesAgree).length,
    surveys: inputs.filter(({ value }) => value.extractionStatus).map(({ file, value }) => ({ input: `${researchPath}/${file}`, status: value.extractionStatus, ...value.coverage })),
    notes: [
      'This is a source inventory with selected historical coverage, not a complete annual series for every BC municipality. Missing years are unknown, not zero.',
      'Office survey figures, scheduled annual rates and payments to named officials have distinct definitions. No combined pay total, inflation adjustment, interpolation or automatic growth comparison is calculated.',
      'Council records are separate from employee disclosures. Existing salary files and name-link groups are not rebuilt or merged by this companion.',
      'Some modern Vancouver officials already appear in retained compiled editions. The official calendar-year source remains separate; do not add the two source editions together.',
      `Vancouver named-payment coverage includes ${yearRanges(paymentYears)}. Gaps within that span: ${yearRanges(paymentGaps) || 'none'}. The 1996 table remains held for source errors; years before 1994 are not covered. Annual-rate coverage does not fill payment gaps.`,
      'Some older schedules publish independently rounded whole-dollar cells. The receipt distinguishes exact column totals from documented differences within the reported-precision bound; original values are never adjusted to force agreement.',
      'Council-term groups and role changes can produce more than one payment row for a person in a year. These remain source rows, not a count of distinct people.',
      'A current municipal roster is a discovery aid and does not establish that every municipality existed in each historical year.'
    ],
    municipalities: roster.map((entry) => ({ municipality: entry.municipality, employerSlug: entry.employerSlug, website: entry.website, officeYears: sortedYears(data.observations.filter((row) => row.employerSlug === entry.employerSlug).map((row) => row.year)), paymentYears: sortedYears(data.payments.filter((row) => row.employerSlug === entry.employerSlug).map((row) => row.year)) }))
  }
  validateDataset(data)
  const output = JSON.stringify(data) + '\n'
  const outputs = { 'public/salaries/council-pay.json': output, 'public/salaries/council-pay.csv': datasetCsv(data), [`${researchPath}/coverage.json`]: JSON.stringify(data.coverage, null, 2) + '\n' }
  const validation = {
    version: 1, asOf: data.asOf, scope: 'Council-pay companion only; existing salary and name-link exports are untouched.',
    counts: { sources: data.sources.length, officeObservations: data.observations.length, namedPayments: data.payments.length, columnControls: controls.length, exactColumnControls: controls.filter((entry) => entry.status === 'exact').length, roundingQualifiedControls: controls.filter((entry) => entry.status === 'within-reported-rounding').length, surveyValueChecks },
    inputs: [...inputs.filter(({ value }) => value.sources || value.tables || value.comparisons || value.blocks || value.protectedOfficeIds).map(({ file }) => `${researchPath}/${file}`), 'research/salaries/municipal-audit/roster.json', compiledPath, salaryYearsPath].map((path) => ({ path, sha256: createHash('sha256').update(readFileSync(join(repoRoot, path))).digest('hex') })),
    controls, precisionEvidence, preservation,
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
  console.log(`${check ? 'Verified' : 'Built'} council pay: ${validation.counts.officeObservations} office observations; ${validation.counts.namedPayments} named payments; ${validation.counts.exactColumnControls} exact column controls and ${validation.counts.roundingQualifiedControls} documented rounding differences.`)
}
