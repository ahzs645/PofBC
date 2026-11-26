// The signs: a shelf (see src/posters/ShelfView.jsx) over the sign catalogue, so a sign opens on the
// same stage as a poster, with the same hotspots, panels and export.

import { bearAwareWindowId, bearAwareWindowScan } from '../initiatives/bearAwareArtwork.js'
import { ShelfView } from '../posters/ShelfView.jsx'
import { SIGNS, SIGN_SERIES } from './catalogue.js'
import { FOREST_SERVICE_SIGNS } from './forest-service/signs.js'
import { FISH_WILDLIFE_SIGNS } from './fish-wildlife/signs.js'
import cheakamusThumb from './fish-wildlife/cheakamus.svg?url'
import cheakamusReference from './fish-wildlife/cheakamus.reference.png?url'
import { ENTRY_SIGNS, entryReconstructionFile } from './entering-bc/signs.js'
import { TOURISM_SIGNS } from './tourism/signs.js'
import { PARKS_SIGNS } from './parks/signs.js'
import fireDayReference from './forest-service/fire-day.reference.png?url'
import fireDayThumb from './forest-service/fire-day.svg?url'
import lookoutThumb from './forest-service/lookout.svg?url'
import forestClosureThumb from './forest-service/forest-closure.svg?url'
import superNaturalThumb from './tourism/super-natural.svg?url'
import borderedThumb from './tourism/super-natural-bordered.svg?url'
import borderedPhoto from '../../artwork/signs/super-natural-bordered/source.png?url'
import borderedReference from './tourism/super-natural-bordered.reference.png?url'
import borderedOverlap from './tourism/super-natural-bordered.overlap.png?url'
import parkSymbolsThumb from './parks/proposed-park-symbols.svg?url'

const fromData = (signs) => (id, drawing, reference, figures) => async () => {
  const { default: svgRaw } = await drawing()
  const { parts, order, regions, spotlight, variations } = signs[id]
  return { svgRaw, parts, order, regions, spotlight, variations, reference, figures }
}
const forestService = fromData(FOREST_SERVICE_SIGNS)
const fishWildlife = fromData(FISH_WILDLIFE_SIGNS)
const tourism = fromData(TOURISM_SIGNS)
const parks = fromData(PARKS_SIGNS)

const entryDrawing = fromData(ENTRY_SIGNS)
const entryRaw = import.meta.glob('./entering-bc/*.svg', { query: '?raw' })
const entryFiles = Object.keys(ENTRY_SIGNS).map((id) => [id, `./entering-bc/${id}.svg`])

const LOADERS = {
  [bearAwareWindowId]: () => import('./bearAwareWindow.js').then(({ loadBearAwareWindow }) => loadBearAwareWindow()),
  ...Object.fromEntries(entryFiles.map(([id, file]) => [id, entryDrawing(id, entryRaw[file])])),
  'fire-day': forestService('fire-day', () => import('./forest-service/fire-day.svg?raw'), {
    src: fireDayReference,
    box: SIGNS['fire-day'].view,
    caption: 'Powell River Digester, July 1938. The four corners of the photographed panel are aligned to the drawing.'
  }),
  lookout: forestService('lookout', () => import('./forest-service/lookout.svg?raw')),
  'forest-closure': forestService('forest-closure', () => import('./forest-service/forest-closure.svg?raw')),
  'cheakamus-notice-to-anglers': fishWildlife('cheakamus-notice-to-anglers', () => import('./fish-wildlife/cheakamus.svg?raw'), {
    src: cheakamusReference,
    box: SIGNS['cheakamus-notice-to-anglers'].view,
    caption: 'The supplied photograph, aligned to the board. People in the foreground obscure parts of the notice.'
  }),
  'super-natural': tourism('super-natural', () => import('./tourism/super-natural.svg?raw')),
  'super-natural-bordered': tourism('super-natural-bordered', () => import('./tourism/super-natural-bordered.svg?raw'), {
    src: borderedReference,
    box: SIGNS['super-natural-bordered'].view,
    caption: 'This view straightens the photographed board. The pink overlay above shows the drawing at the original camera angle.'
  }, { photo: borderedPhoto, overlap: borderedOverlap }),
  'proposed-park-symbols': parks('proposed-park-symbols', () => import('./parks/proposed-park-symbols.svg?raw'))
}

const THUMBNAILS = {
  [bearAwareWindowId]: import.meta.env.BASE_URL + bearAwareWindowScan,
  ...Object.fromEntries(entryFiles.map(([id]) => [id, `${import.meta.env.BASE_URL}${entryReconstructionFile(id)}`])),
  'fire-day': fireDayThumb,
  lookout: lookoutThumb,
  'forest-closure': forestClosureThumb,
  'super-natural': superNaturalThumb,
  'super-natural-bordered': borderedThumb,
  'cheakamus-notice-to-anglers': cheakamusThumb,
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
