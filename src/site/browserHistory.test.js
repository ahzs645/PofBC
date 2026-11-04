import { test } from 'node:test'
import assert from 'node:assert/strict'
import { writeHistory } from './browserHistory.js'

test('page navigation preserves the previous entry and edits preserve its Back metadata', () => {
  const previousHistory = globalThis.history
  const previousLocation = globalThis.location
  const entries = [{ href: 'https://example.org/?view=salaries', state: null }]
  globalThis.location = { href: entries[0].href }
  globalThis.history = {
    get state() { return entries.at(-1).state },
    pushState(state, _, href) { entries.push({ href, state }); globalThis.location.href = href },
    replaceState(state, _, href) { entries[entries.length - 1] = { href, state }; globalThis.location.href = href }
  }
  try {
    const detail = 'https://example.org/?view=salaries&employer=example'
    const state = { salaryTrail: [{ label: 'Salaries' }] }
    assert.equal(writeHistory(detail, { state }), true)
    assert.equal(entries.length, 2)
    assert.equal(entries[0].href, 'https://example.org/?view=salaries')
    assert.equal(writeHistory(detail), false)
    assert.equal(entries.length, 2, 'reselecting the same page must not create a Back trap')
    writeHistory(`${detail}&employer-year=2024`, { replace: true })
    assert.equal(entries.length, 2)
    assert.deepEqual(entries.at(-1).state, state)
    writeHistory('https://example.org/?view=gallery')
    assert.equal(entries.length, 3)
    assert.equal(entries.at(-1).state, null, 'another view must not inherit the salary trail')
  } finally {
    if (previousHistory === undefined) delete globalThis.history
    else globalThis.history = previousHistory
    if (previousLocation === undefined) delete globalThis.location
    else globalThis.location = previousLocation
  }
})
