// The JSON a person or an agent hands over. Tested hard because it is the one input that arrives
// from outside the app entirely, and the one an agent will write without ever seeing the UI.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { TRANSPARENT } from '../logo/logoColors.js'
import { CONFIG_PARAM, buildConfigUrl, fromConfig, parseConfig, readConfigParam, toConfig } from './configFormat.js'
import { DEFAULTS } from './lockupDefaults.js'

test('a configuration round-trips through the state it describes', () => {
  const patch = fromConfig(toConfig(DEFAULTS))
  const restored = toConfig({ ...DEFAULTS, ...patch })

  assert.deepEqual(restored, toConfig(DEFAULTS))
})

test('it speaks the vocabulary the manifest and the tools use', () => {
  // Not the internal names. An agent reads capabilities.json and writes what it saw there.
  const config = toConfig(DEFAULTS)

  assert.ok('lockup' in config && !('layout' in config))
  assert.ok('markAlignment' in config && !('markAlign' in config))
  assert.ok('showWordmark' in config && !('wordmark' in config))
})

test('absent fields are left alone rather than reset', () => {
  // "Just make it red" must not silently return everything else to its default.
  const patch = fromConfig({ markColor: '#9f1d21' })

  assert.deepEqual(Object.keys(patch), ['markColor'])
})

test('a ministry switches the form to its manual mode', () => {
  const patch = fromConfig({ ministry: 'Ministry of\nEnvironment' })

  assert.equal(patch.source, 'manual')
  assert.equal(patch.manualMinistry, 'Ministry of\nEnvironment', 'the line break survives')
})

test('naming the type colour separately unlinks it from the mark', () => {
  assert.equal(fromConfig({ textColor: '#e3a82b' }).linkColors, false)
  assert.ok(!('linkColors' in fromConfig({ markColor: '#e3a82b' })), 'the mark alone does not')
})

test('"transparent" becomes the value the renderer uses', () => {
  assert.equal(fromConfig({ background: 'transparent' }).background, TRANSPARENT)
  assert.equal(fromConfig({ background: 'TRANSPARENT' }).background, TRANSPARENT)
  assert.equal(toConfig({ ...DEFAULTS, background: TRANSPARENT }).background, 'transparent')
})

test('unrecognised values fall back instead of passing through', () => {
  const patch = fromConfig({
    lockup: '../../etc/passwd',
    markAlignment: 'diagonal',
    clearSpace: 42,
    markColor: '"/><script>alert(1)</script>'
  })

  assert.equal(patch.layout, DEFAULTS.layout)
  assert.equal(patch.markAlign, DEFAULTS.markAlign)
  assert.equal(patch.clearSpace, DEFAULTS.clearSpace)
  assert.equal(patch.markColor, DEFAULTS.markColor, 'a colour cannot carry markup')
})

test('a payload that is not an object is refused', () => {
  for (const value of [null, undefined, 'text', 7, ['a']]) {
    assert.equal(fromConfig(value), null, JSON.stringify(value))
  }
})

test('parse failures say what is wrong', () => {
  assert.match(parseConfig('{nope').error, /not valid JSON/)
  assert.match(parseConfig('').error, /Nothing to apply/)
  assert.match(parseConfig('[]').error, /JSON object/)
  assert.match(parseConfig('{"unknown": 1}').error, /No recognised settings/)
  assert.ok(parseConfig('{"lockup":"columns"}').patch)
})

test('a configuration URL carries readable JSON and keeps the rest of the address', () => {
  const url = new URL(buildConfigUrl(DEFAULTS, 'https://example.org/PofBC/?utm=x#top'))

  assert.equal(url.pathname, '/PofBC/')
  assert.equal(url.searchParams.get('utm'), 'x')
  assert.equal(url.hash, '#top')
  // Readable, not compressed: whoever wrote it can check it by eye.
  assert.deepEqual(JSON.parse(url.searchParams.get(CONFIG_PARAM)), toConfig(DEFAULTS))
})

test('reading a configuration back out of a URL', () => {
  const search = new URL(buildConfigUrl(
    { ...DEFAULTS, layout: 'columns', markAlign: 'top' },
    'https://example.org/'
  )).search

  const patch = readConfigParam(search)
  assert.equal(patch.layout, 'columns')
  assert.equal(patch.markAlign, 'top')
  assert.equal(readConfigParam('?nothing=here'), null)
})

test('the scenario this was built for', () => {
  // An agent that read the manifest, decided what it wanted, and could not hand it over.
  const patch = fromConfig({
    lockup: 'columns',
    showWordmark: true,
    ministry: 'Ministry of\nEnvironment',
    markAlignment: 'top',
    markColor: '#eee3c0',
    textColor: '#eee3c0',
    background: 'transparent',
    clearSpace: 'none'
  })

  assert.equal(patch.layout, 'columns')
  assert.equal(patch.manualMinistry, 'Ministry of\nEnvironment')
  assert.equal(patch.markAlign, 'top')
  assert.equal(patch.markColor, '#eee3c0')
  assert.equal(patch.background, TRANSPARENT)
  assert.equal(patch.clearSpace, 'none')
})
