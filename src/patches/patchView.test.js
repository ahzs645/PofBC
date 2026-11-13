import { test } from 'node:test'
import assert from 'node:assert/strict'
import { FIT, MAX_ZOOM, VIEW_DEFAULTS, VIEW_KEY, clampPan, exportSize, loadView, modeFor, normalizeView, saveView, zoomTo } from './patchView.js'

const memory = (initial = {}) => {
  const data = new Map(Object.entries(initial))
  return { getItem: (key) => data.get(key) ?? null, setItem: (key, value) => data.set(key, value), data }
}

test('settings survive a round trip and bad values fall back to the defaults', () => {
  const storage = memory()
  saveView(storage, { ...VIEW_DEFAULTS, finish: 'glossy', lightDeg: 45, widthMm: '127' })
  assert.deepEqual(loadView(storage), { ...VIEW_DEFAULTS, finish: 'glossy', lightDeg: 45, widthMm: '127' })
  assert.deepEqual(normalizeView({ finish: 'chrome', widthMm: 12, lightDeg: 'north', mode: 'x-ray' }), { ...VIEW_DEFAULTS })
  assert.equal(normalizeView({ lightDeg: -90 }).lightDeg, 270)
  assert.equal(normalizeView({ lightDeg: 360 }).lightDeg, 0)
})

test('missing, broken or throwing storage gives the defaults', () => {
  assert.deepEqual(loadView(undefined), { ...VIEW_DEFAULTS })
  assert.deepEqual(loadView(memory({ [VIEW_KEY]: '{not json' })), { ...VIEW_DEFAULTS })
  const blocked = { getItem: () => { throw new Error('blocked') }, setItem: () => { throw new Error('blocked') } }
  assert.deepEqual(loadView(blocked), { ...VIEW_DEFAULTS })
  assert.doesNotThrow(() => saveView(blocked, VIEW_DEFAULTS))
})

test('a design without a source shows the simulation instead of a source view', () => {
  assert.equal(modeFor('source', false), 'embroidery')
  assert.equal(modeFor('compare', false), 'embroidery')
  assert.equal(modeFor('vector', false), 'vector')
  assert.equal(modeFor('compare', true), 'compare')
})

test('zooming keeps the point under the pointer where it is', () => {
  const view = zoomTo(FIT, 2, 100, -50, 400, 300)
  // Content point c is drawn at x + k * c: the point that was at (100, -50) at k = 1 is still there.
  assert.equal(view.x + view.k * 100, 100)
  assert.equal(view.y + view.k * -50, -50)
  const again = zoomTo(view, 4, 100, -50, 400, 300)
  assert.equal(again.x + again.k * 100, 100)
})

test('zoom stays within its limits and fitting recentres', () => {
  assert.equal(zoomTo(FIT, 99, 0, 0, 400, 300).k, MAX_ZOOM)
  assert.deepEqual(zoomTo({ k: 3, x: 120, y: -80 }, 0.2, 10, 10, 400, 300), { ...FIT })
})

test('panning cannot push the content off the stage', () => {
  assert.deepEqual(clampPan({ k: 2, x: 9999, y: -9999 }, 400, 300), { k: 2, x: 200, y: -150 })
  assert.deepEqual(clampPan({ k: 1, x: 50, y: 50 }, 400, 300), { k: 1, x: 0, y: 0 })
})

test('the export size is capped at 6000 px on the long side', () => {
  assert.deepEqual(exportSize({ widthMm: 97, heightMm: 120 }), { width: 2328, height: 2880 })
  assert.deepEqual(exportSize({ widthMm: 500, heightMm: 250 }), { width: 6000, height: 3000 })
})
