import assert from 'node:assert/strict'
import { test } from 'node:test'
import { LAYOUTS } from '../logo/layouts.js'
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
