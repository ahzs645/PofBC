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
import { summarizePostsecondaryArtwork } from '../src/gallery/postsecondaryArtwork.js'
import { EDITORIAL_LOGO_SPECIMENS } from '../src/gallery/editorialLogoSpecimens.js'
import { CNC_BRAND_RESOURCES, CNC_CURRENT_MARKS, CNC_HISTORICAL_MARKS, CNC_SUBJECT, cncCover } from '../src/gallery/cncIdentity.js'

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
    else if (subject.id !== CNC_SUBJECT) assert.ok(html.includes('class="identity-empty"'), `${subject.id}: missing evidence must stay visible`)
    const editorialImages = new Set((EDITORIAL_LOGO_SPECIMENS[subject.id] ?? []).map(({ src }) => src))
    for (const [, url] of html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)) {
      if (url.startsWith('data:image/webp;base64,') && editorialImages.has(url)) continue
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
  assert.doesNotMatch(vectorLead, /No separately held artwork/)
  assert.match(vectorLead, /recovered-official-camosun-college-vector/)
  const cnc = renderSubject('college-of-new-caledonia')
  assert.match(cnc, /Identity history and official sources/)
  assert.match(cnc, /<time[^>]*datetime="1978-12-01"[^>]*>December 1, 1978/i)
  assert.match(cnc, /<time[^>]*datetime="1996-06-04"[^>]*>June 4, 1996/i)
  assert.match(cnc, /Open signed designation order/)
  assert.match(cnc, /Open heraldic register/)
  assert.equal((cnc.match(/Open official vector source/g) ?? []).length, 3)
  for (const [end, count] of [['2960_1978', 1], ['project/616', 1], ['sfvrsn=5df38d8d_1#page=1', 2], ['sfvrsn=aa5c3de8_1#page=1', 2]]) {
    assert.equal([...cnc.matchAll(/href="([^"]+)"/g)].filter(([, href]) => href.endsWith(end)).length, count, end)
  }
  assert.match(cnc, /Pre-redesign geometric monogram and serif name/)
  assert.match(cnc, /Secondary lockup: enclosed CNC initials/)
  assert.match(cnc, /class="identity-artwork__image"/)
  assert.match(cnc, /Amalgamated with/)
  assert.doesNotMatch(cnc, /Amalgamated into/i)
  for (const item of [...CNC_CURRENT_MARKS, ...CNC_HISTORICAL_MARKS]) {
    assert.ok(cnc.includes(`src="/PofBC/${item.file}"`), item.label)
    assert.ok(cnc.includes(`href="${item.url}"`), item.credit)
  }
  for (const { label, url } of CNC_BRAND_RESOURCES) assert.ok(cnc.includes(`href="${url}"`), label)
  assert.match(cnc, /view=arms&amp;holder=college-of-new-caledonia/)
  const cncSubject = model.identitySubjectById('college-of-new-caledonia')
  for (const theme of ['light', 'dark']) {
    const card = renderToStaticMarkup(React.createElement(components.CncIdentityCard, { subject: cncSubject, theme }))
    assert.ok(card.includes(`src="/PofBC/${cncCover(theme).file}"`))
    assert.match(card, /subject=college-of-new-caledonia/)
  }
  const { GalleryView } = await server.ssrLoadModule('/src/gallery/GalleryView.jsx')
  const renderGalleryLink = (search) => {
    const previous = globalThis.location
    try {
      globalThis.location = new URL(`https://projects.ahmadjalil.com/PofBC/${search}`)
      return renderToStaticMarkup(React.createElement(GalleryView, callbacks))
    } finally {
      if (previous) globalThis.location = previous
      else delete globalThis.location
    }
  }
  const oldBcitLink = renderGalleryLink('?view=gallery&logos=collected-bcit&mark=source-expanded-bcit-website-logo')
  assert.match(oldBcitLink, /British Columbia Institute of Technology: Website logo/)
  assert.match(oldBcitLink, /href="[^"]*subject=bcit"/)
  assert.doesNotMatch(oldBcitLink, /Incoming Trade Gothic full-name lockup/)
  const bcit = renderGalleryLink('?view=gallery&subject=bcit')
  for (const label of ['Inaugural globe and spear emblem', 'Upright outlined BCIT acronym',
    'BCIT 20th-anniversary emblem', 'Italic striped acronym without a swoosh', 'Striped acronym with orbital swoosh',
    'Outgoing Eras full-name lockup', 'Incoming Trade Gothic full-name lockup', 'Early 2017 visual identity refresh'
  ]) assert.ok(bcit.includes(label), `BCIT subject missing: ${label}`)
  assert.match(bcit, /<time[^>]*datetime="1996-02-29"[^>]*>February 29, 1996/i)
  assert.match(bcit, /Open heraldic register/)
  assert.equal((bcit.match(/Open official vector source/g) ?? []).length, 2)
  assert.match(bcit, /research reconstruction is an approximation/)
  assert.doesNotMatch(bcit, /<(img|image|object|iframe)\b[^>]*\b(src|href|data)="https:/)
  const shared = renderSubject('ubc-okanagan-campus')
  assert.match(shared, /Shared branding/)
  assert.match(shared, /subject=university-of-british-columbia/)
  assert.doesNotMatch(shared, /No separately held artwork/)
  assert.match(shared, /recovered-ubc-logo-2018-ok-campus-standard-blue282rgb/)
  const cover = renderSubject('vancouver-school-of-art')
  assert.match(cover, /Publication cover, institutional status unconfirmed/)
  assert.doesNotMatch(cover, /Open official vector source/)
  const register = renderToStaticMarkup(React.createElement(components.IdentityCoverageBrowser, { onHome() {}, onOpenSubject() {} }))
  assert.ok(register.includes(`${model.IDENTITY_COVERAGE.length} subjects`), 'register count does not render')
  const counts = summarizePostsecondaryArtwork(model.IDENTITY_COVERAGE.filter((subject) => subject.family === 'postsecondary-history'))
  for (const wording of [
    `${counts.held} with artwork in the gallery`, `${counts.vector} with verified native-vector sources`,
    `${counts.observedNonvector} with observed nonvector artwork only`, `${counts.unverified} without distinct verified logo artwork`
  ]) assert.ok(register.includes(wording), `missing post-secondary count: ${wording}`)
  const overview = renderToStaticMarkup(React.createElement(components.IdentityCoverageOverview, callbacks))
  assert.ok(overview.includes('Browse the register'), 'register is not reachable from overview')
  const { CollectedMarkView } = await server.ssrLoadModule('/src/gallery/CollectedMarkView.jsx')
  const { collectedEntriesOf } = await server.ssrLoadModule('/src/gallery/collectedCollections.js')
  const surveyDesigns = collectedEntriesOf('sub-british-columbia-geological-survey')
  for (const id of ['bcgs-survey-seal', 'bcgs-centennial-1995', 'bcgs-anniversary-2020', 'bcgs-founding-year-seal']) {
    const design = surveyDesigns.find((entry) => entry.id === id)
    assert.ok(design, id)
    const vector = design.versions.find((version) => version.evidenceType === 'native-pdf-vector-extraction')
    assert.ok(vector, `${design.id}: missing extracted vector`)
    const detail = renderToStaticMarkup(React.createElement(CollectedMarkView, { entry: design }))
    assert.ok(detail.includes(`href="/PofBC/${vector.file}"`), `${design.id}: vector download is missing`)
    assert.ok(detail.includes(vector.versionLabel), `${design.id}: vector version is missing`)
  }
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
  const { findGalleryEntry } = await server.ssrLoadModule('/src/gallery/collections.js')
  const oldLocation = globalThis.location
  try {
    for (const id of [
      'source-expanded-bc-ferry-authority-2003-website-logo',
      'historical-kootenay-boundary-health-2002-website',
      'source-expanded-nechako-kitamaat-development-fund-website-logo',
      'source-recovered-ehsc-launch-advertisement-1974',
      'source-recovered-followup-government-communications-and-public-engagement-estimate-notes-2024'
    ]) {
      globalThis.location = { search: `?view=gallery&mark=${id}` }
      const entry = findGalleryEntry(id)
      assert.equal(entry.asset.reconstructionOf, id)
      assert.ok(entry.versions.some((version) => version.id === id && !version.isVector))
      const html = renderToStaticMarkup(React.createElement(CollectedMarkView, { entry }))
      assert.match(html, /Download reconstruction SVG/)
      assert.match(html, /Download displayed SVG/)
      assert.match(html, /Published image/)
    }
  } finally {
    if (oldLocation === undefined) delete globalThis.location
    else globalThis.location = oldLocation
  }
  const { TIMELINES } = await server.ssrLoadModule('/src/gallery/timelines.js')
  const crest = TIMELINES['bc-wildfire-service'].eras.find(({ id }) => id === 'bcws-oval-crest')
  assert.equal(crest.years, 'June 2021')
  assert.equal(crest.applicability.years, crest.years)
  assert.match(crest.applicability.note, /2015 news release dates the name only/)
  console.log(`Rendered ${renders} subject pages (light and dark), register and overview; checked local images at /PofBC/.`)
} finally {
  await server.close()
}
