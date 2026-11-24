import { test } from 'node:test'
import assert from 'node:assert/strict'
import { eventsFor, EVENT_SOURCES } from './events.js'
import { HISTORICAL_BODIES } from './historyData.js'

test('the two March 1981 endpoints are for distinct companies, not Vancouver Island Transit', () => {
  const holding = eventsFor(['ts-holdings']).find(event => event.id === 'atlas:subs-ts-struck-1981')
  const transit = eventsFor(['sub-thompson-okanagan-transit']).find(event => event.id === 'atlas:subs-tot-dissolved-1981')
  assert.deepEqual([holding.subject, transit.subject], ['ts-holdings', 'sub-thompson-okanagan-transit'])
  assert.ok([holding, transit].every(event => event.date.start === '1981-03-31' && event.type === 'dissolution'))
  assert.match(holding.locator, /9\(e\)/)
  assert.match(transit.locator, /9\(f\)/)
  assert.equal(HISTORICAL_BODIES.find(body => body.id === 'ts-holdings').ended, '1981-03-31')
  assert.ok(!eventsFor(['sub-vancouver-island-transit']).some(event => event.type === 'dissolution'))
})

test('Pacific Coach Lines company 178561 retains distinct operation, name and legal endpoints', () => {
  const body = HISTORICAL_BODIES.find(entry => entry.id === 'pacific-coach-lines')
  assert.equal(body.operationalEnd[0], '1984-03-31')
  assert.ok(body.names.some(([name, date]) => name === '178561 B.C. Ltd.' && date === '1990-07-19'))
  assert.equal(body.ended, '1993-06-11')
  const event = eventsFor([body.id]).find(entry => entry.id === 'atlas:subs-pcl-dissolved-1993')
  assert.equal(event.date.start, body.ended)
  assert.match(EVENT_SOURCES[event.sources[0]].url, /677380567#page=10$/)
  assert.match(event.notes, /no evidence about ownership at dissolution/)
})
