import { test } from 'node:test'
import assert from 'node:assert/strict'
import { monarchOn } from './monarchs.js'
import { governmentIn } from './snapshot.js'

test('the monarch is whoever reigned on the day, from the day of accession', () => {
  assert.equal(monarchOn('1871-12-31').name, 'Victoria')
  assert.equal(monarchOn('1901-01-21').name, 'Victoria')
  assert.equal(monarchOn('1901-01-22').name, 'Edward VII')
  assert.equal(monarchOn('1936-12-31').name, 'George VI')
  assert.equal(monarchOn('2022-09-07').title, 'Queen')
  assert.equal(monarchOn('2022-09-08').title, 'King')
})

test('the Lieutenant Governor represents the King or the Queen of the year', () => {
  const crownIn = (year) => governmentIn(year).nodes.find((node) => node.id === 'lieutenant-governor')
  assert.match(crownIn(1880).description, /^The Queen’s representative/)
  assert.match(crownIn(1930).description, /^The King’s representative/)
  assert.match(crownIn(1990).description, /^The Queen’s representative/)
  assert.match(crownIn(2024).description, /^The King’s representative/)
})
