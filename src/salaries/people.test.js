import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { nameMatch, personKey, readName, surnameShard } from './people.js'

const DIR = new URL('../../public/salaries/people/', import.meta.url)

test('a disclosed name is read as a surname and a first given name', () => {
  assert.deepEqual(readName('Wong, Christine, OnPui'), { surname: 'wong', given: 'christine', initial: 'c' })
  assert.deepEqual(readName('Hilde, C'), { surname: 'hilde', given: 'c', initial: 'c' })
  assert.deepEqual(readName("O'Brien-Smith, Ann Marie"), { surname: 'obriensmith', given: 'ann', initial: 'a' })
  assert.equal(surnameShard('Lee, Adelaide'), 'le')
  assert.equal(personKey('LEE, Adelaide M.'), personKey('Lee, Adelaide'))
})

test('a link between two rows says what it rests on', () => {
  assert.equal(nameMatch('Lee, Adelaide', 'Lee, Adelaide M'), 'name')
  assert.equal(nameMatch('Hilde, C', 'Hilde, Carol'), 'initial')
  assert.equal(nameMatch('Lee, Adelaide', 'Lee, Anne'), null)
  assert.equal(nameMatch('Lee, Adelaide', 'Leeds, Adelaide'), null)
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
  assert.deepEqual(index.years, ['2017/18', '2020/21', '2023/24'])
})
