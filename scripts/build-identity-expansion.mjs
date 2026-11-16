#!/usr/bin/env node
// Generate additive gallery metadata from the acquired-artwork manifest.
// This is deliberately offline: a source website changing cannot silently change the catalogue.
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { DOMParser } from '@xmldom/xmldom'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
// Each manifest generates its own module; IDs must stay unique across all of them.
const MANIFESTS = [
  { manifest: 'research/identity/coverage-expansion-2026-11-15/assets-manifest.json', output: 'src/gallery/expandedIdentityData.js', name: 'EXPANDED_IDENTITY_BODIES', dir: 'identity-expanded' },
  { manifest: 'research/identity/municipalities-2026-11-15/assets-manifest.json', output: 'src/gallery/municipalIdentityData.js', name: 'MUNICIPAL_IDENTITY_BODIES', dir: 'identity-municipal' }
]
const check = process.argv.includes('--check')
const seenBodies = new Set()
const seenAssets = new Set()
const checkedFiles = new Map()
let fileDir = ''

function assert(condition, message) {
  if (!condition) throw new Error(message)
}

function verifyFile(record) {
  assert(typeof record.file === 'string' && record.file.startsWith(`${fileDir}/`) && /^[a-z-]+\/[a-z0-9_./-]+$/.test(record.file) && !record.file.split('/').includes('..'), `Unsafe asset path: ${record.file}`)
  const data = fs.readFileSync(path.join(root, 'public', record.file))
  const hash = crypto.createHash('sha256').update(data).digest('hex')
  assert(data.length === record.bytes, `Byte count changed: ${record.file}`)
  assert(hash === record.sha256, `SHA-256 changed: ${record.file}`)
  checkedFiles.set(record.file, hash)
  return data
}

function verifySvg(data, asset) {
  const svg = data.toString('utf8')
  const document = new DOMParser({ onError: (level, message) => { throw new Error(`${asset.file}: ${level}: ${message}`) } }).parseFromString(svg, 'image/svg+xml')
  assert(document.documentElement.localName === 'svg' && document.documentElement.namespaceURI === 'http://www.w3.org/2000/svg', `Invalid SVG root: ${asset.file}`)
  const ids = new Map()
  for (const element of Array.from(document.getElementsByTagName('*'))) {
    const id = element.getAttribute('id')
    if (!id) continue
    // Preserve harmless source-authored duplicate IDs on unreferenced paths.
    // Referenced definitions must still resolve to one unambiguous element.
    ids.set(id, (ids.get(id) ?? 0) + 1)
  }
  assert(/<svg\b[^>]*xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(svg), `Missing SVG namespace: ${asset.file}`)
  assert(/\bviewBox="\s*[-.\d]+[ ,]+[-.\d]+[ ,]+[.\d]+[ ,]+[.\d]+\s*"/.test(svg) || (/\bwidth=/.test(svg) && /\bheight=/.test(svg)), `Missing SVG dimensions: ${asset.file}`)
  assert(!/<(?:script|foreignObject|iframe|object|embed)\b/i.test(svg), `Active SVG content: ${asset.file}`)
  assert(!/\son\w+\s*=/.test(svg), `SVG event attribute: ${asset.file}`)
  assert(!/<!ENTITY\b/i.test(svg), `SVG entity declaration: ${asset.file}`)
  for (const [, ref] of svg.matchAll(/(?:xlink:)?href\s*=\s*["']([^"']+)["']/g)) {
    assert(ref.startsWith('#'), `External or embedded SVG reference in ${asset.file}: ${ref.slice(0, 80)}`)
    assert(ids.get(ref.slice(1)) === 1, `Unresolved or ambiguous SVG reference ${ref}: ${asset.file}`)
  }
  for (const [, ref] of svg.matchAll(/url\(\s*["']?([^)'"\s]+)/g)) {
    assert(ref.startsWith('#'), `External SVG CSS URL: ${asset.file}`)
    assert(ids.get(ref.slice(1)) === 1, `Unresolved or ambiguous SVG definition ${ref}: ${asset.file}`)
  }
  assert(!/@import\b|javascript\s*:/i.test(svg), `External or active SVG style: ${asset.file}`)
  assert(!/<image\b/i.test(svg), `Raster content cannot be marked as native vector: ${asset.file}`)
  assert(!/<text\b/i.test(svg), `Font-dependent text in acquired logo: ${asset.file}`)
  assert(/<(?:path|polygon|polyline|circle|ellipse|rect|use)\b/i.test(svg), `Empty SVG: ${asset.file}`)
}

// The 16 November vector searches propose SVGs for logos held only as website images: vector paths
// taken from the body's own PDFs, or, where none was found, a reconstruction that says so. Their
// source PDFs are not archived here; each package's source register keeps the URL and checksum.
const VECTOR_SEARCHES = ['health-bodies-vector-2026-11-16', 'municipal-logos-vector-2026-11-16']
// Finds that are another lockup or version of the logo than the website image: they sit beside
// it, rather than taking it as one of their versions.
const OTHER_DESIGN = new Set([
  'bcehs-2024-progress-report-endorsed', // with the PHSA line and a larger name
  'municipal-fort-st-john-ocp-2025-stacked', // stacked; the website image is horizontal
  'municipal-prince-george-annual-report-2025-horizontal', // horizontal; the website image is stacked
  'municipal-prince-rupert-community-assessment-2024', // the full logo with the arch
  'municipal-smithers-new-residents-guide-2026', // stacked with a slate name, no tagline
  'municipal-smithers-new-residents-guide-2026-tagline-white' // horizontal, with the tagline
])

function mergeSearches(manifest, output) {
  for (const search of VECTOR_SEARCHES) {
    const proposals = JSON.parse(fs.readFileSync(path.join(root, 'research/identity', search, 'proposed-assets.json'), 'utf8'))
    for (const { dataFile, bodyId, targetAssetId, asset } of proposals) {
      if (dataFile !== path.basename(output)) continue
      const body = manifest.bodies.find((each) => each.id === bodyId)
      assert(body, `Unknown body for ${asset.id}: ${bodyId}`)
      assert(asset.search === search && asset.format === 'svg' && asset.isVector, `Unexpected record: ${asset.id}`)
      body.assets.push(asset)
      // The website image it stands for becomes one of its versions, so the vector leads the card.
      const target = body.assets.find((each) => each.id === targetAssetId)
      if (!target || target.variantOf || OTHER_DESIGN.has(asset.id)) continue
      const keeper = asset.variantOf ?? asset.id
      for (const each of body.assets) if (each.variantOf === target.id) each.variantOf = keeper
      target.variantOf = keeper
      target.versionLabel ??= 'Published image'
      const lead = body.assets.find((each) => each.id === keeper)
      lead.versionLabel ??= lead.reconstruction ? 'Vector reconstruction' : 'Vector'
    }
  }
}

for (const { manifest: manifestFile, output, name, dir } of MANIFESTS) {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, manifestFile), 'utf8'))
  const outputPath = path.join(root, output)
  fileDir = dir
  assert(manifest.schemaVersion === 1, 'Unsupported identity acquisition manifest')
  mergeSearches(manifest, output)
  for (const source of manifest.sources ?? []) verifyFile(source)
  for (const body of manifest.bodies) {
    assert(!seenBodies.has(body.id), `Duplicate body ID: ${body.id}`)
    seenBodies.add(body.id)
    assert(body.assets.length > 0 && body.status === 'asset-collected', `Empty collected body: ${body.id}`)
    assert(Object.hasOwn(body, 'graphNode'), `graphNode must be explicit, including null: ${body.id}`)
    for (const asset of body.assets) {
      assert(!seenAssets.has(asset.id), `Duplicate asset ID: ${asset.id}`)
      seenAssets.add(asset.id)
      assert(asset.sourceUrl?.startsWith('https://') && asset.sourcePage?.startsWith('https://'), `Source attribution missing: ${asset.id}`)
      assert(asset.publisher && asset.sourceLocator && asset.fidelityNote && asset.observedDate, `Incomplete evidence: ${asset.id}`)
      // A vector search may add a reconstruction, which must say so; nothing else is rebuilt.
      assert(asset.supplied === false && (asset.reconstruction === false || (asset.search && asset.evidenceType === 'vector-reconstruction')), `Unexpected artwork category: ${asset.id}`)
      assert(asset.isVector === (asset.format === 'svg'), `Inconsistent vector label: ${asset.id}`)
      const data = verifyFile(asset)
      assert(asset.search || checkedFiles.has(asset.sourceFile), `Archived source is missing from the manifest: ${asset.id}`)
      if (asset.format === 'svg') verifySvg(data, asset)
      if (asset.format === 'png') assert(data.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), `Invalid PNG: ${asset.file}`)
      if (asset.format === 'webp') assert(data.toString('ascii', 0, 4) === 'RIFF' && data.toString('ascii', 8, 12) === 'WEBP', `Invalid WebP: ${asset.file}`)
      for (const download of asset.downloads ?? []) verifyFile(download)
      // A resized copy for the page; the archived file stays the evidence.
      if (asset.preview) {
        const preview = verifyFile({ file: asset.preview, sha256: asset.previewSha256, bytes: asset.previewBytes })
        assert(asset.format === 'png' && preview.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])) && asset.previewNote, `Invalid preview: ${asset.id}`)
      }
    }
  }

  const source = '// Generated by scripts/build-identity-expansion.mjs from assets-manifest.json.\n'
    + '// Artwork observation dates and publication dates are not inferred logo adoption dates.\n'
    + `export const ${name} = ${JSON.stringify(manifest.bodies, null, 2)}\n`
  if (check) {
    assert(fs.existsSync(outputPath) && fs.readFileSync(outputPath, 'utf8') === source, `${output} is stale; run node scripts/build-identity-expansion.mjs`)
  } else {
    fs.writeFileSync(outputPath, source)
  }
}

console.log(`${check ? 'Verified' : 'Generated'} ${seenBodies.size} identity bodies / ${seenAssets.size} source-linked artworks; verified ${checkedFiles.size} files.`)
