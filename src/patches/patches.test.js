// The patch library comes from the Patcher submodule (vendor/patcher/library). These check that it
// is there and hangs together as the Patches view expects: every patch filed under exactly one
// organization, every organization under a sector the view lists, and every patch joining back from
// its stored file and shared parts into the atlas's drawing (or the supplied one), byte for byte.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'

const LIBRARY = new URL('../../vendor/patcher/library/', import.meta.url)
const MANIFEST = new URL('manifest.json', LIBRARY)
const JOIN = new URL('../src/library-join.js', LIBRARY)

test('the Patcher submodule is checked out', () => {
  assert.ok(existsSync(MANIFEST), 'vendor/patcher is empty: run `git submodule update --init --recursive`')
})

const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : null
const read = (path) => readFileSync(new URL(path, LIBRARY), 'utf8')

test('every organization belongs to a listed sector and counts its own designs by collection', { skip: !manifest }, () => {
  const sectors = new Set(manifest.sectors.map((sector) => sector.id))
  const collections = new Set(manifest.collections.map((collection) => collection.id))
  for (const org of manifest.orgs) {
    assert.ok(sectors.has(org.sector), `${org.id}: unknown sector ${org.sector}`)
    assert.ok(org.patches.length > 0, `${org.id}: empty`)
    for (const id of collections) assert.equal(org.counts[id], org.patches.filter((p) => p.collection === id).length, `${org.id}: ${id} count`)
  }
  assert.equal(manifest.summary.orgs, manifest.orgs.length)
})

test('badges are their own collection, and what orgs.json leaves out stays out', { skip: !manifest }, () => {
  const designs = manifest.orgs.flatMap((org) => org.patches)
  assert.ok(manifest.collections.some((c) => c.id === 'badges'), 'the library has no badges collection')
  for (const design of designs) {
    const badge = /badge/i.test(design.medium)
    assert.equal(design.collection, badge ? 'badges' : 'patches', `${design.id} (${design.medium})`)
  }
  const kept = new Set(designs.map((d) => d.id))
  for (const gone of manifest.excluded) assert.ok(!kept.has(gone.id), `${gone.id} is excluded but still in the library`)
  // Another photograph of a kept design is merged into it, not listed twice.
  for (const { id, into } of manifest.merged) {
    assert.ok(!kept.has(id), `${id} is merged into ${into} but still listed`)
    assert.ok(designs.find((d) => d.id === into)?.merged.includes(id), `${into} doesn't record ${id}`)
  }
  // The Province's identity, BC Timber Sales and the corporate logos are not patches.
  const orgs = new Set(manifest.orgs.map((org) => org.id))
  for (const id of ['province-of-bc', 'bc-timber-sales', 'bc-transit', 'icbc']) assert.ok(!orgs.has(id), `${id} should be left out`)
})

test('every patch is filed once, under its own folder, and nothing is left unsorted', { skip: !manifest }, () => {
  const ids = manifest.orgs.flatMap((org) => org.patches.map((patch) => patch.id))
  assert.equal(new Set(ids).size, ids.length, 'a patch is listed twice')
  assert.equal(ids.length, manifest.summary.designs)
  assert.equal(manifest.summary.unsorted, 0, 'some patches matched no organization in orgs.json')
  for (const org of manifest.orgs) {
    for (const patch of org.patches) {
      assert.ok(patch.svg.startsWith(`${org.id}/`), `${patch.id}: filed outside ${org.id}/`)
      assert.ok(existsSync(new URL(patch.svg, LIBRARY)), `${patch.id}: ${patch.svg} is missing`)
      assert.ok(patch.preview && existsSync(new URL(patch.preview, LIBRARY)), `${patch.id}: preview missing`)
    }
  }
})

test('every patch joins back into the atlas drawing, byte for byte', { skip: !manifest }, async () => {
  const { joinSvg, unwrapBlock } = await import(JOIN)
  const blockFile = new Map(manifest.shared.blocks.map((block) => [block.id, block.file]))
  const bundleFile = new Map(manifest.shared.bundles.map((bundle) => [bundle.name, bundle.file]))
  for (const org of manifest.orgs) {
    for (const patch of org.patches) {
      // Only the parts the manifest says this patch needs, as the view fetches them.
      const blocks = new Map(patch.blocks.map((id) => [id, unwrapBlock(id, read(blockFile.get(id)))]))
      const paths = Object.assign({}, ...patch.bundles.map((name) => JSON.parse(read(bundleFile.get(name)))))
      const joined = Buffer.from(joinSvg(read(patch.svg), { block: (id) => blocks.get(id), path: (id) => paths[id] }), 'utf8')
      assert.equal(joined.length, patch.bytes, `${patch.id}: size`)
      assert.equal(createHash('sha256').update(joined).digest('hex'), patch.sha256, `${patch.id}: SHA-256`)
    }
  }
})

test('variant groups name designs in the library, each in one group, in one collection', { skip: !manifest }, () => {
  const designs = new Map(manifest.orgs.flatMap((org) => org.patches.map((p) => [p.id, p])))
  for (const group of manifest.variants) {
    assert.ok(group.members.length > 1, `${group.id}: a group needs two variants`)
    for (const { id, name } of group.members) {
      assert.equal(designs.get(id)?.group, group.id, `${id} should be in ${group.id}`)
      assert.equal(designs.get(id).variant, name)
    }
    assert.equal(new Set(group.members.map(({ id }) => designs.get(id).collection)).size, 1, `${group.id} spans collections`)
  }
  // The scenic arch and its integrated Ranger edition are one card.
  assert.deepEqual(manifest.variants.find((g) => g.id === 'parks-scenic-arch')?.members.map((m) => m.id), ['S30-O04', 'S27-O04'])
})

test('atlas entries absorbed into a supplied design are gone, and the design says so', { skip: !manifest }, () => {
  const designs = new Map(manifest.orgs.flatMap((org) => org.patches.map((p) => [p.id, p])))
  for (const { id, into } of manifest.absorbed) {
    assert.ok(!designs.has(id), `${id} is absorbed into ${into} but still listed`)
    assert.ok(designs.get(into)?.supplied, `${into} isn't a supplied design`)
    assert.ok(designs.get(into).absorbs.includes(id), `${into} doesn't record ${id}`)
  }
  // The atlas's Forest Service and Wildfire Service ovals are PofBC's Forest Ovals, one card per design.
  const ovals = ['forest-service-oval', 'forests-oval', 'long-ministry-oval', 'forest-service-yellow-sky', 'forest-service-green-gold']
  for (const id of ovals) assert.ok(manifest.variants.some((g) => g.id === id), `${id} is missing`)
  for (const id of ['R22-O01', 'R13-O01', 'S43-O01', 'S58-O05', 'S47-O01']) assert.ok(manifest.absorbed.some((a) => a.id === id), `${id} should be absorbed`)
  assert.ok(!manifest.orgs.some((org) => org.id === 'bc-wildfire-service'), 'every Wildfire Service oval is a Forest Oval variant now')
})
