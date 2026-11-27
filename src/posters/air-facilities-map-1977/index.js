import svgRaw from './poster.svg?raw'
import reference from './reference.jpg'
import { AIR_FACILITIES_POSTER } from './poster.js'
export const load = () => ({
  ...AIR_FACILITIES_POSTER, svgRaw,
  reference: { src: reference, box: AIR_FACILITIES_POSTER.parts.overview.box, caption: 'Perspective-corrected photograph of the historical 1977/78 map cover. Its original physical proportions and colours have not been independently measured.' }
})
