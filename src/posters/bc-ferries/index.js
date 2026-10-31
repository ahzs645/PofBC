// Attaches each BC Ferries decal drawing to its parts. One loader per decal, so opening one fetches
// that drawing and nothing else.

import { BC_FERRIES_POSTERS } from './posters.js'

const DRAWINGS = {
  'go-bc-ferries': () => import('./go-bc-ferries.svg?raw'),
  'queen-of-sidney': () => import('./queen-of-sidney.svg?raw')
}

export const loaderFor = (id) => async () => {
  const { default: svgRaw } = await DRAWINGS[id]()
  const { parts, order, regions, spotlight } = BC_FERRIES_POSTERS[id]
  return { svgRaw, parts, order, regions, spotlight }
}
