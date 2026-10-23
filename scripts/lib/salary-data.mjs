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
  const match = /^(\d{4})\/(\d{2})$/.exec(label)
  if (!match || String(Number(match[1]) + 1).slice(-2) !== match[2]) throw new Error(`Invalid disclosure year ${label}`)
  return label.replace('/', '-')
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
