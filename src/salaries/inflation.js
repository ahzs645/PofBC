// Amounts in another year's dollars, by the B.C. consumer price index. The Financial Information
// Act's $75,000 threshold has not moved since 2002 while prices rose more than half again, so a
// series read in its own nominal dollars mixes pay with inflation. Sources and method:
// research/salaries/cpi/README.md.

/** Statistics Canada Table 18-10-0005-01, British Columbia, All-items, annual average, 2002=100. */
export const BC_CPI = {
  1995: 91.6, 1996: 92.4, 1997: 93.1, 1998: 93.4, 1999: 94.4, 2000: 96.1, 2001: 97.7, 2002: 100.0,
  2003: 102.2, 2004: 104.2, 2005: 106.3, 2006: 108.1, 2007: 110.0, 2008: 112.3, 2009: 112.3,
  2010: 113.8, 2011: 116.5, 2012: 117.8, 2013: 117.7, 2014: 118.9, 2015: 120.2, 2016: 122.4,
  2017: 125.0, 2018: 128.4, 2019: 131.4, 2020: 132.4, 2021: 136.1, 2022: 145.5, 2023: 151.2,
  2024: 155.2, 2025: 158.5
}
const known = Object.keys(BC_CPI).map(Number)
export const CPI_FIRST = Math.min(...known)
export const CPI_LATEST = Math.max(...known)

const annual = (year) => BC_CPI[Math.min(Math.max(year, CPI_FIRST), CPI_LATEST)]

/** The index for a period label: "2024" is the calendar year, "2024/25" a fiscal year. */
export const cpiFor = (label) => {
  const text = String(label ?? '')
  const year = Number(text.slice(0, 4))
  if (!Number.isFinite(year) || year < 1900) return null
  return /^\d{4}\/\d{2}$/.test(text) ? 0.75 * annual(year) + 0.25 * annual(year + 1) : annual(year)
}

/** `value`, paid in period `label`, in the dollars of `base` (the latest published year by default). */
export const inDollarsOf = (value, label, base = String(CPI_LATEST)) => {
  const from = cpiFor(label)
  const to = cpiFor(base)
  if (!Number.isFinite(value) || !from || !to) return null
  return value * (to / from)
}

/** The yearly rate prices rose from one period to another. */
export const inflationRate = (fromLabel, toLabel, span) => {
  const from = cpiFor(fromLabel)
  const to = cpiFor(toLabel)
  return from && to && span > 0 ? (to / from) ** (1 / span) - 1 : null
}
