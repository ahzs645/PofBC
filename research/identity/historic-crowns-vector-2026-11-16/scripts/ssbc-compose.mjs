// Shared Services BC lockups, put together from the gallery's Best Place on Earth mark and letters of
// the Province's Garamond lifted from the gallery's one-off marks (src/assets/oneOffMarks.js), each
// letter scaled by its source's x-height and placed where the published PNG prints it.
//   node ssbc-compose.mjs 2015 OUT.svg   |   node ssbc-compose.mjs 2006 OUT.svg
import { writeFileSync } from 'node:fs'
import { ONE_OFF_MARKS } from '/home/user/PofBC/src/assets/oneOffMarks.js'
import { renderOneOffSvg } from '/home/user/PofBC/src/gallery/renderOneOff.js'
import { lettersOf, transformed } from '/home/user/PofBC/scripts/glyphs.mjs'
import { absolute, boundsOf } from '/home/user/PofBC/scripts/svgAbsolute.mjs'
const [variant, out] = process.argv.slice(2)
const shapeOf = (id, role) => ONE_OFF_MARKS[id].shapes.find((s) => s.role === role)
const L = (id, role) => lettersOf(shapeOf(id, role).d)
const wild = L('bc-wildfire-service-one-line', 'name')   // W i . l d fi r e S e r v i . c e
const stats = L('bc-stats', 'name')                     // S t a t s
const tag = L('best-place-on-earth', 'tagline')         // Th e B e s t P l a c e o n E a r t h
const welcome = L('welcome-bc', 'accent')               // B C
const h = (l) => l.box.bottom - l.box.top
// Each source: its x-height and baseline (foot of a flat-footed letter).
const SRC = {
  wild: { x: h(wild[9]), base: wild[10].box.bottom },
  stats: { x: h(stats[2]), base: stats[1].box.bottom },
  tag: { x: h(tag[1]), base: tag[17].box.bottom },
  welcome: { x: 8.21, base: welcome[0].box.bottom } // WelcomeBC's own e (name[1]) is 8.21 tall
}
// The 2015 brochure PNG (810 x 267): each letter's left edge, and the two baselines, in its pixels.
// x-height there (e, line 2): 46 px. Line 1 baseline 143, line 2 baseline 234.
const X = 46
const name = [
  ['wild', wild[8], 339, 143], ['tag', tag[17], 386, 143], ['stats', stats[2], 442, 143], ['wild', wild[10], 484, 143], ['wild', wild[9], 517, 143], ['wild', wild[4], 558, 143],
  ['wild', wild[8], 339, 234], ['wild', wild[9], 386, 234], ['wild', wild[10], 427, 234], ['wild', wild[11], 460, 234], ['wild', wild[12], 508, 234, wild[13]], ['wild', wild[14], 533, 234], ['wild', wild[15], 574, 234], ['stats', stats[4], 615, 234]
]
const accent = [['welcome', welcome[0], 650, 234], ['welcome', welcome[1], 710, 234]]
const place = (list) => list.flatMap(([src, letter, left, base, extra]) => {
  const s = X / SRC[src].x
  const dx = left - letter.box.left * s; const dy = base - SRC[src].base * s
  return [...transformed(letter.subpaths, s, dx, dy), ...(extra ? transformed(extra.subpaths, s, dx, dy) : [])]
})
const nameSub = place(name); const accentSub = place(accent)
// The mark, from the gallery's Best Place on Earth one-off.
const bpe = ONE_OFF_MARKS['best-place-on-earth']
const roles = variant === '2015' ? ['sun', 'rays', 'core', 'mountains', 'wordmark'] : ['sun', 'rays', 'core', 'mountains', 'wordmark', 'rule', 'tagline']
const parts = bpe.shapes.filter((s) => roles.includes(s.role)).map((s) => ({ role: s.role, sub: absolute(s.d) }))
const union = (subs) => subs.map(boundsOf).reduce((a, b) => ({ left: Math.min(a.left, b.left), top: Math.min(a.top, b.top), right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom) }))
const mb = union(parts.flatMap((p) => p.sub))
let shapes, sunAt, unit
const rect = (x, y, w, hh) => [[['M', x, y], ['L', x + w, y], ['L', x + w, y + hh], ['L', x, y + hh], ['Z']]]
if (variant === '2015') {
  // Mark box in the PNG: x 31-270, y 31-236 (sun top to COLUMBIA foot). Divider x 302-305, y 30-235.
  const k = (236 - 31) / (mb.bottom - mb.top)
  const dx = 31 - mb.left * k; const dy = 31 - mb.top * k
  shapes = [...parts.map((p) => ({ role: p.role, sub: transformed(p.sub, k, dx, dy) })),
    { role: 'divider', sub: rect(302, 30, 3, 205) }, { role: 'name', sub: nameSub }, { role: 'accent', sub: accentSub }]
  sunAt = { cx: bpe.sun.cx * k + dx, cy: bpe.sun.cy * k + dy, r: bpe.sun.r * k }
} else {
  // 2006/07 report PNG (386 x 109, cut off at its foot): mark x 2-129 from y 2; divider x 142-145;
  // "Shared" S at x 162, its cap top 22 and baseline 62. The name block is the 2015 setting, scaled.
  const k = (129 - 2) / (mb.right - mb.left)
  const dx = 2 - mb.left * k; const dy = 2 - mb.top * k
  const markBottom = mb.bottom * k + dy
  const s = (62 - 22) / (143 - 70)  // cap height of the S here against there
  const nx = (x) => 162 + (x - 339) * s
  const mv = (sub) => sub.map((path) => path.map(([c, ...v]) => [c, ...v.map((val, i) => i % 2 === 0 ? nx(val) : 62 + (val - 143) * s)]))
  shapes = [...parts.map((p) => ({ role: p.role, sub: transformed(p.sub, k, dx, dy) })),
    { role: 'divider', sub: rect(142.5, 2, 2, markBottom - 2) }, { role: 'name', sub: mv(nameSub) }, { role: 'accent', sub: mv(accentSub) }]
  sunAt = { cx: bpe.sun.cx * k + dx, cy: bpe.sun.cy * k + dy, r: bpe.sun.r * k }
}
const box = union(shapes.flatMap((s) => s.sub))
const r3 = (v) => Math.round(v * 1000) / 1000
const ser = (subs) => subs.map((p) => p.map(([c, ...v]) => c + v.map((val, i) => r3(i % 2 === 0 ? val - box.left : val - box.top)).join(' ')).join('')).join('')
ONE_OFF_MARKS.__ssbc = {
  width: r3(box.right - box.left), height: r3(box.bottom - box.top),
  sun: { cx: r3(sunAt.cx - box.left), cy: r3(sunAt.cy - box.top), r: r3(sunAt.r) },
  gradients: bpe.gradients,
  printed: variant === '2015'
    ? { background: null, sun: '#fdb812', light: '#ffffff', mountains: '#496da6', wordmark: '#ffffff', divider: '#fdb812', name: '#ffffff', accent: '#fdb812' }
    : { background: null, sun: '#fdb812', light: '#ffffff', mountains: '#092871', wordmark: '#092871', rule: '#feb100', tagline: '#092871', divider: '#feb100', name: '#092871', accent: '#feb100' },
  shapes: shapes.map((s) => ({ role: s.role, d: ser(s.sub) }))
}
let { svg } = renderOneOffSvg({ id: '__ssbc', idPrefix: 'ssbc' + variant })
const title = variant === '2015' ? 'Shared Services BC — reversed, without tagline (reconstruction)' : 'Shared Services BC — with The Best Place on Earth (reconstruction)'
svg = svg.replace(/ data-role="[a-z]+"/g, '').replace('<svg xmlns="http://www.w3.org/2000/svg" ', `<svg xmlns="http://www.w3.org/2000/svg" width="${r3((box.right - box.left) * 2)}" height="${r3((box.bottom - box.top) * 2)}" `).replace(/(<svg[^>]*>)/, `$1<title>${title}</title>`)
writeFileSync(out, svg + '\n')
console.log(out, box, svg.length, /<image|<text/.test(svg))
// also emit the PNG-space offset for overlays
writeFileSync(out + '.offset.json', JSON.stringify({ left: box.left, top: box.top }))
