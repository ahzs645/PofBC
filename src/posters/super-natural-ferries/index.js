import svgRaw from './poster.svg?raw'
import reference from './reference.jpg'
import { FERRIES_POSTER } from './poster.js'

export const load = () => ({
  ...FERRIES_POSTER,
  svgRaw,
  reference: {
    src: reference,
    box: FERRIES_POSTER.parts.overview.box,
    caption: 'The supplied reference scan of “Our good ferries take you to some very enchanted islands.”, part of the Tourism B.C. campaign awarded ADCC Gold in 1985. The scan does not establish the original print dimensions.'
  }
})
