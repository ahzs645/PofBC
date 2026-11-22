const LEGACY_TOURISM_COLLECTIONS = new Set([
  'tourism-bc-destination-bc',
  'collected-tourism-bc',
  'collected-destination-bc'
])

/** An initiative, its section and an open record can each be shared in the address. */
export const readInitiativePlace = (href = globalThis.location?.href ?? 'http://localhost/') => {
  const params = new URL(href).searchParams
  return Object.fromEntries(['initiative', 'section', 'record'].map((key) => [key, params.get(key) || null]))
}

/** Start a fresh initiative address while retaining the site's deployment path. */
export const initiativePlaceUrl = (href, { initiative, section, record } = {}) => {
  const url = new URL(href)
  url.search = ''
  url.hash = ''
  url.searchParams.set('view', 'initiatives')
  for (const [key, value] of Object.entries({ initiative, section, record })) {
    if (value !== null && value !== undefined && value !== '') url.searchParams.set(key, value)
  }
  return url
}

/** Only the former tourism detail fragments move; corporate gallery marks keep their URLs. */
export const legacyInitiativeUrl = (href) => {
  const url = new URL(href)
  if (url.searchParams.get('view') !== 'gallery' ||
      !LEGACY_TOURISM_COLLECTIONS.has(url.searchParams.get('logos')) ||
      url.searchParams.has('mark')) return null
  const fragment = url.hash.match(/^#tourism-(websites|marks|timeline|publications|sources)(?:\/([^/]+))?$/)
  if (!fragment) return null
  let record = null
  if (fragment[2]) {
    try { record = decodeURIComponent(fragment[2]) }
    catch { return null }
  }
  return initiativePlaceUrl(url.href, { initiative: 'tourism', section: fragment[1], record })
}
