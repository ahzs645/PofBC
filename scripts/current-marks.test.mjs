// The extracted artwork itself. Guards the shape of what extract_current_marks.py produced, since
// nothing downstream can tell a subtly wrong extraction from a right one.

import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const dir = resolve(root, 'public/current-marks')
const missing = existsSync(resolve(dir, 'index.json')) ? false : 'run `npm run extract:current-marks` first'

const catalogue = missing ? null : JSON.parse(readFileSync(resolve(dir, 'index.json'), 'utf8'))
const read = (file) => readFileSync(resolve(dir, file), 'utf8')

test('every ministry has both languages, and both files exist', { skip: missing }, () => {
  assert.ok(catalogue.ministries.length >= 20, `only ${catalogue.ministries.length} ministries`)

  for (const ministry of catalogue.ministries) {
    for (const language of ['en', 'fr']) {
      assert.ok(ministry[language], `${ministry.code} has no ${language}`)
      assert.ok(existsSync(resolve(dir, ministry[language].file)), ministry[language].file)
    }
  }
})

test('each file is one SVG with the size the catalogue claims', { skip: missing }, () => {
  for (const ministry of catalogue.ministries.slice(0, 5)) {
    for (const language of ['en', 'fr']) {
      const svg = read(ministry[language].file)
      assert.equal((svg.match(/<svg/g) || []).length, 1, ministry.code)
      assert.ok(
        svg.includes(`viewBox="0 0 ${ministry[language].width} ${ministry[language].height}"`),
        `${ministry.code}/${language}: viewBox disagrees with the catalogue`
      )
    }
  }
})

test('every shape is labelled, so the colourways can be applied', { skip: missing }, () => {
  const svg = read(catalogue.ministries[0].en.file)
  const roles = new Set([...svg.matchAll(/data-role="(\w+)"/g)].map(([, role]) => role))

  for (const role of ['sun', 'mountains', 'knockout', 'wordmark', 'divider', 'name']) {
    assert.ok(roles.has(role), `nothing is labelled ${role}`)
  }
})

test('the mountains and the wordmark were told apart', { skip: missing }, () => {
  // Both are the same blue in the source. If the split went wrong, one of these would be empty and
  // the reverse colourway would silently come out as a single flat colour.
  const svg = read(catalogue.ministries[0].en.file)

  assert.ok((svg.match(/data-role="mountains"/g) || []).length >= 1)
  assert.ok((svg.match(/data-role="wordmark"/g) || []).length > 5, 'the wordmark is many letters')
})

test('the files carry the screen colours, and record the print ones', { skip: missing }, () => {
  const svg = read(catalogue.ministries[0].en.file)
  const fills = new Set([...svg.matchAll(/fill="(#[0-9a-f]{6})"/g)].map(([, fill]) => fill))

  assert.ok(fills.has(catalogue.colours.screen.blue), 'screen blue')
  assert.ok(fills.has(catalogue.colours.screen.gold), 'screen gold')
  assert.ok(!fills.has(catalogue.colours.print.blue), 'the print blue should have been converted')
  assert.equal(catalogue.colours.print.blue, '#053673')
})

test('nothing is typeset — the wording is drawn', { skip: missing }, () => {
  // The whole basis of this era: the names are outlines, so the serif they are set in is never
  // needed and the marks are used exactly as published.
  for (const ministry of catalogue.ministries.slice(0, 5)) {
    const svg = read(ministry.en.file)
    assert.ok(!svg.includes('<text'), `${ministry.code} contains live text`)
    assert.ok(!svg.includes('font-family'), `${ministry.code} refers to a font`)
  }
})
