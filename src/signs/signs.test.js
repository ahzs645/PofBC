// The signs hang together as the posters do: every series lists real signs, every part sits on its
// drawing and names layers the drawing has, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { SIGNS, SIGN_SERIES, signIds } from './catalogue.js'
import { FOREST_SERVICE_SIGNS } from './forest-service/signs.js'
import { FISH_WILDLIFE_SIGNS } from './fish-wildlife/signs.js'
import { ENTRY_SIGNS } from './entering-bc/signs.js'
import { TOURISM_SIGNS } from './tourism/signs.js'
import { PARKS_SIGNS } from './parks/signs.js'
import { loadInitiative } from '../initiatives/initiatives.js'
import { POSTERS } from '../posters/catalogue.js'
import { FOREST_SERVICE_POSTERS } from '../posters/forest-service/posters.js'
import { GALLERY_COLLECTIONS } from '../gallery/collections.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const DRAWINGS = {
  ...Object.fromEntries(Object.keys(ENTRY_SIGNS).map((id) => [id, read(`./entering-bc/${id}.svg`)])),
  'fire-day': read('./forest-service/fire-day.svg'),
  'cheakamus-notice-to-anglers': read('./fish-wildlife/cheakamus.svg'),
  lookout: read('./forest-service/lookout.svg'),
  'forest-closure': read('./forest-service/forest-closure.svg'),
  'super-natural-bordered': read('./tourism/super-natural-bordered.svg'),
  'super-natural': read('./tourism/super-natural.svg'),
  'proposed-park-symbols': read('./parks/proposed-park-symbols.svg')
}
const ALL_SIGNS = { ...ENTRY_SIGNS, ...FOREST_SERVICE_SIGNS, ...TOURISM_SIGNS, ...FISH_WILDLIFE_SIGNS, ...PARKS_SIGNS }
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

test('every link lands somewhere that exists, and no text has an em dash', async () => {
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
          } else if (to.view === 'initiatives') {
            const initiative = await loadInitiative(to.initiative)
            const section = initiative?.sections.find((entry) => entry.id === to.section)
            assert.ok(section, `${id}/${partId}: no initiative section ${to.section}`)
            if (to.page) assert.ok(section.guide?.chapters.flatMap((entry) => entry.pages)[to.page - 1], `no guide page ${to.page}`)
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

test('the Cheakamus sign draws the gallery’s Fish and Wildlife paths in sign colours', () => {
  const master = read('../../public/identity-recreation-conservation/drc-fw-oval-1973.svg')
  const sign = DRAWINGS['cheakamus-notice-to-anglers']
  const emblem = sign.split('id="ck-fw-emblem"')[1].split('id="ck-red-header"')[0]
  const paths = (svg) => [...svg.matchAll(/<path\b[^>]*\sd="([^"]+)"[^>]*fill-rule="([^"]+)"/g)]
    .map(([, d, fillRule]) => ({ d: d.replace(/\s+/g, ' ').trim(), fillRule }))
  assert.ok(paths(master).length > 0)
  assert.deepEqual(paths(emblem), paths(master))
  assert.match(emblem, /fill="#E5B641"/)
  assert.match(emblem, /fill="#252D23"/)
})

test('the blue-bordered sign uses the font’s kerning and advances for each complete line', async () => {
  const { default: opentype } = await import('opentype.js')
  const file = new URL('../../artwork/signs/super-natural-bordered/texgyretermes-bold.otf', import.meta.url)
  const bytes = readFileSync(file)
  const font = opentype.parse(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength))
  const drawing = DRAWINGS['super-natural-bordered']
  const size = 99
  for (const [line, baseline] of [['Super, Natural', 127], ['British Columbia', 266], ['welcomes you', 377]]) {
    const start = (SIGNS['super-natural-bordered'].view.w - font.getAdvanceWidth(line, size)) / 2
    const expected = font.getPath(line, start, baseline, size, { kerning: true })
    const group = drawing.split(`aria-label="${line}"`)[1].split('</g>')[0]
    assert.doesNotMatch(group, /transform=/)
    const actual = [...group.matchAll(/<path d="([^"]+)"/g)].map(([, path]) => path).join('')
    assert.equal(actual, expected.toPathData({ flipY: false, decimalPlaces: 3 }), line)
  }
})

test('the closure sign is the package’s two faces in one drawing, one strip showing at a time', () => {
  const drawing = DRAWINGS['forest-closure']
  const artwork = (name) => read(`../../artwork/signs/forest-closure/svg/${name}`)
  const paths = (svg) => [...svg.matchAll(/ d="([^"]+)"/g)].map(([, d]) => d)
  const open = artwork('forest-closure-open.svg')
  const closed = artwork('forest-closure-closed.svg')
  const closedStrip = closed.slice(closed.indexOf('<g id="closed-panel"'))
  // Every path of the OPEN sign, then the CLOSED strip's, unchanged.
  assert.deepEqual(paths(drawing), [...paths(open), ...paths(closedStrip)])
  // Its ids are prefixed, so it can sit on a page beside another drawing without a collision.
  for (const [, id] of drawing.matchAll(/ id="([^"]+)"/g)) assert.ok(id.startsWith('fc-'), id)
  for (const [, id] of drawing.matchAll(/url\(#([^)]+)\)/g)) assert.ok(drawing.includes(`id="${id}"`), id)
  assert.ok(!/<title[^>]*>[^<]*—/.test(drawing))
  // The Strip switch names a face for each option; as drawn, the first shows and the rest are hidden.
  const { options } = ALL_SIGNS['forest-closure'].variations
  assert.deepEqual(options.map(({ id }) => id), ['open', 'closed'])
  options.forEach(({ show }, i) => {
    for (const name of idsIn(show)) {
      const tag = new RegExp(`<g id="${name}"[^>]*>`).exec(drawing)?.[0]
      assert.ok(tag, `no #${name}`)
      assert.equal(tag.includes('display="none"'), i > 0, name)
    }
  })
})

test('the park symbols are the package’s 22 drawings, in the report’s order, and say they were proposed', () => {
  const drawing = DRAWINGS['proposed-park-symbols']
  const manifest = JSON.parse(read('../../research/identity/recreation-conservation-2026-11-21/construction/park_symbols/manifest.json'))
  const sign = PARKS_SIGNS['proposed-park-symbols']
  assert.equal(manifest.symbols.length, 22)
  assert.deepEqual(sign.order.slice(1).map((key) => sign.parts[key].label), manifest.symbols.map(({ name }) => name))
  manifest.symbols.forEach(({ id }, index) => {
    const source = read(`../../artwork/recreation-conservation/park_symbols/${id}.svg`)
    const key = sign.order[index + 1]
    const group = new RegExp(`<g id="pps-${key}"[^>]*>([\\s\\S]*?)</g></g></g>`).exec(drawing)?.[1]
    assert.ok(group, key)
    // Every shape is the file's own, unchanged.
    const shapes = (svg) => [...svg.matchAll(/<(path|circle|rect|polygon|line|ellipse)\b([^>]*)>/g)].map((m) => m[0].replace(/\s*\/?>$/, ''))
      .map((tag) => tag.replace(/clip-path="[^"]*"/, '').replace(/\s+/g, ' '))
    assert.ok(shapes(source).length >= 2, key)
    assert.deepEqual(shapes(group), shapes(source), key)
  })
  for (const [, id] of drawing.matchAll(/ id="([^"]+)"/g)) assert.match(id, /^pps-[a-z-]+$/)
  for (const key of sign.order.slice(1)) assert.match(sign.parts[key].panel.em, /proposed/)
  assert.match(sign.parts.overview.panel.blocks[0], /proposals/)
})
