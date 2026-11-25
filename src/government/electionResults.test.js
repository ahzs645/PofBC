import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ELECTION_RESULTS_2026 } from './atlasData.js'
import { BODY_CHECKED, CURRENT_AS_OF } from './currentData.js'
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
  assert.equal(BODY_CHECKED, '2026-09-25')
  assert.equal(CURRENT_AS_OF, '2026-11-25')
  assert.equal(ELECTION_RESULTS_2026.checkedOn, '2026-11-25')
  assert.equal(ELECTION_RESULTS_2026.status, 'judicial_recounts_complete')
  assert.equal(governmentIn(PRESENT_YEAR).premier.name, 'Lorne Doerkson')
  assert.ok(ELECTION_RESULTS_2026.candidates.every((row) => !row.swornIn && !row.appointmentDate))
})

test('the cabinet and its responsibility paths change at the November handover', () => {
  const today = governmentIn(2026)
  const ministries = today.nodes.filter((node) => node.kind === 'ministry')
  assert.equal(ministries.length, 18)
  assert.ok(ministries.every((node) => node.head?.since === '2026-11-20' && node.deputy && node.mandate))
  assert.equal(ministries.flatMap((node) => node.ministersOfState).length, 6)
  assert.equal(ministries.flatMap((node) => node.parliamentarySecretaries).length, 12)
  assert.equal(today.election.parliament, 44)
  assert.equal(today.dissolved, false)
  const assignments = [
    ['icbc', 'ministry-of-finance-2001', 'responsible'],
    ['skilledtradesbc', 'ministry-of-economic-development-and-tourism-2026', 'responsible'],
    ['sub-real-property-division', 'ministry-of-citizens-services-and-technology-2026', 'part'],
    ['sub-gender-equity-office', 'ministry-of-attorney-general-2017', 'part']
  ]
  for (const [body, parent, kind] of assignments) {
    const links = today.edges.filter((edge) => edge.to === body && edge.kind === kind)
    assert.deepEqual(links.map((edge) => edge.from), [parent])
    assert.ok(today.nodes.find((node) => node.id === body).evidence.some((row) => row.source.url.includes('0421_2026')))
  }
  const before = governmentIn(2025)
  assert.equal(before.premier.name, 'David Eby')
  assert.ok(before.edges.some((edge) => edge.from === 'ministry-of-post-secondary-education-and-future-skills-2022' && edge.to === 'skilledtradesbc'))
})
