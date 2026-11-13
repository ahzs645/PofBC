import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'
import { manualPages } from './vendor/brandkit/src/vite.js'

// @firstform/json-url is vendored as a git submodule (see README). Its codec registry references
// every algorithm it supports, a few of which are backed by Node built-ins; the share engine
// enables only lz, so the rest resolve to a stub that explains itself if anything reaches them.
const unusedCodec = fileURLToPath(new URL('./src/site/unusedCodec.js', import.meta.url))
// Patcher (SVG to embroidered patch, and its patch library by organization) is a git submodule too
// (see README). It ships TypeScript source, which Vite compiles with its digitizing worker, so it is
// aliased to its source rather than installed: installing it would also install its own toolchain.
const patcher = (entry) => fileURLToPath(new URL(`./vendor/patcher/src/${entry}`, import.meta.url))
// brandkit (brand kits from one brand.json, and the manual library) is a submodule as well, aliased
// to its source the same way. It holds the Visual Guides' pages, which its plugin serves and copies
// to visual-guides/, the address they had when they lived in public/. Its React components must
// share this app's React, so React is deduplicated.
const brandkit = (path) => fileURLToPath(new URL(`./vendor/brandkit/${path}`, import.meta.url))

// PlateForge (licence plates, drawn as SVG from its region data) is a submodule too, aliased to its
// embed entry points (vendor/plateforge/docs/embed.md): `plateforge/bc` registers British Columbia
// alone, and `plateforge` is the renderer and gallery API. Its fonts come from the @fontsource
// packages this app installs at PlateForge's pinned versions.
const plateforge = (entry) => fileURLToPath(new URL(`./vendor/plateforge/src/embed/${entry}`, import.meta.url))

// geo-toolkit (maps, map UI) is a submodule too. Its source is TypeScript with Tailwind CSS, so the
// site imports its compiled dist/, which scripts/build-geo-toolkit.mjs builds as part of
// build:assets. The Health Maps view draws its map with it.
const geoToolkit = (entry) => fileURLToPath(new URL(`./vendor/geo-toolkit/dist/${entry}`, import.meta.url))

export default defineConfig(({ command }) => ({
  plugins: [react(), manualPages({ pack: 'bc', mount: 'visual-guides' })],
  // Scan the host entry rather than example applications within vendored repositories.
  optimizeDeps: { entries: ['index.html'] },
  resolve: {
    alias: [
      { find: 'node:zlib', replacement: unusedCodec },
      { find: 'path', replacement: unusedCodec },
      { find: /^patcher$/, replacement: patcher('index.ts') },
      { find: /^patcher\/library$/, replacement: patcher('library.ts') },
      { find: /^brandkit\/studio$/, replacement: brandkit('src/studio/TemplateStudio.jsx') },
      { find: /^brandkit\/manuals$/, replacement: brandkit('src/manuals/index.js') },
      { find: /^brandkit$/, replacement: brandkit('src/engine/index.js') },
      { find: /^plateforge\/bc$/, replacement: plateforge('bc.ts') },
      { find: /^plateforge$/, replacement: plateforge('index.ts') },
      { find: /^@pgmaps\/geo-toolkit\/styles\.css$/, replacement: geoToolkit('styles.css') },
      { find: /^@pgmaps\/geo-toolkit\/(map|ui|workspace|format|calculations)$/, replacement: geoToolkit('$1/index.js') }
    ],
    dedupe: ['react', 'react-dom', 'maplibre-gl']
  },
  // GitHub Pages serves a project site from a repository subpath; local dev serves it from the
  // root. BASE_PATH lets the workflow pass the real repository name, so renaming the repository
  // cannot silently produce a build whose asset URLs all 404.
  base: process.env.BASE_PATH || (command === 'build' ? '/PofBC/' : '/'),
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
}))
