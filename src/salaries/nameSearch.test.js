import test from 'node:test'
import assert from 'node:assert/strict'
import { personKey } from './people.js'
import { chooseNameSearchBucket, createNameSearchDocuments, matchNameSearch, nameSearchTokens, searchNameSearchDocuments } from './nameSearch.js'

const index = {
  employers: [['Northern Health', 'health', 'authority', 'northern-health'], ['Other employer', 'education', 'university', 'other']],
  years: ['2019/20', '2020/21', '2021/22', '2022/23', '2023/24']
}
const row = (name, employerAt = 0, yearAt = 0) => [name, 'Position', 78500, null, employerAt, yearAt, 'source', 1]
const milad = 'Fathi Baghbadorani, Milad'

test('finds Milad by given name, either surname word, full name and any word order', () => {
  for (const query of ['milad', 'fathi', 'baghbadorani', 'Milad Fathi Baghbadorani', 'baghbadorani milad fathi']) {
    assert.equal(matchNameSearch(milad, nameSearchTokens(query)), 0, query)
  }
  for (const query of ['mil', 'fath mil', 'baghb milad']) assert.equal(matchNameSearch(milad, nameSearchTokens(query)), 1, query)
  assert.equal(matchNameSearch(milad, nameSearchTokens('milad smith')), null)
  assert.equal(matchNameSearch(milad, []), null)
  assert.equal(matchNameSearch(milad, nameSearchTokens('iladi')), null, 'matches word prefixes, not arbitrary substrings')
})

test('normalizes accents, case, apostrophes, hyphens and punctuation without guessing name order', () => {
  assert.deepEqual(nameSearchTokens(' [ÉLODIE]  /  García. '), ['elodie', 'garcia'])
  assert.deepEqual(nameSearchTokens('O’Neill, Anne-Marie'), ['oneill', 'anne', 'marie'])
  for (const query of ["ANNE-MARIE O'NEILL", 'oneill marie', 'anne marie oneill']) {
    assert.equal(matchNameSearch('O’Neill, Anne-Marie', nameSearchTokens(query)), 0, query)
  }
  assert.equal(matchNameSearch('García, José', nameSearchTokens('jose garcia')), 0)
  assert.equal(matchNameSearch('Milad Fathi Baghbadorani', nameSearchTokens('baghbadorani milad')), 0)
  assert.deepEqual(nameSearchTokens('milad    fathi'), ['milad', 'fathi'], 'query spacing does not hide later words')
  assert.equal(matchNameSearch(milad, nameSearchTokens('milad    fathi')), 0)
})

test('ranks complete words ahead of prefixes, then sorts by the existing surname key', () => {
  const documents = createNameSearchDocuments([
    row('Miladinovic, Ana'), row('Zed, Milad'), row(milad), row('Adams, Miladin')
  ], index)
  const found = searchNameSearchDocuments(documents, 'milad')
  assert.deepEqual(found.map(({ key, tier }) => [key, tier]), [
    [personKey(milad), 0], [personKey('Zed, Milad'), 0],
    [personKey('Adams, Miladin'), 1], [personKey('Miladinovic, Ana'), 1]
  ])
})

test('chooses the smallest required bucket, with document counts as fallback and tie-breaker', () => {
  const manifest = { buckets: {
    mi: { documents: 20, bytes: 300 }, fa: { documents: 50, bytes: 100 }, ba: { documents: 10, bytes: 100 }
  } }
  assert.equal(chooseNameSearchBucket('milad fathi', manifest), 'fa')
  assert.equal(chooseNameSearchBucket('baghbadorani milad fathi', manifest), 'ba')
  assert.equal(chooseNameSearchBucket(['m', 'fathi'], manifest), 'fa', 'an initial can accompany a longer search word')
  assert.equal(chooseNameSearchBucket('fathi milad', { buckets: { mi: { documents: 3 }, fa: { documents: 5 } } }), 'mi')
  assert.equal(chooseNameSearchBucket('milad unknown', manifest), null, 'one missing required prefix rules out all matches')
  assert.equal(chooseNameSearchBucket('milad fathi', { buckets: { mi: { documents: 0 }, fa: { documents: 1 } } }), null)
  assert.equal(chooseNameSearchBucket('m', manifest), null)
  assert.equal(chooseNameSearchBucket('', manifest), null)
  assert.equal(chooseNameSearchBucket('milad', null), null)
})

test('creates compact employer documents with complete period coverage and original record shards', () => {
  const rows = [0, 1, 2, 3, 4].map((year) => row(milad, 0, year))
  rows.push(row(milad, 0, 4), row(milad, 1, 2))
  const documents = createNameSearchDocuments(rows, index)
  assert.deepEqual(documents, [
    [personKey(milad), milad, 0, [0, 1, 2, 3, 4], [milad], ['fa']],
    [personKey(milad), milad, 1, [2], [milad], ['fa']]
  ])
  assert.deepEqual(createNameSearchDocuments([...rows].reverse(), index), documents)
  const [found] = searchNameSearchDocuments(documents, 'milad')
  assert.deepEqual(found.employerIds, [0, 1])
  assert.deepEqual(found.years, [0, 1, 2, 3, 4])
  assert.deepEqual(found.recordShards, ['fa'])
})

test('filters employer and reporting period together before grouping, avoiding false intersections', () => {
  const documents = createNameSearchDocuments([row(milad, 0, 0), row(milad, 1, 4)], index)
  assert.deepEqual(searchNameSearchDocuments(documents, 'milad', { employerIds: new Set([0]), yearIds: new Set([4]) }), [])
  const [found] = searchNameSearchDocuments(documents, 'milad', { employerIds: new Set([1]), yearIds: new Set([4]) })
  assert.deepEqual(found.employerIds, [1])
  assert.deepEqual(found.years, [4])
  assert.deepEqual(searchNameSearchDocuments(documents, 'milad', { employerIds: new Set() }), [])
  assert.deepEqual(searchNameSearchDocuments(documents, 'milad', { yearIds: new Set() }), [])
  assert.deepEqual(searchNameSearchDocuments(documents, ''), [])
})

test('applies existing aliases only at their employer and preserves cross-surname record routes', () => {
  const oldName = 'Oldname, René'
  const canonical = 'Newname, René'
  const canonicalKey = personKey(canonical)
  const link = { key: canonicalKey, name: canonical, status: 'verified' }
  const links = new Map([[`0|${personKey(oldName)}`, link], [`0|${canonicalKey}`, link]])
  const documents = createNameSearchDocuments([
    row(oldName, 0, 0), row(canonical, 0, 1), row(oldName, 1, 0), row(canonical, 1, 4)
  ], index, links)
  const joined = documents.find(([key, , employer]) => key === canonicalKey && employer === 0)
  assert.equal(joined[1], canonical)
  assert.deepEqual(joined[3], [0, 1])
  assert.deepEqual(joined[4], [canonical, oldName])
  assert.deepEqual(joined[5], ['ne', 'ol'])
  const found = searchNameSearchDocuments(documents, 'oldname')
  assert.deepEqual(found.map(({ key, employerIds }) => [key, employerIds]), [
    [canonicalKey, [0]], [personKey(oldName), [1]]
  ])
  assert.deepEqual(searchNameSearchDocuments(documents, 'oldname', { employerIds: new Set([1]), yearIds: new Set([4]) }), [])
  assert.deepEqual(searchNameSearchDocuments(documents, 'newname')[0].employerIds, [0, 1])
})

test('does not assemble a match from fragments of different aliases', () => {
  const canonical = 'MacLeod, Alice'
  const alias = 'McLeod, Alison'
  const link = { key: personKey(canonical), name: canonical, status: 'verified' }
  const documents = createNameSearchDocuments([row(canonical), row(alias)], index,
    new Map([[`0|${personKey(canonical)}`, link], [`0|${personKey(alias)}`, link]]))
  assert.deepEqual(searchNameSearchDocuments(documents, 'mcleod alice'), [])
  assert.equal(searchNameSearchDocuments(documents, 'mcleod alis')[0].tier, 1)
  assert.equal(searchNameSearchDocuments(documents, 'macleod alice')[0].tier, 0)
})

test('keeps identity keys and conflicting initials distinct while excluding appended jobs from search', () => {
  const withPosition = 'Moller, J      Director, Engineering'
  const names = ['Smith, Jennifer J', 'Smith, Jennifer N', 'Smith, Jennifer', 'Jennifer Smith', withPosition]
  const documents = createNameSearchDocuments(names.map((name) => row(name)), index)
  assert.deepEqual(new Set(documents.map(([key]) => key)), new Set(names.map(personKey)))
  assert.equal(searchNameSearchDocuments(documents, 'jennifer').length, 4, 'search finds names without joining their keys')
  const [moller] = searchNameSearchDocuments(documents, 'moller')
  assert.equal(moller.key, personKey(withPosition))
  assert.equal(moller.name, 'Moller, J')
  assert.deepEqual(moller.spellings, ['Moller, J'])
  assert.deepEqual(searchNameSearchDocuments(documents, 'director'), [])
  assert.deepEqual(searchNameSearchDocuments(documents, 'engineering'), [])
  assert.equal(matchNameSearch(withPosition, nameSearchTokens('engineering')), null)
})

test('every searchable word routes back to a matching document through its token bucket', () => {
  const documents = createNameSearchDocuments([row(milad), row('O’Neill, Anne-Marie'), row('García, José')], index)
  const buckets = new Map()
  for (const document of documents) {
    for (const prefix of new Set(document[4].flatMap(nameSearchTokens).filter((word) => word.length >= 2).map((word) => word.slice(0, 2)))) {
      if (!buckets.has(prefix)) buckets.set(prefix, [])
      buckets.get(prefix).push(document)
    }
  }
  const manifest = { buckets: Object.fromEntries([...buckets].map(([prefix, entries]) => [prefix, { documents: entries.length }])) }
  for (const document of documents) for (const word of document[4].flatMap(nameSearchTokens).filter((token) => token.length >= 2)) {
    const prefix = chooseNameSearchBucket(word, manifest)
    assert.ok(searchNameSearchDocuments(buckets.get(prefix), word).some(({ key }) => key === document[0]), word)
  }
})

test('rejects stale index references instead of generating misleading filter coverage', () => {
  assert.throws(() => createNameSearchDocuments([row(milad, 2, 0)], index), /unknown employer/)
  assert.throws(() => createNameSearchDocuments([row(milad, 0, 5)], index), /unknown reporting period/)
})

test('reuses immutable documents safely across queries and filters without sharing mutable result arrays', () => {
  const documents = createNameSearchDocuments([row(milad, 0, 0), row(milad, 1, 4), row('Smith, Jane')], index)
  for (const document of documents) {
    for (const at of [3, 4, 5]) Object.freeze(document[at])
    Object.freeze(document)
  }
  Object.freeze(documents)
  const first = searchNameSearchDocuments(documents, 'milad')
  assert.deepEqual(first[0].employerIds, [0, 1])
  assert.equal(searchNameSearchDocuments(documents, 'smith')[0].name, 'Smith, Jane')
  assert.deepEqual(searchNameSearchDocuments(documents, 'milad smith'), [])
  const [filtered] = searchNameSearchDocuments(documents, 'fathi', { employerIds: new Set([1]), yearIds: new Set([4]) })
  assert.deepEqual(filtered.employerIds, [1])
  assert.deepEqual(filtered.years, [4])
  first[0].spellings.push('Changed result')
  first[0].years.push(99)
  const [again] = searchNameSearchDocuments(documents, 'milad')
  assert.deepEqual(again.spellings, [milad])
  assert.deepEqual(again.years, [0, 4])
})

test('a whole typed surname ranks before hyphenated surnames and given names', () => {
  const documents = [
    ['armstrong smith|christine', 'Christine Armstrong-Smith', 0, [0], ['Armstrong-Smith, Christine'], ['ar']],
    ['smith|brad', 'Brad Smith', 0, [0], ['Smith, Brad'], ['sm']],
    ['jones|smith', 'Smith Jones', 0, [0], ['Jones, Smith'], ['jo']]
  ]
  assert.deepEqual(searchNameSearchDocuments(documents, 'smith').map(({ key }) => key), ['smith|brad', 'armstrong smith|christine', 'jones|smith'])
})
