import test from 'node:test'
import assert from 'node:assert/strict'
import { merge, validate } from './merge-research.mjs'

const known = new Set(['gender-equity-office'])
const observation = { date: '2020', precision: 'year', evidence: 'estimates', source: 'https://www.bcbudget.gov.bc.ca/2020/pdf/2020_Estimates.pdf', locator: 'p. 81, sub-vote list', meaning: 'Listed; not a founding claim' }
const record = (extra = {}) => ({
  id: 'gender-equity-office',
  first_observed: observation,
  names: [{ name: 'Gender Equity Office', observed_on: '2020', coverage: 'observation_only', evidence: 'estimates', source: observation.source, locator: observation.locator }],
  parents: [{ ministry_as_printed: 'Ministry of Finance', relation: 'part_of', observed_on: '2020', coverage: 'observation_only', source: observation.source, locator: observation.locator }],
  review: { checked: '2026-10-01', sources_checked: [{ source: 'https://www.bcbudget.gov.bc.ca/2015/estimates/2015_Estimates.pdf', year: '2015', listed: false }] },
  ...extra
})

test('a well-formed batch passes', () => {
  assert.deepEqual(validate({ records: [record()] }, { known }).errors, [])
})

test('a year padded to a day, a missing locator and funding recorded as a parent are refused', () => {
  const { errors } = validate({
    records: [record({
      established: { date: '2019-01-01', precision: 'year', source: 'https://example.org' },
      parents: [{ ministry_as_printed: 'Ministry of Finance', relation: 'funded_by', coverage: 'observation_only', observed_on: '2020', source: 'https://example.org', locator: 'p. 1' }]
    })]
  }, { known })
  assert.ok(errors.some((e) => /does not match precision/.test(e)))
  assert.ok(errors.some((e) => /no locator/.test(e)))
  assert.ok(errors.some((e) => /is not parentage/.test(e)))
})

test('a body outside the queue, or a check without a result, is refused', () => {
  const { errors } = validate({ records: [record({ id: 'made-up-branch', review: { checked: '2026-10-01', sources_checked: [{ source: 'x' }] } })] }, { known })
  assert.ok(errors.some((e) => /not a sub-agency in the queue/.test(e)))
  assert.ok(errors.some((e) => /listed must be true or false/.test(e)))
})

test('an unresolved check carries its outcome, and the outcome must agree with listed', () => {
  const check = (extra) => validate({ records: [record({ review: { checked: '2026-10-01', sources_checked: [{ source: 'x', scope: 'Vote 32', ...extra }] } })] }, { known }).errors
  assert.deepEqual(check({ listed: null, outcome: 'function_only' }), [])
  assert.ok(check({ listed: true, outcome: 'not_found_in_scope' }).some((e) => /needs listed false/.test(e)))
  assert.ok(check({ listed: null, outcome: 'maybe' }).some((e) => /outcome must be one of/.test(e)))
})

test('merging keeps the earliest sighting, the negative checks, and a competing start beside the held one', () => {
  const research = { records: [{ id: 'gender-equity-office', name: 'Gender Equity Office', established: { date: '2018', precision: 'year', source: 'a', locator: 'p. 1' }, first_observed: { date: '2022', precision: 'year' }, names: [], parents: [], review: { checked: '2026-09-26' } }], gone: [] }
  const catalogue = { sources: [] }
  merge(research, catalogue, { records: [record({ established: { date: '2017', precision: 'year', source: 'b', locator: 'p. 2' } })], sources: [{ id: 'est-2020', url: observation.source }] })
  const held = research.records[0]
  assert.equal(held.first_observed.date, '2020')
  assert.equal(held.established.date, '2018')
  assert.equal(held.date_claims[0].date, '2017')
  assert.equal(held.evidence_status, 'requires_reconciliation')
  assert.equal(held.review.sources_checked[0].listed, false)
  assert.equal(held.review.checked, '2026-10-01')
  assert.equal(catalogue.sources.length, 1)
  // Merging the same batch twice changes nothing more.
  const before = JSON.stringify(research)
  merge(research, catalogue, { records: [record({ established: { date: '2017', precision: 'year', source: 'b', locator: 'p. 2' } })], sources: [{ id: 'est-2020', url: observation.source }] })
  assert.equal(JSON.stringify(research), before)
})
