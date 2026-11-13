// A body's logos for the government panel: only those the project holds as vectors — drawn by its
// own renderers, or collected as SVG — so a body with only a raster scan shows none yet. Loaded on
// demand, so the government view does not carry the gallery's renderers until a body has logos.

import { collectionsOfNode, entriesOfNode } from './collections.js'
import { onPage, tileArt } from './tileArt.js'

// A design's default download can be EPS while another published colourway is usable SVG.
// Select artwork for this thumbnail without changing the design ID or its gallery downloads.
const vectorEntry = (entry) => {
  if (entry.kind !== 'collected') return entry
  const asset = (entry.versions ?? [entry.asset]).find((version) => version.isVector && version.format === 'svg')
  return asset ? { ...entry, asset } : null
}

/**
 * The collection holding a body's logos, with up to `limit` of its vector logos drawn for the
 * theme: its cover first, then one from each era, newest first. Null for a body with no vector logo.
 */
export const logosFor = (nodeId, theme = 'light', limit = 4) => {
  const collections = collectionsOfNode(nodeId)
  const collection = collections[0]
  if (!collection) return null
  // Each body keeps its own entries, including those placed on a shared gallery shelf.
  const held = collections.flatMap((owner) => entriesOfNode(owner, nodeId)
    .map(vectorEntry).filter(Boolean).map((entry) => ({ collection: owner, entry })))
  if (!held.length) return null
  // An era collection lists its eras oldest first; a collected one its files as they were registered.
  const firsts = collections.flatMap((owner) => [...(owner.eras ?? [])].reverse()
    .map((era) => held.find((item) => item.collection === owner && era.entries.some((entry) => entry.id === item.entry.id)))
    .filter(Boolean))
  const ordered = [...new Set([...firsts, ...held])]
  const cover = ordered.find((item) => item.entry.id === collection.cover)
  const shown = [...(cover ? [cover] : []), ...ordered.filter((item) => item !== cover)].slice(0, limit)
  return {
    collection: collection.id,
    collections: [...new Set(held.map((item) => item.collection.id))],
    label: collection.label,
    total: held.length,
    entries: shown.map(({ collection: owner, entry }) => ({
      id: entry.id,
      collection: owner.id,
      label: entry.label,
      ground: onPage(entry) ? 'page' : 'own',
      image: entry.kind === 'collected' && !onPage(entry),
      html: tileArt(entry, theme)
    }))
  }
}
