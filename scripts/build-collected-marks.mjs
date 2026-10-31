// Build the small gallery index from the complete acquisition records.
// Assets are local source files, including raster specimens; no remote hotlink is needed.
//
// The acquisition inventory, vector search and historical follow-up registers feed it.
// They add original artwork to bodies and to the one-off programs on the gallery's timelines.
// Every file is checked against the checksum its record gives.
import { readFileSync, writeFileSync } from 'node:fs'
import { basename } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'

const root = new URL('../', import.meta.url)
const read = (path) => JSON.parse(readFileSync(new URL(path, root), 'utf8'))
const inventory = read('research/identity/collection-2026-10-22/inventory.json')
const register = read('research/identity/vector-search-2026-10-30/source-register.json')
const historical = read('research/identity/historical-vector-followup-2026-10-30/source-register.json')

const checked = (asset) => {
  if (!/^identity-collected\/[a-z0-9._/-]+$/i.test(asset.file) || asset.file.includes('..')) {
    throw new Error(`Invalid asset path: ${asset.file}`)
  }
  const data = readFileSync(new URL(`public/${asset.file}`, root))
  if (createHash('sha256').update(data).digest('hex') !== asset.sha256) {
    throw new Error(`Source checksum differs: ${asset.file}`)
  }
  if (asset.preview) {
    if (!/^identity-collected\/[a-z0-9._/-]+$/.test(asset.preview) || asset.preview.includes('..')) {
      throw new Error(`Invalid preview path: ${asset.preview}`)
    }
    const preview = readFileSync(new URL(`public/${asset.preview}`, root))
    if (asset.previewSha256 && createHash('sha256').update(preview).digest('hex') !== asset.previewSha256) {
      throw new Error(`Preview checksum differs: ${asset.preview}`)
    }
  }
  return asset
}

// The register's labels are its file names; these say what each file shows.
const LABELS = {
  'bccie-2022-source-vector': 'Full colour, 2022–2025 strategic plan',
  'bcfma-2021-source-vector': 'Teal emblem and wordmark, 2020/21 report',
  'bc-housing-corporate-component-source-vector': 'Emblem and wordmark',
  'bc-housing-research-centre-source-vector': 'Research Centre lockup',
  'bcib-2022-horizontal-reversed-source-vector': 'Full name, reversed, 2021/22 report',
  'bcib-2025-tagline-reversed-source-vector': '“Building Opportunity Here”, reversed, 2024/25 report',
  'columbia-power-2024-reversed-source-vector': 'Reversed, 2024 history book',
  'community-living-bc-2014-reversed-source-vector': 'Reversed, 2013/14 annual report',
  'community-living-bc-2023-colour-source-vector': 'Full colour, 2023 report',
  'infrastructure-bc-2026-colour-source-vector': 'Full colour, Spring 2026 brochure',
  'infrastructure-bc-2026-reversed-source-vector': 'Reversed, Spring 2026 brochure',
  'fnha-icon': 'Symbol',
  'fnha-logo-colour': 'Full colour',
  'fnha-logo-white': 'White lettering',
  'interior-health-blue-horizontal-source-extraction': 'Blue, horizontal, 2023 roadmap',
  'phsa-black-source-extraction': 'Black',
  'phsa-white-source-extraction': 'White',
  'bc-oil-gas-commission-2014': 'Full colour, 2014 report',
  'bc-transmission-2009': 'Short name, 2009 service plan',
  'partnerships-bc-2012': 'Full colour, 2012/13 report',
  'bc-public-service-where-ideas-work-2023-reverse': '“Where ideas work”, reversed, 2023 corporate plan',
  'canada-starts-here-2012': '“Canada Starts Here”, 2012',
  'canada-starts-here-bc-jobs-plan-2012': '“Canada Starts Here” with the BC Jobs Plan, 2012',
  BCID_StrongerBC_RGB_pos: 'Endorsed, full colour',
  BCID_StrongerBC_RGB_rev: 'Endorsed, full colour, reversed',
  BCID_StrongerBC_Solid_pos: 'Endorsed, solid colour',
  BCID_StrongerBC_Solid_rev: 'Endorsed, solid colour, reversed',
  StrongerBC_RGB_pos: 'Wordmark, full colour',
  StrongerBC_RGB_rev: 'Wordmark, full colour, reversed',
  StrongerBC_Solid_pos: 'Wordmark, solid colour',
  StrongerBC_Solid_rev: 'Wordmark, solid colour, reversed',
  'welcomebc-2016': 'The flat mark with a gold rule, 2016',
  'welcomebc-current': 'Endorsed, with a gold rule, current',
  'workbc-2016': 'The flat mark with a gold rule, 2016',
  'workbc-current': 'The flat mark with a grey rule, current'
}

/** A register entry as the inventory's asset record, so both read the same in the gallery. */
const fromRegister = (entry) => {
  if (!LABELS[entry.id]) throw new Error(`No label for ${entry.id}`)
  if (!entry.genuineVectorVerified || entry.validation?.embeddedImages || entry.validation?.textElements || entry.validation?.externalResources?.length) {
    throw new Error(`Not verified as pure vector: ${entry.id}`)
  }
  const original = entry.sourceBytesUnchanged
  return checked({
    id: `vector-${entry.id}`,
    label: `${entry.organization} — ${LABELS[entry.id]}`,
    file: `identity-collected/${entry.bodyId}/${basename(entry.file)}`,
    format: 'svg',
    isVector: true,
    supplied: false,
    reconstruction: false,
    publisher: entry.organization,
    sourcePage: entry.sourcePageUrl ?? entry.sourceUrl,
    sourceUrl: entry.sourceUrl,
    sourceLocator: entry.sourcePdfPage ? `PDF page ${entry.sourcePdfPage}` : entry.sourcePackageEntry ?? null,
    sourceFile: null,
    sourceDate: entry.sourceDate ?? null,
    dateNote: entry.dateMeaning ?? '',
    observedDate: entry.retrievedDate,
    evidenceType: original ? 'official-svg-download' : 'native-pdf-vector-extraction',
    notes: entry.notes,
    fidelityNote: original
      ? 'Published SVG retained byte for byte, checked for real geometry and no embedded images or text, and rendered. Its source is linked below.'
      : `${entry.provenance} ${entry.method ?? ''}`.trim(),
    sha256: entry.sha256,
    bytes: entry.bytes,
    darkBackground: Boolean(entry.darkBackgroundRecommended),
    ...(entry.timelineId ? { timelineEra: entry.timelineId } : {}),
    search: 'vector-search-2026-10-30'
  })
}

const additions = new Map()
for (const entry of register.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry))
}

// Historical specimens use inventory-shaped records; detailed extraction evidence stays in
// their source register rather than in the gallery bundle. They must name an inventory body.
const bodyIds = new Set(inventory.bodies.map((body) => body.id))
for (const { bodyId, verification, ...asset } of historical.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown historical body: ${bodyId}`)
  if (asset.isVector && (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0 || verification.externalResources?.length !== 0)) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  additions.get(bodyId).push(checked({ ...asset, search: 'historical-vector-followup-2026-10-30' }))
}
for (const bodyId of Object.keys(historical.bodyUpdates)) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown historical body update: ${bodyId}`)
}

const bodies = inventory.bodies.map((body) => {
  for (const asset of body.assets) checked(asset)
  const { queries, researchSources, ...display } = body
  const added = additions.get(body.id) ?? []
  additions.delete(body.id)
  return added.length ? {
    ...display,
    ...historical.bodyUpdates[body.id],
    status: 'asset-collected',
    assets: [...display.assets, ...added]
  } : display
})

// What is left belongs to the one-off programs, which are timelines rather than inventory bodies.
const specimens = [...additions].map(([program, assets]) => ({ program, assets }))

const seenIds = new Set()
const seenFiles = new Set()
for (const { assets } of [...bodies, ...specimens]) for (const asset of assets) {
  if (seenIds.has(asset.id) || seenFiles.has(asset.file)) throw new Error(`Duplicate collected asset: ${asset.id} (${asset.file})`)
  seenIds.add(asset.id)
  seenFiles.add(asset.file)
}

writeFileSync(new URL('src/gallery/collectedData.js', root),
  '// Generated by scripts/build-collected-marks.mjs from the source-linked acquisition inventory.\n' +
  '// Logo dates are recorded separately from organization dates.\n' +
  `export const COLLECTED_BODIES = ${JSON.stringify(bodies, null, 2)}\n` +
  '// Published vector specimens of the one-off programs, by the timeline each belongs to.\n' +
  `export const COLLECTED_SPECIMENS = ${JSON.stringify(specimens, null, 2)}\n`)
console.log(`Wrote ${bodies.length} research records, ${bodies.reduce((sum, body) => sum + body.assets.length, 0)} body assets and ${specimens.reduce((sum, each) => sum + each.assets.length, 0)} program specimens to ${fileURLToPath(new URL('src/gallery/collectedData.js', root))}`)
