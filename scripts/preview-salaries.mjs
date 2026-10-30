// Exercise the real salary components and published data without the unrelated licensed
// artwork-font build. npm run preview:salaries; add -- --build to create a static preview.
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, cpSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { build, createServer } from 'vite'
import react from '@vitejs/plugin-react'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const args = process.argv.slice(2)
const option = (key, fallback) => args.includes(key) ? args[args.indexOf(key) + 1] : fallback
const temp = mkdtempSync(join(root, '.salary-preview-'))
const cleanup = () => rmSync(temp, { recursive: true, force: true })
process.on('exit', cleanup)
writeFileSync(join(temp, 'index.html'), '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PofBC salaries preview</title></head><body><div id="root"></div><script type="module" src="/main.jsx"></script></body></html>')
writeFileSync(join(temp, 'main.jsx'), `
import React from 'react'
import { createRoot } from 'react-dom/client'
import { SalariesView } from '../src/salaries/SalariesView.jsx'
import '../src/site/site.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
createRoot(document.getElementById('root')).render(<div className="app"><header className="masthead"><h1 className="masthead__crumbs">Province of BC / Salaries</h1></header><SalariesView /></div>)
`)
// A fixed-width iframe uses real viewport media queries when the browser automation
// surface cannot change its outer window size. Query parameters pass to the real view.
writeFileSync(join(temp, 'mobile.html'), '<!doctype html><html lang="en"><meta charset="UTF-8"><title>Salary narrow-screen review</title><style>body{margin:0;background:#ddd;display:grid;justify-content:center}iframe{width:390px;height:844px;border:0;background:white}</style><iframe title="390 pixel salary viewport"></iframe><script>document.querySelector("iframe").src="/index.html"+location.search</script></html>')
const config = { configFile: false, root: temp, base: '/', plugins: [react()], publicDir: false,
  server: { host: '0.0.0.0', port: Number(option('--port', 4173)), strictPort: true, fs: { allow: [root] } } }
if (args.includes('--build')) {
  const outDir = resolve(option('--out', join(root, 'dist-salaries')))
  if (outDir === root || root.startsWith(`${outDir}/`)) throw new Error('Preview output must not replace the repository or its parents')
  await build({ ...config, build: { outDir, emptyOutDir: false, rollupOptions: { input: { main: join(temp, 'index.html'), mobile: join(temp, 'mobile.html') } } } })
  cpSync(join(root, 'public/salaries'), join(outDir, 'salaries'), { recursive: true })
  console.log(`Salary preview built at ${outDir}`)
} else {
  const publicDir = join(temp, 'public')
  mkdirSync(publicDir)
  cpSync(join(root, 'public/salaries'), join(publicDir, 'salaries'), { recursive: true })
  const server = await createServer({ ...config, publicDir })
  await server.listen()
  server.printUrls()
  const shutdown = async () => { await server.close(); cleanup(); process.exit(0) }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}
