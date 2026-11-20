// The cards hang together as the signs do: every series lists real cards, every part sits on its
// drawing and names layers the drawing has, every story chapter is short and sourced where it
// claims a source, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { CARDS, CARD_SERIES, cardIds } from './catalogue.js'
import { FOREST_SERVICE_CARDS } from './forest-service/cards.js'
import { POSTERS } from '../posters/catalogue.js'
import { SIGNS } from '../signs/catalogue.js'
import { FOREST_LOGOS } from '../internal/forestLogos.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const DRAWINGS = { 'england-expects': read('./forest-service/england-expects.svg') }
const ALL_CARDS = { ...FOREST_SERVICE_CARDS }
const GOVERNMENT = read('../government/historyData.js')
const idsIn = (selector) => [...selector.matchAll(/#([\w-]+)/g)].map((m) => m[1])
// A sentence ends at a stop after a lowercase letter or a figure, so initials (H. R.) and
// abbreviations (vol. II) do not end one.
const sentences = (text) => text.split(/(?<=[a-z0-9)][.!?]”?)(?<!\b(?:vol|no|pp)\.)\s+(?=[A-Z“])/).length

test('every series lists cards that exist, each in the series it names', () => {
  const listed = cardIds()
  assert.equal(new Set(listed).size, listed.length)
  assert.deepEqual([...listed].sort(), Object.keys(CARDS).sort())
  for (const series of CARD_SERIES) for (const id of series.cards) assert.equal(CARDS[id].series, series.id)
  assert.deepEqual(Object.keys(ALL_CARDS).sort(), cardIds().sort())
  assert.deepEqual(Object.keys(DRAWINGS).sort(), cardIds().sort())
})

test('every part sits on its drawing and names layers the drawing has', () => {
  for (const [id, { parts, order, regions }] of Object.entries(ALL_CARDS)) {
    const { view } = CARDS[id]
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

test('every part tells the story in a few sentences, and its sources are named', () => {
  for (const [id, { parts, order }] of Object.entries(ALL_CARDS)) {
    for (const partId of order) {
      const { story, storySources = [] } = parts[partId]
      assert.ok(Array.isArray(story) && story.length, `${id}/${partId}: no story`)
      const count = story.reduce((n, paragraph) => n + sentences(paragraph), 0)
      assert.ok(count >= 1 && count <= 3, `${id}/${partId}: ${count} sentences`)
      for (const source of storySources) {
        assert.ok(source.label, `${id}/${partId}: unnamed source`)
        if (source.href) assert.match(source.href, /^https:\/\//)
      }
    }
  }
})

test('every link lands somewhere that exists, and no text has an em dash', () => {
  for (const [id, { parts, variations }] of Object.entries(ALL_CARDS)) {
    for (const option of variations?.options ?? []) assert.ok(!`${option.label} ${option.note}`.includes('—'), `${id}: ${option.label}`)
    for (const [partId, { panel, story, storySources, label, hint }] of Object.entries(parts)) {
      const words = [label, hint, panel.eyebrow, panel.heading, panel.em, panel.lede, ...story, ...(storySources ?? []).map((s) => s.label)]
      for (const block of panel.blocks ?? []) {
        if (typeof block === 'string') words.push(block)
        if (block.h) words.push(block.h)
        if (block.note) words.push(block.note)
        for (const row of block.facts ?? []) words.push(...row)
        for (const link of block.links ?? []) words.push(link.label, link.note)
        for (const source of block.sources ?? []) words.push(source.label)
      }
      for (const text of words.filter(Boolean)) assert.ok(!text.includes('—') && !text.includes(' - '), `${id}/${partId}: ${text}`)
      for (const block of panel.blocks ?? []) {
        for (const { to } of block.links ?? []) {
          if (to.view === 'posters') assert.ok(POSTERS[to.poster], `${id}/${partId}: no poster ${to.poster}`)
          else if (to.view === 'signs') assert.ok(SIGNS[to.sign], `${id}/${partId}: no sign ${to.sign}`)
          else if (to.view === 'government') assert.ok(GOVERNMENT.includes(`"${to.node}"`), `${id}/${partId}: no body ${to.node}`)
          else if (to.view === 'internal') assert.ok(FOREST_LOGOS.some(({ id: logo }) => logo === to['internal-logo']), `${id}/${partId}: no logo ${to['internal-logo']}`)
          else assert.fail(`${id}/${partId}: unexpected view ${to.view}`)
        }
      }
    }
  }
})

test('the card and the Lands Department seal point at each other', () => {
  const seal = FOREST_LOGOS.find(({ id }) => id === 'forest-service-lands-department')
  const back = seal.seenOn.find(({ to }) => to.view === 'cards')
  assert.ok(back && CARDS[back.to.card] && ALL_CARDS[back.to.card].parts[back.to.part], 'the seal does not lead to the card')
  const links = ALL_CARDS['england-expects'].parts.emblem.panel.blocks.flatMap((block) => block.links ?? [])
  assert.ok(links.some(({ to }) => to['internal-logo'] === seal.id), 'the card does not lead to the seal')
  assert.ok(seal.comments.some((comment) => comment.includes('Root and Branch') && comment.includes('1924')))
})

test('the card is the package’s drawing, its ids prefixed and its title plain', () => {
  const drawing = DRAWINGS['england-expects']
  const master = read('../../artwork/cards/forest-service-card/artwork/forest-service-card.svg')
  const paths = (svg) => [...svg.matchAll(/ d="([^"]+)"/g)].map(([, d]) => d)
  // Every path of the package's card, unchanged: only paint already inherited and whitespace went.
  assert.deepEqual(paths(drawing), paths(master))
  assert.equal(drawing.match(/<circle /g).length, master.match(/<circle /g).length)
  for (const [, id] of drawing.matchAll(/ id="([^"]+)"/g)) assert.ok(id.startsWith('fsc-'), id)
  assert.ok(!/<title[^>]*>[^<]*(—| - )/.test(drawing))
  // Its black-on-white switch swaps exactly the two colours the drawing uses.
  const colours = new Set([...drawing.matchAll(/(?:fill|stroke)="(#[0-9A-Fa-f]{6})"/g)].map(([, c]) => c.toUpperCase()))
  const { options } = ALL_CARDS['england-expects'].variations
  assert.deepEqual([...colours].sort(), options[1].swap.map(([from]) => from).sort())
  assert.equal(CARDS['england-expects'].prefetch, false)
})
