// The signs: a shelf (see src/posters/ShelfView.jsx) over the sign catalogue, so a sign opens on the
// same stage as a poster, with the same hotspots, panels and export.

import { ShelfView } from '../posters/ShelfView.jsx'
import { SIGNS, SIGN_SERIES } from './catalogue.js'
import { FOREST_SERVICE_SIGNS } from './forest-service/signs.js'
import { TOURISM_SIGNS } from './tourism/signs.js'
import lookoutThumb from './forest-service/lookout.svg?url'
import superNaturalThumb from './tourism/super-natural.svg?url'

const fromData = (signs) => (id, drawing) => async () => {
  const { default: svgRaw } = await drawing()
  const { parts, order, regions, spotlight } = signs[id]
  return { svgRaw, parts, order, regions, spotlight }
}
const forestService = fromData(FOREST_SERVICE_SIGNS)
const tourism = fromData(TOURISM_SIGNS)

const LOADERS = {
  lookout: forestService('lookout', () => import('./forest-service/lookout.svg?raw')),
  'super-natural': tourism('super-natural', () => import('./tourism/super-natural.svg?raw'))
}

const THUMBNAILS = { lookout: lookoutThumb, 'super-natural': superNaturalThumb }

const signsOf = (series) => series.signs

export const SignsView = () => (
  <ShelfView
    view="signs"
    param="sign"
    title="Signs"
    noun="sign"
    series={SIGN_SERIES}
    itemsOf={signsOf}
    items={SIGNS}
    loaders={LOADERS}
    thumbnails={THUMBNAILS}
  />
)
