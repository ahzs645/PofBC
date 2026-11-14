// The posters: a shelf (see ShelfView.jsx) over the poster catalogue.

import { ShelfView } from './ShelfView.jsx'
import { FACETS, POSTERS, SERIES } from './catalogue.js'
import coastalThumb from './coastal-forest/thumbnail.jpg'
import dropThumb from './forest-service/dont-drop-it.svg?url'
import gambleThumb from './forest-service/dont-gamble-with-fire.svg?url'
import rewardThumb from './forest-service/reward-living-forest.svg?url'
import enjoyThumb from './forest-service/enjoy-protect-forests.svg?url'
import goFerriesThumb from './bc-ferries/go-bc-ferries.svg?url'
import queenThumb from './bc-ferries/queen-of-sidney.svg?url'
import wildlifeThumb from './wildlife-trees/thumbnail.jpg'
import bewareThumb from './noxious-weeds/beware-these-alien-invaders.thumb.jpg'
import shatteringThumb from './noxious-weeds/shattering-the-environment.thumb.jpg'
import explosionThumb from './noxious-weeds/explosion-in-slow-motion.thumb.jpg'
import expoDavidsonThumb from './expo-86/thumbnail.jpg'

// Each poster's drawing and parts, fetched when it is opened.
const forestService = (id) => () => import('./forest-service/index.js').then((module) => module.loaderFor(id)())
const bcFerries = (id) => () => import('./bc-ferries/index.js').then((module) => module.loaderFor(id)())
const noxiousWeeds = (id) => () => import('./noxious-weeds/index.js').then((module) => module.loaderFor(id)())
const LOADERS = {
  'coastal-forest': () => import('./coastal-forest/index.jsx').then((module) => module.load()),
  'dont-drop-it': forestService('dont-drop-it'),
  'dont-gamble-with-fire': forestService('dont-gamble-with-fire'),
  'reward-living-forest': forestService('reward-living-forest'),
  'enjoy-protect-forests': forestService('enjoy-protect-forests'),
  'wildlife-trees': () => import('./wildlife-trees/index.js').then((module) => module.load()),
  'beware-these-alien-invaders': noxiousWeeds('beware-these-alien-invaders'),
  'shattering-the-environment': noxiousWeeds('shattering-the-environment'),
  'explosion-in-slow-motion': noxiousWeeds('explosion-in-slow-motion'),
  'go-bc-ferries': bcFerries('go-bc-ferries'),
  'queen-of-sidney': bcFerries('queen-of-sidney'),
  // Unlisted (catalogue.js): opened only from its address.
  'expo-86-davidson': () => import('./expo-86/index.js').then((module) => module.loaderFor('expo-86-davidson')())
}

const THUMBNAILS = {
  'coastal-forest': coastalThumb,
  'dont-drop-it': dropThumb,
  'dont-gamble-with-fire': gambleThumb,
  'reward-living-forest': rewardThumb,
  'enjoy-protect-forests': enjoyThumb,
  'wildlife-trees': wildlifeThumb,
  'beware-these-alien-invaders': bewareThumb,
  'shattering-the-environment': shatteringThumb,
  'explosion-in-slow-motion': explosionThumb,
  'go-bc-ferries': goFerriesThumb,
  'queen-of-sidney': queenThumb,
  'expo-86-davidson': expoDavidsonThumb
}

const postersOf = (series) => series.posters

export const PostersView = () => (
  <ShelfView
    view="posters"
    param="poster"
    title="Posters"
    noun="poster"
    series={SERIES}
    itemsOf={postersOf}
    items={POSTERS}
    loaders={LOADERS}
    thumbnails={THUMBNAILS}
    facets={FACETS}
  />
)
