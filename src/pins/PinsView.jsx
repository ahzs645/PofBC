// The pins and buttons: a shelf (see src/posters/ShelfView.jsx) over the pin catalogue, so a pin
// opens on the same stage as a poster or a sign, with the same hotspots, panels, story and export.
//
// A pin with a construction recipe (construction.js) also gets a 3D view of the object, loaded
// only when it is opened (PinModel.jsx), so the shelf does not carry three.js.
//
// The Interior University Society's drawings are not copied here: they are fetched from where the
// gallery serves them (public/unbc-origins/svg/), and their ids prefixed on the way in.

import { lazy } from 'react'
import { ShelfView } from '../posters/ShelfView.jsx'
import { PINS, PIN_SERIES } from './catalogue.js'
import { INTERIOR_UNIVERSITY_PINS } from './interior-university/pins.js'
import { NOVELTY_PINS } from './novelty/pins.js'
import { FOREST_BRANCH_PINS } from './forest-branch/pins.js'
import { prefixIds } from './prefixIds.js'
import welcomeThumb from './novelty/welcome-bc-pattison.svg?url'
import campfiresThumb from './forest-branch/forest-branch-campfires.svg?url'

const BASE = import.meta.env?.BASE_URL ?? '/'
const served = (file) => `${BASE}unbc-origins/svg/${file}`

const PinModel = lazy(() => import('./PinModel.jsx'))

const fromData = (pins) => (id, drawing) => async () => {
  const svgRaw = await drawing()
  const { parts, order, regions, spotlight, variations, construction } = pins[id]
  return { svgRaw, parts, order, regions, spotlight, variations, ...(construction ? { construction, model: PinModel } : {}) }
}

const society = (id) => {
  const { file, prefix } = INTERIOR_UNIVERSITY_PINS[id]
  return fromData(INTERIOR_UNIVERSITY_PINS)(id, async () => {
    const response = await fetch(served(file))
    if (!response.ok) throw new Error(`${file}: ${response.status}`)
    return prefixIds(await response.text(), prefix)
  })
}
const novelty = fromData(NOVELTY_PINS)
const forestBranch = fromData(FOREST_BRANCH_PINS)

const LOADERS = {
  'ius-enamel-pin': society('ius-enamel-pin'),
  'northern-u-button': society('northern-u-button'),
  'say-yes-button': society('say-yes-button'),
  'welcome-bc-pattison': novelty('welcome-bc-pattison', () => import('./novelty/welcome-bc-pattison.svg?raw').then((module) => module.default)),
  'forest-branch-campfires': forestBranch('forest-branch-campfires', () => import('./forest-branch/forest-branch-campfires.svg?raw').then((module) => module.default))
}

const THUMBNAILS = {
  ...Object.fromEntries(Object.entries(INTERIOR_UNIVERSITY_PINS).map(([id, { file }]) => [id, served(file)])),
  'welcome-bc-pattison': welcomeThumb,
  'forest-branch-campfires': campfiresThumb
}

const pinsOf = (series) => series.pins

export const PinsView = () => (
  <ShelfView
    view="pins"
    param="pin"
    title="Pins"
    noun="pin"
    series={PIN_SERIES}
    itemsOf={pinsOf}
    items={PINS}
    loaders={LOADERS}
    thumbnails={THUMBNAILS}
  />
)
