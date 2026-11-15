import assert from 'node:assert/strict'
import { test } from 'node:test'
import { renderDocumentArmsSvg } from '../documentArms/renderDocumentArmsSvg.js'
import { DEFAULTS } from './lockupDefaults.js'
import { getPreviewAppearance } from './useLockupState.js'

const historic = {
  ...DEFAULTS, era: 'document', documentLayout: 'emblem',
  documentMarkColor: '#000000', documentTextColor: '#ffffff',
  documentBackground: 'none', linkColors: false
}

test('arms alone chooses its preview surface and contrast from the visible arms', () => {
  const { svg } = renderDocumentArmsSvg({
    layout: historic.documentLayout,
    markColor: historic.documentMarkColor,
    textColor: historic.documentTextColor,
    background: historic.documentBackground
  })
  assert.doesNotMatch(svg, /data-part="heading"/, 'this layout really has no lettering')
  const appearance = getPreviewAppearance(historic)
  assert.equal(appearance.backdrop, 'light', 'hidden white text must not put black arms on dark')
  assert.equal(appearance.background, 'none')
  assert.equal(appearance.isTransparent, true)
  assert.deepEqual(appearance.contrast.map(({ ratio, part, differs }) => ({ ratio, part, differs })), [
    { ratio: 21, part: 'mark', differs: false },
    { ratio: 1, part: 'mark', differs: false }
  ])
})

test('switching from arms alone to a heading restores the saved lettering in preview decisions', () => {
  for (const documentLayout of ['split-serif', 'government', 'split-blackletter']) {
    const appearance = getPreviewAppearance({ ...historic, documentLayout })
    assert.equal(appearance.backdrop, 'dark', documentLayout)
    assert.equal(appearance.contrast[0].part, 'text', documentLayout)
    assert.equal(appearance.contrast[0].ratio, 1, documentLayout)
    assert.equal(appearance.contrast[0].differs, true, documentLayout)
  }
  assert.equal(historic.documentTextColor, '#ffffff', 'the stored heading colour is untouched')
})

test('white arms choose dark automatically while a manual surface leaves exports transparent', () => {
  const state = { ...historic, documentMarkColor: '#ffffff', documentTextColor: '#000000' }
  assert.equal(getPreviewAppearance(state).backdrop, 'dark')
  assert.deepEqual(getPreviewAppearance(state).contrast.map(({ ratio }) => ratio), [1, 21])
  for (const backdrop of ['light', 'dark']) {
    const appearance = getPreviewAppearance({ ...state, backdrop })
    assert.equal(appearance.backdrop, backdrop)
    assert.equal(appearance.background, 'none')
    assert.equal(appearance.isTransparent, true)
  }
})
