// The posters hang together: every series lists real posters, every part sits on its drawing and
// names layers the drawing has, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { POSTERS, SERIES, neighbours, posterIds, seriesOf } from './catalogue.js'
import { FOREST_SERVICE_POSTERS } from './forest-service/posters.js'
import { BC_FERRIES_POSTERS } from './bc-ferries/posters.js'
import { WILDLIFE_TREES } from './wildlife-trees/posters.js'
import { NOXIOUS_WEEDS_POSTERS } from './noxious-weeds/posters.js'
import { GALLERY_COLLECTIONS } from '../gallery/collections.js'
import { ORDER as COASTAL_ORDER, PARTS as COASTAL_PARTS, REGIONS as COASTAL_REGIONS } from './coastal-forest/parts.js'
import { FOREST_LOGOS } from '../internal/forestLogos.js'
import { CERTAINTY, GROUPS, MARK_OBJECTS, connectedPosters, connectionsOf, groupedConnections, objectsForLogo, postersForLogo, postersForPatch } from './connections.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const DRAWINGS = {
  'coastal-forest': read('./coastal-forest/poster.svg'),
  'dont-drop-it': read('./forest-service/dont-drop-it.svg'),
  'dont-gamble-with-fire': read('./forest-service/dont-gamble-with-fire.svg'),
  'reward-living-forest': read('./forest-service/reward-living-forest.svg'),
  'enjoy-protect-forests': read('./forest-service/enjoy-protect-forests.svg'),
  'go-bc-ferries': read('./bc-ferries/go-bc-ferries.svg'),
  'queen-of-sidney': read('./bc-ferries/queen-of-sidney.svg'),
  'wildlife-trees': read('./wildlife-trees/wildlife-trees.svg'),
  'beware-these-alien-invaders': read('./noxious-weeds/beware-these-alien-invaders.svg'),
  'shattering-the-environment': read('./noxious-weeds/shattering-the-environment.svg'),
  'explosion-in-slow-motion': read('./noxious-weeds/explosion-in-slow-motion.svg')
}
const GOVERNMENT = read('../government/historyData.js')

// The patch library (the Patcher submodule), for links into the Patches and Badges views.
const MANIFEST = new URL('../../vendor/patcher/library/manifest.json', import.meta.url)
const LIBRARY = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : null
const PATCHES = new Map((LIBRARY?.orgs ?? []).flatMap((org) => org.patches.map((patch) => [patch.id, patch.collection])))
const ORGS = new Set((LIBRARY?.orgs ?? []).map((org) => org.id))

/** Fails unless a place on the site (a link's `to`) exists. `where` names the link in the message. */
const assertPlace = (to, where) => {
  const internal = new Set(FOREST_LOGOS.map(({ id }) => id))
  const galleries = new Set(GALLERY_COLLECTIONS.map(({ id }) => id))
  if (to.view === 'posters') {
    assert.ok(POSTERS[to.poster], `${where}: no poster ${to.poster}`)
    assert.ok(DEFINITIONS[to.poster].parts[to.part ?? 'overview'], `${where}: ${to.poster} has no part ${to.part}`)
  } else if (to.view === 'internal') {
    assert.equal(to.internal, 'forests')
    if (to['internal-logo']) assert.ok(internal.has(to['internal-logo']), `${where}: no logo ${to['internal-logo']}`)
  } else if (to.view === 'gallery') {
    assert.ok(galleries.has(to.logos), `${where}: no logo collection ${to.logos}`)
  } else if (to.view === 'government') {
    assert.ok(GOVERNMENT.includes(`"${to.node}"`), `${where}: no body ${to.node}`)
  } else if (to.view === 'patches' || to.view === 'badges') {
    // Without the submodule there is nothing to check these against.
    if (!LIBRARY) return
    if (to.patch) assert.equal(PATCHES.get(to.patch), to.view, `${where}: ${to.patch} is not in ${to.view}`)
    else assert.ok(ORGS.has(to.org), `${where}: no organization ${to.org}`)
  } else {
    assert.fail(`${where}: a link to an unknown view, ${to.view}`)
  }
}

// Every poster as the viewer sees it: its parts, the order they are stepped through, and which of
// them are hotspots.
const DEFINITIONS = {
  'coastal-forest': { parts: COASTAL_PARTS, order: COASTAL_ORDER, regions: COASTAL_REGIONS.map(({ id }) => id) },
  ...FOREST_SERVICE_POSTERS,
  ...BC_FERRIES_POSTERS,
  'wildlife-trees': WILDLIFE_TREES,
  ...NOXIOUS_WEEDS_POSTERS
}
// The posters whose panels are data.
const DATA_POSTERS = { ...FOREST_SERVICE_POSTERS, ...BC_FERRIES_POSTERS, 'wildlife-trees': WILDLIFE_TREES, ...NOXIOUS_WEEDS_POSTERS }

const idsIn = (selector) => [...selector.matchAll(/#([\w-]+)/g)].map((m) => m[1])
const partsIn = (selector) => [...selector.matchAll(/\[data-part="([\w-]+)"\]/g)].map((m) => m[1])
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
      for (const { x, y, w, h } of [part.box, ...(part.boxes ?? [])]) {
        assert.ok(w > 0 && h > 0, `${id}/${partId}: empty box`)
        assert.ok(x >= view.x - 1 && y >= view.y - 1 && x + w <= view.x + view.w + 1 && y + h <= view.y + view.h + 1, `${id}/${partId}: box off the drawing`)
      }
      // A part found by several boxes is framed by one that holds them all.
      for (const { x, y, w, h } of part.boxes ?? []) {
        const { box } = part
        assert.ok(x >= box.x - 1 && y >= box.y - 1 && x + w <= box.x + box.w + 1 && y + h <= box.y + box.h + 1, `${id}/${partId}: a hotspot outside the part's frame`)
      }
      if (partId === 'overview') continue
      assert.ok(part.label && part.hint, `${id}/${partId}: label and hint`)
      assert.ok(part.layer, `${id}/${partId}: no layer to spotlight`)
      for (const layer of idsIn(part.layer)) assert.ok(hasId(svg, layer), `${id}/${partId}: the drawing has no #${layer}`)
      for (const name of partsIn(part.layer)) assert.ok(svg.includes(`data-part="${name}"`), `${id}/${partId}: nothing in the drawing is tagged ${name}`)
    }
  }
})

test('the data panels say something, and every link lands somewhere that exists', () => {
  for (const [id, { parts }] of Object.entries(DATA_POSTERS)) {
    for (const [partId, { panel }] of Object.entries(parts)) {
      assert.ok(panel?.eyebrow && panel.heading && panel.lede, `${id}/${partId}: panel`)
      for (const block of panel.blocks ?? []) {
        for (const link of block.links ?? []) {
          assert.ok(link.label, `${id}/${partId}: a link without a label`)
          assertPlace(link.to, `${id}/${partId}`)
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

test('the Forest Service tree oval and Wildlife Trees point at each other', () => {
  const oval = FOREST_LOGOS.find(({ id }) => id === 'forest-service')
  assert.deepEqual(oval.seenOn.map(({ to }) => [to.poster, to.part]), [['wildlife-trees', 'oval']])
  const links = WILDLIFE_TREES.parts.oval.panel.blocks.flatMap((block) => block.links ?? [])
  assert.ok(links.some(({ to }) => to.view === 'internal' && to['internal-logo'] === 'forest-service'), 'the oval does not link to its logo')
  assert.ok(hasId(DRAWINGS['wildlife-trees'], 'forest-service-mark'))
})

test('a story tells every part of its poster, in order, with something to say', () => {
  for (const [id, { parts, order }] of Object.entries(DEFINITIONS)) {
    const told = order.filter((partId) => parts[partId].story)
    if (!told.length) continue
    assert.deepEqual(told, order, `${id}: a story leaves out a part`)
    for (const partId of told) {
      const { story } = parts[partId]
      assert.ok(Array.isArray(story) && story.length && story.every((p) => typeof p === 'string' && p.length > 20), `${id}/${partId}: story`)
    }
  }
})

test('the Wildlife Trees copy is light enough to draw: few paths, no editor notes', () => {
  const svg = DRAWINGS['wildlife-trees']
  assert.ok(svg.length < 16e6, `the drawing is ${(svg.length / 1e6).toFixed(1)} MB`)
  assert.ok((svg.match(/<path\b/g) ?? []).length < 2500, 'more paths than the joined copy has')
  assert.ok(!/<(?:title|desc|metadata)>/.test(svg.slice(svg.indexOf('</desc>') + 7, svg.lastIndexOf('<metadata>'))), 'editor notes left inside the drawing')
  assert.ok(!svg.includes('inkscape:'), 'editor attributes left in')
})

test('Wildlife Trees opens on a small preview in the drawing’s shape', () => {
  const png = readFileSync(new URL('./wildlife-trees/preview.png', import.meta.url))
  assert.ok(png.length < 300e3, `the preview is ${Math.round(png.length / 1e3)} KB`)
  const width = png.readUInt32BE(16)
  const height = png.readUInt32BE(20)
  const { w, h } = POSTERS['wildlife-trees'].view
  assert.ok(Math.abs(width / height - w / h) < 0.002, `the preview is ${width} × ${height}, not the drawing’s shape`)
  assert.ok(width >= 800, 'the preview is too small to stand in for the whole poster')
})

test('the Noxious Weeds drawings name their pictures by files that exist, and are light', () => {
  for (const id of Object.keys(NOXIOUS_WEEDS_POSTERS)) {
    const svg = DRAWINGS[id]
    assert.ok(!svg.includes('base64,'), `${id}: a picture is still inside the drawing`)
    assert.ok(svg.length < 600e3, `${id}: the drawing is ${Math.round(svg.length / 1e3)} KB`)
    const files = [...svg.matchAll(/href="(images\/[^"]+)"/g)].map((m) => m[1])
    assert.ok(files.length, `${id}: no pictures`)
    for (const file of files) assert.ok(readFileSync(new URL(`./noxious-weeds/${file}`, import.meta.url)).length > 0, `${id}: ${file}`)
    // Poppler numbers ids the same way in every file: each drawing's are its own.
    const prefix = { 'beware-these-alien-invaders': 'btai-', 'shattering-the-environment': 'ste-', 'explosion-in-slow-motion': 'eis-' }[id]
    for (const m of svg.matchAll(/ id="([^"]+)"/g)) assert.ok(m[1].startsWith(prefix), `${id}: the id ${m[1]} is not its own`)
  }
})

test('a highlight is a masked copy of a photograph in its own drawing', () => {
  for (const id of Object.keys(NOXIOUS_WEEDS_POSTERS)) {
    const svg = DRAWINGS[id]
    for (const m of svg.matchAll(/<g data-part="([\w-]+)" data-highlight="" mask="url\(#([^)]+)\)"><use xlink:href="#([^"]+)"/g)) {
      assert.ok(hasId(svg, m[2]), `${id}/${m[1]}: no mask ${m[2]}`)
      assert.ok(hasId(svg, m[3]), `${id}/${m[1]}: no photograph ${m[3]}`)
    }
  }
})

test('the two fire-prevention badges share one green; the photograph’s blue is only a comparison', () => {
  const fills = (svg) => new Set([...svg.matchAll(/(?:fill|stroke)="(#[0-9a-f]{6})"/gi)].map((m) => m[1].toUpperCase()))
  const drop = fills(DRAWINGS['dont-drop-it'])
  const gamble = fills(DRAWINGS['dont-gamble-with-fire'])
  assert.ok(drop.has('#003E2D') && gamble.has('#003E2D'))
  assert.ok(!gamble.has('#01375D'), 'the gamble badge paints the photograph’s blue')
  const { options } = FOREST_SERVICE_POSTERS['dont-gamble-with-fire'].variations
  assert.ok(!options[0].swap, 'the first variation is the drawing as it is')
  const blue = options.find(({ id }) => id === 'as-photographed')
  assert.deepEqual(blue.swap, [['#003E2D', '#01375D']])
  assert.match(blue.note, /not a printing/, 'the blue is not labelled as the photograph’s')
})

test('every piece is worded for what it is made of, and its exports follow', () => {
  for (const [id, meta] of Object.entries(POSTERS)) {
    assert.ok(['vector', 'mixed', 'photographic'].includes(meta.made), `${id}: made`)
    const pictures = /<image\b/.test(DRAWINGS[id])
    assert.equal(meta.made !== 'vector', pictures, `${id}: says ${meta.made}, but ${pictures ? 'holds' : 'holds no'} pictures`)
  }
})

test('every connection says what it is and what it rests on, and leads somewhere that exists', () => {
  assert.deepEqual(connectedPosters().sort(), Object.keys(POSTERS).sort(), 'a piece has no connections')
  const groups = new Set(GROUPS.map(({ id }) => id))
  for (const id of connectedPosters()) {
    const entries = connectionsOf(id)
    assert.ok(entries.some(({ group }) => group === 'issuer'), `${id}: no issuer`)
    assert.equal(groupedConnections(id).reduce((n, group) => n + group.entries.length, 0), entries.length)
    const keys = entries.map(({ rel, label }) => rel + label)
    assert.equal(new Set(keys).size, keys.length, `${id}: a connection is listed twice`)
    for (const entry of entries) {
      const where = `${id} → ${entry.label}`
      assert.ok(groups.has(entry.group) && entry.rel && entry.label && entry.note, `${where}: incomplete`)
      assert.ok(CERTAINTY[entry.certainty], `${where}: certainty`)
      assert.ok(!(entry.to && entry.href), `${where}: both a place and a page`)
      if (entry.to) assertPlace(entry.to, where)
      if (entry.href) assert.match(entry.href, /^https:\/\//, `${where}: href`)
      if (entry.to?.view === 'posters') assert.notEqual(entry.to.poster === id && !entry.to.part, true, `${where}: leads to itself`)
    }
  }
})

test('a mark, the pieces that use it and the object made of it name each other', () => {
  for (const { logo } of MARK_OBJECTS) {
    const seenOn = FOREST_LOGOS.find(({ id }) => id === logo).seenOn.map(({ to }) => to.poster).sort()
    assert.deepEqual(postersForLogo(logo).sort(), seenOn, `${logo}: the registry and the logo’s own list differ`)
    for (const object of objectsForLogo(logo)) {
      assert.deepEqual(postersForPatch(object.to.patch).map(({ poster }) => poster).sort(), seenOn, `${object.to.patch}: not tied back to the pieces`)
    }
  }
  // The emblem's cloth square, from both posters; the fire artefacts, from the fire pieces.
  assert.deepEqual(postersForPatch('S48-O01').map(({ poster }) => poster).sort(), ['enjoy-protect-forests', 'reward-living-forest'])
  assert.ok(postersForPatch('FO-fire-control').some(({ poster, certainty }) => poster === 'dont-drop-it' && certainty === 'thematic'))
  assert.deepEqual(postersForPatch('no-such-patch'), [])
})

test('no card dates a piece more firmly than its evidence', () => {
  for (const id of ['reward-living-forest', 'enjoy-protect-forests', 'wildlife-trees', 'beware-these-alien-invaders', 'shattering-the-environment', 'explosion-in-slow-motion', 'queen-of-sidney']) {
    assert.match(POSTERS[id].when, /^Undated/, `${id}: ${POSTERS[id].when}`)
  }
  assert.match(POSTERS['coastal-forest'].when, /1979–86 or 1988–91/)
})

test('neighbours step through the posters in catalogue order', () => {
  const ids = posterIds()
  assert.deepEqual(neighbours(ids[0]), { previous: null, next: ids[1] })
  assert.deepEqual(neighbours(ids.at(-1)), { previous: ids.at(-2), next: null })
})
