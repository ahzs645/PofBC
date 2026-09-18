// The path arithmetic that the mark consolidation depends on.
//
// If translatePath() were wrong, build-mark.mjs would either reject three copies of the same
// drawing or — worse — silently emit a mark whose sub-shapes had drifted apart.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { parsePath, pathBounds, serializePath, translatePath, translatePoints } from './svgPath.mjs'

test('repeated parameter groups imply the command again', () => {
  assert.deepEqual(
    parsePath('M10,20 30,40').map((group) => group.command),
    ['M', 'L'],
    'a repeated moveto is an implicit lineto'
  )
  assert.deepEqual(parsePath('c1,2 3,4 5,6 7,8 9,10 11,12').map((g) => g.command), ['c', 'c'])
})

test('relative commands are untouched by a translation', () => {
  const data = 'M100,200l10,10c1,2 3,4 5,6z'
  const moved = translatePath(data, -100, -200)

  assert.ok(moved.startsWith('M0 0'), moved)
  assert.ok(moved.includes('l10 10'), moved)
  assert.ok(moved.includes('c1 2 3 4 5 6'), moved)
})

test('only the endpoint of an absolute arc moves', () => {
  const moved = translatePath('M10,10A5,5 0 0 1 20,20', -10, -10)
  // rx, ry, rotation and the two flags are not coordinates.
  assert.ok(moved.includes('A5 5 0 0 1 10 10'), moved)
})

test('H and V shift on their own axis only', () => {
  assert.ok(translatePath('M10,10H50', -10, -5).includes('H40'))
  assert.ok(translatePath('M10,10V50', -5, -10).includes('V40'))
})

test('a round trip through parse and serialize preserves the geometry', () => {
  const data = 'M283.13,184.6l-.03,6.1c-2.79-1.41-5.47.43-7.82,1z'
  assert.deepEqual(parsePath(serializePath(parsePath(data))), parsePath(data))
})

test('polygon points translate as x y pairs', () => {
  assert.equal(translatePoints('10 20 30 40', -10, -20), '0 0 20 20')
})

test('bounding boxes are exact, not the control-point hull', () => {
  // A cubic that bulges well past its endpoints but whose controls overstate the reach: the true
  // maximum of this curve is 7.5, while the control points suggest 10.
  const box = pathBounds('M0,0 C0,10 10,10 10,0')
  assert.equal(box.minX, 0)
  assert.equal(box.maxX, 10)
  assert.equal(box.minY, 0)
  assert.ok(Math.abs(box.maxY - 7.5) < 1e-9, `expected 7.5, got ${box.maxY}`)
})

test('a straight line box is the line', () => {
  assert.deepEqual(pathBounds('M5,5L15,25'), { minX: 5, minY: 5, maxX: 15, maxY: 25 })
})

test('Z returns to the subpath start', () => {
  const box = pathBounds('M10,10L20,10L20,20Zl-5,-5')
  assert.equal(box.minX, 5, 'the relative line after Z starts from 10,10 again')
})

test('quadratic extremes are exact too', () => {
  // Peak of this quadratic is at t=0.5, y = 5 — the control point at 10 overstates it.
  const box = pathBounds('M0,0 Q5,10 10,0')
  assert.equal(box.minY, 0)
  assert.ok(Math.abs(box.maxY - 5) < 1e-9, `expected 5, got ${box.maxY}`)
  assert.equal(box.minX, 0)
  assert.equal(box.maxX, 10)
})

test('T mirrors the previous quadratic control point', () => {
  const mirrored = pathBounds('M0,0 Q5,10 10,0 T20,0')
  const explicit = pathBounds('M0,0 Q5,10 10,0 Q15,-10 20,0')
  assert.deepEqual(mirrored, explicit)
})

test('glyph outlines measure to the metrics the layout engine uses', async (t) => {
  // TrueType outlines are quadratic throughout, so this is the path that exercises Q in anger.
  // The table is generated from a licensed font and not committed, so a fresh clone skips this.
  const outlines = await import('../src/fonts/generated/outlines.js')
    .then((module) => module.default)
    .catch(() => null)
  if (!outlines) return t.skip('run `npm run build:fonts` first')

  const box = pathBounds(outlines.regular.glyphs[77]) // capital M
  const scale = 1000 / outlines.regular.unitsPerEm

  // Matches the side bearing and cap height in src/logo/fontMetrics.js.
  assert.ok(Math.abs(box.minX * scale - 73.73) < 0.5, `left side bearing: ${box.minX * scale}`)
  assert.ok(Math.abs(-box.minY * scale - 717.29) < 0.5, `cap height: ${-box.minY * scale}`)
})
