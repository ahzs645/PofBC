import { test } from 'node:test'
import assert from 'node:assert/strict'
import { initiativePlaceUrl, legacyInitiativeUrl, readInitiativePlace } from './initiativePlace.js'

test('initiative links round-trip and leave unrelated query and fragment state behind', () => {
  const url = initiativePlaceUrl('https://example.org/PofBC/?view=government&node=tourism-bc&year=2008&mark=old&colour=blue&identity-query=park#tourism-marks/old', {
    initiative: 'tourism', section: 'websites', record: 'hellobc'
  })
  assert.equal(url.origin, 'https://example.org')
  assert.equal(url.pathname, '/PofBC/')
  assert.equal(url.search, '?view=initiatives&initiative=tourism&section=websites&record=hellobc')
  assert.equal(url.hash, '')
  assert.deepEqual(readInitiativePlace(url.href), { initiative: 'tourism', section: 'websites', record: 'hellobc' })
})

test('returning to the index clears the initiative and all detail selections', () => {
  const url = initiativePlaceUrl('https://example.org/PofBC/?view=initiatives&initiative=tourism&section=marks&record=worldhost-mark#old')
  assert.equal(url.search, '?view=initiatives')
  assert.equal(url.hash, '')
  assert.deepEqual(readInitiativePlace(url.href), { initiative: null, section: null, record: null })
  assert.deepEqual(readInitiativePlace('https://example.org/?initiative=&section=&record='), { initiative: null, section: null, record: null })
})

test('the legacy tourism website record becomes a canonical initiative URL', () => {
  const url = legacyInitiativeUrl('https://example.org/PofBC/?view=gallery&logos=tourism-bc-destination-bc&colour=blue#tourism-websites/hellobc')
  assert.equal(url.href, 'https://example.org/PofBC/?view=initiatives&initiative=tourism&section=websites&record=hellobc')
  assert.equal(legacyInitiativeUrl(url.href), null, 'the canonical URL must not migrate again')
})

test('both former corporate collection aliases retain every tourism section link', () => {
  for (const collection of ['collected-tourism-bc', 'collected-destination-bc']) {
    for (const section of ['websites', 'marks', 'timeline', 'publications', 'sources']) {
      const url = legacyInitiativeUrl(`https://example.org/PofBC/?view=gallery&logos=${collection}#tourism-${section}`)
      assert.deepEqual(readInitiativePlace(url.href), { initiative: 'tourism', section, record: null })
    }
  }
})

test('corporate mark and plain collection URLs stay in the gallery', () => {
  for (const mark of ['source-tourism-bc-tourism-british-columbia-2005-svg', '']) {
    assert.equal(legacyInitiativeUrl(`https://example.org/?view=gallery&logos=tourism-bc-destination-bc&mark=${mark}#tourism-marks`), null)
  }
  assert.equal(legacyInitiativeUrl('https://example.org/?view=gallery&logos=tourism-bc-destination-bc'), null)
})

test('unrelated views, collections and unrecognized fragments are not migrated', () => {
  for (const href of [
    'https://example.org/?view=government&logos=tourism-bc-destination-bc#tourism-websites',
    'https://example.org/?view=gallery&logos=bc-hydro#tourism-websites',
    'https://example.org/?view=gallery&logos=tourism-bc-destination-bc#tourism-unknown',
    'https://example.org/?view=gallery&logos=tourism-bc-destination-bc#tourism-websites/hellobc/extra',
    'https://example.org/?view=gallery&logos=tourism-bc-destination-bc#railway-history',
    'https://example.org/?view=gallery&logos=tourism-bc-destination-bc#tourism-websites/%broken'
  ]) assert.equal(legacyInitiativeUrl(href), null, href)
})

test('record names use query encoding without carrying hash escapes into the ID', () => {
  const url = legacyInitiativeUrl('https://example.org/PofBC/?view=gallery&logos=collected-tourism-bc#tourism-marks/hello%20bc')
  assert.equal(readInitiativePlace(url.href).record, 'hello bc')
  assert.equal(url.searchParams.get('record'), 'hello bc')
})

test('a shared guide page survives a direct visit and is cleared when leaving the reader', () => {
  const base = 'https://example.org/PofBC/'
  const url = initiativePlaceUrl(base, { initiative: 'tourism', section: 'brand-guide', page: 64 })
  assert.equal(readInitiativePlace(url.href).page, '64')
  assert.equal(initiativePlaceUrl(url, { initiative: 'tourism', section: 'marks' }).searchParams.has('page'), false)
})
