// How a patch is being looked at: the simulation's settings, kept from one patch to the next, and
// the arithmetic of zooming and panning the stage. No React and no DOM, so it can be tested alone.

export const VIEW_KEY = 'pofbc.patch-view.v1'

export const WIDTHS = ['76', '89', '102', '127']
export const BORDERS = ['merrow', 'satin', 'none']
export const FINISHES = ['matte', 'glossy']
export const GROUNDS = ['cloth', 'stitched']
export const MODES = ['embroidery', 'vector', 'source', 'compare']

export const VIEW_DEFAULTS = Object.freeze({
  widthMm: '89',
  border: 'merrow',
  finish: 'matte',
  // Most cloth patches are sewn on a twill ground, which shows between the lettering and the motif.
  ground: 'cloth',
  lightDeg: 225,
  mode: 'embroidery'
})

const oneOf = (value, allowed, fallback) => (allowed.includes(value) ? value : fallback)

/** Any stored or partial settings, made whole and valid. */
export const normalizeView = (raw) => {
  const view = raw && typeof raw === 'object' ? raw : {}
  const light = Number(view.lightDeg)
  return {
    widthMm: oneOf(String(view.widthMm), WIDTHS, VIEW_DEFAULTS.widthMm),
    border: oneOf(view.border, BORDERS, VIEW_DEFAULTS.border),
    finish: oneOf(view.finish, FINISHES, VIEW_DEFAULTS.finish),
    ground: oneOf(view.ground, GROUNDS, VIEW_DEFAULTS.ground),
    lightDeg: Number.isFinite(light) ? ((Math.round(light) % 360) + 360) % 360 : VIEW_DEFAULTS.lightDeg,
    mode: oneOf(view.mode, MODES, VIEW_DEFAULTS.mode)
  }
}

/** Storage can be missing, blocked or full; the viewer works the same without it. */
export const loadView = (storage) => {
  try {
    return normalizeView(JSON.parse(storage?.getItem(VIEW_KEY) ?? 'null'))
  } catch {
    return normalizeView(null)
  }
}

export const saveView = (storage, view) => {
  try {
    storage?.setItem(VIEW_KEY, JSON.stringify(normalizeView(view)))
  } catch { /* private window, quota */ }
}

/** A source comparison needs a source: badges and unreviewed collections fall back to the simulation. */
export const modeFor = (mode, hasSource) => (!hasSource && (mode === 'source' || mode === 'compare') ? 'embroidery' : mode)

// ── Zoom and pan ──
// The stage's content is drawn with `translate(x, y) scale(k)` about its centre; x and y are in
// CSS pixels, and a point is given relative to the stage's centre.

export const MIN_ZOOM = 1
export const MAX_ZOOM = 6
export const FIT = Object.freeze({ k: 1, x: 0, y: 0 })

/** Keep the content over the stage: it may move only as far as zooming made it larger. */
export const clampPan = ({ k, x, y }, width, height) => {
  const limitX = ((k - 1) * width) / 2
  const limitY = ((k - 1) * height) / 2
  return { k, x: Math.max(-limitX, Math.min(limitX, x)), y: Math.max(-limitY, Math.min(limitY, y)) }
}

/** Zoom to `k` so that the content under (px, py) stays under it. */
export const zoomTo = (view, k, px, py, width, height) => {
  const next = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, k))
  if (next === MIN_ZOOM) return { ...FIT }
  const ratio = next / view.k
  return clampPan({ k: next, x: px - (px - view.x) * ratio, y: py - (py - view.y) * ratio }, width, height)
}

/** The pixel size of a PNG export of a result (mm, with its padding). */
export const exportScale = (result) => Math.min(24, 6000 / Math.max(result.widthMm, result.heightMm))
export const exportSize = (result) => {
  const scale = exportScale(result)
  return { width: Math.round(result.widthMm * scale), height: Math.round(result.heightMm * scale) }
}
