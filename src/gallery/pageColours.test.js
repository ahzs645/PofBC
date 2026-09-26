import { test } from 'node:test'
import assert from 'node:assert/strict'
import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'
import { luminance, pageColoursFor } from './pageColours.js'

const printed = (id) => ONE_OFF_MARKS[id].printed

test('every mark loses its published ground on the page', () => {
  for (const id of Object.keys(ONE_OFF_MARKS)) {
    for (const theme of ['light', 'dark']) assert.equal(pageColoursFor(printed(id), theme).background, 'none', `${id} ${theme}`)
  }
})

test('a mark published reversed takes its colour version on a light page, keeping its gold', () => {
  const welcome = printed('welcome-bc')
  const light = pageColoursFor(welcome, 'light')
  assert.ok(luminance(light.name) < 0.2, 'the name goes dark')
  assert.equal(light.accent, welcome.accent)
  assert.equal(light.sun, welcome.sun)
})

test('a mark published on white takes its reversal on a dark page, keeping its own colours', () => {
  const stats = pageColoursFor(printed('bc-stats'), 'dark')
  assert.ok(luminance(stats.name) > 0.8, 'the name goes white')
  assert.equal(stats.accent, printed('bc-stats').accent)
  // BC Timber Sales' green lightens rather than turning white.
  const bcts = pageColoursFor(printed('bcts'), 'dark')
  assert.notEqual(bcts.name, '#ffffff')
  assert.ok(luminance(bcts.name) > luminance(printed('bcts').name))
})

test('a mark already in the page’s version is left as published', () => {
  const stats = printed('bc-stats')
  const light = pageColoursFor(stats, 'light')
  for (const role of Object.keys(stats)) if (role !== 'background') assert.equal(light[role], stats[role], role)
})
