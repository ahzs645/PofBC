// Employer comparisons use official annual employee schedules, apart from council, board,
// executive-only and compiled observations. Counts describe published records, not headcount.
import { medianMoney } from './money.js'
import { isCadEmployer } from './recordAnnotations.js'
import { medianOf, stayerRaises } from './growth.js'

export const MIN_EMPLOYER_RECORDS = 10
/** Names needed in both years before their median raise is reported or ranked. */
export const MIN_STAYERS = 10
/** A ranking of raises needs more names, so a few retroactive payments cannot top it. */
export const MIN_RANKED_STAYERS = 50
/**
 * Rankings compare employers whose latest disclosure ends within this many days of the most recent
 * one in the selection, so a 2017/18 schedule is not ranked beside 2025/26 ones.
 */
export const CURRENT_WINDOW_DAYS = 550
const cents = (value) => Math.round(value * 100)
const day = 86400000
const annual = (source) => {
  const start = Date.parse(source.periodStart)
  const end = Date.parse(source.periodEnd)
  const days = (end - start) / day + 1
  return ['calendar', 'fiscal'].includes(source.periodType) && days >= 350 && days <= 371
}
const signature = (source) => JSON.stringify([
  source.periodType, source.periodStart, source.periodEnd, source.threshold,
  source.thresholdComparison, source.scopeDescription ?? null
])

/** Employer export rows: [name, title, pay, expenses, year index, source id, PDF page]. */
export const buildEmployerStats = (rows, { slug, years, sources }) => {
  const periods = new Map()
  for (const row of rows) {
    const source = sources[row[5]]
    if (!source?.sourceKind?.startsWith('official') || source.scope !== 'employee-remuneration'
      || source.completeEmployeeSchedule === false || !annual(source)
      || !Number.isFinite(row[2]) || !isCadEmployer(row, slug, years, sources)) continue
    if (!periods.has(row[4])) periods.set(row[4], [])
    periods.get(row[4]).push(row)
  }
  const kept = new Map()
  const cells = [...periods].sort(([a], [b]) => a - b).flatMap(([year, list]) => {
    const sourceIds = [...new Set(list.map((row) => row[5]))].sort()
    const definitions = sourceIds.map((id) => sources[id])
    // Different employee cohorts or overlapping editions cannot safely be pooled.
    if (new Set(definitions.map(signature)).size !== 1) return []
    const observations = new Map()
    for (const row of list) {
      const key = JSON.stringify(row.slice(0, 4))
      if (observations.has(key) && observations.get(key) !== row[5]) return []
      observations.set(key, row[5])
    }
    const source = definitions[0]
    kept.set(year, list)
    const pay = list.map((row) => row[2]).sort((a, b) => a - b)
    const totalCents = pay.reduce((sum, value) => sum + cents(value), 0)
    const names = list.map((row) => row[0]?.trim().toLocaleLowerCase('en-CA')).filter(Boolean)
    return [{
      year, count: pay.length, named: names.length, uniqueNames: new Set(names).size,
      median: medianMoney(pay), mean: Math.round(totalCents / pay.length) / 100,
      total: totalCents / 100, max: pay.at(-1), above100k: pay.filter((value) => value >= 100000).length,
      periodType: source.periodType, start: source.periodStart, end: source.periodEnd,
      threshold: source.threshold, comparison: source.thresholdComparison,
      scope: source.scopeDescription ?? null, sourceIds,
      qualified: definitions.some((entry) => Boolean(entry.publicWarning))
    }]
  })
  // The typical raise of names on both of two adjacent comparable lists. Unlike the count of records,
  // it does not grow just because pay rises carry more people over a fixed threshold.
  for (const cell of cells) {
    const previous = cells.find((other) => other.periodType === cell.periodType && other.threshold === cell.threshold
      && other.comparison === cell.comparison && priorDate(cell.start) === other.start && priorDate(cell.end) === other.end)
    if (!previous) continue
    const records = [previous, cell].flatMap((each) => kept.get(each.year).map((row) => ({ name: row[0], group: '', pay: row[2], year: row[4] })))
    const raises = stayerRaises(records, years).filter((raise) => raise.from.year === previous.year && raise.to.year === cell.year)
    if (raises.length < MIN_STAYERS) continue
    cell.raise = Math.round(medianOf(raises.map((raise) => raise.rate)) * 1e6) / 1e6
    cell.stayers = raises.length
    cell.raiseFrom = previous.year
  }
  return cells
}

const priorDate = (date) => `${Number(date.slice(0, 4)) - 1}${date.slice(4)}`
const sameRules = (a, b) => a.periodType === b.periodType && a.scope === b.scope
  && Number.isFinite(a.threshold) && a.threshold === b.threshold
  && ['>', '>=', 'greater-than'].includes(a.comparison) && a.comparison === b.comparison
  && priorDate(b.start) === a.start && priorDate(b.end) === a.end
  && !a.qualified && !b.qualified
  && a.named === a.count && b.named === b.count
  && a.uniqueNames === a.count && b.uniqueNames === b.count

/** Latest official employee period within the active range; no gaps or rule changes bridged. */
/* The raise is carried on the latest cell itself, measured against its own previous comparable year. */
export const employerSnapshot = (cells = [], range = null) => {
  const selected = cells.filter((cell) => !range || (cell.year >= range[0] && cell.year <= range[1]))
  const latest = selected.at(-1)
  if (!latest) return null
  const previous = selected.find((cell) => sameRules(cell, latest))
  const measured = previous && previous.count >= MIN_EMPLOYER_RECORDS && latest.count >= MIN_EMPLOYER_RECORDS
  return {
    ...latest,
    from: measured ? previous.year : null,
    growth: measured ? latest.count / previous.count - 1 : null,
    added: measured ? latest.count - previous.count : null,
    previousCount: measured ? previous.count : null,
    raise: latest.raise ?? null,
    stayers: latest.stayers ?? null,
    raiseFrom: latest.raiseFrom ?? null
  }
}

/** The ranking's comparison window: the latest end date among the rows, less CURRENT_WINDOW_DAYS. */
export const currentSince = (rows) => {
  const ends = rows.map(({ stats }) => stats?.end).filter(Boolean).map(Date.parse).filter(Number.isFinite)
  return ends.length ? Math.max(...ends) - CURRENT_WINDOW_DAYS * 86400000 : null
}
export const isCurrent = (stats, since) => since === null || (stats?.end && Date.parse(stats.end) >= since)

/** Missing measures sort last; an employer's all-period record count never ranks its pay. */
export const employerRanking = (rows, metric, since = currentSince(rows)) => rows.filter(({ stats }) => stats
  && stats.count >= MIN_EMPLOYER_RECORDS && Number.isFinite(stats[metric]) && isCurrent(stats, since)
  && (metric !== 'raise' || stats.stayers >= MIN_RANKED_STAYERS))
  .sort((a, b) => b.stats[metric] - a.stats[metric] || a.name.localeCompare(b.name, 'en-CA'))
