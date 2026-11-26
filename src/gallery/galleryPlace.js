// Gallery pages and register filters are shareable without carrying another page's selection.
const COVERAGE_FILTERS = ['family', 'state', 'scope', 'query', 'region', 'category']
export const GALLERY_PLACE_KEYS = ['logos', 'mark', 'subject', 'coverage', ...COVERAGE_FILTERS.map((key) => `identity-${key}`)]

export const readCoverageFilters = (search = globalThis.location?.search ?? '') => {
  const params = new URLSearchParams(search)
  return Object.fromEntries(COVERAGE_FILTERS.map((key) => [key, params.get(`identity-${key}`) ?? '']))
}

export const galleryPlaceUrl = (href, { collection, mark, subject, coverage = false, filters = {} } = {}) => {
  const url = new URL(href)
  GALLERY_PLACE_KEYS.forEach((key) => url.searchParams.delete(key))
  for (const key of ['year', 'node', 'mode', 'compare', 'undated', 'local', 'instrument', 'initiative', 'section', 'record']) url.searchParams.delete(key)
  url.searchParams.delete('colour')
  url.searchParams.set('view', 'gallery')
  if (subject) url.searchParams.set('subject', subject)
  else if (coverage) {
    url.searchParams.set('coverage', '1')
    for (const key of COVERAGE_FILTERS) if (filters[key]) url.searchParams.set(`identity-${key}`, filters[key])
  } else {
    if (collection) url.searchParams.set('logos', collection)
    if (mark) url.searchParams.set('mark', mark)
  }
  if (url.hash.startsWith('#era-')) url.hash = ''
  if (/^#railway-(history|connections|evidence)$/.test(url.hash)) url.hash = ''
  if (/^#unbc-origins(?:-(campaign|timeline|sources))?$/.test(url.hash)) url.hash = ''
  if (url.hash === '#council-timeline-heading') url.hash = ''
  if (/^#tourism-/.test(url.hash)) url.hash = ''
  return url
}
