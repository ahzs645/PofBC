// The tools an agent sees. Tested through buildTools() rather than the hook, so no browser and no
// navigator.modelContext are needed — the hook itself is three lines of registration around this.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CLEAR_SPACE_ORDER, LAYOUT_ORDER, MARK_ALIGNMENT_ORDER } from '../logo/layouts.js'
import { EXPORT_FORMAT_ORDER, SIZE_PRESETS } from '../export/exportLogo.js'
import { TRANSPARENT } from '../logo/logoColors.js'
import { DEFAULTS } from './lockupDefaults.js'
import { buildTools } from './useAgentTools.js'

/** A stand-in for the live component, capturing the patches the tools would apply. */
const harness = (overrides = {}) => {
  const patches = []
  const state = { ...DEFAULTS, ...overrides }
  const lockup = {
    layout: state.layout,
    wordmark: state.wordmark,
    ministry: state.source === 'manual' ? state.manualMinistry : state.ministry,
    program: state.program,
    markColor: state.markColor,
    textColor: state.textColor,
    background: state.background,
    padding: 0,
    markAlign: state.markAlign
  }

  const latest = { current: { state, lockup, update: (patch) => patches.push(patch) } }
  const tools = buildTools(latest)

  return {
    patches,
    tools,
    call: (name, input = {}) => tools.find((tool) => tool.name === name).execute(input, {})
  }
}

const schemaOf = (tools, name) => tools.find((tool) => tool.name === name).inputSchema

test('every tool is describable and has an object schema', () => {
  const { tools } = harness()

  assert.deepEqual(tools.map((tool) => tool.name), [
    'get_lockup_state', 'set_lockup', 'set_colours', 'export_lockup', 'get_share_link',
    'list_current_marks', 'find_ministry'
  ])

  for (const tool of tools) {
    assert.equal(typeof tool.execute, 'function', tool.name)
    assert.equal(tool.inputSchema.type, 'object', tool.name)
    // An agent chooses a tool from its description alone, so a terse one is a bug.
    assert.ok(tool.description.length > 60, `${tool.name} needs a fuller description`)
  }
})

test('schemas enumerate from the application’s own constants', () => {
  // The point of deriving them: a tool cannot offer a lockup, format or size that does not exist,
  // and adding one updates the schema for free.
  const { tools } = harness()

  assert.deepEqual(schemaOf(tools, 'set_lockup').properties.lockup.enum, LAYOUT_ORDER)
  assert.deepEqual(schemaOf(tools, 'set_lockup').properties.markAlignment.enum, MARK_ALIGNMENT_ORDER)
  assert.deepEqual(schemaOf(tools, 'set_lockup').properties.clearSpace.enum, CLEAR_SPACE_ORDER)
  assert.deepEqual(schemaOf(tools, 'export_lockup').properties.format.enum, EXPORT_FORMAT_ORDER)
  assert.deepEqual(schemaOf(tools, 'export_lockup').properties.pixelWidth.enum, SIZE_PRESETS)
  assert.deepEqual(schemaOf(tools, 'export_lockup').required, ['format'])
})

test('get_lockup_state reports the geometry that would actually export', () => {
  const { call } = harness({ layout: 'columns', markAlign: 'top' })
  const { content, structuredContent } = call('get_lockup_state')

  assert.equal(content[0].type, 'text')
  assert.ok(content[0].text.includes('Side by side'))
  assert.equal(structuredContent.lockup, 'columns')
  assert.equal(structuredContent.markAlignment, 'top')
  assert.ok(structuredContent.size.width > 0 && structuredContent.size.height > 0)
  assert.ok(structuredContent.contrast.ratio > 1)
})

test('alignment is reported as null where the lockup ignores it', () => {
  // Saying "centre" for a stacked lockup would invite an agent to set something with no effect.
  const { call } = harness({ layout: 'stacked' })
  assert.equal(call('get_lockup_state').structuredContent.markAlignment, null)
})

test('the era can be switched, and its own fields set', () => {
  const { call, patches } = harness()

  call('set_lockup', { era: 'current', ministryCode: 'env', language: 'fr', variant: 'reverse' })

  assert.deepEqual(patches[0], {
    era: 'current',
    // Upper-cased, so an agent need not know which way the codes are written.
    currentMinistry: 'ENV',
    language: 'fr',
    currentVariant: 'reverse'
  })
})

test('the current era reports itself rather than pretending to be a drawing', () => {
  const { call } = harness({ era: 'current', currentMinistry: 'FOR', currentVariant: 'reverse' })
  const { structuredContent, content } = call('get_lockup_state')

  assert.equal(structuredContent.era, 'current')
  assert.equal(structuredContent.ministryCode, 'FOR')
  // None of the historical era's drawing fields, which do not apply and would only mislead.
  assert.ok(!('size' in structuredContent))
  assert.ok(!('markColor' in structuredContent))
  assert.match(content[0].text, /FOR mark \(en\)/)
  // The wording is reported, because it is now something an agent can change.
  assert.match(content[0].text, /Ministry of \/ Forests/)
})

test('set_lockup applies only what it was given', () => {
  const { call, patches } = harness()
  call('set_lockup', { lockup: 'horizontal' })

  assert.deepEqual(patches, [{ layout: 'horizontal' }], 'nothing else is touched')
})

test('naming a ministry switches the form out of its list mode', () => {
  // Otherwise the dropdown would still be showing a different ministry than the one drawn.
  const { call, patches } = harness()
  call('set_lockup', { ministry: 'Office of the Chief Information Officer' })

  assert.deepEqual(patches[0], {
    source: 'manual',
    manualMinistry: 'Office of the Chief Information Officer'
  })
})

test('set_colours unlinks the type when it is given its own colour', () => {
  const { call, patches } = harness()

  call('set_colours', { markColor: '#006837' })
  assert.deepEqual(patches[0], { markColor: '#006837' }, 'the mark alone leaves the link intact')

  call('set_colours', { textColor: '#e3a82b' })
  assert.deepEqual(patches[1], { textColor: '#e3a82b', linkColors: false })
})

test('"transparent" is translated to the value the renderer uses', () => {
  const { call, patches } = harness()

  call('set_colours', { background: 'transparent' })
  call('set_colours', { background: 'TRANSPARENT' })

  assert.equal(patches[0].background, TRANSPARENT)
  assert.equal(patches[1].background, TRANSPARENT, 'case does not matter')
})

test('set_colours reports the contrast that results, not the one before', () => {
  const { call } = harness({ markColor: '#ffffff', background: '#006837' })
  const { structuredContent } = call('set_colours', { background: '#ffffff' })

  // White on white: the reply has to reflect the change it just made.
  assert.equal(structuredContent.contrast.level, 'fail')
})

test('find_ministry matches on words, ignoring punctuation', () => {
  const { call } = harness()

  assert.deepEqual(
    call('find_ministry', { query: 'citizens services' }).structuredContent.matches,
    ['Ministry of Citizens’ Services']
  )
  assert.ok(call('find_ministry', {}).structuredContent.matches.length > 20, 'no query lists everything')
})

test('a ministry that does not exist says so, and says what to do instead', () => {
  const { call } = harness()
  const { content, structuredContent } = call('find_ministry', { query: 'ministry of magic' })

  assert.deepEqual(structuredContent.matches, [])
  assert.ok(content[0].text.includes('can be typed'), content[0].text)
})

test('export_lockup refuses a format it cannot encode rather than substituting one', async () => {
  const { call } = harness()
  const result = await call('export_lockup', { format: 'tiff' })

  assert.ok(result.content[0].text.includes('No such format'), result.content[0].text)
})
