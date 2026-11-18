import { pooledGrowth } from './growth.js'

/** Recalculate title cards from the actual employer/period cells in the active filters. */
export const filterTitles = (titles, scopes, employers, years, sector, range) => {
  const visible = []
  for (const title of titles) {
    const series = new Map()
    let rows = 0
    let first = Infinity
    let last = -1
    let latestTotal = 0
    let latestRows = 0
    for (const [employer, year, count, totalCents] of scopes[title.key] ?? []) {
      if (sector !== 'all' && employers[employer].sector !== sector) continue
      if (range && (year < range[0] || year > range[1])) continue
      if (!series.has(employer)) series.set(employer, [])
      series.get(employer).push({ year, count, mean: totalCents / (count * 100) })
      first = Math.min(first, year)
      rows += count
      if (year > last) {
        last = year
        latestTotal = 0
        latestRows = 0
      }
      if (year === last) {
        latestRows += count
        latestTotal += totalCents
      }
    }
    if (rows) visible.push({
      ...title, rows, employers: series.size, first, last,
      mean: Math.round(latestTotal / (100 * latestRows)),
      growth: pooledGrowth([...series], years), raise: null
    })
  }
  return visible
}

/** Pooling medians requires original payments. Use the source's pooled value only for its own group. */
export const titleMedians = (cells, pooled, sector, years) => {
  const groups = new Set(cells.map((cell) => cell.entry.sector))
  const own = sector === 'all' || (groups.size === 1 && groups.has(sector)) ? pooled?.all : pooled?.[sector]
  const available = new Map(own)
  return years.map((_, year) => {
    const matches = cells.filter((cell) => cell.year === year && (sector === 'all' || cell.entry.sector === sector))
    if (matches.length === 1) return matches[0].median
    return matches.length ? available.get(year) ?? null : null
  })
}
