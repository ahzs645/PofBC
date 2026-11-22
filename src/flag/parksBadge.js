// The badge lockups — the ones that put the symbol inside a frame.
//
// BC Parks is the one of these everybody knows: a rounded square, thickly drawn, holding "BC" and
// the flag on one line with "Parks" beneath at the same size. It is not a ministry lockup with a
// small name under it — both words are the wordmark, and they are set alike.
//
// The frame is the real artwork, not a shape fitted to it. It was a superellipse until the drawing
// turned up, and the drawing is not symmetrical — its wall runs 30.3 units on the left against
// 30.5 on the right, 29.6 at the top against 30.7 at the bottom. It was drawn by hand, and no
// fitted curve was going to find that.

import { PARKS_FRAME } from '../assets/parksFrame.js'
import { getFaceMetrics } from '../logo/fontMetrics.js'
import { measureLine, positionWords } from '../logo/logoText.js'
import { FLAG_ASPECT } from './flagLayout.js'

const sizeForCap = (cap, face) => cap * 1000 / face.capHeight

const round = (value) => Math.round(value * 100) / 100

/**
 * The frame with a thinner wall: its outer edge as drawn, and its inner edge scaled out about the
 * hole's middle until the wall is `wall` units across. Scaling keeps the inner edge's hand-drawn
 * shape, its corners widening with it, which a stroke or an offset of the outer edge would not.
 */
export const thinFrame = (wall) => {
  const { width, height, inner, d } = PARKS_FRAME
  const at = d.lastIndexOf('M')
  const [, mx, my, rest] = /^M(-?[\d.]+)[ ,](-?[\d.]+)(.*)$/s.exec(d.slice(at))
  const k = (width - 2 * wall) / inner.width
  const cx = inner.x + inner.width / 2
  const cy = inner.y + inner.height / 2
  // Every number after the move is a relative step, so it scales as it stands.
  const steps = rest.replace(/-?(?:\d+\.?\d*|\.\d+)/g, (n) => String(round(Number(n) * k)))
  const hole = { width: inner.width * k, height: inner.height * k }
  return {
    width,
    height,
    inner: { x: cx - hole.width / 2, y: cy - hole.height / 2, ...hole },
    d: `${d.slice(0, at)}M${round(cx + (Number(mx) - cx) * k)} ${round(cy + (Number(my) - cy) * k)}${steps}`
  }
}

/**
 * The badge's proportions, as multiples of the wordmark's cap height.
 *
 * Measured off the BC Parks mark: its letters stand about 135 units against a frame whose inner
 * edge is 562 across, and the numbers below are that reading reduced to cap heights.
 */
export const BADGE = {
  /** Flag height, and how far its foot sits below the letters' baseline. */
  flagHeight: 1.33,
  flagGap: 0.1,
  /** Baseline to baseline, between the two words. */
  linePitch: 1.11,
  /** Clear space between the wording and the frame's inner edge, as a share of the frame. */
  inset: 0.06
}

const escapeXml = (value) => String(value)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

/**
 * Lays a badge out, in units where the wordmark's cap height is `cap`.
 *
 * The origin is the frame's top-left corner, and y runs downward.
 *
 * @param {object} options
 * @param {string} [options.first]   The word beside the flag. "BC" in the mark everyone knows.
 * @param {string} [options.second]  The word beneath it.
 * @param {number} [options.cap]     Wordmark cap height.
 * @param {string} [options.weight]  'bold', as BC Parks', or 'regular'.
 * @param {number} [options.wall]    A thinner frame wall, in frame units (BC Parks' is about 30).
 * @param {number} [options.inset]   Clear space inside the frame, as a share of the hole.
 */
export const layoutBadge = ({ first = 'BC', second = 'Parks', cap = 100, weight = 'bold', wall, inset = BADGE.inset } = {}) => {
  const style = { fontSize: sizeForCap(cap, getFaceMetrics(weight)), weight }
  const frame = wall ? thinFrame(wall) : PARKS_FRAME
  const top = measureLine(first, style)
  const bottom = measureLine(second, style)

  const flagHeight = BADGE.flagHeight * cap
  const flagWidth = flagHeight * FLAG_ASPECT
  const topWidth = (top.inkRight - top.inkLeft) + BADGE.flagGap * cap + flagWidth
  const bottomWidth = bottom.inkRight - bottom.inkLeft

  const contentWidth = Math.max(topWidth, bottomWidth)
  const contentTop = Math.min(-top.inkTop, -flagHeight)
  const contentBottom = BADGE.linePitch * cap - bottom.inkBottom
  const contentHeight = contentBottom - contentTop

  // The frame is a fixed drawing, so the wording is fitted into its hole rather than the frame
  // being grown around the wording. Whichever way the wording runs longer decides the scale.
  const hole = frame.inner
  const room = { width: hole.width * (1 - 2 * inset), height: hole.height * (1 - 2 * inset) }
  const scale = Math.min(room.width / contentWidth, room.height / contentHeight)
  const side = frame.width

  // Centred in the hole, in the frame's own units.
  const originX = hole.x + (hole.width - contentWidth * scale) / 2 - top.inkLeft * scale
  const originY = hole.y + (hole.height - contentHeight * scale) / 2 - contentTop * scale

  return {
    cap,
    scale,
    side,
    frame,
    first: { text: first, style, x: originX, y: originY, ink: top, scale },
    second: {
      text: second,
      style,
      x: hole.x + (hole.width - contentWidth * scale) / 2 - bottom.inkLeft * scale,
      y: originY + BADGE.linePitch * cap * scale,
      ink: bottom,
      scale
    },
    flag: {
      x: originX + (top.inkRight - top.inkLeft + top.inkLeft + BADGE.flagGap * cap) * scale,
      y: originY - flagHeight * scale,
      width: flagWidth * scale,
      height: flagHeight * scale
    },
    box: { x: 0, y: 0, width: side, height: frame.height }
  }
}

/**
 * The frame as a single path.
 *
 * Two contours in one, filled even-odd, so the inner one cuts a hole in the outer rather than
 * being painted over it — which is what lets a background show through the middle.
 */
export const frameMarkup = (layout, fill) =>
  `<path data-role="frame" fill-rule="evenodd" d="${layout.frame.d}" fill="${escapeXml(fill)}"/>`

/** The two words, as lines the shared text machinery can draw. */
export const badgeLines = (layout) => [layout.first, layout.second].map((line) => {
  // The wording is fitted into a fixed frame, so its size carries the fit rather than the caller
  // scaling a group around it — which would scale the frame too.
  const style = { ...line.style, fontSize: line.style.fontSize * line.scale }
  return {
    text: line.text,
    style,
    x: line.x,
    y: line.y,
    words: positionWords(line.text, style),
    ink: line.ink
  }
})
