import assert from 'node:assert/strict'
import { test } from 'node:test'
import { MINISTRIES, MINISTRY_GROUPS, isKnownMinistry, searchMinistries } from './ministries.js'

test('the flat list and the grouped list hold the same names', () => {
  assert.equal(MINISTRIES.length, MINISTRY_GROUPS.flatMap((group) => group.options).length)
  assert.ok(MINISTRIES.includes('Ministry of Forests'))
  assert.equal(new Set(MINISTRIES).size, MINISTRIES.length, 'no duplicates')
})

test('an empty query returns everything, ungrouped and unfiltered', () => {
  assert.deepEqual(searchMinistries(''), MINISTRY_GROUPS)
  assert.deepEqual(searchMinistries(null), MINISTRY_GROUPS)
})

test('search ignores case, apostrophes and dashes', () => {
  // Typing "citizens services" should find "Ministry of Citizens’ Services": nobody reproduces a
  // curly apostrophe from memory, and the difference is invisible in a search box.
  const byPlainText = searchMinistries('citizens services')
  assert.deepEqual(byPlainText.flatMap((group) => group.options), ['Ministry of Citizens’ Services'])

  const hyphenated = searchMinistries('post secondary')
  assert.ok(hyphenated.flatMap((group) => group.options)[0].includes('Post-Secondary'))

  assert.equal(searchMinistries('FORESTS').flatMap((group) => group.options).length, 1)
})

test('empty groups are dropped from the results', () => {
  const results = searchMinistries('premier')
  assert.ok(results.every((group) => group.options.length > 0))
  assert.deepEqual(results.flatMap((group) => group.options), ['Office of the Premier'])
})

test('a query matching nothing returns nothing rather than everything', () => {
  assert.deepEqual(searchMinistries('ministry of magic'), [])
})

test('membership ignores the same punctuation the search does', () => {
  assert.equal(isKnownMinistry('Ministry of Forests'), true)
  assert.equal(isKnownMinistry("Ministry of Citizens' Services"), true, 'straight apostrophe')
  assert.equal(isKnownMinistry('  ministry of forests  '), true)
  assert.equal(isKnownMinistry('Ministry of Magic'), false)
})
