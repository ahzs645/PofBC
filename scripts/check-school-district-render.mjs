// Render the actual pages and integration components. This verifies data and links, not browser interaction or visual layout.
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
  const { SchoolDistrictsView } = await server.ssrLoadModule('/src/schools/SchoolDistrictsView.jsx')
  const { SCHOOL_DISTRICTS, CURRENT_DISTRICTS } = await server.ssrLoadModule('/src/schools/districts.js')
  const { CollectedMarkView } = await server.ssrLoadModule('/src/gallery/CollectedMarkView.jsx')
  const { collectedEntriesOf } = await server.ssrLoadModule('/src/gallery/collectedCollections.js')
  const render = (params) => {
    globalThis.location = new URL(`https://example.test/PofBC/?${new URLSearchParams({ view: 'school-districts', ...params })}`)
    return renderToStaticMarkup(React.createElement(SchoolDistrictsView))
  }
  const directory = render({})
  assert.equal((directory.match(/class="schools__card"/g) ?? []).length, 60)
  for (const district of SCHOOL_DISTRICTS) {
    const html = render({ district: district.id })
    for (const section of ['connections', 'history', 'logos', 'sources']) assert.ok(html.includes(`id="district-${section}"`), `${district.id}: ${section}`)
    assert.ok(!html.includes('src="undefined"'), district.id)
    for (const [, src] of html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)) {
      assert.ok(src.startsWith('/PofBC/'), `${district.id}: base path ${src}`)
      assert.ok(existsSync(resolve(root, 'public', src.slice('/PofBC/'.length))), `${district.id}: ${src}`)
    }
    if (district.current) {
      assert.ok(html.includes(`employer=${district.employerSlug}`), district.id)
      assert.ok(html.includes(`logos=collected-${district.id}`), district.id)
    }
    for (const entry of collectedEntriesOf(district.id)) {
      const mark = renderToStaticMarkup(React.createElement(CollectedMarkView, { entry }))
      assert.ok(mark.includes(`Download ${entry.asset.format.toUpperCase()}`), entry.id)
      if (entry.asset.darkBackground) assert.ok(mark.includes('data-dark="true"'), entry.id)
    }
  }
  assert.match(render({ district: 'school-district-70' }), /Institutional origin/)
  assert.match(render({ district: 'school-district-93' }), /Sources give different dates/)
  assert.match(render({ district: 'does-not-exist' }), /District not found/)
  assert.match(render({ 'school-query': 'not-a-district-xyz' }), /No matching districts/)
  console.log(`Rendered ${SCHOOL_DISTRICTS.length} district details, ${CURRENT_DISTRICTS.length} current gallery collections, directory and empty states. Asset paths and connected links checked at /PofBC/.`)
} finally {
  if (previousLocation === undefined) delete globalThis.location
  else globalThis.location = previousLocation
  await server.close()
}
