#!/usr/bin/env node
// Package the supplied IUS reconstruction without running its authoring scripts.
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { zipSync } from 'fflate'

const root = fileURLToPath(new URL('../', import.meta.url))
const publicDir = join(root, 'public/unbc-origins')
const researchDir = join(root, 'research/identity/unbc-origins')
const check = process.argv.includes('--check')
const jsonBytes = (value) => Buffer.from(`${JSON.stringify(value, null, 2)}\n`)
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex')
const supplied = JSON.parse(readFileSync(join(researchDir, 'supplied/asset-manifest.json'), 'utf8'))
const catalogue = JSON.parse(readFileSync(join(researchDir, 'assets.json'), 'utf8'))
const suppliedById = new Map(supplied.assets.map((asset) => [asset.id, asset]))

assert.equal(supplied.version, '1.2', 'Review the distribution when the supplied kit version changes')
assert.equal(supplied.assets.length, 26)
assert.equal(catalogue.length, 26)
assert.equal(new Set(catalogue.map((asset) => asset.id)).size, 26)

const files = new Map()
const add = (path, bytes) => {
  assert(!files.has(path), `Duplicate ZIP entry: ${path}`)
  assert(!path.startsWith('/') && !path.split('/').includes('..'), `Unsafe ZIP path: ${path}`)
  files.set(path, bytes)
}
const from = (path, diskPath) => add(path, readFileSync(diskPath))
const assets = catalogue.map((asset) => {
  const original = suppliedById.get(asset.id)
  assert(original, `Unknown asset: ${asset.id}`)
  const svg = `svg/${asset.id}.svg`
  const pdf = `pdf/${asset.id}.pdf`
  assert.equal(asset.svg, svg)
  assert.equal(asset.pdf, pdf)
  assert.equal(asset.svgSha256, original.sha256_svg)
  const [, , width, height] = original.viewBox.split(/\s+/).map(Number)
  assert.equal(asset.width, width)
  assert.equal(asset.height, height)
  const svgBytes = readFileSync(join(publicDir, svg))
  assert.equal(sha256(svgBytes), original.sha256_svg, `SVG differs from supplied master: ${asset.id}`)
  add(svg, svgBytes)
  from(pdf, join(publicDir, pdf))
  from(`eps/${asset.id}.eps`, join(researchDir, `eps/${asset.id}.eps`))
  return asset
})

const addDirectory = (directory, archivePrefix) => {
  for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)) {
    assert(entry.isFile(), `Only committed regular files are expected: ${join(directory, entry.name)}`)
    from(`${archivePrefix}/${entry.name}`, join(directory, entry.name))
  }
}
addDirectory(join(researchDir, 'source'), 'source')
addDirectory(join(researchDir, 'palette'), 'palette')
for (const name of ['ius-colours.json', 'ius-colours.css']) {
  assert(readFileSync(join(publicDir, 'palette', name)).equals(files.get(`palette/${name}`)), `Public palette drift: ${name}`)
}
from('README.md', join(publicDir, 'README.md'))
assert(readFileSync(join(publicDir, 'SUPPLIED_README.md')).equals(readFileSync(join(researchDir, 'supplied/README.md'))), 'Supplied README drift')
from('SUPPLIED_README.md', join(publicDir, 'SUPPLIED_README.md'))
for (const name of ['FONT_NOTES.md', 'asset-manifest.json', 'vector-validation.json', 'font-audit.json']) {
  from(name, join(researchDir, 'supplied', name))
}
for (const name of ['source-audit.md', 'source-inventory.json']) {
  from(`evidence/${name}`, join(researchDir, 'supplied', name))
}
from('evidence/import-provenance.json', join(researchDir, 'provenance.json'))
add('assets.json', jsonBytes(assets))

const sortedFiles = () => [...files].sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0)
const manifest = {
  title: 'Interior University Society — public vector collection',
  version: '1.2',
  distribution: 'Compact public subset of the user-supplied kit; original photographs and raster references excluded.',
  assetCount: assets.length,
  formats: ['svg', 'pdf', 'eps'],
  fileRoot: 'IUS_Vector_Brand_Kit_Public',
  files: sortedFiles().map(([path, bytes]) => ({ path, bytes: bytes.length, sha256: sha256(bytes) })),
  checksumScope: 'All payload files are listed. The embedded manifest excludes itself to avoid a circular hash.',
}
add('manifest.json', jsonBytes(manifest))
// fflate writes local date parts. A fixed local date keeps ZIP timestamps stable
// across machine timezones without relying on wall-clock time or file mtimes.
const zipEntries = Object.fromEntries(sortedFiles().map(([path, bytes]) => [
  `${manifest.fileRoot}/${path}`,
  [new Uint8Array(bytes), { mtime: new Date(2000, 0, 1, 0, 0, 0), level: 9 }],
]))
const zipBytes = Buffer.from(zipSync(zipEntries, { level: 9 }))
const archiveName = 'ius-vector-brand-kit-v1.2.zip'
const publicManifest = {
  ...manifest,
  archive: { path: archiveName, bytes: zipBytes.length, sha256: sha256(zipBytes) },
}
const outputs = new Map([
  ['assets.json', jsonBytes(assets)],
  ['FONT_NOTES.md', readFileSync(join(researchDir, 'supplied/FONT_NOTES.md'))],
  ['manifest.json', jsonBytes(publicManifest)],
  [archiveName, zipBytes],
])
for (const [name, bytes] of outputs) {
  const destination = join(publicDir, name)
  if (check) {
    assert(existsSync(destination), `Missing generated file: ${relative(root, destination).split(sep).join('/')}`)
    assert(readFileSync(destination).equals(bytes), `Generated file is stale: ${name}`)
  } else {
    writeFileSync(destination, bytes)
  }
}
console.log(`IUS public collection: ${assets.length} SVG/PDF/EPS sets, ${files.size} ZIP entries, ${zipBytes.length.toLocaleString('en-CA')} bytes; ${check ? 'reproducible outputs verified' : 'outputs written'}.`)
