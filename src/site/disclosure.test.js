import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

// The site has one fold (Disclosure.jsx) and one style for it (site.css). A raw <details> or a
// stylesheet of its own for a summary brings back the browser's triangle and a look of its own.

const SRC = fileURLToPath(new URL('..', import.meta.url))
const files = (extension) => readdirSync(SRC, { recursive: true })
  .filter((file) => file.endsWith(extension))
  .map((file) => join(SRC, file))
const at = (file) => relative(SRC, file)

// The posters' record cards are a card that opens in place, marked "+" beside its sibling links'
// "→" and "↗", not a fold of text; they keep their own element.
const OWN_DETAILS = new Set(['site/Disclosure.jsx', 'posters/ui/Connections.jsx'])
const OWN_SUMMARY_STYLE = new Set(['posters/posters.css'])

test('every fold goes through Disclosure', () => {
  const raw = files('.jsx').filter((file) => !OWN_DETAILS.has(at(file)) && /<details\b|<summary\b/.test(readFileSync(file, 'utf8')))
  assert.deepEqual(raw.map(at), [])
})

test('no stylesheet styles a summary of its own', () => {
  const styled = files('.css').filter((file) => {
    if (OWN_SUMMARY_STYLE.has(at(file))) return false
    // A selector that names the element (summary, details) rather than the shared classes.
    const css = readFileSync(file, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '')
    return /(^|[\s,>+~(])(summary|details)(?=[\s,.:[>{)])/m.test(css)
  })
  assert.deepEqual(styled.map(at), [])
})

test('a summary never holds a heading', () => {
  const headed = files('.jsx').filter((file) => /<Disclosure\b[^>]*summary=\{?\s*<h[1-6]/.test(readFileSync(file, 'utf8')))
  assert.deepEqual(headed.map(at), [])
})
