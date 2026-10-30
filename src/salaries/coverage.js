// Missing imported records are a statement about coverage, not about someone's employment.

export const coverageAt = (entry, year) => entry?.coverage?.[year] ?? {
  status: entry?.counts?.[year] ? 'available' : (entry?.repeated?.includes(entry?.years?.[year]) ? 'excluded' : 'missing'),
  scope: 'compiled-unverified',
  sourceIds: [],
  notes: []
}

export const scopeLabel = (scope) => ({
  'employee-remuneration': 'Employee remuneration disclosure',
  'named-employees-over-threshold': 'Employee remuneration disclosure above the reporting threshold',
  'executive-only': 'Executive compensation only',
  'deputy-ministers': 'Deputy minister remuneration',
  'deputy-minister-remuneration': 'Deputy minister remuneration',
  'oic-appointees': 'Order in Council appointee remuneration',
  'appointee-remuneration': 'Order in Council appointee remuneration',
  'mixed-disclosure': 'Combined disclosure categories; individual sources identify their scope',
  'compiled-unverified': 'Compiled records; disclosure scope not yet verified'
}[scope] ?? 'Disclosure scope not yet verified')

/** A row's cited document narrows an employer-year that may combine several disclosure categories. */
export const rowCoverage = (coverage, sourceId, sources = {}) => {
  const source = sources[sourceId]
  if (!source) return coverage
  return {
    ...coverage, sourceIds: [sourceId], scope: source.scope === 'compiled-unverified' ? (coverage?.scope ?? source.scope) : (source.scope ?? coverage?.scope),
    periodStart: source.periodStart ?? null, periodEnd: source.periodEnd ?? null,
    threshold: source.threshold ?? null, thresholdComparison: source.thresholdComparison ?? null, duplicateRows: 0, notes: []
  }
}

export const expenseLabel = (sourceId, sources = {}) => sources[sourceId]?.travelSource ? 'Travel expenses' : 'Expenses'

/** Do not change an inclusive threshold into a strict one, or infer an unstated comparison. */
export const thresholdLabel = (coverage) => {
  if (coverage?.threshold == null) return null
  const amount = `$${Number(coverage.threshold).toLocaleString('en-CA')}`
  return coverage.thresholdComparison === '>=' ? `at least ${amount}` : coverage.thresholdComparison === '>' ? `over ${amount}` : `threshold ${amount}`
}

/** An issuer report awaiting review is a lead, not an accepted source for the published rows. */
export const coverageStatus = (coverage, sources = {}) => {
  if (coverage?.status === 'excluded') return { kind: 'held', label: 'Held for source review' }
  if (['source-found', 'located', 'awaiting-extraction'].includes(coverage?.status)) return { kind: 'found', label: 'Source found · records not yet imported' }
  if (coverage?.status !== 'available') return { kind: 'missing', label: 'No records imported' }
  const ids = coverage.sourceIds ?? []
  const primary = ids.length > 0 && ids.every((id) => sources[id]?.url && sources[id]?.scope !== 'compiled-unverified')
  return primary
    ? { kind: 'primary', label: 'Employer-issued sources' }
    : { kind: 'compiled', label: 'Compiled records · source review pending' }
}

export const yearAvailability = (coverage, count) => {
  if (count > 0) return `${count.toLocaleString('en-CA')} records`
  if (coverage?.status === 'excluded') return 'held for source review'
  if (['source-found', 'located', 'awaiting-extraction'].includes(coverage?.status)) return 'source found; records not yet imported'
  return 'no records imported'
}

/** Add a physical PDF page only when supplied by the parser; never infer it from row order. */
export const sourceHref = (source, pdfPage) => {
  if (!source?.url || !/^https?:\/\//i.test(source.url)) return null
  if (!Number.isInteger(pdfPage) || pdfPage < 1) return source.url
  try {
    const url = new URL(source.url)
    if (!/\.pdf$/i.test(url.pathname)) return source.url
    url.hash = `page=${pdfPage}`
    return url.href
  } catch { return null }
}

export const disclosurePeriod = (coverage, sources = {}) => {
  if (coverage?.periodStart && coverage?.periodEnd) return [coverage.periodStart, coverage.periodEnd]
  const periods = (coverage?.sourceIds ?? []).map((id) => sources[id])
    .filter((source) => source?.periodStart && source?.periodEnd)
    .map(({ periodStart, periodEnd }) => `${periodStart}|${periodEnd}`)
  const unique = [...new Set(periods)]
  return unique.length === 1 ? unique[0].split('|') : null
}

/** Report whether the employers associated with this disclosed name have usable records. */
export const missingYearMessage = (coverage, employers, year) => {
  if (!coverage) return 'No matching name was found in the imported records. Employer coverage has not been established for this period; absence does not establish whether the person was employed or paid.'
  const entries = employers.map((slug) => coverage?.[slug]?.[year])
  if (entries.length && entries.every((entry) => !entry || entry.status !== 'available')) {
    return 'No usable records are available here for the associated employers in this period. This coverage gap does not establish whether the person was employed or paid.'
  }
  if (entries.some((entry) => entry?.scope === 'executive-only')) {
    return 'No matching name was found in the imported records. Some associated employer records cover executives only; absence does not establish whether the person was employed or paid.'
  }
  if (entries.some((entry) => !entry || entry.status !== 'available')) {
    return 'No matching name was found in the imported records, and some associated employers have a coverage gap. Absence does not establish whether the person was employed or paid.'
  }
  return 'No matching name was found in the imported records. Disclosure thresholds, withheld names and spelling differences can leave a person absent; this does not establish whether they were employed or paid.'
}

/** Count only employers with records in the selected collection year and sector. */
export const filterEmployers = (employers, sector = 'all', year = 'all') => employers.filter((entry) =>
  (sector === 'all' || entry.sector === sector) && (year === 'all' || entry.counts[Number(year)] > 0))

/**
 * Why a disclosed name has no record in a year, as a short reason a run of such years can share:
 * the associated employers have no records imported then ('no-coverage'), disclosed only executives
 * ('executive-only'), are covered only in part ('partial'), or are covered and the name is not in it
 * ('not-found'). The same cases missingYearMessage explains at length.
 */
export const gapReason = (coverage, employers, year) => {
  if (!coverage) return 'not-found'
  const entries = employers.map((slug) => coverage?.[slug]?.[year])
  if (entries.length && entries.every((entry) => !entry || entry.status !== 'available')) return 'no-coverage'
  if (entries.some((entry) => entry?.scope === 'executive-only')) return 'executive-only'
  if (entries.some((entry) => !entry || entry.status !== 'available')) return 'partial'
  return 'not-found'
}

export const GAP_LABELS = {
  'no-coverage': 'No records imported for this employer',
  'executive-only': 'Only executives disclosed',
  partial: 'Not found; some employers not covered',
  'not-found': 'Not in that year’s disclosure'
}

/** Consecutive years sharing a reason, as runs: [{ from, to, reason }], from and to inclusive. */
export const gapRuns = (years, reasonOf) => {
  const runs = []
  for (const year of years) {
    const reason = reasonOf(year)
    const last = runs.at(-1)
    if (last && last.to === year - 1 && last.reason === reason) last.to = year
    else runs.push({ from: year, to: year, reason })
  }
  return runs
}
