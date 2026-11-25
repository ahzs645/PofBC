// Lightweight destinations used by both the gallery and the app's deep-link reader.
export const TRAVEL_LOGO = 'bc-travel-industry-ca-1970'
export const TRAVEL_PLACE = { view: 'internal', internal: 'travel-industry', 'internal-logo': TRAVEL_LOGO }

const youthMarks = new Set(['bc-youth-left-flag', 'bc-youth-right-flag'])
const gcpeMark = 'gcpe-estimate-notes-2024-rebuilt'

export function movedGalleryPlace({ view, logos, mark, subject, coverage }) {
  if (view !== 'gallery' || subject || coverage) return null
  if (mark === TRAVEL_LOGO || logos === 'specimens-travel-industry') return TRAVEL_PLACE
  if (logos === 'collected-bc-youth' || youthMarks.has(mark)) {
    return { view: 'initiatives', initiative: 'bc-youth', ...(youthMarks.has(mark) ? { section: 'marks', record: mark } : {}) }
  }
  if (logos === 'collected-government-communications-and-public-engagement') {
    return { view: 'gallery', logos: 'bc-mark', mark: mark || gcpeMark }
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
