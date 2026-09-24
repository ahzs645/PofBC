// Finding the letters in a line of drawn type, and where the metrics say that line was set.
//
// Shared by the scripts that take letters out of published artwork and the ones that set new
// wording on a published line, so both read the artwork the same way.

import { EXTENTS, KERNING, WIDTHS } from '../src/current/nameMetrics.js'

const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const half = sorted.length >> 1
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}

/**
 * Contours gathered into letters, left to right: a counter, a dot or an accent sits over the
 * letter it belongs to.
 *
 * @param {{ subpath: any[], box: { left: number, top: number, right: number, bottom: number } }[]} contours
 */
export function groupLetters (contours) {
  const letters = []
  for (const contour of [...contours].sort((a, b) => a.box.left - b.box.left)) {
    const owner = letters.find(({ box }) => {
      const overlap = Math.min(box.right, contour.box.right) - Math.max(box.left, contour.box.left)
      return overlap > 0.6 * Math.min(box.right - box.left, contour.box.right - contour.box.left)
    })
    if (owner) {
      owner.subpaths.push(contour.subpath)
      owner.box = {
        left: Math.min(owner.box.left, contour.box.left),
        top: Math.min(owner.box.top, contour.box.top),
        right: Math.max(owner.box.right, contour.box.right),
        bottom: Math.max(owner.box.bottom, contour.box.bottom)
      }
    } else letters.push({ subpaths: [contour.subpath], box: { ...contour.box } })
  }
  return letters.sort((a, b) => a.box.left - b.box.left)
}

/** Each non-space character of a line, with where its pen sits in 1/1000 em. */
export function pensOf (text, tracking) {
  const out = []
  let pen = 0
  ;[...text].forEach((character, index) => {
    if (character !== ' ') out.push({ character, pen })
    pen += WIDTHS[character]
    const next = text[index + 1]
    if (next !== undefined) pen += tracking + (KERNING[character + next] ?? 0)
  })
  return out
}

/**
 * The size, pen origin and baseline a drawn line was set at, by least squares on where its
 * reference letters' ink starts and ends.
 *
 * Only letters `isReference` accepts have a say: a letter being lifted has no metrics-backed
 * position to check, and a pair respaced by hand would pull the fit away from every other letter.
 *
 * @returns {{ size: number, origin: number, baseline: number, worst: number, pens: { character: string, pen: number }[] }}
 *   `worst` is the largest ink-edge disagreement, in 1/1000 em.
 */
export function fitLine ({ text, letters, tracking, isReference }) {
  const pens = pensOf(text, tracking)
  if (pens.length !== letters.length) {
    throw new Error(`found ${letters.length} letters, "${text}" has ${pens.length}`)
  }

  const known = pens.map((p, i) => ({ ...p, drawn: letters[i] })).filter(({ character }) => isReference(character))
  const samples = known.flatMap(({ character, pen, drawn }) => [
    [(pen + EXTENTS[character][0]) / 1000, drawn.box.left],
    [(pen + EXTENTS[character][1]) / 1000, drawn.box.right]
  ])
  const mx = samples.reduce((sum, [a]) => sum + a, 0) / samples.length
  const my = samples.reduce((sum, [, b]) => sum + b, 0) / samples.length
  const size = samples.reduce((sum, [a, b]) => sum + (a - mx) * (b - my), 0) /
    samples.reduce((sum, [a]) => sum + (a - mx) ** 2, 0)
  const origin = my - size * mx
  const worst = Math.max(...samples.map(([a, b]) => Math.abs(origin + size * a - b))) * 1000 / size
  const baseline = median(known.map(({ character, drawn }) => drawn.box.bottom - size * EXTENTS[character][3] / 1000))

  return { size, origin, baseline, worst, pens }
}
