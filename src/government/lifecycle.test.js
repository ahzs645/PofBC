// What a body's life says, and only that: an untraced end is not survival to today, operations that
// passed elsewhere are not a legal end, ownership is not accountability, and every view reads a life
// the same way (the integration review of 21 October 2026, research/reviews/integration-review-2026-10-21).

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { compareYears } from './compare.js'
import { canonicalId, episodeById } from './episodes.js'
import { eventsFor } from './events.js'
import { HISTORICAL_BODIES } from './historyData.js'
import { governmentIn, lifeOf, lifespanOf, lifeYears, pathToPeople, PRESENT_YEAR } from './snapshot.js'

const find = (year, id, options) => governmentIn(year, options).nodes.find((node) => node.id === id)
const BOARD = 'cariboo-regional-health-board'

test('a rural board with an untraced end stands as far as a source shows it, and no further', () => {
  // Designated 3 November 1994 (M339/1994); one of the twenty boards of M597/1995.
  assert.ok(!find(1993, BOARD))
  assert.ok(find(1994, BOARD) && find(1995, BOARD))
  assert.ok(!find(1996, BOARD, { includeUndated: false }), 'not confirmed after its last sighting')
  assert.ok(find(1996, BOARD, { includeUndated: true })?.uncertain, 'shown on the layer for bodies not confirmed that year')
  assert.ok(!find(PRESENT_YEAR, BOARD, { includeUndated: false }), 'a missing end is not survival to today')
})

test('an untraced end is said as such, and is not a proved end on an unknown day', () => {
  const board = HISTORICAL_BODIES.find((body) => body.id === BOARD)
  const life = lifespanOf(board)
  assert.equal(life.toKind, 'untraced')
  assert.equal(life.lastSeen, '1995-12-06')
  assert.equal(lifeYears(life), '1994–?')
  const timeline = lifeOf(BOARD)
  assert.equal(timeline.toKind, 'untraced')
  assert.equal(timeline.to, null)
})

test('MTOC stands after its operations passed to BC Transit, and does not close in 1985', () => {
  assert.ok(find(1985, 'metro-transit-operating-company', { includeUndated: false }))
  assert.ok(!compareYears(1984, 1985).bodies.closed.some((node) => node.id === 'metro-transit-operating-company'))
  const mtoc = HISTORICAL_BODIES.find((body) => body.id === 'metro-transit-operating-company')
  assert.equal(lifespanOf(mtoc).operationalEnd, '1985-06-01')
  assert.equal(lifespanOf(mtoc).toKind, 'untraced')
})

test('ownership is drawn as ownership, and is not a path to the people', () => {
  const government = governmentIn(PRESENT_YEAR)
  assert.deepEqual(government.edges.filter((edge) => edge.to === 'sub-powertech-labs').map((edge) => edge.kind), ['owned'])
  assert.deepEqual(pathToPeople(government, 'sub-powertech-labs'), [])
})

test('a body known only from a sighting is found, and says so', () => {
  const harbours = HISTORICAL_BODIES.find((body) => body.id === 'bc-harbours-board')
  assert.equal(lifeYears(lifespanOf(harbours)), 'known 1983–1985')
})

test('an event is found from every body it names, not only its subject', () => {
  assert.ok(eventsFor(['south-fraser-health-region']).some((event) => event.id === 'atlas:round4-gvrhd-dissolved-1999'))
})

test('a start with a source of its own cites it: BC Hydro from the 1962 proclamation', () => {
  const hydro = find(1970, 'bc-hydro')
  assert.match(hydro.evidence[0].source.url, /0839_1962/)
})

test('a period no source closes says what bounds it', () => {
  const ldb = find(1980, 'liquor-distribution-branch')
  assert.ok(ldb.evidence.some((claim) => /Answered to the Ministry of Consumer/.test(claim.claim) && /Capped at 1986/.test(claim.note)))
})

test('a link to the 1978 ministry under its old id still finds it', () => {
  const old = 'ministry-of-transportation-communication-and-highways-1978'
  assert.equal(canonicalId(old), 'ministry-of-transportation-communications-and-highways-1978')
  assert.equal(episodeById(old)?.name, 'Ministry of Transportation, Communications and Highways')
})

test('every ministry of every year has a minister, the Treasury under both its styles', () => {
  for (let year = 1871; year <= PRESENT_YEAR; year += 1) {
    for (const node of governmentIn(year).nodes) {
      if (node.kind === 'ministry') assert.ok(node.head?.person, `${node.id} in ${year} has no minister`)
    }
  }
  // "Minister of Finance and Agriculture" to June 1916, then "Minister of Finance".
  assert.ok(find(1905, 'treasury-department-1899').head.person)
  assert.ok(find(1920, 'treasury-department-1899').head.person)
})
