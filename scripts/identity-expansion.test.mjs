import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { COLLECTED_BODIES } from '../src/gallery/collectedData.js'
import { EXPANDED_IDENTITY_BODIES } from '../src/gallery/expandedIdentityData.js'
import { MUNICIPAL_IDENTITY_BODIES } from '../src/gallery/municipalIdentityData.js'
import { RECOVERED_IDENTITY_BODIES } from '../src/gallery/recoveredIdentityData.js'
import { NORTHERN_TRAVEL_GUIDE_ARTWORK } from '../src/gallery/northernTravelGuides.js'
import { IDENTITY_SUBJECTS } from '../src/gallery/identitySubjects.js'
import { REGIONAL_DISTRICT_BODIES } from '../src/gallery/regionalDistricts.js'
import { collectionById, entriesOf } from '../src/gallery/collections.js'

test('expanded artwork, preserved sources and generated metadata pass the offline integrity gate', () => {
  execFileSync(process.execPath, ['scripts/build-identity-expansion.mjs', '--check'], {
    cwd: fileURLToPath(new URL('../', import.meta.url)), stdio: 'pipe', timeout: 30000
  })
})

test('every added artwork body has its own declared subject and retains every accepted file', () => {
  const oldIds = new Set(COLLECTED_BODIES.map((body) => body.id))
  const subjects = new Map(IDENTITY_SUBJECTS.map((subject) => [subject.id, subject]))
  const districtIds = new Set(REGIONAL_DISTRICT_BODIES.map(({ id }) => id))
  const expandedBodies = EXPANDED_IDENTITY_BODIES.filter(({ id }) => !districtIds.has(id))
  for (const body of [...expandedBodies, ...REGIONAL_DISTRICT_BODIES, ...MUNICIPAL_IDENTITY_BODIES, ...RECOVERED_IDENTITY_BODIES]) {
    assert.ok(!oldIds.has(body.id), `${body.id}: expansion overwrites a legacy body`)
    const subject = subjects.get(body.id)
    assert.ok(subject, `${body.id}: artwork has no declared identity subject`)
    assert.equal(body.kind, subject.kind, `${body.id}: legal/service category drift`)
    assert.equal(body.graphNode, subject.graphNode, `${body.id}: organization link drift`)
    const collection = collectionById(`collected-${body.id}`)
    assert.ok(collection, `${body.id}: no reachable collection`)
    // A body shelved in a shared collection (the Office of the Premier with the one-off marks) is
    // reached by its old address, and keeps every file among the entries it owns there.
    const own = collection.id === `collected-${body.id}` ? entriesOf(collection) : entriesOf(collection).filter((entry) => entry.owner === body.id)
    const accepted = new Set(own.flatMap((entry) => (entry.versions ?? [entry.asset]).map((asset) => asset.id)))
    const original = districtIds.has(body.id) ? EXPANDED_IDENTITY_BODIES.find(({ id }) => id === body.id) : undefined
    const expected = [...body.assets, ...(original?.assets ?? []), ...(NORTHERN_TRAVEL_GUIDE_ARTWORK[body.id] ?? [])]
    for (const asset of expected) {
      assert.ok(accepted.has(asset.id), `${body.id}: ${asset.id} lost in collection assembly`)
    }
  }
})

test('follow-up accepts only attributed municipal and named institutional signatures', () => {
  const recovered = new Map(RECOVERED_IDENTITY_BODIES.map((body) => [body.id, body]))
  assert.equal(recovered.get('municipality-warfield').assets.filter((asset) => asset.isVector).length, 2)
  for (const id of ['municipality-keremeos', 'liquor-control-board', 'provincial-court', 'court-of-appeal', 'supreme-court', 'office-of-the-premier', 'government-communications-and-public-engagement']) {
    assert.equal(recovered.get(id).assets.filter((asset) => !asset.reconstruction).length, 1, id)
  }
  const lionsBay = recovered.get('municipality-lions-bay').assets
  assert.equal(lionsBay.filter((asset) => !asset.reconstruction).length, 2)
  assert.equal(lionsBay.find((asset) => asset.id === 'municipal-lions-bay-bear-smart-stacked').isVector, false)
  assert.match(recovered.get('liquor-control-board').assets[0].notes, /not current LDB branding/)
  assert.match(recovered.get('provincial-court').notes, /not a claim.*distinct heraldic grant/)
  const [grandForks] = recovered.get('municipality-grand-forks').assets
  assert.equal(grandForks.publisher, 'City of Grand Forks')
  assert.equal(grandForks.evidenceType, 'native-pdf-vector-extraction')
  assert.equal(grandForks.extraction.page, 12)
  assert.equal(grandForks.isVector && !grandForks.reconstruction, true)
  for (const id of ['municipality-okanagan-falls', 'municipality-shishalh-nation-government-district', 'thompson-health-region']) {
    assert.ok(!recovered.has(id), `${id} must not be credited from a source link, shared emblem, or OCR alone`)
  }
})
