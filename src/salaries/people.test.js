import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { groupHighestPaidRecords, matchesNameQuery, nameMatch, nameQueryTier, nameReadings, personKey, readName, surnameShard } from './people.js'

const DIR = new URL('../../public/salaries/people/', import.meta.url)

const browseIndex = {
  employers: [['City A', 'Municipalities', null, 'city-a'], ['City B', 'Municipalities', null, 'city-b'], ['School', 'School districts', null, 'school']],
  sources: { official: { url: 'https://example.test/report.pdf', sourceKind: 'official-pdf' }, compiled: { scope: 'compiled-unverified', sourceKind: 'compiled' } }
}

test('people browse groups identical names per employer without merging initials or employers', () => {
  const rows = [
    ['Lee, Jane A.', null, 100, null, 0, 0, 'official'],
    ['LEE, JANE A', null, 110, null, 0, 1, 'official'],
    ['Lee, Jane A', null, 120, null, 1, 1, 'official'],
    ['Lee, J A', null, 130, null, 0, 1, 'official'],
    ['Lee, Jane B', null, 140, null, 0, 1, 'official']
  ]
  const groups = groupHighestPaidRecords(rows, browseIndex)
  assert.equal(groups.length, 4)
  const cityA = groups.find((group) => group.row[0] === 'LEE, JANE A')
  assert.deepEqual(cityA.records, rows.slice(0, 2))
  assert.deepEqual(cityA.years, [0, 1])
  assert.equal(cityA.row[2], 110, 'display the highest payment, never the sum')
})

test('people browse filters periods and sectors before choosing a payment', () => {
  const rows = [
    ['Lee, Jane', null, 100, null, 0, 0, 'official'],
    ['Lee, Jane', null, 200, null, 0, 1, 'official'],
    ['Lee, Jane', null, 300, null, 2, 0, 'official']
  ].map(Object.freeze)
  Object.freeze(rows)
  const groups = groupHighestPaidRecords(rows, { ...browseIndex, sector: 'Municipalities', range: [0, 0] })
  assert.equal(groups.length, 1)
  assert.equal(groups[0].row, rows[0])
  assert.deepEqual(groups[0].records, [rows[0]])
  assert.equal(groups[0].row[3], null)
})

test('equal payments prefer original sources without dropping the compiled observation', () => {
  const original = ['Lee, Jane', null, 100, 10, 0, 0, 'official']
  const compiled = ['Lee, Jane', null, 100, 11, 0, 1, 'compiled']
  for (const rows of [[original, compiled], [compiled, original]]) {
    const [group] = groupHighestPaidRecords(rows, browseIndex)
    assert.equal(group.row, original)
    assert.equal(group.records.length, 2)
    assert.deepEqual(group.years, [0, 1])
  }
  const higherCompiled = [...compiled]; higherCompiled[2] = 101
  assert.equal(groupHighestPaidRecords([original, higherCompiled], browseIndex)[0].row, higherCompiled, 'a higher compiled payment is not silently discarded')
})

test('same-period conflicting observations stay available without adding their amounts', () => {
  const rows = [
    ['Lee, Jane', 'Role A', 100, 10, 0, 0, 'official'],
    ['Lee, Jane', 'Role B', 200, 20, 0, 0, 'official']
  ]
  const [group] = groupHighestPaidRecords(rows, browseIndex)
  assert.deepEqual(group.records, rows)
  assert.equal(group.row, rows[1])
  assert.deepEqual(group.years, [0])
})

test('Surrey and Metro Vancouver browse overlaps each produce one group with all source rows retained', () => {
  const index = JSON.parse(readFileSync(new URL('index.json', DIR)))
  const top = JSON.parse(gunzipSync(readFileSync(new URL('top.json.gzip', DIR))))
  const rows = top.rows.filter((row) => ['2023', '2023/24'].includes(index.years[row[5]]))
  const groups = groupHighestPaidRecords(rows, { ...index, sector: 'Municipalities' })
  for (const [slug, name, pay, source] of [
    ['city-of-surrey', 'Lalonde, V', 750302.39, 'lower-mainland-surrey-2023-employees'],
    ['metro-vancouver', 'Dobrovolny, Jerry', 674527, 'sector-government-police-metro-vancouver-2023-employees']
  ]) {
    const employer = index.employers.findIndex((entry) => entry[3] === slug)
    const matching = groups.filter((group) => group.row[4] === employer && personKey(group.row[0]) === personKey(name))
    assert.equal(matching.length, 1)
    assert.equal(matching[0].row[2], pay)
    assert.equal(matching[0].row[6], source)
    assert.deepEqual(matching[0].records, rows.filter((row) => row[4] === employer && personKey(row[0]) === personKey(name)))
    assert.ok(matching[0].records.some((row) => row[6] === 'pssdb-2026-10-22'))
  }
})

test('a disclosed name is read as a surname and a first given name', () => {
  assert.deepEqual(readName('Wong, Christine, OnPui'), { surname: 'wong', given: 'christine', initial: 'c' })
  assert.deepEqual(readName('Hilde, C'), { surname: 'hilde', given: 'c', initial: 'c' })
  assert.deepEqual(readName("O'Brien-Smith, Ann Marie"), { surname: 'obriensmith', given: 'ann', initial: 'a' })
  assert.equal(surnameShard('Lee, Adelaide'), 'le')
  assert.notEqual(personKey('LEE, Adelaide M.'), personKey('Lee, Adelaide'))
  assert.equal(personKey('LEE, Adelaide M.'), personKey('Lee, Adelaide M'))
})

test('a link between two rows says what it rests on', () => {
  assert.equal(nameMatch('Lee, Adelaide', 'Lee, Adelaide M'), 'partial')
  assert.equal(nameMatch('Lee, Adelaide M', 'LEE, Adelaide M.'), 'name')
  assert.equal(nameMatch('Hilde, C', 'Hilde, Carol'), 'initial')
  assert.equal(nameMatch('Lee, Adelaide', 'Lee, Anne'), null)
  assert.equal(nameMatch('Lee, Adelaide', 'Leeds, Adelaide'), null)
  assert.equal(nameMatch('Baerg, Jennifer J', 'Baerg, Jennifer N'), null)
  assert.equal(nameMatch('Smith, J A', 'Smith, John B'), null)
  assert.equal(nameMatch('Smith, John A', 'Smith, John Andrew'), 'partial')
  assert.equal(nameMatch('Ono Santa', 'Ono, Santa'), null)
})

test('all disclosed given names remain separate and can be searched as token prefixes', () => {
  assert.notEqual(personKey('Baerg, Jennifer J'), personKey('Baerg, Jennifer N'))
  assert.notEqual(personKey('Chan, Vincent Wing Chuen'), personKey('Chan, Vincent Wing Ho'))
  assert.ok(matchesNameQuery('Chan, Vincent Wing Chuen', 'Chan, Vincent W'))
  assert.ok(matchesNameQuery('Wong, Christine, OnPui', 'Wong, Christine On'))
  assert.ok(matchesNameQuery('Tremblay, Émilie', 'Tremblay, Emi'))
  assert.equal(matchesNameQuery('Smith, John A', 'Smith, John B'), false)
  assert.ok(matchesNameQuery('Mo, BL', 'Mo, B. L.', 'surname-and-initials'))
  assert.equal(matchesNameQuery('Mo, BL', 'Mo, Belaid', 'surname-and-initials'), false)
})

test('a typed name is read surname first, then surname last, then as a longer surname', () => {
  assert.deepEqual(nameReadings('smith').map((each) => each.typed), ['smith,'])
  assert.deepEqual(nameReadings('john smith').map((each) => each.typed), ['john,smith', 'smith,john', 'john smith,'])
  assert.deepEqual(nameReadings('Smith, J').map((each) => each.typed), ['Smith,J'])
  const longer = nameReadings('maria de la cruz').map((each) => each.typed)
  assert.equal(longer[0], 'maria,de la cruz')
  assert.equal(longer[1], 'cruz,maria de la')
  assert.ok(longer.includes('de la cruz,maria'))
  assert.deepEqual(nameReadings('a b').map((each) => each.typed), ['a b,'], 'single letters only as one surname')
  assert.deepEqual(nameReadings('  '), [])
})

test('a search ranks a full name before a beginning, and a beginning before initials alone', () => {
  assert.equal(nameQueryTier('Smith, John', 'smith,john'), 0)
  assert.equal(nameQueryTier('Smith, John A', 'smith,john'), 0)
  assert.equal(nameQueryTier('Smith, Mary', 'smith,'), 0)
  assert.equal(nameQueryTier('Smith, Johnny', 'smith,john'), 1)
  assert.equal(nameQueryTier('Smithers, John', 'smith,john'), 1)
  assert.equal(nameQueryTier('Smith, J', 'smith,john'), 2)
  assert.equal(nameQueryTier('Smith, J B', 'smith,john a'), null)
  assert.equal(nameQueryTier('Smith, Jane', 'smith,john'), null)
  assert.equal(nameQueryTier('Smithers, J', 'smith,john'), null)
  assert.equal(nameQueryTier('Mo, BL', 'mo,bl', 'surname-and-initials'), 0)
  assert.equal(nameQueryTier('Mo, BL', 'mo,b', 'surname-and-initials'), 1)
  assert.equal(nameQueryTier('Mo, BL', 'mo,belaid', 'surname-and-initials'), 2)
})

test('a surname of more than one word is found, and a comma fixes where the surname ends', () => {
  const matches = (name, query) => nameReadings(query).some((reading) => matchesNameQuery(name, reading.typed))
  for (const query of ['van der meer', 'van der meer j', 'van der meer, j']) assert.ok(matches('Van der Meer, Jane A', query), query)
  assert.ok(matches('O Brien, Ann Marie', 'O Brien'))
  assert.ok(matches('O Brien, Ann Marie', 'O Brien Ann M'))
  assert.ok(matches('Tremblay, Émilie', 'Tremblay Emi'))
  assert.ok(matches('Smith, John A', 'Smith John A'))
  assert.equal(matches('Smith, John A', 'Smith John B'), false)
  // "John Smith" is read surname first, and only after that the other way round.
  assert.equal(matchesNameQuery('Smith, John', nameReadings('John Smith')[0].typed), false)
  assert.ok(matches('Smith, John', 'John Smith'))
  // A comma chooses a precise surname boundary, rather than another alternative.
  assert.equal(matches('Van der Meer, Jane', 'Van, der Meer'), false)
  assert.ok(matches('O, Jane', 'O, J'))
  assert.equal(surnameShard(`${nameReadings('O, J')[0].surname},`), 'o_')
  assert.deepEqual(nameReadings('O'), [])
  assert.deepEqual(nameReadings(',Jane'), [])
  assert.notEqual(personKey('Van der Meer, Jane A'), personKey('Van der Meer, Jane B'))
})

test('the index’s slices hold every row it counts, each under its surname', () => {
  const index = JSON.parse(readFileSync(new URL('index.json', DIR)))
  // top.json.gzip is the landing page's highest-paid list, not a surname slice.
  const files = readdirSync(DIR).filter((name) => name.endsWith('.json.gzip') && name !== 'top.json.gzip')
  assert.equal(files.length, Object.keys(index.shards).length)
  let total = 0
  for (const file of files) {
    const shard = file.replace('.json.gzip', '')
    const rows = JSON.parse(gunzipSync(readFileSync(new URL(file, DIR))))
    assert.equal(rows.length, index.shards[shard], shard)
    for (const row of rows.slice(0, 50)) {
      assert.equal(surnameShard(row[0]), shard)
      assert.ok(index.employers[row[4]] && index.years[row[5]], shard)
    }
    total += rows.length
  }
  assert.ok(total > 350000)
  for (const year of ['2017/18', '2020/21', '2023/24']) assert.ok(index.years.includes(year), year)
  assert.equal(new Set(index.years).size, index.years.length)
})

test('a name is shown as a person is called, and a position however it was spelled is one', async () => {
  const { displayName, positionKey } = await import('./people.js')
  assert.equal(displayName('Moa, Belaid'), 'Belaid Moa')
  assert.equal(displayName('Hilde, C'), 'C. Hilde')
  assert.equal(displayName('SMITH, JOHN A'), 'John A. Smith')
  assert.equal(displayName('Mo, BL', 'surname-and-initials'), 'B. L. Mo')
  assert.equal(displayName('DELA CRUZ, K. T.', 'surname-and-initials'), 'K. T. Dela Cruz')
  assert.equal(displayName('MO, BELAID'), 'Belaid Mo')
  assert.equal(displayName('WONG, CHRISTINE ONPUI'), 'Christine Onpui Wong')
  assert.equal(positionKey('Correction Serv 18 ADLT CUST'), positionKey('Correction Serv 18 Adlt Cust.'))
})

test('employer coverage distinguishes excluded compiled years from verified replacements', () => {
  const index = JSON.parse(readFileSync(new URL('../../public/salaries/employers/index.json', import.meta.url)))
  const hydro = index.employers.find((entry) => entry.slug === 'bc-hydro')
  const year = index.years.indexOf('2020/21')
  assert.ok(year >= 0)
  if (hydro.counts[year] > 0) {
    assert.equal(hydro.coverage[year].status, 'available')
    assert.ok(hydro.coverage[year].sourceIds.some((id) => index.sources[id]?.url))
  } else {
    assert.ok(hydro.repeated.includes('2020/21'))
  }
})
