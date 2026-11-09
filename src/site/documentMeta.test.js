import test from 'node:test'
import assert from 'node:assert/strict'
import { DEFAULT_TITLE, documentTitle } from './documentMeta.js'

test('page titles name the page, then the site', () => {
  assert.equal(documentTitle('UNBC', 'Salaries'), 'UNBC · Salaries — Province of BC')
  assert.equal(documentTitle(null, 'Salaries'), 'Salaries — Province of BC')
  assert.equal(documentTitle(), DEFAULT_TITLE)
})
