import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ELECTION_RESULTS_2026 } from './atlasData.js'
import { CURRENT_AS_OF } from './currentData.js'
import { governmentIn, PRESENT_YEAR } from './snapshot.js'

test('the official final-count roster reconciles to 93 distinct districts and declared party totals', () => {
  const results = ELECTION_RESULTS_2026
  assert.equal(results.candidates.length, 93)
  assert.equal(new Set(results.candidates.map((row) => row.district)).size, 93)
  const totals = results.candidates.reduce((out, row) => { out[row.party] = (out[row.party] ?? 0) + 1; return out }, {})
  assert.deepEqual(totals, results.parties)
  assert.deepEqual(results.parties, { 'BC Green Party': 2, 'BC NDP': 27, 'Conservative Party': 64 })
  assert.deepEqual(results.candidates.filter((row) => row.judicialRecountRequired).map((row) => row.district).sort(), ['Kelowna Centre', 'Ladysmith-Oceanside'])
})

test('new election evidence retains its own date without falsely refreshing government offices', () => {
  assert.equal(CURRENT_AS_OF, '2026-09-25')
  assert.equal(ELECTION_RESULTS_2026.checkedOn, '2026-11-12')
  assert.equal(ELECTION_RESULTS_2026.status, 'declared_results_subject_to_judicial_recounts')
  assert.equal(governmentIn(PRESENT_YEAR).premier.name, 'David Eby')
  assert.ok(ELECTION_RESULTS_2026.candidates.every((row) => !row.swornIn && !row.appointmentDate))
})
