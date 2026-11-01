// Offline, aggregate-only import of authorized SunshineLists snapshots.
// Source directory coverage and individual reporting-period coverage are separate.
import { createHash } from 'node:crypto'
import { csvRows, yearSlug } from './salary-data.mjs'

export const SUNSHINE_DIRECTORY_URL = 'https://www.sunshinelists.ca/british-columbia/employers'
const PERIOD_TYPES = new Set(['unknown', 'calendar', 'fiscal'])
const COUNT_BASES = new Set(['records', 'named-records', 'unique-individuals', 'unknown'])
const THRESHOLD_COMPARISONS = new Set(['>', '>='])
const REQUIRED_CSV = ['name', 'url', 'year', 'recordCount']
const CSV_COLUMNS = [...REQUIRED_CSV, 'periodType', 'periodStart', 'periodEnd', 'scope', 'threshold', 'thresholdComparison']
const AGGREGATE_CSV = ['aggregateRecordCount', 'uniqueIndividuals', 'yearRangeLabel', 'yearMin', 'yearMax']
const hasValue = (value) => value !== undefined && value !== null && value !== ''
const fail = (message) => { throw new Error(`Sunshine snapshot: ${message}`) }
const text = (value, label, { optional = false } = {}) => {
  if (!hasValue(value) && optional) return null
  if (typeof value !== 'string' || !value.trim()) fail(`${label} must be a non-empty string`)
  return value.trim()
}
const count = (value, label) => {
  if (!hasValue(value)) return null
  if (typeof value !== 'number' && typeof value !== 'string') fail(`${label} must be a non-negative integer`)
  const normalized = typeof value === 'string' ? value.trim() : value
  if (typeof normalized === 'string' && !/^(?:\d+|\d{1,3}(?:,\d{3})+)$/.test(normalized)) fail(`${label} must be a non-negative integer`)
  const result = Number(String(normalized).replaceAll(',', ''))
  if (!Number.isSafeInteger(result) || result < 0) fail(`${label} must be a non-negative integer`)
  return result
}
const date = (value, label) => {
  if (!hasValue(value)) return null
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) fail(`${label} must be YYYY-MM-DD`)
  const parsed = new Date(`${value}T00:00:00Z`)
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) fail(`${label} is not a valid date`)
  return value
}
const instant = (value, label) => {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(value)) fail(`${label} must be an ISO timestamp with timezone`)
  if (Number.isNaN(Date.parse(value))) fail(`${label} must be a valid ISO timestamp`)
  date(value.slice(0, 10), label)
  return new Date(value).toISOString()
}
const sourceUrl = (value, label) => {
  let url
  try { url = new URL(text(value, label)) } catch { fail(`${label} must be an absolute HTTP(S) URL`) }
  if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) fail(`${label} must be an HTTP(S) URL without credentials`)
  url.hash = ''
  return url.href.replace(/\/$/, '')
}
const stringList = (value, label) => {
  if (value === undefined || value === null) return []
  if (!Array.isArray(value)) fail(`${label} must be an array`)
  return [...new Set(value.map((item) => text(item, label)))]
}
const countBasis = (value, label) => {
  const basis = text(value, label)
  if (!COUNT_BASES.has(basis)) fail(`${label} must be records, named-records, unique-individuals, or unknown`)
  return basis
}

function normalizeYear (input, employerName) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail(`${employerName}: year entries must be objects`)
  const year = String(input.year ?? '').trim()
  try { yearSlug(year) } catch { fail(`${employerName}: invalid year label ${year || '(empty)'}`) }
  const periodType = input.periodType ?? 'unknown'
  if (!PERIOD_TYPES.has(periodType)) fail(`${employerName}|${year}: invalid periodType`)
  if (periodType === 'calendar' && !/^\d{4}$/.test(year)) fail(`${employerName}|${year}: fiscal label cannot be calendar`)
  const periodStart = date(input.periodStart, `${employerName}|${year} periodStart`)
  const periodEnd = date(input.periodEnd, `${employerName}|${year} periodEnd`)
  if (Boolean(periodStart) !== Boolean(periodEnd)) fail(`${employerName}|${year}: periodStart and periodEnd must be supplied together`)
  if (periodStart && periodStart > periodEnd) fail(`${employerName}|${year}: reversed reporting period`)
  if (periodType === 'calendar' && periodStart && (periodStart !== `${year}-01-01` || periodEnd !== `${year}-12-31`)) {
    fail(`${employerName}|${year}: dates disagree with calendar reporting period`)
  }
  if (periodType === 'fiscal' && /^\d{4}\/\d{2}$/.test(year) && periodStart &&
    (periodStart.slice(0, 4) !== year.slice(0, 4) || Number(periodEnd.slice(0, 4)) !== Number(year.slice(0, 4)) + 1)) {
    fail(`${employerName}|${year}: dates disagree with fiscal year label`)
  }
  if (hasValue(input.thresholdComparison) && !THRESHOLD_COMPARISONS.has(input.thresholdComparison)) {
    fail(`${employerName}|${year}: thresholdComparison must be > or >=`)
  }
  return {
    year,
    recordCount: count(input.recordCount, `${employerName}|${year} recordCount`),
    periodType,
    ...(periodStart ? { periodStart, periodEnd } : {}),
    ...(hasValue(input.scope) ? { scope: text(input.scope, 'scope') } : {}),
    ...(hasValue(input.threshold) ? { threshold: count(input.threshold, 'threshold') } : {}),
    ...(hasValue(input.thresholdComparison) ? { thresholdComparison: input.thresholdComparison } : {}),
    ...(hasValue(input.countBasis) ? { countBasis: countBasis(input.countBasis, 'countBasis') } : {})
  }
}

function normalizeAggregate (input, employerName) {
  if (input === undefined || input === null) return undefined
  if (typeof input !== 'object' || Array.isArray(input)) fail(`${employerName}: aggregate must be an object`)
  const aggregate = {
    recordCount: count(input.recordCount, `${employerName} aggregate recordCount`),
    uniqueIndividuals: count(input.uniqueIndividuals, `${employerName} aggregate uniqueIndividuals`)
  }
  if (aggregate.recordCount !== null && aggregate.uniqueIndividuals !== null && aggregate.uniqueIndividuals > aggregate.recordCount) {
    fail(`${employerName}: unique individuals exceed total records`)
  }
  if (hasValue(input.yearRangeLabel)) aggregate.yearRangeLabel = text(input.yearRangeLabel, 'yearRangeLabel')
  if (hasValue(input.yearMin) || hasValue(input.yearMax)) {
    const yearMin = count(input.yearMin, 'yearMin'); const yearMax = count(input.yearMax, 'yearMax')
    if (yearMin === null || yearMax === null || yearMin < 1000 || yearMax > 9999 || yearMin > yearMax) fail(`${employerName}: invalid aggregate year range`)
    Object.assign(aggregate, { yearMin, yearMax })
  }
  return aggregate
}

function validateCompleteness (source, employers) {
  if (source.complete !== true) return null
  if (['manual-page-summary-review', 'authorized-saved-html'].includes(source.collectionMethod)) {
    fail('employer-page summary observations cannot establish complete directory coverage')
  }
  const expected = count(source.expectedEmployerCount, 'expectedEmployerCount')
  const evidence = source.completenessEvidence
  if (expected === null || !evidence || evidence.kind !== 'paginated-directory') {
    fail('complete:true requires expectedEmployerCount and paginated-directory completenessEvidence; a boolean or search-result count is not proof of a complete directory')
  }
  const pageCount = count(evidence.pageCount, 'completenessEvidence.pageCount')
  const reportedTotal = count(evidence.reportedTotal, 'completenessEvidence.reportedTotal')
  if (reportedTotal !== expected || expected !== employers.length) fail('directory employer counts do not match the declared total')
  if (!pageCount || !Array.isArray(evidence.pages) || evidence.pages.length !== pageCount) fail('missing directory page receipts')
  const pages = evidence.pages.map((page) => ({
    page: count(page.page, 'page receipt number'),
    url: sourceUrl(page.url, 'page receipt url'),
    sha256: text(page.sha256, 'page receipt sha256'),
    employerUrls: Array.isArray(page.employerUrls) ? page.employerUrls.map((url) => sourceUrl(url, 'page receipt employer URL')) : fail('page receipt employerUrls must be an array')
  })).sort((a, b) => a.page - b.page)
  for (let index = 0; index < pages.length; index += 1) {
    if (pages[index].page !== index + 1 || !/^[a-f\d]{64}$/.test(pages[index].sha256)) fail('invalid or duplicate directory page receipts')
  }
  const urls = pages.flatMap((page) => page.employerUrls)
  const observed = new Set(urls)
  if (urls.length !== expected || observed.size !== expected || employers.some((employer) => !observed.has(employer.url))) {
    fail('page receipts contain missing, repeated, or unrecognized employer URLs')
  }
  return { kind: 'paginated-directory', pageCount, reportedTotal, pages }
}

/** Validate provenance and normalize aggregate observations without adding absent years or people. */
export function normalizeSunshineSnapshot (input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail('input must be an object')
  if (input.version !== undefined && input.version !== 1) fail('unsupported version')
  const rawSource = input.source
  if (!rawSource || typeof rawSource !== 'object') fail('source provenance is required')
  if (rawSource.complete !== undefined && typeof rawSource.complete !== 'boolean') fail('source.complete must be a boolean')
  if (!Array.isArray(input.employers)) fail('employers must be an array')
  const source = {
    url: sourceUrl(rawSource.url, 'source.url'),
    retrievedAt: instant(rawSource.retrievedAt, 'source.retrievedAt'),
    complete: rawSource.complete === true,
    expectedEmployerCount: count(rawSource.expectedEmployerCount, 'source.expectedEmployerCount'),
    collectionMethod: text(rawSource.collectionMethod, 'source.collectionMethod'),
    notes: stringList(rawSource.notes, 'source.notes'),
    ...(hasValue(rawSource.countBasis) ? { countBasis: countBasis(rawSource.countBasis, 'source.countBasis') } : {}),
    ...(hasValue(rawSource.inputSha256) ? { inputSha256: text(rawSource.inputSha256, 'source.inputSha256') } : {})
  }
  if (source.inputSha256 && !/^[a-f\d]{64}$/.test(source.inputSha256)) fail('source.inputSha256 must be a SHA-256 hex digest')
  const identities = new Map()
  for (const record of input.employers) {
    if (!record || typeof record !== 'object' || Array.isArray(record)) fail('employer entries must be objects')
    const name = text(record.name, 'employer name')
    const url = sourceUrl(record.url, `${name} url`)
    if (!Array.isArray(record.years)) fail(`${name}: years must be an array (use [] when annual data is unavailable)`)
    const years = record.years.map((year) => normalizeYear(year, name))
    const yearKeys = new Set()
    for (const entry of years) {
      if (yearKeys.has(entry.year)) fail(`${name}: repeated year ${entry.year}; resolve duplicate evidence explicitly`)
      yearKeys.add(entry.year)
    }
    const aggregate = normalizeAggregate(record.aggregate, name)
    const normalized = { name, url, years: years.sort((a, b) => a.year.localeCompare(b.year)), ...(aggregate ? { aggregate } : {}) }
    if (record.notes !== undefined) normalized.notes = stringList(record.notes, `${name} notes`)
    if (identities.has(url)) fail(`${name}: repeated employer URL ${url}`)
    identities.set(url, normalized)
  }
  const employers = [...identities.values()].sort((a, b) => a.name.localeCompare(b.name, 'en'))
  if (source.expectedEmployerCount !== null && employers.length > source.expectedEmployerCount) fail('observed employers exceed expectedEmployerCount')
  const evidence = validateCompleteness({ ...source, completenessEvidence: rawSource.completenessEvidence }, employers)
  if (evidence) source.completenessEvidence = evidence
  if (!source.complete && !source.notes.includes('This snapshot does not establish complete employer-directory coverage.')) {
    source.notes.push('This snapshot does not establish complete employer-directory coverage.')
  }
  return {
    version: 1,
    source,
    employers,
    summary: {
      employerCount: employers.length,
      employerYearCount: employers.reduce((sum, employer) => sum + employer.years.length, 0),
      employerYearsWithCounts: employers.reduce((sum, employer) => sum + employer.years.filter((year) => year.recordCount !== null).length, 0),
      aggregateOnlyEmployers: employers.filter((employer) => employer.years.length === 0 && employer.aggregate).length,
      directoryComplete: source.complete,
      completenessBasis: source.complete ? 'internally-reconciled-page-receipts' : 'not-established'
    }
  }
}

/** Long-form CSV. A blank year preserves an employer-only observation; it is never year zero. */
export function parseSunshineCsv (input, source) {
  const rows = [...csvRows(String(input).replace(/^\uFEFF/, ''))]
  if (!rows.length) fail('CSV is empty')
  const headers = rows.shift().map((header) => header.trim())
  if (new Set(headers).size !== headers.length) fail('CSV has duplicate columns')
  for (const required of REQUIRED_CSV) if (!headers.includes(required)) fail(`CSV is missing ${required} column`)
  for (const header of headers) if (![...CSV_COLUMNS, 'countBasis', ...AGGREGATE_CSV].includes(header)) fail(`unsupported CSV column ${header}`)
  const employers = new Map()
  for (let index = 0; index < rows.length; index += 1) {
    const values = rows[index]
    if (values.length !== headers.length) fail(`CSV row ${index + 2} has ${values.length} columns; expected ${headers.length}`)
    const row = Object.fromEntries(headers.map((key, column) => [key, values[column].trim()]))
    const url = sourceUrl(row.url, `CSV row ${index + 2} url`)
    const name = text(row.name, `CSV row ${index + 2} name`)
    if (!employers.has(url)) employers.set(url, { name, url, years: [] })
    const employer = employers.get(url)
    if (employer.name !== name) fail(`CSV has conflicting employer names for ${url}`)
    if (AGGREGATE_CSV.some((column) => hasValue(row[column]))) {
      const aggregate = normalizeAggregate({ recordCount: row.aggregateRecordCount, ...Object.fromEntries(AGGREGATE_CSV.slice(1).map((column) => [column, row[column]])) }, name)
      if (employer.aggregate && JSON.stringify(employer.aggregate) !== JSON.stringify(aggregate)) fail(`CSV has conflicting aggregate figures for ${name}`)
      employer.aggregate = aggregate
    }
    if (row.year) {
      const year = Object.fromEntries(Object.entries(row).filter(([key]) => !['name', 'url', ...AGGREGATE_CSV].includes(key)))
      year.periodType ||= 'unknown'
      employer.years.push(year)
    } else if (Object.entries(row).some(([key, value]) => !['name', 'url', 'year', ...AGGREGATE_CSV].includes(key) && value !== '')) {
      fail(`CSV row ${index + 2}: values without a year cannot be treated as annual data`)
    }
  }
  return normalizeSunshineSnapshot({ version: 1, source, employers: [...employers.values()] })
}

const decodeHtml = (input) => String(input).replace(/&(?:#(x[\da-f]+|\d+)|([a-z]+));/gi, (match, numeric, named) => {
  if (numeric) {
    const code = numeric[0].toLowerCase() === 'x' ? parseInt(numeric.slice(1), 16) : Number(numeric)
    return code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : '\uFFFD'
  }
  return { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', ndash: '–', mdash: '—' }[named.toLowerCase()] ?? match
})
const visibleHtmlText = (html) => decodeHtml(String(html).replace(/<[^>]*>/g, ' ')).normalize('NFC').replace(/\s+/g, ' ').trim()
const employerSummary = (visible) => ({
  total: /Total Records\s*:\s*([\d,]+)\s+across\s+([\d,]+)\s+unique individuals/i.exec(visible),
  years: /Years Present\s*:\s*(\d{4})(?:\s*[-–—]\s*(\d{4}))?/i.exec(visible)
})

/**
 * A saved employer page exposes totals but loads annual tables separately.
 * Extract only explicit totals/ranges. Do not interpret the range as continuous annual coverage.
 * source.employerName must match the observed employer h3 heading. Only its following block is read.
 */
export function parseSunshineEmployerHtml (html, source) {
  const name = text(source?.employerName, 'source.employerName for saved HTML')
  const document = String(html)
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
  const headings = [...document.matchAll(/<h3\b[^>]*>([\s\S]*?)<\/h3\s*>/gi)]
  if (!headings.length) fail('saved HTML is missing an observed employer h3 heading')
  const expectedName = decodeHtml(name).normalize('NFC').replace(/\s+/g, ' ').trim()
  const sections = headings.map((heading, index) => ({
    name: visibleHtmlText(heading[1]),
    ...employerSummary(visibleHtmlText(document.slice(heading.index + heading[0].length, headings[index + 1]?.index ?? document.length)))
  }))
  const matches = sections.filter((section) => section.name === expectedName)
  if (matches.length !== 1) fail(`saved HTML employer identity mismatch: expected one h3 heading for "${name}", found ${matches.length}`)
  if (sections.some((section) => section.name !== expectedName && (section.total || section.years))) {
    fail('saved HTML contains an employer summary under a different h3 identity')
  }
  const { total, years } = matches[0]
  if (!total && !years) fail('saved HTML contains no recognized employer summary; dynamic or changed markup needs review')
  const aggregate = {
    recordCount: total ? count(total[1], 'total records') : null,
    uniqueIndividuals: total ? count(total[2], 'unique individuals') : null,
    ...(years ? { yearRangeLabel: years[0].replace(/^Years Present\s*:\s*/i, ''), yearMin: Number(years[1]), yearMax: Number(years[2] || years[1]) } : {})
  }
  const notes = [...(source.notes ?? []), 'Saved employer HTML provides aggregate figures only; a displayed year range does not establish every intervening employer-year.']
  return normalizeSunshineSnapshot({
    version: 1,
    source: { ...source, complete: false, collectionMethod: source.collectionMethod || 'authorized-saved-html', notes },
    employers: [{ name, url: source.url, years: [], aggregate }]
  })
}

const escapeCsv = (value) => {
  const raw = value === null || value === undefined ? '' : String(value)
  return /[",\r\n]/.test(raw) ? `"${raw.replaceAll('"', '""')}"` : raw
}
export function sunshineSnapshotToCsv (snapshot) {
  const normalized = normalizeSunshineSnapshot(snapshot)
  const columns = [...CSV_COLUMNS, 'countBasis', ...AGGREGATE_CSV]
  const rows = [columns]
  for (const employer of normalized.employers) {
    const observations = employer.years.length ? employer.years : [{}]
    for (const year of observations) {
      const { recordCount: aggregateRecordCount, ...aggregate } = employer.aggregate ?? {}
      const row = { name: employer.name, url: employer.url, ...year, aggregateRecordCount, ...aggregate }
      rows.push(columns.map((column) => row[column]))
    }
  }
  return `${rows.map((row) => row.map(escapeCsv).join(',')).join('\n')}\n`
}

export const sunshineInputSha256 = (bytes) => createHash('sha256').update(bytes).digest('hex')
