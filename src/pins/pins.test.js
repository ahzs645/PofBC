// The pins hang together as the signs do: every series lists real pins, every part sits on its
// drawing and names layers the drawing has (the society's drawings as the stage prefixes them),
// every story chapter is short, and every link lands somewhere that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { PINS, PIN_SERIES, pinIds } from './catalogue.js'
import { INTERIOR_UNIVERSITY_PINS } from './interior-university/pins.js'
import { NOVELTY_PINS } from './novelty/pins.js'
import { prefixIds } from './prefixIds.js'
import { FACE_SHAPES, constructionProblems } from './construction.js'
import { buttonProfile, profileNormals } from './buttonProfile.js'
import { POSTERS } from '../posters/catalogue.js'
import { SIGNS } from '../signs/catalogue.js'
import { GALLERY_COLLECTIONS } from '../gallery/collections.js'
import { IDENTITY_SUBJECTS } from '../gallery/identitySubjects.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const RECORDS = JSON.parse(read('../../public/unbc-origins/assets.json'))
const DRAWINGS = {
  ...Object.fromEntries(Object.entries(INTERIOR_UNIVERSITY_PINS).map(([id, { file, prefix }]) => [id, prefixIds(read(`../../public/unbc-origins/svg/${file}`), prefix)])),
  'welcome-bc-pattison': read('./novelty/welcome-bc-pattison.svg')
}
const ALL_PINS = { ...INTERIOR_UNIVERSITY_PINS, ...NOVELTY_PINS }
const GALLERIES = new Set(GALLERY_COLLECTIONS.map(({ id }) => id))
const SUBJECTS = new Set(IDENTITY_SUBJECTS.map(({ id }) => id))
const idsIn = (selector) => [...selector.matchAll(/#([\w-]+)/g)].map((m) => m[1])
// A sentence ends at a stop after a lowercase letter or a figure, so initials do not end one.
const sentences = (text) => text.split(/(?<=[a-z0-9)][.!?]”?)\s+(?=[A-Z“])/).length

test('every series lists pins that exist, each in the series it names', () => {
  const listed = pinIds()
  assert.equal(new Set(listed).size, listed.length)
  assert.deepEqual([...listed].sort(), Object.keys(PINS).sort())
  for (const series of PIN_SERIES) for (const id of series.pins) assert.equal(PINS[id].series, series.id)
  assert.deepEqual(Object.keys(ALL_PINS).sort(), pinIds().sort())
})

test('every part sits on its drawing and names layers the drawing has', () => {
  for (const [id, { parts, order, regions }] of Object.entries(ALL_PINS)) {
    const { view } = PINS[id]
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

test('every drawing has its ids prefixed and a plain title', () => {
  for (const [id, drawing] of Object.entries(DRAWINGS)) {
    const prefix = INTERIOR_UNIVERSITY_PINS[id]?.prefix ?? 'wbc-'
    for (const [, name] of drawing.matchAll(/ id="([^"]+)"/g)) assert.ok(name.startsWith(prefix), `${id}: ${name}`)
    for (const [, names] of drawing.matchAll(/aria-labelledby="([^"]+)"/g)) for (const name of names.split(' ')) assert.ok(drawing.includes(`id="${name}"`), `${id}: ${name}`)
    assert.ok(!/<title[^>]*>[^<]*(—| - )/.test(drawing), id)
  }
})

test('the society’s pins are the gallery’s files, and their panels say they are reconstructions', () => {
  for (const [id, { file, parts }] of Object.entries(INTERIOR_UNIVERSITY_PINS)) {
    const record = RECORDS.find((asset) => asset.svg === `svg/${file}`)
    assert.equal(record?.id, id, `${file}: no record`)
    assert.equal(record.status, 'Reconstructed')
    const facts = Object.fromEntries(parts.overview.panel.blocks.find((block) => block.facts).facts)
    assert.match(facts.Status, /reconstruction/)
    const links = parts.overview.panel.blocks.flatMap((block) => block.links ?? [])
    assert.ok(links.some(({ to }) => to.view === 'gallery' && to.subject === 'university-of-northern-bc'), `${id}: no UNBC link`)
    assert.ok(links.some(({ to }) => to.view === 'gallery' && to.logos === 'collected-interior-university-society'), `${id}: no IUS link`)
  }
})

test('every part tells the story in a few sentences, and its sources are named', () => {
  for (const [id, { parts, order }] of Object.entries(ALL_PINS)) {
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
  for (const [id, { parts, variations }] of Object.entries(ALL_PINS)) {
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
          else if (to.view === 'gallery' && to.logos) assert.ok(GALLERIES.has(to.logos), `${id}/${partId}: no logo collection ${to.logos}`)
          else if (to.view === 'gallery' && to.subject) assert.ok(SUBJECTS.has(to.subject), `${id}/${partId}: no subject ${to.subject}`)
          else assert.fail(`${id}/${partId}: unexpected link ${JSON.stringify(to)}`)
        }
      }
    }
  }
})

test('the welcome button is the package’s drawing, with a white face to switch to', () => {
  const drawing = DRAWINGS['welcome-bc-pattison']
  const master = read('../../artwork/pins/welcome-bc-pattison/welcome-bc-pin.svg')
  const white = read('../../artwork/pins/welcome-bc-pattison/welcome-bc-pin-white.svg')
  const paths = (svg) => [...svg.matchAll(/ d="([^"]+)"/g)].map(([, d]) => d)
  assert.deepEqual(paths(drawing), paths(master))
  const [[from, to]] = NOVELTY_PINS['welcome-bc-pattison'].variations.options[1].swap
  assert.equal(master.replace(from, to), white)
})

test('the welcome button has a printed-button recipe that says what is illustrative', () => {
  const recipe = NOVELTY_PINS['welcome-bc-pattison'].construction
  assert.deepEqual(constructionProblems(recipe), [])
  assert.equal(recipe.kind, 'printed-button')
  assert.equal(recipe.diameterStatus, 'illustrative')
  assert.equal(recipe.fittingStatus, 'generic')
  assert.ok(recipe.dome >= 0 && recipe.dome <= 0.15, `dome ${recipe.dome}`)
  // The face prints the pin's own drawing, and the edge carries that drawing's ground colour.
  assert.equal(recipe.face.svg, 'welcome-bc-pattison.svg')
  assert.ok(DRAWINGS['welcome-bc-pattison'].includes(`fill="${recipe.face.background}"`))
  for (const line of recipe.evidence) assert.ok(!line.includes('—'), line)
  // Its facts say so too.
  const facts = Object.fromEntries(NOVELTY_PINS['welcome-bc-pattison'].parts.overview.panel.blocks.find((block) => block.facts).facts)
  assert.match(facts['Size in 3D'], /^38 mm \(1½ in\), illustrative$/)
  assert.match(facts['Back in 3D'], /generic/)
  // Every recipe a pin has is sound; pins without one simply have no 3D view.
  for (const [id, { construction }] of Object.entries(ALL_PINS)) if (construction) assert.deepEqual(constructionProblems(construction), [], id)
})

test('a printed button’s profile stays within its diameter and closes to the back', () => {
  for (const diameterMm of [32, 38, 57]) {
    for (const { dome } of FACE_SHAPES) {
      const profile = buttonProfile({ diameterMm, dome })
      const { points, radius, shoulder, backZ, lipRadius } = profile
      assert.equal(points[0].r, 0)
      assert.ok(Math.abs(points[0].z - dome * diameterMm) < 1e-9, 'the face rises by the dome')
      for (const { r } of points) assert.ok(r >= 0 && r <= diameterMm / 2 + shoulder + 1e-9, `r ${r}`)
      assert.ok(Math.abs(Math.max(...points.map(({ r }) => r)) - radius) < 1e-9, 'the edge is the diameter')
      // The front is everything seen straight on, and nothing behind it is printed.
      const firstBack = points.findIndex(({ printed }) => !printed)
      assert.ok(firstBack > 0 && points.slice(firstBack).every(({ printed }) => !printed))
      for (let i = 1; i < firstBack; i++) assert.ok(points[i].z <= points[i - 1].z + 1e-9, 'the face only falls away to the rim')
      // It closes to the back: the last point is on the back plane, inside the rim, at the lip.
      const last = points[points.length - 1]
      assert.ok(Math.abs(last.z - backZ) < 1e-9 && Math.abs(last.r - lipRadius) < 1e-9 && last.r < radius)
      assert.ok(profile.plateZ > backZ && profile.plateRadius > lipRadius && profile.plateRadius < radius, 'the tin back sits behind the lip')
      // The normals face out: up from the face, out from the side, back from the lip.
      const normals = profileNormals(points)
      assert.ok(normals[0].nz > 0.999 && normals[normals.length - 1].nz < -0.999)
      assert.ok(normals[points.findIndex(({ r }) => r === radius)].nr > 0.999)
    }
  }
  assert.throws(() => buttonProfile({ diameterMm: 38, dome: 0.2 }), RangeError)
})
