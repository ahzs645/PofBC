// Measures what the app now draws against what the Province published.
//
// verify-current-names.mjs answers a narrower question — does Adobe Garamond put the letters where
// the artwork has them. This answers the one that matters: does the whole composed lockup, built
// from the catalogue wording, the deduplicated alphabet and the measured layout, land on top of
// the published file it replaces.
//
// It needs the published marks, so it only runs while they are still in the tree.
//
// Run: npm run compare:current

import { existsSync, readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { pathBounds } from './svgPath.mjs'
import { NAME_LEADING } from '../src/assets/currentMark.js'
import { layoutLockup, lettersOf } from '../src/current/currentLayout.js'
import { MINISTRIES } from '../src/current/ministries.js'
import { EXTENTS, KERNING, TRACKING, WIDTHS } from '../src/current/nameMetrics.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const MARKS = resolve(root, 'public/current-marks')

if (!existsSync(MARKS)) {
  console.error('\nThe published marks are no longer in the tree; there is nothing to compare against.\n')
  process.exit(1)
}

/** The published name glyphs, grouped into lines and ordered left to right. */
function publishedLines (key) {
  const source = readFileSync(resolve(MARKS, `${key}.svg`), 'utf8')
  const group = /<g transform="translate\(([-\d.]+) ([-\d.]+)\)">((?:(?!<\/g>).)*?data-role="name".*?)<\/g>/s
    .exec(source)
  if (!group) return null

  const tx = Number(group[1])
  const ty = Number(group[2])
  const glyphs = [...group[3].matchAll(/\sd="([^"]+)"/g)].map((match) => {
    const box = pathBounds(match[1])
    return { x: box.minX + tx, foot: box.maxY + ty }
  })

  const feet = glyphs.map((g) => g.foot).sort((a, b) => a - b)
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
  for (const glyph of glyphs) {
    const line = Math.round((glyph.foot - top) / NAME_LEADING)
    if (!rows.has(line)) rows.set(line, [])
    rows.get(line).push(glyph)
  }
  return [...rows.entries()].sort((a, b) => a[0] - b[0]).map(([, row]) => row.sort((a, b) => a.x - b.x))
}

/** Where the app puts each glyph's ink, line by line. */
function drawnLines (text, language) {
  const layout = layoutLockup({ text, language })
  const em = layout.size / 1000

  return layout.lines.map((line) => {
    const letters = lettersOf(line.text)
    const out = []
    let pen = 0

    letters.forEach((letter, index) => {
      const extent = EXTENTS[letter]
      if (extent) out.push({ x: line.x + (pen + extent[0]) * em, foot: line.baseline + extent[3] * em })
      pen += WIDTHS[letter] ?? 500
      const next = letters[index + 1]
      if (next !== undefined) pen += TRACKING + (KERNING[letter + next] ?? 0)
    })
    return out
  })
}

const compared = []
const skipped = []

for (const ministry of MINISTRIES) {
  for (const language of ['en', 'fr']) {
    const key = `${ministry.code.toLowerCase()}-${language}`
    const published = publishedLines(key)
    if (!published) { skipped.push([key, 'no published artwork']); continue }

    const drawn = drawnLines(ministry[language], language)
    if (drawn.length !== published.length) {
      skipped.push([key, `${drawn.length} lines drawn against ${published.length} published`])
      continue
    }

    let worst = 0
    let counted = 0
    let mismatch = null
    drawn.forEach((line, index) => {
      if (line.length !== published[index].length) {
        mismatch = `line ${index + 1}: ${line.length} letters against ${published[index].length}`
        return
      }
      line.forEach((glyph, n) => {
        worst = Math.max(worst, Math.abs(glyph.x - published[index][n].x))
        counted += 1
      })
    })
    if (mismatch) { skipped.push([key, mismatch]); continue }
    compared.push({ key, worst, glyphs: counted })
  }
}

compared.sort((a, b) => b.worst - a.worst)
const values = compared.map((c) => c.worst).sort((a, b) => a - b)
const median = values[Math.floor(values.length / 2)]
const close = compared.filter((c) => c.worst <= 0.1).length

console.log(`${compared.length} lockups compared against the published artwork, ` +
  `${compared.reduce((n, c) => n + c.glyphs, 0)} glyphs\n`)
console.log(`   median worst offset  ${median.toFixed(3)} pt`)
console.log(`   within 0.1 pt        ${close}/${compared.length} lockups`)
console.log(`\n   furthest off:`)
for (const c of compared.slice(0, 5)) {
  console.log(`      ${c.key.padEnd(9)} ${c.worst.toFixed(3)} pt over ${c.glyphs} glyphs`)
}

if (skipped.length) {
  console.log(`\n   not comparable:`)
  for (const [key, why] of skipped) console.log(`      ${key.padEnd(9)} ${why}`)
}
