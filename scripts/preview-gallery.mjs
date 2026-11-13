// Review the real gallery without rebuilding the unrelated licensed generator fonts.
// First run build-current-extras.mjs and build-fonts.mjs; the latter supports the repository's
// local TeX Gyre stand-in. Collected SVG logos already contain their original outlined lettering.
// node scripts/preview-gallery.mjs --build --base /PofBC/ --out dist-gallery
import { mkdtempSync, writeFileSync, rmSync, cpSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { build, createServer } from 'vite'
import react from '@vitejs/plugin-react'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const args = process.argv.slice(2)
const option = (key, fallback) => args.includes(key) ? args[args.indexOf(key) + 1] : fallback
const temp = mkdtempSync(join(root, '.gallery-preview-'))
const cleanup = () => rmSync(temp, { recursive: true, force: true })
process.on('exit', cleanup)
writeFileSync(join(temp, 'index.html'), '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PofBC gallery preview</title></head><body><div id="root"></div><script type="module" src="/main.jsx"></script></body></html>')
writeFileSync(join(temp, 'main.jsx'), `
import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GalleryView } from '../src/gallery/GalleryView.jsx'
import { useSiteTheme } from '../src/site/useTheme.js'
import '../src/site/site.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
const Preview = () => {
  const { name, toggle } = useSiteTheme()
  return <div className="app"><header className="masthead"><h1 className="masthead__crumbs">Province of BC / Gallery preview</h1><button type="button" onClick={toggle}>Switch to {name === 'light' ? 'dark' : 'light'}</button></header><GalleryView /></div>
}
createRoot(document.getElementById('root')).render(<StrictMode><Preview /></StrictMode>)
`)
const config = {
  configFile: false, root: temp, base: option('--base', '/'), plugins: [react()],
  resolve: { dedupe: ['react', 'react-dom'] }, publicDir: false,
  server: { host: '0.0.0.0', port: Number(option('--port', 4175)), strictPort: true, fs: { allow: [root] } }
}
if (args.includes('--build')) {
  const outDir = resolve(option('--out', join(root, 'dist-gallery')))
  if (outDir === root || root.startsWith(`${outDir}/`)) throw new Error('Preview output must not replace the repository or its parents')
  await build({ ...config, build: { outDir, emptyOutDir: false } })
  for (const directory of ['identity-collected', 'identity-display']) {
    cpSync(join(root, 'public', directory), join(outDir, directory), { recursive: true })
  }
  console.log(`Gallery preview built at ${outDir}`)
} else {
  const server = await createServer({ ...config, publicDir: join(root, 'public') })
  await server.listen()
  server.printUrls()
  const shutdown = async () => { await server.close(); cleanup(); process.exit(0) }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}
