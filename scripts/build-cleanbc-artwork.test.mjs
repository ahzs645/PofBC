import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import register from '../src/gallery/cleanbcSources.json' with { type: 'json' }
import { buildCleanbcArtwork } from './build-cleanbc-artwork.mjs'

test('the shared CleanBC artwork rebuilds every registered rendition in scope with its original bytes', (t) => {
  const destination = mkdtempSync(join(tmpdir(), 'pofbc-cleanbc-artwork-'))
  t.after(() => rmSync(destination, { recursive: true, force: true }))
  const expected = register.flatMap(({ id, versions }) => versions
    .filter(({ treatment }) => id.startsWith('better-buildings-') || (id === 'base-wordmark' && treatment === 'white'))
    .map(({ treatment, sha256 }) => [`${id}-${treatment}.svg`, sha256]))

  buildCleanbcArtwork(destination)
  assert.deepEqual(readdirSync(destination).sort(), expected.map(([file]) => file).sort())
  for (const [file, expectedHash] of expected) {
    const bytes = readFileSync(join(destination, file))
    assert.equal(createHash('sha256').update(bytes).digest('hex'), expectedHash, file)
  }
})
