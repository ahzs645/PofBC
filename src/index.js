// Province of British Columbia logo generator — public API.
//
// Two layers, deliberately separated:
//
//   * The core (logo/, ministries/) is plain JavaScript with no React dependency. resolveLockup()
//     and the wrapping rules run in Node, in a worker, or under any framework — which is what lets
//     the build scripts check the output against the original artwork.
//   * The React component is a convenience for apps already using React. Importing it pulls in
//     React; importing only the core does not.

// ── Core rendering (framework-free) ───────────────────────────────────────────────────────────────
export {
  renderLockupSvg,
  renderLockupMarkup,
  renderMarkMarkup,
  resolveLockup,
  escapeXml,
  LOGO_FONT_FAMILY,
  MARK_BOX,
  PROVINCE_WORDMARK
} from './logo/renderLogoSvg.js'

// ── Layouts: the three lockups ────────────────────────────────────────────────────────────────────
export {
  LAYOUTS,
  LAYOUT_ORDER,
  getLayout,
  CLEAR_SPACE,
  CLEAR_SPACE_ORDER,
  DEFAULT_CLEAR_SPACE,
  clearSpacePadding
} from './logo/layouts.js'

// ── Text layout: the measuring and wrapping rules the lockups obey ────────────────────────────────
export { measureLine, measureWidth, wrapText, layoutBlock, positionWords } from './logo/logoText.js'
export { outlineLineMarkup, outlineTextMarkup, canOutline } from './logo/textOutline.js'
export { getFaceMetrics } from './logo/fontMetrics.js'

// ── Colour ────────────────────────────────────────────────────────────────────────────────────────
export {
  BRAND_COLORS,
  TRANSPARENT,
  resolveColor,
  parseHex,
  isLightColor,
  contrastRatio,
  describeContrast,
  preferredInkFor
} from './logo/logoColors.js'

// ── Export (browser) ──────────────────────────────────────────────────────────────────────────────
export {
  exportLogo,
  renderLogoBlob,
  buildSvgSource,
  buildFileName,
  downloadBlob,
  isFormatSupported,
  EXPORT_FORMATS,
  EXPORT_FORMAT_ORDER,
  SIZE_PRESETS
} from './export/exportLogo.js'
export { getEmbeddedFontCss, getEmbeddedFaces, BRAND_FONT_FAMILY } from './export/fontEmbed.js'
export { getGlyphOutlines } from './export/fontOutlines.js'

// ── Ministries ────────────────────────────────────────────────────────────────────────────────────
export {
  MINISTRIES,
  MINISTRY_GROUPS,
  MINISTRY_LIST_REVIEWED,
  searchMinistries,
  isKnownMinistry
} from './ministries/ministries.js'

// ── React ─────────────────────────────────────────────────────────────────────────────────────────
export { BcLockup } from './logo/BcLockup.jsx'
