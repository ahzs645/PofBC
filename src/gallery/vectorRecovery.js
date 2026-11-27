// Source artwork acquired after the gallery's first collections: the 2026-11-26 gallery audit, and
// packages from a single source since (the City of Vancouver's 2018 visual standards guide, and
// Northwest Community College's logos from the college's own publications).
// Existing design IDs, published rasters and collection metadata stay in place; matching native
// files are added as versions. Different layouts and historical designs remain entries.
import recovery from './vectorRecoveryData.json' with { type: 'json' }
import vancouver from './vancouverVisualStandards.json' with { type: 'json' }
import nwcc from './nwccVectorLogos.json' with { type: 'json' }
import { groupSpecimen } from './groupedSpecimens.js'

/** Every package of recovered artwork, oldest first. */
export const RECOVERY_PACKAGES = [recovery, vancouver, nwcc]

export const withVectorRecovery = (bodies) => {
  const held = new Set(bodies.map(({ id }) => id))
  const newBodies = RECOVERY_PACKAGES.flatMap((pack) => pack.newBodies ?? []).filter(({ id }) => !held.has(id))
  const patches = Object.assign({}, ...RECOVERY_PACKAGES.map((pack) => pack.assetPatches ?? {}))
  return [...bodies, ...newBodies].map((original) => {
    // A package can say what a body's collection now holds, and how its page groups it.
    const body = Object.assign({}, original, ...RECOVERY_PACKAGES.map((pack) => pack.bodyPatches?.[original.id] ?? {}))
    const additions = RECOVERY_PACKAGES.flatMap((pack) => pack.additions?.[body.id] ?? [])
    const assets = [...(body.assets ?? []), ...additions].map((asset) => {
      const patch = patches[asset.id]
      if (!patch) return groupSpecimen(asset)
      return groupSpecimen({
        ...asset, ...patch,
        ...(patch.alsoSeen ? { alsoSeen: [...(asset.alsoSeen ?? []), ...patch.alsoSeen] } : {})
      })
    })
    // An explicitly sectioned collection must expose newly acquired designs too.
    const placed = new Set((body.artworkSections ?? []).flatMap(({ marks }) => marks))
    const newDesigns = additions.filter(({ variantOf, id }) => !variantOf && !placed.has(id)).map(({ id }) => id)
    const section = { id: 'source-recovery-2026', label: 'Further published artwork', marks: newDesigns }
    return {
      ...body, assets,
      ...(body.artworkSections && newDesigns.length
        ? { artworkSections: [...body.artworkSections, section] } : {}),
      ...(body.eras && newDesigns.length
        ? { eras: [...body.eras, { ...section, years: 'Dates on each specimen' }] } : {})
    }
  })
}
