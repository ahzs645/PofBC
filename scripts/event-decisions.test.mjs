import { test } from 'node:test'
import assert from 'node:assert/strict'
import { digest, eventCollector, ledger } from './evidence-integrity.mjs'
import { collectEventAssertions } from './lib/event-decisions.mjs'

const assertion = (origin, date, title, source = 0) => ({ origin, input: { originalDate: date, title, sourceUrl: `https://example.test/${source}` }, event: {
  id: 'same-event', subject: 'some-body', type: 'identity_change', title, notes: null,
  date: { start: date, end: null, precision: date.length === 4 ? 'year' : 'day', inclusive: false },
  status: 'source_reported_past', sources: [source], locator: origin, reviewed: '2026-11-12'
} })
const choice = { id: 'reviewed-event', subject: 'events/same-event', field: 'preferred_assertion',
  value: { origin: 'precise', corroboratingOrigins: ['coarse'] }, reason: 'A dated announcement refines the official year summary.', decided: '2026-11-12' }
const pinned = (inputs, decision = choice) => ({ ...decision, value: { ...decision.value,
  inputDigests: Object.fromEntries(inputs.map((item) => [item.origin, digest(item.input)])) } })

test('a reviewed refinement retains both original dates and sources without duplicate events', () => {
  const accounting = ledger(); const collector = eventCollector(accounting)
  const inputs = [assertion('coarse', '2017', 'A yearly summary'), assertion('precise', '2017-11-15', 'The announcement', 1)]
  collectEventAssertions(inputs, [pinned(inputs)], collector)
  assert.equal(collector.events.length, 1)
  assert.equal(collector.events[0].date.start, '2017-11-15')
  assert.deepEqual(collector.events[0].sources, [0, 1])
  assert.equal(collector.events[0].evidence.find((e) => e.origin === 'coarse').date.start, '2017')
  assert.deepEqual(accounting.rows.map((row) => row.input.originalDate).sort(), ['2017', '2017-11-15'])
})

test('similar dates remain conflicting without an explicit reviewed decision', () => {
  const collector = eventCollector(ledger())
  collectEventAssertions([assertion('coarse', '2017', 'Yearly summary'), assertion('precise', '2017-11-15', 'Announcement')], [], collector)
  assert.equal(collector.events.length, 2)
  assert.ok(collector.events.every((event) => event.status === 'conflicting'))
})

test('a changed source, missing origin or incompatible date cannot silently reuse an old decision', () => {
  for (const inputs of [
    [assertion('coarse', '2018', 'Other year'), assertion('precise', '2017-11-15', 'Announcement')],
    [assertion('coarse', '2017', 'Summary')],
    [assertion('coarse', '2017-11-14', 'Other day'), assertion('precise', '2017-11-15', 'Announcement')]
  ]) assert.throws(() => collectEventAssertions(inputs, [pinned(inputs)], eventCollector(ledger())))
  const inputs = [assertion('coarse', '2017', 'Summary'), assertion('precise', '2017-11-15', 'Announcement')]
  inputs[0].event.subject = 'different-body'
  assert.throws(() => collectEventAssertions(inputs, [pinned(inputs)], eventCollector(ledger())), /Incompatible/)
})

test('a reviewed source URL, wording or status change requires a fresh decision', () => {
  for (const field of ['title', 'sourceUrl', 'notes', 'status']) {
    const inputs = [assertion('coarse', '2017', 'Summary'), assertion('precise', '2017-11-15', 'Announcement')]
    const reviewed = pinned(inputs)
    inputs[0].input[field] = 'changed'
    assert.throws(() => collectEventAssertions(inputs, [reviewed], eventCollector(ledger())), /changed or was not pinned/)
  }
})

test('duplicate decision IDs are refused before any assertion can be dropped', () => {
  const inputs = [assertion('coarse', '2017', 'Summary'), assertion('precise', '2017-11-15', 'Announcement')]
  const review = pinned(inputs)
  assert.throws(() => collectEventAssertions(inputs, [review, review], eventCollector(ledger())), /Duplicate event decision ID/)
})

test('exclusive date boundaries are not widened during refinement', () => {
  const inputs = [assertion('coarse', '2017-01-01', 'Interval'), assertion('precise', '2017-11-15', 'Announcement')]
  inputs[0].event.date.end = '2017-11-15'
  assert.throws(() => collectEventAssertions(inputs, [pinned(inputs)], eventCollector(ledger())), /Incompatible/)
  inputs[0].event.date.inclusive = true
  const collector = eventCollector(ledger())
  collectEventAssertions(inputs, [pinned(inputs)], collector)
  assert.equal(collector.events.length, 1)
})

test('repeated unadjudicated origins keep the collector’s existing preservation behavior', () => {
  const accounting = ledger(), collector = eventCollector(accounting)
  collectEventAssertions([assertion('repeated', '2017', 'One assertion'), assertion('repeated', '2018', 'Another')], [], collector)
  assert.equal(accounting.rows.length, 2)
  assert.equal(collector.events.length, 2)
})
