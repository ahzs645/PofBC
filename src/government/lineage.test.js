// The institutional-history research of 2026-10-21 (research/reviews/institutional-history-2026-10-21):
// the health authorities' named predecessors, and the line from a body to the people.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { EVENTS } from './events.js'
import { HISTORICAL_BODIES } from './historyData.js'
import { aroundCentre, CENTRE, SEAL_CLEARANCE } from './layout.js'
import { franchiseIn, governmentIn, pathToPeople, PEOPLE_ID } from './snapshot.js'

const find = (year, id) => governmentIn(year).nodes.find((node) => node.id === id)
const amalgamatedInto = (id) => HISTORICAL_BODIES.filter((body) => body.became === id && body.ended === '2001-12-12')

test('Schedule A of B.C. Reg. 293/2001 names 44 constituents, by authority', () => {
  const counts = Object.fromEntries(['fraser-health', 'interior-health', 'northern-health', 'vancouver-coastal-health', 'island-health'].map((id) => [id, amalgamatedInto(id).length]))
  assert.deepEqual(counts, { 'fraser-health': 3, 'interior-health': 17, 'northern-health': 13, 'vancouver-coastal-health': 5, 'island-health': 6 })
})

test('no generic 1997 node stands in for the predecessors, and PHSA is not a successor of the boards', () => {
  assert.ok(!HISTORICAL_BODIES.some((body) => body.id === 'regional-health-boards-1997'))
  const phsa = find(2005, 'provincial-health-services-authority')
  assert.equal(phsa.cameFrom.length, 0)
})

test('the societies passed on services, not amalgamated, and the Cariboo society’s went two ways', () => {
  const cariboo = find(2000, 'cariboo-community-health-services-society')
  assert.equal(cariboo.became, null)
  assert.deepEqual(cariboo.passedTo.map((body) => body.id).sort(), ['interior-health', 'northern-health'])
  assert.equal(cariboo.presence, 'seen')
  assert.ok(find(2002, 'northern-health').cameFrom.some((body) => body.id === 'cariboo-community-health-services-society'))
})

test('Northern Health reaches back through Northern Interior to Prince George’s council', () => {
  assert.ok(find(2002, 'northern-health').cameFrom.some((body) => body.id === 'northern-interior-regional-health-board'))
  const board = find(1995, 'northern-interior-regional-health-board')
  assert.equal(board.firstSeen, '1994-10-13')
  assert.ok(board.cameFrom.some((body) => body.id === 'prince-george-health-council' && body.established === '1995-03-24'))
  assert.equal(find(1995, 'prince-george-health-council')?.became?.id, 'northern-interior-regional-health-board')
})

test('a council whose start no source gives is not drawn, but is still what its board came from', () => {
  for (const year of [1994, 1995, 1996]) assert.ok(!find(year, 'new-westminster-health-council'))
  assert.ok(find(1998, 'simon-fraser-health-region').cameFrom.some((body) => body.id === 'new-westminster-health-council'))
})

test('the boundary change of March 2002 is its own event, not a rewrite of the 2001 destinations', () => {
  assert.equal(HISTORICAL_BODIES.find((body) => body.id === 'central-coast-transitional-health-authority').became, 'island-health')
  assert.ok(EVENTS.some((event) => event.subject === 'vancouver-coastal-health' && event.date.start === '2002-03-18'))
})

test('a health authority answers to the people through its ministry, the Premier and the Assembly', () => {
  const government = governmentIn(2010)
  const steps = pathToPeople(government, 'northern-health')
  const main = steps.filter((step) => step.route === 'main')
  assert.deepEqual(main.map((step) => step.kind), ['responsible', 'appoints', 'confidence', 'elects'])
  assert.equal(main.at(-1).from, PEOPLE_ID)
  assert.equal(main[2].from, 'legislative-assembly')
})

test('every route is kept: the Lieutenant Governor appoints the Premier beside the Assembly’s confidence', () => {
  const steps = pathToPeople(governmentIn(2010), 'northern-health')
  const also = steps.filter((step) => step.route === 'also')
  assert.deepEqual(also.map((step) => [step.from, step.to, step.kind]), [['lieutenant-governor', 'premier', 'appoints']])
})

test('the people’s line to the Assembly carries the seats they elect', () => {
  const government = governmentIn(2010)
  const elects = pathToPeople(government, 'northern-health').find((step) => step.kind === 'elects')
  assert.equal(elects.seats, government.election.totalSeats)
  assert.ok(elects.seats > 0)
})

test('a line that would cross the people bows round them; one that starts there does not', () => {
  const clear = (point) => Math.hypot(point.x - CENTRE.x, point.y - CENTRE.y)
  const a = { x: CENTRE.x - 200, y: CENTRE.y + 10 }
  const b = { x: CENTRE.x + 200, y: CENTRE.y + 10 }
  const control = aroundCentre(a, b)
  const mid = { x: 0.25 * a.x + 0.5 * control.x + 0.25 * b.x, y: 0.25 * a.y + 0.5 * control.y + 0.25 * b.y }
  assert.ok(Math.abs(clear(mid) - SEAL_CLEARANCE) < 1e-6)
  assert.ok(mid.y > CENTRE.y, 'it bows to the side the line was passing')
  assert.equal(aroundCentre({ ...CENTRE }, b), null)
  assert.equal(aroundCentre({ x: CENTRE.x - 200, y: CENTRE.y + 150 }, { x: CENTRE.x + 200, y: CENTRE.y + 150 }), null)
})

test('a partner and the Crown have no drawn line to the people', () => {
  const government = governmentIn(2015)
  assert.deepEqual(pathToPeople(government, 'first-nations-health-authority'), [])
  assert.deepEqual(pathToPeople(government, 'lieutenant-governor'), [])
})

test('a historical year says who the franchise left out', () => {
  assert.deepEqual(franchiseIn(1900).excluded, ['women', 'Chinese and South Asian Canadians', 'Japanese Canadians', 'First Nations people'])
  assert.deepEqual(franchiseIn(1948).excluded, ['Japanese Canadians', 'First Nations people'])
  assert.equal(franchiseIn(1960), null)
  assert.ok(find(1900, PEOPLE_ID).franchise)
})
