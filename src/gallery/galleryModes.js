// The gallery's other ways through its collections: every logo at once, the organizations that
// stand today, and a timeline that shows which logo each organization was using in a year.
//
// Everything here reads the dates the collections already give, as text ("1961–1990", "Seen
// 2015", "1972–73 synopsis", "2016–present"). Nothing is inferred beyond two stated rules:
//   · a mark is "documented" in a year its own dates cover;
//   · a mark is "carried forward" past its last documented year only while its organization is
//     known to stand (its dates run to the present, or end later), and only until a later mark of
//     the same organization is documented. The timeline says which of the two each card is.
// A mark whose dates are unestablished is left off the timeline and counted, not placed.

import { GALLERY_COLLECTIONS, entriesOf } from './collections.js'
import { IDENTITY_COVERAGE } from './identityCoverage.js'
import { nodesOf } from './collectedCollections.js'
import { CURRENT_AS_OF, CURRENT_BODIES } from '../government/currentData.js'

export const PRESENT_YEAR = Number(CURRENT_AS_OF.slice(0, 4))

// A year, then optionally its range's end: "1972–73" and "2023/24" (two digits after an en dash or a
// slash), or "1961–1990" (four after either dash). "2024-04" is a month, not a range.
const YEAR = /(1[89]\d{2}|20\d{2})(?:\s*[–/]\s*(\d{2})(?!\d)|\s*[–-]\s*(1[89]\d{2}|20\d{2}))?/g
const UNDATED = /unestablished|undated|unknown|reproduced/i

/**
 * The years a date text spans, or null when it gives none. `open` is a span that runs to the
 * present; `openStart` and `openEnd` are a "?" at either end ("?–1996", "2003–?").
 * @returns {{from: number|null, to: number|null, open: boolean} | null}
 */
export const yearsOf = (text) => {
  if (!text || UNDATED.test(text)) return null
  const years = []
  for (const [, first, short, long] of String(text).matchAll(YEAR)) {
    years.push(Number(first))
    if (short) years.push(Number(first.slice(0, 2) + short))
    if (long) years.push(Number(long))
  }
  const open = /present|today/i.test(text)
  if (!years.length) return null
  const openStart = /^\s*\?\s*[–-]/.test(text)
  const openEnd = /[–-]\s*\?\s*$/.test(text)
  return {
    from: openStart ? null : Math.min(...years),
    to: open ? PRESENT_YEAR : openEnd ? null : Math.max(...years),
    open
  }
}

// ── Whose each collection is, and whether that organization stands today ─────────────────────────

const ownCollection = (subject, collection) => subject.collectionIds?.includes(collection.id) ||
  collection.id === `collected-${subject.id}` || nodesOf(collection).includes(subject.entryOwner ?? subject.id)

let subjectsByCollection
const subjectOf = (collection) => {
  if (!subjectsByCollection) {
    subjectsByCollection = new Map()
    for (const subject of IDENTITY_COVERAGE) {
      for (const owned of subject.collections) {
        if (ownCollection(subject, owned) && !subjectsByCollection.has(owned.id)) subjectsByCollection.set(owned.id, subject)
      }
    }
  }
  return subjectsByCollection.get(collection.id)
}

const currentNodes = new Set(CURRENT_BODIES.map(({ id }) => id))

/**
 * Whether a collection's organization stands today, and what says so.
 * @returns {{status: 'current'|'former'|'unconfirmed', reason: string}}
 */
export const organizationStatus = (collection) => {
  const life = yearsOf(collection.years)
  const subject = subjectOf(collection)
  if (life?.open) return { status: 'current', reason: `Its dates run to the present (${collection.years}).` }
  if (life?.to && life.to < PRESENT_YEAR) return { status: 'former', reason: `Its dates end in ${life.to}.` }
  if (subject?.current === true) return { status: 'current', reason: 'The identity register records it as current.' }
  if (subject?.current === false || subject?.to) return { status: 'former', reason: 'The identity register records it as a former body.' }
  if (subject?.municipal || subject?.regionalDistrict || subject?.schoolDistrict) {
    return { status: 'current', reason: 'A local government or school district in the register.' }
  }
  if (currentNodes.has(collection.graphNode)) return { status: 'current', reason: 'In the government atlas as a body today.' }
  return { status: 'unconfirmed', reason: 'No source here says whether it stands today.' }
}

// ── Dated marks ──────────────────────────────────────────────────────────────────────────────────

const datedCache = new Map()

/** A collection's marks with the years their own dates (or their era's) give, oldest first. */
export const datedMarksOf = (collection) => {
  if (datedCache.has(collection.id)) return datedCache.get(collection.id)
  const placed = (collection.eras ?? [{ years: null, entries: collection.entries ?? [] }]).flatMap((era) => era.entries.map((entry) => {
    const span = yearsOf(entry.years) ?? yearsOf(entry.identity?.applicability?.years) ?? yearsOf(era.years)
    return span?.from ? { entry, from: span.from, to: span.to ?? span.from, open: span.open } : null
  })).filter(Boolean).sort((a, b) => a.from - b.from)
  datedCache.set(collection.id, placed)
  return placed
}

/**
 * The mark to show for an organization today: the newest one whose dates run to the present, or
 * else none, so its card keeps the cover its collection chose (often today's logo, left undated).
 */
export const currentMarkOf = (collection) => datedMarksOf(collection).filter(({ open }) => open).at(-1)?.entry

/**
 * Each organization's logo in a year: those its own dates place there ("documented"), or else its
 * last earlier mark, carried forward while the organization is known to stand ("carried").
 * @param {object[]} collections
 * @param {number} year
 * @param {{documentedOnly?: boolean}} [options]
 */
export const logosInYear = (collections, year, { documentedOnly = false } = {}) => {
  const shown = []
  for (const collection of collections) {
    const life = yearsOf(collection.years)
    if (life?.from && year < life.from) continue
    if (life?.to && year > life.to) continue
    const marks = datedMarksOf(collection)
    const documented = marks.filter(({ from, to }) => from <= year && year <= to)
    if (documented.length) {
      shown.push({ collection, marks: documented, documented: true })
      continue
    }
    if (documentedOnly) continue
    const earlier = marks.filter(({ to }) => to < year).at(-1)
    const stands = life?.open || (life?.to && year <= life.to) || organizationStatus(collection).status === 'current'
    if (earlier && stands) shown.push({ collection, marks: [earlier], documented: false })
  }
  return shown
}

/** How many organizations have a documented logo in each year, for the timeline's strip. */
export const documentedCounts = (collections, from, to) => {
  const counts = new Array(to - from + 1).fill(0)
  for (const collection of collections) {
    // The same bounds logosInYear keeps: nothing before the organization begins or after it ends.
    const life = yearsOf(collection.years)
    const first = Math.max(from, life?.from ?? from)
    const last = Math.min(to, life?.to ?? to)
    const years = new Set()
    for (const mark of datedMarksOf(collection)) {
      for (let year = Math.max(mark.from, first); year <= Math.min(mark.to, last); year++) years.add(year)
    }
    for (const year of years) counts[year - from]++
  }
  return counts
}

/** The first year any of these collections has a dated mark. */
export const firstMarkYear = (collections) => Math.min(...collections.flatMap((collection) =>
  datedMarksOf(collection).map(({ from }) => from)), PRESENT_YEAR)

/** Every mark in these collections, each with the collection it opens in. */
export const allLogosOf = (collections) => {
  const seen = new Set()
  return collections.flatMap((collection) => entriesOf(collection)
    .filter((entry) => !seen.has(entry.id) && seen.add(entry.id))
    .map((entry) => {
      const span = datedMarksOf(collection).find((mark) => mark.entry === entry)
      return { entry, collection, from: span?.from ?? null }
    }))
}

export const GALLERY_MODES = [
  { value: '', label: 'Collections', title: 'Each organization’s collection, by type' },
  { value: 'all', label: 'All logos', title: 'Every logo in the gallery at once' },
  { value: 'current', label: 'Current organizations', title: 'Organizations that stand today, with their newest logo' },
  { value: 'timeline', label: 'Timeline', title: 'Scrub through the years to see each organization’s logo at the time' }
]

export const isGalleryMode = (value) => GALLERY_MODES.some((mode) => mode.value === value)

// For tests and the gallery's own counts.
export const indexedCollections = () => GALLERY_COLLECTIONS.filter(({ showInGalleryIndex }) => showInGalleryIndex !== false)
