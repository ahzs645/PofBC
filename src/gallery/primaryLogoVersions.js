// Keep published rasters and their design IDs when adding independently reviewed versions.
import versions from './primaryLogoVersions.json' with { type: 'json' }

export const withPrimaryLogoVersions = (body) => ({
  ...body,
  assets: (body.assets ?? []).flatMap((design) => {
    const recovered = versions[design.id]
    if (!recovered || design.variantOf) return [design]
    const preferred = recovered.preferred && !design.preferredVector && !design.preferredReconstruction
      ? { preferredReconstruction: recovered.preferred }
      : {}
    return [
      { ...design, versionLabel: design.versionLabel ?? recovered.sourceLabel, ...preferred },
      recovered.asset,
    ]
  })
})
