// A one-off's timeline claims no more than its sources, and every mark on it is one the gallery has.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { APPLICABILITY, GALLERY_COLLECTIONS, entriesOf, eraStatus, findGalleryEntry, timelineOf } from './collections.js'
import { COLLECTION_ERAS, TIMELINES } from './timelines.js'

const timelineEras = Object.entries(TIMELINES).flatMap(([key, timeline]) => timeline.eras.map((era) => ({ key, era })))
const collectionEras = Object.entries(COLLECTION_ERAS).flatMap(([key, eras]) => eras.map((era) => ({ key, era })))
const everyEra = [...timelineEras, ...collectionEras]

test('every era says what it is, what its dates rest on, and where they come from', () => {
  for (const { key, era } of everyEra) {
    const where = `${key}/${era.id}`
    for (const field of ['id', 'years', 'label', 'note']) assert.ok(era[field]?.trim(), `${where}: no ${field}`)
    assert.ok(['held', 'generator', 'sought', 'none'].includes(era.status), `${where}: status ${era.status}`)
    assert.ok(era.applicability?.kind in APPLICABILITY, `${where}: applicability ${era.applicability?.kind}`)
    assert.ok(era.applicability.years?.trim() && era.applicability.note?.trim(), `${where}: dates unexplained`)
    assert.ok(era.sources?.length > 0, `${where}: no source`)
    for (const { title, url } of era.sources) {
      assert.ok(title?.trim(), `${where}: a source without a title`)
      assert.match(url, /^https:\/\//, `${where}: ${url}`)
    }
    for (const url of era.seenAt ?? []) assert.match(url, /^https:\/\//, `${where}: ${url}`)
    assert.equal(era.status === 'generator', Boolean(era.generator), `${where}: a generator era says how to open it, and only one does`)
  }
})

test('era ids are unique, since the page scrolls to them', () => {
  const ids = timelineEras.map(({ era }) => era.id)
  const collectionIds = GALLERY_COLLECTIONS.flatMap((collection) => (collection.eras ?? []).map((era) => era.id))
  assert.equal(new Set([...ids, ...collectionIds]).size, ids.length + collectionIds.length)
})

test('a held era names marks the gallery has, and only a held era names any', () => {
  for (const { key, era } of timelineEras) {
    if (era.status === 'held') {
      assert.ok(era.marks?.length > 0, `${key}/${era.id} holds nothing`)
      for (const id of era.marks) assert.ok(findGalleryEntry(id), `${key}/${era.id}: no mark ${id}`)
    } else {
      assert.equal(era.marks, undefined, `${key}/${era.id} is ${era.status} but names marks`)
    }
  }
})

test('every one-off on a timeline is in one of its eras, and resolves to the gallery’s own entry', () => {
  const onTimelines = GALLERY_COLLECTIONS.flatMap(entriesOf).filter((entry) => entry.timeline)
  assert.ok(onTimelines.length > 0)
  for (const entry of onTimelines) {
    const timeline = timelineOf(entry)
    assert.ok(timeline, `${entry.id}: timeline ${entry.timeline} not found`)
    const holding = timeline.eras.filter((era) => era.entries.includes(findGalleryEntry(entry.id)))
    assert.equal(holding.length, 1, `${entry.id} is in ${holding.length} eras of its timeline`)
    for (const era of timeline.eras) assert.equal(eraStatus(era), era.status)
  }
})

test('a date first seen is never promoted to an adoption', () => {
  for (const { key, era } of everyEra) {
    if (era.applicability.kind !== 'first_observation') continue
    assert.doesNotMatch(era.applicability.note, /\badopted\b/i, `${key}/${era.id}`)
  }
})

test('a collection’s researched eras hold its marks exactly where they say they do', () => {
  for (const [key, eras] of Object.entries(COLLECTION_ERAS)) {
    const collection = GALLERY_COLLECTIONS.find((candidate) => candidate.id === key)
    assert.deepEqual(collection.eras.map((era) => era.id), eras.map((era) => era.id), key)
    for (const era of collection.eras) {
      assert.equal(era.entries.length > 0, era.status === 'held', `${key}/${era.id}`)
    }
  }
})
