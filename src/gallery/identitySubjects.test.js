import { test } from 'node:test'
import assert from 'node:assert/strict'
import { IDENTITY_FAMILIES, IDENTITY_KIND_LABELS, IDENTITY_RELATION_LABELS, IDENTITY_SUBJECTS } from './identitySubjects.js'
import { CURRENT_BODIES } from '../government/currentData.js'
import { HISTORICAL_BODIES, LOCAL_BODIES, SUB_AGENCIES } from '../government/historyData.js'
import { RELATED_BODIES } from '../government/relatedBodies.js'
import { FIRST_YEAR, PRESENT_YEAR, governmentIn, lifeOf } from '../government/snapshot.js'
import { MINISTRY_EPISODES } from '../government/episodes.js'

const byId = new Map(IDENTITY_SUBJECTS.map((subject) => [subject.id, subject]))
// The snapshot also creates the Assembly and other constitutional nodes used by the map.
const graphIds = new Set([...CURRENT_BODIES, ...HISTORICAL_BODIES, ...LOCAL_BODIES, ...SUB_AGENCIES,
  ...RELATED_BODIES, ...MINISTRY_EPISODES, ...governmentIn(PRESENT_YEAR).nodes].map((body) => body.id))
const fold = (value) => value.normalize('NFKC').toLocaleLowerCase('en-CA').trim()

test('identity subjects have stable unique keys, readable evidence and a declared collection scope', () => {
  assert.equal(byId.size, IDENTITY_SUBJECTS.length, 'duplicate subject IDs would merge unrelated coverage')
  const families = new Map(IDENTITY_FAMILIES.map((family) => [family.id, family]))
  assert.equal(families.size, IDENTITY_FAMILIES.length, 'family IDs must remain unambiguous')
  for (const family of families.values()) {
    assert.match(family.id, /^[a-z0-9]+(?:-[a-z0-9]+)*$/)
    assert.ok(family.label.trim() && family.description.trim(), family.id)
    assert.ok(IDENTITY_SUBJECTS.some((subject) => subject.family === family.id), `${family.id} is an empty filter`)
  }
  for (const subject of IDENTITY_SUBJECTS) {
    assert.match(subject.id, /^[a-z0-9]+(?:-[a-z0-9]+)*$/)
    assert.ok(families.has(subject.family), `${subject.id}: unknown family ${subject.family}`)
    assert.ok(subject.kind in IDENTITY_KIND_LABELS, `${subject.id}: unknown legal/service category`)
    for (const field of ['label', 'name', 'nextAction', 'note']) {
      assert.equal(typeof subject[field], 'string', `${subject.id}: ${field}`)
      assert.ok(subject[field].trim(), `${subject.id}: empty ${field}`)
    }
    assert.ok([1, 2, 3].includes(subject.priority), `${subject.id}: invalid priority`)
    assert.ok(['core', 'institution'].includes(subject.scope), `${subject.id}: invalid scope`)
    for (const field of ['aliases', 'collectionIds', 'salaryEmployers', 'sources', 'relations']) {
      assert.ok(Array.isArray(subject[field]), `${subject.id}: ${field} must be explicit`)
    }
    assert.ok(subject.sources.length, `${subject.id}: no evidence route`)
    for (const source of subject.sources) {
      assert.ok(source.title?.trim(), `${subject.id}: source title missing`)
      // A printed source with no online copy says so, rather than inventing a link.
      if (source.url === undefined) {
        assert.ok(source.citation?.trim(), `${subject.id}: a source needs a URL or a print citation`)
        continue
      }
      const url = new URL(source.url)
      assert.equal(url.protocol, 'https:', `${subject.id}: non-HTTPS source`)
      assert.ok(!url.username && !url.password, `${subject.id}: source must not contain credentials`)
      assert.ok(!/example\.(?:com|org)|localhost/.test(url.hostname), `${subject.id}: placeholder source`)
    }
    for (const field of ['aliases', 'collectionIds', 'salaryEmployers']) {
      assert.ok(subject[field].every((value) => typeof value === 'string' && value.trim()), `${subject.id}: invalid ${field}`)
      assert.equal(new Set(subject[field].map(fold)).size, subject[field].length, `${subject.id}: duplicate ${field}`)
    }
  }
})

test('every atlas and relationship reference resolves without inventing a government node', () => {
  for (const subject of IDENTITY_SUBJECTS) {
    if (subject.graphNode !== null) {
      assert.ok(graphIds.has(subject.graphNode), `${subject.id}: ${subject.graphNode} is not an atlas body`)
    }
    const seen = new Set()
    for (const relation of subject.relations) {
      assert.ok(byId.has(relation.subject), `${subject.id}: unknown related subject ${relation.subject}`)
      assert.notEqual(relation.subject, subject.id, `${subject.id}: self-reference`)
      assert.ok(relation.type in IDENTITY_RELATION_LABELS, `${subject.id}: unknown relation ${relation.type}`)
      const key = `${relation.type}:${relation.subject}`
      assert.ok(!seen.has(key), `${subject.id}: duplicate relation ${key}`)
      seen.add(key)
      if (relation.label !== undefined) assert.ok(relation.label.trim(), `${subject.id}: blank relation label`)
    }
  }
})

test('organization links select a year where their actual atlas node exists', () => {
  const relatedIds = new Set(RELATED_BODIES.map((body) => body.id))
  const snapshots = new Map()
  const at = (year) => {
    if (!snapshots.has(year)) {
      snapshots.set(year, new Set(governmentIn(year, { includeUndated: true }).nodes.map((node) => node.id)))
    }
    return snapshots.get(year)
  }
  for (const subject of IDENTITY_SUBJECTS) {
    if (!subject.graphNode || relatedIds.has(subject.graphNode)) {
      assert.equal(subject.graphYear, undefined, `${subject.id}: services and related bodies do not acquire a provincial timeline`)
      continue
    }
    const year = subject.graphYear ?? PRESENT_YEAR
    assert.ok(Number.isInteger(year) && year >= FIRST_YEAR && year <= PRESENT_YEAR, `${subject.id}: invalid navigation year`)
    assert.ok(at(year).has(subject.graphNode), `${subject.id}: ${subject.graphNode} cannot be selected in ${year}`)
    const life = lifeOf(subject.graphNode)
    if (life?.toKind !== 'open') {
      assert.ok(Number.isInteger(subject.graphYear), `${subject.id}: historical link needs an explicit navigation year`)
      if (life?.lastSeen) {
        assert.ok(year <= Number(String(life.lastSeen).slice(0, 4)), `${subject.id}: do not select a year beyond the last confirmed sighting`)
      }
    }
  }
})

test('explicit shelves exist and a service does not inherit its parent’s artwork', async () => {
  const { GALLERY_COLLECTIONS } = await import('./collections.js')
  const collectionIds = new Set(GALLERY_COLLECTIONS.map((collection) => collection.id))
  for (const subject of IDENTITY_SUBJECTS) {
    for (const id of subject.collectionIds) assert.ok(collectionIds.has(id), `${subject.id}: unknown collection ${id}`)
    for (const relation of subject.relations.filter((item) => ['service-of', 'owned-by', 'part-of'].includes(item.type))) {
      const parent = byId.get(relation.subject)
      for (const id of subject.collectionIds) {
        assert.ok(!parent.collectionIds.includes(id), `${subject.id}: generic parent collection ${id} would overstate coverage`)
      }
    }
  }
  // Historical source records have their own raster evidence. Modern parent vectors must
  // not silently make those records appear to hold source-native historical artwork.
  assert.deepEqual(byId.get('bc-ferry-authority').collectionIds, [])
  assert.deepEqual(byId.get('urban-transit-authority').collectionIds, [])
  for (const [child, wrongShelf] of [
    ['sub-powerex', 'bc-hydro'], ['power-smart', 'bc-hydro'],
    ['sub-playnow', 'bclc'], ['gamesense', 'bclc'],
    ['sub-bc-place', 'collected-bc-place-ltd'],
    ['sub-bc-centre-for-disease-control', 'collected-provincial-health-services-authority']
  ]) assert.ok(!byId.get(child).collectionIds.includes(wrongShelf), child)
})

test('network symbols, operators, service brands and historical programs stay distinct', () => {
  const translink = byId.get('translink')
  assert.equal(translink.kind, 'regional-authority')
  assert.ok(translink.aliases.includes('GVTA'))
  assert.ok(!translink.aliases.includes('BCRTC'), 'an operator is not an alias for the authority')
  assert.equal(byId.get('translink-t-marker').kind, 'service-brand')
  assert.match(byId.get('translink-t-marker').note, /no inverse or monochrome/)
  assert.equal(byId.get('skytrain').graphNode, null, 'a project node must not stand in for the service')
  assert.ok(!byId.get('transit-security').aliases.includes('Transit Police'))
  assert.deepEqual(byId.get('handydart').relations.filter((relation) => relation.type === 'service-of').map((relation) => relation.subject).sort(), ['bc-transit', 'translink'])
  assert.match(byId.get('umo').note, /Cubic.*licensed by BC Transit/)
  assert.equal(byId.get('umo').kind, 'service-brand')
  assert.match(byId.get('aircare').note, /Historical/)
  assert.match(byId.get('quickpass').note, /Historical/)
  const historicalAuthority = byId.get('bc-ferry-authority')
  const modernAuthority = byId.get('bc-ferry-authority-2003')
  assert.notEqual(historicalAuthority.graphNode, modernAuthority.graphNode)
  assert.notEqual(historicalAuthority.kind, modernAuthority.kind)
})

test('named institutions retain their own legal scope, and salary links do not reconcile employers', () => {
  for (const id of ['university-of-northern-bc', 'university-of-british-columbia', 'simon-fraser-university', 'university-of-victoria', 'bcit', 'science-world']) {
    const subject = byId.get(id)
    assert.ok(subject, id)
    assert.equal(subject.scope, 'institution', id)
    assert.notEqual(subject.kind, 'crown-corporation', id)
    assert.ok(subject.sources.every((source) => !source.url.includes('wikipedia.org')), `${id}: use institutional primary sources`)
  }
  assert.equal(byId.get('science-world').kind, 'charitable-institution')
  assert.deepEqual(byId.get('metro-vancouver-transit-police').salaryEmployers, ['metro-vancouver-transit-police', 'transit-police'])
  assert.deepEqual(byId.get('university-of-british-columbia').salaryEmployers, ['university-of-bc'])
  for (const subject of IDENTITY_SUBJECTS) {
    assert.ok(!('mergeEmployers' in subject), `${subject.id}: employer links are not deduplication rules`)
  }
})

test('uncertainty and a documented shared signature are explicit without fabricated artwork or dates', () => {
  const prhc = byId.get('provincial-rental-housing-corporation')
  assert.equal(prhc.identityStatus, 'shared-identity')
  assert.deepEqual(prhc.collectionIds, [], 'documented shared use must not import all BC Housing designs')
  assert.ok(prhc.sources.some((source) => source.url.endsWith('#page=7') && source.note?.includes('6 November 2025')))
  assert.match(prhc.note, /not a universal rule/)
  for (const id of ['metro-transit-operating-company', 'wlc-developments', 'bc-harbours-board', 'court-of-appeal', 'supreme-court', 'provincial-court', 'office-of-the-premier', 'government-communications-and-public-engagement']) {
    assert.equal(byId.get(id).identityStatus, 'distinct-unconfirmed', id)
  }
  for (const subject of IDENTITY_SUBJECTS) {
    if (subject.identityStatus !== undefined) {
      // A municipality with no located logo source is recorded as wanted, not as a source lead.
      const allowed = subject.family === 'municipalities' ? ['artwork-missing'] : ['shared-identity', 'distinct-unconfirmed']
      assert.ok(allowed.includes(subject.identityStatus), `${subject.id}: asset coverage must be derived`)
    }
    for (const field of ['assets', 'svg', 'isVector', 'held', 'adopted', 'from', 'to']) {
      assert.ok(!(field in subject), `${subject.id}: ${field} requires asset/chronology evidence elsewhere`)
    }
  }
})
