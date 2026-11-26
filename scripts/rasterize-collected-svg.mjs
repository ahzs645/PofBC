// Rasterizes SVG files for build_collected_display.py, in Chromium (through Playwright) so that
// they are drawn exactly as the gallery's browser draws them; resvg drops some of these files'
// clip paths. Reads a JSON list of jobs on stdin — { src, out, height, maxWidth, aspect, antialias } — and
// writes each as a transparent PNG. With antialias off every pixel takes one of the drawing's own
// colours, which is how the display build works out which colour each part of a mark is drawn in.
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
let playwright
try {
  playwright = require('playwright')
} catch {
  playwright = require(require.resolve('playwright', { paths: [process.env.NODE_PATH ?? '', '/usr/lib/node_modules', '/usr/local/lib/node_modules'] }))
}

const jobs = JSON.parse(readFileSync(0, 'utf8'))
// Reuse an installed Chromium when the build environment has no Playwright browser bundle.
const browser = await playwright.chromium.launch(process.env.CHROMIUM_EXECUTABLE_PATH
  ? { executablePath: process.env.CHROMIUM_EXECUTABLE_PATH } : {})
const page = await browser.newPage()
const results = []
for (const job of jobs) {
  let svg = readFileSync(job.src, 'utf8')
  if (job.antialias === false) {
    svg = svg.replace(/<((?:\w+:)?svg)\b[^>]*>/, (tag) =>
      `${tag}<style xmlns="http://www.w3.org/2000/svg">*{shape-rendering:crispEdges!important;text-rendering:optimizeSpeed!important}</style>`)
  }
  const url = `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`
  // The drawing's proportions are its viewBox's, which the build passes in. The image is given its
  // size before it loads: resizing it afterwards raced the screenshot, which then sometimes caught
  // it still at its own size, overflowing the clip, and the build trimmed to that.
  const height = Math.round(Math.min(job.height, job.maxWidth / job.aspect))
  const width = Math.round(height * job.aspect)
  await page.setViewportSize({ width, height })
  await page.setContent(`<body style="margin:0;background:transparent"><img id="i" src="${url}" ` +
    `style="display:block;width:${width}px;height:${height}px"></body>`)
  await page.waitForFunction(() => document.getElementById('i').complete)
  await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))))
  await page.screenshot({ path: job.out, omitBackground: true, clip: { x: 0, y: 0, width, height } })
  results.push({ out: job.out, width, height })
}
await browser.close()
process.stdout.write(JSON.stringify(results))
