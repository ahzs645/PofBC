import assert from 'node:assert/strict'
import { test } from 'node:test'
import { unzipSync, strFromU8 } from 'fflate'
import { DOCUMENT_ARMS_LAYOUT_ORDER } from '../documentArms/layouts.js'
import { renderDocumentArmsSvg } from '../documentArms/renderDocumentArmsSvg.js'
import { buildFileName, buildSvgSource, renderLogoBlob } from '../export/exportLogo.js'
import { planBundle, renderBundle } from '../export/exportBundle.js'
import { clearSpaceFactor } from '../logo/layouts.js'
import { DEFAULTS } from './lockupDefaults.js'
import { applyShare, applyUpdate, swapColours } from './lockupReducer.js'
import { buildConfigUrl, fromConfig, readConfigParam, toConfig } from './configFormat.js'
import { buildShareUrl, decodeShare, encodeShare, sanitizeShare } from './shareLink.js'
import { buildTools } from './useAgentTools.js'

const stateFor = (layout) => ({
  ...DEFAULTS, era: 'document', documentLayout: layout,
  documentMarkColor: '#123456', documentTextColor: '#654321',
  documentBackground: 'none', linkColors: false, clearSpace: 'generous'
})
const exportOptions = (state) => ({
  era: state.era, documentLayout: state.documentLayout,
  documentMarkColor: state.documentMarkColor,
  documentTextColor: state.linkColors ? state.documentMarkColor : state.documentTextColor,
  documentBackground: state.documentBackground,
  clearSpaceFactor: clearSpaceFactor(state.clearSpace)
})

test('every document layout survives readable and actual compressed sharing', async () => {
  for (const layout of DOCUMENT_ARMS_LAYOUT_ORDER) {
    const state = stateFor(layout)
    const readable = readConfigParam(new URL(buildConfigUrl(state, 'https://example.test/PofBC/')).search)
    const compressed = await decodeShare(await encodeShare(state))
    for (const patch of [readable, compressed]) {
      const restored = applyShare(DEFAULTS, patch)
      assert.deepEqual(toConfig(restored), toConfig(state), layout)
      assert.equal(restored.era, 'document')
    }
  }
})

test('sharing preserves linked colours for the next edit, not only the initial drawing', async () => {
  const state = { ...DEFAULTS, era: 'document', documentMarkColor: '#123456' }
  for (const patch of [fromConfig(toConfig(state)), await decodeShare(await encodeShare(state))]) {
    const restored = applyShare(DEFAULTS, patch)
    assert.equal(restored.linkColors, true)
    const edited = applyUpdate(restored, { documentMarkColor: '#abcdef' })
    assert.equal(edited.documentTextColor, '#abcdef')
    assert.equal(edited.markColor, DEFAULTS.markColor, 'other identities retain their colours')
  }
})

test('each kind of share link removes the competing stale configuration', async () => {
  const state = stateFor('government')
  const readable = new URL(buildConfigUrl(state, 'https://example.test/PofBC/?s=old&utm=keep#top'))
  assert.equal(readable.searchParams.has('s'), false)
  assert.equal(readable.searchParams.get('utm'), 'keep')
  const compressed = new URL(await buildShareUrl(state, 'https://example.test/PofBC/?c=old&utm=keep#top'))
  assert.equal(compressed.searchParams.has('c'), false)
  assert.equal(compressed.hash, '#top')
  assert.equal((await decodeShare(compressed.searchParams.get('s'))).documentLayout, 'government')
})

test('document configurations validate their own fields and reject injected attributes', () => {
  const patch = fromConfig({ era: 'document', documentLayout: '../../bad', markColor: '\"/><script/>', background: 'TRANSPARENT', linkColors: 'yes' })
  assert.equal(patch.documentLayout, DEFAULTS.documentLayout)
  assert.equal(patch.documentMarkColor, DEFAULTS.documentMarkColor)
  assert.equal(patch.documentBackground, 'none')
  assert.equal(patch.linkColors, DEFAULTS.linkColors)
  assert.ok(!Object.hasOwn(patch, 'markColor'))
  assert.equal(sanitizeShare({ config: null }), null)
})

test('document swap changes the active palette and preserves independent text', () => {
  const state = stateFor('emblem')
  const swapped = swapColours(state)
  assert.equal(swapped.documentMarkColor, '#ffffff')
  assert.equal(swapped.documentTextColor, state.documentTextColor)
  assert.equal(swapped.documentBackground, state.documentMarkColor)
  assert.equal(swapped.background, DEFAULTS.background)
  assert.equal(swapColours({ ...state, linkColors: true }).documentTextColor, '#ffffff')
})

test('agent tools report and update the document identity in the same public vocabulary', () => {
  const state = stateFor('government')
  const patches = []
  const tools = buildTools({ current: { state, lockup: exportOptions(state), update: (patch) => patches.push(patch) } })
  const tool = (name) => tools.find((entry) => entry.name === name)
  assert.deepEqual(tool('set_lockup').inputSchema.properties.documentLayout.enum, DOCUMENT_ARMS_LAYOUT_ORDER)
  const result = tool('get_lockup_state').execute({})
  assert.equal(result.structuredContent.accuracy, 'reconstruction-study')
  assert.equal(result.structuredContent.documentLayout, 'government')
  assert.match(result.content[0].text, /reconstruction study/)
  assert.doesNotMatch(result.content[0].text, /wordmark only/)
  tool('set_colours').execute({ markColor: '#abcdef', background: 'transparent' })
  assert.deepEqual(patches[0], { documentMarkColor: '#abcdef', documentBackground: 'none' })
})

test('export uses the preview renderer byte for byte without requesting fonts or references', async () => {
  const originalFetch = globalThis.fetch
  globalThis.fetch = () => { throw new Error('Document export must not fetch a font or reference') }
  try {
    for (const layout of DOCUMENT_ARMS_LAYOUT_ORDER) {
      const state = stateFor(layout)
      const options = { ...exportOptions(state), pixelWidth: 1024 }
      const expected = renderDocumentArmsSvg({
        layout, markColor: state.documentMarkColor, textColor: state.documentTextColor,
        background: state.documentBackground, clearSpaceFactor: options.clearSpaceFactor, pixelWidth: 1024
      }).svg
      assert.equal(await buildSvgSource(options), expected, layout)
      assert.equal(await (await renderLogoBlob({ ...options, format: 'svg' })).text(), expected, layout)
      assert.doesNotMatch(expected, /<text\b|<image\b|<style\b|@font-face/)
      assert.match(expected, /generated master/)
      assert.match(buildFileName({ ...options, ministry: 'Unrelated ministry', format: 'svg' }), new RegExp(`^bc-historic-arms-${layout}-study\\.svg$`))
    }
  } finally { globalThis.fetch = originalFetch }
})

test('document bundle contains only the chosen layout, distinct filenames and honest notes', async () => {
  const options = { ...exportOptions(stateFor('split-blackletter')), formats: ['svg'] }
  const plan = planBundle({ ...options, formats: ['svg', 'pdf', 'png'], sizes: [512, 1024] })
  assert.equal(plan.length, 4)
  assert.equal(new Set(plan.map(({ path }) => path)).size, 4)
  assert.ok(plan.every(({ layout }) => layout === null))
  const blob = await renderBundle(options)
  const files = unzipSync(new Uint8Array(await blob.arrayBuffer()))
  const names = Object.keys(files)
  assert.equal(names.filter((name) => name.endsWith('.svg')).length, 1)
  const readme = strFromU8(files[names.find((name) => name.endsWith('README.txt'))])
  assert.match(readme, /not a verified historical or official drawing/)
  assert.doesNotMatch(readme, /official ministry mark|live text, font embedded/)
})
