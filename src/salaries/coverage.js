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
  'elected-officials': 'Mayor and council remuneration',
  'aggregate-only': 'Aggregate payroll only; no individual records',
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
    periodStart: source.periodStart ?? null, periodEnd: source.periodEnd ?? null, periodType: source.periodType ?? 'unverified',
    threshold: source.threshold ?? null, thresholdComparison: source.thresholdComparison ?? null, duplicateRows: 0, notes: []
  }
}

export const expenseLabel = (sourceId, sources = {}) => sources[sourceId]?.travelSource ? 'Travel expenses' : 'Expenses'

/** Do not change an inclusive threshold into a strict one, or infer an unstated comparison. */
export const thresholdLabel = (coverage) => {
  if (coverage?.threshold == null) return null
  const amount = `$${Number(coverage.threshold).toLocaleString('en-CA')}`
  if (coverage.thresholdComparison === 'reported-conflict') return `threshold ${amount} (source wording differs)`
  return coverage.thresholdComparison === '>=' ? `at least ${amount}` : coverage.thresholdComparison === '>' ? `over ${amount}` : `threshold ${amount}`
}

/** An issuer report awaiting review is a lead, not an accepted source for the published rows. */
export const coverageStatus = (coverage, sources = {}) => {
  if (coverage?.status === 'not-applicable') return { kind: 'missing', label: 'Different reporting-period type' }
  if (coverage?.status === 'aggregate-only') return { kind: 'primary', label: 'Verified aggregate disclosure' }
  if (coverage?.status === 'excluded') return { kind: 'held', label: 'Held for source review' }
  if (['source-found', 'located', 'awaiting-extraction'].includes(coverage?.status)) return { kind: 'found', label: 'Source found · records not yet imported' }
  if (coverage?.status !== 'available') return { kind: 'missing', label: 'No records imported' }
  const ids = coverage.sourceIds ?? []
  const primary = ids.length > 0 && ids.every((id) => sources[id]?.url && sources[id]?.sourceKind !== 'compiled' && sources[id]?.scope !== 'compiled-unverified')
  return primary
    ? { kind: 'primary', label: 'Employer-issued sources' }
    : { kind: 'compiled', label: 'Compiled records · source review pending' }
}

/** Narrow a mixed disclosure to its source category without attributing employee thresholds to council. */
export const categoryCoverage = (coverage, category, sources = {}, rows) => {
  if (category === 'all') return coverage
  const ids = (coverage?.sourceIds ?? []).filter((id) => sources[id]?.scope === category)
  const details = ids.map((id) => sources[id])
  const common = (key) => details.length && details.every((source) => source[key] === details[0][key]) ? details[0][key] ?? null : null
  return { ...coverage, scope: category, sourceIds: ids, periodStart: common('periodStart'), periodEnd: common('periodEnd'),
    periodType: common('periodType'), threshold: common('threshold'), thresholdComparison: common('thresholdComparison'),
    duplicateRows: rows ? rows.length - new Set(rows.map((row) => JSON.stringify(row.slice(0, 4)))).size : null,
    notes: [...new Set(details.flatMap((source) => source.notes ?? []))] }
}

/** Keep full calendar labels even in narrow charts, so 2020 cannot be mistaken for fiscal 20/21. */
export const shortYearLabel = (label) => /^\d{4}$/.test(label) ? label : label.slice(2)

export const reportingYearLabel = (label) => /^\d{4}$/.test(label) ? `${label} (calendar year)` : label

/** A calendar-only employer should not acquire a false gap at every fiscal label in the catalog. */
export const relevantYearIndexes = (years, coverage = [], counts = []) => {
  const kind = (label) => /^\d{4}$/.test(label) ? 'calendar' : 'fiscal'
  const types = new Set(coverage.map((entry) => entry?.periodType).filter((type) => ['calendar', 'fiscal'].includes(type)))
  if (!types.size) years.forEach((label, at) => { if (counts[at]) types.add(kind(label)) })
  return years.map((_, at) => at).filter((at) => !types.size || types.has(kind(years[at])) || counts[at] > 0 || ['aggregate-only', 'source-found', 'excluded'].includes(coverage[at]?.status))
}

export const samePeriodKinds = (years, observedIndexes) => {
  const calendar = (label) => /^\d{4}$/.test(label)
  const types = new Set(observedIndexes.map((at) => calendar(years[at])))
  return years.map((_, at) => at).filter((at) => types.has(calendar(years[at])))
}

export const yearAvailability = (coverage, count) => {
  if (coverage?.status === 'not-applicable') return 'different reporting-period type'
  if (coverage?.status === 'aggregate-only') return 'aggregate payroll only; no named records'
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
  const entries = employers.map((slug) => coverage?.[slug]?.[year]).filter((entry) => entry?.status !== 'not-applicable')
  if (!entries.length) return 'The associated employers use a different reporting-period type. Compare their corresponding calendar or fiscal disclosures.'
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
  const entries = employers.map((slug) => coverage?.[slug]?.[year]).filter((entry) => entry?.status !== 'not-applicable')
  if (!entries.length) return 'different-period'
  if (entries.length && entries.every((entry) => !entry || entry.status !== 'available')) return 'no-coverage'
  if (entries.some((entry) => entry?.scope === 'executive-only')) return 'executive-only'
  if (entries.some((entry) => !entry || entry.status !== 'available')) return 'partial'
  return 'not-found'
}

export const GAP_LABELS = {
  'different-period': 'Different reporting-period type',
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
