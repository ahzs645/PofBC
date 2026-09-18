// Geometry checks for the three lockups, against the artwork they were derived from.
//
// The expectations here are positions measured directly out of artwork/*.svg, converted into the
// renderer's origin-relative space. Where this code deliberately departs from the source — the
// centred lockup in the originals is eyeballed rather than actually centred — the size of that
// departure is asserted too, so it stays a known, bounded decision rather than drifting.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { MARK_BOX, renderLockupSvg, resolveLockup } from './renderLogoSvg.js'
import { LAYOUTS } from './layouts.js'
import { measureLine } from './logoText.js'

const FORESTS = { ministry: 'Ministry of Forests' }

const closeTo = (actual, expected, tolerance, message) => {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `${message}: expected ${expected} ± ${tolerance}, got ${actual}`
  )
}

test('the mark is the size the build extracted from the artwork', () => {
  assert.deepEqual(MARK_BOX, { width: 497.02, height: 497.19 })
})

test('stacked: the first baseline sits where the artwork puts it', () => {
  const { lines, mark } = resolveLockup({ layout: 'stacked', ...FORESTS })

  assert.deepEqual(lines.map((line) => line.text), ['Province of', 'British Columbia', 'Ministry of', 'Forests'])
  assert.deepEqual(lines.map((line) => line.style.weight), ['bold', 'bold', 'regular', 'regular'])

  // In artwork/lockup-stacked.svg the mark's top is at y=184.60 and the first baseline at 865.96.
  closeTo(lines[0].y, 865.96 - 184.60, 0.02, 'first baseline below the mark top')
  // One uniform leading runs through both blocks: 146.64 units, which is 1.2 em at 122.2.
  lines.forEach((line, index) => closeTo(line.y, lines[0].y + index * 146.64, 0.02, `baseline ${index}`))

  assert.equal(mark.x, 0, 'the mark defines the left edge')
  assert.equal(mark.y, 0, 'and the top')
})

test('stacked: the mark aligns to the leftmost ink of the text block', () => {
  const { lines, mark, viewBox } = resolveLockup({ layout: 'stacked', ...FORESTS })

  assert.ok(lines.every((line) => line.x === lines[0].x), 'left-aligned lines share an origin')

  // Every line's ink starts at or right of zero, and the widest one defines the box.
  const inked = lines.map((line) => ({ ...measureLine(line.text, line.style), x: line.x }))
  closeTo(Math.min(...inked.map((line) => line.x + line.inkLeft)), mark.x, 0.001, 'block ink left = mark left')
  closeTo(Math.max(...inked.map((line) => line.x + line.inkRight)), viewBox.width, 0.001, 'widest ink = box width')
})

test('stacked: that alignment is under a unit from where the artwork puts it', () => {
  // artwork/lockup-stacked.svg draws the mark's left edge at x=283.13 and anchors its bold text at
  // 273.39 and its regular text at 273.4837 — aligning the mark to the "P" of Province rather than
  // to the leftmost ink in the block, which is the "M" of Ministry. This code uses the block, which
  // is text-independent where matching one capital's side bearing is not. The gap that opens up is
  // the whole of the difference, and it is well under a unit on a 497-unit mark.
  const bold = { fontSize: 122.2, weight: 'bold', wordSpacing: 0.027 }
  const regular = { fontSize: 122.2, weight: 'regular', wordSpacing: 0.027 }

  const artworkBlockInk = Math.min(
    273.39 + measureLine('Province of', bold).inkLeft,
    273.39 + measureLine('British Columbia', bold).inkLeft,
    273.4837 + measureLine('Ministry of', regular).inkLeft,
    273.4837 + measureLine('Forests', regular).inkLeft
  )

  const deviation = 283.13 - artworkBlockInk
  assert.ok(deviation > 0 && deviation < 1, `expected a sub-unit deviation, got ${deviation}`)
})

test('centred: the mark and every line share a centre', () => {
  const resolved = resolveLockup({ layout: 'centred', wordmark: false, ...FORESTS, program: 'Research Program' })
  const { lines, mark, viewBox } = resolved

  assert.deepEqual(lines.map((line) => line.text), ['Ministry of Forests', 'Research Program'])

  const centre = viewBox.width / 2
  closeTo(mark.x + MARK_BOX.width / 2, centre, 0.01, 'mark centre')

  // Lines are centred on their ink, not their advance — which is what "centred" means to the eye.
  // The source artwork is hand-placed and misses this by 19 and 28 units respectively, and its own
  // two lines disagree with each other by 9, so there is no single offset that could be copied.
  // This is the one place the reconstruction knowingly improves on the original.
  for (const line of lines) {
    const ink = measureLine(line.text, line.style)
    closeTo(line.x + (ink.inkLeft + ink.inkRight) / 2, centre, 0.01, `"${line.text}" centred on its ink`)
  }

  closeTo(lines[0].y, 1062.1859 - 402.98, 0.02, 'first baseline below the mark top')
  closeTo(lines[1].y - lines[0].y, 125.53, 0.01, 'the centred lockup uses a tighter leading')
})

test('horizontal: the text sits beside the mark, vertically centred on it', () => {
  const { lines, mark, viewBox } = resolveLockup({ layout: 'horizontal', ...FORESTS })

  assert.deepEqual(lines.map((line) => line.text), ['Province of British Columbia', 'Ministry of Forests'])

  // artwork/lockup-horizontal.svg: mark right edge at 783.48, text origin at 860.5824.
  closeTo(lines[0].x, 497.02 + LAYOUTS.horizontal.gap - 8.969, 0.01, 'text origin beside the mark')
  closeTo(lines[1].y - lines[0].y, 145.968, 0.01, '1.2 em leading')

  // The mark is centred on the text's cap band — the cap height of the first line down to the last
  // baseline. The artwork sits it 7.83 units higher, which is hand placement, not a different rule.
  closeTo(mark.y, -227.21 + 7.83, 0.05, 'mark top relative to the first baseline')
  closeTo(viewBox.width, 2249.87, 0.05, 'overall width')
  closeTo(viewBox.height, MARK_BOX.height, 0.01, 'the mark is the tallest thing in this lockup')
})

test('the viewBox hugs the ink in every layout', () => {
  for (const id of ['stacked', 'centred', 'horizontal']) {
    const { viewBox, mark } = resolveLockup({ layout: id, ...FORESTS })
    assert.ok(viewBox.width >= MARK_BOX.width, `${id}: at least as wide as the mark`)
    assert.ok(viewBox.height >= MARK_BOX.height - 0.01, `${id}: at least as tall as the mark`)
    assert.ok(mark.x >= viewBox.x - 0.01, `${id}: mark is inside the box horizontally`)
    assert.ok(mark.y >= viewBox.y - 0.01, `${id}: mark is inside the box vertically`)
  }
})

test('padding grows the box symmetrically without moving the contents', () => {
  const tight = resolveLockup({ layout: 'stacked', ...FORESTS })
  const padded = resolveLockup({ layout: 'stacked', ...FORESTS, padding: 60 })

  assert.deepEqual(padded.mark, tight.mark, 'the lockup itself does not move')
  closeTo(padded.viewBox.x, tight.viewBox.x - 60, 0.001, 'x')
  closeTo(padded.viewBox.width, tight.viewBox.width + 120, 0.001, 'width')
  closeTo(padded.viewBox.height, tight.viewBox.height + 120, 0.001, 'height')
})

test('dropping the wordmark leaves only the ministry', () => {
  const { lines } = resolveLockup({ layout: 'stacked', wordmark: false, ...FORESTS })
  assert.deepEqual(lines.map((line) => line.text), ['Ministry of', 'Forests'])
  assert.ok(lines.every((line) => line.style.weight === 'regular'))
})

test('with no text at all the lockup is just the mark', () => {
  const { lines, viewBox } = resolveLockup({ layout: 'stacked', wordmark: false, ministry: '' })
  assert.equal(lines.length, 0)
  assert.deepEqual(
    { width: viewBox.width, height: viewBox.height },
    { width: MARK_BOX.width, height: MARK_BOX.height }
  )
})

test('a long ministry wraps to the layout measure rather than running away', () => {
  const long = 'Ministry of Post-Secondary Education and Future Skills'

  for (const id of ['stacked', 'centred', 'horizontal']) {
    const { lines, viewBox } = resolveLockup({ layout: id, ministry: long })
    assert.ok(lines.length > 2, `${id}: wrapped onto several lines`)
    const measure = LAYOUTS[id].measure({ hasWordmark: true })
    assert.ok(viewBox.width <= measure + MARK_BOX.width + LAYOUTS[id].gap + 1, `${id}: stays within the measure`)
  }
})

test('markup escapes text that would otherwise break the document', () => {
  const svg = renderLockupSvg({ layout: 'stacked', ministry: 'Parks & Rec <script>', wordmark: false })

  assert.ok(svg.includes('Parks &amp; Rec &lt;script&gt;'), 'escaped in the text node')
  assert.ok(!svg.includes('<script>'), 'no raw tag survives')
  // Valid enough to parse: every tag opened is closed.
  assert.equal((svg.match(/<svg/g) || []).length, 1)
  assert.ok(svg.trimEnd().endsWith('</svg>'))
})

test('a transparent background paints no rectangle', () => {
  const clear = renderLockupSvg({ layout: 'stacked', ...FORESTS, background: 'none' })
  const green = renderLockupSvg({ layout: 'stacked', ...FORESTS, background: 'green' })

  assert.ok(!clear.includes('<rect'), 'nothing is painted behind a transparent lockup')
  assert.ok(green.includes('<rect') && green.includes('#006837'))
})

test('a pixel width sets both dimensions, preserving the aspect ratio', () => {
  const { viewBox } = resolveLockup({ layout: 'horizontal', ...FORESTS })
  const svg = renderLockupSvg({ layout: 'horizontal', ...FORESTS, pixelWidth: 1000 })

  const expectedHeight = Math.round(1000 * viewBox.height / viewBox.width)
  assert.ok(svg.includes(`width="1000" height="${expectedHeight}"`), svg.slice(0, 200))
})

test('the accessible name describes what is actually drawn', () => {
  assert.equal(
    resolveLockup({ layout: 'stacked', ...FORESTS }).description,
    'Province of British Columbia — Ministry of Forests'
  )
  assert.equal(
    resolveLockup({ layout: 'centred', wordmark: false, ...FORESTS, program: 'Research Program' }).description,
    'Ministry of Forests — Research Program'
  )
})

test('the mark and the type take their colours independently', () => {
  const resolved = resolveLockup({ layout: 'stacked', ...FORESTS, markColor: 'green', textColor: 'gold' })

  assert.equal(resolved.markColor, '#006837')
  assert.equal(resolved.textColor, '#e3a82b')

  const svg = renderLockupSvg({ layout: 'stacked', ...FORESTS, markColor: 'green', textColor: 'gold' })
  // The mark's fill wraps its group; each line of type carries its own.
  assert.ok(svg.includes('<g fill="#006837">'), 'mark group')
  assert.ok(svg.includes('fill="#e3a82b"'), 'text fill')
  assert.equal((svg.match(/fill="#e3a82b"/g) || []).length, 4, 'one per line')
})

test('`color` is a shorthand that either half can override', () => {
  const both = resolveLockup({ layout: 'stacked', ...FORESTS, color: 'blue' })
  assert.equal(both.markColor, '#234075')
  assert.equal(both.textColor, '#234075')

  const overridden = resolveLockup({ layout: 'stacked', ...FORESTS, color: 'blue', textColor: 'white' })
  assert.equal(overridden.markColor, '#234075', 'the mark keeps the shorthand')
  assert.equal(overridden.textColor, '#ffffff', 'the type takes the override')
})

test('the background covers the clear space, not just the ink', () => {
  const padding = 120
  const { viewBox } = resolveLockup({ layout: 'stacked', ...FORESTS, background: 'green', padding })
  const svg = renderLockupSvg({ layout: 'stacked', ...FORESTS, background: 'green', padding })

  // A background painted only behind the ink would leave the margin transparent, which is exactly
  // what makes a padded export look like a cropping mistake.
  assert.ok(
    svg.includes(`<rect x="${viewBox.x}" y="${viewBox.y}" width="${viewBox.width}" height="${viewBox.height}" fill="#006837"/>`),
    svg.slice(0, 400)
  )
})

test('a colour cannot break out of the attribute it is written into', () => {
  // Colours are free text in the UI and arrive from strangers over a share link, so a value
  // carrying a quote must not be able to close its attribute and open a tag of its own.
  const hostile = '"/><script>alert(1)</script><g fill="red'

  for (const key of ['markColor', 'textColor', 'background']) {
    const svg = renderLockupSvg({ layout: 'stacked', ...FORESTS, [key]: hostile })
    assert.ok(!svg.includes('<script'), `${key}: injected a tag`)
    assert.ok(svg.includes('&quot;'), `${key}: the quote should be escaped, not dropped`)
  }
})
