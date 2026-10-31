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
// Reuse the pinned PGMaps story components directly, without the toolkit's optional map/editor
// dependencies or a separate package build. These entry points need only React and local helpers.
const storyToolkit = (entry) => fileURLToPath(new URL(`./vendor/geo-toolkit/src/${entry}`, import.meta.url))

export default defineConfig(({ command }) => ({
  plugins: [react()],
  // Scan the host entry rather than example applications within vendored repositories.
  optimizeDeps: { entries: ['index.html'] },
  resolve: {
    alias: [
      { find: 'node:zlib', replacement: unusedCodec },
      { find: 'path', replacement: unusedCodec },
      { find: /^patcher$/, replacement: patcher('index.ts') },
      { find: /^patcher\/library$/, replacement: patcher('library.ts') },
      { find: /^@pgmaps\/geo-toolkit\/stories\/components\/StorySidecar$/, replacement: storyToolkit('stories/components/StorySidecar.tsx') },
      { find: /^@pgmaps\/geo-toolkit\/stories\/components\/StoryChapterNavigation$/, replacement: storyToolkit('stories/components/StoryChapterNavigation.tsx') },
      { find: /^@pgmaps\/geo-toolkit\/workspace\/workspace-context$/, replacement: storyToolkit('workspace/workspace-context.tsx') },
      { find: /^@pgmaps\/geo-toolkit\/stories\/styles\.css$/, replacement: storyToolkit('stories/styles.css') }
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
