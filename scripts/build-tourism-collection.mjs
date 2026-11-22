import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const ROOT = fileURLToPath(new URL('../', import.meta.url))
const FOLDER = 'research/identity/tourism-asset-transfer-2013'
const OUTPUT = 'src/gallery/tourismData.js'
const SOURCE_ARRAYS = ['digitalRecords', 'marks', 'timeline', 'publications', 'leads']
const REQUIRED_DIGITAL = ['hellobc', 'worldhost', 'near-me-bc', 'bc-escapes', 'bc-magazine', 'share-your-bc']
const readJson = (root, file) => JSON.parse(readFileSync(resolve(root, file), 'utf8'))
const fail = (message) => { throw new Error(`Tourism collection: ${message}`) }
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex')

/** Source IDs, source positions and original repeated entries remain inspectable. */
export const validateTourismData = (catalogue, register, domainDocument) => {
  const sourceIds = new Set()
  for (const source of register.sources ?? []) {
    if (!source.id || sourceIds.has(source.id)) fail(`duplicate or absent source id: ${source.id}`)
    if (!/^https:\/\//.test(source.url ?? '')) fail(`source URL missing: ${source.id}`)
    sourceIds.add(source.id)
  }
  const itemIds = new Set()
  for (const key of SOURCE_ARRAYS) {
    if (!Array.isArray(catalogue[key])) fail(`missing array: ${key}`)
    for (const item of catalogue[key]) {
      if (!item.id || itemIds.has(item.id)) fail(`duplicate or absent item id: ${item.id}`)
      itemIds.add(item.id)
      if (!item.title || !item.description) fail(`incomplete item: ${item.id}`)
      if (!item.sourceRefs?.length) fail(`item has no source: ${item.id}`)
      for (const source of item.sourceRefs) {
        if (!sourceIds.has(source.sourceId)) fail(`unknown source ${source.sourceId} on ${item.id}`)
        if (source.page != null && (!Number.isInteger(source.page) || source.page < 1)) fail(`invalid page on ${item.id}`)
        if (source.sourceId === 'mo-68-2013' && source.page > 89) fail(`order page out of range on ${item.id}`)
      }
      for (const link of item.links ?? []) {
        if (!/^https:\/\//.test(link.url ?? '') && !/^\?view=/.test(link.url ?? '')) fail(`invalid link on ${item.id}`)
      }
    }
  }
  for (const id of REQUIRED_DIGITAL) {
    if (!catalogue.digitalRecords.some((record) => record.id === id)) fail(`required digital record missing: ${id}`)
  }
  const rows = domainDocument.records
  if (!Array.isArray(rows) || rows.length !== 193) fail('Appendix 5 must preserve all 193 listed entries')
  const ids = new Set()
  const seenValues = new Map()
  const counts = new Map()
  for (const row of rows) {
    if (ids.has(row.id)) fail(`duplicate inventory id: ${row.id}`)
    ids.add(row.id)
    if (row.sourceId !== 'mo-68-2013' || ![83, 84].includes(row.page)) fail(`invalid inventory source: ${row.id}`)
    if (![1, 2, 3].includes(row.column) || !Number.isInteger(row.row) || row.row < 1) fail(`invalid cell position: ${row.id}`)
    if (row.id !== `p${row.page}-c${row.column}-r${String(row.row).padStart(2, '0')}`) fail(`cell id and position disagree: ${row.id}`)
    if (row.value !== row.printedValue?.toLowerCase() || /\s/.test(row.value)) fail(`value differs from transcription: ${row.id}`)
    if (!['domain', 'subdomain', 'email'].includes(row.kind)) fail(`unknown address kind: ${row.id}`)
    if ((row.kind === 'email') !== row.value.includes('@')) fail(`email classified as website: ${row.id}`)
    if (row.status !== 'source-listed' || row.url || row.href || row.active === true) fail(`inventory claims a live address: ${row.id}`)
    if (!Object.hasOwn(catalogue.domainFamilies, row.family)) fail(`unknown address family: ${row.family}`)
    if (seenValues.has(row.value)) {
      if (row.duplicateOf !== seenValues.get(row.value)) fail(`repeat is not linked to its first entry: ${row.id}`)
    } else {
      if (row.duplicateOf) fail(`first entry incorrectly marked duplicate: ${row.id}`)
      seenValues.set(row.value, row.id)
    }
    const column = `${row.page}-${row.column}`
    counts.set(column, (counts.get(column) ?? 0) + 1)
  }
  for (const [column, expected] of [['83-1', 38], ['83-2', 38], ['83-3', 38], ['84-1', 28], ['84-2', 28], ['84-3', 23]]) {
    if (counts.get(column) !== expected) fail(`source column ${column} should contain ${expected} entries`)
  }
  if (seenValues.size !== 191 || rows.filter((row) => row.kind === 'email').length !== 7) fail('source inventory totals changed')
  const timeline = new Map(catalogue.timeline.map((event) => [event.id, event]))
  if (timeline.get('tourism-bc-dissolved')?.date !== '2010-04-01') fail('Tourism BC dissolution must remain separate')
  if (timeline.get('destination-bc-established')?.date !== '2012-11-02') fail('Destination BC establishment must remain separate')
  if (timeline.get('destination-bc-operations')?.date !== '2013-04-01') fail('Destination BC operations must remain separate')
  return true
}

const manifestAssets = (root) => {
  const assets = new Map()
  for (const name of ['artwork-manifest.json', 'website-manifest.json']) {
    const file = `${FOLDER}/${name}`
    if (!existsSync(resolve(root, file))) continue
    const manifest = readJson(root, file)
    for (const asset of manifest.assets ?? []) {
      const id = asset.id ?? asset.assetId
      if (!id || assets.has(id)) fail(`duplicate or absent manifest asset: ${id}`)
      assets.set(id, { ...asset, manifest: file })
    }
  }
  return assets
}

const imageOf = (root, asset, sources) => {
  const file = (asset.path ?? asset.file ?? (asset.filename ? `tourism/websites/${asset.filename}` : '')).replace(/^public\//, '')
  if (!/^tourism\/(?:marks|websites)\/[a-zA-Z0-9._/-]+$/.test(file) || file.includes('..')) fail(`invalid asset path: ${file}`)
  const disk = resolve(root, 'public', file)
  if (!existsSync(disk)) fail(`missing image file: ${file}`)
  const bytes = readFileSync(disk)
  if (!asset.sha256 || hash(bytes) !== asset.sha256) fail(`image checksum mismatch: ${file}`)
  const source = sources.get(asset.sourceId)
  if (!source) fail(`unknown image source: ${asset.sourceId}`)
  const width = asset.width ?? asset.dimensions?.width ?? asset.dimensions?.[0]
  const height = asset.height ?? asset.dimensions?.height ?? asset.dimensions?.[1]
  if (!(width > 0 && height > 0)) fail(`missing image dimensions: ${file}`)
  const vector = asset.kind === 'source-vector-extraction' || file.endsWith('.svg')
  const evidenceType = asset.evidenceType ?? (vector ? 'native-pdf-vector-extraction'
    : asset.kind === 'source-crop' ? 'printed-source-crop'
      : asset.kind === 'source-image' ? 'official-published-raster'
        : asset.evidenceStatus ?? 'published-website-image')
  const sourceLabel = asset.kind === 'source-image' ? 'Gazette image'
    : asset.kind === 'source-crop' && /\/marks\//.test(file) ? 'Order scan' : null
  return {
    id: asset.id ?? asset.assetId,
    file,
    title: asset.title ?? asset.alt ?? source.title,
    label: asset.label ?? asset.variant ?? (sourceLabel ? `${asset.title} · ${sourceLabel}` : asset.title) ?? asset.sourceDate ?? source.date ?? 'Source image',
    alt: asset.alt ?? asset.title ?? source.title,
    width,
    height,
    caption: asset.caption ?? asset.note ?? (vector
      ? 'Native artwork extracted from the cited publication. Its publication date is not an adoption date.'
      : asset.kind === 'source-crop'
        ? 'Unretouched specimen from the 2013 order scan. This is source evidence, not reconstructed vector artwork.'
        : asset.kind === 'source-image'
          ? 'Original standalone image from the official Gazette, preserved unchanged. The corresponding order scan is separate evidence.'
          : 'An authentic website image reproduced in the cited publication; its date is the publication date.'),
    evidenceType,
    isVector: vector,
    format: asset.format ?? file.split('.').at(-1),
    date: asset.sourceDate ?? asset.date ?? source.date,
    dateLabel: asset.sourceDateMeaning ?? asset.dateMeaning ?? source.dateRole,
    sourceId: asset.sourceId,
    sourceUrl: asset.sourceUrl ?? source.url,
    ...(asset.sourceImageUrl ? { sourceImageUrl: asset.sourceImageUrl } : {}),
    sourcePage: asset.sourcePage ?? asset.pdfPage ?? null,
    sourceLocator: asset.sourceLocator ?? (asset.sourcePdfPage
      ? `Official Gazette image; corresponding order PDF page ${asset.sourcePdfPage}`
      : (asset.pdfPage ?? asset.sourcePage) ? `PDF page ${asset.pdfPage ?? asset.sourcePage}${asset.printedPage ? `; printed page ${asset.printedPage}` : ''}` : source.locator ?? ''),
    ...(asset.sourcePdfPage ? { sourcePdfPage: asset.sourcePdfPage } : {}),
    ...(asset.extractionNotes ? { extractionNotes: asset.extractionNotes } : {}),
    ...(asset.reference ? { reference: asset.reference } : {}),
    sha256: asset.sha256,
    manifest: asset.manifest,
    ...(asset.darkBackground || asset.displayBackground === 'dark' || /-reverse(?:-grayscale)?-2005$/.test(asset.id ?? '') ? { darkBackground: true } : {}),
  }
}

export const buildTourismCollection = (root = ROOT) => {
  const catalogue = readJson(root, `${FOLDER}/catalogue.json`)
  const register = readJson(root, `${FOLDER}/source-register.json`)
  const domainDocument = readJson(root, `${FOLDER}/domains.json`)
  validateTourismData(catalogue, register, domainDocument)
  const sources = new Map(register.sources.map((source) => [source.id, source]))
  const assets = manifestAssets(root)
  const usedAssets = new Set()
  const resolveItem = (item, kind) => {
    const { assetIds = [], ...record } = item
    const images = assetIds.map((id) => {
      if (!assets.has(id)) fail(`unresolved asset ${id} on ${item.id}`)
      usedAssets.add(id)
      return imageOf(root, assets.get(id), sources)
    })
    if (images.length) {
      record.images = images
      record.image = images[0]
      if (kind === 'marks') record.variants = images
      if (kind === 'marks' && record.kind !== 'word-mark') {
        record.artworkStatus = images.some((image) => image.isVector) ? 'native-vector-held' : 'source-specimen-held'
        record.status = images.some((image) => image.isVector) ? 'native-vector' : 'source-specimen'
        record.statusLabel = images.some((image) => image.isVector) ? 'Native vector from publication' : 'Printed source specimen'
      }
    }
    return record
  }
  const output = {
    ...catalogue,
    sources: register.sources,
    ...Object.fromEntries(SOURCE_ARRAYS.map((key) => [key, catalogue[key].map((item) => resolveItem(item, key))])),
    domains: domainDocument.records,
    domainMethod: domainDocument.method,
    domainCountMeaning: domainDocument.domainCountMeaning,
  }
  const images = [...usedAssets].map((id) => assets.get(id))
  output.stats = {
    digitalRecords: output.digitalRecords.length,
    marks: output.marks.length,
    timelineEvents: output.timeline.length,
    publications: output.publications.length,
    programAreas: output.leads.filter((lead) => lead.category === 'program area').length,
    sources: output.sources.length,
    listedAddresses: output.domains.length,
    distinctAddresses: new Set(output.domains.map((entry) => entry.value)).size,
    domainEntries: output.domains.filter((entry) => entry.kind === 'domain').length,
    subdomainEntries: output.domains.filter((entry) => entry.kind === 'subdomain').length,
    emailEntries: output.domains.filter((entry) => entry.kind === 'email').length,
    duplicateEntries: output.domains.filter((entry) => entry.duplicateOf).length,
    visualSpecimens: usedAssets.size,
    nativeVectors: images.filter((image) => image.kind === 'source-vector-extraction').length,
    sourceCrops: images.filter((image) => image.kind === 'source-crop' && /\/marks\//.test(image.path ?? image.file ?? '')).length,
    sourceImages: images.filter((image) => image.kind === 'source-image').length,
    websiteImages: output.digitalRecords.reduce((count, record) => count + (record.images?.length ?? 0), 0),
  }
  return output
}

export const renderTourismModule = (data) =>
  '// Generated by scripts/build-tourism-collection.mjs from the sourced tourism inventory.\n' +
  '// Website evidence, source-listed addresses, artwork and corporate dates remain separate.\n' +
  `export const TOURISM_COLLECTION = ${JSON.stringify(data, null, 2)}\n\n` +
  'export const TOURISM_DIGITAL_RECORDS = TOURISM_COLLECTION.digitalRecords\n' +
  'export const TOURISM_MARKS = TOURISM_COLLECTION.marks\n' +
  'export const TOURISM_DOMAINS = TOURISM_COLLECTION.domains\n'

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const args = process.argv.slice(2)
  if (args.some((arg) => arg !== '--check')) fail('only --check is supported')
  const data = buildTourismCollection()
  const text = renderTourismModule(data)
  const output = resolve(ROOT, OUTPUT)
  if (args.includes('--check')) {
    if (!existsSync(output) || readFileSync(output, 'utf8') !== text) fail(`generated data is stale; run node scripts/build-tourism-collection.mjs`)
    console.log(`Tourism collection verified: ${data.stats.digitalRecords} digital records, ${data.stats.marks} mark/name groups, ${data.stats.listedAddresses} listed addresses.`)
  } else {
    writeFileSync(output, text)
    console.log(`Wrote ${OUTPUT}: ${data.stats.digitalRecords} digital records, ${data.stats.marks} mark/name groups, ${data.stats.listedAddresses} listed addresses.`)
  }
}
