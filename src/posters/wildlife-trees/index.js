// Attaches the Wildlife Trees drawing to its parts.
//
// The drawing is the largest on the site (15 MB, about 4.5 MB as served compressed), so it is
// fetched as a file rather than built into a script: a script would carry it as one escaped
// string, to be parsed before it could be used. See artwork/posters/wildlife-trees/ for how this
// copy is made from the supplied master.

import drawingUrl from './wildlife-trees.svg?url'
import { WILDLIFE_TREES } from './posters.js'

let drawing

export const load = async () => {
  drawing ??= fetch(drawingUrl).then((response) => {
    if (!response.ok) throw new Error(`Wildlife Trees: ${response.status} fetching the drawing`)
    return response.text()
  })
  try {
    const svgRaw = await drawing
    const { parts, order, regions, spotlight } = WILDLIFE_TREES
    return { svgRaw, parts, order, regions, spotlight }
  } catch (error) {
    drawing = undefined // let a retry fetch it again
    throw error
  }
}
