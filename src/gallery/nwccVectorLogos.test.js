import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import pack from './nwccVectorLogos.json' with { type: 'json' }
import provenance from '../../research/identity/nwcc-vector-2026-11-27/provenance.json' with { type: 'json' }
import { collectionById, findGalleryEntry } from './collections.js'
import { identitySubjectById } from './identityCoverage.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'

const root = new URL('../../', import.meta.url)
const assets = pack.additions['northwest-community-college']

test('Northwest Community College’s files are the supplied extractions, unchanged, as paths only', () => {
  const supplied = new Set(provenance.assets.map(({ svg_sha256: sha }) => sha))
  const sources = new Set(provenance.sources.map(({ sha256 }) => sha256))
  for (const asset of assets) {
    const data = readFileSync(new URL(`public/${asset.file}`, root))
    assert.equal(createHash('sha256').update(data).digest('hex'), asset.sha256, asset.id)
    assert.ok(supplied.has(asset.sha256), `${asset.id}: as supplied`)
    assert.ok(sources.has(asset.extraction.sourceSha256), `${asset.id}: source checksum recorded`)
    assert.doesNotMatch(data.toString('utf8'), /<(?:image|text|use|script|foreignObject)\b/, asset.id)
    assert.ok(COLLECTED_DISPLAY[asset.id], `${asset.id}: display copies`)
  }
  // The isolated Thunderbird is a crop of the lockup, not a mark any source shows alone.
  assert.ok(!assets.some(({ file }) => file.includes('thunderbird-colour')))
})

test('the college is the first era of Coast Mountain College’s line, and its logo opens in colour', () => {
  const line = collectionById('collected-coast-mountain-college')
  assert.deepEqual(line.eras.map(({ label }) => label), ['Northwest Community College', 'Coast Mountain College'])
  const logo = findGalleryEntry('nwcc-thunderbird-wordmark-white-2015')
  assert.equal(logo.asset.id, 'nwcc-thunderbird-wordmark-colour')
  assert.equal(logo.identity.provenance, 'extracted_from_official_vector')
  assert.equal(identitySubjectById('northwest-community-college').state, 'native-vector')
})
