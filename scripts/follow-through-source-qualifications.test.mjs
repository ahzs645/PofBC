import test from 'node:test'
import assert from 'node:assert/strict'
import { applyFollowThroughQualifications, qualificationMetadataFingerprint } from './lib/follow-through-source-qualifications.mjs'

const fixture = () => {
  const result = {
  sources: { new: { id: 'new', url: 'https://example.gov/report.pdf', year: '2020', periodType: 'calendar', periodStart: '2020-01-01', periodEnd: '2020-12-31', currency: 'CAD', sha256: 'a'.repeat(64), dataSha256: 'b'.repeat(64), sourceKind: 'official', scope: 'employee-remuneration', completeEmployeeSchedule: true, publicWarning: 'Printed expense residual preserved.', validation: {} } },
  employers: new Map([['new', ['example-employer']]]),
  review: { accepted: true, noOutreach: true, decisions: [{ sourceId: 'new', sourceSha256: 'a'.repeat(64), dataSha256: 'b'.repeat(64), approvedBy: 'root', completeEmployeeSchedule: true, retainCompiledPartition: true, reason: 'Compiled source scope and reporting period have not been established.' }] }
  }
  result.review.decisions[0].employerSlug = 'example-employer'
  result.review.decisions[0].metadataSha256 = qualificationMetadataFingerprint(result.sources.new, ['example-employer'])
  return result
}
test('new exact source qualification preserves source warning and requires retention', () => {
  const { sources, review, employers } = fixture()
  applyFollowThroughQualifications(sources, review, employers)
  assert.equal(sources.new.retainCompiledPartition, true)
  assert.equal(sources.new.validation.compiledPartitionRetained, true)
  assert.match(sources.new.publicWarning, /^Printed expense residual preserved\./)
})
test('changed source bytes, partial scope and unapproved duplicate decisions fail closed', () => {
  for (const change of [
    x => { x.sources.new.sha256 = 'c'.repeat(64) },
    x => { x.sources.new.dataSha256 = 'c'.repeat(64) },
    x => { x.sources.new.completeEmployeeSchedule = false },
    x => { x.sources.new.scope = 'board-remuneration' },
    x => { x.review.decisions[0].approvedBy = 'unreviewed' },
    x => { x.review.decisions.push({ ...x.review.decisions[0] }) }
  ]) {
    const f = fixture(); change(f)
    assert.throws(() => applyFollowThroughQualifications(f.sources, f.review, f.employers), /stale or invalid/)
  }
})
test('the same payments cannot be relabelled to a new period, currency or legal employer', () => {
  for (const change of [
    f => { Object.assign(f.sources.new, { year: '2021', periodStart: '2021-01-01', periodEnd: '2021-12-31' }) },
    f => { f.sources.new.currency = 'USD' },
    f => { f.employers.set('new', ['another-employer']) },
    f => { f.sources.new.threshold = 100000 }
  ]) {
    const f = fixture(); change(f)
    assert.throws(() => applyFollowThroughQualifications(f.sources, f.review, f.employers), /stale or invalid/)
  }
})
