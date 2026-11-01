// Review the real health-map view without the unrelated licensed artwork fonts.
// npm run preview:health-map; add -- --build for a standalone production build.
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, cpSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { build, createServer } from 'vite'
import react from '@vitejs/plugin-react'
import siteConfig from '../vite.config.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const args = process.argv.slice(2)
const option = (key, fallback) => args.includes(key) ? args[args.indexOf(key) + 1] : fallback
const temp = mkdtempSync(join(root, '.health-map-preview-'))
const cleanup = () => rmSync(temp, { recursive: true, force: true })
process.on('exit', cleanup)
writeFileSync(join(temp, 'index.html'), '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PofBC health-map preview</title></head><body><div id="root"></div><script type="module" src="/main.jsx"></script></body></html>')
writeFileSync(join(temp, 'main.jsx'), `
import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HealthStoryView } from '../src/health/HealthStoryView.jsx'
import '../src/site/site.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
createRoot(document.getElementById('root')).render(<StrictMode><div className="app"><header className="masthead"><h1 className="masthead__crumbs">Province of BC / Health Maps preview</h1></header><HealthStoryView /></div></StrictMode>)
`)
// Keep the same toolkit entry points and React deduplication as the full app.
const config = { configFile: false, root: temp, base: option('--base', '/'),
  plugins: [react()], resolve: siteConfig({ command: args.includes('--build') ? 'build' : 'serve' }).resolve,
  publicDir: false, server: { host: '0.0.0.0', port: Number(option('--port', 4174)), strictPort: true, fs: { allow: [root] } } }
if (args.includes('--build')) {
  const outDir = resolve(option('--out', join(root, 'dist-health-map')))
  if (outDir === root || root.startsWith(`${outDir}/`)) throw new Error('Preview output must not replace the repository or its parents')
  await build({ ...config, build: { outDir, emptyOutDir: false } })
  cpSync(join(root, 'public/health-geography'), join(outDir, 'health-geography'), { recursive: true })
  console.log(`Health-map preview built at ${outDir}`)
} else {
  const publicDir = join(temp, 'public')
  mkdirSync(publicDir)
  cpSync(join(root, 'public/health-geography'), join(publicDir, 'health-geography'), { recursive: true })
  const server = await createServer({ ...config, publicDir })
  await server.listen()
  server.printUrls()
  const shutdown = async () => { await server.close(); cleanup(); process.exit(0) }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}
