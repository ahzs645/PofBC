import test from 'node:test'
import assert from 'node:assert/strict'
import { gzipSync } from 'node:zlib'
import { gzipContentMatches } from './lib/gzip-content.mjs'

test('equivalent compression encodings preserve exact employer-statistics payloads', () => {
  const payload = JSON.stringify({ values: Array.from({ length: 100 }, (_, n) => n), count: 100 }) + '\n'
  const low = gzipSync(payload, { level: 1 })
  const high = gzipSync(payload, { level: 9 })
  const otherPlatform = Buffer.from(high); otherPlatform[9] = 19
  for (const bytes of [low, high, otherPlatform]) assert.equal(gzipContentMatches(bytes, payload), true)
})

test('changed values, ordering, whitespace and corrupt compressed data fail closed', () => {
  const bytes = gzipSync('{"count":100,"value":1}\n')
  for (const text of ['{"count":101,"value":1}\n', '{"value":1,"count":100}\n', '{"count":100,"value":1}']) assert.equal(gzipContentMatches(bytes, text), false)
  assert.equal(gzipContentMatches(Buffer.from('invalid'), '{}'), false)
})
