// The cards, by series. Like the signs' catalogue (src/signs/catalogue.js): each card names its
// series, each series lists its cards, and nothing here imports a drawing, so it can be tested
// without a browser. Adding a card is a drawing and its parts (see forest-service/), an entry here,
// and a loader in CardsView.jsx.
//
// `view` is the drawing's own viewBox; `page` is the export page in inches; `made` words the
// exports. A drawing too large to fetch on spec says `prefetch: false`.

export const CARECARD_ISSUER = { view: 'government', year: 1989, node: 'ministry-of-health-1976' }
const careCardFormat = {
  series: 'carecard',
  format: 'Reconstructed card',
  when: 'Introduced 1989',
  made: 'vector',
  view: { x: 3, y: 3.06588785, w: 244, h: 153.86822430 },
  page: { w: 85.6 / 25.4, h: 53.98 / 25.4 },
  issuer: CARECARD_ISSUER
}

export const CARD_SERIES = [
  {
    id: 'forest-service',
    title: 'British Columbia Forest Service',
    kind: 'Fire-prevention cards',
    cards: ['england-expects']
  },
  {
    id: 'carecard',
    title: 'Ministry of Health',
    kind: 'Medical Services Plan',
    cards: ['standard-carecard', 'gold-carecard']
  }
]

export const CARDS = {
  'standard-carecard': {
    ...careCardFormat,
    id: 'standard-carecard',
    title: 'Standard CareCard',
    blurb: 'The two-colour CareCard wordmark above the provincial flag and rising sun.'
  },
  'gold-carecard': {
    ...careCardFormat,
    id: 'gold-carecard',
    title: 'Gold CareCard',
    blurb: 'The seniors’ edition pairs a pale wordmark with a gold field and flag.'
  },
  'england-expects': {
    id: 'england-expects',
    series: 'forest-service',
    title: 'England Expects: Prevent Forest Fires',
    blurb: 'Nelson’s call to duty, turned on carelessness with fire.',
    format: 'Card',
    when: 'Undated',
    made: 'vector',
    // 2.3 MB: the Lands Department seal it carries is drawn in 6,567 paths and 5,049 dots.
    prefetch: false,
    view: { x: 0, y: 0, w: 1050, h: 500 },
    // The package's 210 × 100 mm, an export size rather than a measurement of the card.
    page: { w: 8.27, h: 3.94 }
  }
}

export const cardIds = () => CARD_SERIES.flatMap((series) => series.cards)
