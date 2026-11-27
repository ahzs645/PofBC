import { test } from 'node:test'
import assert from 'node:assert/strict'
import { collectionById } from './collections.js'
import { gallerySections } from './gallerySearch.js'
import {
  PRESENT_YEAR, allLogosOf, currentMarkOf, datedMarksOf, documentedCounts, firstMarkYear, logosInYear, organizationStatus, yearsOf
} from './galleryModes.js'

test('date texts read as the years they name, and no more', () => {
  assert.deepEqual(yearsOf('1961–1990'), { from: 1961, to: 1990, open: false })
  assert.deepEqual(yearsOf('1972–73 synopsis and 1973 report'), { from: 1972, to: 1973, open: false })
  assert.deepEqual(yearsOf('Seen 2023/24'), { from: 2023, to: 2024, open: false })
  // A month is not a range.
  assert.deepEqual(yearsOf('Seen 2024-04'), { from: 2024, to: 2024, open: false })
  assert.deepEqual(yearsOf('Seen 2025-09-18'), { from: 2025, to: 2025, open: false })
  assert.deepEqual(yearsOf('2016–present'), { from: 2016, to: PRESENT_YEAR, open: true })
  assert.deepEqual(yearsOf('?–1996'), { from: null, to: 1996, open: false })
  assert.deepEqual(yearsOf('2003–?'), { from: 2003, to: null, open: false })
  assert.equal(yearsOf('Logo dates unestablished'), null)
  assert.equal(yearsOf('Historical design · reproduced 2011'), null)
  assert.equal(yearsOf('Expo 86 years'), null)
})

test('an organization’s status rests on a stated source', () => {
  assert.equal(organizationStatus(collectionById('bc-hydro')).status, 'current')
  assert.equal(organizationStatus(collectionById('recreation-conservation')).status, 'former')
  for (const section of gallerySections('')) {
    for (const collection of section.collections) {
      const { status, reason } = organizationStatus(collection)
      assert.ok(['current', 'former', 'unconfirmed'].includes(status))
      assert.ok(reason)
    }
  }
})

test('BC Hydro’s timeline shows the Rimmer signature in 1975 and a later mark today', () => {
  const hydro = collectionById('bc-hydro')
  const [in1975] = logosInYear([hydro], 1975)
  assert.ok(in1975.documented)
  assert.ok(in1975.marks.every(({ from, to }) => from <= 1975 && 1975 <= to))
  const [today] = logosInYear([hydro], PRESENT_YEAR)
  assert.ok(today)
  assert.ok(today.marks[0].from > 1990)
})

test('a former body is not carried past its end, and undated marks are not placed', () => {
  const department = collectionById('recreation-conservation')
  assert.equal(logosInYear([department], 1990).length, 0)
  assert.equal(logosInYear([department], 1972)[0].marks.length, 6) // the five squares and the 1972–73 oval
  const all = gallerySections('').flatMap(({ collections }) => collections)
  for (const collection of all) {
    for (const mark of datedMarksOf(collection)) assert.ok(mark.from <= mark.to, `${mark.entry.id} ends before it starts`)
  }
  // Documented-only never shows a carried mark.
  assert.ok(logosInYear(all, 2010, { documentedOnly: true }).every(({ documented }) => documented))
  const start = firstMarkYear(all)
  assert.ok(start > 1800 && start < 1950)
  const counts = documentedCounts(all, start, PRESENT_YEAR)
  assert.equal(counts.length, PRESENT_YEAR - start + 1)
  assert.equal(counts[2010 - start], logosInYear(all, 2010, { documentedOnly: true }).length)
})

test('all logos lists each mark once', () => {
  const all = gallerySections('').flatMap(({ collections }) => collections)
  const logos = allLogosOf(all)
  assert.equal(new Set(logos.map(({ entry }) => entry.id)).size, logos.length)
  assert.ok(logos.length > 1000)
})

test('today’s card shows a mark dated to the present, or leaves the collection’s cover', () => {
  const all = gallerySections('').flatMap(({ collections }) => collections)
  for (const collection of all) {
    const mark = currentMarkOf(collection)
    if (mark) assert.ok(datedMarksOf(collection).some(({ entry, open }) => entry === mark && open))
  }
})
