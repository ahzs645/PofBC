// Patch links to designs Patcher's library no longer carries, and where each now leads. Kept
// independent of 'patcher/library' so App can redirect an old link without loading the catalogue.

const YELLOW_SKY_LOGO = { view: 'internal', internal: 'forests', 'internal-logo': 'forest-service-yellow-sky' }
const GREEN_GOLD_PATCH = { view: 'patches', patch: 'FO-green-gold' }

/**
 * Retired ids, by their own id or an atlas id once absorbed into them. The yellow-sky oval was
 * printed on Forest Service posters, not sewn, so it lives in Departmental Logos; the green-and-gold
 * oval's generated black recolours were dropped, and lead to its full-colour patch.
 */
export const RETIRED_PATCHES = {
  'FO-yellow-sky': YELLOW_SKY_LOGO,
  'FO-yellow-sky-cream': YELLOW_SKY_LOGO,
  'FO-yellow-sky-dark': YELLOW_SKY_LOGO,
  'S05-O01': YELLOW_SKY_LOGO,
  'S54-O01': YELLOW_SKY_LOGO,
  'S04-O01': YELLOW_SKY_LOGO,
  'FO-green-gold-black-gold': GREEN_GOLD_PATCH,
  'FO-green-gold-black': GREEN_GOLD_PATCH
}

const PATCH_VIEWS = new Set(['patches', 'badges'])
/** The patch view's own place, dropped when the link moves on. */
const PATCH_PLACE_KEYS = ['org', 'patch', 'group', 'family', 'q']

/** A patch link to a retired design, rewritten to the place that holds it now; otherwise null. */
export function retiredPatchUrl(href) {
  const url = new URL(href)
  if (!PATCH_VIEWS.has(url.searchParams.get('view'))) return null
  const to = RETIRED_PATCHES[url.searchParams.get('patch') ?? '']
  if (!to) return null
  for (const key of PATCH_PLACE_KEYS) url.searchParams.delete(key)
  for (const [key, value] of Object.entries(to)) url.searchParams.set(key, value)
  return url
}
