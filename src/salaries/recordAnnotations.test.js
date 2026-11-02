import test from 'node:test'
import assert from 'node:assert/strict'
import { RECORD_ANNOTATIONS, decodedAnnotation, decodedCurrency, employerAnnotation, governmentAnnotation, personAnnotation, personCurrency, validateRecordAnnotations } from './recordAnnotations.js'
import { formatMoney } from './money.js'
import { withoutCompiledRepeats } from './people.js'

const annotation = RECORD_ANNOTATIONS.annotations[0]
const r = annotation.record
const index = { employers: [['BCI', 'Crown corporations', 'bc-investment-management-corporation', r.employer]], years: [r.period], sources: { [r.sourceId]: { sourceKind: 'compiled' } } }
const person = [r.name, r.position, r.pay, r.expenses, 0, 0, r.sourceId, r.pdfPage]
const employer = [r.name, r.position, r.pay, r.expenses, 0, r.sourceId, r.pdfPage]
const government = [r.name, r.position, r.pay, r.expenses, r.sourceId, r.pdfPage]
const decoded = { ...r, slug: r.employer, year: r.period, page: r.pdfPage }

test('the reviewed USD observation is found consistently in every export schema', () => {
  assert.equal(personAnnotation(person, index), annotation)
  assert.equal(employerAnnotation(employer, r.employer, index.years), annotation)
  assert.equal(governmentAnnotation(government, r.employer, r.period), annotation)
  assert.equal(decodedAnnotation(decoded), annotation)
  assert.equal(personCurrency(person, index), 'USD')
  assert.equal(decodedCurrency(decoded, index.sources), 'USD')
  assert.equal(formatMoney(r.pay, '—', 'USD'), 'US$3,902,330')
  assert.equal(formatMoney(0, '—', 'unverified'), '0 (currency unverified)')
})

test('currency review fails closed when the observation changes, disappears or is duplicated', () => {
  assert.equal(validateRecordAnnotations([decoded], index.sources), RECORD_ANNOTATIONS)
  for (const key of ['name', 'position', 'pay', 'expenses', 'slug', 'year', 'sourceId', 'page']) {
    const changed = { ...decoded, [key]: typeof decoded[key] === 'number' ? decoded[key] + 1 : `${decoded[key]}-changed` }
    assert.throws(() => validateRecordAnnotations([changed], index.sources), /observation changed/)
  }
  assert.throws(() => validateRecordAnnotations([], index.sources), /observation changed/)
  assert.throws(() => validateRecordAnnotations([decoded, decoded], index.sources), /observation changed/)
  assert.equal(personCurrency(['Pittman, J.', 'SVP', 1512762, 19531, 0, 0, r.sourceId, null], index), 'CAD', 'the USD correction never applies to the entire source or employer')
})

test('same numeric CAD and USD payments are never folded as compiled repeats', () => {
  const rows = [[...person], [...person]]
  rows[1][6] = 'official'
  const sources = { ...index.sources, official: { sourceKind: 'official-pdf', url: 'https://example.test/report.pdf', sha256: 'primary-pdf' } }
  assert.equal(withoutCompiledRepeats(rows, sources).length, 1, 'control: otherwise identical same-currency rows can be folded')
  assert.equal(withoutCompiledRepeats(rows, sources, (row) => personCurrency(row, index)).length, 2)
})
