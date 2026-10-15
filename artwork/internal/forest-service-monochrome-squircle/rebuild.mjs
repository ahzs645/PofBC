// Recalculate the identical standardized squircle outline used by all monochrome studies.
// Usage: node artwork/internal/forest-service-monochrome-squircle/rebuild.mjs [--check]
// Only the badge-outline path is updated; the manually drawn province/tree/islands remain unchanged.
import { readFileSync, writeFileSync } from 'node:fs'
const ROOT = new URL('../../../', import.meta.url)
const CONFIG = new URL('./parameters.json', import.meta.url)
const { geometry: g } = JSON.parse(readFileSync(CONFIG, 'utf8'))
const point = (t) => {
  const x = Math.cos(t), y = Math.sin(t), e = 2 / g.exponent
  return [g.cx + g.rx * Math.sign(x) * Math.abs(x) ** e,
          g.cy + g.ry * Math.sign(y) * Math.abs(y) ** e]
}
const tangent = ([px, py]) => {
  const x = (px - g.cx) / g.rx, y = (py - g.cy) / g.ry
  const dx = Math.abs(y) > 1e-10 ? -Math.sign(y) * Math.abs(y) ** (g.exponent - 1) / g.ry : 0
  const dy = Math.abs(x) > 1e-10 ? Math.sign(x) * Math.abs(x) ** (g.exponent - 1) / g.rx : 0
  const norm = Math.hypot(dx, dy)
  return [dx / norm, dy / norm]
}
const f = n => n.toFixed(4)
const nodes = Array.from({ length: g.cubicSegments + 1 }, (_, i) => point(2 * Math.PI * i / g.cubicSegments))
nodes[nodes.length - 1] = nodes[0]
let outline = 'M ' + f(nodes[0][0]) + ' ' + f(nodes[0][1])
for (let i = 0; i < g.cubicSegments; i++) {
  const a = nodes[i], b = nodes[i + 1], v = tangent(a), w = tangent(b)
  const arm = Math.hypot(b[0] - a[0], b[1] - a[1]) * 0.3345
  const p1 = [a[0] + arm * v[0], a[1] + arm * v[1]]
  const p2 = [b[0] - arm * w[0], b[1] - arm * w[1]]
  outline += ' C ' + f(p1[0]) + ' ' + f(p1[1]) + ' ' + f(p2[0]) + ' ' + f(p2[1]) + ' ' + f(b[0]) + ' ' + f(b[1])
}
outline += ' Z'
const files = [
  'forest-service-emblem-one-ink.svg',
  'forest-service-emblem-joined-islands.svg',
  'forest-service-emblem-reverse.svg',
  'forest-service-emblem-reverse-joined-islands.svg'
]
let failures = 0
for (const file of files) {
  const path = new URL('src/internal/' + file, ROOT)
  const input = readFileSync(path, 'utf8')
  const re = /(<path id="badge-outline" d=")[^"]+(" fill="none" stroke="[^"]+" stroke-width=")[^"]+(")/g
  const replacement = (_, a, b, c) => a + outline + b + g.strokeWidth + c
  const matches = [...input.matchAll(re)]
  if (matches.length !== 1) throw new Error('Expected exactly one named badge-outline: ' + file)
  const output = input.replace(re, replacement)
  if (process.argv.includes('--check')) {
    if (input !== output) { console.error('Out of sync:', file); failures++ }
  } else {
    if (input !== output) writeFileSync(path, output)
    console.log('Rebuilt', file)
  }
}
if (failures) process.exitCode = 1
