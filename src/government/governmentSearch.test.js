import { test } from 'node:test'
import assert from 'node:assert/strict'
import { buildSearchIndex, search } from './governmentSearch.js'

const names = (query) => search(query).map((result) => result.name)

test('a body that still runs is listed once, not once from today and again from its history', () => {
  const found = names('northern development')
  assert.equal(found.filter((name) => name === 'Northern Development Initiative Trust').length, 1)
  // Today's entry, which opens the body now, borrows its years from the history.
  const trust = search('northern development initiative').find((result) => result.name === 'Northern Development Initiative Trust')
  assert.equal(trust.year > 2020, true)
  assert.equal(trust.detail, '2004–')
})

test('no organization appears twice under one id', () => {
  const index = buildSearchIndex().filter((entry) => !entry.minister)
  const ids = index.map((entry) => entry.id)
  assert.deepEqual(ids.filter((id, at) => ids.indexOf(id) !== at), [])
})

test('every result has a unique key, ministers included', () => {
  const keys = buildSearchIndex().map((entry) => entry.key)
  assert.equal(new Set(keys).size, keys.length)
})

test('distinct bodies that share a name stay apart, with their own years', () => {
  const boards = search('labour relations board').filter((result) => result.name === 'Labour Relations Board')
  assert.equal(boards.length, 2)
  assert.notEqual(boards[0].detail, boards[1].detail)
})
