import { test } from 'node:test'
import assert from 'node:assert/strict'
import { glance } from './glance.js'

test('a glance keeps what can be scanned and holds back the prose', () => {
  const facts = { facts: [['Date', 'not established']] }
  const palette = { palette: [{ name: 'Green', value: '#003E2D' }] }
  const links = { links: [{ label: 'The ministry', to: { view: 'government' } }] }
  const blocks = ['A paragraph.', facts, palette, { note: 'A caveat.' }, { h: 'Where it sat' }, links, { sources: [] }]
  const { kept, held } = glance(blocks)
  assert.deepEqual(kept, [facts, palette, { h: 'Where it sat' }, links])
  assert.equal(held, 3)
})

test('only the first table of facts is kept, and a heading goes with the block it heads', () => {
  const first = { facts: [['A', '1']] }
  const second = { facts: [['B', '2']] }
  const { kept } = glance([first, { h: 'More measurements' }, second, { h: 'Trailing' }])
  assert.deepEqual(kept, [first])
})

test('a panel with nothing held back needs no toggle', () => {
  assert.equal(glance([]).held, 0)
  assert.equal(glance([{ palette: [] }]).held, 0)
})
