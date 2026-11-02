import reviewed from '../../research/salaries/record-annotations.json' with { type: 'json' }

export const RECORD_ANNOTATIONS = reviewed
export const recordAnnotation = (name, position, pay, expenses, employer, period, sourceId, pdfPage) => reviewed.annotations.find(({ record: r }) =>
  r.pay === pay && r.sourceId === sourceId && r.employer === employer && r.period === period && r.name === name
  && r.position === position && r.expenses === expenses && r.pdfPage === (pdfPage ?? null)) ?? null

export const decodedAnnotation = (row) => recordAnnotation(row.name, row.position, row.pay, row.expenses, row.slug, row.year, row.sourceId, row.page)
export const personAnnotation = (row, index) => recordAnnotation(...row.slice(0, 4), index.employers[row[4]][3], index.years[row[5]], row[6], row[7])
export const employerAnnotation = (row, employer, years) => recordAnnotation(...row.slice(0, 4), employer, years[row[4]], row[5], row[6])
export const governmentAnnotation = (row, employer, period) => recordAnnotation(...row.slice(0, 4), employer, period, row[4], row[5])
export const currencyOf = (annotation, source) => annotation?.currency ?? source?.currency ?? 'CAD'
export const decodedCurrency = (row, sources) => currencyOf(decodedAnnotation(row), sources?.[row.sourceId])
export const personCurrency = (row, index) => currencyOf(personAnnotation(row, index), index.sources?.[row[6]])
export const employerCurrency = (row, employer, years, sources) => currencyOf(employerAnnotation(row, employer, years), sources?.[row[5]])
export const isCadPerson = (row, index) => personCurrency(row, index) === 'CAD'
export const isCadEmployer = (row, employer, years, sources) => employerCurrency(row, employer, years, sources) === 'CAD'

/** An annotation is stale if even one selector field changes or acquires a duplicate observation. */
export const validateRecordAnnotations = (rows, sources, annotations = reviewed) => {
  if (annotations.schemaVersion !== 1 || !Array.isArray(annotations.annotations)) throw new Error('Invalid record annotations')
  const ids = new Set()
  for (const entry of annotations.annotations) {
    if (ids.has(entry.id)) throw new Error('Duplicate record annotation')
    ids.add(entry.id)
    if (!['CAD', 'USD'].includes(entry.currency) || !entry.evidence?.length || !entry.evidence.every((e) => /^https:\/\//.test(e.url) && /^[a-f0-9]{64}$/.test(e.pdfSha256) && Number.isInteger(e.pdfPage))) throw new Error('Invalid reviewed currency evidence')
    const r = entry.record
    const matches = rows.filter((row) => row.name === r.name && row.position === r.position && row.pay === r.pay
      && row.expenses === r.expenses && row.slug === r.employer && row.year === r.period
      && row.sourceId === r.sourceId && (row.page ?? null) === r.pdfPage)
    if (matches.length !== 1 || !sources[matches[0].sourceId]) throw new Error(`Reviewed currency observation changed: ${entry.id}`)
  }
  return annotations
}
