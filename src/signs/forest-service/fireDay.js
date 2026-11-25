import { SIGNS } from '../catalogue.js'

const source = { label: 'Powell River Digester, July 1938, vol. 14, no. 7, front cover (PDF page 123), qathet Museum and Archives', href: 'https://qathetmuseum.ca/wp-content/uploads/2024/01/digester-1938-prhma__exoptmed_.pdf#page=123' }

export const FIRE_DAY = {
  id: 'fire-day',
  order: ['overview', 'warnings', 'tree', 'notice'],
  regions: ['warnings', 'tree', 'notice'],
  parts: {
    overview: { label: 'Whole sign', box: SIGNS['fire-day'].view, pad: 0.05, panel: {
      eyebrow: 'British Columbia Forest Service · fire prevention', heading: 'TO-DAY IS A FIRE DAY',
      lede: 'This sign stood at Second Street and Ocean View in Powell River. The July 1938 Digester said it had been up for ten days during a prolonged dry spell.',
      blocks: ['The Forest Service displayed the panel on days of extreme fire danger. The two columns address campfires and cigarettes, and the lower notice explains why the sign was up.',
        { note: 'The drawing follows a black-and-white photograph. Its tones and outlined letterforms are interpretations. The original paint colours, typeface, dimensions and first issue date are unknown.' }, { sources: [source] }]
    } },
    warnings: { label: 'Two warnings', layer: '#warnings', box: { x: 28, y: 96, w: 504, h: 145 }, pad: 0.04, panel: {
      heading: 'Campfires and cigarettes', lede: 'The left column asks readers to avoid lighting campfires. The right column asks them to put all cigarette stubs out.', blocks: [{ sources: [source] }]
    } },
    tree: { label: 'Tree emblem', layer: '#tree-panel', box: { x: 174, y: 87, w: 204, h: 162 }, pad: 0.1, panel: {
      heading: 'The evergreen', lede: 'A light disc separates the dark tree from its rectangular field. The lower branches spread over a short, rooted trunk.', blocks: [{ sources: [source] }]
    } },
    notice: { label: 'Extreme fire danger notice', layer: '#explanation, #issuer', box: { x: 30, y: 266, w: 488, h: 130 }, pad: 0.06, panel: {
      heading: 'When the sign went up', lede: 'The notice singles out roadside and forest debris. It underlines INFLAMMABLE, retains the spelling “to-day” and names the British Columbia Forest Service along the foot.', blocks: [{ sources: [source] }]
    } }
  }
}
