import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { FLAG } from '../assets/flagMark.js'
import { governmentIn } from '../government/snapshot.js'
import { collectionById } from '../gallery/collections.js'
import { initiativesForBody, loadInitiative } from './initiatives.js'

test('BC Youth reconstructions reuse the provincial flag and retain the source for each printing', async () => {
  const initiative = await loadInitiative('bc-youth')
  const [right, left] = initiative.sections.find(section => section.id === 'marks').records
  assert.deepEqual(right.images.filter(image => image.evidenceType === 'printed-source-crop').map(image => image.date),
    ['1989-10-04', '1989-10-24'])
  assert.ok(left.images.every(image => image.darkBackground && image.sourceId === 'reverse' && !image.date))
  for (const image of [...right.images, ...left.images].filter(image => image.evidenceType === 'vector-reconstruction')) {
    const svg = readFileSync(new URL('../../public/' + image.file, import.meta.url), 'utf8')
    assert.doesNotMatch(svg, /<(?:image|text)\b/)
    for (const shape of FLAG.shapes.filter(shape => shape.fill !== '#fcba19')) assert.ok(svg.includes(shape.d), image.file)
  }
})

test('historical ministry links resolve in the selected atlas year and lead back to the initiative', async () => {
  assert.equal(collectionById('collected-bc-youth').initiativeId, 'bc-youth')
  for (const id of ['bc-youth', 'challenge-89', 'passport-to-apprenticeship', 'environment-youth-corps']) {
    const initiative = await loadInitiative(id)
    const ministries = initiative.relatedLinks.filter(link => link.to.view === 'government')
    assert.ok(ministries.length, id)
    for (const {to} of ministries) {
      assert.ok(governmentIn(to.year).nodes.some(node => node.id === to.node), to.node)
      assert.ok(initiativesForBody(to.node).some(program => program.id === id), id)
    }
  }
})
