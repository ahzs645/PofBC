// Lightweight destinations used by both the gallery and the app's deep-link reader.
export const TRAVEL_LOGO = 'bc-travel-industry-ca-1970'
export const TRAVEL_PLACE = { view: 'internal', internal: 'travel-industry', 'internal-logo': TRAVEL_LOGO }

const youthMarks = new Set(['bc-youth-left-flag', 'bc-youth-right-flag'])
const bcMarkDestinations = new Map([
  ['collected-endorsed-marks-2019', null],
  ['collected-government-communications-and-public-engagement', 'gcpe-estimate-notes-2024-rebuilt'],
  ['specimens-public-service', 'vector-bc-public-service-where-ideas-work-2023-reverse'],
  ['specimens-welcome-bc', 'welcome-bc'],
  ['specimens-work-bc', 'work-bc'],
  ['specimens-stronger-bc', 'stronger-bc']
])

export function movedGalleryPlace({ view, logos, mark, subject, coverage }) {
  if (view !== 'gallery' || subject || coverage) return null
  if (mark === 'icet-lowercase-teal-specimen') return { view, logos: 'collected-island-coastal-economic-trust', mark: 'icet-lowercase-report' }
  if (logos === 'collected-forrex' && mark === 'forrex-siferp') return { view, logos: 'collected-siferp', mark }
  if (mark === TRAVEL_LOGO || logos === 'specimens-travel-industry') return TRAVEL_PLACE
  if (logos === 'collected-bc-youth' || youthMarks.has(mark)) {
    return { view: 'initiatives', initiative: 'bc-youth', ...(youthMarks.has(mark) ? { section: 'marks', record: mark } : {}) }
  }
  if (logos === 'specimens-pacific-gateway') {
    return { view: 'initiatives', initiative: 'pacific-gateway', section: 'marks', ...(mark ? { record: mark } : {}) }
  }
  if (logos === 'specimens-bc-the-education-province') {
    return { view: 'initiatives', initiative: 'bc-the-education-province', ...(mark ? { section: 'marks', record: mark } : {}) }
  }
  if (bcMarkDestinations.has(logos)) {
    const destinationMark = mark || bcMarkDestinations.get(logos)
    return { view: 'gallery', logos: 'bc-mark', ...(destinationMark ? { mark: destinationMark } : {}) }
  }
  return null
}

export function movedGalleryUrl(href) {
  const url = new URL(href)
  const dest = movedGalleryPlace(Object.fromEntries(url.searchParams))
  if (!dest) return null
  for (const key of ['view', 'logos', 'mark']) url.searchParams.delete(key)
  for (const [key, value] of Object.entries(dest)) url.searchParams.set(key, value)
  return url
}
