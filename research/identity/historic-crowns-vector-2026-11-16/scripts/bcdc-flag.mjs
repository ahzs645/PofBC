// The Province's BC Flag Symbol, horizontal, one ink — as BCDC printed it in 1984/85.
// Rendered with the repo's own flag renderer (src/flag/renderFlagSvg.js), type outlined.
import { renderFlagSvg } from '/home/user/PofBC/src/flag/renderFlagSvg.js'
import outlines from '/home/user/PofBC/src/fonts/generated/outlines.js'
import { writeFileSync } from 'node:fs'
const [out, palette = 'ink', ink = '#000000'] = process.argv.slice(2)
const { svg, box } = renderFlagSvg({ ministry: '', symbol: 'horizontal', letterColor: ink, flagPalette: palette, glyphs: outlines, title: 'British Columbia Development Corporation — BC flag symbol' })
writeFileSync(out, svg + '\n'); console.log(box, svg.length, /<text|<image/.test(svg))
