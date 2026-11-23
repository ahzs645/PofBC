// Designs Patcher's library carries as patches that turned out not to be cloth patches. They are
// left out of Patches and Badges, and a link to one (by its own id or an atlas id absorbed into it)
// opens the place on this site that now holds the design.
//
// Patcher keeps the records; this site only stops offering them as patches. Kept independent of
// 'patcher/library' so App can redirect an old link without loading the patch catalogue.

/** Retired variant groups (Patcher cards), each with the place its links now open. */
export const RETIRED_PATCH_GROUPS = {
  // Printed on Forest Service posters, never photographed as a cloth patch. The internal logo is
  // the current drawing; the patch variants were recolours of an earlier version of it.
  'forest-service-yellow-sky': {
    reason: 'A printed emblem on Forest Service posters, not a cloth patch.',
    to: { view: 'internal', internal: 'forests', 'internal-logo': 'forest-service-yellow-sky' }
  }
}

/** Every id that opened a retired card: its variants, and the atlas ids absorbed into them. */
export const RETIRED_PATCH_IDS = {
  'FO-yellow-sky': 'forest-service-yellow-sky',
  'FO-yellow-sky-cream': 'forest-service-yellow-sky',
  'FO-yellow-sky-dark': 'forest-service-yellow-sky',
  'S05-O01': 'forest-service-yellow-sky',
  'S54-O01': 'forest-service-yellow-sky',
  'S04-O01': 'forest-service-yellow-sky'
}

const PATCH_VIEWS = new Set(['patches', 'badges'])
/** The patch view's own place, dropped when its link moves to another view. */
const PATCH_PLACE_KEYS = ['org', 'patch', 'group', 'family', 'q']

export const isRetiredPatch = (patch) => Boolean(
  patch && ((patch.group && RETIRED_PATCH_GROUPS[patch.group]) || RETIRED_PATCH_IDS[patch.id])
)

/** Sectors without the retired patches, and without any organization or sector left empty. */
export const withoutRetiredPatches = (sectors) => sectors
  .map((sector) => ({
    ...sector,
    orgs: sector.orgs
      .map((org) => ({ ...org, patches: org.patches.filter((patch) => !isRetiredPatch(patch)) }))
      .filter((org) => org.patches.length)
  }))
  .filter((sector) => sector.orgs.length)

/** A patch link to a retired design, rewritten to the place that holds it now; otherwise null. */
export function retiredPatchUrl(href) {
  const url = new URL(href)
  if (!PATCH_VIEWS.has(url.searchParams.get('view'))) return null
  const group = RETIRED_PATCH_IDS[url.searchParams.get('patch') ?? '']
  if (!group) return null
  for (const key of PATCH_PLACE_KEYS) url.searchParams.delete(key)
  for (const [key, value] of Object.entries(RETIRED_PATCH_GROUPS[group].to)) url.searchParams.set(key, value)
  return url
}
