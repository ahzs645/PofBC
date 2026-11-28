import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { initiativeAncestors, initiativeById, initiativeParts, initiativesForBody, loadInitiative } from './initiatives.js'
import { ASC_ID, ASDT_ID } from './asdt.js'
import { relatedBodyById } from '../government/relatedBodies.js'
import { governmentIn } from '../government/snapshot.js'

const root = new URL('../../', import.meta.url)
const sha256 = (path) => createHash('sha256').update(readFileSync(new URL(path, root))).digest('hex')

test('ASDT and the collaborative that followed it are one programme', async () => {
  assert.deepEqual(initiativeParts(ASDT_ID).map(({ id }) => id), [ASC_ID])
  assert.deepEqual(initiativeAncestors(ASC_ID).map(({ id }) => id), [ASDT_ID])
  for (const id of [ASDT_ID, ASC_ID]) {
    const detail = await loadInitiative(id)
    assert.equal(detail.sections.at(-1).type, 'sources')
    for (const section of detail.sections) {
      for (const record of section.records ?? []) {
        for (const reference of record.sourceRefs ?? []) assert.ok(detail.sources.some((source) => source.id === reference.sourceId), `${id}: ${reference.sourceId}`)
      }
    }
  }
})

test('every body the programme names is a site body, and each lists the programme', () => {
  for (const id of [ASDT_ID, ASC_ID]) {
    for (const body of initiativeById(id).relatedBodyIds) {
      const standing = relatedBodyById(body) || [2012, 2014, 2016, 2018, 2020, 2022, 2026].some((year) => governmentIn(year).nodes.some((node) => node.id === body))
      assert.ok(standing, `${id}: ${body}`)
      assert.ok(initiativesForBody(body).some((entry) => entry.id === id))
    }
  }
  assert.ok(initiativeById(ASDT_ID).relatedBodyIds.includes('bcnet'))
})

test('the wordmark is the bulletin’s own image, kept with its source', () => {
  assert.equal(sha256('research/identity/asdt-2026-11-27/source/asdt-update-q3-2016-17.pdf'), '83c219dd886179f65842a48fae20108cc3fb57ccb88ac500615ceb7dd4342bf0')
  assert.ok(existsSync(new URL('public/initiatives/asdt/asdt-wordmark-2017.png', root)))
  // The two vectors are the reports' own paths: no embedded bitmap, no live text.
  for (const file of ['asdt-2015-16-progress-report.svg', 'asc-2019-strategic-plan.svg']) {
    const svg = readFileSync(new URL(`public/initiatives/asdt/${file}`, root), 'utf8')
    assert.doesNotMatch(svg, /<image|<text/, file)
  }
  assert.equal((readFileSync(new URL('public/initiatives/asdt/asdt-2015-16-progress-report.svg', root), 'utf8').match(/<radialGradient/g) ?? []).length, 5)
  assert.ok(existsSync(new URL('research/identity/asdt-2026-11-27/README.md', root)))
})
