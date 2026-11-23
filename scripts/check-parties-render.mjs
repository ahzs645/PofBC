// Render the Parties view's pages on the server. This verifies data and links, not browser interaction or layout.
import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'
import react from '@vitejs/plugin-react'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const server = await createServer({ root, configFile: false, plugins: [react()], base: '/PofBC/',
  optimizeDeps: { noDiscovery: true, entries: [] }, server: { middlewareMode: true }, appType: 'custom' })
const previousLocation = globalThis.location
try {
  const { PartiesView } = await server.ssrLoadModule('/src/parties/PartiesView.jsx')
  const { PARTIES, PARTY_GROUPS } = await server.ssrLoadModule('/src/parties/parties.js')
  const render = (params) => {
    globalThis.location = new URL(`https://example.test/PofBC/?${new URLSearchParams({ view: 'parties', ...params })}`)
    return renderToStaticMarkup(React.createElement(PartiesView))
  }
  const checkImages = (html, label) => {
    assert.ok(!html.includes('src="undefined"'), label)
    for (const [, src] of html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)) {
      assert.ok(src.startsWith('/PofBC/'), `${label}: base path ${src}`)
      assert.ok(existsSync(resolve(root, 'public', src.slice('/PofBC/'.length))), `${label}: ${src}`)
    }
    for (const [, href] of html.matchAll(/<a\b[^>]*\bhref="(\/PofBC\/parties\/[^"]+)"/g)) {
      assert.ok(existsSync(resolve(root, 'public', href.slice('/PofBC/'.length))), `${label}: ${href}`)
    }
  }
  const directory = render({})
  checkImages(directory, 'directory')
  assert.equal((directory.match(/class="parties__card"/g) ?? []).length, PARTIES.filter((party) => party.files).length)
  assert.equal((directory.match(/class="parties__lineage"/g) ?? []).length, PARTY_GROUPS.length)
  assert.equal((render({ 'party-scope': 'all' }).match(/class="parties__card"/g) ?? []).length, PARTIES.length)
  for (const party of PARTIES) {
    const html = render({ party: party.id })
    for (const section of ['logos', 'history', 'gaps', 'sources']) assert.ok(html.includes(`id="party-${section}"`), `${party.id}: ${section}`)
    assert.equal((html.match(/class="parties__design"/g) ?? []).length, party.designs.length, party.id)
    checkImages(html, party.id)
  }
  assert.match(render({ party: 'does-not-exist' }), /Party not found/)
  assert.match(render({ 'party-query': 'not-a-party-xyz' }), /No matching parties/)
  console.log(`Rendered the directory, ${PARTIES.length} party pages and the empty states. Image and download paths checked at /PofBC/.`)
} finally {
  if (previousLocation === undefined) delete globalThis.location
  else globalThis.location = previousLocation
  await server.close()
}
