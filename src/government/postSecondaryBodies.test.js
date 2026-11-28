import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { POST_SECONDARY_RELATED_BODIES } from './postSecondaryBodies.js'
import { relatedBodyById } from './relatedBodies.js'
import { FINANCE_INDEX } from './financeIndex.js'
import { governmentIn } from './snapshot.js'
import { identitySubjectById } from '../gallery/identityCoverage.js'
import { collectionsOfNode } from '../gallery/collections.js'
import register from '../../research/identity/postsecondary-2026-11-24/source-register.json' with { type: 'json' }

const ids = POST_SECONDARY_RELATED_BODIES.map((body) => body.id)
const research = new URL('../../research/finance/public-accounts-23-1/', import.meta.url)
const rows = (name) => readFileSync(new URL(name, research), 'utf8').trim().split('\n').slice(1)

test('the nineteen institutions with statements and no record now have one each', () => {
  assert.equal(ids.length, 19)
  assert.equal(new Set(ids).size, 19)
  // Every current institution in the register is a site body, here or in relatedBodies.js (JIBC in the atlas).
  const current = register.records.filter((record) => record.current && /^public-(college|university|institute)$/.test(record.kind)).map((record) => record.id)
  assert.deepEqual([...current].sort(), [...ids].sort())
  for (const id of ids) {
    assert.ok(relatedBodyById(id), id)
    assert.ok(FINANCE_INDEX[id]?.s > 0, `${id} has statements on its Money card`)
  }
  const keys = new Set(rows('site-ids.csv').map((row) => row.split(',')[2]))
  for (const id of ids) assert.ok(keys.has(id), `${id} is joined in site-ids.csv`)
})

test('each record opens its register entry and gallery collection, and its lineage stays in the register', () => {
  for (const body of POST_SECONDARY_RELATED_BODIES) {
    assert.ok(identitySubjectById(body.id), `${body.id} is a register subject`)
    assert.ok(collectionsOfNode(body.id).length > 0, `${body.id} has a gallery collection`)
    for (const entry of body.lineage ?? []) {
      assert.ok(identitySubjectById(entry.subject), `${body.id}: ${entry.subject} is a register subject`)
      assert.equal(relatedBodyById(entry.subject), null, `${entry.subject} is not also a site body`)
    }
  }
  assert.deepEqual(relatedBodyById('coast-mountain-college').lineage.map((entry) => entry.subject), ['northwest-community-college'])
  assert.deepEqual(relatedBodyById('vancouver-island-university').lineage.map((entry) => entry.subject), ['malaspina-college', 'malaspina-university-college'])
})

test('each names its statute, its 2026 ministry and BCNET, with sources', () => {
  for (const body of POST_SECONDARY_RELATED_BODIES) {
    assert.match(body.act, /^(College and Institute Act|University Act|Royal Roads University Act|Thompson Rivers University Act)$/)
    assert.ok(body.description.includes(body.act) || body.kind === 'public-institute', body.id)
    const [ministry, bcnet] = body.relationships
    assert.equal(ministry.id, 'ministry-of-post-secondary-education-and-labour-2026')
    assert.ok(governmentIn(ministry.year).nodes.some((node) => node.id === ministry.id))
    assert.equal(bcnet.id, 'bcnet')
    assert.ok(body.sources.some((entry) => /audited financial statements 2025-26/.test(entry.title)), body.id)
    for (const entry of body.sources) assert.equal(new URL(entry.url).protocol, 'https:')
  }
})
