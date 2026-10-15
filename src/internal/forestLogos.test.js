// The Forests family's supplied drawings are there, and their colourways recolour colours the
// drawings actually use.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { FOREST_LOGOS, variantsFor } from './forestLogos.js'

const drawings = FOREST_LOGOS.filter((logo) => logo.kind === 'drawing')

test('every design has its words, and ids are unique', () => {
  assert.equal(new Set(FOREST_LOGOS.map(({ id }) => id)).size, FOREST_LOGOS.length)
  for (const logo of FOREST_LOGOS) {
    assert.ok(logo.name && logo.description && logo.evidence && logo.comments.length, `${logo.id} is missing its words`)
    assert.ok(Array.isArray(logo.sources), `${logo.id}: sources`)
  }
})

test('every supplied drawing exists, and every recolour names a colour it paints', () => {
  assert.ok(drawings.length >= 2)
  for (const logo of drawings) {
    const { colours, studies = [] } = variantsFor(logo)
    assert.equal(colours[0].id, 'colour', `${logo.id} opens on its full colour`)
    for (const variant of [...colours, ...studies]) {
      const svg = readFileSync(new URL(`./${variant.artwork}`, import.meta.url), 'utf8')
      const paints = new Set([...svg.matchAll(/(?:fill|stroke)="(#[0-9a-f]{6})"/gi)].map((m) => m[1].toUpperCase()))
      assert.ok(svg.includes('<svg') && !svg.includes('<image'), `${variant.id} must be all-vector`)
      for (const [from, to] of Object.entries(variant.recolour)) {
        assert.ok(paints.has(from), `${logo.id}/${variant.id}: the drawing never paints ${from}`)
        assert.match(to, /^#[0-9A-F]{6}$/, `${logo.id}/${variant.id}: ${to}`)
      }
    }
  }
})

test('the green-and-gold oval keeps its landscape clipped to the inner rim', () => {
  const svg = readFileSync(new URL('./forest-service-green-gold.svg', import.meta.url), 'utf8')
  assert.match(svg, /<clipPath id="landscape-clip"/)
  assert.match(svg, /clip-path="url\(#landscape-clip\)"/)
})

test('evergreen joined-island studies are explicit and the original remains separate', () => {
  const logo = FOREST_LOGOS.find(({ id }) => id === 'forest-service-emblem')
  assert.ok(logo.article?.title.includes('Socreds'))
  const variants = variantsFor(logo)
  assert.ok(variants.studies.length >= 5)
  const original = readFileSync(new URL('./forest-service-emblem.svg', import.meta.url), 'utf8')
  const merged = readFileSync(new URL('./forest-service-emblem-joined-islands.svg', import.meta.url), 'utf8')
  assert.match(original, /id="island-north"/)
  assert.match(original, /id="island-middle"/)
  assert.match(original, /id="island-south"/)
  assert.match(merged, /id="islands-combined"/)
  assert.doesNotMatch(merged, /id="island-middle"/)
  const reverse = readFileSync(new URL('./forest-service-emblem-reverse-joined-islands.svg', import.meta.url), 'utf8')
  assert.match(reverse, /id="ground"/)
  assert.match(reverse, /id="islands-combined"/)
})


// Structural regression: no return to the earlier seven-shape recolour with a white painted triangle.
test('black-and-white print reconstructions share the same compact geometry and true tree cutout', () => {
  const variants = [
    'forest-service-emblem-one-ink.svg',
    'forest-service-emblem-joined-islands.svg',
    'forest-service-emblem-reverse.svg',
    'forest-service-emblem-reverse-joined-islands.svg'
  ]
  const svgs = variants.map((file) => readFileSync(new URL(`./${file}`, import.meta.url), 'utf8'))
  const badges = svgs.map((svg) => svg.match(/id="badge-outline" d="([^"]+)"/)?.[1])
  assert.ok(badges.every(Boolean))
  assert.equal(new Set(badges).size, 1, 'all one-ink studies must share their manually reconstructed badge geometry')
  for (const [index, svg] of svgs.entries()) {
    assert.match(svg, /id="province-and-tree"[^>]*fill-rule="evenodd"/)
    assert.match(svg, /id="badge-outline"[^>]*fill-rule="evenodd"/)
    assert.doesNotMatch(svg, /<(?:image|filter)\b/)
    assert.ok([...svg.matchAll(/<path\b/g)].length <= 4, `${variants[index]} must remain a compact geometric vector`)
  }
  assert.match(svgs[0], /id="northern-island"/)
  assert.match(svgs[0], /id="southern-island"/)
  assert.doesNotMatch(svgs[0], /id="islands-combined"/)
  assert.match(svgs[1], /id="islands-combined"/)
  assert.match(svgs[3], /id="islands-combined"/)
  assert.match(svgs[2], /id="ground"/)
  assert.match(svgs[3], /id="ground"/)
})
