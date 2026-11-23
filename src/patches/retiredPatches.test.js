import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { FOREST_LOGOS } from '../internal/forestLogos.js'
import { RETIRED_PATCHES, retiredPatchUrl } from './retiredPatches.js'

const MANIFEST = new URL('../../vendor/patcher/library/manifest.json', import.meta.url)
const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : null

test('an old link to the yellow-sky patch opens the internal Forests logo', () => {
  for (const id of ['FO-yellow-sky', 'FO-yellow-sky-cream', 'FO-yellow-sky-dark', 'S05-O01']) {
    const url = retiredPatchUrl(`https://example.test/PofBC/?view=patches&patch=${id}&org=bc-forest-service&q=oval`)
    assert.equal(url?.search, '?view=internal&internal=forests&internal-logo=forest-service-yellow-sky', id)
  }
  assert.equal(retiredPatchUrl('https://example.test/?view=badges&patch=FO-yellow-sky')?.searchParams.get('view'), 'internal')
  assert.equal(retiredPatchUrl('https://example.test/?view=gallery&patch=FO-yellow-sky'), null)
  assert.equal(retiredPatchUrl('https://example.test/?view=patches'), null)
})

test('a dropped green-and-gold recolour opens the full-colour patch', () => {
  for (const id of ['FO-green-gold-black', 'FO-green-gold-black-gold']) {
    assert.equal(retiredPatchUrl(`https://example.test/?view=patches&patch=${id}&family=x`)?.search, '?view=patches&patch=FO-green-gold')
  }
  assert.equal(retiredPatchUrl('https://example.test/?view=patches&patch=FO-green-gold-light-band'), null)
})

test('each redirect leads somewhere that exists, and no retired id is still in the library', { skip: !manifest }, () => {
  const patches = new Set(manifest.orgs.flatMap((org) => org.patches.map(({ id }) => id)))
  const moved = new Set([...manifest.merged, ...(manifest.absorbed ?? [])].map(({ id }) => id))
  for (const [id, to] of Object.entries(RETIRED_PATCHES)) {
    assert.ok(!patches.has(id) && !moved.has(id), `${id} is still in the library`)
    if (to.view === 'internal') assert.ok(FOREST_LOGOS.some((logo) => logo.id === to['internal-logo']), to['internal-logo'])
    else assert.ok(patches.has(to.patch), to.patch)
  }
})
