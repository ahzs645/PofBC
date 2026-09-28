// A supplied mark is drawn as it came: nothing added to it but a ground, and nothing that would
// collide with another mark on the same page.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { CROWN_MARKS } from '../assets/crownMarks.js'
import { isReversed, renderSuppliedSvg } from './renderSupplied.js'

const ids = Object.keys(CROWN_MARKS)

test('every mark is plain vector drawing, with no text, image or script', () => {
  for (const id of ids) {
    const { svg } = renderSuppliedSvg({ id })
    assert.doesNotMatch(svg, /<(image|text|script|style|foreignObject|use)\b/, id)
    assert.doesNotMatch(svg, /(inkscape|sodipodi):/, id)
  }
})

test('no two marks share an id, so any of them can sit on one page', () => {
  const seen = new Map()
  for (const id of ids) {
    for (const [, name] of CROWN_MARKS[id].body.matchAll(/\sid="([^"]*)"/g)) {
      assert.ok(name.startsWith(`${id}-`), `${id}: ${name} is not prefixed`)
      assert.ok(!seen.has(name), `${name} is in both ${seen.get(name)} and ${id}`)
      seen.set(name, id)
    }
    for (const [, name] of CROWN_MARKS[id].body.matchAll(/url\(#([^)]+)\)/g)) {
      assert.match(CROWN_MARKS[id].body, new RegExp(`id="${name}"`), `${id} points at ${name}, which it lacks`)
    }
  }
})

test('the drawing is the file’s own, placed rather than changed', () => {
  const plain = renderSuppliedSvg({ id: 'icbc-rounded-orange' }).svg
  const placed = renderSuppliedSvg({ id: 'icbc-rounded-orange', background: '#ffffff', clearSpace: 0.25, width: 800, title: 'ICBC' }).svg
  assert.ok(plain.includes(CROWN_MARKS['icbc-rounded-orange'].body))
  assert.ok(placed.includes(CROWN_MARKS['icbc-rounded-orange'].body))
  assert.match(placed, /viewBox="-40.5 -40.5 243 243"/)
  assert.match(placed, /width="800" height="800"/)
  assert.match(placed, /<rect [^>]*fill="#ffffff"/)
  assert.doesNotMatch(plain, /<rect /)
})

test('only the marks supplied reversed are white alone', () => {
  assert.deepEqual(ids.filter(isReversed), ['bclc-legacy-reversed', 'bcf-wave-white'])
})
