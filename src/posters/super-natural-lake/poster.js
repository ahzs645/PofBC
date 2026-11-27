const overview = { x: 0, y: 0, w: 1112, h: 1081 }

const sources = [
  {
    label: 'ADCC archive: the three-ad campaign, 1985 Gold and creative credits',
    href: 'https://theadcc.ca/archive/so-many-of-our-visitors-our-good-ferries-take-away-our-great-hotels_1985_gold_consumer-magazine'
  },
  {
    label: 'ADCC reference scan: Take away our great hotels',
    href: 'https://theadcc.ca/wp-content/uploads/2022/10/adcc_38309_OBJ-1024x995.jpg'
  }
]

export const LAKE_POSTER = {
  spotlight: { keep: ['lake-paper'] },
  order: ['overview', 'photograph', 'headline', 'copy', 'wordmark'],
  regions: ['photograph', 'headline', 'copy', 'wordmark'],
  parts: {
    overview: {
      label: 'Whole advertisement', box: overview,
      story: ['A lone kayaker occupies a quiet opening on a mountain lake. The headline takes away the city’s attractions and leaves the reader with this scene.'],
      panel: {
        eyebrow: 'Super, Natural British Columbia · campaign recognised in 1985',
        heading: 'Take away our great hotels, fine restaurants, markets and sparkling nightlife and what’s left?',
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
            ['Export size', '11.12 × 10.81 inches; a working size, not measured original print dimensions']
          ] },
          { note: 'This reconstruction combines raster photography and vector lettering. The Original and Overlay controls show the historical scan. The supplied scene is not the historical photograph, and the original typeface is unconfirmed.' },
          { sources }
        ]
      }
    },
    photograph: {
      label: 'The lake scene', hint: 'A kayaker beneath a mountain wall',
      layer: '#lake-photo', box: { x: 0, y: 121, w: 1112, h: 960 },
      story: ['Mist and reflected light open the water around a small kayaker, beneath the dark trees and mountain. The space above the headline is central to the composition.'],
      panel: {
        eyebrow: 'The photograph', heading: 'What remains after the city',
        lede: 'The supplied Gemini-generated lake recreation fills the picture area, with the small boat kept clear of the headline.',
        blocks: [
          { facts: [
            ['Supplied scene', 'Gemini_Generated_Image_jeaoa0jeaoa0jeao.jpeg'],
            ['Image status', 'Modern recreation supplied for this reconstruction']
          ] },
          'The copy names kayaking at Emerald Lake in the Rockies. The reconstruction follows the supplied scene and composition; it does not establish an independently verified camera location.',
          { note: 'Peter Thomas, Ed Gifford and Bob Herger are credited collectively for the historical campaign. The archive does not assign this individual photograph, and those credits do not apply to the supplied recreated image.' },
          { sources: [sources[0]] }
        ]
      }
    },
    headline: {
      label: 'The headline', hint: 'The question across the lake',
      layer: '#lake-headline', hit: 'letters', box: { x: 15, y: 810, w: 1088, h: 263 },
      story: ['Three centred lines list hotels, restaurants, markets and nightlife before asking “what’s left?” The quiet lake supplies the answer.'],
      panel: {
        eyebrow: 'The headline', heading: 'A question the photograph answers',
        lede: 'The three original line breaks, closely spaced serif lettering and apostrophe in “what’s” are retained.',
        blocks: [
          { facts: [
            ['First line', 'Take away our great hotels,'],
            ['Second line', 'fine restaurants, markets and'],
            ['Third line', 'sparkling nightlife and what’s left?'],
            ['Reconstruction typeface', 'TeX Gyre Termes Regular'],
            ['Original typeface', 'Unconfirmed']
          ] },
          'The headline is rebuilt from glyph outlines. Its increasing line widths and tight leading follow the reference while keeping the final question mark inside the clean page.'
        ]
      }
    },
    copy: {
      label: 'The small copy', hint: 'City holidays and getting away',
      layer: '#lake-copy', box: { x: 8, y: 5, w: 1086, h: 110 },
      story: ['The writer begins with affordable city vacations and then gets carried away by the thought of leaving them. A separate address block sits at the top right.'],
      panel: {
        eyebrow: 'The copy strip', heading: 'It’s almost embarrassing',
        lede: 'The asymmetric header is rebuilt as a broad five-line paragraph, a narrow address block and a small italic minister credit at lower left.',
        blocks: [
          'The transcription preserves “off season”, “night spots”, the Inside Passage ferry and Emerald Lake. The address reads Department 0804, 1117 Wharf Street, Victoria, British Columbia, Canada V8W 2Z2.',
          'The scanned paragraph breaks “wherever” across two lines as “wher-” and “ever”. That line-end division is a typesetting feature rather than a different word.',
          { note: 'The clean header removes the scan’s tilt. The supplied original remains available for the small punctuation and letterforms that the scan cannot resolve fully.' }
        ]
      }
    },
    wordmark: {
      label: 'The campaign signature', hint: 'Super,Natural British Columbia',
      layer: '#lake-wordmark', box: { x: 611, y: 78, w: 430, h: 32 },
      story: ['The serif signature sits below the address, beginning to the left of that column. It completes the white band while leaving the photograph uninterrupted.'],
      panel: {
        eyebrow: 'The campaign', heading: 'Super, Natural British Columbia',
        lede: 'The signature follows this advertisement’s type-only treatment and tight spacing after the comma.',
        blocks: [
          { links: [
            { label: 'Spring visitors', note: 'The whale advertisement in the same award-winning campaign', to: { view: 'posters', poster: 'super-natural-spring' } },
            { label: 'Our good ferries', note: 'The island-crossing advertisement in the same campaign', to: { view: 'posters', poster: 'super-natural-ferries' } },
            { label: 'Tourism BC & Destination BC', note: 'The wider tourism identity collection', to: { view: 'gallery', logos: 'tourism-bc-destination-bc' } }
          ] },
          { sources }
        ]
      }
    }
  }
}
