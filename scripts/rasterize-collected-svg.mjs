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
const browser = await playwright.chromium.launch()
const page = await browser.newPage()
const results = []
for (const job of jobs) {
  let svg = readFileSync(job.src, 'utf8')
  if (job.antialias === false) {
    svg = svg.replace(/<((?:\w+:)?svg)\b[^>]*>/, (tag) =>
      `${tag}<style xmlns="http://www.w3.org/2000/svg">*{shape-rendering:crispEdges!important;text-rendering:optimizeSpeed!important}</style>`)
  }
  const url = `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`
  await page.setContent(`<body style="margin:0;background:transparent"><img id="i" src="${url}"></body>`)
  await page.waitForFunction(() => document.getElementById('i').complete)
  // The drawing's proportions are its viewBox's, which the build passes in.
  const height = Math.round(Math.min(job.height, job.maxWidth / job.aspect))
  const width = Math.round(height * job.aspect)
  await page.setViewportSize({ width, height })
  await page.evaluate(([width, height]) => {
    const image = document.getElementById('i')
    Object.assign(image.style, { display: 'block', width: `${width}px`, height: `${height}px` })
  }, [width, height])
  await page.screenshot({ path: job.out, omitBackground: true, clip: { x: 0, y: 0, width, height } })
  results.push({ out: job.out, width, height })
}
await browser.close()
process.stdout.write(JSON.stringify(results))
