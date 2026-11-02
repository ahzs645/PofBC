import test from 'node:test'
import assert from 'node:assert/strict'
import { nameRecordFingerprint, nameRowsFingerprint, validateReviewedNameConnections } from './lib/reviewed-name-connections.mjs'

const original = ['Murthy,Srinivasa', null, 351290, 11382, 0, 0, 'official', 180]
const retained = ['Murtby, Srinivasa', null, 351290, 11382, 0, 0, 'compiled', null]
const index = { years: ['2023/24'], employers: [['PHSA', 'Health authorities', null, 'phsa']],
  sources: { official: { url: 'https://example.test/report.pdf', sourceKind: 'official-pdf', sha256: 'pdf-hash' }, compiled: { sourceKind: 'compiled' } } }
const payload = () => ({ schemaVersion: 1, decisions: [{ employer: 'phsa', names: [retained[0], original[0]],
  preferredName: original[0], decision: 'verified', evidence: [{ sourceId: 'official', pdfPage: 180 }],
  proof: { compiledNameKey: 'murtby|srinivasa', compiledRowsSha256: nameRowsFingerprint([retained], index),
    witnesses: [{ rowSha256: nameRecordFingerprint(original, index), sourceId: 'official', pdfSha256: 'pdf-hash', pdfPage: 180 }] } }] })

test('a reviewed spelling requires the complete retained row and original witness, preserving both', () => {
  const rows = [Object.freeze([...original]), Object.freeze([...retained])]
  assert.equal(validateReviewedNameConnections(payload(), rows, index).length, 1)
  assert.deepEqual(rows, [original, retained])
})

test('new alias observations, multiplicity and unknown expenses invalidate old reviews', () => {
  const modified = [...retained]; modified[2] += 1
  for (const changed of [modified, [...retained.slice(0, 3), null, ...retained.slice(4)]]) {
    assert.throws(() => validateReviewedNameConnections(payload(), [original, changed], index), /observations changed/)
  }
  assert.throws(() => validateReviewedNameConnections(payload(), [original, retained, retained], index), /observations changed/)
})

test('new employers and historical periods can shift index offsets without invalidating unchanged source evidence', () => {
  const shifted = structuredClone(index)
  shifted.employers.unshift(['Another employer', 'Other', null, 'another'])
  shifted.years.unshift('2000/01')
  const rows = [original, retained].map((row) => { const next = [...row]; next[4] += 1; next[5] += 1; return next })
  assert.equal(validateReviewedNameConnections(payload(), rows, shifted).length, 1)
})

test('a changed source hash, source row or physical page cannot reuse an identity review', () => {
  const changedIndex = structuredClone(index)
  changedIndex.sources.official.sha256 = 'new-pdf'
  assert.throws(() => validateReviewedNameConnections(payload(), [original, retained], changedIndex), /witness changed/)
  const changedRow = [...original]; changedRow[7] = 181
  assert.throws(() => validateReviewedNameConnections(payload(), [changedRow, retained], index), /witness changed/)
})

test('a second official name with the same money blocks a previously unique witness', () => {
  const other = [...original]; other[0] = 'Murthy,Sriram'
  assert.throws(() => validateReviewedNameConnections(payload(), [original, retained, other], index), /no longer uniquely/)
})

test('the employer, preferred name and candidate pair cannot drift or acquire conflicting targets', () => {
  for (const field of ['employer', 'preferredName']) {
    const changed = payload(); changed.decisions[0][field] = 'different'
    assert.throws(() => validateReviewedNameConnections(changed, [original, retained], index))
  }
  const duplicate = payload(); duplicate.decisions.push(structuredClone(duplicate.decisions[0]))
  assert.throws(() => validateReviewedNameConnections(duplicate, [original, retained], index), /conflicting/)
})
