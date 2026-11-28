import { test } from 'node:test'
import assert from 'node:assert/strict'
import { COLLECTED_COLLECTIONS } from './collectedCollections.js'
import { GALLERY_COLLECTIONS, collectionById, entriesOf, findGalleryEntry } from './collections.js'
import { MARK_ROLES, MARK_ROLE_LABELS, SECONDARY_SECTIONS, identityFirst, isIdentityMark, markRoleOf, withMarkRoles } from './markRoles.js'

const coverEntryOf = (collection) => entriesOf(collection).find(({ id }) => id === collection.cover) ?? findGalleryEntry(collection.cover)

test('every classified design is held, with a known role and the evidence for it', () => {
  const held = new Set(GALLERY_COLLECTIONS.flatMap(entriesOf).flatMap((entry) =>
    [entry.id, entry.asset?.id, ...(entry.versions ?? []).map(({ id }) => id)]))
  for (const [id, { role, evidence }] of Object.entries(MARK_ROLES)) {
    assert.ok(held.has(id), `${id}: not a held design`)
    assert.ok(role !== 'identity' && Object.hasOwn(MARK_ROLE_LABELS, role), `${id}: unknown role ${role}`)
    assert.ok(SECONDARY_SECTIONS.some(({ roles }) => roles.includes(role)), `${id}: no section for ${role}`)
    assert.ok(evidence?.length > 10, `${id}: says what shows its role`)
  }
})

test('a collection’s cover is an identity design whenever it holds one', () => {
  for (const collection of [...GALLERY_COLLECTIONS, ...COLLECTED_COLLECTIONS]) {
    const entries = entriesOf(collection) ?? []
    if (!entries.some(isIdentityMark)) continue
    const cover = coverEntryOf(collection)
    if (cover) assert.ok(isIdentityMark(cover), `${collection.id}: cover ${cover.id} is a ${markRoleOf(cover)} mark`)
    const specimen = collection.shelfSpecimen && entries.find(({ id }) => id === collection.shelfSpecimen)
    if (specimen) assert.ok(isIdentityMark(specimen), `${collection.id}: shelf specimen ${specimen.id} is a ${markRoleOf(specimen)} mark`)
  }
})

test('secondary marks never sort before a collection’s identity designs', () => {
  const identityLeads = (entries, where) => {
    const firstSecondary = entries.findIndex((entry) => !isIdentityMark(entry))
    if (firstSecondary < 0) return
    assert.ok(entries.slice(firstSecondary).every((entry) => !isIdentityMark(entry)),
      `${where}: ${entries.map((entry) => `${entry.id}:${markRoleOf(entry)}`).join(', ')}`)
  }
  for (const collection of [...GALLERY_COLLECTIONS, ...COLLECTED_COLLECTIONS]) {
    if (collection.entries) identityLeads(collection.entries, collection.id)
    for (const era of collection.eras ?? []) identityLeads(era.entries, `${collection.id} ${era.id}`)
    // Each loose secondary mark is in a section of its own kind, shown after the identity designs.
    if (collection.eras) continue
    const placed = new Set((collection.artworkSections ?? []).flatMap(({ entries }) => entries))
    for (const entry of collection.entries ?? []) {
      if (isIdentityMark(entry)) continue
      assert.ok(placed.has(entry), `${collection.id}: ${entry.id} is in a section`)
    }
    for (const section of (collection.artworkSections ?? []).filter(({ secondary }) => secondary)) {
      const { roles } = SECONDARY_SECTIONS.find(({ id }) => id === section.id)
      assert.ok(section.entries.every((entry) => roles.includes(markRoleOf(entry))), `${collection.id}: ${section.id}`)
    }
  }
})

test('FESBC leads with its logo-kit identity and shows its 10th-anniversary mark apart', () => {
  const collection = collectionById('collected-forest-enhancement-society')
  const kit = ['source-forest-enhancement-society-fesbc-horizontal-eps', 'source-forest-enhancement-society-fesbc-vertical-eps']
  const anniversary = 'source-forest-enhancement-society-fesbc-10th-anniversary-svg'
  assert.equal(collection.cover, kit[0], 'the horizontal logo leads')
  assert.ok(kit.includes(collection.entries[0].id), collection.entries[0].id)
  assert.deepEqual(collection.entries.slice(0, 2).map(({ id }) => id).sort(), [...kit].sort())
  const section = collection.artworkSections.find(({ entries }) => entries.some(({ id }) => id === anniversary))
  assert.equal(section?.id, 'secondary-commemorative')
  assert.equal(section.label, 'Anniversary and commemorative marks')
  assert.ok(section.secondary)
  assert.equal(collection.entries.find(({ id }) => id === anniversary).markRole, 'commemorative')
  // Presentation only: the design keeps its ID and file.
  assert.equal(findGalleryEntry(anniversary).asset.file, 'identity-collected/forest-enhancement-society/fesbc-10th-anniversary.svg')
})

test('a collection holding only secondary marks keeps one as its cover, labelled as such', () => {
  const only = (id) => ({ id, label: id, asset: { id }, markRole: 'commemorative' })
  const collection = withMarkRoles({ id: 'only-anniversary', cover: 'a', entries: [only('a'), only('b')] })
  assert.equal(collection.cover, 'a')
  assert.equal(collection.entries[0].markRole, 'commemorative')
  assert.deepEqual(collection.artworkSections.map(({ id }) => id), ['secondary-commemorative'])
})

test('withMarkRoles moves a secondary cover to the first identity design and keeps body sections', () => {
  const identity = (id) => ({ id, asset: { id } })
  const campaign = { id: 'c', asset: { id: 'c', markRole: 'campaign' } }
  const kept = { id: 'k', asset: { id: 'k', markRole: 'commemorative' } }
  const collection = withMarkRoles({
    id: 'mixed', cover: 'c', shelfSpecimen: 'c',
    entries: [campaign, kept, identity('x'), identity('y')],
    artworkSections: [{ id: 'own', label: 'Own', entries: [kept] }]
  })
  assert.equal(collection.cover, 'x')
  assert.equal(collection.shelfSpecimen, undefined)
  assert.deepEqual(collection.entries.map(({ id }) => id), ['x', 'y', 'c', 'k'])
  assert.deepEqual(collection.artworkSections.map(({ id, entries }) => [id, entries.map((entry) => entry.id)]),
    [['own', ['k']], ['secondary-campaign', ['c']]])
  assert.deepEqual(identityFirst([campaign, identity('z')]).map(({ id }) => id), ['z', 'c'])
})
