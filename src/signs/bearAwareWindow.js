import {
  bearAwareReport, bearAwareTitle, bearAwareWindowScan, bearAwareWindowSvg, bearAwareWindowTitle, bearAwareWindowView
} from '../initiatives/bearAwareArtwork.js'

const titleAndPaw = 'ellipse, svg > g[aria-label$="letter master"], svg > g > g:is([aria-label="B"], [aria-label="R"], [aria-label="Bear paw and five claws"])'
const sponsors = '[aria-label="Friends of Mt. Revelstoke & Glacier crest"], [aria-label^="Columbia Basin"], [aria-label="Fish & Wildlife"], [aria-label="Compensation Program"], [aria-label="Sponsored"], [aria-label="By"], [aria-label="BC Hydro historic wordmark"], [aria-label="BC Environment flag wordmark"]'

export const bearAwareWindow = {
  order: ['overview', 'oval', 'sponsors'],
  regions: ['oval', 'sponsors'],
  spotlight: { keep: [] },
  parts: {
    overview: {
      label: 'Whole window sign', box: bearAwareWindowView,
      story: ['Revelstoke’s 1997 campaign gave this window sign to residents and businesses that met its Bear Aware checklist criteria. Displaying it showed neighbours and customers that the property was taking part.'],
      panel: {
        eyebrow: bearAwareTitle + ' · 1997',
        heading: bearAwareWindowTitle,
        lede: 'Revelstoke residents and businesses could earn this window sign by meeting the campaign’s Bear Aware checklist criteria.',
        blocks: [
          { facts: [['Documented', '1997 Final Report, PDF page 27'], ['Artwork', 'Modern SVG reconstruction'], ['Export size', '7.64 × 10 inches, set from the SVG proportions']] },
          { downloads: [
            { label: 'Download original scan', file: bearAwareWindowScan },
            { label: 'Download reconstructed SVG', file: bearAwareWindowSvg }
          ] },
          { note: 'The scan preserves the original lettering and sponsor marks. The vector redraws them from the scan. The original print dimensions are unknown.' },
          { sources: [{ label: '1997 Final Report, PDF page 27', href: bearAwareReport + '#page=27' }] }
        ]
      }
    },
    oval: {
      label: 'Oval and paw', hint: 'Four lines of serif lettering above a five-clawed paw',
      story: ['Oversized serif lettering fills the oval. The paw and its five claws repeat the symbol printed beside the checklist headings.'],
      layer: titleAndPaw, box: { x: 39, y: 50, w: 709, h: 758 },
      boxes: [{ x: 44, y: 53, w: 689, h: 656 }],
      panel: {
        eyebrow: 'Campaign artwork', heading: 'The oval and paw',
        lede: 'The sign sets its four words inside a heavy oval. A five-clawed paw sits beneath the lettering.',
        blocks: ['The reconstruction uses a clean ellipse, custom letter shapes and manually redrawn paw curves.']
      }
    },
    sponsors: {
      label: 'Sponsor artwork', hint: 'Four marks around the sponsor credit',
      story: ['The lower margin names the campaign’s sponsors in four different marks. The report’s scan preserves details such as the trees in the Friends crest and the lettering of the two provincial signatures.'],
      layer: sponsors, box: { x: 35, y: 713, w: 715, h: 280 },
      boxes: [{ x: 35, y: 800, w: 715, h: 193 }, { x: 617, y: 713, w: 128, h: 87 }],
      panel: {
        eyebrow: 'Sponsor artwork', heading: 'The organizations named on the sign',
        lede: 'Friends of Mt. Revelstoke & Glacier, the Columbia Basin Fish & Wildlife Compensation Program, BC Hydro and BC Environment appear below and beside the oval.',
        blocks: ['The reconstruction simplifies the crest, sponsor lettering and small graphic details. Use the original scan to see how the marks were printed.']
      }
    }
  }
}

export const loadBearAwareWindow = async () => {
  const base = import.meta.env.BASE_URL
  const response = await fetch(base + bearAwareWindowSvg)
  if (!response.ok) throw new Error(`Bear Aware window sign: HTTP ${response.status}`)
  return {
    ...bearAwareWindow, svgRaw: await response.text(),
    reference: {
      src: base + bearAwareWindowScan, box: bearAwareWindowView,
      caption: 'Original window-sign scan on PDF page 27 of the 1997 Final Report.'
    }
  }
}
