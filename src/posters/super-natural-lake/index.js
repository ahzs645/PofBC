import svgRaw from './poster.svg?raw'
import reference from './reference.jpg'
import { LAKE_POSTER } from './poster.js'

export const load = () => ({
  ...LAKE_POSTER,
  svgRaw,
  reference: {
    src: reference,
    box: LAKE_POSTER.parts.overview.box,
    caption: 'The supplied reference scan of “Take away our great hotels, fine restaurants, markets and sparkling nightlife and what’s left?”, part of the Tourism B.C. campaign awarded ADCC Gold in 1985. The scan does not establish the original print dimensions.'
  }
})
