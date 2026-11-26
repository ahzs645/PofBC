// Runs against a temporary Vite server unless a URL is supplied. Requires Playwright and Chromium.
// npm run check:segmented -- [http://localhost:5173/dev/data] [--all-gallery]
import { createRequire } from 'node:module'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { GALLERY_COLLECTIONS, entriesOf } from '../src/gallery/collections.js'
import { VIEW_LOADERS } from '../src/site/viewLoaders.js'

const args = process.argv.slice(2)
const address = args.find((arg) => !arg.startsWith('--'))
const require = createRequire(import.meta.url)
let chromium
try {
  ({ chromium } = require('playwright'))
} catch {
  console.error('Install Playwright and its Chromium browser to run this check.')
  process.exit(1)
}

const widths = [320, 390, 576, 1280]
const views = ['generator', ...Object.keys(VIEW_LOADERS)]
const viewPages = views.map((view) => ({ view }))
const detailPages = [
  { view: 'salaries', browse: 'positions' },
  { view: 'salaries', browse: 'workforce' },
  { view: 'salaries', person: 'ionescu|diana', 'person-at': 'provincial-health-services-authority' },
  { view: 'salaries', employer: 'provincial-health-services-authority' },
  { view: 'salaries', title: 'director' },
  { view: 'posters', poster: 'coastal-forest' },
  { view: 'pins', pin: 'welcome-bc-pattison' },
  { view: 'gallery', logos: 'bc-hydro', mark: 'bc-hydro-current-colour' },
  { view: 'gallery', logos: 'collected-advanced-systems-institute-of-bc', mark: 'asi-exchange-square' },
  { view: 'gallery', logos: 'collected-advanced-systems-institute-of-bc', mark: 'asi-nextphase' }
]
const galleryPages = GALLERY_COLLECTIONS.flatMap((collection) => entriesOf(collection)
  .filter((entry) => entry.versions?.length > 1 || entry.paletteGroup)
  .map((entry) => ({ view: 'gallery', logos: collection.id, mark: entry.id })))
const routes = new Map([...viewPages, ...detailPages, ...(args.includes('--all-gallery') ? galleryPages : [])]
  .map((params) => [new URLSearchParams(params).toString(), params]))

const selector = ':is(.segmented, .pv-seg)'
const tolerance = 2

// Executed in Chromium so the measurements include actual fonts, grid tracks and theme styles.
function inspect({ selector, tolerance }) {
  const rgb = (color) => color.match(/[\d.]+/g)?.map(Number) ?? [0, 0, 0, 0]
  const blend = (foreground, background) => {
    const alpha = foreground[3] ?? 1
    return background.map((channel, i) => foreground[i] * alpha + channel * (1 - alpha))
  }
  const luminance = (color) => color.reduce((sum, channel, i) => {
    const s = channel / 255
    return sum + [0.2126, 0.7152, 0.0722][i] * (s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4)
  }, 0)
  const contrast = (button) => {
    const layers = []
    for (let element = button; element; element = element.parentElement) {
      const layer = rgb(getComputedStyle(element).backgroundColor)
      layers.push(layer)
      if ((layer[3] ?? 1) === 1) break
    }
    const ground = layers.reverse().reduce((background, layer) => blend(layer, background), [255, 255, 255])
    const foreground = blend(rgb(getComputedStyle(button).color), ground)
    const a = luminance(foreground)
    const b = luminance(ground)
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
  }

  const issues = []
  let groups = 0
  for (const group of document.querySelectorAll(selector)) {
    if (!group.getClientRects().length) continue
    groups++
    const label = group.getAttribute('aria-label') ??
      document.getElementById(group.getAttribute('aria-labelledby'))?.textContent ?? group.className
    const bounds = group.getBoundingClientRect()
    if (bounds.left < -tolerance || bounds.right > document.documentElement.clientWidth + tolerance) {
      issues.push(`${label}: control extends beyond the viewport`)
    }
    if (group.scrollWidth > group.clientWidth + tolerance) issues.push(`${label}: options overflow the track`)
    const buttons = [...group.querySelectorAll(':scope > button')].filter((button) => button.getClientRects().length)
    if (getComputedStyle(group).display.endsWith('flex')) {
      const rows = Map.groupBy(buttons, (button) => button.offsetTop)
      const style = getComputedStyle(group)
      const trackWidth = group.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight)
      for (const row of rows.values()) {
        if (rows.size > 1 && row.length === 1 && row[0].offsetWidth < trackWidth - tolerance) {
          issues.push(`${label}: a wrapped option leaves an empty part of its row`)
        }
      }
    }
    for (const button of buttons) {
      if (button.disabled) continue
      const name = button.innerText.trim() || button.getAttribute('aria-label')
      if (button.scrollWidth > button.clientWidth + tolerance || button.scrollHeight > button.clientHeight + tolerance) {
        issues.push(`${label} / ${name}: label overflows its button`)
      }
      // Icon-only choices do not have normal-size text to measure.
      if (!button.innerText.trim()) continue
      const ratio = contrast(button)
      if (ratio < 4.5) issues.push(`${label} / ${name}: text contrast ${ratio.toFixed(2)}:1`)
    }
  }
  return { groups, issues }
}

let server
let browser
let cache
const results = []
const failures = []
try {
  let base = address
  if (!base) {
    const { createServer } = await import('vite')
    cache = mkdtempSync(join(tmpdir(), 'pofbc-segmented-'))
    server = await createServer({ cacheDir: cache, logLevel: 'error', server: { host: '127.0.0.1', port: 0 } })
    await server.listen()
    base = new URL('dev/data', server.resolvedUrls.local[0]).href
  }
  browser = await chromium.launch()
  // Discover real deep links for catalogue viewers rather than guessing their asset IDs.
  const discover = await browser.newPage()
  for (const [view, param] of Object.entries({ patches: 'patch', badges: 'patch', 'paper-models': 'model' })) {
    const url = new URL(base)
    url.searchParams.set('view', view)
    await discover.goto(url.href)
    const link = discover.locator(`a[href*="&${param}="]`).first()
    const params = new URL(await link.evaluate((anchor) => anchor.href)).searchParams
    routes.set(params.toString(), Object.fromEntries(params))
  }
  await discover.close()

  const jobs = [...routes.entries()].flatMap(([query, params]) => ['light', 'dark'].map((colorScheme) => ({ query, params, colorScheme })))
  const worker = async () => {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
    page.setDefaultTimeout(10_000)
    try {
      for (let job = jobs.shift(); job; job = jobs.shift()) {
        const { query, params, colorScheme } = job
        const url = new URL(base)
        url.search = query
        try {
          await page.emulateMedia({ colorScheme })
          await page.goto(url.href, { waitUntil: 'domcontentloaded' })
          await page.locator('.app > header + :not(p), .gov').first().waitFor({ state: 'attached' })
          // Wait for the control itself on artwork details with versions, which load lazily.
          if (params.mark) await page.locator(selector).first().waitFor()
          if (params.employer) await page.getByRole('group', { name: 'Show records', exact: true }).waitFor()
          if (params.patch) await page.locator('.patch').first().waitFor()
          if (params.pin) await page.locator('.pv:not(.pv-loading)').first().waitFor()
          if (params.poster) {
            const exportButton = page.getByRole('button', { name: 'Export', exact: true })
            await exportButton.click()
            await page.locator('.pv-seg').last().waitFor()
          }
          await page.mouse.move(0, 0)
          await page.evaluate(() => document.fonts.ready)
          for (const width of widths) {
            await page.setViewportSize({ width, height: 900 })
            const result = await page.evaluate(inspect, { selector, tolerance })
            results.push({ query, colorScheme, width, ...result })
          }
        } catch (error) {
          const failure = `${query} (${colorScheme}): ${error.message.split('\n')[0]}`
          failures.push(failure)
          console.error(failure)
        }
      }
    } finally {
      await page.close()
    }
  }
  await Promise.all(Array.from({ length: 4 }, worker))
} finally {
  await browser?.close()
  await server?.close()
  if (cache) rmSync(cache, { recursive: true, force: true })
}

const findings = results.flatMap(({ query, colorScheme, width, issues }) =>
  issues.map((issue) => `${query} (${colorScheme}, ${width}px): ${issue}`))
const withControls = new Set(results.filter((result) => result.groups > 0).map((result) => result.query))
console.log(`${routes.size} URLs requested, ${withControls.size} with visible segmented controls, ${results.length} viewport and theme checks.`)
for (const finding of findings.sort()) console.error(finding)
if (findings.length || failures.length) process.exitCode = 1
