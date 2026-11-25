import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { governmentIn } from '../government/snapshot.js'
import { initiativeById, initiativesForBody, loadInitiative } from './initiatives.js'
import { imagesOf, resolveInitiativeSelection, searchInitiatives } from './initiativeModel.js'

test('Achieve BC retains all five official design notices and identifies the two publication artwork formats', async () => {
  const initiative = await loadInitiative('achieve-bc')
  const marks = initiative.sections.find((section) => section.id === 'marks').records
  assert.equal(marks.length, 6)
  assert.deepEqual(marks.flatMap((item) => item.registrations ?? []).map((entry) => entry.number).sort(), [915352, 915353, 915354, 915355, 915357])
  assert.ok(initiative.sources.some((source) => source.id === 'cipo-915356'))
  const sourceIds = new Set(initiative.sources.map((source) => source.id))
  assert.equal(sourceIds.size, initiative.sources.length)
  for (const section of initiative.sections.filter((section) => section.type !== 'sources')) {
    for (const record of section.records) {
      for (const ref of record.sourceRefs) assert.ok(sourceIds.has(ref.sourceId), record.id)
      for (const image of imagesOf(record)) {
        assert.ok(sourceIds.has(image.sourceId))
        assert.ok(image.date && image.alt)
        const bytes = readFileSync(new URL('../../public/' + image.file, import.meta.url))
        assert.ok(bytes.length > 0)
        if (image.evidenceType === 'mixed-pdf-artwork') assert.match(bytes.toString(), /<image .*data:image\/jpeg;base64,/)
        if (image.evidenceType === 'native-pdf-vector-extraction') {
          assert.match(bytes.toString(), /<radialGradient /)
          assert.doesNotMatch(bytes.toString(), /<(?:text|image)\b/)
        }
      }
    }
  }
  assert.equal(resolveInitiativeSelection(initiative, { record: 'deceive-bc' }).section.id, 'related')
  assert.equal(searchInitiatives('Bringing Out the Best', [initiativeById('achieve-bc')]).length, 1)
  for (const { to } of initiative.relatedLinks) {
    assert.ok(governmentIn(to.year).nodes.some((node) => node.id === to.node), to.node)
    assert.ok(initiativesForBody(to.node).some((entry) => entry.id === initiative.id))
  }
})
