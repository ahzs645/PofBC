export const ASHTRAY_REGULATIONS = {
  label: 'British Columbia Game Regulations 1961–62, Fish and Game Branch, first foldout',
  href: 'https://a100.gov.bc.ca/pub/acat/documents/r22560/regs_61-62_1348237474410_03f19de84e89ab74e08c6213e7e353100bb0074cd7c725155ed9367b3704a70a.pdf#page=1'
}
export const ASHTRAY_ROAD_MARKER = {
  label: 'Summerland Review, July 5, 1962, PDF page 2',
  href: 'https://static1.squarespace.com/static/5995f4e96b8f5b9ef7c7355f/t/61ff07e33c229f6f8e9b5df0/1644103669635/1962%2BJUL.pdf#page=2'
}

export const ASHTRAY_PANEL = {
  id: 'use-your-ashtray',
  order: ['overview', 'lettering', 'frame'],
  regions: ['lettering', 'frame'],
  parts: {
    overview: {
      box: { x: 0, y: 0, w: 754, h: 227 },
      panel: {
        eyebrow: 'Fire prevention · 1961–62',
        heading: 'Keep B.C. Green— Use Your Ashtray.',
        lede: 'A small two-ink notice sits at the foot of a notes panel in the Fish and Game Branch’s folded regulations.',
        blocks: [
          'The long dash carries the eye from the first line to the instruction below. The Fish and Game Branch identifies itself on the adjoining cover panel.',
          { h: 'The words on the road' },
          'In July 1962 the Summerland Review reported that Ray Williston had stencilled the same words on the Victoria–Sidney Highway to open the Forest Service’s annual road-sign painting program. The article describes a paint gun and stencil. The printed panel supplies the lettering and layout shown here.',
          { sources: [ASHTRAY_REGULATIONS, ASHTRAY_ROAD_MARKER] }
        ]
      }
    },
    lettering: {
      label: 'Italic lettering', hint: 'The two staggered lines', layer: '#ashtray-line-one, #ashtray-line-two',
      box: { x: 50, y: 41, w: 646, h: 155 },
      panel: {
        eyebrow: 'Lettering', heading: 'Two lines of italic type',
        lede: 'The capital K starts close to the left rule. The second line begins beneath B.C., and the descending y carries the full stop close to the right edge.',
        blocks: ['The word outlines follow the printed shapes, including the two stops in B.C., the long dash after Green and the final stop. The typeface and designer are unidentified.']
      }
    },
    frame: {
      label: 'Red frame', hint: 'The narrow rule around the notice', layer: '#ashtray-frame',
      box: { x: 12, y: 13, w: 730, h: 201 },
      panel: {
        eyebrow: 'Printing', heading: 'A single red rule',
        lede: 'Red also marks headings and notices elsewhere on the foldout. Here it encloses the black lettering on all four sides.',
        blocks: ['The red, dark ink and paper colours are sampled from the scan. The drawing smooths the rule and the ink edges. The lightly pink paper ground represents the appearance of this digitized copy.']
      }
    }
  }
}
