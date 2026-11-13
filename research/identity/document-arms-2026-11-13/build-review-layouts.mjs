// Evidence sheet only. This SVG deliberately embeds the three unchanged reference PNGs.
// The exported logo artwork produced by renderDocumentArmsSvg never includes those images.
import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { openSync } from 'fontkit'
import { Resvg } from '@resvg/resvg-js'
import { renderDocumentArmsSvg } from '../../../src/documentArms/renderDocumentArmsSvg.js'
import { DOCUMENT_ARMS_PATH } from '../../../src/documentArms/geometry.generated.js'

const directory = new URL('./', import.meta.url)
const root = new URL('../../../', import.meta.url)
const fonts = Object.fromEntries([400, 700].map((weight) => [weight,
  openSync(fileURLToPath(new URL(`node_modules/@fontsource/noto-sans/files/noto-sans-latin-${weight}-normal.woff`, root)))
]))
const round = (n) => Math.round(n * 1000) / 1000
const escape = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

// Outlined labels keep the comparison sheet portable, as well as the study headings.
const label = (text, x, baseline, size = 16, weight = 400, fill = '#30383e') => {
  const font = fonts[weight]
  const run = font.layout(text)
  const scale = size / font.unitsPerEm
  let penX = 0
  let penY = 0
  const paths = run.glyphs.map((glyph, i) => {
    const position = run.positions[i]
    const path = glyph.path.mapPoints((px, py) => [
      round(x + (px + penX + position.xOffset) * scale),
      round(baseline - (py + penY + position.yOffset) * scale)
    ]).toSVG()
    penX += position.xAdvance
    penY += position.yAdvance
    return path
  }).join('')
  return `<g aria-label="${escape(text)}" fill="${fill}"><title>${escape(text)}</title><path d="${paths}"/></g>`
}

const rows = [
  { layout: 'split-serif', reference: 'split-serif.png', label: '1  Split serif heading', y: 240, height: 238,
    note: 'Noto Serif Bold stand-in; fixed BRITISH / COLUMBIA wording.' },
  { layout: 'government', reference: 'government-caption.png', label: '2  Government heading · supplied order dated 4 May 1978', y: 556, height: 350,
    note: 'Barlow Condensed Bold stand-in; two-line government caption.' },
  { layout: 'split-blackletter', reference: 'blackletter-grant.png', label: '3  Crown grant heading · document date unestablished', y: 984, height: 220,
    note: 'UnifrakturMaguntia stand-in; original blackletter face unidentified.' }
]

const parts = [
  '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1332" viewBox="0 0 1200 1332">',
  '<title>Historical document arms: unchanged references and provisional vector layout studies</title>',
  '<desc>This is an evidence comparison sheet containing three embedded original screenshots. It is not the path-only logo export. The study uses a generated-master arms conversion and modern font stand-ins; the reference engravings and historical typefaces have not been recreated or verified.</desc>',
  `<defs><path id="shared-study-arms" d="${DOCUMENT_ARMS_PATH}" fill-rule="evenodd"/></defs>`,
  '<rect width="1200" height="1332" fill="#f5f4ef"/>',
  label('Historical document headings', 32, 52, 30, 700, '#162a49'),
  label('Supplied references and the new layout studies', 32, 86, 18),
  '<rect x="32" y="107" width="1136" height="68" rx="5" fill="#e8e7df"/>',
  label('Arms drawing and historical typefaces are unverified.', 48, 134, 17, 700),
  label('The study reuses the existing PlateForge arms. Its engraving differs from the references.', 48, 159, 16),
  label('COMPLETE SUPPLIED SCREENSHOT', 32, 210, 14, 700),
  label('PROVISIONAL VECTOR STUDY', 620, 210, 14, 700)
]

for (const row of rows) {
  const image = await readFile(new URL(`reference/${row.reference}`, directory))
  const { svg, box } = renderDocumentArmsSvg({ layout: row.layout, markColor: '#000000', textColor: '#000000', background: '#ffffff', clearSpaceFactor: 0.03 })
  // Only the evidence sheet reuses the same arms definition to avoid storing it three times.
  const inner = svg.slice(svg.indexOf('>') + 1, svg.lastIndexOf('</svg>'))
    .replace(`<path d="${DOCUMENT_ARMS_PATH}" fill-rule="evenodd"/>`, '<use href="#shared-study-arms"/>')
  const top = row.y + 16
  parts.push(label(row.label, 32, row.y, 18, 700, '#162a49'))
  for (const x of [32, 620]) parts.push(`<rect x="${x}" y="${top}" width="548" height="${row.height}" rx="4" fill="#ffffff" stroke="#d3d4d0"/>`)
  parts.push(`<image x="44" y="${top + 12}" width="524" height="${row.height - 24}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,${image.toString('base64')}"/>`)
  parts.push(`<svg x="632" y="${top + 12}" width="524" height="${row.height - 24}" viewBox="${box.x} ${box.y} ${box.width} ${box.height}" preserveAspectRatio="xMidYMid meet">${inner}</svg>`)
  parts.push(label('Full supplied image, without further cropping.', 32, top + row.height + 23, 13))
  parts.push(label(row.note, 620, top + row.height + 23, 12.5))
}
parts.push(
  label('Images are fitted independently for inspection; this is not a scale-matched overlay.', 32, 1281, 14, 700),
  label('Original scans appear only in this evidence sheet. Exported logo SVGs contain paths, not reference images.', 32, 1307, 14),
  '</svg>'
)

const proof = parts.join('\n')
await writeFile(new URL('review-layouts.svg', directory), proof)
await writeFile(new URL('review-layouts.png', directory), new Resvg(proof).render().asPng())
console.log('Wrote review-layouts.svg and review-layouts.png. The three reference images are embedded unchanged.')
