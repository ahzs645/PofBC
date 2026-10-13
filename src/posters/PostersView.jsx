// The posters: a shelf (see ShelfView.jsx) over the poster catalogue.

import { ShelfView } from './ShelfView.jsx'
import { POSTERS, SERIES } from './catalogue.js'
import coastalThumb from './coastal-forest/thumbnail.jpg'
import dropThumb from './forest-service/dont-drop-it.svg?url'
import gambleThumb from './forest-service/dont-gamble-with-fire.svg?url'
import rewardThumb from './forest-service/reward-living-forest.svg?url'
import enjoyThumb from './forest-service/enjoy-protect-forests.svg?url'

// Each poster's drawing and parts, fetched when it is opened.
const forestService = (id) => () => import('./forest-service/index.js').then((module) => module.loaderFor(id)())
const LOADERS = {
  'coastal-forest': () => import('./coastal-forest/index.jsx').then((module) => module.load()),
  'dont-drop-it': forestService('dont-drop-it'),
  'dont-gamble-with-fire': forestService('dont-gamble-with-fire'),
  'reward-living-forest': forestService('reward-living-forest'),
  'enjoy-protect-forests': forestService('enjoy-protect-forests')
}

const THUMBNAILS = {
  'coastal-forest': coastalThumb,
  'dont-drop-it': dropThumb,
  'dont-gamble-with-fire': gambleThumb,
  'reward-living-forest': rewardThumb,
  'enjoy-protect-forests': enjoyThumb
}

const postersOf = (series) => series.posters

export const PostersView = () => (
  <ShelfView
    view="posters"
    param="poster"
    title="Posters"
    intro="Open a poster and click any part to see its history."
    noun="poster"
    series={SERIES}
    itemsOf={postersOf}
    items={POSTERS}
    loaders={LOADERS}
    thumbnails={THUMBNAILS}
  />
)
