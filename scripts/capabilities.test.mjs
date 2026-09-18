// The manifest is generated, so it cannot drift by hand — but it can drift by omission, if a new
// option is added to the application and nobody teaches the generator about it. These checks are
// the reminder.

import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { CLEAR_SPACE_ORDER, LAYOUT_ORDER, MARK_ALIGNMENT_ORDER } from '../src/logo/layouts.js'
import { BRAND_COLORS } from '../src/logo/logoColors.js'
import { EXPORT_FORMAT_ORDER, SIZE_PRESETS } from '../src/export/exportLogo.js'
import { MINISTRIES } from '../src/ministries/ministries.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

// Gitignored, like the fonts: a fresh clone that has not built yet skips rather than fails.
const manifest = (() => {
  try {
    return JSON.parse(readFileSync(resolve(root, 'public/capabilities.json'), 'utf8'))
  } catch {
    return null
  }
})()

const missing = manifest ? false : 'run `npm run build:capabilities` first'

test('the manifest lists every lockup, in order', { skip: missing }, () => {
  assert.deepEqual(manifest.lockups.map((entry) => entry.id), LAYOUT_ORDER)
})

test('every lockup says where its numbers came from', { skip: missing }, () => {
  for (const lockup of manifest.lockups) {
    // Null is a real answer — side by side has no vector original — but the key must be present,
    // because "measured from artwork" and "inferred from a photograph" are different claims.
    assert.ok('derivedFrom' in lockup, lockup.id)
  }
  assert.equal(manifest.lockups.find((entry) => entry.id === 'columns').derivedFrom, null)
})

test('alignment is offered only where it does something', { skip: missing }, () => {
  for (const lockup of manifest.lockups) {
    if (lockup.markAlignment === null) continue
    assert.deepEqual(lockup.markAlignment.options, MARK_ALIGNMENT_ORDER, lockup.id)
    assert.ok(MARK_ALIGNMENT_ORDER.includes(lockup.markAlignment.default), lockup.id)
  }
  assert.equal(manifest.lockups.find((entry) => entry.id === 'stacked').markAlignment, null)
})

test('the manifest lists every format, colour, size and clear space', { skip: missing }, () => {
  assert.deepEqual(manifest.formats.map((entry) => entry.id), EXPORT_FORMAT_ORDER)
  assert.deepEqual(manifest.rasterWidths, SIZE_PRESETS)
  assert.deepEqual(manifest.clearSpace.map((entry) => entry.id), CLEAR_SPACE_ORDER)
  assert.deepEqual(manifest.colours.named, BRAND_COLORS)
})

test('the ministry list matches, and is dated', { skip: missing }, () => {
  const listed = manifest.ministries.groups.flatMap((group) => group.options)
  assert.deepEqual(listed, MINISTRIES)
  assert.match(manifest.ministries.reviewed, /^\d{4}-\d{2}$/)
})

test('clear space is stated as a rule and as a number', { skip: missing }, () => {
  // A factor alone makes an agent do arithmetic against a mark width it has to find first.
  for (const entry of manifest.clearSpace) {
    assert.equal(typeof entry.factorOfMarkWidth, 'number', entry.id)
    assert.equal(entry.units, entry.factorOfMarkWidth * manifest.mark.width, entry.id)
  }
})

test('the advertised agent tools are the ones the page registers', { skip: missing }, async () => {
  const { buildTools } = await import('../src/site/useAgentTools.js')
  const registered = buildTools({ current: {} }).map((tool) => tool.name)

  assert.deepEqual(manifest.agentTools.tools, registered)
})
