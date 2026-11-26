import { ShelfView } from '../posters/ShelfView.jsx'
import thumbnail from './i-heart-bc-parks.svg?url'
import svgRaw from './i-heart-bc-parks.svg?raw'
import photoCrop from './i-heart-bc-parks-reference.webp'

const id = 'i-heart-bc-parks'
const view = { x: 0, y: 0, w: 740, h: 114 }
const series = [{ id: 'bc-parks', title: 'BC Parks', kind: 'Outreach', stickers: [id] }]
const itemsOf = (entry) => entry.stickers
const thumbnails = { [id]: thumbnail }
const items = {
  [id]: {
    id, series: 'bc-parks', title: 'I ♥ BC PARKS', format: 'Vehicle sticker',
    when: 'Undated',
    made: 'vector', view, page: { w: 7.4, h: 1.14 }
  }
}

const sources = [
  { label: 'Becoming Design Office, photograph of the vehicle sticker', href: 'https://cdn.prod.website-files.com/60d2303d770c7e4f4545cdd3/63bf52089924f4e6821c2222_Image-Right-Align-3.avif' },
  { label: 'Becoming’s BC Parks case study and brand guide excerpts', href: 'https://www.wearebecoming.ca/work/bc-parks' }
]

const parts = {
  overview: {
    label: 'Whole sticker', box: view, pad: 0.05,
    panel: {
      eyebrow: 'BC Parks outreach', heading: 'I ♥ BC PARKS',
      lede: 'A red heart sits between the I and BC PARKS. The white edge follows the outlines of the letters across the back of a vehicle.',
      blocks: [
        { facts: [
          ['Artwork', 'Vector reconstruction of the horizontal sticker'],
          ['Reference', 'Vehicle photograph published by Becoming Design Office'],
          ['Size', 'Original dimensions unknown. The export uses a proportional 7.4 × 1.14 inch page.']
        ] },
        { note: 'The photograph was cropped and its baseline levelled before the contours were fitted with curves. The brand guide also shows a stacked arrangement.' },
        { sources },
        { links: [{ label: 'BC Parks logos', to: { view: 'gallery', logos: 'bc-parks' } }] }
      ]
    }
  },
  lettering: {
    label: 'Lettering', box: { x: 22, y: 22, w: 698, h: 75 }, pad: 0.06,
    layer: '#sticker-letters', hit: 'shape',
    panel: {
      eyebrow: 'Lettering', heading: 'Eight rounded capitals',
      lede: 'The narrow I and the broad, closely spaced capitals of PARKS are drawn from the photograph. Each letter has its own editable outline.',
      blocks: [{ note: 'The source does not identify a typeface.' }]
    }
  },
  heart: {
    label: 'Heart', box: { x: 84, y: 20, w: 82, h: 74 }, pad: 0.18, layer: '#sticker-heart',
    panel: {
      eyebrow: 'Symbol', heading: 'The heart',
      lede: 'Two rounded lobes meet above a low, curved point. The heart reaches just above and below the neighbouring I.',
      blocks: [{ palette: [{ name: 'Red sampled from the photograph', value: '#F4646B' }] }]
    }
  }
}

const loaders = {
  [id]: async () => ({
    svgRaw, parts, order: ['overview', 'lettering', 'heart'], regions: ['lettering', 'heart'],
    spotlight: { keep: ['sticker-backing'] }, reference: { src: photoCrop, box: view, caption: 'Becoming’s vehicle photograph, cropped and levelled.' }
  })
}

export const StickersView = () => (
  <ShelfView view="stickers" param="sticker" title="Stickers" noun="sticker"
    series={series} itemsOf={itemsOf} items={items} loaders={loaders} thumbnails={thumbnails} />
)
