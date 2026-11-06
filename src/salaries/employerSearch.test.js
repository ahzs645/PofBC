import test from 'node:test'
import assert from 'node:assert/strict'
import { employerMatcher } from './employerSearch.js'

test('employers match any word order, partial words, punctuation and case', () => {
  const northern = { slug: 'northern-health', names: ['Northern Health'] }
  for (const query of ['Northern Health', 'health northern', '  HEALTH   north  ', 'northern-health']) {
    assert.equal(employerMatcher(query)(northern), true, query)
  }
  assert.equal(employerMatcher('northern hydro')(northern), false)
  assert.equal(employerMatcher('')(northern), false)
  const hydro = { slug: 'bc-hydro', names: ['B.C. Hydro', 'BC Hydro and Power Authority'] }
  for (const query of ['BC Hydro', 'B.C. Hydro', 'hydro bc', 'power authority']) assert.equal(employerMatcher(query)(hydro), true, query)
})

test('verified university acronyms find only their associated employer without changing disclosed names', () => {
  const unbc = Object.freeze({ slug: 'university-of-northern-bc', names: Object.freeze(['University of Northern B.C.', 'University of Northern British Columbia']) })
  const uvic = Object.freeze({ slug: 'university-of-victoria', names: Object.freeze(['University of Victoria']) })
  assert.equal(employerMatcher('UNBC')(unbc), true)
  assert.equal(employerMatcher('uvic')(uvic), true)
  assert.equal(employerMatcher('uvic university')(uvic), true)
  assert.equal(employerMatcher('uvic')(unbc), false)
  assert.equal(employerMatcher('unbc')(uvic), false)
  assert.deepEqual(uvic.names, ['University of Victoria'])
  assert.equal(employerMatcher('unbc')({ slug: 'other-university', names: ['University of Northern B.C.'] }), false, 'an acronym does not create an identity match for another slug')
})
