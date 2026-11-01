// Compare aggregate source evidence without turning an edition label or matching
// row count into a claim that the underlying people and payment records agree.
import { createHash } from 'node:crypto'
import { resolveEmployer, EMPLOYEE_SCOPES } from './sunshine-coverage.mjs'

const sum = values => values.reduce((total, value) => total + value, 0)
const unique = values => [...new Set(values)].sort()
const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex')
const md = value => String(value ?? '').replaceAll('|', '\\|').replaceAll('\n', ' ')
const fmt = value => Number(value).toLocaleString('en-CA')
const observedYear = value => /^\d{4}$/.test(String(value)) ? Number(value) : null
const labelYears = value => {
  const match = /^(\d{4})(?:\/(\d{2}|\d{4}))?$/.exec(String(value))
  if (!match) return []
  const start = Number(match[1])
  if (!match[2]) return [start]
  const end = match[2].length === 4 ? Number(match[2]) : Math.floor(start / 100) * 100 + Number(match[2]) + (Number(match[2]) < start % 100 ? 100 : 0)
  return [start, end]
}

function referencePeriod(reference) {
  if (reference.periodStart && reference.periodEnd && ['calendar', 'fiscal'].includes(reference.periodType)) {
    return { type: reference.periodType, start: reference.periodStart, end: reference.periodEnd }
  }
  const year = observedYear(reference.year)
  if (year !== null && reference.periodType === 'calendar') return { type: 'calendar', start: `${year}-01-01`, end: `${year}-12-31` }
  return null
}

/** Only verified source dates establish an exact period; numerical labels provide leads. */
export function findPeriodCandidates(reference, employer) {
  const exact = referencePeriod(reference)
  const year = observedYear(reference.year)
  return employer.periods.filter(period => period.rows > 0).flatMap(period => {
    const matchingCohorts = exact ? period.cohorts.filter(cohort => cohort.verifiedPeriod && cohort.periodType === exact.type && cohort.periodStart === exact.start && cohort.periodEnd === exact.end) : []
    if (matchingCohorts.length) return [{ period, cohorts: matchingCohorts, match: 'verified-dates' }]
    // An explicitly known period cannot be satisfied by a conflicting official
    // period, even if a compiler happened to give it the same edition label.
    const sameLabel = String(period.yearLabel) === String(reference.year)
    const possibleYear = year !== null && period.cohorts.some(cohort => cohort.verifiedPeriod
      ? cohort.periodEndYear === year : labelYears(period.yearLabel).includes(year))
    const unverified = period.cohorts.filter(cohort => !cohort.verifiedPeriod)
    if (exact) return sameLabel && unverified.length ? [{ period, cohorts: unverified, match: 'unverified-edition' }] : []
    return sameLabel || possibleYear ? [{ period, cohorts: period.cohorts, match: 'label-candidate' }] : []
  })
}

function describeCandidates(candidates) {
  return candidates.map(({ period, cohorts, match }) => ({
    year: period.yearLabel, match, periodType: period.periodType,
    rows: sum(cohorts.map(cohort => cohort.rows)),
    officialRows: sum(cohorts.filter(cohort => cohort.official).map(cohort => cohort.rows)),
    compiledRows: sum(cohorts.filter(cohort => !cohort.official).map(cohort => cohort.rows)),
    sourceIds: cohorts.map(cohort => cohort.sourceId),
    scopes: unique(cohorts.map(cohort => cohort.scope)),
    periods: cohorts.map(cohort => ({ sourceId: cohort.sourceId, periodType: cohort.periodType, periodStart: cohort.periodStart, periodEnd: cohort.periodEnd })),
  }))
}

const partial = cohort => Boolean(cohort.partialDisclosure || cohort.publicWarning)

export function compareEmployerYear(reference, employer) {
  const candidates = findPeriodCandidates(reference, employer)
  const allCohorts = candidates.flatMap(candidate => candidate.cohorts)
  const official = allCohorts.filter(cohort => cohort.official)
  const result = { referenceYear: String(reference.year), referenceRecordCount: reference.recordCount ?? null,
    referencePeriodType: reference.periodType ?? 'unknown', referenceScope: reference.scope ?? null,
    candidatePeriods: describeCandidates(candidates), repositoryComparableRows: null, countDifference: null,
    status: null, priority: 2, nextAction: null }
  const finish = (status, priority, nextAction) => ({ ...result, status, priority, nextAction })
  if (!allCohorts.length && reference.recordCount === 0) return finish('zero-reference-count', 3, 'The supplied reference reports zero observations for this period. No missing salary rows are inferred; verify the scope before interpreting the zero.')
  if (!allCohorts.length) return finish('missing-period', 1, 'Locate the original employer report for this observed reference year; verify its dates and disclosure scope before importing.')
  if (!official.length) return finish('compiled-only', 1, 'Recover and validate the original report. Compiled edition labels do not establish a verified reporting period or complete coverage.')
  if (candidates.some(candidate => candidate.match !== 'verified-dates')) return finish('period-review', 2, 'Confirm the reference reporting dates. Calendar labels, fiscal ending years and compiled edition labels are not interchangeable.')
  if (!reference.scope || reference.scope === 'unknown') return finish('scope-review', 2, 'Establish whether the reference includes employees, executives, elected officials, board members or other payments before comparing counts.')
  const relevant = official.filter(cohort => cohort.scope === reference.scope || EMPLOYEE_SCOPES.has(reference.scope) && EMPLOYEE_SCOPES.has(cohort.scope))
  if (!relevant.length) return finish('scope-mismatch', 1, 'Find the matching disclosure cohort. Council, board and executive records do not fill employee-schedule gaps.')
  if (relevant.some(cohort => cohort.partialDisclosure)) return finish('partial-disclosure', 1, 'Resolve the withheld or unaccepted rows before claiming full aggregate coverage; preserve the published values.')
  if (relevant.some(cohort => cohort.publicWarning)) return finish('source-warning-review', 2, 'Review the source-specific warning before relying on aggregate parity; a warning may concern control totals or another limitation rather than missing rows.')
  if (relevant.length > 1) return finish('multiple-cohorts-review', 2, 'Check the accepted cohorts for overlapping employees or amendments before adding their record counts together.')
  if (reference.recordCount == null) return finish('record-count-unavailable', 2, 'Add an observed annual record count to the reference snapshot; an employer-wide total cannot fill this field.')
  if (reference.countBasis !== 'records') return finish('count-basis-review', 2, 'Confirm that the reference counts disclosed observations. Unique people, named-only records and all records are different denominators.')
  const cohort = relevant[0]
  if (reference.threshold == null || !reference.thresholdComparison || cohort.threshold !== reference.threshold || cohort.thresholdComparison !== reference.thresholdComparison) {
    return finish('threshold-review', 2, 'Verify the disclosure threshold and its greater-than / at-least rule on both sources before comparing annual record counts.')
  }
  result.repositoryComparableRows = cohort.rows
  result.countDifference = cohort.rows - reference.recordCount
  if (result.countDifference < 0) return finish('repository-fewer-records', 1, 'Reconcile the original schedules row by row to establish whether records are missing or the references use different inclusion rules.')
  if (result.countDifference > 0) return finish('repository-more-records', 2, 'Review scope, amendments and duplicates against the original source; a larger count does not establish better coverage.')
  return finish('aggregate-count-match', 3, 'Period, declared scope, threshold and record count agree. This is an aggregate check; record-level values and identities have not been compared.')
}

function summarizeRepository(employer) {
  const occupied = employer.periods.filter(period => period.rows)
  return { slug: employer.slug, name: employer.name, names: employer.names, sector: employer.sector,
    rows: employer.rows, namedRows: employer.namedRows, officialRows: employer.officialRows,
    compiledRows: employer.compiledRows, employeeRows: employer.employeeRows,
    officialPeriods: occupied.filter(period => period.officialRows).map(period => period.yearLabel),
    officialEmployeePeriods: occupied.filter(period => period.employeeRows).map(period => period.yearLabel),
    compiledEditionLabels: occupied.filter(period => period.compiledRows).map(period => period.yearLabel),
    acceptedPeriodCount: occupied.filter(period => period.officialRows).length,
    sourceLeadCount: employer.leads.length,
    partialSources: unique(occupied.flatMap(period => period.cohorts.filter(partial).map(cohort => cohort.sourceId))) }
}

function leadQueue(repository) {
  const bySlug = new Map(repository.employers.map(employer => [employer.slug, employer]))
  const seen = new Set()
  return repository.sourceCatalog.filter(lead => !['imported', 'aggregate-only'].includes(lead.status)).flatMap(lead => {
    const key = JSON.stringify([lead.employerSlug, lead.year, lead.url, lead.scope])
    if (seen.has(key)) return []
    seen.add(key)
    const employer = bySlug.get(lead.employerSlug)
    const period = employer?.periods.find(period => period.yearLabel === lead.year)
    return [{ id: `source-${hash(key).slice(0, 16)}`, origin: 'repository-source-catalog',
      priority: !employer?.officialRows || lead.year && !period?.employeeRows ? 1 : 2,
      employerSlug: lead.employerSlug, employerName: employer?.name ?? lead.employerSlug,
      referenceEmployer: null, year: lead.year ?? null, status: lead.status,
      sourceUrl: lead.url ?? lead.indexUrl ?? null, sourceId: lead.id,
      scope: lead.scope ?? null, repositoryRows: period?.rows ?? 0, referenceRecords: null,
      nextAction: lead.nextAction ?? lead.reason ?? 'Verify the original report and extraction controls before importing.',
      reason: lead.reason ?? null }]
  })
}

export function buildSunshineComparison(snapshot, repository, aliases = {}) {
  const bySlug = new Map(repository.employers.map(employer => [employer.slug, employer]))
  const queue = leadQueue(repository)
  const employers = snapshot.employers.map(external => {
    const match = resolveEmployer(external, { employers: repository.employers, aliases })
    const employer = match.slug ? bySlug.get(match.slug) : null
    const years = employer ? external.years.map(year => compareEmployerYear(year, employer)) : external.years.map(year => ({
      referenceYear: String(year.year), referenceRecordCount: year.recordCount ?? null, status: match.status === 'ambiguous' ? 'ambiguous-employer' : year.recordCount === 0 ? 'unmatched-employer-zero-count' : 'missing-employer',
      priority: year.recordCount === 0 ? 2 : 1, candidatePeriods: [], repositoryComparableRows: null, countDifference: null,
      nextAction: match.status === 'ambiguous' ? 'Review the legal employer identity and add an explicit alias.' : 'Verify the employer identity, then locate and validate its original salary schedule.' }))
    const summaryStatus = !employer ? match.status === 'ambiguous' ? 'ambiguous-employer' : 'missing-employer'
      : !external.years.length ? employer.officialRows ? 'summary-only' : 'compiled-only-summary'
        : years.every(year => year.status === 'aggregate-count-match') ? 'aggregate-counts-match' : 'review-required'
    const row = { name: external.name, url: external.url ?? null, match, status: summaryStatus,
      aggregate: external.aggregate ?? null, repository: employer ? summarizeRepository(employer) : null, years }
    const findings = years.length ? years.filter(year => !['aggregate-count-match', 'zero-reference-count'].includes(year.status)) : [{
      referenceYear: null, referenceRecordCount: null, status: summaryStatus, priority: !employer || !employer.officialRows ? 1 : 2,
      nextAction: !employer ? 'Review the employer identity and obtain an authorized annual coverage snapshot and original source reports.'
        : !employer.officialRows ? 'Recover the original official history; obtain annual reference counts and reporting dates before claiming a complete comparison.'
          : 'Obtain annual reference counts and reporting dates. Employer-wide totals and displayed year ranges cannot prove year-by-year coverage.' }]
    for (const finding of findings) queue.push({ id: `external-${hash([external.url, external.name, finding.referenceYear]).slice(0, 16)}`,
      origin: 'external-reference', priority: finding.priority, employerSlug: match.slug, employerName: employer?.name ?? external.name,
      referenceEmployer: external.name, year: finding.referenceYear, status: finding.status, sourceUrl: external.url ?? snapshot.source.url,
      sourceId: null, scope: finding.referenceScope ?? null, repositoryRows: finding.repositoryComparableRows ?? null,
      referenceRecords: finding.referenceRecordCount, nextAction: finding.nextAction, reason: null })
    return row
  })
  queue.sort((a, b) => a.priority - b.priority || a.employerName.localeCompare(b.employerName) || String(a.year ?? '').localeCompare(String(b.year ?? '')) || a.id.localeCompare(b.id))
  const statuses = {}
  for (const year of employers.flatMap(employer => employer.years)) statuses[year.status] = (statuses[year.status] ?? 0) + 1
  const summaries = repository.employers.map(summarizeRepository)
  const sectors = unique(summaries.map(employer => employer.sector)).map(sector => {
    const entries = summaries.filter(employer => employer.sector === sector)
    return { sector, employers: entries.length, employersWithOfficial: entries.filter(employer => employer.officialRows).length,
      compiledOnlyEmployers: entries.filter(employer => !employer.officialRows && employer.compiledRows).length,
      officialRows: sum(entries.map(employer => employer.officialRows)), compiledRows: sum(entries.map(employer => employer.compiledRows)),
      rows: sum(entries.map(employer => employer.rows)) }
  })
  const complete = snapshot.source.complete === true
  const annualCount = sum(employers.map(employer => employer.years.length))
  const allAggregateMatches = annualCount > 0 && employers.every(employer => employer.years.length && employer.years.every(year => year.status === 'aggregate-count-match'))
  const status = !complete ? 'incomplete-reference' : allAggregateMatches ? 'observed-aggregate-counts-aligned' : 'review-required'
  return { version: 1, status, source: snapshot.source,
    limitations: [
      'The comparison covers only employers and annual observations present in the supplied snapshot. Partial input is never a complete directory audit.',
      'A displayed employer-wide year range is preserved as a range, not expanded into assumed annual observations.',
      'Calendar, fiscal and compiled edition labels are distinct. Only verified reporting dates establish an exact fiscal period match.',
      'Employer identity matches and equal aggregate counts do not establish record-level equality, unique people, or complete employee coverage.',
      'Directory completeness concerns employer enumeration only. It does not establish a complete annual series for each employer.',
      'Existing source leads are a processing queue, not accepted salary records or proved missing observations.',
    ],
    fingerprints: { snapshotSha256: hash(snapshot), aliasesSha256: hash(aliases), repositoryInputsSha256: repository.inputsSha256 },
    summary: { referenceEmployers: employers.length, referenceAnnualObservations: annualCount,
      matchedEmployers: employers.filter(employer => employer.match.status === 'matched').length,
      unmatchedEmployers: employers.filter(employer => employer.match.status === 'unmatched').length,
      ambiguousEmployers: employers.filter(employer => employer.match.status === 'ambiguous').length,
      summaryOnlyEmployers: employers.filter(employer => !employer.years.length).length,
      annualStatuses: statuses, directoryComplete: complete, annualSeriesCompletenessEstablished: false, recordLevelParityChecked: false,
      repository: repository.totals, repositoryEmployersWithOfficial: summaries.filter(employer => employer.officialRows).length,
      repositoryCompiledOnlyEmployers: summaries.filter(employer => !employer.officialRows && employer.compiledRows).length,
      repositorySourceTasks: queue.filter(task => task.origin === 'repository-source-catalog').length,
      externalReferenceTasks: queue.filter(task => task.origin === 'external-reference').length },
    employers, repositoryEmployers: summaries, sectors, queue, inputs: repository.inputs }
}

export function compareReportChanges(previous, current) {
  if (previous?.version !== 1 || !Array.isArray(previous.queue) || !Array.isArray(previous.repositoryEmployers)) throw new Error('Previous comparison has an unsupported report schema')
  const before = new Map(previous.queue.map(task => [task.id, task]))
  const after = new Map(current.queue.map(task => [task.id, task]))
  const oldPeriods = new Set(previous.repositoryEmployers.flatMap(employer => employer.officialEmployeePeriods.map(year => `${employer.slug}|${year}`)))
  const newPeriods = new Set(current.repositoryEmployers.flatMap(employer => employer.officialEmployeePeriods.map(year => `${employer.slug}|${year}`)))
  const split = key => { const [employerSlug, year] = key.split('|'); return { employerSlug, year } }
  return { previousInputSha256: previous.fingerprints.repositoryInputsSha256, currentInputSha256: current.fingerprints.repositoryInputsSha256,
    referenceChanged: previous.fingerprints.snapshotSha256 !== current.fingerprints.snapshotSha256,
    addedTasks: current.queue.filter(task => !before.has(task.id)),
    removedTasks: previous.queue.filter(task => !after.has(task.id)),
    changedTasks: current.queue.filter(task => before.has(task.id) && JSON.stringify(task) !== JSON.stringify(before.get(task.id))),
    officialEmployeePeriodsAdded: [...newPeriods].filter(key => !oldPeriods.has(key)).sort().map(split),
    officialEmployeePeriodsRemoved: [...oldPeriods].filter(key => !newPeriods.has(key)).sort().map(split),
    rowChange: current.summary.repository.rows - previous.summary.repository.rows }
}

export function toCsv(rows, fields) {
  const cell = value => {
    let text = value == null ? '' : Array.isArray(value) ? value.join('; ') : String(value)
    // CSVs are intended for spreadsheets: prevent source-provided text from
    // becoming a formula when opened. Numeric values remain numeric.
    if (typeof value !== 'number' && /^[\s]*[=+@-]/.test(text)) text = `'${text}`
    return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text
  }
  return [fields.join(','), ...rows.map(row => fields.map(field => cell(row[field])).join(','))].join('\n') + '\n'
}

export const QUEUE_FIELDS = ['priority', 'origin', 'employerName', 'employerSlug', 'referenceEmployer', 'year', 'status', 'scope', 'repositoryRows', 'referenceRecords', 'sourceUrl', 'sourceId', 'nextAction', 'reason', 'id']
export const EMPLOYER_FIELDS = ['slug', 'name', 'sector', 'rows', 'officialRows', 'compiledRows', 'employeeRows', 'officialEmployeePeriods', 'compiledEditionLabels', 'sourceLeadCount', 'partialSources']

export function renderSunshineReport(report) {
  const s = report.summary
  const lines = ['# Sunshine Lists comparison and salary source queue', '',
    `**Comparison status: ${report.status}.** Reference captured ${report.source.retrievedAt}.`, '',
    `The supplied snapshot contains **${s.referenceEmployers} employers** and **${s.referenceAnnualObservations} annual observations**. ${s.directoryComplete ? 'Its declared directory total and collection receipts reconcile.' : '**It is not a complete Sunshine Lists employer inventory.**'} ${s.summaryOnlyEmployers} employer entries contain summary evidence only.`, '',
    `All **${fmt(s.repository.rows)} published PofBC observations** across **${s.repository.employers} employers** were reconciled against the actual employer files: **${fmt(s.repository.officialRows)} official-source observations** and **${fmt(s.repository.compiledRows)} retained compiled observations**. ${s.repositoryEmployersWithOfficial} employers have some official records; ${s.repositoryCompiledOnlyEmployers} have compiled records only.`, '',
    '## Observed reference employers', '',
    '| Sunshine Lists employer | Identity match | Reference summary | PofBC official rows | PofBC compiled rows | Comparison result |',
    '| --- | --- | --- | ---: | ---: | --- |',
    ...report.employers.map(employer => `| ${employer.url ? `[${md(employer.name)}](${employer.url})` : md(employer.name)} | ${md(employer.match.slug ?? employer.match.status)} | ${employer.aggregate ? `${fmt(employer.aggregate.recordCount)} records; ${md(employer.aggregate.yearRangeLabel ?? '')}` : `${employer.years.length} annual observations`} | ${employer.repository ? fmt(employer.repository.officialRows) : '—'} | ${employer.repository ? fmt(employer.repository.compiledRows) : '—'} | ${md(employer.status)} |`), '',
    'Reference totals span the source’s own reported years and definitions. The table deliberately does not subtract employer-wide totals: PofBC can include different years and disclosure categories. A range is not an annual series.', '',
    '## Repository coverage by sector', '',
    '| Sector | Employers | With official records | Compiled only | Official observations | Compiled observations |',
    '| --- | ---: | ---: | ---: | ---: | ---: |',
    ...report.sectors.map(sector => `| ${md(sector.sector)} | ${sector.employers} | ${sector.employersWithOfficial} | ${sector.compiledOnlyEmployers} | ${fmt(sector.officialRows)} | ${fmt(sector.compiledRows)} |`), '',
    '## Processing queue', '',
    `The [work queue](work-queue.csv) contains **${s.repositorySourceTasks} existing official-source tasks** and **${s.externalReferenceTasks} reference-comparison tasks**. Existing leads are linked to their original report or archive and retain the recorded next action. They do not prove that additional records are available or that a report has passed validation.`, '',
    'Priority 1 covers missing official employer/period coverage, held partial employee disclosures, or a smaller comparable count. Priority 2 requires scope, period or source review. The priority is an action order, not a count of missing employees.', '',
    '## How coverage is judged', '', ...report.limitations.map(text => `- ${text}`), '',
    '## Files and reproducibility', '',
    '- [Machine-readable comparison](comparison.json) contains every observed employer, annual decision, source task and SHA-256 input fingerprint.',
    '- [All PofBC employers](repository-employers.csv) lists accepted official employee periods and compiled edition labels separately.',
    '- [Work queue](work-queue.csv) is suitable for filtering by employer, period, source status and priority.',
    '- [Usage and snapshot format](README.md) explains importing a saved snapshot and rerunning the audit.', '',
    `Repository input fingerprint: \`${report.fingerprints.repositoryInputsSha256}\`.`,
    `Reference snapshot fingerprint: \`${report.fingerprints.snapshotSha256}\`.`, '',
  ]
  if (report.changes) lines.push('## Changes since the supplied previous report', '',
    `${report.changes.officialEmployeePeriodsAdded.length} official employee periods added; ${report.changes.officialEmployeePeriodsRemoved.length} removed; ${fmt(report.changes.rowChange)} net observations.`, '',
    'The reference snapshot changed: ' + (report.changes.referenceChanged ? 'yes' : 'no') + '. New/removed tasks must be interpreted against that source change.', '')
  return lines.join('\n')
}
