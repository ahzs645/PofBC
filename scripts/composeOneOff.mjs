// One-off marks put together from the parts of others, for marks the Province published but whose
// artwork has not been obtained.
//
// BC Parks set “BCParks” beside the shaded sun in 2005–2007 and beside the Best Place on Earth mark
// in 2010–2016 (src/gallery/timelines.js). Both were drawn from the BC mark the gallery already
// holds and from letters of the same Garamond the Province published: WorkBC's “BC” and its
// “k”, and the Best Place on Earth tagline's “P”, “a”, “r” and “s”, scaled to the same x-height. The
// arrangement is read off the archived pictures, which are small. So these are reconstructions, and
// say so: the letters are the Province's own, their spacing and placing are not measured from the
// marks' artwork.

import { boundsOf } from './svgAbsolute.mjs'
import { lettersOf, transformed } from './glyphs.mjs'
import { absolute } from './svgAbsolute.mjs'

const union = (boxes) => boxes.reduce((a, b) => ({
  left: Math.min(a.left, b.left), top: Math.min(a.top, b.top), right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom)
}), { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity })

const shapeOf = (mark, role) => mark.shapes.find((shape) => shape.role === role)
const subpathsOf = (mark, role) => absolute(shapeOf(mark, role).d)
const boxOf = (subpaths) => union(subpaths.map(boundsOf))
const rectangle = (left, top, width, height) => [[['M', left, top], ['L', left + width, top], ['L', left + width, top + height], ['L', left, top + height], ['Z']]]

/**
 * “BCParks” in the Province's Garamond, on a baseline at y = 0 with its cap height `cap`, from x = 0.
 * Each letter keeps its outline; the gaps between them are the sources' own where the pair occurs
 * there (B–C, r–k, a–r), and the tagline's between neighbouring letters elsewhere.
 */
export function bcParks (marks, cap) {
  const work = marks['work-bc']
  const tagline = lettersOf(shapeOf(marks['best-place-on-earth'], 'tagline').d)
  const accent = lettersOf(shapeOf(work, 'accent').d)
  const name = lettersOf(shapeOf(work, 'name').d)
  // Baselines: the bottom of a flat-footed capital in each source.
  const workBase = accent[0].box.bottom
  const tagBase = tagline[2].box.bottom
  const workCap = accent[0].box.bottom - accent[0].box.top
  // The tagline's B against WorkBC's B: one Garamond at two sizes.
  const tagScale = workCap / (tagline[2].box.bottom - tagline[2].box.top)
  const gap = (a, b, scale = 1) => (b.box.left - a.box.right) * scale
  const letters = [
    { letter: accent[0], scale: 1, base: workBase },
    { letter: accent[1], scale: 1, base: workBase, before: gap(accent[0], accent[1]) },
    // Between the two words of WorkBC: its k and its B.
    { letter: tagline[6], scale: tagScale, base: tagBase, before: gap(name[3], accent[0]) },
    // P to a: the tagline's P to its l, the next letter it sets.
    { letter: tagline[8], scale: tagScale, base: tagBase, before: gap(tagline[6], tagline[7], tagScale) },
    { letter: tagline[15], scale: tagScale, base: tagBase, before: gap(tagline[14], tagline[15], tagScale) },
    { letter: name[3], scale: 1, base: workBase, before: gap(name[2], name[3]) },
    // k to s: the tagline's e to its s, in “Best”.
    { letter: tagline[4], scale: tagScale, base: tagBase, before: gap(tagline[3], tagline[4], tagScale) }
  ]
  const unit = cap / workCap
  let x = 0
  const subpaths = []
  for (const { letter, scale, base, before = 0 } of letters) {
    x += before * unit
    const s = scale * unit
    subpaths.push(...transformed(letter.subpaths, s, x - letter.box.left * s, -base * s))
    x += (letter.box.right - letter.box.left) * s
  }
  return subpaths
}

/** A mark's parts moved by (dx, dy) and scaled by `scale`, keeping their roles. */
const moved = (mark, roles, scale, dx, dy) => mark.shapes.filter(({ role }) => roles.includes(role))
  .map(({ role, d }) => ({ role, subpaths: transformed(absolute(d), scale, dx, dy) }))

const SYMBOL = ['sun', 'rays', 'core', 'mountains']
const LOCKUP = ['sun', 'rays', 'core', 'mountains', 'wordmark', 'rule', 'tagline']

/**
 * Builds a composed mark as the one-off build's own shape: parts with roles, the sun the glow is
 * measured from, its gradients, and the colours as published.
 */
export function compose (entry, marks) {
  const source = marks['best-place-on-earth']
  if (entry.compose === 'bc-parks-banner') {
    // The archived banner (2005–2007): the symbol alone, “BCParks” after it. Read off the picture:
    // the name's cap height is 0.61 of the symbol's height, its baseline 0.88 of the way down it,
    // and it starts 0.24 of that height after the symbol.
    const parts = moved(source, SYMBOL, 1, 0, 0)
    const symbol = boxOf(parts.flatMap(({ subpaths }) => subpaths))
    const height = symbol.bottom - symbol.top
    const name = bcParks(marks, 0.61 * height)
    const placed = transformed(name, 1, symbol.right + 0.24 * height, symbol.top + 0.88 * height)
    return {
      shapes: [...parts, { role: 'name', subpaths: placed }],
      sun: source.sun,
      gradients: source.gradients,
      colours: { ...entry.colours }
    }
  }
  if (entry.compose === 'bc-parks-best-place') {
    // The archived mark (2010–2016): the whole Best Place on Earth mark, a thin gold divider the
    // height of it, and the name. Read off the picture, against the mark's height: the divider
    // stands 0.185 of it after the mark, the name 0.21 after the divider, with a cap height of 0.35
    // and its baseline on the mark's foot.
    const parts = moved(source, LOCKUP, 1, 0, 0)
    const mark = boxOf(parts.flatMap(({ subpaths }) => subpaths))
    const height = mark.bottom - mark.top
    const rule = mark.right + 0.185 * height
    const width = 0.022 * height
    const divider = rectangle(rule - width / 2, mark.top, width, height)
    const name = transformed(bcParks(marks, 0.35 * height), 1, rule + 0.21 * height, mark.bottom)
    return {
      shapes: [...parts, { role: 'divider', subpaths: divider }, { role: 'name', subpaths: name }],
      sun: source.sun,
      gradients: source.gradients,
      colours: { ...entry.colours }
    }
  }
  throw new Error(`${entry.id}: no composition called ${entry.compose}`)
}
