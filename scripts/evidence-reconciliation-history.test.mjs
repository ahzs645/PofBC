import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const read = (file) => JSON.parse(readFileSync(new URL(`../${file}`, import.meta.url), 'utf8'))
const events = (file) => read(`research/atlas/${file}`).events

test('BCEC operating end, statutory dissolution and registry status remain distinct', () => {
  const bodies = read('research/history/bodies.json').records
  const bcec = bodies.find((body) => body.id === 'bc-enterprise-corporation')
  const pavco = bodies.find((body) => body.id === 'bc-pavilion-corporation')
  assert.equal(bcec.becameId, null)
  assert.equal(bcec.ended, '1989-09-30')
  assert.equal(pavco.established, '1984-05-03')
  assert.ok(!pavco.predecessorIds.includes(bcec.id))
  const transfer = events('events-bcplace-jibc-2026-11-12.json').find((event) => event.id === 'atlas:bcplace-jibc-stadium-to-pavco-1989')
  assert.equal(transfer.event_type, 'asset_transfer')
  assert.ok(transfer.related_subject_ids.includes(pavco.id))
  const dissolution = events('events-corporate-reconciliation-2026-11-12.json').find((event) => event.event_type === 'dissolution')
  assert.equal(dissolution.date.start, '2023-03-13')
  const registry = events('events-round4.json').find((event) => event.id === 'atlas:round4-bcec-administratively-dissolved-2023')
  assert.equal(registry.event_type, 'registry_status_observed')
  assert.equal(registry.date.start, '2023-03-27')
})

test('BC Rail uses contemporary transaction evidence and preserves the attributed later date', () => {
  const transaction = events('events-bc-rail-2026-11-12.json').find((event) => event.id === 'atlas:bcrail-cn-lease-2004')
  assert.equal(transaction.date.start, '2004-07-14')
  assert.match(transaction.evidence.source_url, /^https:\/\/www2\.gov\.bc\.ca\//)
  assert.equal(transaction.superseded_assertion.date.start, '2004-07-15')
  const claim = events('events-railway-identity.json').find((event) => event.id === 'atlas:railway-cn-operational-transition-2004-07-15')
  assert.equal(claim.event_type, 'retrospective_date_claim')
  assert.equal(claim.date.start, '2004-07-15')
  assert.match(claim.title, /TSB/)
  const gallery = read('research/identity/railway-history-2026-11-12/history.json').events.find((event) => event.id === 'railway-cn-transaction')
  assert.match(gallery.description, /discrepancy does not establish a separate/)
  assert.ok(gallery.sources.some((source) => source.url.includes('sec.gov/Archives/edgar/')))
})
