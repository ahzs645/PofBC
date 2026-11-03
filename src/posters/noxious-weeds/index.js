// Attaches each Noxious Weeds drawing to its parts. The drawings name their pictures by file
// (`images/…`), as the build wrote them; the bundle gives each a hashed address, put in here.

import { NOXIOUS_WEEDS_POSTERS } from './posters.js'

const IMAGES = import.meta.glob('./images/*', { eager: true, query: '?url', import: 'default' })
const prepare = (raw) => raw.replace(/href="images\/([^"]+)"/g, (whole, name) => `href="${IMAGES[`./images/${name}`] ?? `images/${name}`}"`)

const DRAWINGS = {
  'beware-these-alien-invaders': () => import('./beware-these-alien-invaders.svg?raw'),
  'shattering-the-environment': () => import('./shattering-the-environment.svg?raw'),
  'explosion-in-slow-motion': () => import('./explosion-in-slow-motion.svg?raw')
}

export const loaderFor = (id) => async () => {
  const { default: svgRaw } = await DRAWINGS[id]()
  const { parts, order, regions, spotlight } = NOXIOUS_WEEDS_POSTERS[id]
  return { svgRaw, prepare, parts, order, regions, spotlight }
}
