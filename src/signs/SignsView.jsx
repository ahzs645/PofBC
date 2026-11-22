// The signs: a shelf (see src/posters/ShelfView.jsx) over the sign catalogue, so a sign opens on the
// same stage as a poster, with the same hotspots, panels and export.

import { ShelfView } from '../posters/ShelfView.jsx'
import { SIGNS, SIGN_SERIES } from './catalogue.js'
import { FOREST_SERVICE_SIGNS } from './forest-service/signs.js'
import { TOURISM_SIGNS } from './tourism/signs.js'
import { PARKS_SIGNS } from './parks/signs.js'
import lookoutThumb from './forest-service/lookout.svg?url'
import forestClosureThumb from './forest-service/forest-closure.svg?url'
import superNaturalThumb from './tourism/super-natural.svg?url'
import parkSymbolsThumb from './parks/proposed-park-symbols.svg?url'

const fromData = (signs) => (id, drawing) => async () => {
  const { default: svgRaw } = await drawing()
  const { parts, order, regions, spotlight, variations } = signs[id]
  return { svgRaw, parts, order, regions, spotlight, variations }
}
const forestService = fromData(FOREST_SERVICE_SIGNS)
const tourism = fromData(TOURISM_SIGNS)
const parks = fromData(PARKS_SIGNS)

const LOADERS = {
  lookout: forestService('lookout', () => import('./forest-service/lookout.svg?raw')),
  'forest-closure': forestService('forest-closure', () => import('./forest-service/forest-closure.svg?raw')),
  'super-natural': tourism('super-natural', () => import('./tourism/super-natural.svg?raw')),
  'proposed-park-symbols': parks('proposed-park-symbols', () => import('./parks/proposed-park-symbols.svg?raw'))
}

const THUMBNAILS = {
  lookout: lookoutThumb,
  'forest-closure': forestClosureThumb,
  'super-natural': superNaturalThumb,
  'proposed-park-symbols': parkSymbolsThumb
}

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
