// The cards: a shelf (see src/posters/ShelfView.jsx) over the card catalogue, so a card opens on the
// same stage as a poster or a sign, with the same hotspots, panels, story and export.

import { ShelfView } from '../posters/ShelfView.jsx'
import { CARECARDS } from './carecard/cards.js'
import { CARDS, CARD_SERIES } from './catalogue.js'
import { FOREST_SERVICE_CARDS } from './forest-service/cards.js'
// The card's drawing is 2.3 MB, so its shelf picture is a small raster of it.
import englandExpectsThumb from './forest-service/england-expects.thumb.jpg'

const fromData = (cards) => (id, drawing) => async () => {
  const { default: svgRaw } = await drawing()
  const { parts, order, regions, spotlight, variations } = cards[id]
  return { svgRaw, parts, order, regions, spotlight, variations }
}
const forestService = fromData(FOREST_SERVICE_CARDS)

const careCardUrl = (file) => `${import.meta.env.BASE_URL}cards/carecard/${file}`
const loadCareCard = (variant) => async () => {
  const response = await fetch(careCardUrl(`${variant}-card.svg`))
  if (!response.ok) throw new Error(`CareCard drawing: ${response.status}`)
  const svgRaw = await response.text()
  return { ...CARECARDS[`${variant}-carecard`], svgRaw, editorHref: careCardUrl(`editor.html#${variant}`) }
}

const LOADERS = {
  'standard-carecard': loadCareCard('standard'),
  'gold-carecard': loadCareCard('gold'),
  'england-expects': forestService('england-expects', () => import('./forest-service/england-expects.svg?raw'))
}

const THUMBNAILS = {
  'england-expects': englandExpectsThumb,
  'standard-carecard': careCardUrl('standard-card.svg'),
  'gold-carecard': careCardUrl('gold-card.svg')
}

const cardsOf = (series) => series.cards

export const CardsView = () => (
  <ShelfView
    view="cards"
    param="card"
    title="Cards"
    noun="card"
    series={CARD_SERIES}
    itemsOf={cardsOf}
    items={CARDS}
    loaders={LOADERS}
    thumbnails={THUMBNAILS}
  />
)
