// Screenshots of the salary pages at phone and desktop widths, with a word count for each, so a
// change to the interface can be checked for how much text it puts on screen.
//
// Run: npm run shots:salaries            (starts its own dev server)
//      npm run shots:salaries -- <url>   (uses a server already running at <url>)
//
// Needs Playwright with Chromium (`npm i -D playwright && npx playwright install chromium`); it is
// not a project dependency. Images and a summary go to .shots/salaries/, which is not committed.

import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const out = resolve(root, '.shots/salaries')

const PAGES = {
  landing: '',
  people: '&browse=people',
  positions: '&browse=positions',
  search: '&q=ionescu',
  person: '&person=ionescu%7Cdiana&person-at=provincial-health-services-authority',
  employer: '&employer=provincial-health-services-authority',
  'employer-people': '&employer=provincial-health-services-authority&employer-year=2023%2F24&show=people',
  title: '&title=director'
}
const VIEWPORTS = { mobile: { width: 390, height: 844 }, desktop: { width: 1280, height: 900 } }

let chromium
try {
  ({ chromium } = createRequire(import.meta.url)('playwright'))
} catch {
  console.error('Playwright is not installed. Run: npm i -D playwright && npx playwright install chromium')
  process.exit(1)
}

let server
let base = process.argv[2]
if (!base) {
  const { createServer } = await import('vite')
  server = await createServer({ root, logLevel: 'error', server: { port: 0, host: '127.0.0.1' } })
  await server.listen()
  base = server.resolvedUrls.local[0]
}

mkdirSync(out, { recursive: true })
const browser = await chromium.launch()
const rows = []
try {
  for (const [viewport, size] of Object.entries(VIEWPORTS)) {
    const context = await browser.newContext({ viewport: size })
    const page = await context.newPage()
    for (const [name, query] of Object.entries(PAGES)) {
      await page.goto(new URL(`?view=salaries${query}`, base).href, { waitUntil: 'networkidle' })
      await page.waitForTimeout(1500)
      await page.screenshot({ path: resolve(out, `${viewport}-${name}.png`), fullPage: true })
      const { words, height } = await page.evaluate(() => ({
        words: (document.querySelector('.salaries') ?? document.body).innerText.split(/\s+/).filter(Boolean).length,
        height: document.documentElement.scrollHeight
      }))
      rows.push({ viewport, page: name, words, height })
    }
    await context.close()
  }
} finally {
  await browser.close()
  await server?.close()
}

const table = ['viewport  page              words  height', ...rows.map((row) =>
  `${row.viewport.padEnd(9)} ${row.page.padEnd(17)} ${String(row.words).padStart(5)}  ${String(row.height).padStart(6)}`)].join('\n')
writeFileSync(resolve(out, 'summary.txt'), `${table}\n`)
console.log(`${table}\n\n→ ${out}`)
