import { test } from 'node:test'
import assert from 'node:assert/strict'
import { identitySubjectById } from './identityCoverage.js'
import { TOURISM_SECTOR_RECORDS } from './tourismSectorPartners.js'
import { findGalleryEntry } from './collections.js'

test('Fishing BC separates partnership formation and the branded launch from dated raster use', () => {
  const record = TOURISM_SECTOR_RECORDS.find(({ id }) => id === 'fishing-bc')
  assert.equal(record.from, 2016)
  assert.match(record.history, /partnership to 2016.*branded website and video in May 2017/)
  const subject = identitySubjectById(record.id)
  assert.ok(subject.sources.some(({ url }) => url.endsWith('Sept_Oct_2021.pdf#page=7')))
  assert.ok(subject.sources.some(({ url }) => url.endsWith('Nov_Dec_2021.pdf#page=21')))
  const design = findGalleryEntry('fishing-bc-appendix-2024')
  assert.ok(design.versions.some(({ id, format, isVector }) => id === 'fishing-bc-white-outline-site' && format === 'png' && !isVector))
})

test('PSBSBC links the current wordmark without replacing the report specimen', () => {
  const subject = identitySubjectById('prevent-shaken-baby-syndrome-bc')
  assert.ok(subject.sources.some(({ title, url }) => /monochrome header PNG/.test(title) && url.endsWith('_Logo%20(2).png')))
  assert.match(subject.note, /wider monochrome PSBSBC wordmark/)
  const design = findGalleryEntry('psbsbc-2024')
  assert.equal(design.asset.format, 'png')
  assert.equal(design.asset.isVector, false)
})
