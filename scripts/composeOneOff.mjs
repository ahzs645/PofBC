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

/**
 * “Coroners Service” in the Province's Garamond, on a baseline at y = 0 with its cap height `cap`,
 * from x = 0. “Service” is BC Wildfire Service's own word, with its own spacing. “Coroners” takes its
 * C from that mark's “BC”, its o, r, n and e from Environmental Reporting BC's name and its s from BC
 * Stats', each scaled to the same x-height. The gaps between the letters of “Coroners”, and the word
 * space, are measured off the lockup as the Coroners Service's reports print it (a 1241 × 385 image
 * whose C is 80 pixels tall), as a fraction of the cap height.
 */
export function coronersService (marks, cap) {
  const wild = marks['bc-wildfire-service-one-line']
  const wildName = lettersOf(shapeOf(wild, 'name').d)
  const wildAccent = lettersOf(shapeOf(wild, 'accent').d)
  const env = lettersOf(shapeOf(marks['environmental-reporting-bc'], 'name').d)
  const stats = lettersOf(shapeOf(marks['bc-stats'], 'name').d)
  // Each source's x-height, from its e (BC Wildfire Service, Environmental Reporting BC) or its a.
  const xOf = (letter) => letter.box.bottom - letter.box.top
  const wildX = xOf(wildName[9])
  const envScale = wildX / xOf(env[19])
  const statsScale = wildX / xOf(stats[2])
  // Baselines: the foot of a flat-footed letter in each source (an r, a t).
  const wildBase = wildName[10].box.bottom
  const envUpper = env[9].box.bottom
  const statsBase = stats[1].box.bottom
  const unit = cap / (wildAccent[1].box.bottom - wildAccent[1].box.top)
  // A gap in the printed lockup, in pixels against its 80-pixel C, or one in the source's own units.
  const printed = (pixels) => ({ gap: pixels / 80 * cap })
  const own = (a, b) => ({ gap: (b.box.left - a.box.right) * unit })
  const fromEnv = (letter, gap) => ({ letter, scale: envScale, base: envUpper, ...gap })
  const letters = [
    { letter: wildAccent[1], scale: 1, base: wildBase },
    fromEnv(env[11], printed(5)),
    fromEnv(env[9], printed(7)),
    fromEnv(env[11], printed(2)),
    fromEnv(env[13], printed(7)),
    fromEnv(env[19], printed(4)),
    { letter: wildName[10], scale: 1, base: wildBase, ...printed(4) },
    { letter: stats[4], scale: statsScale, base: statsBase, ...printed(2) },
    { letter: wildName[8], scale: 1, base: wildBase, ...printed(34) },
    ...wildName.slice(9).map((letter, i) => ({
      letter, scale: 1, base: wildBase,
      // The i's dot sits over its stem rather than after it.
      ...(letter === wildName[13] ? { gap: (wildName[13].box.left - wildName[12].box.right) * unit } : own(wildName[8 + i], letter))
    }))
  ]
  let x = 0
  const subpaths = []
  for (const { letter, scale, base, gap = 0 } of letters) {
    x += gap
    const s = scale * unit
    subpaths.push(...transformed(letter.subpaths, s, x - letter.box.left * s, -base * s))
    x += (letter.box.right - letter.box.left) * s
  }
  return subpaths
}

/**
 * “BCOnLine” in the Province's Garamond, on a baseline at y = 0 with its cap height `cap`, from x = 0,
 * as two parts: the accent (“BC”, WelcomeBC's own) and the name (“OnLine”). The L, n, i and e are
 * Environmental Lab BC's; no held mark sets a Garamond capital O, so the O is the BC mark's own, from
 * COLUMBIA, enlarged from its small-cap size to the capitals'. The gaps are measured off the logo as
 * BC OnLine published it (a 372 × 49 image whose capitals are 27 pixels tall), as fractions of the
 * cap height.
 */
export function bcOnLine (marks, cap) {
  const accent = lettersOf(shapeOf(marks['welcome-bc'], 'accent').d)
  const lab = lettersOf(shapeOf(marks['environmental-lab-bc'], 'name').d)
  const wordmark = lettersOf(shapeOf(marks['best-place-on-earth'], 'wordmark').d)
  const height = (letter) => letter.box.bottom - letter.box.top
  const L = lab[1]
  const labScale = cap / height(L)
  const accentScale = cap / height(accent[0])
  // A round capital stands a little above and below the flat ones it sits with.
  const O = wordmark[2]
  const oScale = (cap * 1.03) / height(O)
  const printed = (pixels) => pixels / 27 * cap
  const letters = [
    { part: 'accent', letter: accent[0], scale: accentScale, base: accent[0].box.bottom },
    { part: 'accent', letter: accent[1], scale: accentScale, base: accent[0].box.bottom, gap: printed(3) },
    { part: 'name', letter: O, scale: oScale, base: O.box.bottom - (cap * 0.015) / oScale, gap: printed(3) },
    { part: 'name', letter: lab[3], scale: labScale, base: lab[3].box.bottom, gap: printed(2) },
    { part: 'name', letter: L, scale: labScale, base: L.box.bottom, gap: printed(3) },
    { part: 'name', letter: lab[6], scale: labScale, base: lab[6].box.bottom, gap: printed(2) },
    // The i's dot sits over its stem, where the source sets it.
    { part: 'name', letter: lab[7], scale: labScale, base: lab[6].box.bottom, gap: (lab[7].box.left - lab[6].box.right) * labScale },
    { part: 'name', letter: lab[3], scale: labScale, base: lab[3].box.bottom, gap: printed(3) - (lab[7].box.right - lab[6].box.right) * labScale },
    { part: 'name', letter: lab[12], scale: labScale, base: lab[12].box.bottom, gap: printed(2) }
  ]
  let x = 0
  const parts = { accent: [], name: [] }
  for (const { part, letter, scale, base, gap = 0 } of letters) {
    x += gap
    parts[part].push(...transformed(letter.subpaths, scale, x - letter.box.left * scale, -base * scale))
    x += (letter.box.right - letter.box.left) * scale
  }
  return parts
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
  if (entry.compose === 'coroners-service') {
    // The BC mark without its tagline, a thin gold divider the height of it, and the name. Measured
    // off the lockup as the Coroners Service's reports print it, against the mark's height: the
    // divider stands 0.187 of it after the mark and 0.009 wide, the name 0.178 after the divider,
    // with a cap height of 0.36 and its baseline on the wordmark's foot.
    const parts = moved(source, [...SYMBOL, 'wordmark'], 1, 0, 0)
    const mark = boxOf(parts.flatMap(({ subpaths }) => subpaths))
    const height = mark.bottom - mark.top
    const rule = mark.right + 0.187 * height
    const width = 0.009 * height
    const divider = rectangle(rule - width / 2, mark.top, width, height)
    const name = transformed(coronersService(marks, 0.36 * height), 1, rule + 0.178 * height, mark.bottom)
    return {
      shapes: [...parts, { role: 'divider', subpaths: divider }, { role: 'name', subpaths: name }],
      sun: source.sun,
      gradients: source.gradients,
      colours: { ...entry.colours }
    }
  }
  if (entry.compose === 'bc-online') {
    // The BC mark set horizontally, its wordmark beside the symbol rather than under it, then a short
    // gold divider and the name. Measured off the published logo, against the symbol's height (49
    // pixels there): the wordmark 6 after the symbol, 10 below its top and 28 tall; the divider 19
    // after the wordmark, 2 wide and as tall as it; the name 20 after the divider, its capitals 27
    // tall on the wordmark's foot.
    const symbolParts = moved(source, SYMBOL, 1, 0, 0)
    const symbol = boxOf(symbolParts.flatMap(({ subpaths }) => subpaths))
    const unit = (symbol.bottom - symbol.top) / 49
    const nativeWordmark = boxOf(subpathsOf(source, 'wordmark'))
    const wordScale = (28 * unit) / (nativeWordmark.bottom - nativeWordmark.top)
    const wordLeft = symbol.right + 6 * unit
    const wordTop = symbol.top + 10 * unit
    const wordmark = moved(source, ['wordmark'], wordScale, wordLeft - nativeWordmark.left * wordScale, wordTop - nativeWordmark.top * wordScale)
    const wordRight = wordLeft + (nativeWordmark.right - nativeWordmark.left) * wordScale
    const ruleLeft = wordRight + 19 * unit
    const divider = rectangle(ruleLeft, wordTop, 2 * unit, 28 * unit)
    const set = bcOnLine(marks, 27 * unit)
    // These letters set wider than the logo's, the enlarged O most of all: the name is scaled as a
    // whole to the logo's measured width, 162 pixels, rather than any letter being narrowed.
    const width = boxOf([...set.accent, ...set.name]).right
    const fit = Math.min(1, (162 * unit) / width)
    const accent = transformed(set.accent, fit, 0, 0)
    const name = transformed(set.name, fit, 0, 0)
    const nameLeft = ruleLeft + 2 * unit + 20 * unit
    const baseline = wordTop + 28 * unit
    return {
      shapes: [
        ...symbolParts, ...wordmark,
        { role: 'divider', subpaths: divider },
        { role: 'accent', subpaths: transformed(accent, 1, nameLeft, baseline) },
        { role: 'name', subpaths: transformed(name, 1, nameLeft, baseline) }
      ],
      sun: source.sun,
      gradients: source.gradients,
      colours: { ...entry.colours }
    }
  }
  throw new Error(`${entry.id}: no composition called ${entry.compose}`)
}
