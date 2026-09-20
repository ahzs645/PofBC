import assert from 'node:assert/strict'
import { test } from 'node:test'
import { BCID } from '../current/currentMarks.js'
import { DEFAULT_MARK_ALIGNMENT, LAYOUTS, defaultMarkAlignment } from '../logo/layouts.js'
import { DEFAULTS } from './lockupDefaults.js'
import { applyShare, applyUpdate, swapColours } from './lockupReducer.js'

const run = (steps, from = DEFAULTS) => steps.reduce(applyUpdate, from)

// ── The province wordmark ─────────────────────────────────────────────────────────────────────────

test('switching lockup adopts what that artwork does with the wordmark', () => {
  // artwork/lockup-centred.svg is set without it; the other two carry it.
  assert.equal(run([{ layout: 'centred' }]).wordmark, false)
  assert.equal(run([{ layout: 'centred' }, { layout: 'horizontal' }]).wordmark, true)
  assert.equal(run([{ layout: 'centred' }, { layout: 'stacked' }]).wordmark, true)
})

test('setting the wordmark by hand pins it against later lockup changes', () => {
  const pinned = run([{ layout: 'centred' }, { wordmark: true }])

  assert.equal(pinned.wordmark, true)
  assert.equal(pinned.wordmarkTouched, true)

  // Every lockup now keeps it, including the one whose artwork omits it.
  for (const layout of ['stacked', 'horizontal', 'centred']) {
    assert.equal(applyUpdate(pinned, { layout }).wordmark, true, layout)
  }
})

test('turning the wordmark off by hand pins it just as firmly', () => {
  const pinned = run([{ wordmark: false }])
  assert.equal(applyUpdate(pinned, { layout: 'horizontal' }).wordmark, false)
})

test('the pin survives being set to the value it already had', () => {
  // Ticking a box that is already on is still a deliberate act.
  const pinned = run([{ wordmark: true }])
  assert.equal(pinned.wordmarkTouched, true)
  assert.equal(applyUpdate(pinned, { layout: 'centred' }).wordmark, true)
})

test('every layout declares what its artwork does', () => {
  for (const layout of Object.values(LAYOUTS)) {
    assert.equal(typeof layout.wordmarkByDefault, 'boolean', layout.id)
  }
  assert.equal(LAYOUTS.centred.wordmarkByDefault, false, 'the centred source artwork omits it')
})

test('a restored link counts as a deliberate choice', () => {
  // Otherwise opening a shared centred lockup and then clicking another layout would lose what the
  // sender set, because the state had never been "touched" in this session.
  const restored = applyShare(DEFAULTS, { layout: 'centred', wordmark: true })

  assert.equal(restored.wordmarkTouched, true)
  assert.equal(applyUpdate(restored, { layout: 'stacked' }).wordmark, true)
})

// ── Colour linking ────────────────────────────────────────────────────────────────────────────────

test('while linked, the type follows the mark', () => {
  const next = applyUpdate(DEFAULTS, { markColor: '#9f1d21' })
  assert.equal(next.textColor, '#9f1d21')
})

test('unlinking lets the two diverge, and relinking resolves to the mark', () => {
  const split = run([{ linkColors: false }, { markColor: '#006837' }, { textColor: '#e3a82b' }])
  assert.equal(split.markColor, '#006837')
  assert.equal(split.textColor, '#e3a82b')

  // Re-linking pulls the type back to the mark rather than to whichever was edited last.
  assert.equal(applyUpdate(split, { linkColors: true }).textColor, '#006837')
})

// ── Swapping ──────────────────────────────────────────────────────────────────────────────────────

test('swapping exchanges the ink and the background', () => {
  const swapped = swapColours({ ...DEFAULTS, markColor: '#ffffff', background: '#006837' })

  assert.equal(swapped.markColor, '#006837')
  assert.equal(swapped.textColor, '#006837', 'linked, so the type comes too')
  assert.equal(swapped.background, '#ffffff')
})

test('swapping out of a transparent background substitutes the brand green', () => {
  // There is no colour to bring forward, and a transparent mark would be nothing at all.
  const swapped = swapColours({ ...DEFAULTS, markColor: '#ffffff', background: 'none' })

  assert.equal(swapped.markColor, '#006837')
  assert.equal(swapped.background, '#ffffff')
})

test('swapping leaves an unlinked type colour alone', () => {
  const swapped = swapColours({
    ...DEFAULTS, linkColors: false, markColor: '#ffffff', textColor: '#e3a82b', background: '#006837'
  })

  assert.equal(swapped.markColor, '#006837')
  assert.equal(swapped.textColor, '#e3a82b', 'it was set independently, so it stays')
})

// ── Mark alignment ────────────────────────────────────────────────────────────────────────────────

test('each lockup opens with the alignment its own artwork uses', () => {
  // Side by side was reconstructed from signage that hangs the mark from the first cap height.
  assert.equal(run([{ layout: 'columns' }]).markAlign, 'top')
  // The horizontal lockup has a vector original, and it centres the mark.
  assert.equal(run([{ layout: 'horizontal' }]).markAlign, 'centre')
  assert.equal(LAYOUTS.columns.markAlignByDefault, 'top')
  assert.equal(LAYOUTS.horizontal.markAlignByDefault, 'centre')
})

test('moving between lockups keeps following their artwork', () => {
  const state = run([{ layout: 'columns' }, { layout: 'horizontal' }, { layout: 'columns' }])
  assert.equal(state.markAlign, 'top')
  assert.equal(state.markAlignTouched, false)
})

test('setting the alignment by hand pins it across lockups', () => {
  const pinned = run([{ layout: 'columns' }, { markAlign: 'bottom' }])

  assert.equal(pinned.markAlignTouched, true)
  for (const layout of ['horizontal', 'columns', 'stacked']) {
    assert.equal(applyUpdate(pinned, { layout }).markAlign, 'bottom', layout)
  }
})

test('choosing the value a lockup already had still pins it', () => {
  // Clicking "Top" on Side by side is a decision even though it was already top.
  const pinned = run([{ layout: 'columns' }, { markAlign: 'top' }])
  assert.equal(applyUpdate(pinned, { layout: 'horizontal' }).markAlign, 'top')
})

test('a restored link pins the alignment too', () => {
  const restored = applyShare(DEFAULTS, { layout: 'columns', markAlign: 'centre' })

  assert.equal(restored.markAlignTouched, true)
  // Otherwise clicking another lockup would throw away what the sender chose.
  assert.equal(applyUpdate(restored, { layout: 'horizontal' }).markAlign, 'centre')
})

test('the library default stays centre, whatever the UI prefers', () => {
  // resolveLockup() with no alignment named must still reproduce the measured artwork, so the
  // per-lockup preferences live in the UI layer rather than changing the renderer's own default.
  assert.equal(DEFAULT_MARK_ALIGNMENT, 'centre')
  assert.equal(defaultMarkAlignment('columns'), 'top')
  assert.equal(defaultMarkAlignment('stacked'), 'centre', 'lockups that ignore it fall back')
})

// ── Colour across the eras ────────────────────────────────────────────────────────────────────────

test('each era keeps its own background', () => {
  // The crest era's forest green is not a BC identity colour. Carrying it into the current era put
  // blue type on green, which is how this came to light.
  const state = run([{ background: '#006837' }, { era: 'current' }])

  assert.equal(state.background, '#006837', 'the historical one is untouched')
  assert.equal(state.currentBackground, DEFAULTS.currentBackground, 'and the current one is its own')
  assert.equal(state.currentBackground, BCID.white)
})

test('setting one era’s background leaves the other alone', () => {
  const state = run([{ era: 'current' }, { currentBackground: BCID.blue }, { era: 'historical' }])

  assert.equal(state.background, DEFAULTS.background)
  assert.equal(state.currentBackground, BCID.blue, 'still there when you go back')
})

test('the colourway follows the background the guidance pairs it with', () => {
  assert.equal(run([{ currentBackground: BCID.blue }]).currentVariant, 'reverse')
  assert.equal(run([{ currentBackground: BCID.gold }]).currentVariant, 'black')
  assert.equal(run([{ currentBackground: BCID.blueTint }]).currentVariant, 'black')
  assert.equal(run([{ currentBackground: 'none' }]).currentVariant, 'colour')
})

test('a background the guidance says nothing about leaves the colourway alone', () => {
  const state = run([{ currentVariant: 'reverse' }, { currentBackground: '#123456' }])
  assert.equal(state.currentVariant, 'reverse')
})

test('choosing a colourway by hand stops it following', () => {
  const pinned = run([{ currentVariant: 'white' }])

  assert.equal(pinned.currentVariantTouched, true)
  assert.equal(applyUpdate(pinned, { currentBackground: BCID.gold }).currentVariant, 'white')
})

test('the ministry is one choice, and a typed name reaches the current era too', () => {
  // It used to be two: a name for the drawn eras and a code for the current one. Switching
  // identity therefore changed the name on the lockup, and a typed name was lost on the way.
  let state = applyUpdate(DEFAULTS, { source: 'manual' })
  state = applyUpdate(state, { manualMinistry: 'Ministry of Widgets' })

  assert.equal(state.currentName, 'Ministry of Widgets', 'the current era shows what was typed')
  assert.equal(applyUpdate(state, { era: 'current' }).currentName, 'Ministry of Widgets')
})

test('picking from the list loads the published wording, in either language', () => {
  const picked = applyUpdate(DEFAULTS, { ministry: 'Ministry of Health' })
  assert.equal(picked.currentMinistry, 'HLTH', 'the code follows the name')
  assert.equal(picked.currentName, 'Ministry of Health')

  const french = applyUpdate(picked, { language: 'fr' })
  assert.equal(french.currentName, 'Ministère de la Santé')
})

test('a name no published mark answers to is simply typeset', () => {
  // The two lists are maintained separately and will drift. A name only the generator's list has
  // must still work — it just has no official wording to load.
  const picked = applyUpdate(DEFAULTS, { ministry: 'Ministry of Jobs, Economic Development and Innovation' })
  assert.equal(picked.currentName, 'Ministry of Jobs, Economic Development and Innovation')
})

test('editing the wording by hand makes it the name every era sets', () => {
  const edited = applyUpdate(DEFAULTS, { currentName: 'Ministry of Widgets' })

  assert.equal(edited.currentNameTouched, true)
  assert.equal(edited.source, 'manual')
  assert.equal(edited.manualMinistry, 'Ministry of Widgets')
  // And the list stops overwriting it, as it did before.
  assert.equal(applyUpdate(edited, { ministry: 'Ministry of Health' }).currentName, 'Ministry of Widgets')
})

test('restoring the official wording puts the link back', () => {
  const edited = applyUpdate(DEFAULTS, { currentName: 'Ministry of Widgets' })
  const restored = applyUpdate(edited, { currentName: 'Ministry of Forests', currentNameTouched: false })

  assert.equal(restored.currentNameTouched, false)
  assert.equal(applyUpdate(restored, { ministry: 'Ministry of Health' }).currentName, 'Ministry of Health')
})

test('the current era’s own list moves the shared choice too', () => {
  const picked = applyUpdate(DEFAULTS, { currentMinistry: 'ENV' })

  assert.equal(picked.source, 'list')
  assert.equal(picked.ministry, 'Ministry of Environment and Parks', 'the drawn eras follow it')
  assert.equal(picked.currentName, 'Ministry of Environment and Parks')
})

test('a restored share puts its wording on every identity', () => {
  // A current-era link carries a code and, when it differs, the wording. Restoring it used to
  // leave the other three showing whatever the defaults had.
  const restored = applyShare(DEFAULTS, { era: 'current', currentName: 'Ministry of Widgets' })

  assert.equal(restored.source, 'manual')
  assert.equal(restored.manualMinistry, 'Ministry of Widgets')
  assert.equal(restored.currentNameTouched, true)
})
