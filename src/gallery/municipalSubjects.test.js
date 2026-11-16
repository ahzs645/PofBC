import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { HISTORICAL_MUNICIPALITIES, MUNICIPAL_SUBJECTS, municipalSubjectId } from './municipalSubjects.js'
import { IDENTITY_COVERAGE, identitySubjectById, searchIdentitySubjects } from './identityCoverage.js'
import { GALLERY_COLLECTIONS, entriesOf } from './collections.js'
import { MUNICIPAL_PROFILE_BY_COUNCIL, MUNICIPAL_PROFILE_BY_EMPLOYER } from '../salaries/municipalProfiles.js'

const json = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url)))
const employers = new Set(json('../../public/salaries/employers/index.json').employers.map((employer) => employer.slug))
const council = json('../../public/salaries/council-pay.json')
const councilLabels = new Set([...council.observations, ...council.payments].map((row) => row.municipality))
const register = new Map(json('../../research/identity/arms-register-2026-11-16/register.json').entries.map((entry) => [entry.register_url, entry]))
const byName = new Map(MUNICIPAL_SUBJECTS.map((subject) => [subject.label, subject]))

test('every held gallery entry has a registered owner', () => {
  const covered = new Set(IDENTITY_COVERAGE.flatMap((subject) => subject.entries.map((entry) => entry.id)))
  const missing = GALLERY_COLLECTIONS.flatMap((collection) => entriesOf(collection).filter((entry) => !covered.has(entry.id)).map((entry) => `${collection.id}/${entry.id}`))
  assert.deepEqual(missing, [])
  for (const collection of GALLERY_COLLECTIONS) {
    assert.ok(IDENTITY_COVERAGE.some((subject) => subject.collections.some((each) => each.id === collection.id)), `${collection.id} has no register subject`)
  }
  assert.ok(searchIdentitySubjects('WorkSafeBC').some((subject) => subject.id === 'workers-compensation-board'))
  assert.equal(identitySubjectById('workers-compensation-board').entries.length, 5)
  // The foundation's marks stay the foundation's.
  assert.deepEqual(identitySubjectById('bc-cancer-foundation').entries.map((entry) => entry.id).sort(), ['bc-cancer-foundation-2018', 'bc-cancer-foundation-2026'])
  assert.ok(!identitySubjectById('sub-bc-cancer').entries.some((entry) => entry.id.startsWith('bc-cancer-foundation')))
})

test('the municipal registry is the 161 legal municipalities plus shíshálh, with no logo assumed', () => {
  assert.equal(MUNICIPAL_SUBJECTS.length, 162)
  assert.equal(MUNICIPAL_SUBJECTS.filter((subject) => subject.municipal.scope === 'current municipality').length, 161)
  assert.equal(MUNICIPAL_SUBJECTS.filter((subject) => subject.municipal.inProvincialLayer).length, 161)
  assert.equal(new Set(MUNICIPAL_SUBJECTS.map((subject) => subject.id)).size, 162)
  assert.equal(new Set(MUNICIPAL_SUBJECTS.map((subject) => subject.municipal.provincialId)).size, 162)
  for (const subject of MUNICIPAL_SUBJECTS) {
    assert.match(subject.municipal.provincialId, subject.municipal.inProvincialLayer ? /^bc-lgaa-\d+$/ : /^bc-shishalh-government-district$/)
    assert.equal(identitySubjectById(subject.id).hasArtwork, false, `${subject.id}: no municipal logo is held yet`)
    assert.equal(subject.graphNode, null, `${subject.id}: municipalities are not provincial atlas bodies`)
  }
  for (const pair of [['Langley (City)', 'Langley (Township)'], ['North Vancouver (City)', 'North Vancouver (District)'], ['Sechelt', 'shíshálh Nation Government District']]) {
    const [a, b] = pair.map((name) => byName.get(name))
    assert.ok(a && b, pair.join(' / '))
    assert.notEqual(a.id, b.id)
  }
  assert.equal(byName.get('shíshálh Nation Government District').kind, 'self-government-district')
  assert.ok(byName.get('Daajing Giids').municipal.historicalNames.includes('Queen Charlotte'))
  assert.ok(searchIdentitySubjects('Queen Charlotte').some((subject) => subject.id === municipalSubjectId('Daajing Giids')))
  assert.equal(byName.get('Northern Rockies').municipal.regionalDistrict, null)
  const falls = identitySubjectById(municipalSubjectId('Okanagan Falls'))
  assert.equal(falls.state, 'artwork-missing')
  assert.ok(!byName.has('Jumbo Glacier'))
  assert.ok(HISTORICAL_MUNICIPALITIES.some((each) => each.name === 'Jumbo Glacier'))
})

test('municipal links point at existing salary, council-pay and register records', () => {
  let salaries = 0
  let arms = 0
  for (const subject of MUNICIPAL_SUBJECTS) {
    for (const slug of subject.salaryEmployers) {
      assert.ok(employers.has(slug), `${subject.id}: unknown employer ${slug}`)
      assert.equal(MUNICIPAL_PROFILE_BY_EMPLOYER[slug], subject.id, `${slug}: salary page link`)
      salaries++
    }
    const label = subject.municipal.councilMunicipality
    if (label) {
      assert.ok(councilLabels.has(label), `${subject.id}: unknown council-pay label ${label}`)
      assert.equal(MUNICIPAL_PROFILE_BY_COUNCIL[label], subject.id, `${label}: council-pay link`)
    }
    for (const grant of subject.municipal.heraldry) {
      const entry = register.get(grant.registerUrl)
      assert.ok(entry, `${subject.id}: ${grant.registerUrl} is not in the arms register`)
      assert.equal(entry.name, grant.recipient)
      assert.ok(['current', 'predecessor'].includes(grant.relation))
    }
    if (subject.municipal.heraldry.length) arms++
  }
  assert.equal(salaries, 119)
  assert.equal(arms, 59)
  assert.equal(MUNICIPAL_SUBJECTS.filter((subject) => subject.municipal.councilMunicipality).length, 160)
  assert.equal(Object.keys(MUNICIPAL_PROFILE_BY_EMPLOYER).length, 119)
  assert.equal(Object.keys(MUNICIPAL_PROFILE_BY_COUNCIL).length, 160)
  // Predecessor arms stay the predecessor's.
  const abbotsford = byName.get('Abbotsford').municipal.heraldry
  assert.deepEqual(abbotsford.filter((grant) => grant.relation === 'predecessor').map((grant) => grant.recipient).sort(), ['District of Abbotsford', 'District of Matsqui'])
})
