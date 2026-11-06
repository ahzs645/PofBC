// Compare a published, filtered employer directory without interpreting edition
// labels as fiscal dates or equal aggregate statistics as independent evidence.
import { resolveEmployer } from './sunshine-coverage.mjs'

const fail = (message) => { throw new Error(`OpenCompensation snapshot: ${message}`) }
const number = (value) => typeof value === 'number' && Number.isFinite(value)

export function candidatePeriodLabels(label) {
  if (/^\d{4}$/.test(label)) return [label]
  const match = /^(\d{4})[-/](\d{2}|\d{4})$/.exec(label)
  if (!match) fail(`unrecognized reporting label ${JSON.stringify(label)}`)
  const first = Number(match[1])
  const last = match[2].length === 4 ? Number(match[2]) : Math.floor(first / 100) * 100 + Number(match[2]) + (Number(match[2]) < first % 100 ? 100 : 0)
  if (last !== first + 1) fail(`nonconsecutive reporting label ${JSON.stringify(label)}`)
  // Candidate calendar years are included because the compilation's edition can
  // contain calendar-year employer reports. None of these is an asserted match.
  return [`${first}/${String(last).slice(-2)}`, String(first), String(last)]
}

export function validateOpenCompensationSnapshot(input) {
  if (input?.version !== 1 || !Array.isArray(input.employers)) fail('expected version 1 and an employers array')
  const source = input.source
  if (!source?.url || !Number.isFinite(Date.parse(source.retrievedAt))) fail('source URL and retrieval date are required')
  if (!Number.isSafeInteger(source.reportedEntryCount) || source.reportedEntryCount !== input.employers.length) fail('captured rows do not reconcile to the stated filtered directory count')
  if (source.minimumPositiveRecords !== 15 || source.latestPerPublishedName !== true) fail('directory selection rules require review')
  const names = new Set()
  for (const row of input.employers) {
    if (typeof row.name !== 'string' || !row.name.trim() || names.has(row.name)) fail('empty or repeated published employer name')
    let url
    try { url = new URL(row.url) } catch { fail(`${row.name}: missing employer-page URL`) }
    if (url.protocol !== 'https:' || url.hostname !== 'www.opencompensation.org' || url.username || url.password) fail(`${row.name}: invalid source URL`)
    if (row.urlScope === 'directory' && url.href !== source.url) fail(`${row.name}: directory provenance must link to the observed directory`)
    names.add(row.name)
    candidatePeriodLabels(row.periodLabel)
    if (!Number.isSafeInteger(row.recordCount) || row.recordCount < source.minimumPositiveRecords) fail(`${row.name}: invalid positive-record count`)
    if (![row.averageCompensation, row.highestCompensation].every(number) || row.averageCompensation <= 0 || row.highestCompensation < row.averageCompensation) fail(`${row.name}: invalid compensation summary`)
  }
  return input
}

/** Source array layout: name, position, remuneration, expenses, period index. */
export function aggregateSignatures(rows) {
  const summarize = (amounts, positiveOnly = true) => {
    const selected = positiveOnly ? amounts.filter(value => value > 0) : amounts
    if (!selected.length) return { recordCount: 0, averageRounded: null, highestRounded: null }
    const totalCents = selected.reduce((sum, value) => sum + Math.round(value * 100), 0)
    return { recordCount: selected.length, averageRounded: Math.round(totalCents / 100 / selected.length), highestRounded: Math.round(Math.max(...selected)) }
  }
  const unknownExpenses = rows.filter(row => !number(row[3])).length
  return { rows: rows.length, unknownExpenses,
    remuneration: summarize(rows.map(row => row[2])),
    remunerationPlusKnownExpenses: summarize(rows.map(row => row[2] + (number(row[3]) ? row[3] : 0))),
    remunerationPlusKnownExpensesForPositiveRemuneration: summarize(rows.filter(row => row[2] > 0).map(row => row[2] + (number(row[3]) ? row[3] : 0)), false),
    expenseTreatment: unknownExpenses ? 'Only reported numeric expenses are added; missing expenses remain unknown. This is an arithmetic diagnostic, not a complete compensation measure.' : 'All expense cells in this input are numeric; remuneration and expenses remain separate source fields.' }
}

export function signatureMatches(reference, signatures) {
  return ['remuneration', 'remunerationPlusKnownExpenses', 'remunerationPlusKnownExpensesForPositiveRemuneration'].filter(key => {
    const value = signatures[key]
    return value?.recordCount === reference.recordCount && value.averageRounded === reference.averageCompensation && value.highestRounded === reference.highestCompensation
  })
}

export function compareOpenCompensation(snapshot, repository, { aliases = [], publishedMetrics = new Map(), baselineMetrics = new Map() } = {}) {
  validateOpenCompensationSnapshot(snapshot)
  const bySlug = new Map(repository.employers.map(employer => [employer.slug, employer]))
  const employers = snapshot.employers.map(reference => {
    const match = resolveEmployer(reference, { employers: repository.employers, aliases })
    const employer = bySlug.get(match.slug)
    const labels = candidatePeriodLabels(reference.periodLabel)
    const candidates = employer?.periods.filter(period => period.rows > 0 && labels.includes(period.yearLabel)).map(period => ({
      yearLabel: period.yearLabel, candidateBasis: period.yearLabel === labels[0] ? 'normalized-edition-label-only' : 'possible-calendar-report-within-edition-label',
      rows: period.rows, officialRows: period.officialRows, compiledRows: period.compiledRows,
      cohorts: period.cohorts.map(cohort => {
        const signatures = publishedMetrics.get(`${employer.slug}|${period.yearLabel}|${cohort.sourceId}`)
        return { sourceId: cohort.sourceId, sourceKind: cohort.sourceKind, scope: cohort.scope, rows: cohort.rows,
          periodType: cohort.periodType, periodStart: cohort.periodStart, periodEnd: cohort.periodEnd,
          threshold: cohort.threshold, thresholdComparison: cohort.thresholdComparison, url: cohort.url,
          hasPublicWarning: Boolean(cohort.publicWarning), partialDisclosure: cohort.partialDisclosure,
          signatures: signatures ?? null, matchingAggregateDefinitions: signatures ? signatureMatches(reference, signatures) : [] }
      })
    })) ?? []
    const baseline = baselineMetrics.get(`${match.slug}|${labels[0]}`)
    return { reference, match,
      status: !employer ? `${match.status}-employer` : !candidates.length ? 'no-candidate-period' : 'period-and-measure-review',
      referencePeriodVerified: false, recordLevelParityChecked: false, countDifference: null,
      repositoryRowsAllPeriods: employer?.rows ?? null,
      candidates,
      originalCompilation: baseline ? { editionLabel: labels[0], signatures: baseline, matchingAggregateDefinitions: signatureMatches(reference, baseline),
        warning: 'Historical compiled input, including subsequently replaced or held records. An aggregate match is not a publication recommendation or proof of common provenance.' } : null }
  })
  const matched = employers.filter(row => row.match.status === 'matched')
  const grouped = new Map()
  for (const row of matched) {
    if (!grouped.has(row.match.slug)) grouped.set(row.match.slug, [])
    grouped.get(row.match.slug).push(row.reference.name)
  }
  const mapped = new Set(grouped.keys())
  return { version: 1, status: 'filtered-directory-compared-periods-unverified', source: snapshot.source,
    datasetSummary: snapshot.datasetSummary ?? null,
    summary: { referencePublishedNames: employers.length, matchedPublishedNames: matched.length, uniqueMappedRepositoryEmployers: mapped.size,
      unmatchedPublishedNames: employers.filter(row => row.match.status === 'unmatched').length,
      ambiguousPublishedNames: employers.filter(row => row.match.status === 'ambiguous').length,
      namesWithCandidatePeriods: employers.filter(row => row.candidates.length).length,
      namesWithOriginalCompilationAggregateMatch: employers.filter(row => row.originalCompilation?.matchingAggregateDefinitions.length).length,
      namesMatchingCompilationOnlyWhenExpensesAdded: employers.filter(row => {
        const definitions = row.originalCompilation?.matchingAggregateDefinitions ?? []
        return definitions.length > 0 && !definitions.includes('remuneration')
      }).length,
      namesMatchingOnlyWithPositiveRemunerationFilter: employers.filter(row => {
        const definitions = row.originalCompilation?.matchingAggregateDefinitions ?? []
        return definitions.includes('remunerationPlusKnownExpensesForPositiveRemuneration') && !definitions.includes('remunerationPlusKnownExpenses') && !definitions.includes('remuneration')
      }).length,
      repository: repository.totals, workforceCompletenessEstablished: false, recordLevelParityChecked: false, importedSalaryRecords: 0 },
    multiplePublishedNames: [...grouped].filter(([, names]) => names.length > 1).map(([repositorySlug, names]) => ({ repositorySlug, publishedNames: names })),
    repositoryEmployersOutsideFilteredDirectory: repository.employers.filter(row => !mapped.has(row.slug)).map(row => ({ slug: row.slug, name: row.name, rows: row.rows })),
    limitations: [
      'The full captured table is a filtered directory: at least 15 positive compensation records in the latest period for each published employer name. It is not the complete employer roster, annual history or workforce.',
      'Published names can be historical aliases. Mapping to repository employer IDs does not independently establish legal-entity equivalence.',
      'Hyphenated edition labels are normalized only to find candidate reports. Calendar years, fiscal dates and compilation labels are not interchangeable.',
      'Source cohorts remain separate. Official schedules and retained compiled copies can overlap; their combined row count is not an employee count.',
      'Compensation averages and maxima are tested against remuneration and remuneration plus known expenses. A matching count and rounded mean/maximum is an aggregate arithmetic signature, not row equality or independent validation.',
      'A separate diagnostic selects positive-remuneration rows before adding known expenses. This can differ from selecting all rows with a positive combined amount; source selection rules are not inferred from a matching signature.',
      'Missing expense cells remain unknown, even when known numeric expenses reproduce a displayed aggregate.',
      'The immutable compilation is historical evidence only. Previously rejected, replaced or misdated records are not restored.',
      'No salary records are imported, removed, relabelled or merged by this comparison.'
    ], employers }
}
