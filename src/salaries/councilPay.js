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
    return [row.id, tab === 'payments' || row.measure === 'actual-remuneration' ? 'named-payment' : 'office-observation', row.municipality, row.name, row.role, row.year, row.currency ?? 'CAD', row.measure, row.amount, row.remuneration, row.expenses, row.knownExpenses, row.annualSupplement, row.effectiveFrom, row.effectiveTo, row.effectiveDateNote, row.components ? JSON.stringify(row.components) : '', row.sourceId, source.title, source.kind, source.url, source.originalUrl, source.locator, row.sourceLocator, row.pdfPage, row.tablePage, row.tableBlock, councilNotes(row.notes).join(' | '), councilNotes(source.notes).join(' | ')].map(csvCell).join(',')
  })
  columns.push('schedule_version', 'effective_date_sources', 'supporting_sources', 'source_effective_from', 'source_effective_to', 'source_row_key', 'source_row_label', 'table_label', 'council_term_label', 'expense_component_keys', 'reported_precision_cad')
  const completeLines = lines.map((line, at) => `${line},${[rows[at].scheduleVersion, (rows[at].effectiveDateSources ?? []).join(' | '), JSON.stringify(sources.get(rows[at].sourceId)?.supportingSources ?? []), rows[at].sourceEffectiveFrom, rows[at].sourceEffectiveTo, rows[at].sourceRowKey, rows[at].sourceRowLabel, rows[at].tableLabel, rows[at].term, (rows[at].expenseComponentKeys ?? []).join(' | '), rows[at].sourcePrecision ?? rows[at].amountPrecisionCad].map(csvCell).join(',')}`)
  return [columns.join(','), ...completeLines].join('\r\n') + '\r\n'
}

const ROLE_ORDER = ['Mayor', 'Councillor']
const byRole = (a, b) => (ROLE_ORDER.indexOf(a) + 1 || 99) - (ROLE_ORDER.indexOf(b) + 1 || 99) || a.localeCompare(b, 'en-CA')

/**
 * Every municipality with council figures, as one entry: its latest figure for each office, the
 * years it covers and how many named payments it has. A latest figure is the newest year's, the
 * highest where sources disagree, and says so.
 */
export const councilMunicipalities = (data) => {
  const places = new Map()
  const entry = (row) => {
    if (!places.has(row.municipality)) places.set(row.municipality, { name: row.municipality, employerSlug: row.employerSlug ?? null, years: new Set(), offices: new Map(), figures: 0, payments: 0 })
    const place = places.get(row.municipality)
    place.employerSlug ??= row.employerSlug ?? null
    place.years.add(row.year)
    return place
  }
  for (const row of data.observations) {
    const place = entry(row)
    place.figures += 1
    const current = place.offices.get(row.role)
    if (!current || row.year > current.year) place.offices.set(row.role, { year: row.year, amounts: new Set([row.amount]) })
    else if (row.year === current.year) current.amounts.add(row.amount)
  }
  for (const row of data.payments) entry(row).payments += 1
  return [...places.values()].map((place) => {
    const years = [...place.years].sort((a, b) => a - b)
    const offices = [...place.offices].sort(([a], [b]) => byRole(a, b)).map(([role, { year, amounts }]) => {
      const values = [...amounts].filter(Number.isFinite)
      return { role, year, amount: values.length ? Math.max(...values) : null, disagree: values.length > 1 }
    })
    return { name: place.name, employerSlug: place.employerSlug, first: years[0], last: years.at(-1), years, offices, figures: place.figures, payments: place.payments }
  }).sort((a, b) => a.name.localeCompare(b.name, 'en-CA'))
}

/**
 * One municipality's office figures by year and office, newest first. Figures for the same office
 * and year with the same amount (to the dollar) are one entry with every source behind it; different amounts stay
 * separate entries, each with its own type of figure. Nothing is averaged or chosen between.
 */
export const councilFiguresByYear = (rows) => {
  const years = new Map()
  for (const row of rows) {
    if (!years.has(row.year)) years.set(row.year, new Map())
    const roles = years.get(row.year)
    if (!roles.has(row.role)) roles.set(row.role, new Map())
    // A source rounding to the dollar ($139,502) agrees with one printing cents ($139,502.08).
    const key = Number.isFinite(row.amount) ? Math.round(row.amount) : `missing:${row.id}`
    const amounts = roles.get(row.role)
    if (!amounts.has(key)) amounts.set(key, { amount: row.amount, currency: row.currency, measures: [], rows: [] })
    const figure = amounts.get(key)
    if (Number.isInteger(figure.amount) && Number.isFinite(row.amount) && !Number.isInteger(row.amount)) figure.amount = row.amount
    if (!figure.measures.includes(row.measure)) figure.measures.push(row.measure)
    figure.rows.push(row)
  }
  return [...years].sort(([a], [b]) => b - a).map(([year, roles]) => ({
    year,
    roles: [...roles].sort(([a], [b]) => byRole(a, b)).map(([role, amounts]) => ({ role, figures: [...amounts.values()].sort((a, b) => (b.amount ?? -1) - (a.amount ?? -1)) }))
  }))
}
