import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { matchesNameQuery, nameMatch, personKey, readName, readNameQuery, surnameShard } from './people.js'

const DIR = new URL('../../public/salaries/people/', import.meta.url)

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

test('surname-first search accepts compound surnames without guessing identity', () => {
  const matches = (name, query) => readNameQuery(query)?.queries.some((candidate) => matchesNameQuery(name, candidate)) ?? false
  for (const query of ['van der meer', 'van der meer j', 'van der meer, j']) {
    assert.ok(matches('Van der Meer, Jane A', query), query)
    assert.equal(readNameQuery(query).shard, 'va')
  }
  assert.ok(matches('O Brien, Ann Marie', 'O Brien'))
  assert.ok(matches('O Brien, Ann Marie', 'O Brien Ann M'))
  assert.equal(readNameQuery('O Brien').shard, 'ob')
  assert.ok(matches('Tremblay, Émilie', 'Tremblay Emi'))
  assert.ok(matches('Smith, John A', 'Smith John A'))
  assert.equal(matches('Smith, John A', 'Smith John B'), false)
  assert.equal(matches('Smith, John', 'John Smith'), false)
  // A comma chooses a precise surname boundary, rather than another alternative.
  assert.equal(matches('Van der Meer, Jane', 'Van, der Meer'), false)
  assert.ok(matches('O, Jane', 'O, J'))
  assert.equal(readNameQuery('O, J').shard, 'o_')
  assert.equal(readNameQuery('O'), null)
  assert.equal(readNameQuery(''), null)
  assert.equal(readNameQuery(',Jane'), null)
  assert.notEqual(personKey('Van der Meer, Jane A'), personKey('Van der Meer, Jane B'))
})

test('the index’s slices hold every row it counts, each under its surname', () => {
  const index = JSON.parse(readFileSync(new URL('index.json', DIR)))
  const files = readdirSync(DIR).filter((name) => name.endsWith('.json.gzip'))
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
