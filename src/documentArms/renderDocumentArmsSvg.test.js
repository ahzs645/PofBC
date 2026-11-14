import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { DOMParser } from '@xmldom/xmldom'
import { DOCUMENT_ARMS_PATH, DOCUMENT_ARMS_SOURCE } from './geometry.generated.js'
import {
  documentArmsSize, layoutDocumentArms, renderDocumentArmsSvg
} from './renderDocumentArmsSvg.js'
import { DOCUMENT_ARMS_LAYOUT_ORDER, DOCUMENT_ARMS_PROVENANCE } from './layouts.js'

const parse = (svg) => new DOMParser().parseFromString(svg, 'image/svg+xml')
const findPart = (document, part) => [...document.getElementsByTagName('*')]
  .find((element) => element.getAttribute('data-part') === part)

test('the shared arms retain the held path exactly and declare the generated-master provenance', () => {
  const fragment = readFileSync(new URL('../../artwork/stationery/grace-mccarthy/evidence/supplied-arms-fragment.txt', import.meta.url))
  const sourcePath = /<path d="([^"]+)"/.exec(fragment.toString('utf8'))?.[1]
  assert.equal(DOCUMENT_ARMS_PATH, sourcePath)
  assert.equal(createHash('sha256').update(fragment).digest('hex'), DOCUMENT_ARMS_SOURCE.arms.sourceSha256)
  assert.equal(createHash('sha256').update(sourcePath).digest('hex'), DOCUMENT_ARMS_SOURCE.arms.pathSha256)
  assert.equal(DOCUMENT_ARMS_SOURCE.status, 'provisional-study')
  assert.match(DOCUMENT_ARMS_PROVENANCE, /vector conversion of a generated master/)
  assert.match(DOCUMENT_ARMS_PROVENANCE, /not a verified historical or official drawing/)
  assert.match(DOCUMENT_ARMS_PROVENANCE, /original typefaces have not been identified/)
})

test('each exported layout is self-contained path artwork with its evidence caveat', () => {
  for (const layout of DOCUMENT_ARMS_LAYOUT_ORDER) {
    const { svg, box } = renderDocumentArmsSvg({ layout, pixelWidth: 2048 })
    const document = parse(svg)
    assert.equal(document.documentElement.getAttribute('data-layout'), layout)
    assert.equal(document.getElementsByTagName('parsererror').length, 0)
    for (const tag of ['text', 'image', 'use', 'script', 'foreignObject', 'style']) {
      assert.equal(document.getElementsByTagName(tag).length, 0, `${layout} unexpectedly contains <${tag}>`)
    }
    assert.ok(document.getElementsByTagName('path').length > 0)
    const metadata = JSON.parse(document.getElementsByTagName('metadata')[0].textContent)
    assert.equal(metadata.layout, layout)
    assert.equal(metadata.status, 'provisional-study')
    assert.equal(metadata.provenance, DOCUMENT_ARMS_PROVENANCE)
    assert.equal(findPart(document, 'arms').getElementsByTagName('path')[0].getAttribute('d'), DOCUMENT_ARMS_PATH)
    assert.equal(findPart(document, 'arms').getElementsByTagName('path')[0].getAttribute('fill-rule'), 'evenodd')
    assert.ok(Object.values(box).every(Number.isFinite))
    assert.ok(box.width > 0 && box.height > 0)
    assert.equal(Number(document.documentElement.getAttribute('width')), 2048)
    assert.equal(Number(document.documentElement.getAttribute('height')), Math.round(2048 * box.height / box.width))
  }
})

test('lettering never overlaps the arms or runs beyond the unpadded artwork', () => {
  for (const layout of DOCUMENT_ARMS_LAYOUT_ORDER) {
    const drawing = layoutDocumentArms({ layout })
    assert.deepEqual(documentArmsSize({ layout }), { width: drawing.width, height: drawing.height })
    assert.ok(Math.abs(drawing.mark.width / drawing.mark.height - 1146 / 1283) < 1e-12)
    for (const heading of drawing.lettering) {
      assert.ok(heading.x >= 0 && heading.y >= 0)
      assert.ok(heading.x + heading.width <= drawing.width + 0.002, `${layout}: right edge`)
      assert.ok(heading.y + heading.height <= drawing.height + 0.002, `${layout}: lower edge`)
      const separated = heading.x + heading.width < drawing.mark.x ||
        heading.x > drawing.mark.x + drawing.mark.width ||
        heading.y > drawing.mark.y + drawing.mark.height
      assert.ok(separated, `${layout}: heading must not cover the arms`)
    }
    if (layout.startsWith('split-')) {
      const [left, right] = drawing.lettering
      assert.ok(Math.abs((left.y + left.baseline) - (right.y + right.baseline)) < 0.001)
    }
  }
})

test('the four layouts retain their distinct wording, separate from arbitrary ministry names', () => {
  const texts = (layout) => layoutDocumentArms({ layout }).lettering.map(({ text }) => text)
  assert.deepEqual(texts('emblem'), [])
  assert.deepEqual(texts('split-serif'), ['BRITISH', 'COLUMBIA'])
  assert.deepEqual(texts('government'), ['THE GOVERNMENT OF', 'THE PROVINCE OF BRITISH COLUMBIA'])
  assert.deepEqual(texts('split-blackletter'), ['British', 'Columbia'])
  assert.equal(layoutDocumentArms({ layout: 'unknown' }).id, 'split-serif')
})

test('recolouring preserves the geometry and transparent exports have no painted background', () => {
  const black = parse(renderDocumentArmsSvg({ markColor: 'black', textColor: '#123456', background: 'white' }).svg)
  const reversed = parse(renderDocumentArmsSvg({ markColor: 'white', textColor: 'white', background: 'transparent' }).svg)
  assert.equal(findPart(black, 'arms').getAttribute('fill'), '#000000')
  assert.equal(findPart(black, 'heading').getAttribute('fill'), '#123456')
  assert.equal(findPart(black, 'background').getAttribute('fill'), '#ffffff')
  assert.equal(findPart(reversed, 'arms').getAttribute('fill'), '#ffffff')
  assert.equal(findPart(reversed, 'heading').getAttribute('fill'), '#ffffff')
  assert.equal(findPart(reversed, 'background'), undefined)
  const paths = (document) => [...document.getElementsByTagName('path')].map((p) => p.getAttribute('d'))
  assert.deepEqual(paths(black), paths(reversed))
})

test('clear space encloses the complete heading and is measured from the drawing width', () => {
  for (const layout of DOCUMENT_ARMS_LAYOUT_ORDER) {
    const original = renderDocumentArmsSvg({ layout })
    const padded = renderDocumentArmsSvg({ layout, clearSpaceFactor: 0.25 })
    assert.ok(Math.abs(padded.box.width - original.box.width * 1.5) < 0.002)
    assert.ok(Math.abs(padded.box.height - (original.box.height + original.box.width * 0.5)) < 0.002)
    assert.ok(Math.abs(padded.box.x + original.box.width * 0.25) < 0.002)
    assert.deepEqual(padded.layout, original.layout)
  }
})

test('malformed and extreme public options cannot create non-finite geometry or injected markup', () => {
  for (const value of [-100, 0, NaN, Infinity, -Infinity, 1e100, '2048']) {
    const result = renderDocumentArmsSvg({ pixelWidth: value, clearSpaceFactor: value })
    const root = parse(result.svg).documentElement
    const width = Number(root.getAttribute('width'))
    const height = Number(root.getAttribute('height'))
    assert.ok(Number.isInteger(width) && width >= 1 && width <= 16384)
    assert.ok(Number.isInteger(height) && height >= 1)
    assert.ok(Object.values(result.box).every(Number.isFinite))
    assert.doesNotMatch(result.svg, /(?:NaN|Infinity)/)
  }
  const attack = '\"><script>alert(1)</script><image href="https://example.test/a"/>'
  const document = parse(renderDocumentArmsSvg({
    layout: attack, title: attack, markColor: attack,
    textColor: 'url(https://example.test/a)', background: 'var(--external)'
  }).svg)
  assert.equal(document.getElementsByTagName('script').length, 0)
  assert.equal(document.getElementsByTagName('image').length, 0)
  assert.equal(document.getElementsByTagName('title')[0].textContent, attack)
  assert.equal(findPart(document, 'arms').getAttribute('fill'), '#000000')
  assert.equal(findPart(document, 'heading').getAttribute('fill'), '#000000')
  assert.equal(findPart(document, 'background'), undefined)
})
