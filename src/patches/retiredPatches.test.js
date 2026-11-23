import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { FOREST_LOGOS } from '../internal/forestLogos.js'
import { RETIRED_PATCH_GROUPS, RETIRED_PATCH_IDS, isRetiredPatch, retiredPatchUrl, withoutRetiredPatches } from './retiredPatches.js'

const MANIFEST = new URL('../../vendor/patcher/library/manifest.json', import.meta.url)
const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : null

test('an old link to the yellow-sky patch opens the internal Forests logo', () => {
  for (const id of ['FO-yellow-sky', 'FO-yellow-sky-cream', 'FO-yellow-sky-dark', 'S05-O01']) {
    const url = retiredPatchUrl(`https://example.test/PofBC/?view=patches&patch=${id}&org=bc-forest-service&q=oval`)
    assert.equal(url?.search, '?view=internal&internal=forests&internal-logo=forest-service-yellow-sky', id)
  }
  assert.equal(retiredPatchUrl('https://example.test/?view=badges&patch=FO-yellow-sky')?.searchParams.get('view'), 'internal')
  assert.equal(retiredPatchUrl('https://example.test/?view=patches&patch=FO-green-gold-light-band'), null)
  assert.equal(retiredPatchUrl('https://example.test/?view=gallery&patch=FO-yellow-sky'), null)
  assert.equal(retiredPatchUrl('https://example.test/?view=patches'), null)
})

test('each retired card leads to a Forests logo that exists', () => {
  for (const { to } of Object.values(RETIRED_PATCH_GROUPS)) {
    assert.equal(to.view, 'internal')
    assert.ok(FOREST_LOGOS.some(({ id }) => id === to['internal-logo']), to['internal-logo'])
  }
  for (const group of Object.values(RETIRED_PATCH_IDS)) assert.ok(RETIRED_PATCH_GROUPS[group], group)
})

test('the catalogue drops retired patches and any organization they leave empty', () => {
  const sectors = [
    { sector: { id: 'a' }, orgs: [{ id: 'one', patches: [{ id: 'FO-yellow-sky', group: 'forest-service-yellow-sky' }, { id: 'kept' }] }] },
    { sector: { id: 'b' }, orgs: [{ id: 'two', patches: [{ id: 'S05-O01' }] }] }
  ]
  assert.deepEqual(withoutRetiredPatches(sectors), [{ sector: { id: 'a' }, orgs: [{ id: 'one', patches: [{ id: 'kept' }] }] }])
  assert.equal(isRetiredPatch(undefined), false)
})

test('every id that opened a retired card in the library redirects', { skip: !manifest }, () => {
  const patches = manifest.orgs.flatMap((org) => org.patches)
  const retired = patches.filter((patch) => RETIRED_PATCH_GROUPS[patch.group])
  const expected = new Set([
    ...retired.map(({ id }) => id),
    ...retired.flatMap(({ sightings = [] }) => sightings.map(({ id }) => id)),
    ...[...manifest.merged, ...(manifest.absorbed ?? [])].filter(({ into }) => retired.some(({ id }) => id === into)).map(({ id }) => id)
  ])
  assert.ok(retired.length, 'no retired patches found in the library')
  assert.deepEqual([...expected].sort(), Object.keys(RETIRED_PATCH_IDS).sort())
  for (const patch of retired) assert.equal(RETIRED_PATCH_IDS[patch.id], patch.group)
})
