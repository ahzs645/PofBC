// Source artwork acquired during the 2026-11-26 gallery audit. Existing design IDs,
// published rasters and collection metadata stay in place; matching native files
// are added as versions. Different layouts and historical designs remain entries.
import recovery from './vectorRecoveryData.json' with { type: 'json' }
import { groupSpecimen } from './groupedSpecimens.js'

export const withVectorRecovery = (bodies) => {
  const held = new Set(bodies.map(({ id }) => id))
  const newBodies = recovery.newBodies.filter(({ id }) => !held.has(id))
  return [...bodies, ...newBodies].map((body) => {
    const additions = recovery.additions[body.id] ?? []
    const assets = [...(body.assets ?? []), ...additions].map((asset) => {
      const patch = recovery.assetPatches[asset.id]
      if (!patch) return groupSpecimen(asset)
      return groupSpecimen({
        ...asset, ...patch,
        ...(patch.alsoSeen ? { alsoSeen: [...(asset.alsoSeen ?? []), ...patch.alsoSeen] } : {})
      })
    })
    // An explicitly sectioned collection must expose newly acquired designs too.
    const newDesigns = additions.filter(({ variantOf }) => !variantOf).map(({ id }) => id)
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
