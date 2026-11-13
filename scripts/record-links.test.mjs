import { test } from 'node:test'
import assert from 'node:assert/strict'
import { checkRecordLinks } from './check-record-links.mjs'
import { EVENTS } from '../src/government/eventsData.js'

test('all organization links, typed event links and source indexes resolve', () => {
  assert.deepEqual(checkRecordLinks().issues, [])
})

test('an unmodelled historical organization remains an explicit research gap', () => {
  const event = EVENTS.find((entry) => entry.id === 'atlas:coroners-in-embc-2007')
  assert.ok(!event.related.includes('emergency-management-bc'))
  assert.equal(event.unresolvedRelated[0].label, 'Emergency Management B.C.')
  assert.match(event.unresolvedRelated[0].reason, /different body/)
})

test('event IDs and legal locators never become organization IDs', () => {
  const parks = EVENTS.find((entry) => entry.id === 'atlas:parks-branch-1957-03-28')
  assert.deepEqual(parks.relatedEvents, ['pkg:parks-branch-1957'])
  const repeal = EVENTS.find((entry) => entry.id === 'atlas:pgt-public-trustee-act-repealed-2000')
  assert.equal(repeal.legalReferences[0].original_reference, 'A40:s.29')
  assert.ok(!repeal.related?.includes('A40:s.29'))
})
