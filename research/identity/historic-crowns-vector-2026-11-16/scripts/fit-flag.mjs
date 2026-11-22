// Fit the flag's placement (scale, x, y) and the BC letters' placement to the 1985 scan by overlap.
import { Resvg } from '/home/user/PofBC/node_modules/@resvg/resvg-js/index.js'
import { readFileSync } from 'node:fs'
const svg0 = readFileSync(process.argv[2], 'utf8')
const mask = readFileSync(process.argv[3]); const W = 288, H = 124
const flagG = svg0.match(/<g transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)">(<path data-role="flag".*?)<\/g>/)
const letters = svg0.match(/(<g fill="#000000"><g transform.*<\/g><\/g>)<\/svg>/)[1]
// scan mapping: BC cap height 100 units -> capPx; B left at units ~0 -> bx; baseline y=0 -> by
function score (p) {
  const { capPx, bx, by, fx, fy, fs } = p
  const k = capPx / 100
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><g transform="translate(${bx} ${by}) scale(${k})">` +
    `<g transform="translate(${fx} ${fy}) scale(${fs})">${flagG[4]}</g>${letters}</g></svg>`
  const px = new Resvg(svg, { background: 'white' }).render().pixels
  let inter = 0, uni = 0
  for (let i = 0; i < W * H; i++) { const a = px[i * 4] < 128 ? 1 : 0; const b = mask[i]; inter += a & b; uni += a | b }
  return inter / uni
}
let best = { capPx: 71, bx: 20 + 1.5, by: 94.5, fx: +flagG[1], fy: +flagG[2], fs: +flagG[3] }
let bs = score(best)
const steps = { capPx: 1, bx: 1, by: 1, fx: 4, fy: 4, fs: 0.006 }
for (let round = 0; round < 6; round++) {
  for (const key of Object.keys(steps)) {
    for (const dir of [-1, 1]) {
      for (let n = 1; n < 30; n++) {
        const t = { ...best, [key]: best[key] + dir * steps[key] }
        const s = score(t); if (s > bs) { best = t; bs = s } else break
      }
    }
  }
  for (const key of Object.keys(steps)) steps[key] /= 2
}
console.log(JSON.stringify(best), 'IoU', bs.toFixed(4), 'start', score({ capPx: 71, bx: 21.5, by: 94.5, fx: +flagG[1], fy: +flagG[2], fs: +flagG[3] }).toFixed(4))
