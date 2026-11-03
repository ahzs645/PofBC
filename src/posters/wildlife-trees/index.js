// Attaches the Wildlife Trees drawing to its parts.
//
// The drawing is the largest on the site (15 MB, about 4.5 MB as served compressed), so the poster
// opens on a stand-in and sharpens when the drawing arrives. The stand-in is a drawing of the same
// size holding one 200 KB image of the poster (preview.png), so the stage, its zoom, the hotspots,
// the panels and the story all work from the first moment; only the spotlight, which lights the
// drawing's own layers, and export wait for the real thing. The drawing is fetched as a file rather
// than built into a script, which would carry it as one escaped string to be parsed first.
//
// See artwork/posters/wildlife-trees/ for how the copy and the preview are made.

import drawingUrl from './wildlife-trees.svg?url'
import previewUrl from './preview.png'
import { POSTERS } from '../catalogue.js'
import { WILDLIFE_TREES } from './posters.js'

const { w, h } = POSTERS['wildlife-trees'].view

const STAND_IN = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}">`
  + '<title>Wildlife Trees (preview while the drawing loads)</title>'
  + `<rect id="paper" width="${w}" height="${h}" fill="#ffffff"/>`
  + `<image href="${previewUrl}" width="${w}" height="${h}" preserveAspectRatio="none"/>`
  + '</svg>'

let drawing

/** The drawing, fetched once; a failed fetch is forgotten, so asking again tries again. */
const fetchDrawing = () => {
  drawing ??= fetch(drawingUrl)
    .then((response) => {
      if (!response.ok) throw new Error(`Wildlife Trees: ${response.status} fetching the drawing`)
      return response.text()
    })
    .catch((error) => {
      drawing = undefined
      throw error
    })
  return drawing
}

export const load = async () => {
  const { parts, order, regions, spotlight } = WILDLIFE_TREES
  // Started now, so the download runs while the stand-in is on screen.
  fetchDrawing().catch(() => {})
  return { svgRaw: STAND_IN, upgrade: fetchDrawing, parts, order, regions, spotlight }
}
