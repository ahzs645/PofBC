// Attaches each Forest Service drawing to its parts. One loader per poster, so opening a badge
// fetches that badge's drawing and nothing else.

import { FOREST_SERVICE_POSTERS } from './posters.js'
import rewardComparison from './reward-comparison.webp'
import raccoon from './coons-age-raccoon.webp'

// Proof sheets a panel shows, by the name the data gives them.
const FIGURES = { 'reward-living-forest': { 'reward-comparison': rewardComparison } }

// A drawing that names its photograph by file: the bundle gives the file a hashed address.
const PREPARE = {
  'coons-age': (raw) => raw.replace('href="coons-age-raccoon.webp"', `href="${raccoon}"`)
}

const DRAWINGS = {
  'dont-drop-it': () => import('./dont-drop-it.svg?raw'),
  'dont-gamble-with-fire': () => import('./dont-gamble-with-fire.svg?raw'),
  'be-careful': () => import('./be-careful.svg?raw'),
  'reward-living-forest': () => import('./reward-living-forest.svg?raw'),
  'enjoy-protect-forests': () => import('./enjoy-protect-forests.svg?raw'),
  'coons-age': () => import('./coons-age.svg?raw')
}

export const loaderFor = (id) => async () => {
  const { default: svgRaw } = await DRAWINGS[id]()
  const { parts, order, regions, spotlight, variations } = FOREST_SERVICE_POSTERS[id]
  return { svgRaw, prepare: PREPARE[id], parts, order, regions, spotlight, variations, figures: FIGURES[id] }
}
