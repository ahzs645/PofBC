// Checks that typesetting a ministry name reproduces the Province's published artwork.
//
// The marks store their wording as outlines. Replacing those outlines with live text is only
// defensible if the text lands in the same place, so this shapes each recovered name in Adobe
// Garamond Pro and measures every glyph against where the published file actually put it.
//
// Two design constants fall out of the fit and are reported here rather than guessed at: the
// tracking the marks are set with, and how wide their word space is. Both are what
// src/current/currentLayout.js uses.
//
// Run: npm run verify:current-names

import * as fontkit from 'fontkit'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { pathBounds } from './svgPath.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')

// The B.C. Visual Identity Program specifies Adobe Garamond Pro. It is licensed, so it is never
// committed; GARAMOND_SOURCE points at a copy.
// No default path, deliberately. Picking a licensed font up off the machine automatically would
// mean an ordinary `npm run build` quietly bundled it — and a deploy would publish it. Extending
// the alphabet is a decision, so it has to be stated.
const SOURCE = process.env.GARAMOND_SOURCE

const LEADING = 8.10

if (!SOURCE || !existsSync(SOURCE)) {
  console.error(
    `\nCould not find Adobe Garamond Pro at ${SOURCE}.\n` +
    'The B.C. Visual Identity Program specifies it for the ministry marks. Point GARAMOND_SOURCE\n' +
    'at a licensed copy:\n\n' +
    '    GARAMOND_SOURCE=/path/to/AGaramondPro-Regular.otf npm run verify:current-names\n')
  process.exit(1)
}

const font = fontkit.openSync(SOURCE)
const names = JSON.parse(readFileSync(resolve(root, 'scripts/current-names.json'), 'utf8'))

/** Every glyph of a mark's name, grouped into lines and ordered left to right. */
function artworkLines (file) {
  const source = readFileSync(resolve(root, 'public/current-marks', file), 'utf8')
  const group = /<g transform="translate\(([-\d.]+) ([-\d.]+)\)">((?:(?!<\/g>).)*?data-role="name".*?)<\/g>/s
    .exec(source)
  if (!group) return null

  const tx = Number(group[1])
  const ty = Number(group[2])
  const glyphs = [...group[3].matchAll(/\sd="([^"]+)"/g)].map((match) => {
    const box = pathBounds(match[1])
    return { x: box.minX + tx, foot: box.maxY + ty }
  })

  // Same baseline-grid trick the recovery uses: feet pile up on the baseline, and the leading is
  // a constant, so each glyph snaps to a line rather than being clustered by proximity.
  const feet = glyphs.map((g) => g.foot).sort((a, b) => a - b)
  const clusters = []
  for (const foot of feet) {
    const last = clusters.at(-1)
    if (last && foot - last.at(-1) < 0.2) last.push(foot)
    else clusters.push([foot])
  }
  const anchored = clusters.filter((c) => c.length >= 2)
  const mean = (c) => c.reduce((a, b) => a + b, 0) / c.length
  const top = Math.min(...(anchored.length ? anchored : clusters).map(mean))

  const rows = new Map()
  for (const glyph of glyphs) {
    const key = Math.round((glyph.foot - top) / LEADING)
    if (!rows.has(key)) rows.set(key, [])
    rows.get(key).push(glyph)
  }
  return [...rows.entries()].sort((a, b) => a[0] - b[0])
    .map(([, row]) => row.sort((a, b) => a.x - b.x))
}

/**
 * Where shaping says each visible glyph's ink starts, in 1/1000 em, plus how many advances and
 * word spaces precede it. Those counts are what let tracking and word spacing be fitted.
 */
function shape (text, kern) {
  const run = font.layout(text, kern ? undefined : { kern: false, liga: true })
  const scale = 1000 / font.unitsPerEm
  const out = []
  let pen = 0
  let advances = 0
  let spaces = 0

  run.glyphs.forEach((glyph, index) => {
    const space = glyph.codePoints[0] === 32
    if (!space) out.push({ ink: (pen + glyph.bbox.minX) * scale, advances, spaces })
    else spaces += 1
    pen += run.positions[index].xAdvance
    advances += 1
  })
  return out
}

/**
 * Least-squares fit of origin, type size, tracking and word space for one mark.
 *
 * The obvious model — actual = origin + size × (ink + tracking·k + wordSpace·w) — is not linear,
 * because size multiplies the two spacing terms. Solving instead for size×tracking and
 * size×wordSpace makes it linear in all four unknowns, and the two are divided back out at the
 * end. Fitting size rather than taking a measured estimate matters: a handful of marks are set a
 * fraction larger than the rest, and an assumed size shows up as spurious tracking.
 */
function fit (rows) {
  const basis = rows.map((r) => [1, r.ink, r.k, r.w])
  const target = rows.map((r) => r.actual)

  const A = Array.from({ length: 4 }, () => new Array(4).fill(0))
  const b = new Array(4).fill(0)
  basis.forEach((row, n) => {
    for (let i = 0; i < 4; i += 1) {
      b[i] += row[i] * target[n]
      for (let j = 0; j < 4; j += 1) A[i][j] += row[i] * row[j]
    }
  })

  const solved = solve(A, b)
  if (!solved) return null
  const [origin, size, scaledTracking, scaledWordSpace] = solved
  if (!(size > 0)) return null

  let worst = 0
  for (const r of rows) {
    const model = origin + size * r.ink + scaledTracking * r.k + scaledWordSpace * r.w
    worst = Math.max(worst, Math.abs(r.actual - model))
  }
  return {
    origin,
    size: size * 1000,
    tracking: scaledTracking / size,
    wordSpace: scaledWordSpace / size,
    worst
  }
}

/**
 * Refit one mark for origin and size alone, with tracking and word space held at the values shared
 * across every mark.
 *
 * The four-parameter fit above is the right way to *discover* those two constants, but the wrong
 * way to describe any single mark: a name with one word space leaves that term almost
 * unconstrained, so it absorbs whatever error is going and drags tracking with it. Once the
 * constants are known, two parameters describe a mark honestly — and these are the two a build
 * actually needs.
 */
function refit (rows, tracking, wordSpace) {
  const adjusted = rows.map((r) => ({ ...r, ink: r.ink + tracking * r.k + wordSpace * r.w }))
  const basis = adjusted.map((r) => [1, r.ink])
  const target = adjusted.map((r) => r.actual)

  const A = [[0, 0], [0, 0]]
  const b = [0, 0]
  basis.forEach((row, n) => {
    for (let i = 0; i < 2; i += 1) {
      b[i] += row[i] * target[n]
      for (let j = 0; j < 2; j += 1) A[i][j] += row[i] * row[j]
    }
  })

  const solved = solve(A, b)
  if (!solved) return null
  const [origin, size] = solved
  if (!(size > 0)) return null

  let worst = 0
  for (const r of adjusted) worst = Math.max(worst, Math.abs(r.actual - (origin + size * r.ink)))
  return { origin, size: size * 1000, worst }
}

/** Gaussian elimination with partial pivoting, for the small normal-equation systems above. */
function solve (A, b) {
  const n = b.length
  const m = A.map((row, i) => [...row, b[i]])
  for (let col = 0; col < n; col += 1) {
    let pivot = col
    for (let r = col + 1; r < n; r += 1) {
      if (Math.abs(m[r][col]) > Math.abs(m[pivot][col])) pivot = r
    }
    if (Math.abs(m[pivot][col]) < 1e-12) return null
    ;[m[col], m[pivot]] = [m[pivot], m[col]]
    for (let r = 0; r < n; r += 1) {
      if (r === col) continue
      const factor = m[r][col] / m[col][col]
      for (let c = col; c <= n; c += 1) m[r][c] -= factor * m[col][c]
    }
  }
  return m.map((row, i) => row[n] / row[i])
}

const results = []
const skipped = []

for (const [key, entry] of Object.entries(names)) {
  const lines = artworkLines(`${key}.svg`)
  if (!lines) { skipped.push([key, 'no name group']); continue }
  if (lines.length !== entry.lines.length) {
    skipped.push([key, `${lines.length} drawn lines vs ${entry.lines.length} recovered`])
    continue
  }

  for (const kern of [true, false]) {
    const rows = []
    let mismatch = null
    entry.lines.forEach((text, index) => {
      const shaped = shape(text, kern)
      if (shaped.length !== lines[index].length) {
        mismatch = `line ${index + 1}: ${shaped.length} shaped vs ${lines[index].length} drawn`
        return
      }
      shaped.forEach((glyph, n) => {
        rows.push({
          ink: glyph.ink,
          k: glyph.advances,
          w: glyph.spaces,
          actual: lines[index][n].x
        })
      })
    })
    if (mismatch) { if (kern) skipped.push([key, mismatch]); break }
    const fitted = fit(rows)
    if (fitted) results.push({ key, kern, rows, ...fitted, glyphs: rows.length })
    else if (kern) skipped.push([key, 'no consistent type size — the drawn glyphs are not this text'])
  }
}

// A mark whose glyphs land points away is not the same wording drawn differently — it is a file
// whose extraction went wrong. Those are reported, not averaged in.
const REJECT = 1.0
const rejected = results.filter((r) => r.kern && r.worst > REJECT).map((r) => r.key)
const usable = results.filter((r) => !rejected.includes(r.key))

const withKern = usable.filter((r) => r.kern)
const without = usable.filter((r) => !r.kern)

const stat = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = sorted[Math.floor(sorted.length / 2)]
  const mean = sorted.reduce((a, b) => a + b, 0) / sorted.length
  const sd = Math.sqrt(sorted.reduce((a, b) => a + (b - mean) ** 2, 0) / sorted.length)
  return { median: mid, mean, sd, min: sorted[0], max: sorted.at(-1) }
}

console.log(`${font.postscriptName}   ${withKern.length} marks fitted, `
  + `${rejected.length} rejected, ${skipped.length} skipped\n`)

for (const [label, set] of [['with kerning', withKern], ['without kerning', without]]) {
  if (!set.length) continue
  const worst = stat(set.map((r) => r.worst))
  const tracking = stat(set.map((r) => r.tracking))
  const wordSpace = stat(set.map((r) => r.wordSpace))
  const size = stat(set.map((r) => r.size))
  console.log(`${label}`)
  console.log(`   worst glyph offset   median ${worst.median.toFixed(3)} pt   max ${worst.max.toFixed(3)} pt`)
  console.log(`   tracking             ${tracking.median.toFixed(1)}/1000 em   (sd ${tracking.sd.toFixed(1)})`)
  console.log(`   word space delta     ${wordSpace.median.toFixed(1)}/1000 em   (sd ${wordSpace.sd.toFixed(1)})`)
  console.log(`   type size            ${size.median.toFixed(3)} pt   (${size.min.toFixed(2)}..${size.max.toFixed(2)})`)
}

// Stage two: hold tracking and word space at the shared values and refit each mark.
const TRACKING = Math.round(stat(withKern.map((r) => r.tracking)).median * 10) / 10
const WORD_SPACE = 0
const refitted = withKern.map((r) => ({ key: r.key, glyphs: r.glyphs, ...refit(r.rows, TRACKING, WORD_SPACE) }))
  .filter((r) => r.size)

{
  const worst = stat(refitted.map((r) => r.worst))
  const size = stat(refitted.map((r) => r.size))
  console.log(`held at tracking ${TRACKING}/1000 em and the font's own word space`)
  console.log(`   worst glyph offset   median ${worst.median.toFixed(3)} pt   max ${worst.max.toFixed(3)} pt`)
  console.log(`   type size            ${size.median.toFixed(3)} pt   (${size.min.toFixed(2)}..${size.max.toFixed(2)})`)
  const over = refitted.filter((r) => r.worst > 0.05).length
  console.log(`   ${refitted.length - over}/${refitted.length} marks reproduce within 0.05 pt`)
}

const best = withKern.length && stat(withKern.map((r) => r.worst)).median <=
  stat(without.map((r) => r.worst)).median ? withKern : without
console.log(`\nworst marks (${best === withKern ? 'with' : 'without'} kerning):`)
for (const r of [...best].sort((a, b) => b.worst - a.worst).slice(0, 6)) {
  console.log(`   ${r.key.padEnd(9)} ${r.worst.toFixed(3)} pt over ${r.glyphs} glyphs`)
}

// A few marks are set a little larger or smaller than the rest. Worth seeing, because it decides
// whether the type size is one constant or something the layout has to carry per mark.
const median = stat(withKern.map((r) => r.size)).median
const odd = withKern.filter((r) => Math.abs(r.size - median) / median > 0.005)
  .sort((a, b) => a.size - b.size)
if (odd.length) {
  console.log(`\nmarks not set at ${median.toFixed(3)} pt:`)
  for (const r of odd) {
    console.log(`   ${r.key.padEnd(9)} ${r.size.toFixed(3)} pt  `
      + `(${((r.size / median - 1) * 100).toFixed(1).padStart(5)}%)  worst ${r.worst.toFixed(3)} pt`)
  }
}

if (rejected.length) {
  console.log(`\nrejected — the drawn wording is not what the catalogue says it is:`)
  for (const key of rejected) {
    const r = results.find((x) => x.key === key && x.kern)
    console.log(`   ${key.padEnd(9)} glyphs land up to ${r.worst.toFixed(0)} pt from where the text puts them`)
  }
}

// The fit is what a build needs: which text, at what size, from what origin.
writeFileSync(resolve(root, 'scripts/current-fit.json'), JSON.stringify(
  {
    tracking: TRACKING,
    wordSpace: WORD_SPACE,
    leading: LEADING,
    marks: Object.fromEntries(refitted.map((r) => [r.key, {
      lines: names[r.key].lines,
      size: Number(r.size.toFixed(4)),
      origin: Number(r.origin.toFixed(4)),
      worst: Number(r.worst.toFixed(4))
    }]))
  }, null, 2) + '\n')
console.log(`\n→ scripts/current-fit.json  (${refitted.length} marks)`)

if (skipped.length) {
  console.log(`\nskipped:`)
  for (const [key, why] of skipped) console.log(`   ${key.padEnd(9)} ${why}`)
}
