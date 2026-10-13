// Attaches each Forest Service drawing to its parts. One loader per poster, so opening a badge
// fetches that badge's drawing and nothing else.

import { FOREST_SERVICE_POSTERS } from './posters.js'

const DRAWINGS = {
  'dont-drop-it': () => import('./dont-drop-it.svg?raw'),
  'dont-gamble-with-fire': () => import('./dont-gamble-with-fire.svg?raw'),
  'reward-living-forest': () => import('./reward-living-forest.svg?raw'),
  'enjoy-protect-forests': () => import('./enjoy-protect-forests.svg?raw')
}

export const loaderFor = (id) => async () => {
  const { default: svgRaw } = await DRAWINGS[id]()
  const { parts, order, regions, spotlight } = FOREST_SERVICE_POSTERS[id]
  return { svgRaw, parts, order, regions, spotlight }
}
