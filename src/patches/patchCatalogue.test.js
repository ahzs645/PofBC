import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  catalogueCards, filterCatalogue, groupCatalogueByTemplate, isGeneratedColourway,
  patchPlaceParams, patchPlaceUrl, readPatchPlace, sourcePhotoCount, variantCount
} from './patchCatalogue.js'

const shield = { id: 'shield', label: 'Ministry shield', description: 'A shared layout.' }
const arch = { id: 'arch', label: 'Scenic arch', description: 'A separate template.' }
const blue = { id: 'blue', label: 'British Columbia / Parks', variant: 'Blue', medium: 'Cloth patch', collection: 'patches', group: 'parks', absorbs: ['OLD-O01'] }
const gold = { id: 'gold', label: 'British Columbia / Parks / Ranger', variant: 'Gold', medium: 'Cloth patch', collection: 'patches', group: 'parks', sightings: [{ id: 'PHOTO-O01' }, { id: 'PHOTO-O02' }] }
const justice = { id: 'justice', label: 'Attorney General', medium: 'Cloth patch', collection: 'patches' }
const unknown = { id: 'unknown', label: 'Unidentified roundel', medium: 'Cloth patch', collection: 'patches' }
const variants = [blue, gold]
const sections = [{
  sector: { id: 'environment', name: 'Environment' },
  orgs: [{ id: 'parks', name: 'BC Parks', patches: variants }]
}, {
  sector: { id: 'justice', name: 'Justice' },
  orgs: [{ id: 'justice', name: 'Attorney General', patches: [justice, unknown] }]
}]
const cards = catalogueCards(sections, {
  isCard: (patch) => patch.id !== 'gold',
  variantsOf: (patch) => patch.group === 'parks' ? { members: variants } : null,
  cardLabel: (patch) => patch.group === 'parks' ? 'Parks shield' : patch.label,
  templateFamilyOf: (patch) => patch.id === 'unknown' ? null : shield
})

test('template grouping keeps every card and variant, including unclassified artwork', () => {
  const shown = filterCatalogue(cards)
  const groups = groupCatalogueByTemplate(shown, [arch, shield])
  assert.deepEqual(groups.map(({ family }) => family.id), ['shield', 'other'])
  assert.equal(groups[0].cards.length, 2, 'a family can connect organizations without merging their cards')
  assert.equal(groups.flatMap(({ cards }) => cards).length, 3)
  assert.equal(variantCount(shown), 4)
  assert.deepEqual(groups[0].cards.map(({ org }) => org.id), ['parks', 'justice'])
})

test('a query for a non-primary variant opens that variant and counts only matching variants', () => {
  const shown = filterCatalogue(cards, { q: 'Ranger Gold' })
  assert.equal(shown.length, 1)
  assert.equal(shown[0].patch.id, 'blue', 'the catalogue card keeps its stable identity')
  assert.equal(shown[0].selected.id, 'gold', 'the link and preview use the matching variant')
  assert.equal(variantCount(shown), 1)
  assert.deepEqual(filterCatalogue(cards, { q: 'blue gold' }), [], 'words from different variants must not create a false match')
  assert.equal(blue.variant, 'Blue', 'filtering never rewrites the source record')
})

test('family labels, stable ids and old source aliases participate in search', () => {
  assert.equal(filterCatalogue(cards, { q: 'Ministry shield' }).length, 2)
  assert.equal(filterCatalogue(cards, { q: 'OLD-O01' })[0].selected.id, 'blue')
  assert.equal(filterCatalogue(cards, { q: 'PHOTO-O02' })[0].selected.id, 'gold')
  assert.equal(filterCatalogue(cards, { q: 'justice' })[0].selected.id, 'justice')
})

test('an exact variant id is not mistaken for another edition with the same prefix', () => {
  const short = { ...blue, id: 'FO-green-gold-black', absorbs: [] }
  const long = { ...gold, id: 'FO-green-gold-black-gold', sightings: [] }
  const related = [{ ...cards[0], patch: long, members: [long, short], templates: new Map([[short.id, shield], [long.id, shield]]) }]
  const shown = filterCatalogue(related, { q: 'FO-green-gold-black' })
  assert.equal(shown[0].selected.id, short.id)
  assert.equal(variantCount(shown), 1)
})

test('organization and template filters intersect, and unclassified designs remain selectable', () => {
  assert.equal(filterCatalogue(cards, { family: 'shield', org: 'parks' }).length, 1)
  assert.equal(variantCount(filterCatalogue(cards, { family: 'shield', org: 'parks' })), 2)
  assert.deepEqual(filterCatalogue(cards, { family: 'arch', org: 'parks' }), [])
  assert.deepEqual(filterCatalogue(cards, { family: 'other' }).map(({ selected }) => selected.id), ['unknown'])
})

test('generated-colourway labels require an explicit note, and photo occurrences count once', () => {
  assert.equal(isGeneratedColourway({ limitations: 'This colourway is a generated recolour, not seen in a photograph.' }), true)
  assert.equal(isGeneratedColourway({ limitations: 'The original date is unknown.', sightings: [] }), false)
  assert.equal(isGeneratedColourway({ supplied: { svg: 'reconstruction.svg' }, sightings: [] }), false)
  assert.equal(sourcePhotoCount(gold), 1)
  assert.equal(sourcePhotoCount({}), 0)
})

const locationOptions = {
  collection: 'patches', orgIds: ['parks', 'justice'], familyIds: ['shield', 'other'],
  findPatch: (id) => id === 'OLD-O01' ? blue : [...variants, justice, unknown, { id: 'badge', collection: 'badges' }].find((patch) => patch.id === id)
}

test('shared links preserve filters and resolve old ids without crossing collections', () => {
  const place = readPatchPlace('?view=patches&group=template&family=shield&org=parks&q=gold&patch=OLD-O01', locationOptions)
  assert.deepEqual(place, { group: 'template', family: 'shield', org: 'parks', q: 'gold', patch: 'blue' })
  const url = patchPlaceUrl('https://example.org/PofBC/?theme=dark', 'patches', place)
  assert.equal(url.searchParams.get('theme'), 'dark')
  assert.deepEqual(readPatchPlace(url.search, locationOptions), place)
  assert.equal(readPatchPlace('?patch=badge', locationOptions).patch, null)
})

test('unknown filters fall back safely, and closing a patch retains the browsing context', () => {
  assert.deepEqual(readPatchPlace('?org=missing&family=missing&group=missing&patch=missing', locationOptions), {
    org: null, family: null, group: 'organization', patch: null, q: ''
  })
  const place = { org: 'parks', family: 'shield', group: 'template', q: 'Ranger', patch: 'gold' }
  const closed = { ...place, patch: null }
  assert.deepEqual(patchPlaceParams('patches', closed), { view: 'patches', org: 'parks', family: 'shield', group: 'template', q: 'Ranger', patch: null })
  const url = patchPlaceUrl('https://example.org/?view=patches&patch=gold&org=parks&group=template&family=shield&q=Ranger', 'patches', closed)
  assert.equal(url.searchParams.has('patch'), false)
  assert.equal(url.searchParams.get('family'), 'shield')
  const cleared = patchPlaceUrl(url.href, 'patches', { ...closed, org: null, family: null, q: '', group: 'organization' })
  assert.equal(cleared.search, '?view=patches')
})
