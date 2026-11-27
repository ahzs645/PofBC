// Every page of Departmental Logos, as an address.
//
//   ?view=internal                                            the index of departments
//   ?view=internal&internal=<department>                      a department's page
//   ?view=internal&internal=<department>&internal-logo=<mark> one of its marks
//   …&internal-variant=<variant>                              a Forests design in one of its versions
//
// A department is Forests, whose designs are this section's own reconstructions (forestLogos.js),
// or one of the gallery's departmental collections (movedGalleryPlaces.js), by its address. Every
// page is reached through the site's navigation, so each is a history entry, opens in a new tab and
// survives a reload. An address that names a page another way — a mark without its department, a
// department by its collection's id, a mark or version that is not there — is rewritten to the one
// address of the page it means (resolveInternalPlace), so a link written before stays good.

import { FOREST_LOGOS, variantsFor } from './forestLogos.js'
import { departmentalPlace, departmentOfAddress, departmentOfMark, DEPARTMENTAL_MARKS, TRAVEL_COLLECTION } from '../gallery/movedGalleryPlaces.js'

export const FORESTS = 'forests'
export const INTERNAL_INDEX = { view: 'internal' }
export const FORESTS_PLACE = { view: 'internal', internal: FORESTS }

/** All of a design's versions, in the order its page offers them; the first is its default. */
export const forestVersions = (logo) => {
  const { colours, studies = [], related = [] } = variantsFor(logo)
  return [...colours, ...studies, ...related]
}

/** A Forests design's page, in one of its versions if that is not its default. */
export const forestPlace = (logoId, variantId) => {
  const logo = FOREST_LOGOS.find(({ id }) => id === logoId)
  const versions = logo ? forestVersions(logo) : []
  const variant = variantId && versions.slice(1).some(({ id }) => id === variantId) ? variantId : null
  return {
    ...FORESTS_PLACE,
    ...(logo ? { 'internal-logo': logo.id } : {}),
    ...(variant ? { 'internal-variant': variant } : {})
  }
}

/**
 * The index's cards, oldest first: what each department is, without loading the gallery. A card's
 * cover is drawn by its department (InternalLogosView.jsx).
 */
export const DEPARTMENT_INDEX = [
  { id: FORESTS, title: 'Forests', note: 'A seal, an emblem and six oval designs' },
  { id: 'collected-bc-public-health-service', title: 'BC Public Health Service', note: 'A public health nursing badge, 1961' },
  { id: TRAVEL_COLLECTION, title: 'Department of Travel Industry', note: 'Map and dogwood, about 1970' },
  { id: 'recreation-conservation', title: 'Department of Recreation and Conservation', note: 'A dogwood oval, five square symbols and two branch emblems, 1970–1973' },
  { id: 'tourism-recreation-culture', title: 'Ministry of Tourism, Recreation and Culture', note: 'The flag run out as three bands, 1986–1988' },
  { id: 'bc-lands', title: 'BC Lands', note: 'The flag-years badge, seen 1986–88 and 1994' },
  { id: 'bc-environment', title: 'Ministry of Environment', note: 'The flag-years mark, undated; the ministry of 1988–1991' },
  { id: 'collected-shared-services-bc', title: 'Solutions BC and Shared Services BC', note: 'Four marks, 2003–2015' }
]

/** A department's page, by its index id. */
export const departmentPlace = (id) => id === FORESTS ? FORESTS_PLACE : departmentalPlace(id)

/**
 * What an address shows, and the one address for it.
 *
 * @param {Record<string, string>} params The address's parameters.
 * @returns {{ department: string|null, mark: string|null, variant: string|null, place: object }}
 *   `department` is FORESTS or a departmental collection's id; `place` is the page's own address.
 */
export const resolveInternalPlace = (params) => {
  const asked = params.internal || null
  const markAsked = params['internal-logo'] || null
  const forest = (id) => FOREST_LOGOS.some((logo) => logo.id === id)
  // A mark named without its department (an older link) belongs to the department that holds it.
  const department = asked === FORESTS ? FORESTS
    : asked ? departmentOfAddress(asked) ?? null
    : forest(markAsked) ? FORESTS
    : departmentOfMark.get(markAsked) ?? null
  if (department === FORESTS) {
    const mark = forest(markAsked) ? markAsked : null
    const place = forestPlace(mark, params['internal-variant'])
    return { department, mark, variant: place['internal-variant'] ?? null, place }
  }
  if (department) {
    const mark = DEPARTMENTAL_MARKS[department].includes(markAsked) ? markAsked : null
    return { department, mark, variant: null, place: departmentalPlace(department, mark) }
  }
  return { department: null, mark: null, variant: null, place: INTERNAL_INDEX }
}

const PLACE_KEYS = ['internal', 'internal-logo', 'internal-variant']

/**
 * The address of the page an address of this section means, when it names that page another way;
 * null when it is already the page's own. Everything else in the address (the theme, the base path)
 * is kept.
 */
export const internalPlaceUrl = (href) => {
  const url = new URL(href)
  const params = Object.fromEntries(url.searchParams)
  if (params.view !== 'internal') return null
  const { place } = resolveInternalPlace(params)
  if (PLACE_KEYS.every((key) => (params[key] || undefined) === place[key])) return null
  for (const key of PLACE_KEYS) url.searchParams.delete(key)
  for (const key of PLACE_KEYS) if (place[key]) url.searchParams.set(key, place[key])
  return url
}
