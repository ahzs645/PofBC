// Solutions BC / Shared Services, 2006 letterhead: the gallery's BC symbol (sun, rays, core, mountains
// of the Best Place on Earth one-off) fitted to the scan's symbol box, a hairline divider, and the two
// lines set in PT Sans outlines (from lines.json, written by build of fit_lines.py results).
import { readFileSync, writeFileSync } from 'node:fs'
import { ONE_OFF_MARKS } from '/home/user/PofBC/src/assets/oneOffMarks.js'
import { renderOneOffSvg } from '/home/user/PofBC/src/gallery/renderOneOff.js'
import { transformed } from '/home/user/PofBC/scripts/glyphs.mjs'
import { absolute, boundsOf } from '/home/user/PofBC/scripts/svgAbsolute.mjs'
const [linesD, out] = process.argv.slice(2)
const bpe = ONE_OFF_MARKS['best-place-on-earth']
const roles = ['sun', 'rays', 'core', 'mountains']
const parts = bpe.shapes.filter((s) => roles.includes(s.role)).map((s) => ({ role: s.role, sub: absolute(s.d) }))
const union = (subs) => subs.map(boundsOf).reduce((a, b) => ({ left: Math.min(a.left, b.left), top: Math.min(a.top, b.top), right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom) }))
const mb = union(parts.flatMap((p) => p.sub))
// symbol box in the scan (684 x 186): x 26-197, y 34-148; divider x 229.5-232, y 34-147
const k = Math.min((197 - 26) / (mb.right - mb.left), (148 - 34) / (mb.bottom - mb.top))
const dx = 26 - mb.left * k; const dy = 34 - mb.top * k
const rect = (x, y, w, h) => [[['M', x, y], ['L', x + w, y], ['L', x + w, y + h], ['L', x, y + h], ['Z']]]
const text = absolute(readFileSync(linesD, 'utf8').trim())
const shapes = [...parts.map((p) => ({ role: p.role, sub: transformed(p.sub, k, dx, dy) })), { role: 'divider', sub: rect(230, 34, 1.6, 113) }, { role: 'name', sub: text }]
const box = union(shapes.flatMap((s) => s.sub))
const r3 = (v) => Math.round(v * 1000) / 1000
const ser = (subs) => subs.map((p) => p.map(([c, ...v]) => c + v.map((val, i) => r3(i % 2 === 0 ? val - box.left : val - box.top)).join(' ')).join('')).join('')
ONE_OFF_MARKS.__solbc = {
  width: r3(box.right - box.left), height: r3(box.bottom - box.top),
  sun: { cx: r3(bpe.sun.cx * k + dx - box.left), cy: r3(bpe.sun.cy * k + dy - box.top), r: r3(bpe.sun.r * k) },
  gradients: bpe.gradients,
  printed: { background: null, sun: '#a8a8a8', light: '#ffffff', mountains: '#1c1c1c', divider: '#1c1c1c', name: '#1c1c1c' },
  shapes: shapes.map((s) => ({ role: s.role, d: ser(s.sub) }))
}
let { svg } = renderOneOffSvg({ id: '__solbc', idPrefix: 'solbc' })
svg = svg.replace(/ data-role="[a-z]+"/g, '').replace('<svg xmlns="http://www.w3.org/2000/svg" ', `<svg xmlns="http://www.w3.org/2000/svg" width="${r3((box.right - box.left) * 2)}" height="${r3((box.bottom - box.top) * 2)}" `).replace(/(<svg[^>]*>)/, '$1<title>Solutions BC / Shared Services — 2006 letterhead (reconstruction)</title>')
writeFileSync(out, svg + '\n'); console.log(out, k, box, /<image|<text/.test(svg))
