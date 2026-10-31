// Input validation and diagnostics shared by the salary build and its tests.
// Repeated names/pay flag a source for review; they do not establish that a year is false.
import { createHash } from 'node:crypto'

export const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex')
export const cents = (amount) => Math.round(amount * 100)
export const sumMoney = (values) => values.reduce((sum, value) => sum + cents(value), 0) / 100
export const median = (values) => {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[middle] : Math.round((sorted[middle - 1] + sorted[middle]) * 50) / 100
}

export function * csvRows (text) {
  let row = []; let field = ''; let quoted = false
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
  if (quoted) throw new Error('Unclosed quoted CSV field')
  if (field || row.length) { row.push(field); yield row }
}

export const money = (value) => {
  const text = String(value ?? '').trim()
  if (!text || /^(?:NA|N\/A|null|—|-)$/i.test(text)) return null
  const cleaned = text.replace(/[$,\s]/g, '')
  if (!/^-?\d+(?:\.\d{1,2})?$/.test(cleaned)) throw new Error(`Invalid money: ${text}`)
  const result = Number(cleaned)
  if (!Number.isSafeInteger(cents(result))) throw new Error(`Unsafe money value: ${text}`)
  return result
}

export const yearSlug = (label) => {
  if (/^\d{4}$/.test(label)) return label
  const match = /^(\d{4})\/(\d{2})$/.exec(label)
  if (!match || String(Number(match[1]) + 1).slice(-2) !== match[2]) throw new Error(`Invalid disclosure year ${label}`)
  return label.replace('/', '-')
}

/** The label describes the source period; calendar disclosures are never filed under fiscal labels. */
export const reportingPeriodType = (label) => {
  yearSlug(label)
  return /^\d{4}$/.test(label) ? 'calendar' : 'fiscal'
}

/**
 * A reviewed employee-only replacement may leave elected officials in a compiled partition.
 * Pin the exact selected rows, and require the replacement source to have reached this build.
 * This prevents a future source change from silently deleting an unrelated cohort.
 */
export const applyCompiledReplacements = (baseline, official, sources, rules = []) => {
  const removed = new Set()
  const classified = new Map()
  const corrections = []
  for (const rule of rules) {
    const { employerSlug, compiledYear, replacementYear, sourceIds, retainPositions = [] } = rule
    yearSlug(compiledYear); yearSlug(replacementYear)
    if (!rule.reason?.trim() || !sourceIds?.length || !Array.isArray(retainPositions)) throw new Error('Incomplete compiled replacement decision')
    for (const id of sourceIds) {
      if (!sources[id] || !official.some((row) => row.slug === employerSlug && row.year === replacementYear && row.sourceId === id)) {
        throw new Error(`${employerSlug}|${compiledYear}: replacement source ${id} was not imported`)
      }
      // A reviewed comparison must not survive a later source update under the
      // same ID. New municipal rules pin the exact accepted data bytes as well
      // as the compiled cohort selected for removal.
      if (rule.sourceDataSha256 && (!/^[a-f0-9]{64}$/.test(rule.sourceDataSha256[id] ?? '') || sources[id].dataSha256 !== rule.sourceDataSha256[id])) {
        throw new Error(`${employerSlug}|${compiledYear}: official replacement source fingerprint changed for ${id}`)
      }
    }
    if (!sourceIds.some((id) => ['employee-remuneration', 'named-employees-over-threshold'].includes(sources[id].scope))) {
      throw new Error(`${employerSlug}|${compiledYear}: partial disclosure cannot replace a compiled employee cohort across periods`)
    }
    const partition = baseline.filter((row) => row.slug === employerSlug && row.year === compiledYear)
    const selected = partition.filter((row) => !retainPositions.includes(row.position))
    const retained = partition.filter((row) => retainPositions.includes(row.position))
    const digest = sha256(JSON.stringify(selected.map((row) => [row.name, row.position, row.pay, row.expenses])))
    if (selected.length !== rule.expectedRows || retained.length !== rule.expectedRetainedRows || digest !== rule.selectedRowsSha256) {
      throw new Error(`${employerSlug}|${compiledYear}: compiled replacement evidence no longer matches`)
    }
    for (const row of selected) {
      if (removed.has(row)) throw new Error(`${employerSlug}|${compiledYear}: overlapping compiled replacement decisions`)
      removed.add(row)
    }
    if (retained.length) {
      if (!rule.retainedSource?.id || !rule.retainedSource?.scope || sources[rule.retainedSource.id]) throw new Error('Missing or duplicate retained cohort source')
      sources[rule.retainedSource.id] = { ...sources[retained[0].sourceId], ...rule.retainedSource,
        url: null, sourceKind: 'compiled', year: compiledYear, periodType: 'unverified', periodStart: null, periodEnd: null }
      for (const row of retained) classified.set(row, rule.retainedSource.id)
    }
    corrections.push({ employer: employerSlug, year: compiledYear, correctedYear: replacementYear, rows: selected.length,
      retainedRows: retained.length, kind: 'wrong-reporting-year', reason: rule.reason,
      evidence: rule.evidence, sourceIds, status: 'replaced-from-official-source' })
  }
  return { rows: baseline.filter((row) => !removed.has(row)).map((row) => classified.has(row) ? { ...row, sourceId: classified.get(row) } : row), corrections }
}

/** A newly recovered cohort can invalidate an earlier name-only travel join. */
export const applyTravelJoinCorrections = (rows, sources, decisions = []) => {
  const replacements = new Map()
  for (const decision of decisions) {
    const { employeeSourceId, employerSlug, year, name, pay, previousExpenses, replacementExpenses, relatedOICSourceId, relatedOICName, relatedOICRemuneration } = decision
    if (!decision.reason?.trim() || replacementExpenses !== null || !sources[employeeSourceId]?.travelSource) throw new Error('Invalid travel-join correction')
    const employee = rows.filter((row) => row.sourceId === employeeSourceId && row.slug === employerSlug && row.year === year && row.name === name && row.pay === pay && row.expenses === previousExpenses)
    const appointee = rows.filter((row) => row.sourceId === relatedOICSourceId && row.slug === employerSlug && row.year === year && row.name === relatedOICName && row.pay === relatedOICRemuneration)
    if (employee.length !== 1 || appointee.length !== 1 || replacements.has(employee[0])) throw new Error('Travel-join correction evidence no longer matches')
    replacements.set(employee[0], replacementExpenses)
  }
  return { rows: rows.map((row) => replacements.has(row) ? { ...row, expenses: replacements.get(row) } : row), corrections: decisions }
}

export const exactRowKey = (row) => JSON.stringify([row.name, row.position, row.pay, row.expenses])
const repeatedKey = (row) => JSON.stringify([row.name?.normalize('NFKC').toLowerCase().trim(), cents(row.pay)])

export const duplicateStats = (rows) => {
  const counts = new Map()
  for (const row of rows) {
    const key = exactRowKey(row)
    counts.set(key, (counts.get(key) ?? 0) + 1)
  }
  return { duplicateRows: rows.length - counts.size, duplicateGroups: [...counts.values()].filter((count) => count > 1).length }
}

/** Compare every earlier populated year, retaining row multiplicity and ignoring anonymous rows. */
export const repeatedCandidates = (rows, minimum = 20, fraction = 0.8) => {
  const employers = new Map()
  for (const row of rows) {
    if (!row.name) continue
    if (!employers.has(row.slug)) employers.set(row.slug, new Map())
    const years = employers.get(row.slug)
    if (!years.has(row.year)) years.set(row.year, [])
    years.get(row.year).push(row)
  }
  const result = []
  for (const [employer, byYear] of employers) {
    const years = [...byYear.keys()].sort()
    const maps = new Map(years.map((year) => {
      const counts = new Map()
      for (const row of byYear.get(year)) { const key = repeatedKey(row); counts.set(key, (counts.get(key) ?? 0) + 1) }
      return [year, counts]
    }))
    for (let at = 1; at < years.length; at += 1) {
      const year = years[at]; const now = byYear.get(year)
      if (now.length < minimum) continue
      for (const previous of years.slice(0, at)) {
        const before = byYear.get(previous)
        if (before.length < minimum) continue
        let same = 0
        for (const [key, count] of maps.get(year)) same += Math.min(count, maps.get(previous).get(key) ?? 0)
        if (same / now.length >= fraction) result.push({ employer, year, repeats: previous, rows: now.length, previousRows: before.length, same, fraction: same / now.length, action: 'review-only' })
      }
    }
  }
  return result
}

/** Validation deliberately runs before any published output is replaced. */
export const validateRow = (row, context) => {
  if (!row.slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(row.slug)) throw new Error(`${context}: invalid employer slug`)
  yearSlug(row.year)
  if (row.name !== null && (typeof row.name !== 'string' || !row.name.trim())) throw new Error(`${context}: invalid name`)
  if (row.position !== null && typeof row.position !== 'string') throw new Error(`${context}: invalid position`)
  for (const key of ['pay', 'expenses']) {
    const amount = row[key]
    if (key === 'expenses' && amount === null) continue
    if (!Number.isFinite(amount) || !Number.isSafeInteger(cents(amount))) throw new Error(`${context}: invalid ${key}`)
    if (Math.abs(cents(amount) / 100 - amount) > 0.000001) throw new Error(`${context}: ${key} has more than two decimals`)
  }
  if (!row.sourceId) throw new Error(`${context}: missing provenance`)
}

/** A small executive/deputy cohort must never silently replace an employee partition. */
export const validateReplacementScopes = (baseline, official, sources, decisions = []) => {
  const previous = new Set(baseline.map((row) => `${row.slug}|${row.year}`))
  const partitions = new Map()
  for (const row of official) {
    const key = `${row.slug}|${row.year}`
    if (!previous.has(key)) continue
    if (!partitions.has(key)) partitions.set(key, new Set())
    partitions.get(key).add(row.sourceId)
  }
  for (const [key, ids] of partitions) {
    if ([...ids].some((id) => ['employee-remuneration', 'named-employees-over-threshold'].includes(sources[id]?.scope))) continue
    const [employer, year] = key.split('|')
    const decision = decisions.find((entry) => entry.kind === 'replace-partition-scope' && entry.employer === employer && entry.year === year)
    if (decision?.reason?.trim() && Array.isArray(decision.sourceIds) && [...ids].every((id) => decision.sourceIds.includes(id))) continue
    throw new Error(`${key}: partial disclosure cannot replace a compiled employee partition without an explicit reviewed scope decision`)
  }
}

// The landing page's view across every employer: each period's highest-paid named records. The
// whole name index is hundreds of slices; this is one small file, and says it is only the top.
export const TOP_PER_PERIOD = 500
/** Person-index rows [name, position, pay, expenses, employer, year, source, page], the top `n` a period. */
export const topRecords = (rows, n = TOP_PER_PERIOD) => {
  const byYear = new Map()
  for (const row of rows) {
    if (!byYear.has(row[5])) byYear.set(row[5], [])
    byYear.get(row[5]).push(row)
  }
  const order = (a, b) => b[2] - a[2] || String(a[0]).localeCompare(String(b[0])) || a[4] - b[4] || String(a[1]).localeCompare(String(b[1])) || String(a[6]).localeCompare(String(b[6]))
  return [...byYear].sort(([a], [b]) => a - b).flatMap(([, list]) => list.sort(order).slice(0, n))
}

/** A title's average in one period across its employers: cells [employer, year, rows, mean, …]. */
export const periodMean = (cells, year) => {
  const chosen = cells.filter((cell) => cell[1] === year)
  const records = chosen.reduce((sum, cell) => sum + cell[2], 0)
  return records ? Math.round(chosen.reduce((sum, cell) => sum + cell[2] * cell[3], 0) / records) : null
}
