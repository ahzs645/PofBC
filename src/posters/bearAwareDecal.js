import {
  bearAwareDecalSvg, bearAwareDecalView, bearAwareReport,
  bearAwareTitle, bearAwareWindowId, bearAwareWindowTitle
} from '../initiatives/bearAwareArtwork.js'

export const bearAwareDecal = {
  order: ['overview'],
  regions: [],
  spotlight: { keep: [] },
  parts: {
    overview: {
      label: 'Window decal', box: bearAwareDecalView,
      story: ['Revelstoke’s 1997 campaign gave this window sign to residents and businesses that met its Bear Aware checklist criteria.'],
      panel: {
        eyebrow: bearAwareTitle + ' · 1997',
        heading: bearAwareWindowTitle,
        lede: 'The four words and five-clawed paw form the main oval decal.',
        blocks: [
          { facts: [['Documented', '1997 Final Report, PDF page 27'], ['Artwork', 'Decal-only SVG reconstruction']] },
          { downloads: [{ label: 'Download decal SVG', file: bearAwareDecalSvg }] },
          { links: [{ label: 'View complete window sign and original scan', to: { view: 'signs', sign: bearAwareWindowId } }] },
          { sources: [{ label: '1997 Final Report, PDF page 27', href: bearAwareReport + '#page=27' }] }
        ]
      }
    }
  }
}

export const loadBearAwareDecal = async (base = import.meta.env.BASE_URL) => {
  const response = await fetch(base + bearAwareDecalSvg)
  if (!response.ok) throw new Error(`Bear Aware window decal: HTTP ${response.status}`)
  return { ...bearAwareDecal, svgRaw: await response.text() }
}
