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
    // By the section's id, not its heading's wording, which has changed ("Artwork held" to "Artwork").
    assert.ok(html.includes('id="identity-artwork"'), `${subject.id}: missing artwork section`)
    assert.ok(!html.includes('src="undefined"'), `${subject.id}: undefined image`)
    if (subject.hasArtwork) assert.match(html, /<(img|svg)\b/, `${subject.id}: artwork does not render`)
    else assert.ok(html.includes('class="identity-empty"'), `${subject.id}: missing evidence must stay visible`)
    for (const [, url] of html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)) {
      assert.ok(url.startsWith('/PofBC/'), `${subject.id}: asset misses the project base: ${url}`)
      assert.ok(existsSync(resolve(root, 'public', url.slice('/PofBC/'.length))), `${subject.id}: missing local image: ${url}`)
    }
    renders++
  }
  const renderSubject = (id) => renderToStaticMarkup(React.createElement(components.IdentitySubjectDetail, {
    subject: model.identitySubjectById(id), theme: 'light', ...callbacks
  }))
  const vectorLead = renderSubject('camosun-college')
  assert.match(vectorLead, /Open official vector source/)
  assert.match(vectorLead, /href="https:\/\/camosun\.ca\/themes\/cam\/logo\.svg"/)
  assert.doesNotMatch(vectorLead, /<img\b[^>]*\bsrc="https:/)
  assert.match(vectorLead, /No separately held artwork/)
  const shared = renderSubject('ubc-okanagan-campus')
  assert.match(shared, /Shared branding/)
  assert.match(shared, /subject=university-of-british-columbia/)
  assert.match(shared, /No separately held artwork/)
  const cover = renderSubject('vancouver-school-of-art')
  assert.match(cover, /Publication cover, institutional status unconfirmed/)
  assert.doesNotMatch(cover, /Open official vector source/)
  const register = renderToStaticMarkup(React.createElement(components.IdentityCoverageBrowser, { onHome() {}, onOpenSubject() {} }))
  assert.ok(register.includes(`${model.IDENTITY_COVERAGE.length} subjects`), 'register count does not render')
  for (const wording of [
    '0 with artwork in the gallery', '24 with verified native-vector sources',
    '7 with observed nonvector artwork only', '18 without distinct verified logo artwork'
  ]) assert.ok(register.includes(wording), `missing post-secondary count: ${wording}`)
  const overview = renderToStaticMarkup(React.createElement(components.IdentityCoverageOverview, callbacks))
  assert.ok(overview.includes('Browse the register'), 'register is not reachable from overview')
  const { CollectedMarkView } = await server.ssrLoadModule('/src/gallery/CollectedMarkView.jsx')
  const { collectedEntriesOf } = await server.ssrLoadModule('/src/gallery/collectedCollections.js')
  const trade = collectedEntriesOf('bc-trade-development-corporation')
    .find(({ id }) => id === 'bc-trade-1991-rebuilt')
  assert.ok(trade, 'BC Trade reconstruction missing')
  const tradeHtml = renderToStaticMarkup(React.createElement(CollectedMarkView, { entry: trade }))
  assert.match(tradeHtml, /SVG · Reconstruction · Vector artwork/)
  assert.match(tradeHtml, /Download reconstruction SVG/)
  assert.match(tradeHtml, /Download 1991 back-cover scan/)
  assert.match(tradeHtml, /The exact typeface is not identified/)
  assert.match(tradeHtml, /The download is the reconstruction, not original artwork/)
  assert.doesNotMatch(tradeHtml, /The download is the file as published/)
  const { TIMELINES } = await server.ssrLoadModule('/src/gallery/timelines.js')
  const crest = TIMELINES['bc-wildfire-service'].eras.find(({ id }) => id === 'bcws-oval-crest')
  assert.equal(crest.years, 'June 2021')
  assert.equal(crest.applicability.years, crest.years)
  assert.match(crest.applicability.note, /2015 news release dates the name only/)
  console.log(`Rendered ${renders} subject pages (light and dark), register and overview; checked local images at /PofBC/.`)
} finally {
  await server.close()
}
