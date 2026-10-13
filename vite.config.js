import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'

// @firstform/json-url is vendored as a git submodule (see README). Its codec registry references
// every algorithm it supports, a few of which are backed by Node built-ins; the share engine
// enables only lz, so the rest resolve to a stub that explains itself if anything reaches them.
const unusedCodec = fileURLToPath(new URL('./src/site/unusedCodec.js', import.meta.url))
// Patcher (SVG to embroidered patch, and its patch library by organization) is a git submodule too
// (see README). It ships TypeScript source, which Vite compiles with its digitizing worker, so it is
// aliased to its source rather than installed: installing it would also install its own toolchain.
const patcher = (entry) => fileURLToPath(new URL(`./vendor/patcher/src/${entry}`, import.meta.url))

export default defineConfig(({ command }) => ({
  plugins: [react()],
  resolve: {
    alias: [
      { find: 'node:zlib', replacement: unusedCodec },
      { find: 'path', replacement: unusedCodec },
      { find: /^patcher$/, replacement: patcher('index.ts') },
      { find: /^patcher\/library$/, replacement: patcher('library.ts') }
    ]
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
