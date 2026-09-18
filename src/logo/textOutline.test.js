// Outlined type has to be the same drawing as live type, or the export option is a trap.
//
// These checks are geometric rather than visual: the emitted path data is measured back and
// compared against the layout model, so they prove the placement itself rather than agreeing with
// whatever a particular rasteriser happened to do.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { pathBounds } from '../../scripts/svgPath.mjs'
import { measureLine } from './logoText.js'
import { renderLockupSvg, resolveLockup } from './renderLogoSvg.js'
import { canOutline, outlineLineMarkup, outlineTextMarkup } from './textOutline.js'

// The outline table is generated from a licensed font and is not committed, so a fresh clone that
// has not run `npm run build:fonts` skips these rather than failing.
const outlines = await import('../fonts/generated/outlines.js')
  .then((module) => module.default)
  .catch(() => null)

const missing = outlines ? false : 'run `npm run build:fonts` first'

const FORESTS = { ministry: 'Ministry of Forests' }

/** The bounds a line's emitted glyph paths actually cover, in artwork units. */
const drawnBounds = (line) => {
  const markup = outlineLineMarkup(line, outlines)
  const face = outlines[line.style.weight === 'bold' ? 'bold' : 'regular']
  const scale = line.style.fontSize / face.unitsPerEm

  let box = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity }
  for (const [, offset, data] of markup.matchAll(/<path(?: transform="translate\(([-\d.]+) 0\)")? d="([^"]+)"/g)) {
    const dx = offset ? Number(offset) : 0
    const bounds = pathBounds(data)
    box = {
      minX: Math.min(box.minX, bounds.minX + dx), maxX: Math.max(box.maxX, bounds.maxX + dx),
      minY: Math.min(box.minY, bounds.minY), maxY: Math.max(box.maxY, bounds.maxY)
    }
  }

  return {
    left: line.x + box.minX * scale,
    right: line.x + box.maxX * scale,
    top: line.y + box.minY * scale,
    bottom: line.y + box.maxY * scale
  }
}

test('the outline table carries both faces', { skip: missing }, () => {
  assert.ok(canOutline(outlines))
  assert.equal(canOutline(null), false)
  assert.equal(canOutline({ regular: outlines.regular }), false, 'one face is not enough')
})

test('outlined glyphs land exactly where the layout model says', { skip: missing }, () => {
  for (const layout of ['stacked', 'centred', 'horizontal']) {
    const { lines } = resolveLockup({
      layout,
      ...FORESTS,
      program: layout === 'centred' ? 'Research Program' : '',
      wordmark: layout !== 'centred'
    })

    for (const line of lines) {
      const drawn = drawnBounds(line)
      const ink = measureLine(line.text, line.style)

      // Sub-thousandth-of-a-unit agreement on all four edges: the outlines are not merely close,
      // they are the same geometry the live-text path is laid out with.
      const expect = (actual, wanted, edge) => assert.ok(
        Math.abs(actual - wanted) < 0.01,
        `${layout} "${line.text}" ${edge}: drawn ${actual}, model ${wanted}`
      )

      expect(drawn.left, line.x + ink.inkLeft, 'left')
      expect(drawn.right, line.x + ink.inkRight, 'right')
      expect(drawn.top, line.y - ink.inkTop, 'top')
      expect(drawn.bottom, line.y - ink.inkBottom, 'bottom')
    }
  }
})

test('an outlined lockup carries no text and needs no font', { skip: missing }, () => {
  const svg = renderLockupSvg({ layout: 'stacked', ...FORESTS, glyphs: outlines })

  assert.equal((svg.match(/<text/g) || []).length, 0, 'no text nodes')
  assert.ok(!svg.includes('font-family'), 'nothing refers to a font')
  assert.ok(!svg.includes('@font-face'), 'nothing embeds one')
  // The mark's own paths plus one per drawn glyph.
  assert.ok((svg.match(/<path/g) || []).length > 40, 'glyphs were drawn as paths')
})

test('the accessible name survives outlining', { skip: missing }, () => {
  const svg = renderLockupSvg({ layout: 'stacked', ...FORESTS, glyphs: outlines })
  // Turning letters into shapes removes the text from the document; the title is all that is left
  // for a screen reader, so it has to still be there.
  assert.ok(svg.includes('<title>Province of British Columbia — Ministry of Forests</title>'), svg.slice(0, 300))
})

test('blank glyphs are skipped, not drawn as empty paths', { skip: missing }, () => {
  const style = { fontSize: 100, weight: 'regular' }
  const spaced = outlineLineMarkup({ text: 'A B', style, x: 0, y: 0 }, outlines)
  assert.equal((spaced.match(/<path/g) || []).length, 2, 'two letters, no path for the space')
})

test('text with no drawable glyphs produces nothing at all', { skip: missing }, () => {
  const style = { fontSize: 100, weight: 'regular' }
  assert.equal(outlineLineMarkup({ text: '   ', style, x: 0, y: 0 }, outlines), '')
  assert.equal(outlineTextMarkup([], outlines, '#fff'), '')
})

test('a missing face degrades to nothing rather than throwing', { skip: missing }, () => {
  const style = { fontSize: 100, weight: 'bold' }
  assert.equal(outlineLineMarkup({ text: 'A', style, x: 0, y: 0 }, { regular: outlines.regular }), '')
  assert.equal(outlineLineMarkup({ text: 'A', style, x: 0, y: 0 }, null), '')
})
