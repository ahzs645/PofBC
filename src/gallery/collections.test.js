// Every mark in the gallery says what it is, and none claims more than has been documented.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  APPLICABILITY, FIDELITY, GALLERY_COLLECTIONS, PROVENANCE, RIGHTS, collectionById, entriesOf, findGalleryEntry
} from './collections.js'
import { ENDORSED_2019 } from './endorsed2019.js'

const everyEntry = GALLERY_COLLECTIONS.flatMap(entriesOf)

test('the 2019 endorsed marks share the BC Mark collection and retain every source version', () => {
  const collection = collectionById('bc-mark')
  assert.equal(collectionById('collected-endorsed-marks-2019'), collection)
  assert.ok(!GALLERY_COLLECTIONS.some(({ id }) => id === 'collected-endorsed-marks-2019'))
  const section = collection.artworkSections.find(({ id }) => id === ENDORSED_2019.id)
  assert.equal(section.entries.length, 3)
  for (const asset of ENDORSED_2019.assets) {
    const entry = findGalleryEntry(asset.id)
    assert.equal(entry.id, asset.variantOf ?? asset.id)
    assert.ok(section.entries.includes(entry))
    assert.ok(entriesOf(collection).includes(entry))
    assert.ok((entry.versions ?? [entry.asset]).includes(asset))
  }
})

test('every entry has a complete identity record, in the gallery’s own vocabulary', () => {
  assert.ok(everyEntry.length > 0)
  for (const { id, identity } of everyEntry) {
    assert.ok(identity, `${id} has no identity record`)
    assert.ok(identity.provenance in PROVENANCE, `${id}: provenance ${identity.provenance}`)
    assert.ok(identity.fidelity in FIDELITY, `${id}: fidelity ${identity.fidelity}`)
    assert.ok(identity.applicability?.kind in APPLICABILITY, `${id}: applicability ${identity.applicability?.kind}`)
    assert.ok(identity.applicability.years?.trim(), `${id}: applicability has no years`)
    assert.ok(identity.applicability.note?.trim(), `${id}: applicability has no note`)
    assert.ok(identity.rights?.status in RIGHTS, `${id}: rights ${identity.rights?.status}`)
    assert.ok(identity.rights.note?.trim(), `${id}: rights have no note`)
  }
})

test('permission for the BCTS downloads is confined to the recovered brochure artwork', () => {
  for (const { id, identity } of everyEntry) {
    if (id === 'bcts-2004-brochure') {
      assert.equal(identity.rights.status, 'permitted')
      assert.match(identity.rights.note, /SVG.*PNG/)
      continue
    }
    assert.notEqual(identity.rights.status, 'permitted', `${id} claims permission`)
    assert.match(identity.rights.note, /No permission/, `${id} does not say plainly that there is none`)
  }
})

test('an era’s record is inherited by marks without their own source record', () => {
  for (const collection of GALLERY_COLLECTIONS) {
    for (const era of collection.eras ?? []) {
      if (!era.identity) continue
      for (const entry of era.entries) {
        if (entry.kind !== 'collected') assert.equal(entry.identity, era.identity, entry.id)
      }
    }
  }
})

test('BC Hydro For Generations keeps both dated guide colourways under the original design', () => {
  const specimen = findGalleryEntry('bc-hydro-for-generations-2012')
  assert.equal(specimen.identity.provenance, 'extracted_from_official_vector')
  assert.equal(specimen.identity.applicability.years, '2012 and 2015')
  assert.equal(specimen.identity.applicability.kind, 'dated_specimen')
  assert.deepEqual(specimen.versions.map(({ specimenDate }) => specimenDate), ['2012', '2015'])
})

test('the reconstructed 1961 signatures own up to their substitute lettering', () => {
  const rimmer = GALLERY_COLLECTIONS.find((collection) => collection.id === 'bc-hydro').eras[0]
  assert.equal(rimmer.identity.provenance, 'reconstructed')
  assert.equal(rimmer.identity.fidelity, 'font substitution')
})

test('an undated mark is unknown, not estimated', () => {
  const remake = everyEntry.find((entry) => entry.id === 'prepared-bc')
  assert.equal(remake.identity.applicability.kind, 'unknown')
})

test('a mark dated by where it was seen says so, rather than claiming an adoption', () => {
  const earlier = everyEntry.find((entry) => entry.id === 'bcts-wordmark-earlier')
  assert.equal(earlier.identity.applicability.kind, 'first_observation')
  const bcts = GALLERY_COLLECTIONS.find((collection) => collection.id === 'bcts')
  assert.deepEqual(bcts.eras.map((era) => era.entries.length > 0), [true, true, false, true])
})

test('grouped gallery versions resolve to one page and retain their own source or editor choice', () => {
  const cases = [
    ['icbc', 'icbc-rounded-blue', 'icbc-rounded-orange'],
    ['bc-hydro', 'bc-hydro-current-colour', 'bc-hydro-current-reverse'],
    ['bc-hydro', 'bc-hydro-current-symbol', 'bc-hydro-current-symbol-border'],
    ['collected-island-health', 'source-island-health-island-health-svg', 'source-island-health-island-health-white-svg'],
    ['collected-legal-aid-bc', 'source-legal-aid-bc-legal-aid-bc-horizontal-svg', 'source-legal-aid-bc-legal-aid-bc-svg'],
    ['collected-interior-university-society', 'ius-ius-print-colour', 'ius-ius-print-reversed-panel']
  ]
  for (const [collection, main, alternate] of cases) {
    const entries = entriesOf(collectionById(collection))
    const page = findGalleryEntry(main)
    assert.equal(findGalleryEntry(alternate), page)
    assert.equal(entries.filter((e) => e.id === main || e.id === alternate).length, 1)
    assert.ok((page.versions ?? page.editorVersions).some((v) => v.id === alternate))
  }
  assert.notEqual(findGalleryEntry('bc-hydro-current-signage'), findGalleryEntry('bc-hydro-current-colour'))
  assert.notEqual(findGalleryEntry('source-legal-aid-bc-legal-aid-bc-vertical-svg'), findGalleryEntry('source-legal-aid-bc-legal-aid-bc-svg'))
})
