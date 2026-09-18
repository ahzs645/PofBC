// Builds the vendored @firstform/json-url submodule.
//
// json-url gitignores its dist/, and every entry in its package `exports` points there, so on a
// fresh checkout the `file:vendor/json-url` dependency resolves to files that do not exist yet.
// This runs ahead of dev, build and test to guarantee a current dist/ before Vite resolves the
// import, and is a no-op when the submodule is already built, so the usual dev loop pays nothing.

import { execFileSync } from 'node:child_process'
import { existsSync, readdirSync, statSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const packageDir = join(root, 'vendor', 'json-url')

if (!existsSync(join(packageDir, 'package.json'))) {
  console.warn(
    '[json-url] vendor/json-url is not checked out — run `git submodule update --init --recursive`.\n' +
    '           Skipping; the share link will be unavailable until it is built.'
  )
  process.exit(0)
}

// Newest mtime anywhere in a tree, so the build only reruns when the source is newer than dist.
const newestMtime = (directory) => readdirSync(directory, { withFileTypes: true })
  .reduce((newest, entry) => {
    const full = join(directory, entry.name)
    const mtime = entry.isDirectory() ? newestMtime(full) : statSync(full).mtimeMs
    return Math.max(newest, mtime)
  }, 0)

const distEntry = join(packageDir, 'dist', 'web-share.js')
const sourceDir = join(packageDir, 'src')

if (existsSync(distEntry) && statSync(distEntry).mtimeMs >= newestMtime(sourceDir)) {
  process.exit(0)
}

const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm'
const run = (args) => execFileSync(npm, args, { cwd: packageDir, stdio: 'inherit' })

// --ignore-scripts skips json-url's husky `prepare` hook, which is meaningless inside a submodule
// checkout and can fail there. Its build tools are plain devDependencies.
if (!existsSync(join(packageDir, 'node_modules'))) {
  console.log('[json-url] installing build dependencies…')
  run(['ci', '--ignore-scripts'])
}

console.log('[json-url] building…')
run(['run', 'build'])
