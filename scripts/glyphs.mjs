// Letters lifted out of a one-off's lettering, one compound shape each.
//
// The published files set a line of type as one path, or one path per letter with its counters as
// separate subpaths. Either way a letter is a contour and the contours inside it (the bowl of a P,
// the eye of an e), so they are grouped by containment and read left to right.

import { absolute, boundsOf } from './svgAbsolute.mjs'

const inside = (a, b, slack = 0.05) => a.left >= b.left - slack && a.right <= b.right + slack && a.top >= b.top - slack && a.bottom <= b.bottom + slack

/** The letters of a path's data, left to right: each { subpaths, box }. */
export function lettersOf (d) {
  const contours = absolute(d).map((subpath) => ({ subpath, box: boundsOf(subpath) }))
    .sort((a, b) => (b.box.right - b.box.left) * (b.box.bottom - b.box.top) - (a.box.right - a.box.left) * (a.box.bottom - a.box.top))
  const letters = []
  for (const contour of contours) {
    const outer = letters.find((letter) => inside(contour.box, letter.box))
    if (outer) outer.subpaths.push(contour.subpath)
    else letters.push({ subpaths: [contour.subpath], box: contour.box })
  }
  return letters.sort((a, b) => a.box.left - b.box.left)
}

/** Subpaths scaled by `scale` about the origin, then moved by (dx, dy). */
export const transformed = (subpaths, scale, dx, dy) => subpaths.map((subpath) =>
  subpath.map(([command, ...values]) => [command, ...values.map((value, i) => value * scale + (i % 2 === 0 ? dx : dy))]))
