// The signs hang together as the posters do: every series lists real signs, every part sits on its
// drawing and names layers the drawing has, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { SIGNS, SIGN_SERIES, signIds } from './catalogue.js'
import { FOREST_SERVICE_SIGNS } from './forest-service/signs.js'
import { TOURISM_SIGNS } from './tourism/signs.js'
import { POSTERS } from '../posters/catalogue.js'
import { FOREST_SERVICE_POSTERS } from '../posters/forest-service/posters.js'
import { GALLERY_COLLECTIONS } from '../gallery/collections.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const DRAWINGS = {
  lookout: read('./forest-service/lookout.svg'),
  'super-natural': read('./tourism/super-natural.svg')
}
const ALL_SIGNS = { ...FOREST_SERVICE_SIGNS, ...TOURISM_SIGNS }
const GOVERNMENT = read('../government/historyData.js')
const GALLERIES = new Set(GALLERY_COLLECTIONS.map(({ id }) => id))
const idsIn = (selector) => [...selector.matchAll(/#([\w-]+)/g)].map((m) => m[1])

test('every series lists signs that exist, each in the series it names', () => {
  const listed = signIds()
  assert.equal(new Set(listed).size, listed.length)
  assert.deepEqual([...listed].sort(), Object.keys(SIGNS).sort())
  for (const series of SIGN_SERIES) for (const id of series.signs) assert.equal(SIGNS[id].series, series.id)
})

test('every part sits on its drawing and names layers the drawing has', () => {
  for (const [id, { parts, order, regions }] of Object.entries(ALL_SIGNS)) {
    const { view } = SIGNS[id]
    const viewBox = /viewBox="([^"]+)"/.exec(DRAWINGS[id])[1].split(/[\s,]+/).map(Number)
    assert.deepEqual(viewBox, [view.x, view.y, view.w, view.h], `${id}: viewBox`)
    assert.equal(order[0], 'overview')
    assert.deepEqual([...order].sort(), Object.keys(parts).sort())
    assert.deepEqual([...regions].sort(), order.filter((part) => part !== 'overview').sort())
    for (const partId of order) {
      const { box, layer, panel } = parts[partId]
      assert.ok(box.x >= view.x - 1 && box.y >= view.y - 1 && box.x + box.w <= view.x + view.w + 1 && box.y + box.h <= view.y + view.h + 1, `${id}/${partId}: box`)
      assert.ok(panel?.heading && panel.lede, `${id}/${partId}: panel`)
      if (partId === 'overview') continue
      for (const name of idsIn(layer)) assert.ok(DRAWINGS[id].includes(`id="${name}"`), `${id}/${partId}: no #${name}`)
    }
  }
})

test('every link lands somewhere that exists, and no text has an em dash', () => {
  for (const [id, { parts }] of Object.entries(ALL_SIGNS)) {
    for (const [partId, { panel }] of Object.entries(parts)) {
      const words = [panel.eyebrow, panel.heading, panel.em, panel.lede, ...(panel.blocks ?? []).filter((b) => typeof b === 'string')]
      for (const text of words.filter(Boolean)) assert.ok(!text.includes('—'), `${id}/${partId}: ${text}`)
      for (const block of panel.blocks ?? []) {
        for (const { to } of block.links ?? []) {
          if (to.view === 'posters') {
            assert.ok(POSTERS[to.poster], `${id}/${partId}: no poster ${to.poster}`)
            if (to.part) assert.ok(FOREST_SERVICE_POSTERS[to.poster]?.parts[to.part], `${id}/${partId}: no part ${to.part}`)
          } else if (to.view === 'signs') {
            assert.ok(SIGNS[to.sign] && to.sign !== id, `${id}/${partId}: no other sign ${to.sign}`)
          } else if (to.view === 'gallery') {
            assert.ok(GALLERIES.has(to.logos), `${id}/${partId}: no logo collection ${to.logos}`)
          } else if (to.view === 'government') {
            assert.ok(GOVERNMENT.includes(`"${to.node}"`), `${id}/${partId}: no body ${to.node}`)
          } else assert.ok(['internal', 'generator'].includes(to.view), `${id}/${partId}: unexpected view ${to.view}`)
        }
      }
    }
  }
})

test('every sign has a drawing and a set of parts, and nothing else does', () => {
  assert.deepEqual(Object.keys(ALL_SIGNS).sort(), signIds().sort())
  assert.deepEqual(Object.keys(DRAWINGS).sort(), signIds().sort())
})

test('the welcome sign keeps the flag the generator draws, path for path', async () => {
  const { FLAG } = await import('../assets/flagMark.js')
  const drawing = DRAWINGS['super-natural']
  const group = /<g id="existing-spirit-of-bc-flag"[^>]*>([\s\S]*?)<\/g>/.exec(drawing)[1]
  const paths = [...group.matchAll(/ d="([^"]+)" fill="([^"]+)"/g)].map(([, d, fill]) => ({ d, fill }))
  assert.deepEqual(paths, FLAG.shapes.map(({ d, fill }) => ({ d, fill })))
  // Its ids are prefixed, so it can sit on a page beside another drawing without a collision.
  for (const generic of ['id="title"', 'id="desc"', 'id="above-baseline"', 'id="below-baseline"']) assert.ok(!drawing.includes(generic), generic)
})
