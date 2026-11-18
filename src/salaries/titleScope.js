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
  const sourceSector = (cell) => cell.entry.sourceSector ?? cell.entry.sector
  return years.map((_, year) => {
    const period = cells.filter((cell) => cell.year === year)
    const matches = sector === 'all' ? period : period.filter((cell) => cell.entry.sector === sector)
    if (!matches.length) return null
    if (matches.length === 1) return matches[0].median
    if (matches.length === period.length) return new Map(pooled?.all).get(year) ?? null
    // Related organizations can have a different display sector. A published sector median is
    // valid only when it pools exactly the same employer cells as the active filter.
    const source = sourceSector(matches[0])
    if (!matches.every((cell) => sourceSector(cell) === source) ||
        period.filter((cell) => sourceSector(cell) === source).length !== matches.length) return null
    return new Map(pooled?.[source]).get(year) ?? null
  })
}
