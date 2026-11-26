import { SCHOOL_DISTRICT_DATA } from './districtData.js'
import { currentDistrictId } from './districtIds.js'
export { currentDistrictId, formerDistrictId } from './districtIds.js'

export const SCHOOL_DISTRICTS_AS_OF = SCHOOL_DISTRICT_DATA.asOf
export const SCHOOL_DIRECTORY_SOURCE = SCHOOL_DISTRICT_DATA.directorySource
export const SCHOOL_ACT_SOURCE = { title: 'School Act — Boards of education', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96412_06' }
export const SCHOOL_FAMILY = { id: 'school-districts', label: 'School districts', description: 'B.C.’s current districts and documented predecessors, with their histories, original logos and salary disclosures.' }
const cleanAliases = (values) => [...new Set(values.filter((value) => typeof value === 'string' && value.trim()))]

export const CURRENT_DISTRICTS = SCHOOL_DISTRICT_DATA.districts.map((record) => ({
  ...record, kind: record.number === 93 ? 'francophone-school-district' : 'school-district',
  title: `SD${record.number} · ${record.name}`,
  aliases: cleanAliases([`SD${record.number}`, `SD ${record.number}`, `School District ${record.number}`, `School District No. ${record.number}`, ...record.aliases])
}))

// A numbered district that was abolished is its own entity. Its successor's artwork, start date
// and payroll are never inherited. In particular, numbers reused later do not identify one body.
export const HISTORICAL_DISTRICTS = (SCHOOL_DISTRICT_DATA.historical ?? []).map((record) => ({
  ...record, current: false, kind: 'school-district',
  title: `SD${record.number} · ${record.name}`, aliases: cleanAliases(record.aliases ?? []),
  assets: record.assets ?? [], sources: record.sources ?? [], events: record.events ?? [], notes: record.notes ?? []
}))
export const DISTRICT_CONNECTIONS = SCHOOL_DISTRICT_DATA.connections ?? []
export const SCHOOL_DISTRICTS = [...CURRENT_DISTRICTS, ...HISTORICAL_DISTRICTS]
export const primaryDistrictDesign = (record) => record.assets.find((asset) => asset.role === 'current' && !asset.variantOf) ??
  record.assets.find((asset) => !asset.variantOf)
export const primaryDistrictLogo = (record) => {
  const design = primaryDistrictDesign(record)
  return record.assets.find((asset) => asset.id === design?.preferredVector) ?? design
}
const byId = new Map(SCHOOL_DISTRICTS.map((record) => [record.id, record]))
export const districtById = (id) => byId.get(String(id)) ?? (/^\d+$/.test(String(id)) ? byId.get(currentDistrictId(id)) : null) ?? null
export const districtForEmployer = (slug) => CURRENT_DISTRICTS.find((record) => record.employerSlug === slug) ?? null
export const establishmentLabel = (record) => record.established?.label ?? (record.established?.kind === 'institutional-origin' ? 'Institutional origin' : record.established?.disputed ? 'Reported establishment' : 'Established')
export const districtPlace = (district, extra = {}) => ({ view: 'school-districts', ...(district ? { district: typeof district === 'object' ? district.id : district } : {}), ...extra })
export const connectionsOf = (id) => ({
  predecessors: DISTRICT_CONNECTIONS.filter((link) => link.to === id).map((link) => ({ ...link, district: districtById(link.from) })),
  successors: DISTRICT_CONNECTIONS.filter((link) => link.from === id).map((link) => ({ ...link, district: districtById(link.to) }))
})
export const connectedDistrictIds = (id) => {
  const seen = new Set([id]); const pending = [id]
  while (pending.length) {
    const next = pending.pop()
    for (const link of DISTRICT_CONNECTIONS.filter((link) => link.from === next || link.to === next)) {
      for (const key of [link.from, link.to]) if (!seen.has(key)) { seen.add(key); pending.push(key) }
    }
  }
  return seen
}
const fold = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('en-CA').replace(/[^\p{L}\p{N}]+/gu, ' ')
export const searchDistricts = ({ query = '', scope = 'current' } = {}) => {
  const words = fold(query).trim().split(/\s+/).filter(Boolean)
  return SCHOOL_DISTRICTS.filter((record) => {
    if (scope === 'current' && !record.current || scope === 'historical' && record.current) return false
    const text = fold([record.title, record.name, record.legalName, record.number, ...record.aliases].join(' '))
    return words.every((word) => text.includes(word))
  })
}
export const formatHistoryDate = (date) => {
  if (!date) return 'Date unconfirmed'
  if (/^\d{4}$/.test(date)) return date
  if (/^\d{4}-\d{4}$/.test(date)) return date.replace('-', '–')
  if (/^\d{4}-\d{2}$/.test(date)) return new Intl.DateTimeFormat('en-CA', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${date}-01T00:00:00Z`))
  if (/^\d{4}-\d{2}-\d{2}$/.test(date)) return new Intl.DateTimeFormat('en-CA', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${date}T00:00:00Z`))
  return date
}
export const districtHistory = (record) => {
  const establishmentEvent = record.events.some((event) => ['established', 'amalgamation'].includes(event.type) && event.date === record.established?.date)
  return [
    ...(record.established?.date && !establishmentEvent ? [{ ...record.established, type: record.established.kind ?? 'established', title: establishmentLabel(record), detail: record.established.meaning }] : []),
    ...record.events,
    ...(record.ended?.date ? [{ ...record.ended, type: 'abolished', title: 'District abolished', detail: record.ended.meaning }] : [])
  ].sort((a, b) => (a.date ?? '9999').localeCompare(b.date ?? '9999'))
}
export const districtSources = (record) => {
  const sources = [
    ...(record.directoryUrl ? [{ title: 'Ministry district directory', url: record.directoryUrl }] : []),
    ...record.sources, ...districtHistory(record).map((event) => ({ title: event.sourceTitle ?? event.title, url: event.sourceUrl, locator: event.locator })),
    ...(record.logoSources ?? []),
    ...record.assets.map((asset) => ({ title: asset.sourceTitle ?? asset.label, url: asset.sourcePage ?? asset.sourceUrl, locator: asset.sourceLocator }))
  ].filter((source) => source.url)
  return [...new Map(sources.map((source) => [`${source.url}:${source.locator ?? ''}`, source])).values()]
}
export const DISTRICT_COUNTS = {
  current: CURRENT_DISTRICTS.length, historical: HISTORICAL_DISTRICTS.length,
  dated: CURRENT_DISTRICTS.filter((record) => record.established?.date).length,
  modernDated: CURRENT_DISTRICTS.filter((record) => record.established?.date && record.established.kind !== 'institutional-origin' && !record.established.disputed).length,
  withLogos: CURRENT_DISTRICTS.filter((record) => record.assets.length).length,
  logos: CURRENT_DISTRICTS.reduce((sum, record) => sum + record.assets.length, 0),
  connections: DISTRICT_CONNECTIONS.length
}
