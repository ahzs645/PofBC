import { downloadBlob } from '../export/exportLogo.js'
import { assetUrl } from './collectedCollections.js'

// Extend the trimmed source's viewBox so the SVG retains vector paths and has
// the requested physical dimensions when imported at 100% in a page layout.
export async function exportProgramPlacement({ asset, copy, height, margin, unit, background }) {
  const response = await fetch(assetUrl(copy.file))
  if (!response.ok) throw new Error('Artwork could not be loaded.')
  const doc = new DOMParser().parseFromString(await response.text(), 'image/svg+xml')
  const svg = doc.documentElement
  if (svg.localName !== 'svg') throw new Error('Artwork could not be read.')
  const box = svg.viewBox.baseVal
  const trim = box.height * copy.inkInset
  const inkHeight = box.height - 2 * trim
  const scale = height / inkHeight
  const outset = margin / scale - trim
  const x = box.x - outset
  const y = box.y - outset
  const w = box.width + 2 * outset
  const h = box.height + 2 * outset
  svg.setAttribute('viewBox', [x, y, w, h].join(' '))
  svg.setAttribute('width', (w * scale) + unit)
  svg.setAttribute('height', (height + 2 * margin) + unit)
  const ground = doc.createElementNS(svg.namespaceURI, 'rect')
  for (const [name, value] of Object.entries({ x, y, width: w, height: h, fill: background }))
    ground.setAttribute(name, value)
  svg.prepend(ground)
  const xml = new XMLSerializer().serializeToString(svg)
  downloadBlob(new Blob([xml], { type: 'image/svg+xml' }), asset.id + '-placement-' + height + unit + '.svg')
}
