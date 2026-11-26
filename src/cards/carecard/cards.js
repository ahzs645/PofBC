import { CARDS, CARECARD_ISSUER } from '../catalogue.js'

const launch = {
  label: 'Ministry of Health, CareCard launch advertisement, 2 August 1989, page B14',
  href: 'https://saltspringarchives.com/driftwood/1989/v30n31Aug2-1989B.pdf'
}

function careCard(id) {
  const card = CARDS[id]
  return {
    parts: {
      overview: {
        label: 'Whole card',
        box: card.view,
        panel: {
          eyebrow: 'Medical Services Plan',
          heading: card.title,
          lede: card.blurb,
          blocks: [
            { links: [{ label: 'BC’s New CareCard.', note: 'The 1989 launch advertisement', to: { view: 'posters', poster: 'new-carecard', part: 'cards' } }, { label: 'Ministry of Health', note: 'Issuing ministry at the 1989 launch', to: CARECARD_ISSUER }] },
            { facts: [['Artwork', 'Archival reconstruction'], ['Template size', '85.60 × 53.98 mm']] },
            { sources: [launch] }
          ]
        },
        story: [card.blurb],
        storySources: [launch]
      },
      fields: {
        label: 'Sample fields',
        box: { x: 20, y: 76, w: 183, h: 75 },
        layer: '#number-label, #sample-number, #date-label, #birth-date, #sample-name',
        panel: {
          eyebrow: 'Specimen template',
          heading: 'Name, date and number',
          lede: 'Open the template to edit the fictional sample fields, save the SVG or print it at card size.'
        },
        story: ['The template keeps the grouped number near the centre and places the birth date and name along the lower edge.']
      }
    },
    order: ['overview', 'fields'],
    regions: ['fields']
  }
}

export const CARECARDS = {
  'standard-carecard': careCard('standard-carecard'),
  'gold-carecard': careCard('gold-carecard')
}
