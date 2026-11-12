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
const ticorp = read('research/identity/ticorp-vector-2026-11-08/source-register.json')
const followup = read('research/identity/vector-followup-2026-11-08/source-register.json')
const historical = read('research/identity/historical-vector-followup-2026-10-30/source-register.json')
const innovate = read('research/identity/innovate-bc-vector-2026-11-12/source-register.json')
const bcAssessment = read('research/identity/bc-assessment-vector-2026-11-12/source-register.json')
const bcPowerCommission = read('research/identity/bc-power-commission-vector-2026-11-12/source-register.json')

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
  'ticorp-2025-colour-source-vector': 'Full colour, Summer 2025 project update',
  'ticorp-2020-reversed-source-vector': 'White, Spring 2020 project overview',
  'pavco-2025-26-colour-source-vector': 'Full colour, FY2025/26 year in review',
  'pavco-2023-reversed-source-vector': 'White, 2023–2026 accessibility plan',
  'forest-renewal-bc-2000-colour-source-vector': 'Full colour, December 2000 funded-project report',
  'forest-renewal-bc-1999-black-source-vector': 'Black, March 1999 woodlot inventory manual',
  'worksafe-2003-serif-source-vector': 'Distressed WorkSafe wordmark and board name, 2003 annual report',
  'worksafebc-2004-tagline-source-vector': 'Black and orange with tagline, 2004 annual report',
  'worksafebc-2024-colour-source-vector': 'Black and orange, 2024 annual report',
  'bclc-2009-colour-tagline-source-vector': 'Older palette with tagline, 2009 service plan update',
  'bclc-2009-reversed-source-vector': 'White with coloured dots, 2009 service plan update',
  'bclc-2011-reversed-tagline-source-vector': 'White with coloured dots and tagline, 2010/11 annual report',
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

// Files dropped because the same design is held as vector artwork (colour aside: a body's colours
// are its standard ones, so a recoloured copy is not another design). The gallery keeps the vector;
// the dropped file's source stays recorded in its acquisition record, and its date, if it has one,
// is kept on the vector as a further sighting.
const SUPERSEDED = {
  'source-transportation-investment-corporation-transportation-investment-corporation-png': 'vector-ticorp-2025-colour-source-vector',
  'source-bc-housing-bc-housing-png': 'vector-bc-housing-corporate-component-source-vector',
  'source-bc-assessment-bc-assessment-jpg': 'bc-assessment-svg',
  // The official EPS stays as the SVG's original download.
  'source-bc-assessment-bc-assessment-eps': 'bc-assessment-svg',
  'source-columbia-power-columbia-power-png': 'vector-columbia-power-2024-reversed-source-vector',
  'source-infrastructure-bc-infrastructure-bc-png': 'vector-infrastructure-bc-2026-colour-source-vector',
  'source-community-living-bc-community-living-bc-png': 'vector-community-living-bc-2023-colour-source-vector',
  'source-knowledge-network-knowledge-network-colour-png': 'source-knowledge-network-knowledge-network-colour-eps',
  'source-bc-pavilion-corporation-pavco-png': 'vector-pavco-2025-26-colour-source-vector',
  'source-forest-enhancement-society-fesbc-horizontal-png': 'source-forest-enhancement-society-fesbc-horizontal-eps',
  'source-forest-enhancement-society-fesbc-vertical-png': 'source-forest-enhancement-society-fesbc-vertical-eps',
  'source-innovate-bc-innovate-bc-teal-png': 'innovate-bc-2024-colour',
  // The wordmark alone, twice; the logo's vector carries it.
  'source-innovate-bc-innovate-bc-logo-png': 'innovate-bc-2024-colour',
  'source-innovate-bc-innovate-bc-wordmark-png': 'innovate-bc-2024-colour',
  'source-bc-family-maintenance-agency-bc-family-maintenance-agency-png': 'vector-bcfma-2021-source-vector',
  'source-inbc-inbc-print-png': 'source-inbc-inbc-svg',
  'source-bc-council-for-international-education-bccie-png': 'vector-bccie-2022-source-vector',
  'source-interior-health-interior-health-png': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-interior-health-interior-health-white-png': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-interior-health-interior-health-horizontal-jpg': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-interior-health-interior-health-2004-letterhead-png': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-provincial-health-services-authority-phsa-png': 'vector-phsa-black-source-extraction',
  'source-bc-heritage-trust-bc-heritage-trust-1989-logo-png': 'historical-bc-heritage-trust-2002',
  'source-forest-renewal-bc-forest-renewal-bc-1999-original-png': 'vector-forest-renewal-bc-1999-black-source-vector',
  // A third-party vector of the design the Corporation's own reports give as original paths.
  'source-forest-renewal-bc-forest-renewal-bc-supplied-vector-svg': 'vector-forest-renewal-bc-2000-colour-source-vector',
  'source-oil-and-gas-commission-bc-oil-gas-commission-2021-jpeg': 'vector-bc-oil-gas-commission-2014',
  'source-oil-and-gas-commission-bc-oil-gas-commission-2019-jpeg': 'vector-bc-oil-gas-commission-2014',
  'source-partnerships-bc-partnerships-bc-2006-logo-crop-png': 'vector-partnerships-bc-2012',
  'source-pacific-carbon-trust-pacific-carbon-trust-2013-png': 'source-pacific-carbon-trust-pacific-carbon-trust-2013-svg',
  'source-capital-health-region-capital-health-region-2000-letterhead-png': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-2000-original-colour': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-2000-original-greyscale': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-1999-january-newspaper-raster': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-1999-october-letterhead-raster': 'historical-capital-health-region-2000-dark-grey',
  'source-central-vancouver-island-health-region-central-vancouver-island-health-region-1999-png': 'source-central-vancouver-island-health-region-central-vancouver-island-health-region-1999-svg',
  // The hybrid SVG wraps the same low-resolution wordmark as the complete image, which is kept.
  'source-north-okanagan-health-region-north-okanagan-health-region-2000-hybrid-svg': 'source-north-okanagan-health-region-north-okanagan-health-region-2000-png',
  'source-northern-interior-regional-health-board-northern-interior-regional-health-board-2001-png': 'historical-northern-interior-regional-health-board-blue-2001',
  // The reconstruction keeps the Power Pioneers image as its source download.
  'source-bc-power-commission-bc-power-commission-original-logo-jpg': 'bc-power-commission-rebuilt'
}

// Another colourway of the same design: shown inside the design's entry as a version to switch
// to, rather than as a separate mark.
const VARIANT_OF = {
  'vector-ticorp-2020-reversed-source-vector': 'vector-ticorp-2025-colour-source-vector',
  'vector-infrastructure-bc-2026-reversed-source-vector': 'vector-infrastructure-bc-2026-colour-source-vector',
  'vector-community-living-bc-2014-reversed-source-vector': 'vector-community-living-bc-2023-colour-source-vector',
  'source-knowledge-network-knowledge-network-svg': 'source-knowledge-network-knowledge-network-colour-eps',
  'vector-pavco-2023-reversed-source-vector': 'vector-pavco-2025-26-colour-source-vector',
  'vector-phsa-white-source-extraction': 'vector-phsa-black-source-extraction',
  'vector-fnha-logo-white': 'vector-fnha-logo-colour',
  'source-first-nations-health-authority-fnha-white-png': 'source-first-nations-health-authority-fnha-horizontal-png',
  'vector-forest-renewal-bc-1999-black-source-vector': 'vector-forest-renewal-bc-2000-colour-source-vector',
  'historical-capital-health-region-2000-dark-white': 'historical-capital-health-region-2000-dark-grey',
  'source-innovate-bc-innovate-bc-white-eps': 'innovate-bc-2024-colour'
}

// What each version is called inside its design's entry.
const VERSION_LABELS = {
  'vector-ticorp-2025-colour-source-vector': 'Full colour',
  'vector-ticorp-2020-reversed-source-vector': 'White',
  'vector-infrastructure-bc-2026-colour-source-vector': 'Full colour',
  'vector-infrastructure-bc-2026-reversed-source-vector': 'Reversed',
  'vector-community-living-bc-2023-colour-source-vector': 'Full colour',
  'vector-community-living-bc-2014-reversed-source-vector': 'Reversed',
  'source-knowledge-network-knowledge-network-colour-eps': 'Full colour',
  'source-knowledge-network-knowledge-network-svg': 'White lettering',
  'vector-pavco-2025-26-colour-source-vector': 'Full colour',
  'vector-pavco-2023-reversed-source-vector': 'White',
  'vector-phsa-black-source-extraction': 'Black',
  'vector-phsa-white-source-extraction': 'White',
  'vector-fnha-logo-colour': 'Full colour',
  'vector-fnha-logo-white': 'White lettering',
  'source-first-nations-health-authority-fnha-horizontal-png': 'Full colour',
  'source-first-nations-health-authority-fnha-white-png': 'White',
  'vector-forest-renewal-bc-2000-colour-source-vector': 'Full colour',
  'vector-forest-renewal-bc-1999-black-source-vector': 'Black',
  'historical-capital-health-region-2000-dark-grey': 'Dark and grey',
  'historical-capital-health-region-2000-dark-white': 'Dark and white',
  'innovate-bc-2024-colour': 'Full colour',
  'source-innovate-bc-innovate-bc-white-eps': 'White'
}

// Shorter accounts where a body's or file's own record is about a file no longer shown.
const BODY_NOTES = {
  'bc-power-commission': 'Established in 1945 to consolidate local electricity systems and extend service to communities outside BC Electric’s territory, the BC Power Commission became one of BC Hydro’s two principal predecessors. BC Hydro was established in 1962, and the authority, BC Electric and the Power Commission were formally amalgamated on 20 August 1965. The emblem is reproduced by BC Hydro Power Pioneers, which documents it on the commission’s red service trucks; its designer and introduction date are unconfirmed.',
  'bc-steamship-company': 'A provincial Crown company, separate from BC Ferries, set up in 1975 to keep the Victoria–Seattle Princess Marguerite service. It added the Vancouver Island Princess in 1987, sold its vessels and operating assets to B.C. Stena Line in November 1988, and continued as a corporation, renamed Victoria Line Ltd. in 1994. Its circular emblem is documented on a 1987 casino token; the emblem’s introduction, colours and designer are unconfirmed, and the Princess Marguerite’s own 1983 brochure branding is a separate service identity.',
  'transportation-investment-corporation': 'One design — the BC emblem, a gold divider and the name on three lines — in full colour and in white, both original vector artwork from Pattullo Bridge Replacement Project publications.',
  'bc-housing': 'The emblem and wordmark, and the Research Centre lockup, as original vector artwork from a BC Housing report.',
  'bc-assessment': 'The full-colour logo from the official media kit: an SVG converted from its EPS, with the EPS itself as the original download.',
  'columbia-power': 'The logo as original vector artwork, reversed, from the 2024 history book.',
  'infrastructure-bc': 'One design in full colour and reversed, both original vector artwork from the Spring 2026 brochure.',
  'community-living-bc': 'One design in full colour and reversed, both original vector artwork from its 2014 and 2023 reports.',
  'knowledge-network': 'One design, in full colour and with white lettering, as vector artwork from the official brand kit.',
  'bc-pavilion-corporation': 'One design in full colour and in white, both original vector artwork from PavCo’s own publications.',
  'forest-enhancement-society': 'The horizontal and vertical logos from the official 2026 logo kit, as vector artwork, and the 10th-anniversary logo.',
  'innovate-bc': 'One logo, the disc with its i over “innovate BC”: in full colour from the 2024/2025 Impact Report (vector, with the report’s star-trail photograph in the disc), and in white as vector artwork from the official brand kit.',
  'bc-family-maintenance-agency': 'The logo as original vector artwork from the 2020/21 annual report.',
  'inbc': 'The logo as vector artwork from the official website.',
  'bc-council-for-international-education': 'The logo as original vector artwork from the 2022–2025 strategic plan.',
  'interior-health': 'The horizontal logo as original vector artwork, seen on a June 2004 letterhead and in a 2023 roadmap, with the stacked logo and the symbol as published images.',
  'provincial-health-services-authority': 'One design in black and in white, as original vector artwork.',
  'bc-heritage-trust': 'The boxed Trust mark as original vector artwork from the 2001/02 annual report; the same mark is on its 1989 conservation publication.',
  'forest-renewal-bc': 'One design in full colour and black, both original vector artwork from the Corporation’s 1999 and 2000 publications.',
  'oil-and-gas-commission': 'The corporate mark as original vector artwork from the 2014 annual report; the same mark is on official PDFs of 2019 and 2021.',
  'partnerships-bc': 'The wordmark as original vector artwork from the 2012/13 annual report; the same wordmark is in the 2006 service plan.',
  'capital-health-region': 'Capital Health Region of Victoria. One design in two original vector versions from 2000 publications, the same mark as on its 1999 and 2000 letterheads and newspaper notices. Dates identify appearances, not adoption.',
  'central-vancouver-island-health-region': 'The March 2002 report The World Without Linen Bags reproduces authentic 1999 letterheads. The full logo uses original PDF vector paths and glyph outlines, not a new trace. A grayscale emblem is also preserved from an embedded source image. Letter dates are sightings; no adoption date is asserted.',
  'north-okanagan-health-region': 'The NOHR emblem and acronym wordmark from the June 2000 report cover. The emblem alone is original vector; the full logo survives only as an image, its wordmark very small (46 × 22 px). No font substitution or traced wordmark supplied.',
  'northern-interior-regional-health-board': 'Original blue vector emblem and full name from the July 2001 annual report; the same mark is on an April 2001 organizational chart. Dates identify source appearances, not first use.'
}
const ASSET_NOTES = {
  'vector-ticorp-2025-colour-source-vector': 'The BC emblem, a gold divider and the name on three lines, as original vector paths from page 1 of the Pattullo Bridge Replacement Project’s Summer 2025 project update. The PDF’s print colours are converted to sRGB.',
  'vector-ticorp-2020-reversed-source-vector': 'The publication’s own white version, as original vector paths from the back cover of the Spring 2020 project overview. Its blue page is left out, so it needs a dark ground.'
}

/** A register entry as the inventory's asset record, so both read the same in the gallery. */
const fromRegister = (entry, search = 'vector-search-2026-10-30') => {
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
    publisher: entry.publisher ?? entry.organization,
    sourcePage: entry.sourcePageUrl ?? entry.sourceUrl,
    sourceUrl: entry.sourceUrl,
    sourceLocator: entry.sourcePdfPage ? `PDF page ${entry.sourcePdfPage}` : entry.sourcePackageEntry ?? null,
    sourceFile: entry.sourceTitle ?? null,
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
    search
  })
}

const additions = new Map()
for (const entry of register.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry))
}
for (const entry of ticorp.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry, 'ticorp-vector-2026-11-08'))
}
for (const entry of followup.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry, 'vector-followup-2026-11-08'))
}

// Historical specimens use inventory-shaped records; detailed extraction evidence stays in
// their source register rather than in the gallery bundle. They must name an inventory body.
const bodyIds = new Set(inventory.bodies.map((body) => body.id))
for (const { bodyId, verification, ...asset } of innovate.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown body: ${bodyId}`)
  // Vector paths over the report's own photograph, so not pure vector, and recorded as such.
  if (asset.isVector || verification?.textElements !== 0 || verification.externalResources?.length !== 0) {
    throw new Error(`Unexpected record for ${asset.id}`)
  }
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  additions.get(bodyId).push(checked({ ...asset, search: 'innovate-bc-vector-2026-11-12' }))
}
for (const { bodyId, verification, ...asset } of [...bcAssessment.assets, ...bcPowerCommission.assets]) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown body: ${bodyId}`)
  if (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0 || verification.externalResources?.length !== 0) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  for (const extra of asset.downloads ?? []) checked({ file: extra.file, sha256: extra.sha256 })
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  additions.get(bodyId).push(checked({ ...asset, search: asset.id === 'bc-power-commission-rebuilt' ? 'bc-power-commission-vector-2026-11-12' : 'bc-assessment-vector-2026-11-12' }))
}
for (const { bodyId, verification, ...asset } of historical.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown historical body: ${bodyId}`)
  if (asset.isVector && (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0 || verification.externalResources?.length !== 0)) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  // A superseded file is not shown, so its file need not be held.
  const record = { ...asset, search: 'historical-vector-followup-2026-10-30' }
  additions.get(bodyId).push(SUPERSEDED[asset.id] ? record : checked(record))
}
for (const bodyId of Object.keys(historical.bodyUpdates)) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown historical body update: ${bodyId}`)
}

// Dates of the files each kept file stands for, as further sightings of its design.
const alsoSeenOf = (all, id) => all.filter((asset) => SUPERSEDED[asset.id] === id && asset.sourceDate)
  .map((asset) => ({ date: asset.sourceDate, source: asset.sourcePage || asset.sourceUrl || null }))
const kept = (assets) => assets.filter((asset) => !SUPERSEDED[asset.id])
  .map((asset) => {
    const alsoSeen = alsoSeenOf(assets, asset.id)
    return alsoSeen.length ? { ...asset, alsoSeen } : asset
  })
const finished = (asset) => ({
  ...asset,
  ...(ASSET_NOTES[asset.id] ? { notes: ASSET_NOTES[asset.id] } : {}),
  ...(VERSION_LABELS[asset.id] ? { versionLabel: VERSION_LABELS[asset.id] } : {}),
  ...(VARIANT_OF[asset.id] ? { variantOf: VARIANT_OF[asset.id] } : {})
})

// Where later research changed a body's years: the Steamship Company was renamed in 1994, not
// dissolved in 1992, and its legal end is untraced.
const BODY_DATES = { 'bc-steamship-company': { to: null } }

const bodies = inventory.bodies.map((body) => {
  const { queries, researchSources, ...display } = body
  for (const asset of kept(display.assets)) checked(asset)
  const added = additions.get(body.id) ?? []
  additions.delete(body.id)
  const record = added.length ? {
    ...display,
    ...historical.bodyUpdates[body.id],
    status: 'asset-collected',
    assets: [...display.assets, ...added]
  } : display
  return {
    ...record,
    ...(BODY_NOTES[body.id] ? { notes: BODY_NOTES[body.id] } : {}),
    ...BODY_DATES[body.id],
    assets: kept(record.assets).map(finished)
  }
})
for (const [id, keeper] of Object.entries({ ...SUPERSEDED, ...VARIANT_OF })) {
  const ids = new Set(bodies.flatMap((body) => body.assets.map((asset) => asset.id)))
  if (!ids.has(keeper) || (VARIANT_OF[id] && !ids.has(id))) throw new Error(`Unknown consolidation: ${id} → ${keeper}`)
}

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
