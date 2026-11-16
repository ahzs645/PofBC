// Pack the two published salary indexes into the one file the browser loads (see
// src/salaries/browseIndex.js for what is packed and why). The published indexes stay untouched.
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { gzipSync } from 'node:zlib'
import { gzipContentMatches } from './lib/gzip-content.mjs'
import { BROWSE_INDEX_PATH, packBrowseIndex } from '../src/salaries/browseIndex.js'

const root = new URL('../public/', import.meta.url)
const read = (path) => readFileSync(new URL(path, root))
const peopleBytes = read('salaries/people/index.json')
const employersBytes = read('salaries/employers/index.json')
const payload = JSON.stringify(packBrowseIndex(JSON.parse(peopleBytes), JSON.parse(employersBytes))) + '\n'
const target = new URL(BROWSE_INDEX_PATH, root)
const current = existsSync(target) && gzipContentMatches(readFileSync(target), payload)
if (process.argv.includes('--check')) {
  if (!current) throw new Error('The packed salary index is stale; run npm run build:salary-browse-index')
} else if (!current) writeFileSync(target, gzipSync(payload, { level: 9, mtime: 0 }))
const packed = readFileSync(target).length
const mib = (bytes) => `${(bytes / 1048576).toFixed(2)} MiB`
console.log(`Salary browse index: ${mib(peopleBytes.length + employersBytes.length)} in two indexes → ${mib(payload.length)} packed, ${mib(packed)} compressed → ${fileURLToPath(target)}`)
