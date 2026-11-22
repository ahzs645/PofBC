// Review the real Logos and Initiatives views without rebuilding unrelated licensed generator fonts.
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
writeFileSync(join(temp, 'index.html'), '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PofBC collections preview</title></head><body><div id="root"></div><script type="module" src="/main.jsx"></script></body></html>')
writeFileSync(join(temp, 'main.jsx'), `
import React, { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { GalleryView } from '../src/gallery/GalleryView.jsx'
import { InitiativesView } from '../src/initiatives/InitiativesView.jsx'
import { legacyInitiativeUrl } from '../src/initiatives/initiativePlace.js'
import { NavigationContext, searchFor } from '../src/site/navigation.jsx'
import { writeHistory } from '../src/site/browserHistory.js'
import { ViewSwitcher, VIEWS } from '../src/site/ViewSwitcher.jsx'
import { SunGlyph, ThemeIcon } from '../src/site/icons.jsx'
import { useSiteTheme } from '../src/site/useTheme.js'
import { documentTitle, setDocumentMeta } from '../src/site/documentMeta.js'
import '../src/site/site.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
const initialView = () => {
  const migrated = legacyInitiativeUrl(location.href)
  if (migrated) history.replaceState(history.state, '', migrated)
  return new URLSearchParams(location.search).get('view') || 'gallery'
}
const Preview = () => {
  const { name, toggle } = useSiteTheme()
  const [view, setView] = useState(initialView)
  const [visit, setVisit] = useState(0)
  useEffect(() => {
    if (view !== 'initiatives') setDocumentMeta({ title: documentTitle(VIEWS.find(entry => entry.id === view)?.label) })
  }, [view])
  useEffect(() => {
    const restore = () => { setView(initialView()); setVisit(value => value + 1) }
    addEventListener('popstate', restore)
    return () => removeEventListener('popstate', restore)
  }, [])
  const navigate = params => {
    const url = new URL(location.href)
    url.search = searchFor(params)
    url.hash = ''
    writeHistory(url)
    setView(params.view || 'gallery')
    setVisit(value => value + 1)
    scrollTo({ top: 0 })
  }
  return <NavigationContext.Provider value={navigate}><div className="app">
    <header className="masthead"><h1 className="masthead__crumbs"><SunGlyph className="masthead__sun" /><span className="masthead__site">Province of BC</span><span className="masthead__slash" aria-hidden="true">/</span><ViewSwitcher view={view} onChange={view => navigate({ view })} /></h1><button type="button" className="icon-button" onClick={toggle} aria-label={'Switch to ' + (name === 'dark' ? 'light' : 'dark') + ' mode'}><ThemeIcon name={name} /></button></header>
    {view === 'initiatives' ? <InitiativesView key={visit} /> : view === 'gallery' ? <GalleryView key={visit} onOpenGovernment={(node, year) => navigate({view:'government',node,year})} /> : <p className="gallery__intro">This local review includes Logos and Initiatives. Use the view menu to return to either collection.</p>}
  </div></NavigationContext.Provider>
}
createRoot(document.getElementById('root')).render(<StrictMode><Preview /></StrictMode>)
`)
// Use the real menu while keeping this focused review independent of other views' asset builds.
const previewViewLoaders = {
  name: 'collections-preview-loaders',
  enforce: 'pre',
  resolveId(id, importer) {
    if (id === './viewLoaders.js' && importer?.endsWith('/src/site/ViewSwitcher.jsx')) return '\0collections-preview-loaders'
  },
  load(id) { if (id === '\0collections-preview-loaders') return 'export const preloadView = () => {}' }
}

const config = {
  configFile: false, root: temp, base: option('--base', '/'), plugins: [react(), previewViewLoaders],
  resolve: { dedupe: ['react', 'react-dom'] }, publicDir: false,
  server: { host: option('--host', '0.0.0.0'), port: Number(option('--port', 4175)), strictPort: true, fs: { allow: [root] } }
}
if (args.includes('--build')) {
  const outDir = resolve(option('--out', join(root, 'dist-gallery')))
  if (outDir === root || root.startsWith(`${outDir}/`)) throw new Error('Preview output must not replace the repository or its parents')
  await build({ ...config, build: { outDir, emptyOutDir: false } })
  for (const directory of ['identity-collected', 'identity-display', 'identity-expanded', 'unbc-origins', 'tourism']) {
    cpSync(join(root, 'public', directory), join(outDir, directory), { recursive: true })
  }
  console.log(`Logos and Initiatives preview built at ${outDir}`)
} else {
  const server = await createServer({ ...config, publicDir: join(root, 'public') })
  await server.listen()
  server.printUrls()
  const shutdown = async () => { await server.close(); cleanup(); process.exit(0) }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}
