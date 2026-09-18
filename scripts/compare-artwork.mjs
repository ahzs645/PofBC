// Renders each reconstructed lockup alongside the artwork it was derived from.
//
// Every constant in src/logo/layouts.js was measured off the files in artwork/. This script closes
// that loop: it re-renders the same content through the generator and overlays it on the original,
// aligned by the mark, so any drift in type size, leading, tracking or spacing shows up as a
// visible ghost rather than as a number nobody checks.
//
// Rasterising needs cairosvg (`python3 -m pip install cairosvg`). Output lands in tmp/compare/.
//
// Run: npm run compare

import { execFileSync } from 'node:child_process'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { renderLockupSvg, resolveLockup } from '../src/logo/renderLogoSvg.js'
import { pathBounds } from './svgPath.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const outputDir = resolve(root, 'tmp/compare')
mkdirSync(outputDir, { recursive: true })

// The content of each source file, so the generator is asked to draw exactly what the artwork
// already shows. The centred lockup is drawn without the province wordmark in the original.
const CASES = [
  {
    layout: 'stacked',
    file: 'lockup-stacked.svg',
    options: { wordmark: true, ministry: 'Ministry of Forests' }
  },
  {
    layout: 'centred',
    file: 'lockup-centred.svg',
    options: { wordmark: false, ministry: 'Ministry of Forests', program: 'Research Program' }
  },
  {
    layout: 'horizontal',
    file: 'lockup-horizontal.svg',
    options: { wordmark: true, ministry: 'Ministry of Forests' }
  }
]

const RENDER_WIDTH = 1400

// The source lockups are hand-positioned, so the reconstruction and the original do not sit at
// identical offsets. Both crops get a margin, or whichever one overhangs gets silently clipped at
// the frame edge and the diff reports a width difference that is really a cropping artefact.
const MARGIN = 60

/** The mark's bounding box within a source file — everything but the background and the text. */
const markBoundsOf = (svg) => {
  const body = svg.replace(/<text[\s\S]*?<\/text>/g, '')
  let box = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity }

  const grow = (other) => {
    box = {
      minX: Math.min(box.minX, other.minX), maxX: Math.max(box.maxX, other.maxX),
      minY: Math.min(box.minY, other.minY), maxY: Math.max(box.maxY, other.maxY)
    }
  }

  for (const [, data] of body.matchAll(/\sd="([^"]+)"/g)) grow(pathBounds(data))

  for (const [, raw] of body.matchAll(/<polygon[^>]*points="([^"]+)"/g)) {
    const numbers = raw.trim().split(/[\s,]+/).map(Number)
    for (let i = 0; i < numbers.length; i += 2) {
      grow({ minX: numbers[i], maxX: numbers[i], minY: numbers[i + 1], maxY: numbers[i + 1] })
    }
  }

  for (const [, cx, cy, rx, ry] of body.matchAll(/<ellipse[^>]*cx="([\d.]+)"[^>]*cy="([\d.]+)"[^>]*rx="([\d.]+)"[^>]*ry="([\d.]+)"/g)) {
    grow({ minX: +cx - +rx, maxX: +cx + +rx, minY: +cy - +ry, maxY: +cy + +ry })
  }

  return box
}

const results = []

for (const testCase of CASES) {
  const source = readFileSync(resolve(root, 'artwork', testCase.file), 'utf8')
  // The margin is applied as the lockup's own padding, so the generated background fills the whole
  // frame exactly as the source artwork's full-bleed rectangle does.
  const options = {
    ...testCase.options,
    layout: testCase.layout,
    color: 'white',
    background: 'green',
    padding: MARGIN
  }

  const resolved = resolveLockup(options)
  // Rendered against the system Helvetica rather than the app's embedded, renamed copy: cairosvg
  // resolves families through fontconfig and has no use for an @font-face the browser would read.
  const mine = renderLockupSvg({ ...options, resolved, fontFamily: 'Helvetica' })

  // Align the two drawings by the one element they are guaranteed to share. The mark is the same
  // size in both, so matching its position and rendering at one scale puts every other difference
  // — a baseline a hair low, a word gap a hair wide — directly on top of itself.
  const sourceMark = markBoundsOf(source)
  const offsetX = resolved.mark.x - resolved.viewBox.x
  const offsetY = resolved.mark.y - resolved.viewBox.y

  const cropped = source.replace(
    /viewBox="[^"]*"/,
    `viewBox="${sourceMark.minX - offsetX} ${sourceMark.minY - offsetY} ${resolved.viewBox.width} ${resolved.viewBox.height}"`
  )

  writeFileSync(resolve(outputDir, `${testCase.layout}-generated.svg`), mine)
  writeFileSync(resolve(outputDir, `${testCase.layout}-original.svg`), cropped)

  results.push({ layout: testCase.layout, width: resolved.viewBox.width, height: resolved.viewBox.height })
  console.log(`  ${testCase.layout.padEnd(11)} ${resolved.viewBox.width.toFixed(1)} × ${resolved.viewBox.height.toFixed(1)}`)
}

writeFileSync(resolve(outputDir, 'cases.json'), JSON.stringify(results, null, 2))

// Rasterise and diff in Python — cairosvg and Pillow are the shortest path to a pixel comparison,
// and this is a development check rather than part of the app's build.
try {
  execFileSync('python3', [resolve(root, 'scripts/compare_render.py'), outputDir, String(RENDER_WIDTH)], {
    stdio: 'inherit'
  })
} catch {
  console.log('\n  Skipped rasterising. For the visual diff: python3 -m pip install cairosvg pillow')
}
