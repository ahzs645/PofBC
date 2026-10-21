// The posters hang together: every series lists real posters, every part sits on its drawing and
// names layers the drawing has, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { POSTERS, SERIES, neighbours, posterIds, seriesOf } from './catalogue.js'
import { FOREST_SERVICE_POSTERS } from './forest-service/posters.js'
import { BC_FERRIES_POSTERS } from './bc-ferries/posters.js'
import { GALLERY_COLLECTIONS } from '../gallery/collections.js'
import { ORDER as COASTAL_ORDER, PARTS as COASTAL_PARTS, REGIONS as COASTAL_REGIONS } from './coastal-forest/parts.js'
import { FOREST_LOGOS } from '../internal/forestLogos.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const DRAWINGS = {
  'coastal-forest': read('./coastal-forest/poster.svg'),
  'dont-drop-it': read('./forest-service/dont-drop-it.svg'),
  'dont-gamble-with-fire': read('./forest-service/dont-gamble-with-fire.svg'),
  'reward-living-forest': read('./forest-service/reward-living-forest.svg'),
  'enjoy-protect-forests': read('./forest-service/enjoy-protect-forests.svg'),
  'go-bc-ferries': read('./bc-ferries/go-bc-ferries.svg'),
  'queen-of-sidney': read('./bc-ferries/queen-of-sidney.svg')
}
const GOVERNMENT = read('../government/historyData.js')

// Every poster as the viewer sees it: its parts, the order they are stepped through, and which of
// them are hotspots.
const DEFINITIONS = {
  'coastal-forest': { parts: COASTAL_PARTS, order: COASTAL_ORDER, regions: COASTAL_REGIONS.map(({ id }) => id) },
  ...FOREST_SERVICE_POSTERS,
  ...BC_FERRIES_POSTERS
}

const idsIn = (selector) => [...selector.matchAll(/#([\w-]+)/g)].map((m) => m[1])
const hasId = (svg, id) => svg.includes(`id="${id}"`)

test('every layer a part names can be found by a CSS selector', () => {
  for (const [id, { parts }] of Object.entries(DEFINITIONS)) {
    for (const [partId, part] of Object.entries(parts)) {
      for (const layer of idsIn(part.layer ?? '')) assert.match(layer, /^[a-z]/i, `${id}/${partId}: #${layer} starts with a digit`)
    }
  }
})

test('every series lists posters that exist, and every poster is in the series it names', () => {
  const listed = posterIds()
  assert.equal(new Set(listed).size, listed.length, 'a poster is listed twice')
  assert.deepEqual([...listed].sort(), Object.keys(POSTERS).sort())
  for (const series of SERIES) {
    assert.ok(series.title && series.kind, `${series.id} is missing its words`)
    for (const id of series.posters) assert.equal(POSTERS[id].series, series.id, `${id} names another series`)
  }
  for (const id of listed) assert.equal(seriesOf(id).id, POSTERS[id].series)
})

test('every poster has a drawing whose viewBox is the catalogue’s', () => {
  for (const [id, meta] of Object.entries(POSTERS)) {
    const svg = DRAWINGS[id]
    assert.ok(svg, `${id} has no drawing`)
    const { x, y, w, h } = meta.view
    const viewBox = /viewBox="([^"]+)"/.exec(svg)[1].split(/[\s,]+/).map(Number)
    assert.deepEqual(viewBox, [x, y, w, h], `${id}: viewBox`)
    assert.ok(meta.page.w > 0 && meta.page.h > 0, `${id}: page`)
    assert.ok(Math.abs(meta.page.w / meta.page.h - w / h) < 0.01, `${id}: the page is not the drawing’s shape`)
  }
})

test('every part sits on its drawing, and names layers the drawing has', () => {
  for (const [id, { parts, order, regions }] of Object.entries(DEFINITIONS)) {
    const { view } = POSTERS[id]
    const svg = DRAWINGS[id]
    assert.equal(order[0], 'overview', `${id} does not start from the whole poster`)
    assert.deepEqual([...order].sort(), Object.keys(parts).sort(), `${id}: order and parts differ`)
    assert.deepEqual([...regions].sort(), order.filter((part) => part !== 'overview').sort(), `${id}: every part but the overview is a hotspot`)
    for (const partId of order) {
      const part = parts[partId]
      const { x, y, w, h } = part.box
      assert.ok(w > 0 && h > 0, `${id}/${partId}: empty box`)
      assert.ok(x >= view.x - 1 && y >= view.y - 1 && x + w <= view.x + view.w + 1 && y + h <= view.y + view.h + 1, `${id}/${partId}: box off the drawing`)
      if (partId === 'overview') continue
      assert.ok(part.label && part.hint, `${id}/${partId}: label and hint`)
      assert.ok(part.layer, `${id}/${partId}: no layer to spotlight`)
      for (const layer of idsIn(part.layer)) assert.ok(hasId(svg, layer), `${id}/${partId}: the drawing has no #${layer}`)
    }
  }
})

test('the data panels say something, and every link lands somewhere that exists', () => {
  const internal = new Set(FOREST_LOGOS.map(({ id }) => id))
  const galleries = new Set(GALLERY_COLLECTIONS.map(({ id }) => id))
  for (const [id, { parts }] of Object.entries({ ...FOREST_SERVICE_POSTERS, ...BC_FERRIES_POSTERS })) {
    for (const [partId, { panel }] of Object.entries(parts)) {
      assert.ok(panel?.eyebrow && panel.heading && panel.lede, `${id}/${partId}: panel`)
      for (const block of panel.blocks ?? []) {
        for (const link of block.links ?? []) {
          const { to } = link
          assert.ok(link.label, `${id}/${partId}: a link without a label`)
          if (to.view === 'posters') {
            assert.ok(POSTERS[to.poster], `${id}/${partId}: no poster ${to.poster}`)
            assert.ok(DEFINITIONS[to.poster].parts[to.part ?? 'overview'], `${id}/${partId}: ${to.poster} has no part ${to.part}`)
          } else if (to.view === 'internal') {
            assert.equal(to.internal, 'forests')
            if (to['internal-logo']) assert.ok(internal.has(to['internal-logo']), `${id}/${partId}: no logo ${to['internal-logo']}`)
          } else if (to.view === 'gallery') {
            assert.ok(galleries.has(to.logos), `${id}/${partId}: no logo collection ${to.logos}`)
          } else if (to.view === 'government') {
            assert.ok(GOVERNMENT.includes(`"${to.node}"`), `${id}/${partId}: no body ${to.node}`)
          } else {
            assert.fail(`${id}/${partId}: a link to an unknown view, ${to.view}`)
          }
        }
      }
    }
  }
})

test('the evergreen emblem and the posters that carry it point at each other', () => {
  const emblem = FOREST_LOGOS.find(({ id }) => id === 'forest-service-emblem')
  assert.ok(emblem, 'the emblem is among the Forests logos')
  assert.equal(emblem.kind, 'drawing')
  const carriers = emblem.seenOn.map(({ to }) => to.poster).sort()
  const withEmblem = Object.entries(FOREST_SERVICE_POSTERS).filter(([, { parts }]) => parts.emblem).map(([id]) => id).sort()
  assert.deepEqual(carriers, withEmblem)
  for (const id of carriers) assert.ok(hasId(DRAWINGS[id], 'forest-service-emblem'), `${id} draws no emblem`)
})

test('the two fire-prevention badges share one green', () => {
  const fills = (svg) => new Set([...svg.matchAll(/(?:fill|stroke)="(#[0-9a-f]{6})"/gi)].map((m) => m[1].toUpperCase()))
  const drop = fills(DRAWINGS['dont-drop-it'])
  const gamble = fills(DRAWINGS['dont-gamble-with-fire'])
  assert.ok(drop.has('#003E2D') && gamble.has('#003E2D'))
  assert.ok(!gamble.has('#01375D'), 'the gamble badge still paints its old blue')
})

test('neighbours step through the posters in catalogue order', () => {
  const ids = posterIds()
  assert.deepEqual(neighbours(ids[0]), { previous: null, next: ids[1] })
  assert.deepEqual(neighbours(ids.at(-1)), { previous: ids.at(-2), next: null })
})
