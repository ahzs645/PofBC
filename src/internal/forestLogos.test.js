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

test('evergreen study retains separate islands and preserves the three-island coloured master', () => {
  const logo = FOREST_LOGOS.find(({ id }) => id === 'forest-service-emblem')
  assert.ok(logo.article?.title.includes('Socreds'))
  const { studies } = variantsFor(logo)
  assert.equal(studies.length, 4)
  assert.ok(studies.every(({ id }) => !id.includes('joined')))
  const original = readFileSync(new URL('./forest-service-emblem.svg', import.meta.url), 'utf8')
  assert.match(original, /id="island-north"/)
  assert.match(original, /id="island-middle"/)
  assert.match(original, /id="island-south"/)
  const printStudy = readFileSync(new URL('./forest-service-emblem-one-ink.svg', import.meta.url), 'utf8')
  const threeStudy = readFileSync(new URL('./forest-service-emblem-three-islands-separated.svg', import.meta.url), 'utf8')
  assert.match(printStudy, /id="northern-island"/)
  assert.match(printStudy, /id="southern-island"/)
  assert.doesNotMatch(printStudy, /id="central-island-colour-study"/)
  assert.match(threeStudy, /id="northern-island"/)
  assert.match(threeStudy, /id="central-island-colour-study"/)
  assert.match(threeStudy, /id="southern-island"/)
  assert.doesNotMatch(threeStudy, /islands-combined|coast-join-bridge/)
})

test('all four studies have one squircle and independently editable islands', () => {
  const files = [
    'forest-service-emblem-one-ink.svg',
    'forest-service-emblem-three-islands-separated.svg',
    'forest-service-emblem-three-islands-green.svg',
    'forest-service-emblem-reverse.svg'
  ]
  const svgs = files.map((file) => readFileSync(new URL(`./${file}`, import.meta.url), 'utf8'))
  const badges = svgs.map((svg) => svg.match(/id="badge-outline" d="([^"]+)"/)?.[1])
  assert.ok(badges.every(Boolean))
  assert.equal(new Set(badges).size, 1, 'every study uses the exact same analytic squircle path')
  for (const [i, svg] of svgs.entries()) {
    assert.match(svg, /id="province-and-tree"[^>]*fill-rule="evenodd"/)
    assert.match(svg, /id="badge-outline"[^>]*fill="none" stroke="#(?:111111|FFFFFF|176A3C)" stroke-width="13\.85"/)
    assert.doesNotMatch(svg, /<(?:image|filter)\b/)
    assert.doesNotMatch(svg, /islands-combined|coast-join-bridge/)
    assert.ok([...svg.matchAll(/<path\b/g)].length <= 5, `${files[i]} should use concise editable primitives`)
    assert.match(svg, /id="northern-island"/)
    assert.match(svg, /id="southern-island"/)
  }
  assert.doesNotMatch(svgs[0], /id="central-island-colour-study"/)
  assert.match(svgs[1], /id="central-island-colour-study"/)
  assert.match(svgs[2], /id="central-island-colour-study"/)
  assert.doesNotMatch(svgs[3], /id="central-island-colour-study"/)
  assert.match(svgs[3], /id="ground"/)
})
