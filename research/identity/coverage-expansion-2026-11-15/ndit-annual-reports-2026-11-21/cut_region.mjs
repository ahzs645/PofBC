// Cut one logo out of a whole-page SVG written by pdftocairo -svg.
// Keeps only the drawn elements that lie wholly inside a region of the page (in PDF points),
// with their own geometry, fills, gradients and clip paths unchanged; drops embedded images
// unless --keep-image is given; prunes defs nothing uses; fits the viewBox to what is kept.
// Usage: node cut_region.mjs page.svg x0,y0,x1,y1 out.svg "title" "desc" [--keep-image]
import { chromium } from 'playwright-core'
import { readFileSync, writeFileSync } from 'node:fs'

const [src, region, out, title, desc] = process.argv.slice(2)
const keepImage = process.argv.includes('--keep-image')
const [x0, y0, x1, y1] = region.split(',').map(Number)
const svg = readFileSync(src, 'utf8')
const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' })
const page = await browser.newPage({ viewport: { width: 1400, height: 1800 } })
await page.setContent(`<!doctype html><body style="margin:0">${svg}</body>`)
const result = await page.evaluate(({ x0, y0, x1, y1, keepImage, title, desc }) => {
  const root = document.querySelector('svg')
  // Page user units: pdftocairo writes width/height in pt and a matching viewBox.
  root.setAttribute('width', root.viewBox.baseVal.width)
  root.setAttribute('height', root.viewBox.baseVal.height)
  const toUser = root.getScreenCTM().inverse()
  const boxOf = (el) => {
    const r = el.getBoundingClientRect()
    const a = new DOMPoint(r.left, r.top).matrixTransform(toUser)
    const b = new DOMPoint(r.right, r.bottom).matrixTransform(toUser)
    return { x0: Math.min(a.x, b.x), y0: Math.min(a.y, b.y), x1: Math.max(a.x, b.x), y1: Math.max(a.y, b.y) }
  }
  const tol = 0.5
  const inside = (b) => b.x0 >= x0 - tol && b.y0 >= y0 - tol && b.x1 <= x1 + tol && b.y1 <= y1 + tol && b.x1 > b.x0 && b.y1 > b.y0
  const drawn = [...root.querySelectorAll('path, rect, use, image, polygon, polyline, line, circle, ellipse')]
    .filter((el) => !el.closest('defs, clipPath, mask, pattern, symbol'))
  const kept = new Set()
  let union = null
  let images = 0
  // What shows of an element clipped by an ancestor's clip-path: the clip shape's own geometry,
  // in the user space of the element that refers to it (clipPathUnits userSpaceOnUse).
  const clipBox = (el) => {
    for (let n = el; n && n !== root; n = n.parentElement) {
      const ref = n.getAttribute && n.getAttribute('clip-path')
      if (!ref) continue
      const clip = document.querySelector(ref.replace(/^url\(["']?|["']?\)$/g, ''))
      if (!clip) continue
      const m = n.getScreenCTM()
      let box = null
      for (const child of clip.children) {
        if (typeof child.getBBox !== 'function') continue
        const bb = child.getBBox()
        const own = child.transform?.baseVal?.consolidate()?.matrix ?? new DOMMatrix()
        for (const [x, y] of [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]]) {
          const p = new DOMPoint(x, y).matrixTransform(own).matrixTransform(m).matrixTransform(toUser)
          box = box ? { x0: Math.min(box.x0, p.x), y0: Math.min(box.y0, p.y), x1: Math.max(box.x1, p.x), y1: Math.max(box.y1, p.y) } : { x0: p.x, y0: p.y, x1: p.x, y1: p.y }
        }
      }
      if (box) return box
    }
    return null
  }
  for (const el of drawn) {
    let b = boxOf(el)
    if (!inside(b)) { const c = clipBox(el); if (c && inside(c)) b = c }
    const isImage = el.tagName.toLowerCase() === 'image'
    if (!inside(b) || (isImage && !keepImage)) { el.remove(); continue }
    if (isImage) images++
    kept.add(el)
    const shown = b
    union = union ? { x0: Math.min(union.x0, shown.x0), y0: Math.min(union.y0, shown.y0), x1: Math.max(union.x1, shown.x1), y1: Math.max(union.y1, shown.y1) } : shown
  }
  // Empty groups go; then defs nothing refers to (repeatedly, as defs refer to defs).
  let removed = true
  while (removed) {
    removed = false
    for (const g of root.querySelectorAll('g')) if (!g.closest('defs') && !g.querySelector('path, rect, use, image, polygon, polyline, line, circle, ellipse')) { g.remove(); removed = true }
  }
  // Defs nothing refers to go, repeatedly, since defs refer to defs (a clip path to a glyph).
  removed = true
  while (removed) {
    removed = false
    const html = root.outerHTML
    for (const def of root.querySelectorAll('defs > [id], defs > g > [id]')) {
      const refs = html.split(`#${def.id}"`).length - 1 + html.split(`#${def.id})`).length - 1
      if (!refs) { def.remove(); removed = true }
    }
    for (const g of root.querySelectorAll('defs > g')) if (!g.children.length) { g.remove(); removed = true }
  }
  const pad = 0.5
  const vb = [union.x0 - pad, union.y0 - pad, union.x1 - union.x0 + 2 * pad, union.y1 - union.y0 + 2 * pad].map((v) => +v.toFixed(3))
  root.setAttribute('viewBox', vb.join(' '))
  root.setAttribute('width', vb[2])
  root.setAttribute('height', vb[3])
  root.removeAttribute('version')
  const t = document.createElementNS('http://www.w3.org/2000/svg', 'title'); t.textContent = title
  const d = document.createElementNS('http://www.w3.org/2000/svg', 'desc'); d.textContent = desc
  root.prepend(d); root.prepend(t)
  return { svg: new XMLSerializer().serializeToString(root), kept: kept.size, images, viewBox: vb }
}, { x0, y0, x1, y1, keepImage, title, desc })
writeFileSync(out, `<?xml version="1.0" encoding="UTF-8"?>\n${result.svg}\n`)
console.log(JSON.stringify({ kept: result.kept, images: result.images, viewBox: result.viewBox, bytes: result.svg.length }))
await browser.close()
