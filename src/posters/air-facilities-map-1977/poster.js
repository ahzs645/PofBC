const overview = { x: 0, y: 0, w: 1000, h: 1500 }
const sources = [
  { label: 'Photographed 1977/78 front cover (source photograph)', href: 'https://i.ebayimg.com/images/g/NFQAAOSwSZlmYOzj/s-l1600.webp' },
  { label: 'Maureen Wilson, Selected Maps of British Columbia Published During 1977 and 1978, BC Studies 41 (Spring 1979), p. 113', href: 'https://ojs.library.ubc.ca/index.php/bcstudies/article/download/1014/1052/4247#page=1' },
  { label: 'Reverse of the map (supplied source lead; not independently retrieved)', href: 'https://i.ebayimg.com/images/g/rjQAAOSw7nlmYOzl/s-l1600.webp' }
]
export const AIR_FACILITIES_POSTER = {
  spotlight: { keep: ['air-paper'] },
  order: ['overview', 'edition', 'headline', 'photograph', 'wordmark'],
  regions: ['edition', 'headline', 'photograph', 'wordmark'],
  parts: {
    overview: {
      label: 'Whole map cover', box: overview,
      story: ['A small aircraft above a snowy mountain landscape carries an early example of the Super, Natural tourism identity onto an aviation publication.'],
      panel: { eyebrow: 'Aviation publications · 1977/78', heading: 'Air Facilities Map', lede: 'A map cover from the British Columbia Aviation Council, with an early stacked Super, Natural signature.', blocks: [
        { facts: [['Edition printed on cover', '1977/78'], ['Bibliographic publication year', '1977'], ['Publisher', 'British Columbia Aviation Council, Vancouver'], ['Map scale', '1:1,900,800 (bibliography; the map interior is not reconstructed)'], ['Medium', 'Mixed: modern recreated raster scene and editable outlined lettering'], ['Working export size', '10 × 15 in; proportions estimated from a photographed cover']] },
        { note: 'The original photograph, exact print dimensions, designer, original typeface and precise ink colours remain unverified. The image layer is the supplied Gemini-generated reconstruction, not an archival photograph. The reverse was provided as a link but was not independently retrieved.' }, { sources }
      ] }
    },
    edition: {
      label: 'The edition', hint: '1977/78 in the upper-right corner', layer: '#air-date', box: { x: 880, y: 25, w: 90, h: 45 },
      story: ['The small printed edition label gives the cover its own date evidence, separate from the bibliographic publication year.'],
      panel: { eyebrow: 'Date evidence', heading: '1977/78', lede: 'The edition is printed on the upper-right of the photographed cover.', blocks: [{ facts: [['Cover', '1977/78'], ['Bibliographic record', '1977']] }, { sources: [sources[0], sources[1]] }] }
    },
    headline: {
      label: 'The map title', hint: 'Dark serif lettering with a double outline', layer: '#air-title', box: { x: 30, y: 123, w: 940, h: 136 },
      story: ['The large outlined serif title identifies the object as a map, rather than a tourism magazine advertisement.'],
      panel: { eyebrow: 'Typography', heading: 'Air Facilities Map', lede: 'The headline is rebuilt from outlined URW Bookman Demi glyphs with a dark outer keyline and narrow cream separation.', blocks: [{ note: 'The source lettering has rounded terminals suggestive of a period face such as ITC Souvenir. Bookman is a substitute, not an identification; the letters and spacing can be refined from a better scan.' }] }
    },
    photograph: {
      label: 'The aircraft and mountains', hint: 'An aircraft above a snow-streaked landscape', layer: '#air-photo', box: { x: 40, y: 334, w: 914, h: 1010 },
      story: ['The aircraft appears in the upper right, while ridges and snow fill the lower half of the cover behind the tourism signature.'],
      panel: { eyebrow: 'Photographic scene', heading: 'Flying over British Columbia', lede: 'The supplied modern image is placed in the panel measured from the rectified original cover.', blocks: [{ facts: [['Scene file', 'Gemini_Generated_Image_m0cc9fm0cc9fm0cc.jpeg'], ['Status', 'Modern generated recreation; not the original photograph']] }, { note: 'The aircraft details and mountains differ from the historical print. The location, original photographer and aircraft identity are not established.' }] }
    },
    wordmark: {
      label: 'The early stacked wordmark', hint: 'Super, Natural / British Columbia, Canada.', layer: '#air-wordmark', box: { x: 175, y: 1005, w: 680, h: 312 },
      story: ['Two closely spaced lines of cream lettering and a smaller geographic line occupy the lower portion of the photograph.'],
      panel: { eyebrow: 'Early tourism identity', heading: 'Super, Natural British Columbia, Canada.', lede: 'The large stacked letters and comma are constructed as independent cubic outlines; the smaller geographic line uses outlined Bookman Light as an approximate substitute.', blocks: [{ note: 'This is evidence of the identity appearing on an aviation publication, not evidence that the later advertising campaign had already begun.' }, { links: [
        { label: 'Tourism BC & Destination BC', note: 'The wider provincial tourism identity collection', to: { view: 'gallery', logos: 'tourism-bc-destination-bc' } },
        { label: 'Spring visitors', note: 'Later tourism advertising with related wording, not the same campaign', to: { view: 'posters', poster: 'super-natural-spring' } },
        { label: 'Super, Natural welcome sign', note: 'A different arrangement of the provincial tourism phrase', to: { view: 'signs', sign: 'super-natural' } }
      ] }, { sources: [sources[0], sources[1]] }] }
    }
  }
}
