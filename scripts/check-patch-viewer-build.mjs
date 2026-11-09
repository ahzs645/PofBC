// Build the actual patch viewer and dependencies without the unrelated full-site asset pipeline.
// Run: node scripts/check-patch-viewer-build.mjs
import { cpSync, existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath, pathToFileURL } from 'node:url'
import assert from 'node:assert/strict'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const require = createRequire(join(root, 'package.json'))
const { build } = await import(pathToFileURL(require.resolve('vite')).href)
const { default: react } = await import(pathToFileURL(require.resolve('@vitejs/plugin-react')).href)
const { default: siteConfig } = await import(pathToFileURL(join(root, 'vite.config.js')).href)
const sourceConfig = siteConfig({ command: 'build', mode: 'production' })
const entry = mkdtempSync(join(root, '.patch-viewer-integration-'))
const output = mkdtempSync(join(tmpdir(), 'pofbc-patch-viewer-build-'))
assert.ok(!output.startsWith(`${root}/`), 'Build output must stay outside the tracked repository')

try {
  writeFileSync(join(entry, 'index.html'), '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PofBC patch review integration</title></head><body><div id="root"></div><script type="module" src="/main.jsx"></script></body></html>')
  writeFileSync(join(entry, 'main.jsx'), `
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { PatchesView } from '../src/patches/PatchesView.jsx'
import '../src/site/site.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
createRoot(document.getElementById('root')).render(
  <StrictMode><div className="app"><header className="masthead"><h1 className="masthead__crumbs">Province of BC / Patches</h1></header><PatchesView /></div></StrictMode>
)
`)
  await build({
    configFile: false,
    root: entry,
    base: sourceConfig.base,
    plugins: [react()],
    resolve: sourceConfig.resolve,
    publicDir: false,
    logLevel: 'warn',
    build: { ...sourceConfig.build, outDir: output, emptyOutDir: false, reportCompressedSize: false },
  })
  cpSync(join(root, 'public/patch-review'), join(output, 'patch-review'), { recursive: true })
  const index = JSON.parse(readFileSync(join(output, 'patch-review/index.json'), 'utf8'))
  let crops = 0
  for (const patch of index.patches) {
    for (const source of patch.sources ?? []) {
      if (!source.cropUrl || /^https?:\/\//.test(source.cropUrl)) continue
      assert.ok(existsSync(resolve(output, source.cropUrl)), `${patch.id}: missing ${source.cropUrl}`)
      crops++
    }
  }
  const html = readFileSync(join(output, 'index.html'), 'utf8')
  assert.ok(html.includes(`${sourceConfig.base}assets/`), 'Production base is absent from HTML asset links')
  const assets = readdirSync(join(output, sourceConfig.build.assetsDir))
  assert.ok(assets.some((name) => name.endsWith('.js')), 'No JS bundle emitted')
  assert.ok(assets.some((name) => name.endsWith('.css')), 'No CSS bundle emitted')
  assert.ok(assets.some((name) => name.includes('worker') && name.endsWith('.js')), 'Patcher digitizing worker missing')
  console.log(JSON.stringify({ output, base: sourceConfig.base, patchRecords: index.patches.length, sourceCropReferencesChecked: crops, emittedAssetCount: assets.length, result: 'PASS: real patch viewer, CSS, library assets and worker bundled' }, null, 2))
} finally {
  rmSync(entry, { recursive: true, force: true })
}
