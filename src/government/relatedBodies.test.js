import { test } from 'node:test'
import assert from 'node:assert/strict'
import { CURRENT_BODIES } from './currentData.js'
import { HISTORICAL_BODIES, LOCAL_BODIES, SUB_AGENCIES } from './historyData.js'
import { readGovernmentPlace } from './governmentPlace.js'
import { governmentIn, PRESENT_YEAR } from './snapshot.js'
import {
  RELATED_BODIES, RELATED_BODY_GROUPS, RELATED_BODY_KINDS, RELATED_SALARY_LINKS,
  connectRelatedSalaryBodies, groupRelatedBodies, relatedBodyById, relatedBodyPlace, searchRelatedBodies
} from './relatedBodies.js'
import { writeHistory } from '../site/browserHistory.js'

const atlasBodies = [...CURRENT_BODIES, ...HISTORICAL_BODIES, ...SUB_AGENCIES, ...LOCAL_BODIES]
const atlasIds = new Set(atlasBodies.map((body) => body.id))
const freeze = (value) => {
  if (value && typeof value === 'object') {
    Object.values(value).forEach(freeze)
    Object.freeze(value)
  }
  return value
}

test('related organizations have distinct sourced records and their own governance classifications', () => {
  assert.equal(new Set(RELATED_BODIES.map((body) => body.id)).size, RELATED_BODIES.length)
  const employerSlugs = RELATED_BODIES.flatMap((body) => body.salaryEmployers.map((entry) => entry.slug))
  assert.equal(new Set(employerSlugs).size, employerSlugs.length, 'an employer file is not assigned to two organizations')
  for (const body of RELATED_BODIES) {
    assert.ok(!atlasIds.has(body.id), `${body.id} duplicates an existing atlas record`)
    assert.ok(RELATED_BODY_KINDS[body.kind], `${body.id} has no public classification`)
    assert.equal(body.chronology, 'current-catalogue')
    assert.equal(body.branch, undefined, 'a catalogue record does not assert executive membership')
    assert.match(body.checked, /^\d{4}-\d{2}-\d{2}$/)
    assert.ok(body.sources.length, `${body.id} has no governance source`)
    for (const source of body.sources) {
      assert.ok(source.title)
      assert.equal(new URL(source.url).protocol, 'https:')
    }
    for (const connection of body.relationships) {
      assert.ok(relatedBodyById(connection.id) || atlasIds.has(connection.id), `${body.id}: unresolved connection ${connection.id}`)
      if (!relatedBodyById(connection.id)) {
        assert.ok(governmentIn(connection.year).nodes.some((node) => node.id === connection.id), `${connection.id} does not stand in the linked year`)
      }
    }
  }
  assert.equal(relatedBodyById('translink').kind, 'regional-transportation-authority')
  assert.equal(relatedBodyById('metro-vancouver').kind, 'regional-federation')
  assert.equal(relatedBodyById('science-world').kind, 'charitable-society')
})

test('current catalogue records are never projected into the provincial government chronology', () => {
  const ids = new Set(RELATED_BODIES.map((body) => body.id))
  for (const year of [1871, 1964, 1970, 1998, 1999, 2003, PRESENT_YEAR]) {
    assert.deepEqual(governmentIn(year, { includeUndated: true, includeLocal: true }).nodes.filter((node) => ids.has(node.id)), [], `${year} contains a current catalogue record`)
  }
  const oldAuthority = HISTORICAL_BODIES.find((body) => body.id === 'bc-ferry-authority')
  assert.equal(oldAuthority.established, '1964-04-01')
  assert.equal(oldAuthority.ended, '1977-01-01')
  assert.ok(relatedBodyById('bc-ferry-authority-2003'))
  assert.equal(relatedBodyById('bc-ferry-authority'), null)
})

test('recognized regional and university aliases find their own records without merging identities', () => {
  assert.deepEqual(searchRelatedBodies('GVTA').map((body) => body.id), ['translink'])
  assert.deepEqual(searchRelatedBodies('GVRD').map((body) => body.id), ['metro-vancouver'])
  assert.deepEqual(searchRelatedBodies('UNBC').map((body) => body.id), ['university-of-northern-bc'])
  assert.deepEqual(searchRelatedBodies('SeaBus').map((body) => body.id), ['coast-mountain-bus-company'])
  // "TransLink Security Management" can also match these words; search does not collapse that
  // policing record into CMBC's separate Transit Security service.
  assert.ok(searchRelatedBodies('Transit Security').some((body) => body.id === 'coast-mountain-bus-company'))
  assert.notEqual(relatedBodyById('coast-mountain-bus-company'), relatedBodyById('metro-vancouver-transit-police'))
  assert.deepEqual(searchRelatedBodies('Transit Police').map((body) => body.id), ['metro-vancouver-transit-police'])
  assert.deepEqual(searchRelatedBodies('unlisted organization'), [])
})

test('gallery and year-tagged salary links open the current related record', () => {
  for (const body of RELATED_BODIES) {
    const direct = readGovernmentPlace(`?view=government&node=${body.id}&year=1970`)
    assert.equal(direct.node, body.id)
    assert.equal(direct.mode, 'related')
    assert.equal(direct.year, PRESENT_YEAR)
    const explicit = readGovernmentPlace(new URLSearchParams(relatedBodyPlace(body.id)))
    assert.equal(explicit.node, body.id)
    assert.equal(explicit.mode, 'related')
  }
  const oldAuthority = readGovernmentPlace('?view=government&node=bc-ferry-authority&year=1970')
  assert.equal(oldAuthority.mode, 'graph')
  assert.equal(oldAuthority.year, 1970)
  assert.equal(readGovernmentPlace('?view=government&mode=related').mode, 'related')
  assert.equal(relatedBodyPlace('unlisted-body'), null)
  assert.equal(readGovernmentPlace('?mode=list&year=1986').mode, 'list')
  assert.equal(readGovernmentPlace('?mode=compare&year=1986&compare=2000').compare, 2000)
})

test('Back and Forward preserve separate related, salary and historical destinations', () => {
  const previousHistory = globalThis.history
  const previousLocation = globalThis.location
  const origin = 'https://example.org/'
  const entries = [origin + '?view=government&node=bc-ferry-authority&year=1970']
  let at = 0
  globalThis.location = { href: entries[0] }
  globalThis.history = {
    pushState(_state, _title, href) { entries.splice(++at); entries.push(String(href)); globalThis.location.href = String(href) },
    replaceState(_state, _title, href) { entries[at] = String(href); globalThis.location.href = String(href) },
    back() { if (at > 0) globalThis.location.href = entries[--at] },
    forward() { if (at + 1 < entries.length) globalThis.location.href = entries[++at] }
  }
  const place = () => readGovernmentPlace(new URL(globalThis.location.href).search)
  try {
    writeHistory(origin + '?' + new URLSearchParams(relatedBodyPlace('bc-ferry-authority-2003')))
    assert.equal(place().node, 'bc-ferry-authority-2003')
    writeHistory(origin + '?view=salaries&employer=transit-police')
    globalThis.history.back()
    assert.equal(place().node, 'bc-ferry-authority-2003')
    assert.equal(place().mode, 'related')
    globalThis.history.back()
    assert.equal(place().node, 'bc-ferry-authority')
    assert.equal(place().year, 1970)
    globalThis.history.forward()
    assert.equal(place().mode, 'related')
    globalThis.history.forward()
    assert.equal(new URL(globalThis.location.href).searchParams.get('employer'), 'transit-police')
  } finally {
    if (previousHistory === undefined) delete globalThis.history
    else globalThis.history = previousHistory
    if (previousLocation === undefined) delete globalThis.location
    else globalThis.location = previousLocation
  }
})

test('employer links retain disclosure evidence and separately filed Transit Police employers', () => {
  const source = freeze({
    years: ['2024'], aliases: { 'old-translink': 'translink' }, sources: [{ title: 'Original disclosure' }],
    employers: [
      { slug: 'translink', names: ['TransLink'], sector: 'Crown corporations', body: null, counts: [2], coverage: [{ status: 'complete' }] },
      { slug: 'transit-police', names: ['Transit Police'], sector: 'Municipal police', body: null, counts: [3] },
      { slug: 'metro-vancouver-transit-police', names: ['Metro Vancouver Transit Police'], sector: 'Municipal police', body: null, counts: [4] },
      { slug: 'university-of-bc', names: ['University of BC'], sector: 'Universities and colleges', body: null, counts: [5] }
    ]
  })
  const result = connectRelatedSalaryBodies(source)
  assert.equal(result.employers.length, source.employers.length)
  assert.deepEqual(result.employers.map((entry) => entry.slug), source.employers.map((entry) => entry.slug))
  assert.equal(result.sources, source.sources)
  assert.equal(result.aliases, source.aliases)
  assert.equal(result.employers[0].names, source.employers[0].names)
  assert.equal(result.employers[0].counts, source.employers[0].counts)
  assert.equal(result.employers[0].coverage, source.employers[0].coverage)
  assert.equal(result.employers[0].sourceSector, 'Crown corporations')
  assert.equal(result.employers[0].sector, 'Regional transportation')
  assert.equal(result.employers[1].body, 'metro-vancouver-transit-police')
  assert.equal(result.employers[2].body, 'metro-vancouver-transit-police')
  assert.notEqual(result.employers[1], result.employers[2])
  assert.equal(result.employers[3].body, 'university-of-british-columbia')
  assert.deepEqual(connectRelatedSalaryBodies(result), result)
})

test('person-index links keep employer offsets, slugs, source labels and people observations unchanged', () => {
  const slugs = Object.keys(RELATED_SALARY_LINKS)
  const source = freeze({
    years: ['2024'], sources: [{ title: 'Original source' }], counts: [99], shards: { ab: 2 },
    employers: slugs.map((slug) => [slug, RELATED_SALARY_LINKS[slug].sector ? 'Crown corporations' : 'Source sector', null, slug]),
    rows: [['Example, Person', 'Role', 100000, 0, 0, 0, 0], ['Example, Person', 'Role', 110000, 0, 1, 0, 0]]
  })
  const result = connectRelatedSalaryBodies(source)
  assert.equal(result.rows, source.rows)
  assert.equal(result.sources, source.sources)
  assert.equal(result.counts, source.counts)
  assert.equal(result.shards, source.shards)
  assert.equal(result.employers.length, source.employers.length)
  source.employers.forEach((entry, at) => {
    assert.equal(result.employers[at][0], entry[0])
    assert.equal(result.employers[at][3], entry[3])
    assert.equal(result.employers[at][2], RELATED_SALARY_LINKS[entry[3]].body)
    if (RELATED_SALARY_LINKS[entry[3]].sector) {
      assert.equal(result.sourceEmployerSectors[at], entry[1])
      assert.equal(result.employers[at][1], 'Regional transportation')
    } else assert.equal(result.employers[at][1], entry[1])
  })
  assert.deepEqual(connectRelatedSalaryBodies(result), result)
})

test('existing links and unlisted employer spellings are not replaced or inferred', () => {
  const source = freeze({ employers: [
    { slug: 'translink', names: ['TransLink'], sector: 'Original sector', body: 'existing-reviewed-link' },
    { slug: 'translink-contractor', names: ['TransLink Contractor'], sector: 'Original sector', body: null },
    ['TransLink contractor', 'Original sector', null, 'translink-contractor'],
    ['TransLink', 'Original sector', 'existing-reviewed-link', 'translink'],
    { slug: 'toString', names: ['Unlisted'], sector: 'Original sector', body: null }
  ] })
  const result = connectRelatedSalaryBodies(source)
  result.employers.forEach((entry, at) => assert.equal(entry, source.employers[at]))
  assert.equal(connectRelatedSalaryBodies(null), null)
  const invalid = { employers: {} }
  assert.equal(connectRelatedSalaryBodies(invalid), invalid)
})

test('every kind of related body belongs to exactly one directory group', () => {
  const placed = RELATED_BODY_GROUPS.flatMap((group) => group.kinds)
  assert.deepEqual([...placed].sort(), Object.keys(RELATED_BODY_KINDS).sort())
  assert.equal(new Set(placed).size, placed.length)
  const grouped = groupRelatedBodies(RELATED_BODIES)
  assert.equal(grouped.reduce((sum, group) => sum + group.bodies.length, 0), RELATED_BODIES.length)
  assert.equal(grouped.some((group) => group.id === 'other'), false)
})

test('a search leaves out the groups it empties', () => {
  const grouped = groupRelatedBodies(searchRelatedBodies('university'))
  assert.deepEqual(grouped.map((group) => group.id), ['learning'])
})
