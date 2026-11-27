const overview = { x: 0, y: 0, w: 1656, h: 1041 }

const sources = [
  {
    label: 'ADCC archive: the three-ad campaign, 1985 Gold and creative credits',
    href: 'https://theadcc.ca/archive/so-many-of-our-visitors-our-good-ferries-take-away-our-great-hotels_1985_gold_consumer-magazine'
  },
  {
    label: 'ADCC reference scan: Our good ferries',
    href: 'https://theadcc.ca/wp-content/uploads/2022/10/adcc_38308_OBJ-1024x644.jpg'
  }
]

export const FERRIES_POSTER = {
  spotlight: { keep: ['ferry-paper'] },
  order: ['overview', 'photograph', 'headline', 'copy', 'wordmark'],
  regions: ['photograph', 'headline', 'copy', 'wordmark'],
  parts: {
    overview: {
      label: 'Whole advertisement', box: overview,
      story: ['A ferry crosses a warm evening seascape. The headline turns the practical crossing into a promise of enchanted islands.'],
      panel: {
        eyebrow: 'Super, Natural British Columbia · campaign recognised in 1985',
        heading: 'Our good ferries take you to some very enchanted islands.',
        lede: 'One of the three McKim Advertising Vancouver advertisements for Tourism B.C. recognised together with ADCC Gold in 1985.',
        blocks: [
          { facts: [
            ['Publication date', 'Not established for this advertisement; the campaign received its award in 1985'],
            ['Award', 'ADCC Gold, Consumer Magazine Ad, Campaign, 1985'],
            ['Client', 'Tourism B.C.'],
            ['Writing and creative direction', 'Alvin Wasserman'],
            ['Design and art direction', 'Bill Cozens'],
            ['Campaign photographers', 'Peter Thomas, Ed Gifford and Bob Herger; the campaign record does not assign each image individually'],
            ['Agency', 'McKim Advertising (Vancouver)'],
            ['Reconstruction', 'Supplied modern recreated photograph with outlined headline, copy and signature'],
            ['Export size', '16.56 × 10.41 inches; a working size, not measured original print dimensions']
          ] },
          { note: 'This reconstruction combines raster photography and vector lettering. The Original and Overlay controls show the historical scan. The supplied scene is not the historical photograph, and the original typeface is unconfirmed.' },
          { sources }
        ]
      }
    },
    photograph: {
      label: 'The ferry scene', hint: 'A crossing between coastal islands',
      layer: '#ferry-photo', box: { x: 0, y: 108, w: 1656, h: 933 },
      story: ['The small ferry gives the broad water and island silhouettes a sense of scale. It remains visible immediately above the headline.'],
      panel: {
        eyebrow: 'The photograph', heading: 'A journey into the islands',
        lede: 'The supplied ferry.jpeg recreation fills the picture area beneath the narrow copy strip.',
        blocks: [
          'The crop keeps the vessel above the first headline line and preserves the wide evening seascape. The image remains raster photography in the SVG and PDF exports.',
          { note: 'The original campaign credits name Peter Thomas, Ed Gifford and Bob Herger collectively. Those credits describe the historical work and do not identify the maker of this supplied modern recreation.' },
          { sources: [sources[0]] }
        ]
      }
    },
    headline: {
      label: 'The headline', hint: 'Good ferries and enchanted islands',
      layer: '#ferry-headline', hit: 'letters', box: { x: 30, y: 778, w: 1610, h: 258 },
      story: ['The narrower first line, “Our good ferries take you”, sits centred above “to some very enchanted islands.” The close white serif lettering carries the play on ferries and fairies.'],
      panel: {
        eyebrow: 'The headline', heading: 'The crossing becomes a fairy tale',
        lede: 'The original two-line arrangement is rebuilt with closely fitted TeX Gyre Termes Regular glyph outlines.',
        blocks: [
          { facts: [
            ['First line', 'Our good ferries take you'],
            ['Second line', 'to some very enchanted islands.'],
            ['Reconstruction typeface', 'TeX Gyre Termes Regular'],
            ['Original typeface', 'Unconfirmed']
          ] },
          'The lettering is vector geometry, so it remains sharp when enlarged and does not require the font to be installed. The fit is a reconstruction of the scan, not a recovered typesetting master.'
        ]
      }
    },
    copy: {
      label: 'The small copy', hint: 'An island invitation in two columns',
      layer: '#ferry-copy', box: { x: 36, y: 7, w: 1585, h: 92 },
      story: ['The opening question asks whether the reader believes in magic. Islands, artisans and a return ferry extend that fairy-tale language through the two compact columns.'],
      panel: {
        eyebrow: 'The copy strip', heading: 'Do you believe in magic?',
        lede: 'The supplied scan guides the two-column transcription and the small italic minister credit below the right column.',
        blocks: [
          'The reconstruction retains the original wording, including “these many special places”, “Sculptured coastlines” and “tree-lined countryside”. The reply address reads Dept. 0930, 1117 Wharf Street, Victoria, B.C., Canada, V8W 2Z2.',
          { note: 'The scan limits certainty about very small punctuation and letter shapes. Its overall tilt is removed in the clean layout; the Original view retains the supplied evidence.' }
        ]
      }
    },
    wordmark: {
      label: 'The campaign signature', hint: 'Super,Natural British Columbia CANADA',
      layer: '#ferry-wordmark', box: { x: 1123, y: 61, w: 496, h: 34 },
      story: ['The signature closes the right column in closely spaced serif type. This version adds a much smaller CANADA after British Columbia.'],
      panel: {
        eyebrow: 'The campaign', heading: 'A signature for the international reader',
        lede: 'The type-only signature retains the tight comma-to-N spacing and the small CANADA addendum visible on the ferry advertisement.',
        blocks: [
          { links: [
            { label: 'Spring visitors', note: 'The whale advertisement in the same award-winning campaign', to: { view: 'posters', poster: 'super-natural-spring' } },
            { label: 'Take away our great hotels', note: 'The lake advertisement in the same campaign', to: { view: 'posters', poster: 'super-natural-lake' } },
            { label: 'Tourism BC & Destination BC', note: 'The wider tourism identity collection', to: { view: 'gallery', logos: 'tourism-bc-destination-bc' } }
          ] },
          { sources }
        ]
      }
    }
  }
}
