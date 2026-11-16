// Exercise the actual React subject/register components against every accepted record without
// needing a browser. This checks rendering and asset URLs; it is not a visual or interaction test.
import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'
import react from '@vitejs/plugin-react'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const server = await createServer({
  root, configFile: false, plugins: [react()], base: '/PofBC/',
  optimizeDeps: { noDiscovery: true, entries: [] },
  server: { middlewareMode: true }, appType: 'custom'
})
try {
  const components = await server.ssrLoadModule('/src/gallery/IdentityCoverage.jsx')
  const model = await server.ssrLoadModule('/src/gallery/identityCoverage.js')
  const callbacks = { onOpenSubject() {}, onOpenRegister() {}, onChooseCollection() {}, onOpenGovernment() {} }
  let renders = 0
  for (const subject of model.IDENTITY_COVERAGE) for (const theme of ['light', 'dark']) {
    const html = renderToStaticMarkup(React.createElement(components.IdentitySubjectDetail, { subject, theme, ...callbacks }))
    assert.ok(html.includes('Artwork held'), `${subject.id}: missing artwork section`)
    assert.ok(!html.includes('src="undefined"'), `${subject.id}: undefined image`)
    if (subject.hasArtwork) assert.match(html, /<(img|svg)\b/, `${subject.id}: artwork does not render`)
    else assert.ok(html.includes('No accepted artwork yet.'), `${subject.id}: missing evidence must stay visible`)
    for (const [, url] of html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)) {
      assert.ok(url.startsWith('/PofBC/'), `${subject.id}: asset misses the project base: ${url}`)
      assert.ok(existsSync(resolve(root, 'public', url.slice('/PofBC/'.length))), `${subject.id}: missing local image: ${url}`)
    }
    renders++
  }
  const register = renderToStaticMarkup(React.createElement(components.IdentityCoverageBrowser, { onHome() {}, onOpenSubject() {} }))
  assert.ok(register.includes(`${model.IDENTITY_COVERAGE.length} subjects`), 'register count does not render')
  const overview = renderToStaticMarkup(React.createElement(components.IdentityCoverageOverview, callbacks))
  assert.ok(overview.includes('Browse the register'), 'register is not reachable from overview')
  console.log(`Rendered ${renders} subject pages (light and dark), register and overview; checked local images at /PofBC/.`)
} finally {
  await server.close()
}
