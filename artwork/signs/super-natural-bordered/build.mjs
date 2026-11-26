import { readFileSync, writeFileSync } from 'node:fs'
import opentype from 'opentype.js'

const bytes = readFileSync(new URL('./texgyretermes-bold.otf', import.meta.url))
const font = opentype.parse(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength))
const boardWidth = 814
const fontSize = 99
const ink = '#234b85'
const rows = [
  { id: 'slogan', text: 'Super, Natural', baseline: 127 },
  { id: 'province', text: 'British Columbia', baseline: 266 },
  { id: 'greeting', text: 'welcomes you', baseline: 377 }
]

function lettering({ id, text, baseline }) {
  const options = { kerning: true }
  const left = (boardWidth - font.getAdvanceWidth(text, fontSize, options)) / 2
  const letters = font.getPaths(text, left, baseline, fontSize, options).filter(path => path.commands.length)
  const paths = letters.map(path => `    <path d="${path.toPathData({ flipY: false, decimalPlaces: 3 })}"/>`)
  return [`  <g id="bordered-${id}" aria-label="${text}" fill="${ink}">`, ...paths, '  </g>'].join('\n')
}

const drawing = [
  '<svg xmlns="http://www.w3.org/2000/svg" width="814" height="440" viewBox="0 0 814 440" role="img" aria-labelledby="bordered-title bordered-description">',
  '  <title id="bordered-title">Super, Natural British Columbia welcomes you · blue-bordered sign</title>',
  '  <desc id="bordered-description">Photographic reconstruction with three centred lines typeset in TeX Gyre Termes Bold at its natural width and approximate colours. Three lines of blue lettering sit inside a rounded border.</desc>',
  '  <rect id="bordered-board" width="814" height="440" rx="32" fill="#eef3f5"/>',
  '  <rect id="bordered-rule" x="6" y="6" width="802" height="428" rx="27" fill="none" stroke="' + ink + '" stroke-width="7"/>',
  ...rows.map(lettering),
  '</svg>', ''
].join('\n')
writeFileSync(new URL('../../../src/signs/tourism/super-natural-bordered.svg', import.meta.url), drawing)
