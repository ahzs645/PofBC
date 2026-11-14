// Portable, path-only document headings. Preview and every export share this renderer.
import { resolveColor, TRANSPARENT } from '../logo/logoColors.js'
import {
  DEFAULT_DOCUMENT_ARMS_LAYOUT, DOCUMENT_ARMS_LAYOUT_ORDER, DOCUMENT_ARMS_PROVENANCE
} from './layouts.js'
import {
  DOCUMENT_ARMS_LETTERING, DOCUMENT_ARMS_PATH, DOCUMENT_ARMS_SOURCE
} from './geometry.generated.js'

export { DOCUMENT_ARMS_LAYOUT_ORDER, DOCUMENT_ARMS_LAYOUTS } from './layouts.js'

const MARK_HEIGHT = 1000
const MARK_SCALE = MARK_HEIGHT / DOCUMENT_ARMS_SOURCE.arms.naturalSize[1]
const MARK_WIDTH = DOCUMENT_ARMS_SOURCE.arms.naturalSize[0] * MARK_SCALE
const round = (value) => Math.round(value * 1000) / 1000
const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&apos;')

// The core renderer is also public, so it cannot rely on the site's URL sanitizer having run.
// Paint servers, CSS variables and external references are deliberately not accepted here.
const PAINT = /^(?:#(?:[0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})|[a-z]+|(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch)\([0-9.,%+\-\s/degturnrad]+\))$/i
const colour = (value, fallback) => {
  const resolved = resolveColor(value, fallback)
  return typeof resolved === 'string' && resolved.length <= 96 && PAINT.test(resolved.trim())
    ? resolved.trim()
    : fallback
}

const boundedNumber = (value, fallback, minimum, maximum) => (
  typeof value === 'number' && Number.isFinite(value)
    ? Math.min(maximum, Math.max(minimum, value))
    : fallback
)

const selectedLayout = (value) => DOCUMENT_ARMS_LAYOUT_ORDER.includes(value)
  ? value
  : DEFAULT_DOCUMENT_ARMS_LAYOUT

const word = (key, x, y) => {
  const lettering = DOCUMENT_ARMS_LETTERING[key]
  return { key, ...lettering, x, y }
}

/** Deterministic geometry before padding. The arms always use one uniform scale. */
export const layoutDocumentArms = ({ layout = DEFAULT_DOCUMENT_ARMS_LAYOUT } = {}) => {
  const id = selectedLayout(layout)
  let width = MARK_WIDTH
  let height = MARK_HEIGHT
  let markX = 0
  const lettering = []

  if (id === 'split-serif' || id === 'split-blackletter') {
    const isBlackletter = id === 'split-blackletter'
    const leftKey = isBlackletter ? 'blackletterBritish' : 'serifBritish'
    const rightKey = isBlackletter ? 'blackletterColumbia' : 'serifColumbia'
    const left = DOCUMENT_ARMS_LETTERING[leftKey]
    const right = DOCUMENT_ARMS_LETTERING[rightKey]
    const gap = isBlackletter ? 460 : 120
    // The source headings place both words on a shared baseline. A capital's flourish therefore
    // keeps its true depth instead of being vertically stretched to match its neighbour.
    const baseline = isBlackletter ? 790 : 560
    markX = left.width + gap
    width = markX + MARK_WIDTH + gap + right.width
    lettering.push(word(leftKey, 0, baseline - left.baseline))
    lettering.push(word(rightKey, markX + MARK_WIDTH + gap, baseline - right.baseline))
  } else if (id === 'government') {
    const first = DOCUMENT_ARMS_LETTERING.government
    const second = DOCUMENT_ARMS_LETTERING.province
    width = Math.max(MARK_WIDTH, first.width, second.width)
    markX = (width - MARK_WIDTH) / 2
    const firstY = MARK_HEIGHT + 48
    const secondY = firstY + first.height + 30
    lettering.push(word('government', (width - first.width) / 2, firstY))
    lettering.push(word('province', (width - second.width) / 2, secondY))
    height = secondY + second.height
  }

  return {
    id,
    width: round(width),
    height: round(height),
    mark: { x: markX, y: 0, width: MARK_WIDTH, height: MARK_HEIGHT, scale: MARK_SCALE },
    lettering
  }
}

/** Size without clear space, matching the other identity renderers. */
export const documentArmsSize = (options = {}) => {
  const { width, height } = layoutDocumentArms(options)
  return { width, height }
}

/**
 * @param {object} options
 * @param {'emblem'|'split-serif'|'government'|'split-blackletter'} [options.layout]
 * @param {string} [options.markColor]
 * @param {string} [options.textColor]
 * @param {string} [options.background]
 * @param {number} [options.clearSpaceFactor] Padding as a fraction of unpadded artwork width.
 * @param {number} [options.pixelWidth] Intrinsic width, clamped to 1–16384 pixels.
 * @param {string} [options.title]
 * @returns {{svg:string,box:{x:number,y:number,width:number,height:number},layout:object}}
 */
export const renderDocumentArmsSvg = ({
  layout = DEFAULT_DOCUMENT_ARMS_LAYOUT,
  markColor = '#000000',
  textColor,
  background = TRANSPARENT,
  clearSpaceFactor = 0,
  pixelWidth,
  title = 'British Columbia historical document heading — provisional study'
} = {}) => {
  const drawing = layoutDocumentArms({ layout })
  const ink = colour(markColor, '#000000')
  const type = colour(textColor ?? markColor, ink)
  const ground = colour(background, TRANSPARENT)
  const padding = boundedNumber(clearSpaceFactor, 0, 0, 2) * drawing.width
  const box = {
    x: round(-padding),
    y: round(-padding),
    width: round(drawing.width + 2 * padding),
    height: round(drawing.height + 2 * padding)
  }
  const pixels = pixelWidth === undefined
    ? null
    : Math.round(boundedNumber(pixelWidth, 2048, 1, 16384))
  const dimensions = pixels === null ? ''
    : ` width="${pixels}" height="${Math.max(1, Math.round(pixels * box.height / box.width))}"`
  const backdrop = ground === TRANSPARENT ? ''
    : `<rect data-part="background" x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" fill="${escapeXml(ground)}"/>`
  const heading = drawing.lettering.map(({ key, text, x, y, path }) => (
    `<path data-part="${key}" aria-label="${escapeXml(text)}" transform="translate(${round(x)} ${round(y)})" d="${path}"/>`
  )).join('')
  const metadata = {
    identity: 'document-arms',
    layout: drawing.id,
    status: DOCUMENT_ARMS_SOURCE.status,
    provenance: DOCUMENT_ARMS_PROVENANCE,
    sources: DOCUMENT_ARMS_SOURCE
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box.x} ${box.y} ${box.width} ${box.height}"${dimensions} data-identity="document-arms" data-layout="${drawing.id}" data-accuracy="provisional-study">` +
    `<title>${escapeXml(String(title ?? '').slice(0, 500))}</title>` +
    `<desc>${escapeXml(DOCUMENT_ARMS_PROVENANCE)}</desc>` +
    `<metadata>${escapeXml(JSON.stringify(metadata))}</metadata>` +
    backdrop +
    `<g data-part="arms" transform="translate(${round(drawing.mark.x)} 0) scale(${MARK_SCALE})" fill="${escapeXml(ink)}">` +
    `<path d="${DOCUMENT_ARMS_PATH}" fill-rule="evenodd"/></g>` +
    (heading ? `<g data-part="heading" fill="${escapeXml(type)}">${heading}</g>` : '') +
    '</svg>'
  return { svg, box, layout: drawing }
}
