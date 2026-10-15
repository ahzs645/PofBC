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
    const { colours } = variantsFor(logo)
    assert.equal(colours[0].id, 'colour', `${logo.id} opens on its full colour`)
    assert.equal(colours[0].artwork, logo.artwork)
    for (const variant of colours) {
      const svg = readFileSync(new URL(`./${variant.artwork}`, import.meta.url), 'utf8')
      const paints = new Set([...svg.matchAll(/(?:fill|stroke)="(#[0-9a-f]{6})"/gi)].map((m) => m[1].toUpperCase()))
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
