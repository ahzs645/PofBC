import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import pack from './vancouverVisualStandards.json' with { type: 'json' }
import recipes from '../../research/identity/vancouver-visual-standards-2026-11-27/extractions.json' with { type: 'json' }
import { collectionById, entriesOf, findGalleryEntry } from './collections.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'

const root = new URL('../../', import.meta.url)
const assets = pack.additions['municipality-vancouver']
const sha256 = (data) => createHash('sha256').update(data).digest('hex')

test('every file extracted from the 2018 guide is its own native paths, with its recipe recorded', () => {
  assert.equal(pack.sourceSha256, recipes.sourceSha256)
  for (const asset of [...assets, ...Object.values(pack.otherViews)]) {
    const recipe = recipes.extractions.find(({ id }) => id === asset.id)
    const data = readFileSync(new URL(`${recipe.fileRoot ?? 'public'}/${asset.file}`, root))
    assert.equal(data.length, asset.bytes, asset.id)
    assert.equal(sha256(data), asset.sha256, asset.id)
    const svg = data.toString('utf8')
    assert.doesNotMatch(svg, /<(?:image|text|use|script|foreignObject)\b/, `${asset.id}: paths only`)
    assert.equal(asset.evidenceType, 'native-pdf-vector-extraction', asset.id)
    assert.equal(asset.reconstruction, false, asset.id)
    assert.equal(asset.extraction.sourceSha256, recipes.sourceSha256, asset.id)
    assert.match(asset.sourcePage, /^https:\/\/policy\.vancouver\.ca\/CP00103P2\.pdf#page=\d+$/, asset.id)
    assert.deepEqual(asset.extraction.region, recipe.region, asset.id)
  }
})

test('the emblem keeps its website PNG and design id, opens on the guide’s colour vector, and is dated by its adoption', () => {
  const emblem = findGalleryEntry('source-recovered-municipal-vancouver-website-logo')
  assert.equal(emblem.id, 'source-recovered-municipal-vancouver-website-logo')
  assert.equal(emblem.asset.id, 'vancouver-emblem-2006-colour')
  assert.deepEqual(emblem.versions.map(({ id }) => id).sort(), [
    'source-recovered-municipal-vancouver-website-logo', 'vancouver-emblem-2006-black', 'vancouver-emblem-2006-colour', 'vancouver-emblem-2006-white'
  ])
  assert.equal(emblem.identity.applicability.kind, 'documented_adoption')
  assert.equal(emblem.identity.applicability.years, '18 July 2006')
  assert.equal(emblem.years, 'Adopted 18 July 2006')
})

test('the Vancouver collection opens on the emblem and shows every design from the guide in a section', () => {
  const collection = collectionById('collected-municipality-vancouver')
  assert.equal(collection.cover, 'source-recovered-municipal-vancouver-website-logo')
  const sectioned = collection.artworkSections.flatMap(({ entries }) => entries.map(({ id }) => id))
  const designs = entriesOf(collection).map(({ id }) => id)
  assert.deepEqual([...sectioned].sort(), [...designs].sort())
  // Different layouts stay separate designs: the former lockup is not a version of the current one.
  assert.notEqual(findGalleryEntry('vancouver-engineering-services-former'), findGalleryEntry('vancouver-engineering-services-colour'))
})

test('every guide file has light and dark display copies, and one-colour black art is redrawn for the dark page', () => {
  for (const asset of assets) {
    assert.ok(COLLECTED_DISPLAY[asset.id], `${asset.id}: display copies`)
    if (asset.id.endsWith('-black')) assert.equal(COLLECTED_DISPLAY[asset.id].dark.recoloured, true, asset.id)
  }
})
