// The posters: a shelf (see ShelfView.jsx) over the poster catalogue.

import { bearAwareDecalSvg, bearAwareWindowId } from '../initiatives/bearAwareArtwork.js'
import { ShelfView } from './ShelfView.jsx'
import { FACETS, POSTERS, SERIES } from './catalogue.js'
import careCardThumb from './carecard/thumbnail.jpg'
import springThumb from './super-natural-spring/thumbnail.jpg'
import tourismFerriesThumb from './super-natural-ferries/thumbnail.jpg'
import tourismLakeThumb from './super-natural-lake/thumbnail.jpg'
import airFacilitiesThumb from './air-facilities-map-1977/thumbnail.jpg'
import coastalThumb from './coastal-forest/thumbnail.jpg'
import ashtrayThumb from './forest-service/use-your-ashtray.svg?url'
import dropThumb from './forest-service/dont-drop-it.svg?url'
import gambleThumb from './forest-service/dont-gamble-with-fire.svg?url'
import rewardThumb from './forest-service/reward-living-forest.svg?url'
import enjoyThumb from './forest-service/enjoy-protect-forests.svg?url'
import beCarefulThumb from './forest-service/be-careful.svg?url'
import coonsAgeThumb from './forest-service/coons-age.thumb.jpg'
import preventFiresThumb from './forest-service/prevent-forest-fires.thumb.jpg'
import matchesThumb from './forest-service/matches-not-for-children.thumb.jpg'
import goFerriesThumb from './bc-ferries/go-bc-ferries.svg?url'
import queenThumb from './bc-ferries/queen-of-sidney.svg?url'
import wildlifeThumb from './wildlife-trees/thumbnail.jpg'
import bewareThumb from './noxious-weeds/beware-these-alien-invaders.thumb.jpg'
import shatteringThumb from './noxious-weeds/shattering-the-environment.thumb.jpg'
import explosionThumb from './noxious-weeds/explosion-in-slow-motion.thumb.jpg'
import expoDavidsonThumb from './expo-86/thumbnail.jpg'
import expoFiorucciThumb from './expo-86/expo-86-fiorucci.thumb.jpg'
import ourBritishColumbiaThumb from './expo-86/our-british-columbia.thumb.jpg'

// Each poster's drawing and parts, fetched when it is opened.
const forestService = (id) => () => import('./forest-service/index.js').then((module) => module.loaderFor(id)())
const bcFerries = (id) => () => import('./bc-ferries/index.js').then((module) => module.loaderFor(id)())
const noxiousWeeds = (id) => () => import('./noxious-weeds/index.js').then((module) => module.loaderFor(id)())
const expo86 = (id) => () => import('./expo-86/index.js').then((module) => module.loaderFor(id)())
const LOADERS = {
  [bearAwareWindowId]: () => import('./bearAwareDecal.js').then(({ loadBearAwareDecal }) => loadBearAwareDecal()),
  'super-natural-spring': () => import('./super-natural-spring/index.js').then((module) => module.load()),
  'super-natural-ferries': () => import('./super-natural-ferries/index.js').then((module) => module.load()),
  'super-natural-lake': () => import('./super-natural-lake/index.js').then((module) => module.load()),
  'air-facilities-map-1977': () => import('./air-facilities-map-1977/index.js').then((module) => module.load()),
  'new-carecard': () => import('./carecard/index.js').then((module) => module.load()),
  'coastal-forest': () => import('./coastal-forest/index.jsx').then((module) => module.load()),
  'use-your-ashtray': forestService('use-your-ashtray'),
  'dont-drop-it': forestService('dont-drop-it'),
  'dont-gamble-with-fire': forestService('dont-gamble-with-fire'),
  'reward-living-forest': forestService('reward-living-forest'),
  'enjoy-protect-forests': forestService('enjoy-protect-forests'),
  'coons-age': forestService('coons-age'),
  'prevent-forest-fires': forestService('prevent-forest-fires'),
  'matches-not-for-children': forestService('matches-not-for-children'),
  'be-careful': forestService('be-careful'),
  'wildlife-trees': () => import('./wildlife-trees/index.js').then((module) => module.load()),
  'beware-these-alien-invaders': noxiousWeeds('beware-these-alien-invaders'),
  'shattering-the-environment': noxiousWeeds('shattering-the-environment'),
  'explosion-in-slow-motion': noxiousWeeds('explosion-in-slow-motion'),
  'go-bc-ferries': bcFerries('go-bc-ferries'),
  'queen-of-sidney': bcFerries('queen-of-sidney'),
  'expo-86-davidson': expo86('expo-86-davidson'),
  'expo-86-fiorucci': expo86('expo-86-fiorucci'),
  'our-british-columbia': expo86('our-british-columbia')
}

const THUMBNAILS = {
  [bearAwareWindowId]: import.meta.env.BASE_URL + bearAwareDecalSvg,
  'super-natural-spring': springThumb,
  'super-natural-ferries': tourismFerriesThumb,
  'super-natural-lake': tourismLakeThumb,
  'air-facilities-map-1977': airFacilitiesThumb,
  'new-carecard': careCardThumb,
  'coastal-forest': coastalThumb,
  'use-your-ashtray': ashtrayThumb,
  'dont-drop-it': dropThumb,
  'dont-gamble-with-fire': gambleThumb,
  'reward-living-forest': rewardThumb,
  'enjoy-protect-forests': enjoyThumb,
  'coons-age': coonsAgeThumb,
  'prevent-forest-fires': preventFiresThumb,
  'matches-not-for-children': matchesThumb,
  'be-careful': beCarefulThumb,
  'wildlife-trees': wildlifeThumb,
  'beware-these-alien-invaders': bewareThumb,
  'shattering-the-environment': shatteringThumb,
  'explosion-in-slow-motion': explosionThumb,
  'go-bc-ferries': goFerriesThumb,
  'queen-of-sidney': queenThumb,
  'expo-86-davidson': expoDavidsonThumb,
  'expo-86-fiorucci': expoFiorucciThumb,
  'our-british-columbia': ourBritishColumbiaThumb
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
