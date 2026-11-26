const overview = { x: 0, y: 0, w: 891, h: 1215 }

const cardLink = (variant) => ({
  label: variant === 'gold' ? 'Gold CareCard' : 'Standard CareCard',
  to: { view: 'cards', card: variant + '-carecard' }
})

export const CARECARD_POSTER = {
  spotlight: { keep: ['paper'] },
  order: ['overview', 'cards', 'photograph', 'ministry'],
  regions: ['cards', 'photograph', 'ministry'],
  parts: {
    overview: {
      story: ['The headline announces a new card. Across the foot of the page, “Carry it in good health” turns its introduction into a direct invitation to the reader.'],
      label: 'Whole advertisement', box: overview,
      panel: {
        eyebrow: 'Ministry of Health · 1989',
        heading: 'BC’s New CareCard.',
        lede: 'Two cards introduce the Medical Services Plan’s new identification card. The seniors’ edition overlaps the lower right edge of the standard card.',
        blocks: [
          { facts: [['Published', 'Gulf Islands Driftwood, 2 August 1989, page B14'], ['Print size', '11 × 15 inches, fitted to the supplied scan']] },
          { links: [cardLink('standard'), cardLink('gold')] },
          { figure: 'overlap', alt: 'Registered overlay showing shared ink and differences between the scan and print reconstruction', caption: 'Ink overlap at the screenshot’s native scale. Open the proof to read the measurements.' },
          { sources: [{ label: 'Gulf Islands Driftwood · page B14', href: 'https://saltspringarchives.com/driftwood/1989/v30n31Aug2-1989B.pdf#page=14' }] }
        ]
      }
    },
    cards: {
      story: ['The standard card sits above the centre column. The seniors’ card starts lower, drawing the eye to the explanation of which two cards it would replace.'],
      label: 'The two CareCards', hint: 'Standard and Gold specimens', layer: '#standard-card, #gold-card',
      box: { x: 308, y: 400, w: 545, h: 283 },
      boxes: [{ x: 309, y: 402, w: 274, h: 173 }, { x: 578, y: 509, w: 274, h: 173 }],
      panel: {
        eyebrow: 'Medical Services Plan', heading: 'Standard and Gold',
        lede: 'The two catalogue drawings carry the sample inscription from the launch ad. The Gold card uses light overprinting for its number and name in the newspaper edition.',
        blocks: [{ links: [cardLink('standard'), cardLink('gold')] }]
      }
    },
    photograph: {
      story: ['Dueck’s photograph interrupts the first column. The last paragraph wraps beside his portrait and his signature closes the message.'],
      label: 'The minister', hint: 'Peter A. Dueck', layer: '#portrait',
      box: { x: 46, y: 822, w: 112, h: 148 },
      panel: {
        eyebrow: 'The minister’s message', heading: 'Peter A. Dueck',
        lede: 'The newspaper identifies Dueck as Minister of Health and Minister Responsible for Seniors. His closing paragraph runs alongside his portrait.',
        blocks: [{ facts: [['Portrait', '112 × 148 pixels, cropped from the supplied scan'], ['Printed resolution', '81 ppi on the 11 × 15 inch page']] }]
      }
    },
    ministry: {
      story: ['Below the seniors’ column, the flag and the three-line ministry name sign the advertisement on behalf of the Province.'],
      label: 'Ministry signature', hint: 'The provincial flag and ministry name', layer: '#issuer',
      box: { x: 575, y: 969, w: 184, h: 56 },
      panel: {
        eyebrow: 'Province of British Columbia', heading: 'Ministry of Health',
        lede: 'The flag uses the twelve paths from the project’s flag generator. The newspaper edition reserves the sun in paper, and the colour edition uses the generator’s official palette.'
      }
    }
  }
}
