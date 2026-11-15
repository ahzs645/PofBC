// How a badge is being looked at, kept from one badge to the next. No React and no DOM.

export const BADGE_VIEW_KEY = 'pofbc.badge-view.v1'
export const BADGE_MODES = ['metal', 'vector']
export const BADGE_CURVES = ['flat', 'cylinder', 'dome']
export const BADGE_CAMERAS = ['front', 'oblique', 'top', 'side', 'back']
export const MAX_RISE_MM = 8

// The curved badge trial's default: a 4 mm centre-to-edge rise across the width.
export const BADGE_VIEW_DEFAULTS = Object.freeze({ mode: 'metal', curvature: 'cylinder', rise: 4, camera: 'oblique' })

const oneOf = (value, allowed, fallback) => (allowed.includes(value) ? value : fallback)

export function normalizeBadgeView (raw) {
  const view = raw && typeof raw === 'object' ? raw : {}
  const rise = Number(view.rise)
  return {
    mode: oneOf(view.mode, BADGE_MODES, BADGE_VIEW_DEFAULTS.mode),
    curvature: oneOf(view.curvature, BADGE_CURVES, BADGE_VIEW_DEFAULTS.curvature),
    rise: Number.isFinite(rise) ? Math.max(0, Math.min(MAX_RISE_MM, Math.round(rise * 2) / 2)) : BADGE_VIEW_DEFAULTS.rise,
    camera: oneOf(view.camera, BADGE_CAMERAS, BADGE_VIEW_DEFAULTS.camera)
  }
}

/** Storage can be missing, blocked or full; the viewer works the same without it. */
export function loadBadgeView (storage) {
  try {
    return normalizeBadgeView(JSON.parse(storage?.getItem(BADGE_VIEW_KEY) ?? 'null'))
  } catch {
    return normalizeBadgeView(null)
  }
}

export function saveBadgeView (storage, view) {
  try {
    storage?.setItem(BADGE_VIEW_KEY, JSON.stringify(normalizeBadgeView(view)))
  } catch { /* private window, quota */ }
}
