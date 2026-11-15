// Browser acceptance of the actual complete production build. No app components are substituted.
// Build with BASE_PATH=/PofBC/ first. Optional Playwright/browser dependencies remain external.
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { createServer } from 'node:http'
import { createHash } from 'node:crypto'
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { DOCUMENT_ARMS_SPECIMENS } from '../../../src/documentArms/evidence.js'

const root = fileURLToPath(new URL('../../../', import.meta.url))
const localRequire = createRequire(path.join(root, 'package.json'))
const browserRequire = process.env.POFBC_BROWSER_DEPS
  ? createRequire(path.resolve(process.env.POFBC_BROWSER_DEPS)) : localRequire
const { chromium } = browserRequire('playwright')
const build = path.join(root, 'dist')
const output = path.resolve(process.env.POFBC_BROWSER_OUTPUT || path.join(root, 'tmp/historic-browser'))
await mkdir(output, { recursive: true })
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.json': 'application/json', '.pdf': 'application/pdf' }
const missing = [], external = [], pageErrors = [], checks = [], captures = [], downloads = []
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex')
const check = (label, assertion) => { assertion(); checks.push(label); console.log(`PASS ${label}`) }
const server = createServer(async (request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  if (pathname === '/favicon.ico') { response.writeHead(204).end(); return }
  const relative = pathname === '/PofBC/' ? 'index.html' : pathname.replace(/^\/PofBC\//, '')
  const file = path.resolve(build, relative)
  try {
    if (!pathname.startsWith('/PofBC/') || !file.startsWith(build + path.sep) || !(await stat(file)).isFile()) throw new Error('Not found')
    response.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' })
    response.end(await readFile(file))
  } catch {
    missing.push(pathname); response.writeHead(404).end('Not found')
  }
})
await new Promise((resolve, reject) => { server.on('error', reject); server.listen(0, '127.0.0.1', resolve) })
const origin = `http://127.0.0.1:${server.address().port}`
let browser
try {
  browser = await chromium.launch({ headless: true,
    ...(process.env.POFBC_CHROMIUM_EXECUTABLE ? { executablePath: process.env.POFBC_CHROMIUM_EXECUTABLE, args: ['--no-zygote'] } : {}) })
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, colorScheme: 'light', acceptDownloads: true })
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin !== origin) { external.push(route.request().url()); return route.abort('blockedbyclient') }
    return route.continue()
  })
  const page = await context.newPage()
  page.on('pageerror', error => pageErrors.push(error.message))
  page.on('console', message => { if (message.type() === 'error') pageErrors.push(message.text()) })
  await page.goto(`${origin}/PofBC/`, { waitUntil: 'networkidle' })
  await page.getByRole('button', { name: 'Historic', exact: true }).click()
  const artwork = page.locator('svg[data-identity="document-arms"]')
  await artwork.waitFor()
  const record = page.locator('.document-arms-source__record')
  const reference = page.getByLabel('Reference specimen', { exact: true })
  const sourceImage = record.locator('img')
  const decode = async () => { await sourceImage.scrollIntoViewIfNeeded(); await sourceImage.evaluate(image => image.decode()) }
  const click = name => page.getByRole('button', { name, exact: true }).click()
  const colour = page.locator('section.panel').filter({ has: page.getByRole('heading', { name: 'Colour', exact: true }) })
  const colourField = label => colour.locator('.field').filter({ has: page.locator('.field__label').getByText(label, { exact: true }) })
  const swatch = (label, name) => colourField(label).getByRole('button', { name, exact: true }).click()
  const setLinked = linked => colour.locator('input[type="checkbox"]').setChecked(linked)
  const layouts = [ ['Arms alone', 'emblem', 'mining-1954-title'], ['Split serif', 'split-serif', 'supplied-split-serif'], ['Government heading', 'government', 'oic-1121-heading'], ['Crown grant heading', 'split-blackletter', 'oic-1121-grant'] ]
  for (const device of [{ name: 'desktop', width: 1440, height: 1000 }, { name: 'phone', width: 390, height: 844 }, { name: 'small-phone', width: 320, height: 568 }]) {
    await page.setViewportSize({ width: device.width, height: device.height })
    for (const theme of ['light', 'dark']) {
      if (await page.locator('html').getAttribute('data-theme') !== theme) await click(`Switch to ${theme} mode`)
      for (const [label, layout, specimen] of layouts) {
        await click(label); await decode()
        assert.equal(await artwork.getAttribute('data-layout'), layout)
        assert.equal(await record.getAttribute('data-specimen'), specimen)
        assert.equal(await artwork.locator('image, text').count(), 0)
        const sizes = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth,
          image: (() => { const i = document.querySelector('.document-arms-source__record img'); return [i.naturalWidth, i.naturalHeight, i.getBoundingClientRect().width] })() }))
        const controlsFit = await page.locator('.controls .segmented').evaluateAll(groups => groups.every(group => {
          const bounds = group.getBoundingClientRect()
          return [...group.querySelectorAll('button')].every(button => {
            const box = button.getBoundingClientRect()
            return box.left >= bounds.left - 1 && box.right <= bounds.right + 1 && box.bottom <= bounds.bottom + 1
          })
        }))
        if (sizes.scroll > sizes.width + 1) {
          await page.screenshot({ path: path.join(output, 'overflow.png'), fullPage: true })
          console.log(await page.evaluate(() => [...document.querySelectorAll('body *')].map(el => ({ tag: el.tagName, class: String(el.className), text: el.textContent?.slice(0, 90), right: el.getBoundingClientRect().right, width: el.getBoundingClientRect().width, minWidth: getComputedStyle(el).minWidth })).filter(el => el.right > innerWidth + 1).slice(0, 30)))
        }
        check(`${device.name}/${theme}/${layout}: image decoded and no horizontal overflow`, () => {
          assert.ok(sizes.scroll <= sizes.width + 1, JSON.stringify(sizes)); assert.ok(sizes.image.every(n => n > 0))
          assert.ok(controlsFit, 'Segmented buttons must remain inside their visible tracks')
        })
        if (layout === 'split-blackletter') {
          const filename = `${device.name}-${theme}.png`
          await page.screenshot({ path: path.join(output, filename), fullPage: true })
          captures.push({ filename, viewport: { width: device.width, height: device.height }, theme, layout })
        }
      }
    }
  }
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }, { width: 320, height: 568 }]) {
    await page.setViewportSize(viewport)
    const visited = new Set()
    for (const [label] of layouts) {
      await click(label)
      const options = await reference.locator('option').evaluateAll(options => options.map(o => o.value))
      for (const value of options) {
        if (visited.has(value)) continue
        visited.add(value)
        await reference.selectOption(value); await decode()
        const expected = DOCUMENT_ARMS_SPECIMENS[value]
        const original = record.locator('a:not([aria-label])')
        assert.equal(await original.count(), expected.sourceUrl ? 1 : 0)
        if (expected.sourceUrl) {
          assert.equal(await original.getAttribute('href'), expected.sourceUrl)
          assert.equal(await original.getAttribute('target'), '_blank')
        }
        assert.equal(await sourceImage.getAttribute('alt'), expected.alt)
        const before = await artwork.evaluate(el => el.outerHTML)
        if (await page.getByRole('button', { name: 'Whole page', exact: true }).count()) {
          const detail = await sourceImage.getAttribute('src')
          await click('Whole page'); await decode()
          assert.equal(await sourceImage.getAttribute('alt'), expected.fullAlt)
          assert.equal(await page.getByRole('button', { name: 'Whole page', exact: true }).getAttribute('aria-pressed'), 'true')
          assert.notEqual(await sourceImage.getAttribute('src'), detail)
          assert.equal(await artwork.evaluate(el => el.outerHTML), before)
          await click('Detail'); await decode()
          assert.equal(await sourceImage.getAttribute('src'), detail)
        }
        const width = await page.evaluate(() => document.documentElement.scrollWidth)
        check(`${viewport.width}px reference ${value}: source link, decoded image and page/detail controls`, () => assert.ok(width <= viewport.width + 1))
      }
    }
    assert.equal(visited.size, 9)
  }
  await page.setViewportSize({ width: 1440, height: 1000 })
  await click('Government heading')
  assert.equal(await record.locator('a:not([aria-label])').getAttribute('href'), 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978#page=1')
  await click('Crown grant heading')
  assert.equal(await record.locator('a:not([aria-label])').getAttribute('href'), 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978#page=4')
  assert.match(await record.innerText(), /creation date and the grant’s issue date are not established/)
  checks.push('verified source links distinguish order page 1 from map page 4 and retain unknown dates')

  await setLinked(false); await swatch('Mark', 'black'); await swatch('Text', 'red')
  const historicText = await artwork.locator('[data-part="heading"]').getAttribute('fill')
  await click('Arms'); await setLinked(false); await setLinked(true); await click('Historic')
  assert.equal(await colour.locator('input[type="checkbox"]').isChecked(), false)
  assert.equal(await artwork.locator('[data-part="heading"]').getAttribute('fill'), historicText)
  checks.push('relinking another identity preserves Historic lettering and link preference')
  await swatch('Text', 'white'); await swatch('Background', 'Transparent'); await click('Arms alone')
  assert.equal(await page.locator('.stage__frame').getAttribute('data-backdrop'), 'light')
  assert.equal(await artwork.locator('[data-part="heading"]').count(), 0)
  assert.equal(await colour.locator('input[type="checkbox"]').count(), 0)
  assert.match(await colour.locator('.contrast-list').innerText(), /21:1/)
  checks.push('black arms ignore hidden white lettering for Auto backdrop and contrast')
  await click('Crown grant heading')
  assert.equal(await artwork.locator('[data-part="heading"]').getAttribute('fill'), '#ffffff')
  assert.equal(await page.locator('.stage__frame').getAttribute('data-backdrop'), 'dark')
  await click('Light')
  assert.equal(await page.locator('.stage__frame').getAttribute('data-backdrop'), 'light')
  assert.equal(await artwork.locator('[data-part="background"]').count(), 0)
  await click('Auto')
  checks.push('heading restores white lettering; manual preview backdrop does not paint export background')
  await swatch('Text', 'black'); await swatch('Background', 'white')
  for (const format of ['SVG', 'PDF', 'PNG', 'WebP', 'JPEG']) {
    await click(format)
    const [download] = await Promise.all([page.waitForEvent('download'), click(`Download ${format}`)])
    const filename = download.suggestedFilename()
    const destination = path.join(output, filename)
    await download.saveAs(destination)
    assert.equal(await download.failure(), null)
    const bytes = await readFile(destination)
    if (format === 'SVG') {
      const text = bytes.toString('utf8'); assert.match(text, /data-layout="split-blackletter"/)
      assert.match(text, /not a verified historical or official drawing/); assert.doesNotMatch(text, /<image\b|<text\b/)
    } else if (format === 'PDF') assert.equal(bytes.subarray(0, 5).toString(), '%PDF-')
    else if (format === 'PNG') assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a')
    else if (format === 'WebP') { assert.equal(bytes.subarray(0, 4).toString(), 'RIFF'); assert.equal(bytes.subarray(8, 12).toString(), 'WEBP') }
    else assert.equal(bytes.subarray(0, 3).toString('hex'), 'ffd8ff')
    downloads.push({ format, filename, bytes: bytes.length, sha256: sha256(bytes) })
  }
  checks.push('all five actual download buttons create files with correct signatures')
  await click('Copy link')
  const share = await page.getByLabel('Shareable link', { exact: true }).inputValue()
  assert.ok(new URL(share).searchParams.get('s'))
  await page.goto(share, { waitUntil: 'networkidle' })
  await artwork.waitFor()
  assert.equal(await artwork.getAttribute('data-layout'), 'split-blackletter')
  await click('Government heading'); await click('Copy readable link')
  const readable = new URL(await page.getByLabel('Shareable link', { exact: true }).inputValue())
  assert.equal(readable.searchParams.has('s'), false)
  assert.equal(JSON.parse(readable.searchParams.get('c')).documentLayout, 'government')
  checks.push('compressed link reopens actual app; readable link removes stale compressed token')
  assert.deepEqual(pageErrors, []); assert.deepEqual(missing, []); assert.deepEqual(external, [])
  const sourceFiles = {}
  for (const file of ['src/site/site.css', 'src/site/ExportPanel.jsx', 'src/site/App.jsx', 'src/site/DocumentArmsPanel.jsx', 'src/site/DocumentArmsPreview.jsx', 'src/site/lockupReducer.js', 'src/site/useLockupState.js', 'src/documentArms/evidence.js']) {
    sourceFiles[file] = sha256(await readFile(path.join(root, file)))
  }
  const result = { browserVersion: browser.version(), source: 'Complete local Vite production build at /PofBC/; not the deployed site or physical iOS devices', productionIndexSha256: sha256(await readFile(path.join(build, 'index.html'))), sourceFiles, checks, captures, downloads, pageErrors, missingAssets: missing, externalRequests: external, passed: true }
  await writeFile(path.join(output, 'browser-check.json'), JSON.stringify(result, null, 2) + '\n')
  console.log(JSON.stringify({ passed: true, checks: checks.length, captures: captures.length, downloads, browserVersion: browser.version(), output }, null, 2))
} finally {
  await browser?.close()
  await new Promise(resolve => server.close(resolve))
}
