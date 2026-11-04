// Council office schedules and named payments are different observations. Keep each source row;
// never deduplicate different editions, infer a person's pay from an office, or fill missing years.
export const councilRows = (data, tab) => tab === 'payments' ? data.payments : data.observations

const normalized = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
const selected = (value) => value && value !== 'all'

export const councilSourceMap = (data) => new Map(data.sources.map((source) => [source.id, source]))

export const filterCouncilRows = (rows, filters = {}, sources = new Map()) => {
  const words = normalized(filters.query).trim().split(/\s+/).filter(Boolean)
  return rows.filter((row) => {
    if (selected(filters.municipality) && row.municipality !== filters.municipality) return false
    if (selected(filters.year) && String(row.year) !== String(filters.year)) return false
    if (selected(filters.role) && row.role !== filters.role) return false
    const text = normalized([row.municipality, row.name, row.role, row.year, sources.get(row.sourceId)?.title].join(' '))
    return words.every((word) => text.includes(word))
  }).sort((a, b) => b.year - a.year || a.municipality.localeCompare(b.municipality, 'en-CA') || a.role.localeCompare(b.role, 'en-CA') || (a.name ?? '').localeCompare(b.name ?? '', 'en-CA') || a.sourceId.localeCompare(b.sourceId) || a.id.localeCompare(b.id))
}

/** Coverage describes observed years, not a complete roster or full-year service. */
export const councilYearCoverage = (rows) => {
  const years = [...new Set(rows.map((row) => row.year))].sort((a, b) => a - b)
  const observed = new Set(years)
  const missing = []
  if (years.length) for (let year = years[0]; year <= years.at(-1); year += 1) if (!observed.has(year)) missing.push(year)
  return { years, missing }
}

export const describeCouncilYears = (years) => {
  const sorted = [...new Set(years)].sort((a, b) => a - b)
  const ranges = []
  for (const year of sorted) {
    const last = ranges.at(-1)
    if (last && year === last[1] + 1) last[1] = year
    else ranges.push([year, year])
  }
  return ranges.map(([from, to]) => from === to ? String(from) : `${from}–${to}`).join(', ')
}

export const councilMoney = (value, currency = 'CAD') => Number.isFinite(value)
  ? new Intl.NumberFormat('en-CA', { style: 'currency', currency, minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
  : 'Not reported'

export const councilMeasure = (measure) => ({
  'reported-office-pay': 'Reported office pay',
  'annual-base-rate': 'Annual base rate',
  'actual-remuneration': 'Actual remuneration'
})[measure] ?? measure ?? 'Source figure'

export const councilNotes = (notes) => Array.isArray(notes) ? notes : notes ? [String(notes)] : []

/** Only web references from the source inventory are actionable links. */
export const councilSourceUrl = (value) => {
  try {
    const url = new URL(value)
    return ['https:', 'http:'].includes(url.protocol) ? url.href : null
  } catch { return null }
}

export const validateCouncilPay = (data) => {
  if (data?.version !== 1 || !Array.isArray(data.sources) || !Array.isArray(data.observations) || !Array.isArray(data.payments)) throw new Error('Unsupported council pay data')
  const sources = councilSourceMap(data)
  const ids = new Set()
  for (const row of [...data.observations, ...data.payments]) {
    if (!row.id || ids.has(row.id) || !row.municipality || !row.role || !Number.isInteger(row.year) || !sources.has(row.sourceId)) throw new Error('Incomplete council pay source record')
    ids.add(row.id)
  }
  return data
}

/** The council view fetches this companion alone, independently of the large salary indexes. */
export const loadCouncilPay = async ({ base = import.meta.env?.BASE_URL ?? '/', fetcher = globalThis.fetch, signal } = {}) => {
  const response = await fetcher(`${base.endsWith('/') ? base : `${base}/`}salaries/council-pay.json`, { signal })
  if (!response.ok) throw new Error(`Council pay request failed (${response.status})`)
  return validateCouncilPay(await response.json())
}

// Escape CSV fields and prevent text values being interpreted as spreadsheet formulas. Numeric
// amounts remain numbers, including zero and negative recoveries; absent amounts remain blank.
const csvCell = (value) => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : ''
  const text = String(value)
  return `"${(/^[=+\-@\t\r]/.test(text) ? `'${text}` : text).replaceAll('"', '""')}"`
}

export const councilCsv = (rows, tab, sources) => {
  const columns = ['id', 'record_type', 'municipality', 'name', 'role', 'year', 'currency', 'measure', 'office_amount', 'remuneration', 'expenses', 'known_expenses', 'annual_supplement', 'effective_from', 'effective_to', 'effective_date_note', 'components', 'source_id', 'source_title', 'source_kind', 'source_url', 'source_original_url', 'source_locator', 'row_source_locator', 'pdf_page', 'table_page', 'table_block', 'notes', 'source_notes']
  const lines = rows.map((row) => {
    const source = sources.get(row.sourceId) ?? {}
    return [row.id, tab === 'payments' ? 'named-payment' : 'office-observation', row.municipality, row.name, row.role, row.year, row.currency ?? 'CAD', row.measure, row.amount, row.remuneration, row.expenses, row.knownExpenses, row.annualSupplement, row.effectiveFrom, row.effectiveTo, row.effectiveDateNote, row.components ? JSON.stringify(row.components) : '', row.sourceId, source.title, source.kind, source.url, source.originalUrl, source.locator, row.sourceLocator, row.pdfPage, row.tablePage, row.tableBlock, councilNotes(row.notes).join(' | '), councilNotes(source.notes).join(' | ')].map(csvCell).join(',')
  })
  columns.push('schedule_version', 'effective_date_sources', 'supporting_sources')
  const completeLines = lines.map((line, at) => `${line},${[rows[at].scheduleVersion, (rows[at].effectiveDateSources ?? []).join(' | '), JSON.stringify(sources.get(rows[at].sourceId)?.supportingSources ?? [])].map(csvCell).join(',')}`)
  return [columns.join(','), ...completeLines].join('\r\n') + '\r\n'
}
