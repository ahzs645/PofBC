import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { INITIATIVES, initiativeAncestors, initiativeById, initiativeParts, loadInitiative } from './initiatives.js'
import { ancestorsOf, indexGroups, resolveInitiativeSelection, searchInitiatives } from './initiativeModel.js'
import { initiativePlaceUrl, legacyInitiativeUrl, readInitiativePlace } from './initiativePlace.js'

const BASE = 'https://projects.ahmadjalil.com/PofBC/'

test('every parentId names another initiative in the catalogue', () => {
  const ids = new Set(INITIATIVES.map(({ id }) => id))
  assert.equal(ids.size, INITIATIVES.length, 'initiative IDs are unique')
  for (const { id, parentId } of INITIATIVES.filter((entry) => 'parentId' in entry)) {
    assert.ok(ids.has(parentId), `${id} → ${parentId}`)
    assert.notEqual(parentId, id)
  }
})

test('no initiative is its own ancestor', () => {
  for (const { id } of INITIATIVES) {
    const seen = new Set([id])
    for (let entry = initiativeById(id); entry?.parentId; entry = initiativeById(entry.parentId)) {
      assert.ok(!seen.has(entry.parentId), `cycle through ${id}`)
      seen.add(entry.parentId)
    }
  }
  // The helper stops on a circular chain instead of looping.
  const circular = [{ id: 'a', parentId: 'b' }, { id: 'b', parentId: 'a' }]
  assert.deepEqual(ancestorsOf('a', circular).map(({ id }) => id), ['b'])
})

test('the programs and their parts are grouped as their records describe', () => {
  const partsOf = (id) => initiativeParts(id).map((entry) => entry.id)
  assert.deepEqual(partsOf('firesmart-bc'), ['wildfire-mitigation', 'local-collective', 'plant-program',
    'training-summit', 'education', 'farm-and-ranch', 'library'].map((key) => `firesmart-bc-${key}`))
  assert.deepEqual(partsOf('bc-youth'), ['challenge-89', 'passport-to-apprenticeship', 'environment-youth-corps'])
  assert.deepEqual(partsOf('tourism'), ['rainforest-to-rockies'])
  for (const program of ['firesmart-bc', 'bc-youth', 'tourism']) {
    const { parts } = initiativeById(program)
    assert.ok(parts.label && parts.source?.url?.startsWith('https://'), `${program} cites the evidence for its parts`)
  }
})

test('every part is listed beneath its program on the index and on the program page', async () => {
  const groups = indexGroups(INITIATIVES, INITIATIVES)
  const listed = groups.flatMap(({ program, parts }) => [program.id, ...parts.map(({ id }) => id)])
  assert.deepEqual([...listed].sort(), INITIATIVES.map(({ id }) => id).sort(), 'each initiative appears once on the index')
  for (const { program, parts } of groups) {
    assert.equal(program.parentId, undefined)
    for (const part of parts) assert.equal(initiativeAncestors(part.id)[0].id, program.id)
  }
  for (const child of INITIATIVES.filter(({ parentId }) => parentId)) {
    const parent = await loadInitiative(child.parentId)
    assert.ok(initiativeParts(parent.id).some(({ id }) => id === child.id), `${child.id} on ${parent.id}`)
    assert.ok(parent.stats.some(({ value }) => value === initiativeParts(parent.id).length), `${parent.id} counts its parts`)
    assert.deepEqual(initiativeAncestors(child.id).map(({ id }) => id), [child.parentId], 'the trail reads All initiatives / Parent / Child')
  }
})

test('a search that matches only a part keeps it under its program', () => {
  const groups = indexGroups(searchInitiatives('Plant Program', INITIATIVES), INITIATIVES)
  assert.deepEqual(groups.map(({ program, parts, matched }) => [program.id, parts.map(({ id }) => id), matched]),
    [['firesmart-bc', ['firesmart-bc-plant-program'], false]])
  const youth = indexGroups(searchInitiatives('BC Youth', INITIATIVES), INITIATIVES).find(({ program }) => program.id === 'bc-youth')
  assert.equal(youth.parts.length, 3)
})

// Section IDs as they were published before the pages shared one template; every one must still open.
const PUBLISHED_SECTIONS = {
  'firesmart-bc': ['marks', 'timeline', 'standards', 'related-work', 'sources'],
  'firesmart-bc-wildfire-mitigation': ['program', 'marks', 'timeline', 'standards', 'sources'],
  'firesmart-bc-library': ['program', 'timeline', 'sources'],
  'power-smart': ['timeline', 'sources'],
  'bear-aware-1997': ['sign-and-checklists', 'times-review', 'unique', 'marks', 'sources'],
  'buy-bc': ['marks', 'timeline', 'sources'],
  jepp: ['marks', 'history', 'sources'],
  dfam: ['marks', 'history', 'sources'],
  'bc-youth': ['marks', 'history', 'sources'],
  'challenge-89': ['timeline', 'advertisement', 'sources'],
  'passport-to-apprenticeship': ['timeline', 'sources'],
  'environment-youth-corps': ['marks', 'timeline', 'sources'],
  'spirit-of-2010': ['marks', 'history', 'sources'],
  'pacific-gateway': ['marks', 'timeline', 'sources'],
  tourism: ['websites', 'programs', 'marks', 'timeline', 'rebranding', 'brand-guide', 'publications', 'sources'],
  'rainforest-to-rockies': ['marks', 'publications', 'sources'],
  'bc-the-education-province': ['marks', 'timeline', 'publications', 'sources'],
  'achieve-bc': ['marks', 'history', 'related', 'sources'],
  gamesense: ['marks', 'timeline', 'sources']
}

test('earlier initiative, section and record addresses still open the same place', async () => {
  for (const [id, sections] of Object.entries(PUBLISHED_SECTIONS)) {
    const detail = await loadInitiative(id)
    for (const section of sections) {
      const place = readInitiativePlace(`${BASE}?view=initiatives&initiative=${id}&section=${section}`)
      assert.equal(initiativeById(place.initiative)?.id, id)
      assert.equal(resolveInitiativeSelection(detail, place).section.id, section, `${id} · ${section}`)
    }
  }
  const records = [
    ['tourism', 'websites', 'hellobc'],
    ['tourism', 'publications', 'our-brand-2021'],
    ['challenge-89', 'advertisement', 'challenge-employer-ad-1989'],
    ['gamesense', 'marks', 'gamesense-logo']
  ]
  for (const [id, section, record] of records) {
    const url = initiativePlaceUrl(BASE + '?view=initiatives', { initiative: id, record })
    const { section: opened, record: found } = resolveInitiativeSelection(await loadInitiative(id), readInitiativePlace(url.href))
    assert.equal(opened.id, section, record)
    assert.equal(found?.id, record)
  }
  const legacy = legacyInitiativeUrl(`${BASE}?view=gallery&logos=tourism-bc-destination-bc#tourism-websites/hellobc`)
  assert.deepEqual(readInitiativePlace(legacy.href), { initiative: 'tourism', section: 'websites', record: 'hellobc' })
})

test('every initiative page follows one template', async () => {
  const views = new Set([...readFileSync(new URL('../site/ViewSwitcher.jsx', import.meta.url), 'utf8')
    .matchAll(/\{ id: '([a-z-]+)', label:/g)].map((match) => match[1]))
  for (const { id } of INITIATIVES) {
    const detail = await loadInitiative(id)
    const types = detail.sections.map(({ type }) => type)
    assert.equal(types.at(-1), 'sources', `${id} ends with its sources`)
    const timeline = types.indexOf('timeline')
    if (timeline >= 0) assert.equal(timeline, types.length - 2, `${id} puts its timeline before its sources`)
    for (const section of detail.sections.filter(({ type }) => type === 'timeline')) assert.equal(section.label, 'Timeline')
    assert.equal(detail.hero.title, initiativeById(id).title, `${id} is named in its hero`)
    assert.ok(detail.stats.length > 0, `${id} has facts under its title`)
    for (const link of detail.relatedLinks ?? []) assert.ok(views.has(link.to.view), `${id}: ${link.label} opens a named section`)
  }
})
