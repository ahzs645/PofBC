// The patch library comes from the Patcher submodule (vendor/patcher/library). These check that it
// is there and hangs together as the Patches view expects: every patch filed under exactly one
// organization, every organization under a sector the view lists, and every file it names present.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'

const LIBRARY = new URL('../../vendor/patcher/library/', import.meta.url)
const MANIFEST = new URL('manifest.json', LIBRARY)

test('the Patcher submodule is checked out', () => {
  assert.ok(existsSync(MANIFEST), 'vendor/patcher is empty: run `git submodule update --init --recursive`')
})

const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : null

test('every organization belongs to a listed sector and counts its own patches', { skip: !manifest }, () => {
  const sectors = new Set(manifest.sectors.map((sector) => sector.id))
  for (const org of manifest.orgs) {
    assert.ok(sectors.has(org.sector), `${org.id}: unknown sector ${org.sector}`)
    assert.equal(org.count, org.patches.length, `${org.id}: count`)
    assert.ok(org.patches.length > 0, `${org.id}: empty`)
  }
  assert.equal(manifest.summary.orgs, manifest.orgs.length)
})

test('every patch is filed once, under its own folder, and nothing is left unsorted', { skip: !manifest }, () => {
  const ids = manifest.orgs.flatMap((org) => org.patches.map((patch) => patch.id))
  assert.equal(new Set(ids).size, ids.length, 'a patch is listed twice')
  assert.equal(ids.length, manifest.summary.patches)
  assert.equal(manifest.summary.unsorted, 0, 'some patches matched no organization in orgs.json')
  for (const org of manifest.orgs) {
    for (const patch of org.patches) {
      assert.ok(patch.svg.startsWith(`${org.id}/`), `${patch.id}: filed outside ${org.id}/`)
      assert.ok(existsSync(new URL(patch.svg, LIBRARY)), `${patch.id}: ${patch.svg} is missing`)
      if (patch.preview) assert.ok(existsSync(new URL(patch.preview, LIBRARY)), `${patch.id}: ${patch.preview} is missing`)
    }
  }
})
