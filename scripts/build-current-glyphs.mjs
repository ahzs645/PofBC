// Turns the Province's 46 ministry marks into one alphabet plus the metrics to set it with.
//
// Every published mark draws its own name as outlines, so the letter "e" is stored forty-odd times
// over — a megabyte of the same few shapes at different sizes and positions. This lifts each
// letter out, moves it onto the font's own origin and em, averages every appearance of it, and
// writes the result once.
//
// Two files come out, and their provenance differs:
//
//   src/current/nameGlyphs.js   the letterforms. Derived wholly from the Province's published
//                               artwork — this is their drawing, deduplicated, not a font file.
//                               Committed, because it is the artwork the app serves.
//   src/current/nameMetrics.js  advance widths, kerning pairs and the ligatures Adobe Garamond
//                               substitutes. Read from the font, but the same reasoning as
//                               src/logo/fontMetrics.js applies: widths are what a layout engine
//                               needs, and they are not the typeface. Committed.
//
// Because both are committed, nothing downstream — a fresh clone, CI, the deployed site — needs a
// licensed font. Only regenerating these two files does.
//
// Run: npm run build:current-glyphs

import * as fontkit from 'fontkit'
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parsePath, pathBounds } from './svgPath.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

// No default path, deliberately. Picking a licensed font up off the machine automatically would
// mean an ordinary `npm run build` quietly bundled it — and a deploy would publish it. Extending
// the alphabet is a decision, so it has to be stated.
const SOURCE = process.env.GARAMOND_SOURCE

// This rebuilds committed files from the published artwork, so it is not part of an ordinary
// build — `npm run build:current` runs it, and it needs both the artwork and the font. Everything
// it produces is committed, so nothing downstream needs either.
if (!SOURCE || !existsSync(SOURCE)) {
  console.error(
    `\nCould not find Adobe Garamond Pro at ${SOURCE}.\n` +
    'Point GARAMOND_SOURCE at a licensed copy:\n\n' +
    '    GARAMOND_SOURCE=/path/to/AGaramondPro-Regular.otf npm run build:current-glyphs\n')
  process.exit(1)
}

const fitPath = resolve(root, 'scripts/current-fit.json')
if (!existsSync(fitPath)) {
  console.error('\nRun `npm run verify:current-names` first — it measures the fit this builds on.\n')
  process.exit(1)
}

const font = fontkit.openSync(SOURCE)
const MARKS = resolve(root, 'public/current-marks')
const fit = JSON.parse(readFileSync(fitPath, 'utf8'))
const { tracking, wordSpace, leading, marks } = fit

// Adobe Garamond substitutes these automatically, so the artwork draws them as single glyphs and
// the layout engine has to do the same or the widths will not match.
const LIGATURES = [['ffi', 'ﬃ'], ['ffl', 'ﬄ'], ['ff', 'ﬀ'], ['fi', 'ﬁ'], ['fl', 'ﬂ']]

// fontkit reports a ligature's *original* code points, so a shaped "ff" comes back as two f's.
// Both directions are needed: one to key the alphabet by the ligature character, one to ask the
// font about it, since laying out the letters is guaranteed to reach the ligature and looking up
// U+FB00 in the cmap is not.
const asLigature = new Map(LIGATURES.map(([from, to]) => [from, to]))
const asLetters = new Map(LIGATURES.map(([from, to]) => [to, from]))
const expand = (character) => asLetters.get(character) ?? character

/** Scales and shifts a path. The extraction emits absolute M, L and C only. */
function mapPath (data, sx, dx, sy, dy) {
  return parsePath(data).map(({ command, values }) => {
    if (command === 'Z' || command === 'z') return 'Z'
    if (!'MLC'.includes(command)) throw new Error(`unexpected path command ${command}`)
    const mapped = values.map((value, i) => (i % 2 === 0 ? value * sx + dx : value * sy + dy))
    return command + mapped.map((v) => round(v)).join(' ').replace(/ -/g, '-')
  }).join('')
}

const round = (value) => String(Math.round(value * 10) / 10).replace(/^(-?)0\./, '$1.')

/** Each glyph of a mark's name, with the character it is and where its pen sat. */
function glyphsOf (key, entry) {
  const source = readFileSync(resolve(root, 'public/current-marks', `${key}.svg`), 'utf8')
  const group = /<g transform="translate\(([-\d.]+) ([-\d.]+)\)">((?:(?!<\/g>).)*?data-role="name".*?)<\/g>/s
    .exec(source)
  const tx = Number(group[1])
  const ty = Number(group[2])

  const drawn = [...group[3].matchAll(/\sd="([^"]+)"/g)].map((match) => {
    const box = pathBounds(match[1])
    return { d: match[1], x: box.minX + tx, foot: box.maxY + ty, tx, ty }
  })

  // The baseline grid, as everywhere else: feet pile up on the baseline and the leading is fixed.
  const feet = drawn.map((g) => g.foot).sort((a, b) => a - b)
  const clusters = []
  for (const foot of feet) {
    const last = clusters.at(-1)
    if (last && foot - last.at(-1) < 0.2) last.push(foot)
    else clusters.push([foot])
  }
  const mean = (c) => c.reduce((a, b) => a + b, 0) / c.length
  const anchored = clusters.filter((c) => c.length >= 2)
  const top = Math.min(...(anchored.length ? anchored : clusters).map(mean))

  const rows = new Map()
  for (const glyph of drawn) {
    const line = Math.round((glyph.foot - top) / leading)
    if (!rows.has(line)) rows.set(line, [])
    rows.get(line).push(glyph)
  }

  const out = []
  const emScale = 1000 / font.unitsPerEm

  entry.lines.forEach((text, index) => {
    const row = (rows.get(index) || []).sort((a, b) => a.x - b.x)
    const run = font.layout(text)
    const baseline = top + index * leading

    let pen = 0
    let advances = 0
    let spaces = 0
    let n = 0

    run.glyphs.forEach((glyph, k) => {
      const code = glyph.codePoints[0]
      if (code !== 32) {
        const joined = String.fromCodePoint(...glyph.codePoints)
        const character = asLigature.get(joined) ?? joined
        // Where this glyph's pen origin landed, in the mark's own points.
        const penX = entry.origin +
          (entry.size / 1000) * (pen * emScale + tracking * advances + wordSpace * spaces)
        if (row[n]) out.push({ character, drawn: row[n], penX, baseline })
        n += 1
      } else spaces += 1
      pen += run.positions[k].xAdvance
      advances += 1
    })
  })

  return out
}

// ── Gather every appearance of every letter ──────────────────────────────────────────────────────

const instances = new Map()

for (const [key, entry] of Object.entries(marks)) {
  for (const { character, drawn, penX, baseline } of glyphsOf(key, entry)) {
    // Onto the font's origin and em: x from the pen, y up from the baseline, scaled to 1000 units.
    // The y axis keeps SVG's downward direction, so these paths drop straight into a <path>.
    const k = 1000 / entry.size
    const path = mapPath(drawn.d, k, (drawn.tx - penX) * k, k, (drawn.ty - baseline) * k)
    if (!instances.has(character)) instances.set(character, [])
    instances.get(character).push(path)
  }
}

// ── Average them ─────────────────────────────────────────────────────────────────────────────────

const signature = (path) => parsePath(path).map((g) => g.command).join('')

/** How far, in 1/1000 em, an instance may sit from the others and still be counted as agreeing. */
const AGREEMENT = 8

const middle = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const half = sorted.length >> 1
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}

const glyphs = {}
const spread = []

for (const [character, paths] of [...instances].sort()) {
  // Instances of one letter are the same drawing, so they share a command sequence. Where a
  // handful disagree — one letter decomposes a curve differently in one mark — the majority wins.
  const bySignature = new Map()
  for (const path of paths) {
    const key = signature(path)
    if (!bySignature.has(key)) bySignature.set(key, [])
    bySignature.get(key).push(path)
  }
  const [, chosen] = [...bySignature].sort((a, b) => b[1].length - a[1].length)[0]

  // The source rounds to two decimals at about five points, so any single appearance carries
  // roughly a unit of quantisation noise per coordinate on a 1000-unit em. Combining every
  // appearance beats that: the letter written out is a better copy than any one of the files it
  // came from.
  //
  // The combination is a coordinate-wise median, not a mean. A few marks are set at their own
  // slightly different size and sit fractionally off the fit, and a mean lets those few drag every
  // letter with them — the spread across an averaged alphabet came out at seventy units per
  // thousand, where the typical mark agrees to under one. A median simply ignores them.
  const parsed = chosen.map(parsePath)
  const combine = (instances) => parsed[0].map(({ command, values }, g) => ({
    command,
    values: values.map((_, v) => middle(instances.map((p) => p[g].values[v])))
  }))

  const deviation = (path, model) => {
    let worst = 0
    path.forEach(({ values }, g) => {
      values.forEach((value, v) => { worst = Math.max(worst, Math.abs(value - model[g].values[v])) })
    })
    return worst
  }

  // One pass to find the letter, a second over only the instances that agree with it, so the
  // reported spread describes the drawing rather than the outliers.
  const provisional = combine(parsed)
  const agreeing = parsed.filter((path) => deviation(path, provisional) <= AGREEMENT)
  const settled = combine(agreeing.length >= 3 ? agreeing : parsed)

  spread.push({
    character,
    n: chosen.length,
    of: paths.length,
    kept: agreeing.length,
    worst: Math.max(...agreeing.map((path) => deviation(path, settled)), 0)
  })

  glyphs[character] = settled.map(({ command, values }) => (
    command === 'Z' ? 'Z' : command + values.map((v) => round(v)).join(' ').replace(/ -/g, '-')
  )).join('')
}

const totalInstances = [...instances.values()].reduce((n, v) => n + v.length, 0)

// ── Letters the good marks missed ────────────────────────────────────────────────────────────────
//
// Three English files merged two lockups when they were extracted from the PDF, so they are left
// out of the fit — and one of them is the only published mark containing a W. The letter is in
// there, just not in a file whose layout can be trusted. Rather than take W from the font and
// commit it, it is found by matching outlines: every glyph in every file, against the shape the
// font says that letter has. What is committed then stays what the Province published.

const FLATNESS = 8
const SAMPLES = 48

/** A path as contours of points, in its own coordinates. */
function contoursOf (data) {
  const contours = []
  let current = []
  let cursor = [0, 0]

  for (const { command, values } of parsePath(data)) {
    if (command === 'M') {
      if (current.length) contours.push(current)
      cursor = [values[0], values[1]]
      current = [cursor]
    } else if (command === 'L') {
      cursor = [values[0], values[1]]
      current.push(cursor)
    } else if (command === 'C') {
      const [x1, y1, x2, y2, x3, y3] = values
      for (let i = 1; i <= FLATNESS; i += 1) {
        const t = i / FLATNESS
        const u = 1 - t
        current.push([
          u ** 3 * cursor[0] + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
          u ** 3 * cursor[1] + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3
        ])
      }
      cursor = [x3, y3]
    }
  }
  if (current.length) contours.push(current)
  return contours.filter((c) => c.length > 2)
}

const RASTER = 48

/**
 * A filled bitmap of a drawing, normalised into the unit square.
 *
 * Comparing point for point does not work here: the font's outline and the PDF's are the same
 * shape described by completely different numbers of segments, so no two points correspond. Filling
 * both and measuring the disagreement compares the shapes themselves and ignores how they are
 * written down.
 */
function rasterOf (contours) {
  const points = contours.flat()
  if (!points.length) return null
  const xs = points.map((p) => p[0])
  const ys = points.map((p) => p[1])
  const x0 = Math.min(...xs)
  const y0 = Math.min(...ys)
  const width = Math.max(Math.max(...xs) - x0, 1e-6)
  const height = Math.max(Math.max(...ys) - y0, 1e-6)

  const edges = []
  for (const contour of contours) {
    for (let i = 0; i < contour.length; i += 1) {
      const a = contour[i]
      const b = contour[(i + 1) % contour.length]
      const ay = (a[1] - y0) / height
      const by = (b[1] - y0) / height
      if (ay === by) continue
      edges.push({ ax: (a[0] - x0) / width, ay, bx: (b[0] - x0) / width, by })
    }
  }

  const bitmap = new Uint8Array(RASTER * RASTER)
  for (let row = 0; row < RASTER; row += 1) {
    const y = (row + 0.5) / RASTER
    const crossings = []
    for (const { ax, ay, bx, by } of edges) {
      if ((y >= ay && y < by) || (y >= by && y < ay)) {
        crossings.push(ax + (y - ay) / (by - ay) * (bx - ax))
      }
    }
    crossings.sort((a, b) => a - b)
    // Even-odd fill: the span between each pair of crossings is inside.
    for (let i = 0; i + 1 < crossings.length; i += 2) {
      const from = Math.max(0, Math.ceil(crossings[i] * RASTER - 0.5))
      const to = Math.min(RASTER - 1, Math.floor(crossings[i + 1] * RASTER - 0.5))
      for (let column = from; column <= to; column += 1) bitmap[row * RASTER + column] = 1
    }
  }
  return bitmap
}

/** Area of disagreement over area of union — 0 is the same drawing. */
const distance = (a, b) => {
  if (!a || !b) return Infinity
  let differ = 0
  let union = 0
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] !== b[i]) differ += 1
    if (a[i] || b[i]) union += 1
  }
  return union ? differ / union : Infinity
}

/** Every name glyph drawn in any published file, trustworthy layout or not. */
function allDrawnGlyphs () {
  const out = []
  for (const file of readdirSync(MARKS).filter((name) => name.endsWith('.svg'))) {
    const source = readFileSync(resolve(MARKS, file), 'utf8')
    for (const group of source.matchAll(/<g transform="translate\(([-\d.]+) ([-\d.]+)\)">((?:(?!<\/g>).)*?data-role="name".*?)<\/g>/gs)) {
      const tx = Number(group[1])
      const ty = Number(group[2])
      for (const match of group[3].matchAll(/\sd="([^"]+)"/g)) out.push({ file, d: match[1], tx, ty })
    }
  }
  return out
}

const needed = new Set()
for (const ministry of JSON.parse(readFileSync(resolve(root, 'public/current-marks/index.json'), 'utf8')).ministries) {
  for (const letter of `Ministry of ${ministry.name}`.replace(/\u00a0/g, ' ')) {
    if (letter !== ' ' && !glyphs[letter]) needed.add(letter)
  }
}

const rescued = []
if (needed.size) {
  const drawn = allDrawnGlyphs().map((item) => ({ ...item, raster: rasterOf(contoursOf(item.d)) }))

  for (const letter of needed) {
    const run = font.layout(letter)
    const glyph = run.glyphs[0]
    if (!glyph?.path?.commands?.length) continue
    const wanted = rasterOf(contoursOf(glyph.path.scale(1, -1).toSVG()))

    let best = null
    for (const item of drawn) {
      // `score`, not `d` — the drawn glyph already has a `d`, and that is its path.
      const score = distance(wanted, item.raster)
      if (score < (best?.score ?? Infinity)) best = { ...item, score }
    }
    // A loose threshold would invent a letter out of a different one; this is tight enough that
    // nothing but the same drawing passes it.
    if (process.env.VERBOSE) {
      console.log(`  looking for "${letter}": closest drawn glyph is ${best?.score?.toFixed(4)} away in ${best?.file}`)
    }
    // Tight enough that only the same drawing passes: a different letter scores an order of
    // magnitude worse, and the Province's own rounding costs only a few per cent.
    if (!best || best.score > 0.08) continue

    // Place it from its own ink: a scale from the height the font says it has, a baseline from its
    // foot, and a pen origin from its left side bearing.
    const box = pathBounds(best.d)
    const em = 1000 / font.unitsPerEm
    const fontBox = glyph.bbox
    // How many em units the drawing covers per point, from the height the font says this letter has.
    const unitsPerPoint = ((fontBox.maxY - fontBox.minY) * em) / (box.maxY - box.minY)
    const baseline = box.maxY + best.ty - (-fontBox.minY * em) / unitsPerPoint
    const penX = box.minX + best.tx - (fontBox.minX * em) / unitsPerPoint

    glyphs[letter] = mapPath(best.d, unitsPerPoint, (best.tx - penX) * unitsPerPoint,
      unitsPerPoint, (best.ty - baseline) * unitsPerPoint)
    rescued.push({ letter, file: best.file, disagreement: best.score })
  }
}

// ── Metrics ──────────────────────────────────────────────────────────────────────────────────────

const emScale = 1000 / font.unitsPerEm

// Widths and kerning cover the whole Latin range a ministry name could use, not just the letters
// the Province happened to publish. They are committed on the same reasoning as
// src/logo/fontMetrics.js — a table of numbers is what a layout engine needs, and is not the
// typeface. The letterforms are what is gated.
const range = (from, to) => Array.from({ length: to - from + 1 }, (_, i) => String.fromCodePoint(from + i))
const CHARSET = [
  ...range(0x20, 0x7e),
  ...range(0xa0, 0xff),
  ...range(0x100, 0x17f),
  ...'\u2010\u2011\u2013\u2014\u2018\u2019\u201c\u201d\u2026\u2039\u203a\u20ac',
  ...LIGATURES.map(([, to]) => to)
]

const characters = [...new Set([...Object.keys(glyphs), ...CHARSET])]
  .filter((character) => {
    const run = font.layout(expand(character))
    return run.glyphs.length && run.glyphs.every((g) => g.id !== 0)
  })

const widths = {}
for (const character of characters) {
  const run = font.layout(expand(character))
  widths[character] = Math.round(run.positions.reduce((total, p) => total + p.xAdvance, 0) * emScale)
}

// Only pairs among letters the marks can actually use. Asking fontkit what it does to each pair is
// slower than reading GPOS but immune to being wrong about how GPOS is structured.
const kerning = {}
let pairs = 0
for (const left of characters) {
  for (const right of characters) {
    const run = font.layout(expand(left) + expand(right))
    // Shaping a pair can produce something other than that pair — "ﬀ" followed by "i" becomes a
    // different ligature entirely — and the advance difference then means nothing. Only a run that
    // came back as the two glyphs asked for describes a kern.
    if (run.glyphs.length !== 2) continue
    if (String.fromCodePoint(...run.glyphs[0].codePoints) !== expand(left)) continue
    if (String.fromCodePoint(...run.glyphs[1].codePoints) !== expand(right)) continue
    const delta = Math.round(run.positions[0].xAdvance * emScale) - widths[left]
    if (delta) { kerning[left + right] = delta; pairs += 1 }
  }
}

const ink = (character) => font.layout(expand(character)).glyphs[0].bbox

// Ink extents come from the averaged glyphs where there is one, so they describe what the app will
// actually draw; from the font otherwise. A lockup's bounding box then hugs the letterforms
// instead of the em.
const extents = {}
const extentsOf = (character) => {
  const d = glyphs[character]
  if (d) {
    const box = pathBounds(d)
    return [Math.round(box.minX), Math.round(box.maxX), Math.round(box.minY), Math.round(box.maxY)]
  }
  const box = font.layout(expand(character)).glyphs[0]?.bbox
  if (!box || !Number.isFinite(box.minY) || box.minY === box.maxY) return null
  return [
    Math.round(box.minX * emScale), Math.round(box.maxX * emScale),
    Math.round(-box.maxY * emScale), Math.round(-box.minY * emScale)
  ]
}

for (const character of characters) {
  const extent = extentsOf(character)
  if (extent) extents[character] = extent
}

writeFileSync(resolve(root, 'src/current/nameGlyphs.js'), `// Generated by scripts/build-current-glyphs.mjs — do not edit.
//
// The alphabet the Province's ministry marks are drawn with, lifted from the published artwork
// itself: every appearance of each letter across the 46 marks, moved onto a common origin and
// 1000-unit em and averaged. It is their drawing, stored once instead of ${instances.size ? [...instances.values()].reduce((n, v) => n + v.length, 0) : 0} times.
//
// Coordinates are in 1/1000 em with the baseline at y=0 and y running downward, which is SVG's
// own direction — a glyph drops into a <path> with only a translate and a scale.

export default {
${Object.entries(glyphs).map(([ch, d]) => `  ${JSON.stringify(ch)}: ${JSON.stringify(d)}`).join(',\n')}
}
`)

writeFileSync(resolve(root, 'src/current/nameMetrics.js'), `// Generated by scripts/build-current-glyphs.mjs — do not edit.
//
// What it takes to set the ministry-mark alphabet: advance widths, the kerning the published marks
// were set with, and the ligatures Adobe Garamond substitutes automatically. All in 1/1000 em.
//
// Measured from Adobe Garamond Pro but committed, on the same reasoning as src/logo/fontMetrics.js:
// widths are what a layout engine needs and are not themselves the typeface. Nothing downstream
// needs the font — only regenerating this file does.

/** Ligature substitutions, longest first so "ffi" wins over "ff". */
export const LIGATURES = ${JSON.stringify(LIGATURES)}

/** Tracking the marks are set with, in 1/1000 em. Measured, not chosen. */
export const TRACKING = ${tracking}

/** Leading, as a multiple of the type size. The marks are set solid. */
export const LEADING = ${Number((leading / median(Object.values(marks).map((m) => m.size))).toFixed(4))}

export const CAP_HEIGHT = ${Math.round(ink('M').maxY * emScale)}
export const ASCENDER = ${Math.round(ink('f').maxY * emScale)}
export const DESCENDER = ${Math.round(-ink('y').minY * emScale)}

export const WIDTHS = ${JSON.stringify(widths)}

export const KERNING = ${JSON.stringify(kerning)}

/** Ink bounds of each drawn letter as [left, right, top, bottom], y downward from the baseline. */
export const EXTENTS = ${JSON.stringify(extents)}
`)

function median (values) {
  const sorted = [...values].sort((a, b) => a - b)
  return sorted[Math.floor(sorted.length / 2)]
}

const glyphBytes = Object.values(glyphs).join('').length
const worstSpread = spread.reduce((a, b) => (b.worst > a.worst ? b : a))
const outliers = spread.filter((s) => s.n !== s.of)

console.log(`  alphabet    ${String(Object.keys(glyphs).length).padStart(3)} letters from ${totalInstances} drawn instances   ${(glyphBytes / 1024).toFixed(1)} KB`)
console.log(`  metrics     ${String(Object.keys(widths).length).padStart(3)} widths, ${pairs} kerning pairs`)
const kept = spread.reduce((n, s) => n + s.kept, 0)
console.log(`  agreement   ${kept}/${totalInstances} instances agree to within ${AGREEMENT}/1000 em; `
  + `worst remaining spread ${worstSpread.worst.toFixed(1)} on "${worstSpread.character}"`)
if (process.env.VERBOSE) {
  for (const s of [...spread].sort((a, b) => b.worst - a.worst).slice(0, 12)) {
    console.log(`              "${s.character}"  ${s.worst.toFixed(1).padStart(6)}  over ${s.n} instances`)
  }
}
for (const o of outliers) {
  console.log(`              "${o.character}" drawn two ways; took the ${o.n} of ${o.of} that share a contour`)
}
for (const r of rescued) {
  console.log(`  rescued     "${r.letter}" from ${r.file} (${(100 * r.disagreement).toFixed(1)}% disagreement), ` +
    'which the fit had to leave out')
}
console.log('  → src/current/nameGlyphs.js, src/current/nameMetrics.js')

