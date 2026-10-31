// A body's logos for the government panel: only those the project holds as vectors — drawn by its
// own renderers, or collected as SVG — so a body with only a raster scan shows none yet. Loaded on
// demand, so the government view does not carry the gallery's renderers until a body has logos.

import { entriesOf, GALLERY_COLLECTIONS } from './collections.js'
import { onPage, tileArt } from './tileArt.js'

const isVector = (entry) => entry.kind !== 'collected' || (entry.asset.isVector && entry.asset.format === 'svg')

/**
 * The collection holding a body's logos, with up to `limit` of its vector logos drawn for the
 * theme: its cover first, then one from each era, newest first. Null for a body with no vector logo.
 */
export const logosFor = (nodeId, theme = 'light', limit = 4) => {
  const collection = GALLERY_COLLECTIONS.find((each) => each.graphNode === nodeId)
  if (!collection) return null
  const held = entriesOf(collection).filter(isVector)
  if (!held.length) return null
  // An era collection lists its eras oldest first; a collected one its files as they were registered.
  const firsts = collection.eras
    ? [...collection.eras].reverse().map((era) => era.entries.find(isVector)).filter(Boolean)
    : []
  const ordered = [...new Set([...firsts, ...held])]
  const cover = ordered.find((entry) => entry.id === collection.cover)
  const shown = [...(cover ? [cover] : []), ...ordered.filter((entry) => entry !== cover)].slice(0, limit)
  return {
    collection: collection.id,
    label: collection.label,
    total: held.length,
    entries: shown.map((entry) => ({
      id: entry.id,
      label: entry.label,
      ground: onPage(entry) ? 'page' : 'own',
      image: entry.kind === 'collected',
      html: tileArt(entry, theme)
    }))
  }
}
