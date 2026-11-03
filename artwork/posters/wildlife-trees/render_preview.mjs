// Renders the site's copy of Wildlife Trees to a PNG in Chromium, the first step in making the
// viewer's loading preview (preview.py is the second). Rendering the site's copy, not the master,
// keeps the preview in register with the drawing that replaces it.
//
//   node render_preview.mjs ../../../src/posters/wildlife-trees/wildlife-trees.svg /tmp/wildlife-trees-2000.png
//
// Needs Playwright with Chromium.

import { mkdtempSync, writeFileSync, copyFileSync, rmSync } from 'node:fs'
import { createRequire } from 'node:module'
import { join, resolve } from 'node:path'
import { tmpdir } from 'node:os'

// Playwright from this project, or else a global install (as scripts/rasterize-collected-svg.mjs).
const require = createRequire(import.meta.url)
let playwright
try {
  playwright = require('playwright')
} catch {
  playwright = require(require.resolve('playwright', { paths: [process.env.NODE_PATH ?? '', '/usr/lib/node_modules', '/usr/local/lib/node_modules', '/opt/node22/lib/node_modules'] }))
}

const [source, target, width = 2000] = process.argv.slice(2)
const W = Number(width)
const H = Math.round(W * 2997.159090909091 / 1000)
const dir = mkdtempSync(join(tmpdir(), 'wildlife-trees-'))
copyFileSync(resolve(source), join(dir, 'drawing.svg'))
writeFileSync(join(dir, 'page.html'), `<body style="margin:0;background:#fff"><img id="i" src="drawing.svg" style="display:block;width:${W}px;height:${H}px">`)
const browser = await playwright.chromium.launch()
const page = await browser.newPage({ viewport: { width: W, height: H } })
await page.goto('file://' + join(dir, 'page.html'))
await page.waitForFunction(() => document.getElementById('i').complete && document.getElementById('i').naturalWidth > 0, null, { timeout: 120000 })
await page.screenshot({ path: resolve(target) })
await browser.close()
rmSync(dir, { recursive: true })
console.log(`${W} × ${H} → ${target}`)
