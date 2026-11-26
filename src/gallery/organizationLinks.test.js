import { test } from 'node:test'
import assert from 'node:assert/strict'
import { searchGallery } from './gallerySearch.js'
import { GALLERY_COLLECTIONS, childCollectionsOf, collectionById, collectionOfNode, collectionsOfNode, entriesOf, entriesOfNode, findGalleryEntry, timelineOf } from './collections.js'
import { logosFor } from './galleryLogos.js'
import { identitySubjectById, relationsOf } from './identityCoverage.js'

test('BC Housing’s Homeowner Protection Office branding leads to the branch and its institutional history', () => {
  const node = 'sub-bc-housing-licensing-and-consumer-services'
  const previous = 'homeowner-protection-office'
  const collection = collectionOfNode(node)
  const mark = findGalleryEntry('homeowner-protection-office-2016')
  assert.ok(childCollectionsOf('collected-bc-housing').includes(collection))
  assert.equal(collection.cover, mark.id)
  assert.equal(mark.owner, node)
  assert.equal(mark.years, 'Seen 2016')
  assert.equal(mark.identity.provenance, 'extracted_from_official_vector')
  assert.equal(logosFor(previous), null)
  for (const theme of ['light', 'dark']) {
    const [logo] = logosFor(node, theme).entries
    assert.equal(logo.collection, collection.id)
    assert.ok(logo.html.includes(`${mark.id}.${theme}.svg`))
  }
  const branch = identitySubjectById(node)
  assert.deepEqual(relationsOf(branch).outgoing.map(({ type, target }) => [type, target.id]), [
    ['part-of', 'bc-housing'], ['received-operations-from', previous]
  ])
  assert.ok(relationsOf(identitySubjectById(previous)).incoming.some(({ target }) => target === branch))
})

test('organizations discover their own marks on shared gallery shelves in both directions', () => {
  for (const [node, ids] of [
    ['sub-workbc', ['work-bc', 'vector-workbc-2016', 'vector-workbc-current']],
    ['sub-bc-stats', ['bc-stats']],
    ['sub-bc-wildfire-service', ['bc-wildfire-service', 'bc-wildfire-service-one-line']],
    ['sub-bc-coroners-service', ['coroners-service']],
    ['sub-bc-bid', ['bc-bid']],
    ['bc-public-service-agency', ['public-service', 'vector-bc-public-service-where-ideas-work-2023-reverse']],
    ['sub-healthlink-bc', ['healthlink-bc-logo']]
  ]) {
    const collection = collectionOfNode(node)
    assert.equal(collection.id, 'bc-mark', node)
    assert.deepEqual(entriesOfNode(collection, node).map((entry) => entry.id).sort(), [...ids].sort(), node)
    for (const id of ids) assert.equal(findGalleryEntry(id).graphNode, node, id)
    const logos = logosFor(node)
    assert.deepEqual(logos.entries.map((entry) => entry.id).sort(), [...ids].sort(), node)
    for (const entry of logos.entries) assert.ok(entriesOf(collectionById(entry.collection)).some((candidate) => candidate.id === entry.id))
  }
})

test('a body can discover dedicated history and shared-shelf artwork without changing its canonical collection', () => {
  const node = 'sub-bc-online'
  assert.equal(collectionOfNode(node).id, 'collected-sub-bc-online')
  assert.deepEqual(collectionsOfNode(node).map((collection) => collection.id), ['collected-sub-bc-online', 'bc-mark'])
  const logos = logosFor(node, 'light', 100)
  assert.ok(logos.entries.some((entry) => entry.id === 'bc-online' && entry.collection === 'bc-mark'))
  for (const entry of logos.entries) assert.ok(entriesOfNode(collectionById(entry.collection), node).some((candidate) => candidate.id === entry.id))
  assert.equal(collectionOfNode('not-a-body'), undefined)
  assert.equal(logosFor('not-a-body'), null)
})

test('Knowledge Network uses its held SVG colourway while retaining the design download and deep link', () => {
  const id = 'source-knowledge-network-knowledge-network-colour-eps'
  const entry = findGalleryEntry(id)
  assert.equal(entry.asset.format, 'svg', 'the gallery uses the shared source SVG')
  assert.ok(entry.versions.some((source) => source.id === id && source.format === 'eps'), 'original EPS remains a source download')
  for (const theme of ['light', 'dark']) {
    const logos = logosFor('knowledge-network', theme)
    assert.equal(logos.total, 1)
    assert.equal(logos.entries[0].id, id)
    assert.match(logos.entries[0].html, new RegExp(`identity-display/source-knowledge-network-knowledge-network-svg\\.${theme}\\.svg`))
  }
  assert.equal(entry.asset.format, 'svg', 'thumbnail selection must not mutate the shared master')
})

test('the Cancer Foundation keeps its own ownership within the shared visual family', () => {
  const collection = collectionById('collected-sub-bc-cancer')
  for (const id of ['bc-cancer-foundation-2018', 'bc-cancer-foundation-2026']) {
    const entry = findGalleryEntry(id)
    assert.ok(entriesOf(collection).includes(entry), id)
    assert.equal(entry.owner, 'bc-cancer-foundation', id)
    assert.ok(!entriesOfNode(collection, 'sub-bc-cancer').includes(entry), id)
    assert.ok(!entry.graphNode, 'the Foundation is not a provincial-government node')
  }
  assert.ok(entriesOfNode(collection, 'sub-bc-cancer').some((entry) => entry.id === 'bc-cancer-phsa'))
})

test('a body panel finds the original specimens of the program its one-off stands for', async () => {
  const { collectionsOfNode, entriesOfNode } = await import('./collections.js')
  const held = (node) => collectionsOfNode(node).flatMap((collection) => entriesOfNode(collection, node)).map((entry) => entry.id)
  assert.ok(['vector-workbc-2016', 'vector-workbc-current'].every((id) => held('sub-workbc').includes(id)))
  assert.ok(held('bc-public-service-agency').includes('vector-bc-public-service-where-ideas-work-2023-reverse'))
  const prepared = collectionsOfNode('sub-preparedbc').flatMap((collection) => entriesOfNode(collection, 'sub-preparedbc'))
  assert.deepEqual(prepared.map((entry) => entry.id), ['prepared-bc'])
  // Linking it does not make the remake read as the program's own lockup.
  assert.equal(prepared[0].identity.provenance, 'synthetic_name_variant')
})

test('departmental, initiative and one-off artwork remains searchable under the correct owner', () => {
  const travel = collectionOfNode('department-of-travel-industry-1967')
  assert.equal(travel.shelf, 'departmental')
  assert.equal(logosFor(travel.graphNode).entries[0].id, 'bc-travel-industry-ca-1970')
  assert.ok(searchGallery('Travel Industry').collections.includes(travel))
  assert.ok(searchGallery('BC Youth').collections.some((c) => c.id === 'collected-bc-youth' && c.shelf === 'initiatives'))
  const oneOffs = collectionById('bc-mark')
  assert.ok(!oneOffs.entries.some((entry) => entry.id === travel.cover))
  const formerCollection = 'collected-government-communications-and-public-engagement'
  assert.equal(collectionById(formerCollection), oneOffs)
  assert.ok(!GALLERY_COLLECTIONS.some((collection) => collection.id === formerCollection))
  const gcpe = oneOffs.entries.find((entry) => entry.id === 'gcpe-estimate-notes-2024-rebuilt')
  assert.equal(gcpe.owner, 'government-communications-and-public-engagement')
  assert.equal(gcpe.versions.length, 2)
  assert.ok(searchGallery('GCPE').marks.some(({ collection, entry }) => collection === oneOffs && entry === gcpe))
  const publicService = searchGallery('where ideas work 2023').marks.find(({ entry }) => entry.id === 'vector-bc-public-service-where-ideas-work-2023-reverse')
  assert.equal(publicService?.collection, oneOffs)
  assert.equal(publicService.entry.timeline, 'public-service')
  assert.ok(!GALLERY_COLLECTIONS.some(({ id }) => id === 'specimens-public-service'))
})

test('provincial health program signatures share a shelf and retain their individual owners', () => {
  const collection = collectionById('health-program-signatures')
  assert.equal(collection.shelf, 'provincial-programs')
  assert.equal(collection.relatedGenerator.era, 'crest')
  assert.equal(collection.graphNode, 'ministry-of-health-services-2001')
  for (const owner of ['bchealthcare', 'bcpharmacare']) {
    assert.deepEqual(entriesOfNode(collection, owner).map((entry) => entry.id), [owner + '-2003'])
    assert.equal(findGalleryEntry(owner + '-2003').identity.provenance, 'extracted_from_official_vector')
  }
  assert.equal(entriesOfNode(collection, collection.graphNode).length, 0)
})

test('program specimens sit next to their original BC marks and retain their program history', () => {
  const shelf = collectionById('bc-mark')
  for (const [program, owner, count] of [['welcome-bc', 'welcome-bc', 2], ['work-bc', 'sub-workbc', 2], ['stronger-bc', 'stronger-bc', 5]]) {
    assert.equal(collectionById(`specimens-${program}`), shelf)
    assert.ok(!GALLERY_COLLECTIONS.some(({ id }) => id === `specimens-${program}`))
    const original = findGalleryEntry(program)
    const specimens = entriesOfNode(shelf, owner).filter((entry) => entry.kind === 'collected')
    assert.equal(specimens.length, count)
    const start = entriesOf(shelf).indexOf(original) + 1
    assert.deepEqual(entriesOf(shelf).slice(start, start + count), specimens)
    const timelineEntries = timelineOf(original).eras.flatMap(({ entries }) => entries)
    assert.ok(specimens.every((specimen) => timelineEntries.includes(specimen) && specimen.timeline === program))
  }
})
