// Build the BCDC 1985 BC-flag symbol: the repo's flag artwork and outlined BC letters
// (src/flag renderer, ink palette), with the flag's scale and position fitted to the 1985 scan.
import { readFileSync, writeFileSync } from 'node:fs'
import { Resvg } from '/home/user/PofBC/node_modules/@resvg/resvg-js/index.js'
const [src, out] = process.argv.slice(2)
const svg0 = readFileSync(src, 'utf8')
const flag = svg0.match(/<g transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)">(<path data-role="flag".*?)<\/g>/)[4]
const letters = svg0.match(/(<g fill="#000000"><g transform.*<\/g><\/g>)<\/svg>/)[1]
const fit = { fx: 186.6, fy: -133, fs: 0.183338 } // from fit-flag.mjs
const body = `<g transform="translate(${fit.fx} ${fit.fy}) scale(${fit.fs})">${flag.replace(/ data-role="flag"/g, '')}</g>${letters}`
// tight box: render big and measure
const probe = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -160 400 200" width="4000" height="2000">${body}</svg>`
const r = new Resvg(probe).render(); const px = r.pixels; let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1
for (let y = 0; y < r.height; y++) for (let x = 0; x < r.width; x++) if (px[(y * r.width + x) * 4 + 3] > 0) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y) }
const vb = [-20 + x0 / 10 - 0.5, -160 + y0 / 10 - 0.5, (x1 - x0 + 1) / 10 + 1, (y1 - y0 + 1) / 10 + 1].map((v) => +v.toFixed(2))
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb.join(' ')}" width="${(vb[2] * 3).toFixed(1)}" height="${(vb[3] * 3).toFixed(1)}"><title>BC flag symbol, as printed by British Columbia Development Corporation (reconstruction)</title>${body}</svg>\n`
writeFileSync(out, svg); console.log(vb, svg.length)
