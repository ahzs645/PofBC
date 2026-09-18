// Framework-free renderer for the Province of British Columbia lockups.
//
// This builds complete, self-contained SVG *strings*. Everything else in the package — the React
// component, the PNG/WebP/PDF exporters, the generator site — is a thin wrapper over this file, so
// the layout rules and colour handling can never drift apart between them. Being plain string
// building (no DOM, no React, no bundler features) it also runs unchanged in Node, which is what
// lets `npm run compare` check the output against the original artwork.

import { PROVINCIAL_MARK } from '../assets/markup.js'
import { getLayout, LAYOUT_ORDER, LAYOUTS, MARK_BOX, PROVINCE_WORDMARK } from './layouts.js'
import { layoutBlock, positionWords, wrapText } from './logoText.js'
import { outlineTextMarkup } from './textOutline.js'
import { BRAND_COLORS, resolveColor, TRANSPARENT } from './logoColors.js'
import { getFaceMetrics } from './fontMetrics.js'

export const LOGO_FONT_FAMILY = "'HelveticaPofBC', Helvetica, Arial, sans-serif"

export { LAYOUTS, LAYOUT_ORDER, MARK_BOX, PROVINCE_WORDMARK }

// Everything reaching the renderer is author-supplied — and, once a lockup can be restored from a
// shared URL, supplied by whoever wrote that URL. Values are escaped before being concatenated
// into markup: without it a ministry name containing "&" produces an SVG that will not parse, and
// a colour containing a quote closes the attribute it sits in and opens a tag of its own.
export const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')

const round = (value) => Math.round(value * 1000) / 1000

/**
 * Works out where everything goes, without drawing anything.
 *
 * Exported because the React component and the export pipeline both need the resolved geometry —
 * and because it is far easier to test a returned box than a string of markup.
 *
 * @param {object} options
 * @param {'stacked'|'centred'|'horizontal'} [options.layout]
 * @param {boolean} [options.wordmark]   Show "Province of British Columbia". The centred lockup
 *                                       is drawn without it in the source artwork.
 * @param {string} [options.ministry]    The ministry line. Wraps to the layout's measure.
 * @param {string} [options.program]     An optional second line, e.g. "Research Program".
 * @param {string} [options.color]       Mark and text colour. A shorthand: whichever of
 *                                       markColor and textColor is not given falls back to it.
 * @param {string} [options.markColor]   The mark on its own.
 * @param {string} [options.textColor]   The type on its own.
 * @param {string} [options.background]  'none' for transparent, or any colour.
 * @param {number} [options.padding]     Clear space around the lockup, in artwork units. The
 *                                       background, where there is one, extends to cover it.
 */
export const resolveLockup = ({
  layout: layoutId = 'stacked',
  wordmark = true,
  ministry = '',
  program = '',
  color = BRAND_COLORS.white,
  markColor,
  textColor,
  background = TRANSPARENT,
  padding = 0
} = {}) => {
  const layout = getLayout(layoutId)
  const { fontSize, leading, letterSpacing, wordSpacing } = layout

  const styleFor = (weight) => ({ fontSize, weight, letterSpacing, wordSpacing })
  const boldStyle = styleFor('bold')
  const regularStyle = styleFor('regular')

  const hasWordmark = Boolean(wordmark)
  const measure = layout.measure({ hasWordmark })

  // The wordmark and the ministry wrap independently but share one continuous leading, so the
  // whole lockup reads as a single block of type rather than two stacked paragraphs.
  const entries = [
    ...(hasWordmark ? wrapText(PROVINCE_WORDMARK, measure, boldStyle).map((text) => ({ text, style: boldStyle })) : []),
    ...wrapText(ministry, measure, regularStyle).map((text) => ({ text, style: regularStyle })),
    ...wrapText(program, measure, regularStyle).map((text) => ({ text, style: regularStyle }))
  ]

  const block = layoutBlock(entries, leading)
  const hasText = entries.length > 0

  const placement = hasText
    ? place(layout, block)
    // With no text at all the lockup is just the mark, sitting at the origin.
    : { markX: 0, markY: 0, textOrigin: { x: 0, y: 0 }, bounds: { minX: 0, minY: 0, maxX: MARK_BOX.width, maxY: MARK_BOX.height } }

  const { markX, markY, textOrigin, bounds } = placement

  // Each line is positioned explicitly rather than leaning on text-anchor, so centring is computed
  // from the ink the glyphs actually cover and comes out identical in every renderer.
  const lines = block.lines.map((line) => {
    const offset = layout.align === 'centre'
      ? (block.inkRight - block.inkLeft) / 2 - (line.inkLeft + line.inkRight) / 2 + block.inkLeft
      : 0

    return {
      text: line.text,
      style: line.style,
      x: round(textOrigin.x + offset),
      y: round(textOrigin.y + line.baseline),
      words: positionWords(line.text, line.style)
    }
  })

  return {
    layout,
    lines,
    hasText,
    // The accessible name for this lockup, so every consumer says the same thing.
    description: [hasWordmark ? PROVINCE_WORDMARK : null, ministry, program].filter(Boolean).join(' — ') || PROVINCE_WORDMARK,
    mark: { x: round(markX), y: round(markY), width: MARK_BOX.width, height: MARK_BOX.height },
    // The mark and the type are coloured independently — a green mark over black type is a real
    // combination — but `color` sets both at once, which is what most callers want.
    markColor: resolveColor(markColor ?? color),
    textColor: resolveColor(textColor ?? color),
    background: resolveColor(background, TRANSPARENT),
    padding,
    // The viewBox hugs the ink: the mark's own bounds and the glyphs' actual extents, with no
    // allowance for ascenders or descenders that nothing in this particular lockup reaches.
    viewBox: {
      x: round(bounds.minX - padding),
      y: round(bounds.minY - padding),
      width: round(bounds.maxX - bounds.minX + padding * 2),
      height: round(bounds.maxY - bounds.minY + padding * 2)
    }
  }
}

/**
 * Positions the mark against the text block and returns the union of their bounds.
 *
 * Both placements align on ink rather than on the type's origin: the mark's left edge lines up
 * with where the letterforms start, not with the invisible point the text is anchored at. That
 * is how the source artwork is drawn, and the difference is visible — a capital P carries about
 * 0.08 em of side bearing.
 */
const place = (layout, block) => {
  const blockWidth = block.inkRight - block.inkLeft

  if (layout.markPlacement === 'beside') {
    // Mark on the left, text to its right, the two centred on each other. The text's optical
    // centre is taken from the cap height of the first line down to the last baseline, which is
    // the mass the eye actually balances — counting the full ascent and descent of the face
    // instead would sit the mark noticeably high.
    const capHeight = capHeightOf(block.lines[0])
    const textTop = -capHeight
    const textBottom = block.lines.at(-1).baseline
    const markY = (textTop + textBottom) / 2 - MARK_BOX.height / 2

    const textX = MARK_BOX.width + layout.gap - block.inkLeft

    return {
      markX: 0,
      markY,
      textOrigin: { x: textX, y: 0 },
      bounds: {
        minX: 0,
        maxX: textX + block.inkRight,
        minY: Math.min(markY, block.inkTop),
        maxY: Math.max(markY + MARK_BOX.height, block.inkBottom)
      }
    }
  }

  // Mark above the text. The gap is measured from the mark's bottom edge to the cap height of the
  // first line, so a line that happens to start with an ascender or a lowercase letter does not
  // change how far the text sits from the mark.
  const firstBaseline = MARK_BOX.height + layout.gap + capHeightOf(block.lines[0])

  // The text block's leftmost ink is pulled to x = 0, so the mark either sits flush with it or,
  // when centred, straddles its midpoint.
  const textX = -block.inkLeft
  const markX = layout.align === 'centre' ? blockWidth / 2 - MARK_BOX.width / 2 : 0

  const left = Math.min(markX, 0)
  const right = Math.max(markX + MARK_BOX.width, blockWidth)

  return {
    markX,
    markY: 0,
    textOrigin: { x: textX, y: firstBaseline },
    bounds: {
      minX: left,
      maxX: right,
      minY: 0,
      maxY: firstBaseline + block.inkBottom
    }
  }
}

const capHeightOf = (line) => (
  getFaceMetrics(line.style.weight).capHeight * line.style.fontSize / 1000
)

// ── Markup ───────────────────────────────────────────────────────────────────────────────────────

/** The mark on its own, as a fragment, at `size` units wide. Colour inherits from the caller. */
export const renderMarkMarkup = ({ x = 0, y = 0, size } = {}) => {
  const scale = size ? size / MARK_BOX.width : 1
  const transform = scale === 1
    ? (x || y ? ` transform="translate(${round(x)} ${round(y)})"` : '')
    : ` transform="translate(${round(x)} ${round(y)}) scale(${round(scale)})"`

  return `<g${transform}>${PROVINCIAL_MARK.inner}</g>`
}

const textMarkup = (lines, fontFamily, fill) => lines.map((line) => {
  const { style } = line
  const spacing = style.letterSpacing ? ` letter-spacing="${round(style.letterSpacing * style.fontSize)}"` : ''
  const weight = style.weight === 'bold' ? ' font-weight="700"' : ''

  const content = line.words.length === 1
    ? escapeXml(line.words[0].text)
    : line.words.map((word) => `<tspan x="${round(line.x + word.x)}">${escapeXml(word.text)}</tspan>`).join('')

  return `<text x="${line.x}" y="${line.y}" fill="${escapeXml(fill)}" font-family="${escapeXml(fontFamily)}"` +
    ` font-size="${style.fontSize}"${weight}${spacing}>${content}</text>`
}).join('')

/**
 * The lockup as an SVG fragment, for embedding in a larger drawing. Coordinates stay in the
 * artwork's native units, positioned as `resolveLockup` decided.
 *
 * Pass `glyphs` — the outline table from the font build — to draw the type as paths instead of as
 * text. The layout is identical either way; only the means of drawing it changes.
 */
export const renderLockupMarkup = (options = {}) => {
  const resolved = options.resolved || resolveLockup(options)
  const fontFamily = options.fontFamily || LOGO_FONT_FAMILY

  const type = options.glyphs
    ? outlineTextMarkup(resolved.lines, options.glyphs, resolved.textColor)
    : textMarkup(resolved.lines, fontFamily, resolved.textColor)

  return `<g fill="${escapeXml(resolved.markColor)}">` +
    renderMarkMarkup({ x: resolved.mark.x, y: resolved.mark.y }) +
    '</g>' +
    type
}

/**
 * The lockup as a complete, standalone SVG document.
 *
 * @param {object} options              Everything `resolveLockup` accepts, plus:
 * @param {number} [options.pixelWidth] Sets width/height attributes at this pixel width.
 * @param {string} [options.fontCss]    CSS injected into <defs>, for embedding @font-face.
 * @param {object} [options.glyphs]     Outline table; draws the type as paths instead of text.
 * @param {string} [options.title]      Accessible name. Pass null to omit.
 * @returns {string} A complete <svg> document.
 */
export const renderLockupSvg = (options = {}) => {
  const resolved = options.resolved || resolveLockup(options)
  const { viewBox, background } = resolved

  // A pixel width is optional; when given the height follows the aspect ratio, so callers never
  // have to compute it and never accidentally distort the lockup.
  const dimensions = options.pixelWidth
    ? ` width="${options.pixelWidth}" height="${Math.round(options.pixelWidth * viewBox.height / viewBox.width)}"`
    : ''

  const backgroundRect = background && background !== TRANSPARENT
    ? `<rect x="${viewBox.x}" y="${viewBox.y}" width="${viewBox.width}" height="${viewBox.height}" fill="${escapeXml(background)}"/>`
    : ''

  const title = options.title === undefined ? resolved.description : options.title

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}"${dimensions}>` +
    (title ? `<title>${escapeXml(title)}</title>` : '') +
    (options.fontCss ? `<defs><style>${options.fontCss}</style></defs>` : '') +
    backgroundRect +
    renderLockupMarkup({ ...options, resolved }) +
    '</svg>'
}

export { BRAND_COLORS }
