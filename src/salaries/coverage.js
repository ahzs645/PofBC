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
    threshold: source.threshold ?? null, duplicateRows: 0, notes: []
  }
}

export const expenseLabel = (sourceId, sources = {}) => sources[sourceId]?.travelSource ? 'Travel expenses' : 'Expenses'

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
