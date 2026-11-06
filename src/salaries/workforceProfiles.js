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
