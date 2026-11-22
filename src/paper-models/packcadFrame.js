// The site's side of PackCAD's viewer contract (vendor/packcad/docs/embed.md).
//
// The viewer is PackCAD's own page, built into public/packcad/ by scripts/build-packcad.mjs and put
// in an iframe: it brings its own React and three.js, which this site does not share. This file
// says where it is and what may pass between the two; PackcadFrame.jsx is the frame itself.

/** The viewer page, under the site's base URL. */
export const viewerPage = (base) => `${base}packcad/viewer.html`

/**
 * The viewer's address for a project. The project path is relative to the viewer page, which is
 * one folder down (packcad/), so a path under public/ is reached with `../`.
 */
export const viewerSrc = (base, projectPath, { step = 'final', autoplay = false, layout = '3d', controls = false } = {}) => {
  const params = new URLSearchParams({
    project: `../${projectPath}`,
    step: String(step),
    autoplay: autoplay ? '1' : '0',
    layout,
    controls: controls ? '1' : '0'
  })
  return `${viewerPage(base)}?${params}`
}

const EVENTS = new Set(['packcad:ready', 'packcad:state', 'packcad:error'])

/** A message from the viewer, or null for anything else on the window's channel. */
export const viewerEvent = (data) =>
  data && typeof data === 'object' && EVENTS.has(data.type) ? data : null

/** The stages a viewer reported, with the setup (the flat sheet) apart from the folds. */
export const stagesOf = (steps = []) => ({ setup: steps[0] ?? null, folds: steps.slice(1) })
