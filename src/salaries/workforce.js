export const WORKFORCE_POPULATIONS = ['all', 'victoria']
const BASE = import.meta.env?.BASE_URL ?? '/'

export function normalizeWorkforcePopulation(value) {
  return WORKFORCE_POPULATIONS.includes(value) ? value : 'all'
}

export function workforceAssetUrl(extension = 'json', base = BASE) {
  return `${base.endsWith('/') ? base : `${base}/`}salaries/workforce.${extension}`
}

export function validateWorkforce(data) {
  if (data?.schemaVersion !== 1 || data?.source?.id !== 'PSA-2024-42006') throw new Error('Unsupported workforce data')
  if (data.source.url !== 'https://docs.openinfo.gov.bc.ca/Response_Package_PSA-2024-42006.pdf') throw new Error('Unexpected workforce source')
  if (data.measures?.averageHeadCount?.label !== 'Average HeadCount' || data.measures?.averageSalary?.label !== 'Average Salary') throw new Error('Workforce measure labels must match the release')
  if (data.period?.periodType !== 'unverified' || data.period.periodStart !== null || data.period.periodEnd !== null) throw new Error('Workforce reporting periods have not been established')
  if (data.measures.averageHeadCount.calculationMethod !== 'unknown' || data.measures.averageSalary.calculationMethod !== 'unknown') throw new Error('Workforce calculation methods have not been established')
  if (!Array.isArray(data.populations) || data.populations.length !== 2 || !Array.isArray(data.observations) || data.observations.length !== 16) throw new Error('Incomplete workforce data')
  const populationIds = data.populations.map(population => population.id)
  if (new Set(populationIds).size !== 2 || WORKFORCE_POPULATIONS.some(id => !populationIds.includes(id))) throw new Error('Unexpected workforce population')
  if (data.populations.find(population => population.id === 'victoria').parentPopulationId !== 'all') throw new Error('Victoria must remain a subset of all employees')
  const seen = new Set()
  for (const row of data.observations) {
    const key = `${row.populationId}:${row.yearLabel}`
    if (!WORKFORCE_POPULATIONS.includes(row.populationId) || typeof row.yearLabel !== 'string' || !/^(201[7-9]|202[0-4])$/.test(row.yearLabel) || seen.has(key)) throw new Error('Duplicate or invalid workforce observation')
    if (!Number.isFinite(row.averageHeadCount) || row.averageHeadCount <= 0 || !Number.isFinite(row.averageSalary) || row.averageSalary <= 0) throw new Error('Invalid workforce measure')
    seen.add(key)
  }
  return data
}

export async function loadWorkforce({ base = BASE, fetcher = globalThis.fetch, signal } = {}) {
  const response = await fetcher(workforceAssetUrl('json', base), { signal })
  if (!response.ok) throw new Error(`Workforce request failed (${response.status})`)
  return validateWorkforce(await response.json())
}

export function selectWorkforceRows(data, populationId) {
  return data.observations.filter(row => row.populationId === normalizeWorkforcePopulation(populationId)).sort((a, b) => a.yearLabel.localeCompare(b.yearLabel))
}

export const formatWorkforceNumber = value => new Intl.NumberFormat('en-CA').format(value)
export const formatWorkforceSalary = value => `$${formatWorkforceNumber(value)}`

const csvCell = value => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : ''
  const text = String(value)
  return `"${(/^[=+\-@\t\r]/.test(text) ? `'${text}` : text).replaceAll('"', '""')}"`
}

export function workforceCsv(data) {
  const headers = ['Population', 'Population source label', 'Parent population', 'Year label', 'Average HeadCount', 'Average Salary', 'Period type', 'Period start', 'Period end', 'Headcount calculation', 'Salary calculation', 'Currency', 'Currency basis', 'Source ID', 'Source URL', 'Source page']
  const rows = [...data.observations].sort((a, b) => a.populationId.localeCompare(b.populationId) || a.yearLabel.localeCompare(b.yearLabel)).map(row => {
    const population = data.populations.find(item => item.id === row.populationId)
    return [population.id, population.sourceLabel, population.parentPopulationId, row.yearLabel, row.averageHeadCount, row.averageSalary, data.period.periodType, data.period.periodStart, data.period.periodEnd, data.measures.averageHeadCount.calculationMethod, data.measures.averageSalary.calculationMethod, data.measures.averageSalary.currency, data.measures.averageSalary.currencyBasis, data.source.id, data.source.url, population.sourcePage]
  })
  return [headers, ...rows].map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n'
}
