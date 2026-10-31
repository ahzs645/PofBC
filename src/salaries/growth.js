// How pay has moved: for a position, an employer, or a title across employers.
//
// Two measures, because a disclosure's average can move for reasons that are not pay. Records only
// appear above the disclosure threshold, and who holds a title changes from year to year, so an
// average rises when juniors leave the list as surely as when anyone is paid more.
//
// - Average growth: a series' average in its first year with enough records to its last, at least
//   MIN_SPAN years on, as a rate a year. Across employers, each employer's own series is measured and the rates are combined by
//   records, so a title is not said to grow because a better-paying employer started disclosing it.
// - Typical raise: the median yearly change for the same name, under the same title at the same
//   employer, between two disclosures no more than MAX_GAP years apart. A name with two records in
//   one year is left out of that year, since which is whose cannot be told. A shared name is not
//   proof of one person, and a part year (a start, a leave) shows as a jump; the median is used so a
//   few of those do not decide it.

import { personKey } from './people.js'

/** Records needed at each end of a series before its average is compared, and years between them. */
export const MIN_RECORDS = 5
export const MIN_SPAN = 3
/** The longest gap, in years, between two records of one name still read as one raise. */
export const MAX_GAP = 3

/** A period label's first year: "2023/24" → 2023, "2025" → 2025. */
export const yearNumber = (label) => Number(String(label).slice(0, 4))

/** A change from `from` to `to` over `span` years, as a rate a year. */
export const annualRate = (from, to, span) => (from > 0 && to > 0 && span > 0 ? (to / from) ** (1 / span) - 1 : null)

export const medianOf = (values) => {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2
}

/**
 * One series' average growth: `cells` are { year, count, mean } for one employer (and title), `years`
 * the period labels. From its first year with MIN_RECORDS records to its last; null without two.
 */
export const seriesGrowth = (cells, years, min = MIN_RECORDS) => {
  const usable = cells.filter((cell) => cell.count >= min).sort((a, b) => a.year - b.year)
  if (usable.length < 2) return null
  const from = usable[0]
  const to = usable.at(-1)
  const span = yearNumber(years[to.year]) - yearNumber(years[from.year])
  if (span < MIN_SPAN) return null
  const rate = annualRate(from.mean, to.mean, span)
  return rate === null ? null : { from, to, span, rate, weight: Math.min(from.count, to.count) }
}

/** Several employers' series as one rate, each weighed by its smaller end. `series` is [key, cells][]. */
export const pooledGrowth = (series, years, min = MIN_RECORDS) => {
  const parts = series.map(([key, cells]) => ({ key, growth: seriesGrowth(cells, years, min) })).filter((part) => part.growth)
  if (!parts.length) return null
  const weight = parts.reduce((sum, part) => sum + part.growth.weight, 0)
  return {
    rate: parts.reduce((sum, part) => sum + part.growth.rate * part.growth.weight, 0) / weight,
    weight,
    employers: parts.length,
    from: Math.min(...parts.map((part) => part.growth.from.year)),
    to: Math.max(...parts.map((part) => part.growth.to.year)),
    parts
  }
}

/**
 * The raises of names that stayed: `records` are { name, group, pay, year }, where `group` is what a
 * name must share across years to count (an employer and a title, or an employer alone). Returns one
 * { key, name, from, to, rate } for each pair of a name's successive single records.
 */
export const stayerRaises = (records, years) => {
  const names = new Map()
  for (const record of records) {
    if (!record.name) continue
    const key = `${record.group}|${personKey(record.name)}`
    if (!names.has(key)) names.set(key, { name: record.name, years: new Map() })
    const entry = names.get(key)
    if (!entry.years.has(record.year)) entry.years.set(record.year, [])
    entry.years.get(record.year).push(record.pay)
  }
  const raises = []
  for (const [key, entry] of names) {
    const single = [...entry.years].filter(([, pay]) => pay.length === 1).map(([year, [pay]]) => ({ year, pay }))
      .sort((a, b) => yearNumber(years[a.year]) - yearNumber(years[b.year]))
    for (let at = 1; at < single.length; at += 1) {
      const from = single[at - 1]
      const to = single[at]
      const span = yearNumber(years[to.year]) - yearNumber(years[from.year])
      if (span < 1 || span > MAX_GAP) continue
      const rate = annualRate(from.pay, to.pay, span)
      if (rate !== null) raises.push({ key, name: entry.name, from, to, rate })
    }
  }
  return raises
}

/** The median of those raises, how many there were, and how many names they came from. */
export const typicalRaise = (raises) => (raises.length
  ? { rate: medianOf(raises.map((raise) => raise.rate)), pairs: raises.length, people: new Set(raises.map((raise) => raise.key)).size }
  : null)

/** "+3.2% a year", "−0.4% a year", or a dash. */
export const formatRate = (rate, suffix = ' a year') => {
  if (rate === null || rate === undefined || !Number.isFinite(rate)) return '—'
  const percent = rate * 100
  const text = Math.abs(percent).toLocaleString('en-CA', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
  return `${percent > 0.05 ? '+' : percent < -0.05 ? '−' : ''}${text}%${suffix}`
}

/**
 * A year's records in bands of `width` dollars: [{ from, to, count }], the last open-ended at `cap`.
 * Records under the first band's floor (the lowest pay, rounded down) start the scale.
 */
export const payBands = (pay, width = 25000, cap = 300000) => {
  if (!pay.length) return []
  const floor = Math.floor(Math.min(...pay) / width) * width
  const top = Math.min(cap, Math.floor(Math.max(...pay) / width) * width)
  const bands = []
  for (let from = floor; from <= top; from += width) bands.push({ from, to: from >= cap ? null : from + width, count: 0 })
  for (const value of pay) {
    const at = Math.min(bands.length - 1, Math.floor((Math.min(value, cap) - floor) / width))
    bands[Math.max(0, at)].count += 1
  }
  return bands
}

/**
 * Who came onto and went off an employer's list from one disclosure to the next of the same kind
 * (fiscal or calendar): for each year with records, the names new since the one before, the names
 * gone, and those in both. Crossing the threshold is coming onto the list, as surely as joining.
 */
export const listChanges = (rows, years) => {
  const byYear = new Map()
  for (const row of rows) {
    if (!row.name) continue
    if (!byYear.has(row.year)) byYear.set(row.year, new Set())
    byYear.get(row.year).add(personKey(row.name))
  }
  const calendar = (label) => /^\d{4}$/.test(label)
  const ordered = [...byYear.keys()].sort((a, b) => yearNumber(years[a]) - yearNumber(years[b]) || a - b)
  const changes = new Map()
  for (const year of ordered) {
    const before = ordered.filter((other) => calendar(years[other]) === calendar(years[year]) && yearNumber(years[other]) < yearNumber(years[year])).at(-1)
    if (before === undefined) continue
    const now = byYear.get(year)
    const then = byYear.get(before)
    let stayed = 0
    for (const key of now) if (then.has(key)) stayed += 1
    changes.set(year, { before, joined: now.size - stayed, left: then.size - stayed, stayed })
  }
  return changes
}
