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

const parsedAlias = ['Murtby,Srinivasa', null, 351290, 11382, 0, 0, 'official', 180]
const laterCorrectName = ['Murthy,Srinivasa', null, 360000, null, 0, 1, 'later', 20]
const renderedIndex = { ...index, years: ['2023/24', '2024/25'], sources: { ...index.sources,
  later: { url: 'https://example.test/later.pdf', sourceKind: 'official-pdf', sha256: 'later-hash' } } }
const renderedPayload = () => ({ schemaVersion: 1, decisions: [{ employer: 'phsa', names: [parsedAlias[0], laterCorrectName[0]],
  preferredName: laterCorrectName[0], decision: 'verified', evidence: [{ sourceId: 'official', pdfPage: 180 }, { sourceId: 'later', pdfPage: 20 }],
  proof: { kind: 'rendered-source-spelling', aliasNameKey: 'murtby|srinivasa', aliasRowsSha256: nameRowsFingerprint([parsedAlias, retained], renderedIndex),
    witnesses: [parsedAlias, laterCorrectName].map((row) => ({ rowSha256: nameRecordFingerprint(row, renderedIndex), sourceId: row[6],
      pdfSha256: renderedIndex.sources[row[6]].sha256, pdfPage: row[7], printedNameKey: 'murthy|srinivasa' })) } }] })

test('a parsed official typo needs every original row reviewed; a compiled alias still needs a unique complete financial witness', () => {
  const rows = [parsedAlias, laterCorrectName, retained].map((row) => Object.freeze([...row]))
  assert.equal(validateReviewedNameConnections(renderedPayload(), rows, renderedIndex).length, 1)
  assert.deepEqual(rows, [parsedAlias, laterCorrectName, retained])
  const missing = renderedPayload(); missing.decisions[0].proof.witnesses.shift()
  assert.throws(() => validateReviewedNameConnections(missing, rows, renderedIndex), /Every official alias row/)
  const unchecked = [...parsedAlias]; unchecked[7] = 181
  const added = renderedPayload(); added.decisions[0].proof.aliasRowsSha256 = nameRowsFingerprint([parsedAlias, retained, unchecked], renderedIndex)
  assert.throws(() => validateReviewedNameConnections(added, [...rows, unchecked], renderedIndex), /Every official alias row/)
  const different = [...parsedAlias]; different[0] = 'Murthy,Sriram'
  assert.throws(() => validateReviewedNameConnections(renderedPayload(), [...rows, different], renderedIndex), /no longer uniquely/)
})

test('a source spelling review cannot stand in for missing target rows, source pages, or a different printed name', () => {
  const rows = [parsedAlias, laterCorrectName, retained]
  const noTarget = renderedPayload(); noTarget.decisions[0].proof.witnesses.pop()
  assert.throws(() => validateReviewedNameConnections(noTarget, rows, renderedIndex), /existing target/)
  const differentPrint = renderedPayload(); differentPrint.decisions[0].proof.witnesses[0].printedNameKey = 'murtby|srinivasa'
  assert.throws(() => validateReviewedNameConnections(differentPrint, rows, renderedIndex), /witness changed/)
  const changedSource = structuredClone(renderedIndex); changedSource.sources.official.sha256 = 'new-pdf'
  assert.throws(() => validateReviewedNameConnections(renderedPayload(), rows, changedSource), /witness changed/)
})
