// The flag lockup.
//
// The numbers pinned here come from the only reference there is — a screenshot of the logo — so
// they are worth defending: a change that moves them is a change that stops matching it. The
// reference measures 333 × 164 at a 100px cap height, and the lockup is built to land there.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { FLAG, FLAG_PALETTE } from '../assets/flagMark.js'
import { FLAG_ASPECT, FLAG_METRICS, LETTERS, flagLockupMarkup, layoutFlagLockup } from './flagLayout.js'
import { flagSize, renderFlagSvg } from './renderFlagSvg.js'

test('the flag artwork is the Province’s, on its own ink box', () => {
  assert.equal(FLAG.shapes.length, 12)
  assert.deepEqual(FLAG_PALETTE, ['#013366', '#ad0000', '#fcba19'], 'navy, red and gold')
  // Moved onto its own origin, so the drawing starts at 0,0 and is exactly as big as it draws.
  assert.ok(Math.abs(FLAG_ASPECT - 1.301) < 0.002, `aspect is ${FLAG_ASPECT}`)
  for (const shape of FLAG.shapes) assert.ok(shape.d.startsWith('M'), 'absolute paths only')
})

test('the lockup reproduces the reference’s proportions', () => {
  // 333 × 164 in the screenshot, at a 100px BC cap. Both dimensions, not just the one the flag
  // size was set from, which is the check that the arrangement is right and not merely scaled.
  const { box } = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })

  assert.ok(Math.abs(box.width - 333) < 4, `width ${box.width.toFixed(1)}`)
  assert.ok(Math.abs(box.height - 164) < 4, `height ${box.height.toFixed(1)}`)
})

test('the flag hangs from the baseline and overshoots the cap line', () => {
  const layout = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })

  // Its foot lines up with the letters' feet, which sit on y = 0.
  assert.ok(Math.abs(layout.flag.y + layout.flag.height - FLAG_METRICS.flagDrop * 100) < 0.01)
  // And its head is above them: the letters' cap top is -cap.
  assert.ok(layout.flag.y < -100, `flag top ${layout.flag.y.toFixed(1)} should clear the cap line`)
  assert.ok(layout.flag.x > layout.letters.ink.inkRight, 'the flag clears the letters')
})

test('the wording sits under the letters, aligned to the B’s ink', () => {
  const layout = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })
  const [line] = layout.lines

  assert.equal(layout.lines.length, 1)
  // Its own ink starts where the letters' does, whatever side bearing the first letter has.
  assert.ok(Math.abs((line.x + line.ink.inkLeft) - layout.letters.ink.inkLeft) < 0.01)
  assert.ok(line.y > 0, 'below the baseline')
})

test('a long name wraps to the lockup’s own width', () => {
  const short = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })
  const long = layoutFlagLockup({ ministry: 'Ministry of Water, Land and Resource Stewardship', cap: 100 })

  assert.ok(long.lines.length > 1)
  assert.ok(long.box.height > short.box.height, 'more lines make it taller')
  // The wording never pushes the lockup wider than the letters and flag above it.
  assert.ok(long.box.width <= short.box.width + 0.01, `${long.box.width} vs ${short.box.width}`)
})

test('the lockup scales as one drawing', () => {
  const small = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 10 })
  const big = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 1000 })

  assert.ok(Math.abs(big.box.width / small.box.width - 100) < 1e-6)
  assert.ok(Math.abs(big.box.height / small.box.height - 100) < 1e-6)
})

test('one ink paints the flag with the letters, colour leaves it alone', () => {
  const layout = layoutFlagLockup({ ministry: 'Ministry of Forests', cap: 100 })
  const options = { layout, letterColor: '#123456', textColor: '#123456' }

  const colour = flagLockupMarkup(options)
  const ink = flagLockupMarkup({ ...options, flagInk: '#123456' })

  for (const shade of FLAG_PALETTE) assert.ok(colour.includes(shade), `colour keeps ${shade}`)
  for (const shade of FLAG_PALETTE) assert.ok(!ink.includes(shade), `one ink drops ${shade}`)
  assert.equal((ink.match(/data-role="flag"/g) || []).length, FLAG.shapes.length)
})

test('an empty name still draws the letters and the flag', () => {
  const { lines, box } = layoutFlagLockup({ ministry: '', cap: 100 })
  assert.deepEqual(lines, [])
  assert.ok(box.width > 0 && box.height > 0)
})

test('the rendered SVG frames the lockup, and clear space grows the frame', () => {
  const plain = renderFlagSvg({ ministry: 'Ministry of Forests' })
  const padded = renderFlagSvg({ ministry: 'Ministry of Forests', clearSpaceFactor: 0.25 })

  assert.ok(plain.svg.startsWith('<svg'))
  assert.equal(flagSize('Ministry of Forests').width, plain.box.width)
  assert.ok(Math.abs(padded.box.width - plain.box.width * 1.5) < 0.01)
  assert.equal((padded.svg.match(/<svg/g) || []).length, 1)
})

test('a background paints the whole frame, and transparent paints nothing', () => {
  const filled = renderFlagSvg({ ministry: 'x', background: '#006837', clearSpaceFactor: 0.2 })
  assert.ok(filled.svg.includes('fill="#006837"'))
  assert.ok(!renderFlagSvg({ ministry: 'x', background: 'none' }).svg.includes('<rect'))
})

test('colours cannot break out of the attributes they are written into', () => {
  // Backgrounds and colours arrive from share links, which arrive from anyone.
  const svg = renderFlagSvg({
    ministry: 'Ministry of <script>',
    letterColor: '"/><script>alert(1)</script>',
    background: '"/><script>'
  }).svg

  assert.ok(!svg.includes('<script>'), svg.slice(0, 300))
  assert.ok(svg.includes('&lt;script&gt;'))
})

test('the letters are the two the identity is built on', () => {
  assert.equal(LETTERS, 'BC')
})
