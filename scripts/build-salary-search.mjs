// Build a small discovery directory from the published salary records and reviewed name links.
// No source reports are reimported and no identity decisions are made here. The browser fetches
// one token bucket, filters/paginates its names, then loads the original rows for visible cards.
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gunzipSync, gzipSync } from 'node:zlib'
import { linkLookup } from '../src/salaries/nameLinks.js'
import { createNameSearchDocuments, nameSearchTokens } from '../src/salaries/nameSearch.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const readGzip = (bytes) => JSON.parse(gunzipSync(bytes).toString('utf8'))
const packed = (value) => gzipSync(JSON.stringify(value), { level: 9, mtime: 0 })

/** Exported for a small real-file build test; the production inputs remain the published exports. */
export const buildSalarySearch = ({ salaries = join(root, 'public/salaries'), out = join(salaries, 'search') } = {}) => {
  const sourceHash = createHash('sha256')
  const input = (path) => {
    const bytes = readFileSync(join(salaries, path))
    sourceHash.update(path).update('\0').update(bytes)
    return bytes
  }
  const index = JSON.parse(input('people/index.json').toString('utf8'))
  const rows = []
  for (const shard of Object.keys(index.shards).sort()) {
    const list = readGzip(input(`people/${shard}.json.gzip`))
    if (!Array.isArray(list) || list.length !== index.shards[shard]) throw new Error(`People shard ${shard} does not match the published index`)
    for (const row of list) rows.push(row)
  }
  // Every cross-surname alias file contains the same employer-scoped link. Merging lookups is
  // intentional and does not create new joins. Missing link directories fail the build.
  const links = new Map()
  for (const file of readdirSync(join(salaries, 'links')).filter((name) => /^[a-z_]{2}\.json\.gzip$/.test(name)).sort()) {
    for (const [key, link] of linkLookup(readGzip(input(`links/${file}`)), index.employers)) links.set(key, link)
  }
  const documents = createNameSearchDocuments(rows, index, links)
  const buckets = new Map()
  for (const document of documents) {
    const prefixes = new Set(document[4].flatMap(nameSearchTokens).filter((token) => token.length >= 2).map((token) => token.slice(0, 2)))
    for (const prefix of prefixes) {
      if (!/^[a-z0-9]{2}$/.test(prefix)) throw new Error(`Unsafe search bucket: ${prefix}`)
      if (!buckets.has(prefix)) buckets.set(prefix, [])
      buckets.get(prefix).push(document)
    }
  }
  mkdirSync(dirname(out), { recursive: true })
  const stage = mkdtempSync(join(dirname(out), '.name-search-'))
  const manifest = {
    schemaVersion: 1,
    note: 'Search discovery only. Documents: [name key, display spelling, employer index, reporting-period indexes, searchable spellings, original record shards]. Names are not personal identifiers. Cards and detail pages use the original records and existing employer-scoped name links.',
    sourceSha256: sourceHash.digest('hex'),
    context: { years: index.years, employers: index.employers.map((employer) => employer[3]) },
    records: rows.length,
    documents: documents.length,
    names: new Set(documents.map((document) => document[0])).size,
    buckets: {}
  }
  try {
    for (const [prefix, list] of [...buckets].sort(([a], [b]) => a.localeCompare(b))) {
      const bytes = packed(list)
      // Content-addressed buckets prevent a cached manifest from reading a different build's
      // bucket. Failed requests remain retryable through the shared salary loader.
      const hash = createHash('sha256').update(bytes).digest('hex').slice(0, 16)
      const file = `${prefix}-${hash}.json.gzip`
      writeFileSync(join(stage, file), bytes)
      manifest.buckets[prefix] = { file, documents: list.length, bytes: bytes.length }
    }
    writeFileSync(join(stage, 'index.json'), `${JSON.stringify(manifest)}\n`)
    const backup = `${out}.previous-build`
    if (existsSync(backup)) throw new Error(`Inspect the previous search build before replacing it: ${backup}`)
    const hadOutput = existsSync(out)
    if (hadOutput) renameSync(out, backup)
    try { renameSync(stage, out) } catch (error) {
      if (hadOutput) renameSync(backup, out)
      throw error
    }
    rmSync(backup, { recursive: true, force: true })
    return manifest
  } finally {
    rmSync(stage, { recursive: true, force: true })
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2)
  const option = (flag) => args.includes(flag) ? args[args.indexOf(flag) + 1] : undefined
  const salaries = resolve(option('--salaries') ?? join(root, 'public/salaries'))
  const manifest = buildSalarySearch({ salaries, out: resolve(option('--out') ?? join(salaries, 'search')) })
  const sizes = Object.values(manifest.buckets).map((bucket) => bucket.bytes)
  console.log(`Name search: ${manifest.names.toLocaleString('en-CA')} names, ${manifest.documents.toLocaleString('en-CA')} employer-name entries, ${sizes.length} buckets; ${(sizes.reduce((sum, bytes) => sum + bytes, 0) / 1024 / 1024).toFixed(2)} MiB compressed; largest ${(Math.max(0, ...sizes) / 1024).toFixed(0)} KiB.`)
}
