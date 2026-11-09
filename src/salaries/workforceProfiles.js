const BASE = import.meta.env?.BASE_URL ?? '/'
export function profileAssetUrl(base = BASE) { return `${base.endsWith('/') ? base : `${base}/`}salaries/workforce-profiles.json` }
export function validateProfiles(data) {
  if (data?.schemaVersion !== 1 || data.datasetType !== 'aggregate-workforce-profiles' || !Array.isArray(data.tables) || data.tables.length !== 30) throw new Error('Unsupported workforce profile archive')
  const ids = new Set()
  for (const table of data.tables) {
    if (ids.has(table.id) || !['aggregate-profile', 'ministry-lookup'].includes(table.recordType) || !Array.isArray(table.columns) || !Array.isArray(table.rows) || table.rows.length !== table.rowCount || table.rows.some(row => row.length !== table.columns.length || row.some(cell => typeof cell !== 'string'))) throw new Error('Invalid workforce profile table')
    if (!table.url.startsWith('https://catalogue.data.gov.bc.ca/')) throw new Error('Unexpected workforce profile source')
    ids.add(table.id)
  }
  return data
}
export async function loadProfiles({ base = BASE, fetcher = globalThis.fetch, signal } = {}) {
  const response = await fetcher(profileAssetUrl(base), { signal })
  if (!response.ok) throw new Error(`Profile request failed (${response.status})`)
  return validateProfiles(await response.json())
}
export function filterProfileRows(table, query) {
  const term = query.trim().toLocaleLowerCase('en-CA')
  return term ? table.rows.filter(row => row.some(cell => cell.toLocaleLowerCase('en-CA').includes(term))) : table.rows
}

/** "WP2024_EmpCounts" → { edition: '2024', kind: 'EmpCounts' }. */
export const profileParts = (name) => {
  const match = /^WP(\d{4})_(.+)$/.exec(String(name ?? ''))
  return match ? { edition: match[1], kind: match[2] } : { edition: '', kind: String(name ?? '') }
}

/** Readable names for the kinds of table each edition publishes. */
export const PROFILE_KINDS = {
  EmpCounts: 'Employee counts',
  Comparison: 'Comparison with B.C.',
  Rep_Occ_Rgn: 'By occupation and region',
  Hiring: 'Hiring',
  Flow: 'Workforce flows',
  Ind_Progress: 'Progress',
  Leadership: 'Leadership',
  MinistryKey: 'Ministry key'
}

/**
 * A table with a "Ministry" column after "Ministry_Key", named from the same edition's own
 * MinistryKey table (keys change between editions). Unknown keys stay blank; nothing is guessed.
 */
export const withMinistryNames = (table, tables) => {
  const at = table.columns.indexOf('Ministry_Key')
  if (at < 0 || table.recordType === 'ministry-lookup') return table
  const { edition } = profileParts(table.name)
  const lookup = tables.find((each) => each.name === `WP${edition}_MinistryKey`)
  if (!lookup) return table
  const names = new Map(lookup.rows.map(([key, title]) => [key, title]))
  return {
    ...table,
    columns: [...table.columns.slice(0, at + 1), 'Ministry', ...table.columns.slice(at + 1)],
    rows: table.rows.map((row) => [...row.slice(0, at + 1), names.get(row[at]) ?? '', ...row.slice(at + 1)])
  }
}

/** A cell as a number, or null for text and for "S", "NA" and blank cells, which are not zero. */
export const profileNumber = (cell) => (/^-?\d+(\.\d+)?$/.test(String(cell ?? '').trim()) ? Number(cell) : null)

/** Columns whose every filled, unsuppressed cell is a number. */
export const numericColumns = (table) => table.columns.map((_, at) => {
  const cells = table.rows.map((row) => String(row[at] ?? '').trim()).filter((cell) => cell && !['S', 'NA'].includes(cell))
  return cells.length > 0 && cells.every((cell) => profileNumber(cell) !== null)
})
