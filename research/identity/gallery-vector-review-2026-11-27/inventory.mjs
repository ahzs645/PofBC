// Run from the repository after build:cleanbc-artwork. Inspect the same files the gallery renders.
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { GALLERY_COLLECTIONS, entriesOf } from '../../../src/gallery/collections.js'
import { defaultCollectedAsset, tileArt } from '../../../src/gallery/tileArt.js'
import gaps from '../vector-recovery-2026-11-26/remaining-gaps.json' with { type: 'json' }

const publicRoot = new URL('../../../public/', import.meta.url)
const openResearch = new Map(gaps.designGaps.map((entry) => [entry.id, entry.nextAction]))
const memo = new Map()

function fileType(path) {
  if (memo.has(path)) return memo.get(path)
  const file = new URL(path.replace(/^\//, ''), publicRoot)
  if (!existsSync(file)) throw new Error('Missing gallery artwork: ' + path)
  const kind = path.endsWith('.svg') ? svgType(readFileSync(file, 'utf8')) : 'Raster'
  memo.set(path, kind)
  return kind
}

function svgType(svg) {
  for (const match of svg.matchAll(/<(?:[\w-]+:)?(?:feImage|image)\b[^>]*>/gi)) {
    const href = /(?:xlink:)?href=["']([^"']+)/.exec(match[0])?.[1]
    // A filter can reference another vector group inside this SVG, as Surrey's logo does.
    if (href?.startsWith('#') && (svg.includes('id="' + href.slice(1) + '"') || svg.includes("id='" + href.slice(1) + "'"))) continue
    if (!href || !href.endsWith('.svg') || fileType(href) !== 'Vector') return 'Contains bitmap'
  }
  return 'Vector'
}

function preview(entry, theme) {
  const art = tileArt(entry, theme)
  const src = /^<img\b[^>]*\bsrc="([^"]+)"/.exec(art)?.[1]
  return src ? fileType(src) : svgType(art)
}

function native(asset) {
  return asset.isVector && !asset.containsRaster && !asset.reconstruction &&
    (asset.format === 'eps' || asset.format === 'svg' && fileType(asset.file) === 'Vector')
}

const treatmentNotes = {
  'innovate-bc-2024-colour': 'The colour signature contains the published star-trail photograph. Dark mode uses the white logo-kit EPS.',
  'source-expanded-coast-mountain-bus-company-route-map-logo': 'The colour route-map specimen is raster. Dark mode uses the published 2022 white signature.',
  'school-district-84-logo-current': 'The website crest has black lettering. Dark mode uses the native light-lettered strategic-plan crest.',
  'school-district-93-sd093-observed-2010-2011': 'The illustrated-book positive has an oval and blue backdrop. Dark mode uses the white-lettered annual-report treatment.',
  'gardens-bc-appendix-2024': 'Orange lettering on the photographed or textured field survives in pixels. The separate monochrome website design has its own native SVG.',
  'bcgs-centennial-1995': 'The title page shows a solid black 100 with heavy lettering. The plotted map has a hatched 100 and different letterforms.',
  'bcgs-survey-seal': 'The 2017 PDF contains the shaded field of the colour seal. The 1999 cover vector has flat fills and different hammer and lettering details.'
}

const header = ['Collection', 'Design', 'Shelf representative', 'Light tile', 'Dark tile', 'Default artwork', 'Alternate native vector IDs', 'Source or guide', 'Evidence or open question', 'Gallery link', 'Default provenance', 'Dark artwork']
const rows = []
for (const collection of GALLERY_COLLECTIONS) {
  const entries = entriesOf(collection)
  const cover = collection.shelfSpecimen ?? collection.cover ?? entries[0]?.id
  for (const entry of entries) {
    const { asset } = entry
    const versions = entry.versions ?? (asset ? [asset] : [])
    for (const version of versions) {
      if (!existsSync(new URL(version.file, publicRoot))) throw new Error('Missing download: ' + version.file)
    }
    const alternates = versions.filter((version) => version !== asset && native(version))
    const artwork = asset ? defaultCollectedAsset(entry, 'light').file : 'Drawn by the gallery'
    const source = asset?.sourceUrl ?? asset?.sourcePage ?? entry.identity.applicability.sources?.[0]?.url ?? ''
    const note = treatmentNotes[entry.id] ?? (!asset ? entry.identity.provenance : native(asset) ? 'Publisher vector or documented source-colour version'
      : asset.reconstruction ? 'Reconstruction; published source and attribution are on the design page'
      : alternates.length ? 'Other published treatments are selectable. The positive specimen retains its documented drawing and colours.'
      : openResearch.get(entry.id) ?? 'Matching native source remains unverified for this specimen.')
    rows.push([collection.label, entry.label, entry.id === cover ? 'Yes' : '', preview(entry, 'light'), preview(entry, 'dark'),
      artwork, alternates.map((a) => a.id).join(' | '), source, note,
      'https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=' + encodeURIComponent(collection.id) + '&mark=' + encodeURIComponent(entry.id),
      entry.identity.provenance, asset ? defaultCollectedAsset(entry, 'dark').file : 'Drawn by the gallery'])
  }
}
function line(row) {
  return row.map((cell) => '"' + String(cell ?? '').replaceAll('"', '""') + '"').join(',')
}
writeFileSync(new URL('inventory.csv', import.meta.url), [header, ...rows].map(line).join('\n') + '\n')
for (const [group, members] of [['All designs', rows], ['Shelf representatives', rows.filter((row) => row[2])]]) {
  console.log(group, members.length, 'designs across', GALLERY_COLLECTIONS.length, 'collections')
  for (const [i, theme] of [[3, 'light'], [4, 'dark']]) {
    const counts = {}
    for (const row of members) counts[row[i]] = (counts[row[i]] ?? 0) + 1
    console.log(theme, counts)
  }
}
