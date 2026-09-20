// Browser export pipeline: one lockup description in, a downloadable file out.
//
// Everything routes through renderLockupSvg() so an exported PNG is the same drawing as the live
// preview. Raster formats go SVG string → <img> → <canvas> → Blob, which keeps the type crisp at
// any size because the vector is rasterised at the target resolution rather than upscaled.

import { renderLockupSvg, resolveLockup } from '../logo/renderLogoSvg.js'
import { markSize, renderCurrentSvg } from '../current/currentMarks.js'
import { flagSize, renderFlagSvg } from '../flag/renderFlagSvg.js'
import { crestSize, renderCrestSvg } from '../crest/renderCrestSvg.js'
import { BRAND_FONT_FAMILY, getEmbeddedFaces, getEmbeddedFontCss } from './fontEmbed.js'
import { getGlyphOutlines } from './fontOutlines.js'

export const EXPORT_FORMATS = {
  svg: { label: 'SVG', extension: 'svg', mimeType: 'image/svg+xml', vector: true },
  pdf: { label: 'PDF', extension: 'pdf', mimeType: 'application/pdf', vector: true },
  png: { label: 'PNG', extension: 'png', mimeType: 'image/png', alpha: true },
  webp: { label: 'WebP', extension: 'webp', mimeType: 'image/webp', alpha: true },
  // JPEG has no alpha channel; a transparent request is composited onto white instead.
  jpeg: { label: 'JPEG', extension: 'jpg', mimeType: 'image/jpeg', alpha: false }
}

export const EXPORT_FORMAT_ORDER = ['svg', 'pdf', 'png', 'webp', 'jpeg']

/** Raster size presets, in pixels of lockup width. */
export const SIZE_PRESETS = [512, 1024, 2048, 4096]

const DEFAULT_PIXEL_WIDTH = 2048

/**
 * Not every browser can encode every format, so a 1px canvas is probed before offering one that
 * would silently hand back a PNG instead.
 */
export const isFormatSupported = (format) => {
  const spec = EXPORT_FORMATS[format]
  if (!spec) return false
  if (spec.vector) return true
  if (typeof document === 'undefined') return false

  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  return canvas.toDataURL(spec.mimeType).startsWith(`data:${spec.mimeType}`)
}

// "Ministry of Forests" → "ministry-of-forests", for a readable download name. Absent values yield
// '' rather than the string "undefined", so buildFileName can drop them.
const slugify = (value) => (value == null ? '' : String(value))
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '')
  .slice(0, 60)

export const buildFileName = ({
  era = 'historical', language, currentMinistry, currentVariant,
  layout = 'stacked', ministry, color, markColor, textColor, outlineText, format
}) => {
  const extension = EXPORT_FORMATS[format]?.extension || format

  // The current era names what it actually is: an official mark, in a language, in one of the
  // Province's colourways. None of the historical era's colour or lockup choices apply.
  if (era === 'flag') {
    return `bc-flag-${slugify(ministry) || 'lockup'}.${extension}`
  }

  if (era === 'crest') {
    return `bc-arms-${slugify(ministry) || 'lockup'}.${extension}`
  }

  if (era === 'current') {
    return `bc-${slugify(currentMinistry)}-${language}-${slugify(currentVariant)}.${extension}`
  }

  const mark = markColor ?? color
  const text = textColor ?? color
  const parts = [
    'bc',
    slugify(ministry) || 'wordmark',
    layout,
    slugify(mark),
    // Only worth naming when the two halves differ; otherwise it is the same word twice.
    slugify(text) === slugify(mark) ? '' : slugify(text),
    outlineText ? 'outlined' : ''
  ].filter(Boolean)

  return `${parts.join('-')}.${extension}`
}

/**
 * The SVG source for an export.
 *
 * `outlineText` draws the type as paths instead of as text. Where it is on, no font is embedded at
 * all — the shapes carry themselves — which is both smaller and the thing that makes the file
 * immune to whatever the receiving application does about fonts.
 *
 * `embedFont: false` skips the inlining without outlining. The PDF path uses that: jsPDF is handed
 * the faces directly, so an @font-face carrying the same two fonts again as base64 would just be a
 * third copy of the payload for svg2pdf to parse.
 */
export const buildSvgSource = async ({ embedFont = true, outlineText = false, ...options } = {}) => {
  if (options.era === 'current') {
    const { svg } = await buildCurrentArtwork(options)
    return svg
  }

  const glyphs = outlineText ? await getGlyphOutlines() : null
  // If the outlines could not be loaded, fall back to live text rather than exporting nothing.
  const fontCss = glyphs || !embedFont ? undefined : await getEmbeddedFontCss()

  if (options.era === 'flag') return buildFlagArtwork({ ...options, glyphs, fontCss }).svg
  if (options.era === 'crest') return buildCrestArtwork({ ...options, glyphs, fontCss }).svg

  return renderLockupSvg({ ...options, glyphs, fontCss })
}

/** The crest lockup's artwork. Drawn from parts, so the outline option applies as it does to the
 * other generated eras. */
const buildCrestArtwork = ({
  ministry, crestArrangement, crestPlacement, crestBold, crestAlign, crestExtra,
  crestMinistrySize, crestExtraStep,
  crestMarkColor, crestTextColor, crestBackground, clearSpaceFactor = 0, pixelWidth, title,
  glyphs, fontCss
}) => {
  const { svg, box } = renderCrestSvg({
    arrangement: crestArrangement,
    placement: crestPlacement,
    ministry,
    extra: crestExtra,
    bold: crestBold,
    align: crestAlign,
    ministrySize: crestMinistrySize,
    extraStep: crestExtraStep,
    markColor: crestMarkColor,
    textColor: crestTextColor,
    background: crestBackground,
    clearSpaceFactor,
    pixelWidth,
    title,
    glyphs,
    fontCss
  })
  return { svg, viewBox: box }
}

/** The crest lockup's box, before any font has loaded. */
const crestViewBox = ({
  ministry, crestArrangement, crestPlacement, crestBold, crestAlign, crestExtra,
  crestMinistrySize, crestExtraStep, clearSpaceFactor = 0
}) => {
  const { width, height } = crestSize({
    ministry, arrangement: crestArrangement, placement: crestPlacement,
    bold: crestBold, align: crestAlign, extra: crestExtra,
    ministrySize: crestMinistrySize, extraStep: crestExtraStep
  })
  const padding = clearSpaceFactor * width
  return { x: -padding, y: -padding, width: width + padding * 2, height: height + padding * 2 }
}

/** The flag lockup's box, clear space included. Needed before the type has a font to draw with. */
const flagViewBox = ({ ministry, flagSymbol, flagPlacement, flagProvince, flagExtra, clearSpaceFactor = 0 }) => {
  const { width, height } = flagSize({
    ministry, symbol: flagSymbol, placement: flagPlacement, province: flagProvince, extra: flagExtra
  })
  const padding = clearSpaceFactor * width
  return { x: -padding, y: -padding, width: width + padding * 2, height: height + padding * 2 }
}

/**
 * The flag era's artwork.
 *
 * Drawn from parts like the crest era, so the same outline option applies: pass the glyph table
 * and the type becomes paths, leave it out and the file carries live text and an embedded face.
 */
const buildFlagArtwork = ({
  ministry, flagSymbol, flagPlacement, flagProvince, flagExtra,
  flagMarkColor, flagTextColor, flagPalette, flagBackground, clearSpaceFactor = 0, pixelWidth,
  title, glyphs, fontCss
}) => {
  const { svg, box } = renderFlagSvg({
    ministry,
    symbol: flagSymbol,
    placement: flagPlacement,
    province: flagProvince,
    extra: flagExtra,
    letterColor: flagMarkColor,
    textColor: flagTextColor,
    flagPalette,
    background: flagBackground,
    clearSpaceFactor,
    pixelWidth,
    title,
    glyphs,
    fontCss
  })
  return { svg, viewBox: box }
}

/**
 * The current era's artwork, composed and coloured.
 *
 * It comes out as outlines — the mark is the Province's drawing and the wording is set from their
 * alphabet, both already paths — so there is no font to embed and nothing to convert. That is why
 * the outline option does not apply to this era and the PDF path needs no faces registered.
 */
const buildCurrentArtwork = ({
  currentName, language = 'en', currentVariant = 'colour',
  background, clearSpaceFactor = 0, pixelWidth, title
}) => {
  const { width, height } = markSize({ text: currentName, language })
  // Measured against this artwork, not the crest's — they are nothing like the same size.
  const padding = clearSpaceFactor * width

  return {
    svg: renderCurrentSvg({
      text: currentName, language, variant: currentVariant, background, clearSpaceFactor, pixelWidth, title
    }),
    viewBox: { x: -padding, y: -padding, width: width + padding * 2, height: height + padding * 2 }
  }
}

/**
 * Rasterises an SVG string. The SVG carries explicit width/height attributes so the <img> reports
 * a definite intrinsic size in every browser — Firefox will not infer one from a viewBox alone.
 */
const rasterize = async (svgSource, { mimeType, quality, background }) => {
  const blob = new Blob([svgSource], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)

  try {
    const image = await new Promise((resolve, reject) => {
      const element = new Image()
      element.onload = () => resolve(element)
      element.onerror = () => reject(new Error('Could not rasterise the lockup SVG'))
      element.src = url
    })

    const canvas = document.createElement('canvas')
    canvas.width = image.naturalWidth || image.width
    canvas.height = image.naturalHeight || image.height

    const context = canvas.getContext('2d')
    if (background) {
      context.fillStyle = background
      context.fillRect(0, 0, canvas.width, canvas.height)
    }
    context.drawImage(image, 0, 0, canvas.width, canvas.height)

    return await new Promise((resolve, reject) => {
      canvas.toBlob(
        (result) => (result ? resolve(result) : reject(new Error(`This browser cannot encode ${mimeType}`))),
        mimeType,
        quality
      )
    })
  } finally {
    URL.revokeObjectURL(url)
  }
}

/**
 * Renders to PDF: a real vector page at the lockup's own proportions, with the type still live
 * text rather than outlines, so it stays selectable and scales cleanly in print.
 *
 * jsPDF and svg2pdf are ~200 KB between them and are only needed for this one format, so they are
 * imported on demand rather than bundled into the initial load.
 */
const renderPdf = async (svgSource, resolved, { outlined }) => {
  const [{ jsPDF }, { svg2pdf }, faces] = await Promise.all([
    import('jspdf'),
    import('svg2pdf.js'),
    // Outlined artwork has no text for jsPDF to set, so the faces are not fetched at all.
    outlined ? null : getEmbeddedFaces()
  ])


  const { width, height } = resolved.viewBox
  const document_ = new jsPDF({
    orientation: width >= height ? 'landscape' : 'portrait',
    unit: 'pt',
    // A page exactly the size of the lockup: this is artwork to be placed, not a document to read.
    format: [width, height]
  })

  // svg2pdf draws <text> with whatever jsPDF has registered, so both faces are handed over under
  // the same family name the SVG asks for. Without this the PDF falls back to Helvetica's
  // built-in metrics and the line breaks shift.
  if (faces) {
    for (const [weight, base64] of Object.entries(faces)) {
      const style = weight === '700' ? 'bold' : 'normal'
      const fileName = `${BRAND_FONT_FAMILY}-${style}.ttf`
      document_.addFileToVFS(fileName, base64)
      document_.addFont(fileName, BRAND_FONT_FAMILY, style)
    }
  }

  // svg2pdf resolves styling through getComputedStyle, which only answers for an element that is
  // actually in a document. Parsing to a detached tree silently yields a blank page, so the SVG is
  // adopted into the page out of view for the duration of the conversion.
  const parsed = new DOMParser().parseFromString(svgSource, 'image/svg+xml').documentElement
  const element = document.importNode(parsed, true)
  const holder = document.createElement('div')
  holder.setAttribute('aria-hidden', 'true')
  holder.style.cssText = 'position:fixed;left:-99999px;top:0;width:0;height:0;overflow:hidden'
  holder.appendChild(element)
  document.body.appendChild(holder)

  try {
    await svg2pdf(element, document_, { x: 0, y: 0, width, height })
  } finally {
    holder.remove()
  }

  return document_.output('blob')
}

/**
 * Renders a lockup to a Blob in the requested format.
 *
 * @param {object} options              Everything resolveLockup() accepts, plus:
 * @param {string} [options.format]     'svg' | 'pdf' | 'png' | 'webp' | 'jpeg'
 * @param {number} [options.pixelWidth] Output width for raster formats.
 * @param {number} [options.quality]    0–1, for WebP and JPEG.
 */
export const renderLogoBlob = async ({
  format = 'png',
  pixelWidth = DEFAULT_PIXEL_WIDTH,
  quality = 0.92,
  ...options
} = {}) => {
  const spec = EXPORT_FORMATS[format]
  if (!spec) throw new Error(`Unsupported export format: ${format}`)

  // The current era's geometry comes from the artwork itself; the other two compute theirs. The
  // flag era's layout needs no font, so its box can be had before any outline has been loaded.
  const current = options.era === 'current' ? buildCurrentArtwork({ ...options, pixelWidth }) : null
  const resolved = current ??
    (options.era === 'flag'
      ? { viewBox: flagViewBox(options) }
      : options.era === 'crest'
        ? { viewBox: crestViewBox(options) }
        : resolveLockup(options))
  const svgSource = current
    ? current.svg
    : await buildSvgSource({ ...options, resolved, pixelWidth, embedFont: format !== 'pdf' })

  // The source is the authority on whether anything still needs a font, rather than the request:
  // an outline load that quietly failed has to leave live text behind, and the PDF writer needs to
  // know that it did.
  const outlined = !svgSource.includes('<text')

  if (format === 'pdf') return renderPdf(svgSource, resolved, { outlined })
  if (spec.vector) return new Blob([svgSource], { type: `${spec.mimeType};charset=utf-8` })

  // renderLockupSvg() already paints any requested background into the SVG itself, so PNG and WebP
  // need no canvas fill — omitting it is what preserves transparency when none was asked for.
  // JPEG has no alpha channel and composites unpainted pixels to black, so it always gets an
  // opaque base; where the SVG does paint a background, that base is simply covered over.
  const background = spec.alpha ? null : '#ffffff'

  return rasterize(svgSource, { mimeType: spec.mimeType, quality, background })
}

/** Saves a Blob under `fileName` via a temporary object URL. */
export const downloadBlob = (blob, fileName) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  // Revoking synchronously can cancel the download in Safari; defer past the click.
  setTimeout(() => URL.revokeObjectURL(url), 10_000)
}

/** Renders and downloads a lockup in one call. Returns the filename it saved. */
export const exportLogo = async (options = {}) => {
  const format = options.format || 'png'
  const blob = await renderLogoBlob(options)
  const fileName = options.fileName || buildFileName({ ...options, format })
  downloadBlob(blob, fileName)
  return fileName
}
