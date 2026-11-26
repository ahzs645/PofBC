// Check the real gallery cards, version detail pages and downloaded bytes for the recovery batch.
// Run with NODE_PATH pointing to Playwright and CHROMIUM_EXECUTABLE_PATH if needed.
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import recovery from '../src/gallery/vectorRecoveryData.json' with { type: 'json' }
import { identitySubjectById } from '../src/gallery/identityCoverage.js'
import { collectionOfNode } from '../src/gallery/collections.js'

const root = fileURLToPath(new URL('../', import.meta.url))
const output = process.env.RECOVERY_QA_DIR ?? '/tmp/pofbc-vector-recovery-qa'
mkdirSync(output, { recursive: true })
const require = createRequire(import.meta.url)
const playwright = require(require.resolve('playwright', { paths: [process.env.NODE_PATH ?? '', '/usr/lib/node_modules', '/usr/local/lib/node_modules'] }))
const port = Number(process.env.RECOVERY_QA_PORT ?? 4176)
const origin = `http://127.0.0.1:${port}`
const server = spawn(process.execPath, ['scripts/preview-gallery.mjs', '--host', '127.0.0.1', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] })
let serverLog = ''
server.stdout.on('data', data => { serverLog += data })
server.stderr.on('data', data => { serverLog += data })
const report = { asOf: recovery.asOf, subjectRenders: 0, detailRenders: 0, verifiedDownloads: 0, screenshots: [], failures: [] }
const selectedSubjects = process.env.RECOVERY_QA_SUBJECTS?.split(',').filter(Boolean)
if (selectedSubjects) {
  for (const id of selectedSubjects) assert.ok(recovery.additions[id], `Unknown recovery subject: ${id}`)
  report.selectedSubjects = selectedSubjects
}
const representativeSubjects = new Set(['nicola-valley-institute-of-technology', 'college-of-new-caledonia', 'ubc-okanagan-campus', 'municipality-sparwood', 'airport-cycd', 'bc-treaty-commission'])
const representativeMarks = new Set(['airport-cycd-mountain-aircraft-2005-colour', 'recovered-ouc-audit-cover-2007', 'recovered-sooke-primary-horizontal-pantone', 'recovered-nvit-rider-circle-1989'])
let browser
try {
  await new Promise((resolve, reject) => {
    server.stdout.on('data', data => { if (data.toString().includes(String(port))) resolve() })
    server.on('exit', code => reject(new Error(`Preview server exited (${code}): ${serverLog}`)))
    setTimeout(() => reject(new Error(`Preview server did not start: ${serverLog}`)), 15000).unref()
  })
  browser = await playwright.chromium.launch(process.env.CHROMIUM_EXECUTABLE_PATH ? { executablePath: process.env.CHROMIUM_EXECUTABLE_PATH } : {})
  for (const theme of ['light', 'dark']) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, colorScheme: theme })
    await context.addInitScript(value => localStorage.setItem('pofbc-theme', value), theme)
    const page = await context.newPage()
    page.on('pageerror', error => report.failures.push({ theme, page: page.url(), error: error.message }))
    const inspectImages = async (label) => {
      const failures = await page.locator('img').evaluateAll(async images => {
        await Promise.all(images.map(image => image.decode().catch(() => {})))
        return images.filter(image => !image.complete || !image.naturalWidth).map(image => image.getAttribute('src'))
      })
      if (failures.length) report.failures.push({ theme, label, brokenImages: failures })
    }
    for (const [owner, assets] of Object.entries(recovery.additions)) {
      if (selectedSubjects && !selectedSubjects.includes(owner)) continue
      const subject = identitySubjectById(owner)
      await page.goto(`${origin}/?view=gallery&subject=${encodeURIComponent(owner)}`, { waitUntil: 'load' })
      await page.locator('#identity-artwork').waitFor()
      assert.ok((await page.locator('body').innerText()).includes(subject.label), owner)
      assert.equal(await page.locator('html').getAttribute('data-theme'), theme)
      await inspectImages(owner)
      report.subjectRenders++
      if (representativeSubjects.has(owner)) {
        const file = `${owner}-${theme}.png`
        await page.screenshot({ path: `${output}/${file}`, fullPage: true })
        report.screenshots.push(file)
      }
      const collection = collectionOfNode(owner)
      for (const asset of assets) {
        await page.goto(`${origin}/?view=gallery&logos=${encodeURIComponent(collection.id)}&mark=${encodeURIComponent(asset.id)}`, { waitUntil: 'load' })
        await page.locator('.gallery__recovered').waitFor()
        await inspectImages(asset.id)
        const sourceLink = page.locator(`a[download][href="/${asset.file}"]`)
        if (await sourceLink.count() !== 1) report.failures.push({ theme, asset: asset.id, missingDownload: asset.file })
        const text = await page.locator('body').innerText()
        if (!text.includes(asset.isVector ? 'Vector artwork' : 'Image')) report.failures.push({ theme, asset: asset.id, missingFormatLabel: true })
        report.detailRenders++
        if (theme === 'light') {
          const response = await context.request.get(`${origin}/${asset.file}`)
          assert.equal(response.status(), 200, asset.file)
          assert.equal(createHash('sha256').update(await response.body()).digest('hex'), asset.sha256, `${asset.id}: source download`)
          report.verifiedDownloads++
        }
        if (representativeMarks.has(asset.id)) {
          const file = `${asset.id}-${theme}.png`
          await page.screenshot({ path: `${output}/${file}`, fullPage: true })
          report.screenshots.push(file)
        }
      }
    }
    await context.close()
    console.log(`${theme}: gallery subjects, source versions and downloads checked`)
  }
} catch (error) {
  report.failures.push({ error: error.stack })
} finally {
  await browser?.close()
  server.kill('SIGTERM')
  writeFileSync(`${output}/server.log`, serverLog)
  writeFileSync(`${output}/render-report.json`, JSON.stringify(report, null, 2) + '\n')
}
console.log(JSON.stringify({ subjectRenders: report.subjectRenders, detailRenders: report.detailRenders, verifiedDownloads: report.verifiedDownloads, failures: report.failures }, null, 2))
if (report.failures.length) process.exitCode = 1
