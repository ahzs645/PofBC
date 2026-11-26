import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { allCollectedDisplayAssets } from './collectedBodies.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'
import { collectionById, entriesOf, findGalleryEntry } from './collections.js'
import { collectedDetailPreview, collectedDisplay, logoScale, onPage, tileArt } from './tileArt.js'

const assets = new Map(allCollectedDisplayAssets().map((asset) => [asset.id, asset]))
const publicFile = (path) => new URL(`../../public/${path}`, import.meta.url)

// Drawn as vector: an SVG (Innovate BC's keeps the report's photograph in its disc) or an EPS.
const drawable = (asset) => asset.format === 'svg' || (asset.format === 'eps' && asset.isVector)

test('the Trust’s five-paddle website SVG stays on the dark gallery ground when selected', () => {
  const entry = findGalleryEntry('source-expanded-island-coastal-economic-trust-website-logo')
  const dark = collectedDisplay(entry.asset, 'dark')
  assert.ok(dark.palette && !dark.plate)
  assert.ok(tileArt(entry, 'dark', { cover: true }).includes(dark.file))
  for (const selected of [true, false]) {
    const preview = collectedDetailPreview(entry.asset, 'dark', selected)
    assert.equal(preview.file, dark.file)
    assert.equal(preview.ground, undefined)
  }
})

test('every collected SVG and vector EPS has a display entry', () => {
  for (const asset of assets.values()) {
    if (drawable(asset)) assert.ok(COLLECTED_DISPLAY[asset.id], `${asset.id} needs display artwork`)
  }
})

test('the Education Province initiative uses display copies without publishing a gallery collection or marks', () => {
  assert.ok(COLLECTED_DISPLAY['education-province-wordmark'])
  assert.equal(collectionById('specimens-bc-the-education-province'), undefined)
  assert.ok(!findGalleryEntry('education-province-wordmark'))
  assert.ok(!findGalleryEntry('education-province-newspaper-badge'))
})

test('every display copy is of a collected vector file, for both themes, and exists', () => {
  for (const [id, entry] of Object.entries(COLLECTED_DISPLAY)) {
    const asset = assets.get(id)
    assert.ok(asset, `${id} is a collected file`)
    assert.ok(drawable(asset), `${id} is a vector file`)
    for (const theme of ['light', 'dark']) {
      const copy = entry[theme]
      assert.ok(copy, `${id} has a ${theme} copy`)
      assert.match(copy.file, /^identity-display\/[A-Za-z0-9._-]+\.svg$/)
      assert.ok(existsSync(publicFile(copy.file)), `${copy.file} exists`)
      assert.ok(copy.aspect > 0, `${id} has its proportions`)
      assert.equal(typeof copy.recoloured, 'boolean')
      // A palette chosen by hand (collected-display-overrides.json) is a redrawn copy, never a plate.
      if (copy.palette) assert.ok(copy.recoloured && !copy.plate, `${id}: a ${theme} palette copy is redrawn`)
    }
  }
})

test('a display copy keeps the source file as it is, apart from its viewBox and colours', () => {
  for (const [id, entry] of Object.entries(COLLECTED_DISPLAY)) {
    const copy = readFileSync(publicFile(entry.light.file), 'utf8')
    assert.doesNotMatch(copy, /<script/i, `${id} carries no script`)
    assert.match(copy, /viewBox="[-\d. ]+"/, `${id} is trimmed by its viewBox`)
  }
})

test('raster files have no display copy and keep their plate', () => {
  const raster = [...assets.values()].find((asset) => ['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(asset.format))
  assert.equal(collectedDisplay(raster, 'dark'), null)
})

test('a matching transparent reconstruction can supply gallery previews without replacing the original', () => {
  for (const [id, vectorId] of [
    ['selectseed-pinecone', 'selectseed-pinecone-rebuilt'],
    ['legislative-library-digital-collections', 'legislative-library-digital-collections-rebuilt'],
    ['legislative-assembly-website-signature', 'legislative-assembly-website-signature-rebuilt']
  ]) {
    const entry = findGalleryEntry(id)
    assert.equal(entry.asset.id, id)
    assert.equal(entry.asset.format, 'png')
    assert.equal(onPage(entry), true)
    for (const theme of ['light', 'dark']) {
      const image = tileArt(entry, theme, { cover: true })
      assert.ok(image.includes(collectedDisplay(assets.get(vectorId), theme).file))
      assert.match(image, /title="Vector reconstruction"/)
      assert.doesNotMatch(image, /data-(?:plate|dark)=/)
    }
  }

  const centennial = findGalleryEntry('bcgs-centennial-1995')
  assert.equal(onPage(centennial), false)
  assert.ok(tileArt(centennial, 'dark').includes(centennial.asset.file))
})

test('ETSI-BC leads with its full-name logo and has vectors for its stacked and anniversary designs', () => {
  const collection = collectionById('collected-etsi-bc')
  const entries = entriesOf(collection)
  assert.equal(collection.cover, 'source-expanded-etsi-bc-bylaws-2026-full-name-colour')
  assert.deepEqual(entries.map((entry) => entry.label), ['Full-name horizontal logo', 'Stacked logo', '20th anniversary logo'])
  const stacked = entries[1]
  assert.equal(stacked.asset.variantOf, stacked.id)
  assert.equal(stacked.versions.find((asset) => asset.id === stacked.id).format, 'png')
  for (const { asset } of entries) {
    assert.equal(asset.isVector, true)
    assert.equal(asset.reconstruction, false)
    assert.doesNotMatch(readFileSync(publicFile(asset.file), 'utf8'), /<(?:image|text)\b/)
  }
})

test('the BC Ambulance badge opens its mixed-media reconstruction at the published design URL', () => {
  const entry = findGalleryEntry('source-recovered-bc-ambulance-service')
  assert.equal(entry.asset.reconstructionOf, entry.id)
  assert.equal(entry.asset.reconstruction, true)
  assert.equal(entry.asset.isVector, false)
  assert.equal(entry.versions.find((version) => version.id === entry.id).format, 'png')
  for (const theme of ['light', 'dark']) {
    const display = collectedDisplay(entry.asset, theme)
    assert.ok(tileArt(entry, theme, { cover: true }).includes(display.file))
    const svg = readFileSync(publicFile(display.file), 'utf8')
    assert.match(svg, /<image\b[^>]+data:image\/png;base64,/)
    assert.match(svg, /<path id="british-columbia"/)
    assert.match(svg, /<path id="ambulance-service"/)
    for (const id of ['outer-ring', 'inner-ring']) {
      assert.match(svg, new RegExp(`<circle id="${id}"[^>]* stroke="#204176"`))
    }
  }
})

test('a long wordmark is drawn shorter than a square emblem, within bounds', () => {
  assert.equal(logoScale(1), 1)
  assert.equal(logoScale(2.4), 1)
  assert.ok(logoScale(5) < 1 && logoScale(5) > logoScale(10))
  assert.equal(logoScale(100), 0.42)
})

test('CleanBC links all layouts to the plan and uses each published reverse on a dark card', () => {
  const collection = collectionById('collected-sub-cleanbc')
  assert.equal(collection.graphNode, 'sub-cleanbc')
  assert.deepEqual(collection.artworkSections.map(({ entries }) => entries.length), [6, 6, 2])
  for (const entry of entriesOf(collection)) {
    assert.equal(entry.owner, collection.graphNode)
    assert.ok(tileArt(entry, 'light').includes(collectedDisplay(entry.asset, 'light').file))
    if (entry.id === 'cleanbc-financeit') {
      assert.equal(entry.asset.darkVariant, undefined)
      continue
    }
    const reverse = entry.versions.find(({ id }) => id === entry.asset.darkVariant)
    assert.equal(reverse.variantOf, entry.id)
    assert.equal(collectedDisplay(reverse, 'dark').recoloured, false)
    assert.ok(tileArt(entry, 'dark').includes(collectedDisplay(reverse, 'dark').file))
  }
})

test('StrongerBC keeps legacy source URLs and uses a published reverse for each guide layout', () => {
  const groups = [
    ['vector-BCID_StrongerBC_RGB_pos', 4], ['vector-StrongerBC_RGB_pos', 2],
    ['vector-StrongerBC_Solid_pos', 2], ['strongerbc-for-everyone-endorsed', 4],
    ['strongerbc-for-everyone-wordmark', 4]
  ]
  for (const [id, count] of groups) {
    const entry = findGalleryEntry(id)
    assert.equal(entry.versions.length, count)
    const reverse = entry.versions.find((asset) => asset.id === entry.asset.darkVariant)
    assert.ok(tileArt(entry, 'dark').includes(collectedDisplay(reverse, 'dark').file))
    for (const version of entry.versions) {
      assert.equal(findGalleryEntry(version.id).id, id)
      assert.equal(collectedDisplay(version, version.sourceGround).recoloured, false)
      for (const download of version.downloads ?? []) assert.ok(existsSync(publicFile(download.file)))
    }
  }
  assert.equal(findGalleryEntry('stronger-bc').kind, 'artwork')
})

test('a design opens on its theme surface and selecting an Ember pose keeps that surface', () => {
  for (const asset of assets.values()) {
    if (!drawable(asset)) continue
    for (const theme of ['light', 'dark']) {
      const preview = collectedDetailPreview(asset, theme)
      assert.equal(preview.file, collectedDisplay(asset, theme).file, asset.id)
      assert.equal(preview.ground, preview.display.plate ? 'light' : undefined, asset.id)
    }
  }
  const ember = findGalleryEntry('firesmart-bc-ember-front')
  assert.equal(ember.versions.length, 4)
  for (const pose of ember.versions) {
    for (const theme of ['light', 'dark']) {
      const preview = collectedDetailPreview(pose, theme, true)
      assert.equal(preview.file, collectedDisplay(pose, theme).file)
      assert.equal(preview.ground, undefined)
    }
  }
  const buyBC = findGalleryEntry('buy-bc-vertical-colour')
  const black = buyBC.versions.find((v) => /black/i.test(v.versionLabel))
  const selected = collectedDetailPreview(black, 'dark', true)
  assert.equal(selected.ground, 'light')
  assert.equal(selected.themed, true)
})
