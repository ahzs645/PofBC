// Every mark in the gallery says what it is, and none claims more than has been documented.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  APPLICABILITY, FIDELITY, GALLERY_COLLECTIONS, PROVENANCE, RIGHTS, entriesOf
} from './collections.js'

const everyEntry = GALLERY_COLLECTIONS.flatMap(entriesOf)

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

test('no entry claims its rights are cleared, since none has documented permission', () => {
  for (const { id, identity } of everyEntry) {
    assert.notEqual(identity.rights.status, 'permitted', `${id} claims permission`)
    assert.match(identity.rights.note, /No permission/, `${id} does not say plainly that there is none`)
  }
})

test('an era’s record is inherited by every mark in it', () => {
  for (const collection of GALLERY_COLLECTIONS) {
    for (const era of collection.eras ?? []) {
      if (!era.identity) continue
      for (const entry of era.entries) assert.equal(entry.identity, era.identity, entry.id)
    }
  }
})

test('the reconstructed 1961 signatures own up to their substitute lettering', () => {
  const rimmer = GALLERY_COLLECTIONS.find((collection) => collection.id === 'bc-hydro').eras[0]
  assert.equal(rimmer.identity.provenance, 'reconstructed')
  assert.equal(rimmer.identity.fidelity, 'font substitution')
})

test('an undated mark is unknown, not estimated', () => {
  const earlier = everyEntry.find((entry) => entry.id === 'bcts-wordmark-earlier')
  assert.equal(earlier.identity.applicability.kind, 'unknown')
})
