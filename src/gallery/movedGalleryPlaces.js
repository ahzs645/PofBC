// Lightweight destinations used by both the gallery and the app's deep-link reader.
export const TRAVEL_LOGO = 'bc-travel-industry-ca-1970'
export const TRAVEL_COLLECTION = 'specimens-travel-industry'

// Former departments, ministries and government branches open in Departmental Logos. Each
// collection stays in the gallery's data, unlisted (collections.js), so marks shared with other
// collections, and the register's links, still resolve. Each lists its marks, so a bare link to one
// opens there too; movedGalleryPlaces.test.js keeps these lists in step with the collections.
export const DEPARTMENTAL_MARKS = {
  'recreation-conservation': [
    'drc-dogwood-oval-1970', 'drc-department', 'drc-fish-wildlife', 'drc-parks', 'drc-museum', 'drc-fisheries',
    'drc-fw-oval-1973', 'drc-fw-lockup-1973', 'drc-parks-shield-1973'
  ],
  'fish-wildlife-branch': ['fwb-1971-square', 'fwb-1973-oval', 'fwb-1973-lockup'],
  'collected-bc-public-health-service': ['bc-public-health-service-green-badge'],
  'tourism-recreation-culture': ['tourism-recreation-culture-1986'],
  'bc-lands': ['bc-lands'],
  'bc-environment': ['bc-environment-flag-years'],
  'collected-shared-services-bc': [
    'solutions-bc-2003-vector', 'solutions-bc-2006-letterhead-rebuilt', 'shared-services-bc-2006-07-rebuilt', 'shared-services-bc-2015-rebuilt'
  ],
  [TRAVEL_COLLECTION]: [TRAVEL_LOGO]
}
export const DEPARTMENTAL_COLLECTIONS = Object.keys(DEPARTMENTAL_MARKS)
/** The first step of every trail in Departmental Logos. */
export const DEPARTMENTAL_ROOT = { label: 'All departments', to: { view: 'internal' } }
export const departmentOfMark = new Map(Object.entries(DEPARTMENTAL_MARKS).flatMap(([id, marks]) => marks.map((mark) => [mark, id])))

// A department whose address is not its collection's id: the Department of Travel Industry had its
// own page, at `internal=travel-industry`, before it was a collection here. Both name it.
const DEPARTMENT_ADDRESSES = { [TRAVEL_COLLECTION]: 'travel-industry' }
const DEPARTMENT_OF_ADDRESS = Object.fromEntries(Object.entries(DEPARTMENT_ADDRESSES).map(([id, address]) => [address, id]))
/** The collection a department's address names, or undefined for one that is not a department. */
export const departmentOfAddress = (address) => {
  const id = DEPARTMENT_OF_ADDRESS[address] ?? address
  return DEPARTMENTAL_MARKS[id] ? id : undefined
}

/** A departmental collection's place in Departmental Logos, at one of its marks if given. */
export const departmentalPlace = (id, mark) => ({
  view: 'internal',
  internal: DEPARTMENT_ADDRESSES[id] ?? id,
  ...(mark ? { 'internal-logo': mark } : {})
})
export const TRAVEL_PLACE = departmentalPlace(TRAVEL_COLLECTION, TRAVEL_LOGO)

// Kept for the links written before the other departments moved.
export const RECREATION_COLLECTION = 'recreation-conservation'
export const RECREATION_PLACE = departmentalPlace(RECREATION_COLLECTION)
export const RECREATION_MARKS = new Set(DEPARTMENTAL_MARKS[RECREATION_COLLECTION])

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
  if (mark === TRAVEL_LOGO) return TRAVEL_PLACE
  if (DEPARTMENTAL_MARKS[logos]) return departmentalPlace(logos, mark)
  // A bare link to one of a department's marks; the same mark under another collection stays there.
  if (!logos && departmentOfMark.has(mark)) return departmentalPlace(departmentOfMark.get(mark), mark)
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
