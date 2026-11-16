import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import {
  CATALOGUE_DIR, GROUPS, HOLDERS, MUNICIPALITIES, PROVINCE, PROVINCE_SPECIMENS, holderById, provinceSections
} from './armsData.js'

const root = fileURLToPath(new URL('../../', import.meta.url))
const imagesDir = fileURLToPath(new URL('./images/', import.meta.url))

test('the Province comes first, with its three designs', () => {
  assert.equal(HOLDERS[0], PROVINCE)
  assert.deepEqual(PROVINCE.stages.map(({ year }) => year), ['1895', '1906', '1987'])
  for (const stage of PROVINCE.stages) assert.ok(stage.sources.length > 0, `${stage.year} has a source`)
})

test('every catalogue specimen is shown once, in catalogue order, with its image on disk', () => {
  const numbers = PROVINCE_SPECIMENS.map(({ number }) => number)
  assert.deepEqual(numbers, [...numbers].sort((a, b) => a - b))
  assert.equal(new Set(numbers).size, numbers.length)
  const shown = provinceSections().flatMap(({ specimens }) => specimens)
  assert.equal(shown.length, PROVINCE_SPECIMENS.length)
  for (const item of PROVINCE_SPECIMENS) {
    assert.ok(existsSync(`${root}${CATALOGUE_DIR}/reference/${item.image}`), `${item.id}: ${item.image}`)
    assert.ok(item.sources.every(({ url }) => /^https:\/\//.test(url)), `${item.id} sources are links`)
  }
})

test('sections keep the catalogue order and carry no numbering', () => {
  const titles = provinceSections().map(({ title }) => title)
  assert.equal(new Set(titles).size, titles.length, 'each section appears once')
  for (const title of titles) assert.doesNotMatch(title, /^\d/)
})

test('every holder has a known group, a unique id and a primary source', () => {
  const groups = new Set(GROUPS.map(({ id }) => id))
  const ids = new Set()
  for (const holder of HOLDERS) {
    assert.ok(groups.has(holder.group), `${holder.id}: group ${holder.group}`)
    assert.ok(!ids.has(holder.id), `${holder.id} is unique`)
    ids.add(holder.id)
    assert.equal(holderById(holder.id), holder)
    const links = [holder.register?.url, ...(holder.sources ?? []).map(({ url }) => url)].filter(Boolean)
    assert.ok(links.length > 0, `${holder.id} cites a source`)
    for (const url of links) assert.match(url, /^https:\/\//, `${holder.id}: ${url}`)
  }
})

test('holder images exist and carry a credit', () => {
  for (const holder of HOLDERS) {
    if (!holder.image?.file) continue
    assert.ok(existsSync(`${imagesDir}${holder.image.file}`), `${holder.id}: ${holder.image.file}`)
    assert.ok(holder.image.credit, `${holder.id} credits its image`)
  }
})

test('municipal entries link to their register records', () => {
  for (const place of MUNICIPALITIES) {
    assert.ok(place.name, 'named')
    assert.match(place.url, /^https:\/\/www\.gg\.ca\//, place.name)
  }
})

test('an unknown holder is no holder', () => {
  assert.equal(holderById('nowhere'), null)
  assert.equal(holderById(null), null)
})
