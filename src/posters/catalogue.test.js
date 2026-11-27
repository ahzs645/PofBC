// The posters hang together: every series lists real posters, every part sits on its drawing and
// names layers the drawing has, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { FACETS, POSTERS, SERIES, listedPosterIds, neighbours, posterIds, seriesOf } from './catalogue.js'
import { RECORDS } from './records.js'
import { STORIES } from './stories.js'
import { MAX_AREA, MAX_EDGE, maxWidthFor } from './export/exportSvg.js'
import { FOREST_SERVICE_POSTERS } from './forest-service/posters.js'
import { BC_FERRIES_POSTERS } from './bc-ferries/posters.js'
import { WILDLIFE_TREES } from './wildlife-trees/posters.js'
import { NOXIOUS_WEEDS_POSTERS } from './noxious-weeds/posters.js'
import { EXPO_86_POSTERS } from './expo-86/posters.js'
import { GALLERY_COLLECTIONS } from '../gallery/collections.js'
import { ORDER as COASTAL_ORDER, PARTS as COASTAL_PARTS, REGIONS as COASTAL_REGIONS } from './coastal-forest/parts.js'
import { FOREST_LOGOS } from '../internal/forestLogos.js'
import { SIGNS } from '../signs/catalogue.js'
import { CARDS } from '../cards/catalogue.js'
import { PINS } from '../pins/catalogue.js'
import { CERTAINTY, GROUPS, MARK_OBJECTS, connectedPosters, connectionsOf, groupedConnections, objectsForLogo, postersForLogo, postersForPatch } from './connections.js'

import { bearAwareWindowId, bearAwareWindowSvg } from '../initiatives/bearAwareArtwork.js'
import { initiativeById, loadInitiative } from '../initiatives/initiatives.js'
import { bearAwareWindow } from '../signs/bearAwareWindow.js'
import { CARECARD_POSTER } from './carecard/poster.js'
import { SPRING_POSTER } from './super-natural-spring/poster.js'
import { FERRIES_POSTER } from './super-natural-ferries/poster.js'
import { LAKE_POSTER } from './super-natural-lake/poster.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const DRAWINGS = {
  [bearAwareWindowId]: read(`../../public/${bearAwareWindowSvg}`),
  'super-natural-spring': read('./super-natural-spring/spring-visitors.svg'),
  'super-natural-ferries': read('./super-natural-ferries/poster.svg'),
  'super-natural-lake': read('./super-natural-lake/poster.svg'),
  'new-carecard': read('./carecard/new-carecard.svg'),
  'coastal-forest': read('./coastal-forest/poster.svg'),
  'use-your-ashtray': read('./forest-service/use-your-ashtray.svg'),
  'dont-drop-it': read('./forest-service/dont-drop-it.svg'),
  'dont-gamble-with-fire': read('./forest-service/dont-gamble-with-fire.svg'),
  'reward-living-forest': read('./forest-service/reward-living-forest.svg'),
  'enjoy-protect-forests': read('./forest-service/enjoy-protect-forests.svg'),
  'be-careful': read('./forest-service/be-careful.svg'),
  'coons-age': read('./forest-service/coons-age.svg'),
  'prevent-forest-fires': read('./forest-service/prevent-forest-fires.svg'),
  'matches-not-for-children': read('./forest-service/matches-not-for-children.svg'),
  'go-bc-ferries': read('./bc-ferries/go-bc-ferries.svg'),
  'queen-of-sidney': read('./bc-ferries/queen-of-sidney.svg'),
  'wildlife-trees': read('./wildlife-trees/wildlife-trees.svg'),
  'beware-these-alien-invaders': read('./noxious-weeds/beware-these-alien-invaders.svg'),
  'shattering-the-environment': read('./noxious-weeds/shattering-the-environment.svg'),
  'explosion-in-slow-motion': read('./noxious-weeds/explosion-in-slow-motion.svg'),
  'expo-86-davidson': read('./expo-86/expo-86-davidson.svg'),
  'expo-86-fiorucci': read('./expo-86/expo-86-fiorucci.svg'),
  'our-british-columbia': read('./expo-86/our-british-columbia.svg')
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
  } else if (to.view === 'initiatives') {
    assert.ok(initiativeById(to.initiative), `${where}: no initiative ${to.initiative}`)
  } else if (to.view === 'gallery') {
    assert.ok(galleries.has(to.logos), `${where}: no logo collection ${to.logos}`)
  } else if (to.view === 'government') {
    assert.ok(GOVERNMENT.includes(`"${to.node}"`), `${where}: no body ${to.node}`)
  } else if (to.view === 'signs') {
    assert.ok(SIGNS[to.sign], `${where}: no sign ${to.sign}`)
  } else if (to.view === 'cards') {
    assert.ok(CARDS[to.card], `${where}: no card ${to.card}`)
  } else if (to.view === 'pins') {
    assert.ok(PINS[to.pin], `${where}: no pin ${to.pin}`)
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
  [bearAwareWindowId]: bearAwareWindow,
  'super-natural-spring': SPRING_POSTER,
  'super-natural-ferries': FERRIES_POSTER,
  'super-natural-lake': LAKE_POSTER,
  'new-carecard': CARECARD_POSTER,
  'coastal-forest': { parts: COASTAL_PARTS, order: COASTAL_ORDER, regions: COASTAL_REGIONS.map(({ id }) => id) },
  ...FOREST_SERVICE_POSTERS,
  ...BC_FERRIES_POSTERS,
  'wildlife-trees': WILDLIFE_TREES,
  ...NOXIOUS_WEEDS_POSTERS,
  ...EXPO_86_POSTERS
}
// The posters whose panels are data.
const DATA_POSTERS = { [bearAwareWindowId]: bearAwareWindow, 'super-natural-spring': SPRING_POSTER, 'super-natural-ferries': FERRIES_POSTER, 'super-natural-lake': LAKE_POSTER, 'new-carecard': CARECARD_POSTER, ...FOREST_SERVICE_POSTERS, ...BC_FERRIES_POSTERS, 'wildlife-trees': WILDLIFE_TREES, ...NOXIOUS_WEEDS_POSTERS, ...EXPO_86_POSTERS }

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

test('the shelf lists every poster in catalogue order', () => {
  assert.deepEqual(listedPosterIds(), posterIds())
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

test('every connection says what it is and what it rests on, and leads somewhere that exists', async () => {
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
      if (entry.to?.view === 'initiatives' && entry.to.record) {
        const initiative = await loadInitiative(entry.to.initiative)
        const section = initiative.sections.find(({ id }) => id === entry.to.section)
        assert.ok(section?.records.some(({ id }) => id === entry.to.record), where)
      }
      if (entry.href) assert.match(entry.href, /^https:\/\//, `${where}: href`)
      if (entry.record) assert.ok(RECORDS[entry.record] && !entry.to && !entry.href, `${where}: no record ${entry.record}`)
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
  assert.deepEqual(postersForPatch('S48-O01').map(({ poster }) => poster).sort(), ['coons-age', 'enjoy-protect-forests', 'reward-living-forest'])
  assert.ok(postersForPatch('FO-fire-control').some(({ poster, certainty }) => poster === 'dont-drop-it' && certainty === 'thematic'))
  assert.deepEqual(postersForPatch('no-such-patch'), [])
})

test('no card dates a piece more firmly than its evidence', () => {
  for (const id of ['reward-living-forest', 'enjoy-protect-forests', 'prevent-forest-fires', 'wildlife-trees', 'beware-these-alien-invaders', 'shattering-the-environment', 'explosion-in-slow-motion', 'queen-of-sidney']) {
    assert.match(POSTERS[id].when, /^Undated/, `${id}: ${POSTERS[id].when}`)
  }
  assert.match(POSTERS['coastal-forest'].when, /1979–86 or 1988–91/)
  assert.match(POSTERS['matches-not-for-children'].when, /^About 1966–67, from its centenary captions$/)
  // Dated by a document, and saying which.
  assert.equal(POSTERS['be-careful'].when, '1960, from the Protection Bulletin')
  assert.equal(POSTERS['coons-age'].when, '2 December 1971, Gulf Islands Driftwood')
  for (const id of ['super-natural-ferries', 'super-natural-lake']) {
    assert.match(POSTERS[id].when, /^Publication date unestablished/, `${id}: publication date inferred from its award`)
    assert.match(POSTERS[id].when, /campaign awarded in 1985/, `${id}: missing award date`)
  }
})

test('the tourism campaign keeps all three advertisements connected and preserves their comparison sources', () => {
  const campaign = ['super-natural-spring', 'super-natural-ferries', 'super-natural-lake']
  assert.deepEqual(seriesOf('super-natural-spring').posters, campaign)
  for (const id of campaign) {
    assert.equal(POSTERS[id].made, 'mixed', `${id}: photographic reconstruction presented as vector-only`)
    assert.equal(POSTERS[id].prefetch, false, `${id}: large photographic artwork fetched before opening`)
    const related = connectionsOf(id).filter(({ rel }) => rel === 'Same advertising campaign').map(({ to }) => to.poster)
    assert.deepEqual(related, campaign.filter((other) => other !== id), `${id}: missing campaign companion`)
    const loader = read(`./${id}/index.js`)
    const file = id === 'super-natural-spring' ? 'reference.png' : 'reference.jpg'
    assert.ok(loader.includes(`import reference from './${file}'`), `${id}: no original comparison source`)
    assert.ok(existsSync(new URL(`./${id}/${file}`, import.meta.url)), `${id}: comparison source missing`)
    assert.match(loader, /reference:\s*\{[\s\S]*src: reference/, `${id}: reference is not passed to the viewer`)
  }
  assert.match(POSTERS['super-natural-lake'].title, /what’s left\?$/)
})

test('every record says what it rests on, and is printed where it says', () => {
  const used = new Set(connectedPosters().flatMap((id) => connectionsOf(id)).map(({ record }) => record).filter(Boolean))
  assert.deepEqual([...used].sort(), Object.keys(RECORDS).sort(), 'a record no connection opens, or the reverse')
  for (const [id, record] of Object.entries(RECORDS)) {
    assert.ok(record.kind && record.title && record.summary && record.limits, `${id}: incomplete`)
    assert.ok(record.facts.length && record.facts.every(([k, v]) => k && v), `${id}: facts`)
    assert.ok(record.seenOn.length, `${id}: printed nowhere`)
    for (const { poster, part, note } of record.seenOn) {
      assert.ok(note && DEFINITIONS[poster]?.parts[part], `${id}: no part ${poster}/${part}`)
    }
    for (const source of record.sources) assert.match(source.href, /^https:\/\//, `${id}: source`)
  }
})

test('every piece has a story, and the written ones tell exactly its parts', () => {
  for (const [id, { parts, order }] of Object.entries(DEFINITIONS)) {
    assert.ok(order.every((partId) => parts[partId].story?.length), `${id}: a part without a story`)
    assert.ok(order.every((partId) => parts[partId].panel?.heading), `${id}: a chapter without a heading`)
  }
  for (const [id, story] of Object.entries(STORIES)) {
    assert.deepEqual(Object.keys(story).sort(), [...DEFINITIONS[id].order].sort(), `${id}: the story and the parts differ`)
  }
})

test('the leaflet’s pages are the papers the build laid down', () => {
  const { pages } = NOXIOUS_WEEDS_POSTERS['beware-these-alien-invaders']
  const svg = DRAWINGS['beware-these-alien-invaders']
  const papers = [...svg.matchAll(/<g(?: transform="translate\(0 (\d+)\)")?><rect id="btai-paper-\d" width="(\d+)" height="(\d+)"/g)]
    .map((m) => ({ x: 0, y: Number(m[1] ?? 0), w: Number(m[2]), h: Number(m[3]) }))
  assert.equal(papers.length, 5)
  assert.deepEqual(pages.map(({ box }) => box), papers)
  assert.ok(pages.every(({ label }) => label))
})

test('the shelf can be filtered: every card names its issuer, subject and format, and says what it is', () => {
  for (const [id, meta] of Object.entries(POSTERS)) {
    for (const { key } of FACETS) assert.ok(meta[key], `${id}: ${key}`)
    assert.ok(meta.blurb?.length > 20 && meta.blurb.length < 110, `${id}: blurb`)
  }
  for (const { key } of FACETS) {
    const values = new Set(listedPosterIds().map((id) => POSTERS[id][key]))
    assert.ok(values.size > 1 && values.size <= 10, `${key}: ${values.size} values is no use as a filter`)
  }
})

test('a raster is held to its whole canvas, not its width alone', () => {
  for (const { view } of Object.values(POSTERS)) {
    const aspect = view.h / view.w
    const width = maxWidthFor(aspect)
    assert.ok(width > 0 && width <= MAX_EDGE && width * aspect <= MAX_EDGE + 1 && width * width * aspect <= MAX_AREA, `${view.w} × ${view.h}`)
  }
  // The long sheet: a width a square poster could take is refused.
  assert.ok(maxWidthFor(3) < 8000)
  assert.equal(maxWidthFor(1), 10000)
})

test('Wildlife Trees has the original to compare with, in the drawing’s shape', () => {
  const jpeg = readFileSync(new URL('./wildlife-trees/reference.jpg', import.meta.url))
  assert.ok(jpeg.length < 800e3, `the reference is ${Math.round(jpeg.length / 1e3)} KB`)
  // The first start-of-frame marker holds the picture's size.
  let at = 2
  while (jpeg[at + 1] < 0xc0 || jpeg[at + 1] > 0xc2) at += 2 + jpeg.readUInt16BE(at + 2)
  const height = jpeg.readUInt16BE(at + 5)
  const width = jpeg.readUInt16BE(at + 7)
  const { w, h } = POSTERS['wildlife-trees'].view
  assert.ok(Math.abs(width / height - w / h) < 0.002, `the reference is ${width} × ${height}, not the drawing’s shape`)
})

test('neighbours step through the posters in catalogue order', () => {
  const ids = listedPosterIds()
  for (const [i, id] of ids.entries()) {
    assert.deepEqual(neighbours(id), { previous: ids[i - 1] ?? null, next: ids[i + 1] ?? null })
  }
})

// The pieces imported from supplied packages: the 1960 decal, the 1971 advertisement, the
// Prevent Forest Fires and matches posters, and two of the Expo 86 posters.
const IMPORTED = ['be-careful', 'coons-age', 'prevent-forest-fires', 'matches-not-for-children', 'expo-86-fiorucci', 'our-british-columbia']

test('the imported pieces say nothing with an em dash, on the card, in the panels, the story or the drawing’s title', () => {
  const strings = (value) => typeof value === 'string' ? [value] : Array.isArray(value) ? value.flatMap(strings) : value && typeof value === 'object' ? Object.values(value).flatMap(strings) : []
  for (const id of IMPORTED) {
    const said = [...strings(POSTERS[id]), ...strings(DEFINITIONS[id].parts), ...strings(connectionsOf(id))]
    for (const text of said) assert.ok(!text.includes('—'), `${id}: “${text}”`)
    assert.ok(!/<title[^>]*>[^<]*—/.test(DRAWINGS[id]), `${id}: the drawing’s title`)
  }
})

test('the imported drawings keep their ids to themselves', () => {
  const ids = (svg) => [...svg.matchAll(/ id="([^"]+)"/g)].map((m) => m[1])
  // Every id but the shared emblem layer, which the posters that carry it all call by one name.
  for (const id of ids(DRAWINGS['be-careful'])) assert.ok(id.startsWith('bcc-'), `be-careful: ${id}`)
  for (const id of ids(DRAWINGS['coons-age'])) assert.ok(/^(coon-|ad-emblem-|forest-service-emblem$)/.test(id), `coons-age: ${id}`)
  for (const id of ids(DRAWINGS['prevent-forest-fires'])) assert.ok(id.startsWith('pff-'), `prevent-forest-fires: ${id}`)
  for (const id of ids(DRAWINGS['matches-not-for-children'])) assert.ok(id.startsWith('mnc-'), `matches-not-for-children: ${id}`)
  for (const id of ids(DRAWINGS['expo-86-fiorucci'])) assert.ok(id.startsWith('fio-'), `expo-86-fiorucci: ${id}`)
  for (const id of ids(DRAWINGS['our-british-columbia'])) assert.ok(id.startsWith('obc-'), `our-british-columbia: ${id}`)
  for (const piece of IMPORTED) {
    const all = Object.entries(DRAWINGS).filter(([id]) => id !== piece).flatMap(([, svg]) => ids(svg))
    for (const id of ids(DRAWINGS[piece])) {
      if (id !== 'forest-service-emblem') assert.ok(!all.includes(id), `${piece}: ${id} is already used by another drawing`)
    }
  }
})

test('Prevent Forest Fires is fetched only when opened, and every reference in it resolves', () => {
  const svg = DRAWINGS['prevent-forest-fires']
  const meta = POSTERS['prevent-forest-fires']
  assert.equal(meta.prefetch, false, 'a 1.6 MB drawing fetched on spec')
  assert.equal(meta.when, 'Undated')
  assert.ok(svg.length < 1.7e6, `the drawing is ${(svg.length / 1e6).toFixed(2)} MB`)
  assert.ok(!/<image\b|base64,|inkscape:/.test(svg), 'a picture or editor markup left in the drawing')
  for (const m of svg.matchAll(/url\(#([^)]+)\)/g)) assert.ok(hasId(svg, m[1]), `no #${m[1]}`)
  for (const name of /aria-labelledby="([^"]+)"/.exec(svg)[1].split(' ')) assert.ok(hasId(svg, name), `no #${name}`)
  // Its seven layers, one per part but the lettering split three ways.
  for (const layer of ['paper', 'canopy', 'flames', 'foreground', 'script', 'headline', 'footer']) assert.ok(hasId(svg, `pff-layer-${layer}`), `no ${layer} layer`)
})

test('Prevent Forest Fires leads to its series, the fire-prevention pieces and the signs', () => {
  const { parts } = FOREST_SERVICE_POSTERS['prevent-forest-fires']
  const panel = Object.values(parts).flatMap(({ panel }) => (panel.blocks ?? []).flatMap((block) => block.links ?? [])).map(({ to }) => to)
  const places = [...panel, ...connectionsOf('prevent-forest-fires').map(({ to }) => to).filter(Boolean)]
  const leads = (view, key, value) => places.some((to) => to.view === view && to[key] === value)
  for (const poster of ['reward-living-forest', 'enjoy-protect-forests', 'dont-drop-it', 'be-careful', 'coons-age']) assert.ok(leads('posters', 'poster', poster), `no link to ${poster}`)
  assert.ok(leads('cards', 'card', 'england-expects'), 'no link to the England Expects card')
  assert.ok(leads('pins', 'pin', 'forest-branch-campfires'), 'no link to the campfire oval')
  for (const sign of ['lookout', 'forest-closure']) assert.ok(leads('signs', 'sign', sign), `no link to ${sign}`)
  // The context for its argument, cited as context.
  const { storySources } = parts.slogan
  assert.ok(storySources.some(({ label }) => label.startsWith('H. R. MacMillan')))
  assert.ok(storySources.some(({ href }) => href === 'https://www.for.gov.bc.ca/hfd/library/documents/bib30294.pdf'))
  assert.match(parts.slogan.story.join(' '), /neither mentions this poster/)
})

test('Matches Are Not for Children!! is fetched only when opened, and every reference in it resolves', () => {
  const svg = DRAWINGS['matches-not-for-children']
  assert.equal(POSTERS['matches-not-for-children'].prefetch, false, 'a 4 MB drawing fetched on spec')
  assert.ok(svg.length < 4.5e6, `the drawing is ${(svg.length / 1e6).toFixed(2)} MB`)
  assert.ok(!/<image\b|base64,|inkscape:/.test(svg), 'a picture or editor markup left in the drawing')
  for (const m of svg.matchAll(/url\(#([^)]+)\)/g)) assert.ok(hasId(svg, m[1]), `no #${m[1]}`)
  for (const name of /aria-labelledby="([^"]+)"/.exec(svg)[1].split(' ')) assert.ok(hasId(svg, name), `no #${name}`)
  // Its eight layers.
  for (const layer of ['painted-background', 'paper-reserves', 'matchstick-illustration', 'headline-lettering', 'forest-service-oval', 'footer-lettering', 'centennial-caption', 'publication-marks']) {
    assert.ok(hasId(svg, `mnc-${layer}`), `no ${layer} layer`)
  }
  // The parts found by the start of an id find something.
  for (const [partId, { layer }] of Object.entries(FOREST_SERVICE_POSTERS['matches-not-for-children'].parts)) {
    for (const [, start] of (layer ?? '').matchAll(/\[id\^="([\w-]+)"\]/g)) assert.ok(svg.includes(`id="${start}`), `${partId}: no id starts ${start}`)
  }
  // The captions that date it.
  assert.match(svg, /aria-label="CENTENARY OF THE CONFEDERATION OF CANADA"/)
  assert.match(svg, /aria-label="1966"/)
})

test('the matches poster’s seal and its logo point at each other', () => {
  const seal = FOREST_LOGOS.find(({ id }) => id === 'forest-service-one-ink-oval')
  assert.deepEqual(seal.seenOn.map(({ to }) => [to.poster, to.part]), [['matches-not-for-children', 'seal']])
  assert.deepEqual(postersForLogo('forest-service-one-ink-oval'), ['matches-not-for-children'])
  const links = FOREST_SERVICE_POSTERS['matches-not-for-children'].parts.seal.panel.blocks.flatMap((block) => block.links ?? [])
  assert.ok(links.some(({ to }) => to.view === 'internal' && to['internal-logo'] === 'forest-service-one-ink-oval'), 'the seal does not link to its logo')
  assert.ok(hasId(DRAWINGS['matches-not-for-children'], 'mnc-forest-service-oval'))
})

test('a part is found by its box, its shapes, or its lettering and the gaps between', () => {
  for (const [id, { parts }] of Object.entries(DEFINITIONS)) {
    for (const [partId, part] of Object.entries(parts)) {
      assert.ok([undefined, 'shape', 'letters'].includes(part.hit), `${id}/${partId}: hit ${part.hit}`)
      if (part.gap !== undefined) assert.ok(part.hit === 'letters' && part.gap > 0 && part.gap <= 2, `${id}/${partId}: gap ${part.gap}`)
    }
  }
})

test('the advertisement names its photograph by file, and the file is a light copy of the supplied one', () => {
  const svg = DRAWINGS['coons-age']
  assert.ok(!svg.includes('base64,'), 'the photograph is still inside the drawing')
  assert.ok(svg.length < 200e3, `the drawing is ${Math.round(svg.length / 1e3)} KB`)
  assert.deepEqual([...svg.matchAll(/<image\b[^>]*\bhref="([^"]+)"/g)].map((m) => m[1]), ['coons-age-raccoon.webp'])
  const webp = readFileSync(new URL('./forest-service/coons-age-raccoon.webp', import.meta.url))
  assert.equal(webp.toString('ascii', 8, 12), 'WEBP')
  assert.ok(webp.length < 600e3, `the photograph is ${Math.round(webp.length / 1e3)} KB`)
  // The emblem is drawn with plain SVG elements: an HTML parser does not draw prefixed ones.
  assert.ok(!/<\/?\w+:\w/.test(svg.replace(/<\?xml[^>]*>/, '')), 'a namespace-prefixed element')
})

