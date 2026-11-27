// Every page of Departmental Logos has one address, and every older form of an address still opens
// the page it meant.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { FOREST_LOGOS, variantsFor } from './forestLogos.js'
import {
  DEPARTMENT_INDEX, departmentPlace, FORESTS, FORESTS_PLACE, forestPlace, forestVersions, INTERNAL_INDEX,
  internalPlaceUrl, resolveInternalPlace
} from './internalPlaces.js'
import { DEPARTMENTAL_COLLECTIONS, DEPARTMENTAL_MARKS, departmentalPlace, TRAVEL_COLLECTION, TRAVEL_LOGO, TRAVEL_PLACE } from '../gallery/movedGalleryPlaces.js'

const BASE = 'https://example.test/PofBC/'
// The query string SiteLink writes for a place (navigation.jsx's searchFor, which is JSX-bound).
const search = (place) => `?${new URLSearchParams(Object.entries(place).filter(([, value]) => value != null && value !== ''))}`
const rewritten = (query) => internalPlaceUrl(`${BASE}${query}`)?.search ?? null

/** Every page in the section: the index, each department, each mark and each Forests version. */
const everyPage = () => [
  { page: 'index', place: INTERNAL_INDEX },
  ...DEPARTMENT_INDEX.map(({ id }) => ({ page: `department ${id}`, place: departmentPlace(id) })),
  ...FOREST_LOGOS.flatMap((logo) => [
    { page: `Forests design ${logo.id}`, place: forestPlace(logo.id) },
    ...forestVersions(logo).slice(1).map((version) => ({ page: `Forests ${logo.id} as ${version.id}`, place: forestPlace(logo.id, version.id) }))
  ]),
  ...Object.entries(DEPARTMENTAL_MARKS).flatMap(([id, marks]) => marks.map((mark) => ({ page: `${id} mark ${mark}`, place: departmentalPlace(id, mark) })))
]

test('the index lists every department once, Forests first', () => {
  const ids = DEPARTMENT_INDEX.map(({ id }) => id)
  assert.equal(new Set(ids).size, ids.length)
  assert.deepEqual(new Set(ids), new Set([FORESTS, ...DEPARTMENTAL_COLLECTIONS]))
  assert.equal(ids[0], FORESTS)
  for (const { title, note } of DEPARTMENT_INDEX) assert.ok(title && note && !note.includes('\n'), title)
  // The Forests card counts its designs: a seal, an emblem and the ovals.
  assert.equal(FOREST_LOGOS.length, 8)
})

test('every page has its own address, which opens it and is not rewritten', () => {
  const addresses = new Set()
  for (const { page, place } of everyPage()) {
    const address = search(place)
    assert.ok(!addresses.has(address), `${page}: ${address} is another page’s address`)
    addresses.add(address)
    assert.equal(rewritten(address), null, `${page}: ${address} is rewritten`)
    const resolved = resolveInternalPlace(Object.fromEntries(new URLSearchParams(address)))
    assert.deepEqual(resolved.place, place, page)
  }
})

test('the addresses are the ones links were written with', () => {
  assert.equal(search(INTERNAL_INDEX), '?view=internal')
  assert.equal(search(FORESTS_PLACE), '?view=internal&internal=forests')
  assert.equal(search(forestPlace('forest-service')), '?view=internal&internal=forests&internal-logo=forest-service')
  assert.equal(search(forestPlace('forest-service', 'black-gold')), '?view=internal&internal=forests&internal-logo=forest-service&internal-variant=black-gold')
  assert.equal(search(departmentPlace(TRAVEL_COLLECTION)), '?view=internal&internal=travel-industry')
  assert.equal(search(TRAVEL_PLACE), '?view=internal&internal=travel-industry&internal-logo=bc-travel-industry-ca-1970')
  assert.equal(search(departmentPlace('recreation-conservation')), '?view=internal&internal=recreation-conservation')
  assert.equal(search(departmentalPlace('bc-environment', 'bc-environment-flag-years')), '?view=internal&internal=bc-environment&internal-logo=bc-environment-flag-years')
})

test('each page resolves to what it shows', () => {
  assert.deepEqual(resolveInternalPlace({ view: 'internal' }), { department: null, mark: null, variant: null, place: INTERNAL_INDEX })
  assert.deepEqual(resolveInternalPlace({ view: 'internal', internal: 'travel-industry' }),
    { department: TRAVEL_COLLECTION, mark: null, variant: null, place: departmentalPlace(TRAVEL_COLLECTION) })
  assert.deepEqual(resolveInternalPlace({ view: 'internal', internal: 'travel-industry', 'internal-logo': TRAVEL_LOGO }),
    { department: TRAVEL_COLLECTION, mark: TRAVEL_LOGO, variant: null, place: TRAVEL_PLACE })
  assert.deepEqual(resolveInternalPlace({ view: 'internal', internal: 'forests', 'internal-logo': 'forests', 'internal-variant': 'wildfire' }),
    { department: FORESTS, mark: 'forests', variant: 'wildfire', place: forestPlace('forests', 'wildfire') })
})

test('a design’s versions have distinct ids and open with the first', () => {
  for (const logo of FOREST_LOGOS) {
    const ids = forestVersions(logo).map(({ id }) => id)
    assert.equal(new Set(ids).size, ids.length, logo.id)
    assert.equal(ids[0], variantsFor(logo).colours[0].id, logo.id)
    // The default version is the design's own page.
    assert.deepEqual(forestPlace(logo.id, ids[0]), forestPlace(logo.id))
  }
})

test('older and partial addresses are rewritten to the page they mean', () => {
  const cases = [
    // A mark named without its department.
    ['?view=internal&internal-logo=forest-service-emblem', '?view=internal&internal=forests&internal-logo=forest-service-emblem'],
    ['?view=internal&internal-logo=bc-travel-industry-ca-1970', '?view=internal&internal=travel-industry&internal-logo=bc-travel-industry-ca-1970'],
    ['?view=internal&internal-logo=drc-parks', '?view=internal&internal=recreation-conservation&internal-logo=drc-parks'],
    // A department by its collection's id.
    ['?view=internal&internal=specimens-travel-industry', '?view=internal&internal=travel-industry'],
    // A mark, version or department that is not there opens the nearest page that is.
    ['?view=internal&internal=forests&internal-logo=no-such-design', '?view=internal&internal=forests'],
    ['?view=internal&internal=forests&internal-logo=forest-service&internal-variant=no-such-version', '?view=internal&internal=forests&internal-logo=forest-service'],
    ['?view=internal&internal=forests&internal-variant=green', '?view=internal&internal=forests'],
    ['?view=internal&internal=forests&internal-logo=forest-service&internal-variant=colour', '?view=internal&internal=forests&internal-logo=forest-service'],
    ['?view=internal&internal=bc-lands&internal-logo=drc-parks', '?view=internal&internal=bc-lands'],
    ['?view=internal&internal=no-such-department', '?view=internal'],
    ['?view=internal&internal=bc-lands&internal-variant=green', '?view=internal&internal=bc-lands']
  ]
  for (const [from, to] of cases) assert.equal(rewritten(from), to, from)
})

test('a rewrite keeps the rest of the address, and leaves other views alone', () => {
  const url = internalPlaceUrl(`${BASE}?theme=dark&view=internal&internal-logo=forests#top`)
  assert.equal(url.pathname, '/PofBC/')
  assert.equal(url.searchParams.get('theme'), 'dark')
  assert.equal(url.searchParams.get('internal'), 'forests')
  assert.equal(url.hash, '#top')
  assert.equal(internalPlaceUrl(`${BASE}?view=gallery&internal=forests`), null)
})
